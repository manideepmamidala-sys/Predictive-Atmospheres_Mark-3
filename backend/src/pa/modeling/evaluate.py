"""Nested grouped model comparison with fold-fitted affect targets and preprocessing."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from math import comb

import numpy as np
import pandas as pd
from numpy.typing import NDArray
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from pa.features.builder import FEATURE_ORDER
from pa.modeling.splits import (
    candidate_key,
    candidate_specs,
    choose_candidate,
    inner_splits,
    outer_splits,
)
from pa.modeling.targets import CalibrationUnavailable, PopulationCalibrator
from pa.signals.common import decisions

CATEGORICAL = ("day_or_night", "space_type")
NUMERIC = tuple(name for name in FEATURE_ORDER if name not in CATEGORICAL)


@dataclass(frozen=True)
class Selection:
    candidate: dict
    scores: dict[str, float | None]
    status: str
    inner_fold_calibrations: tuple[dict, ...]
    ineligibility_reasons: dict[str, str] | None = None


def make_estimator(spec: dict) -> Pipeline:
    numeric = Pipeline([("impute", SimpleImputer(strategy="median", add_indicator=True,
                                                keep_empty_features=True)),
                        ("scale", StandardScaler())])
    categorical = Pipeline([("impute", SimpleImputer(strategy="most_frequent")),
                            ("encode", OneHotEncoder(handle_unknown="ignore"))])
    preprocess = ColumnTransformer([("numeric", numeric, list(NUMERIC)),
                                    ("categorical", categorical, list(CATEGORICAL))])
    name = spec["name"]
    if name == "dummy_median":
        model = DummyRegressor(strategy="median")
    elif name == "dummy_mean":
        model = DummyRegressor(strategy="mean")
    elif name == "ridge":
        model = Ridge(alpha=spec["alpha"])
    elif name == "random_forest":
        cfg = decisions()["modeling"]
        model = RandomForestRegressor(n_estimators=spec["n_estimators"],
                                      max_depth=spec["max_depth"],
                                      min_samples_leaf=spec["min_samples_leaf"],
                                      max_features=cfg["random_forest_max_features"],
                                      random_state=cfg["random_seed"],
                                      n_jobs=cfg["random_forest_n_jobs"])
    else:
        raise ValueError(f"unsupported candidate: {name}")
    return Pipeline([("preprocess", preprocess), ("model", model)])


def group_mae(predicted: NDArray[np.float64], target: NDArray[np.float64],
              groups: NDArray) -> tuple[float, float, float]:
    if predicted.shape != target.shape or target.ndim != 2 or target.shape[1] != 2:
        raise ValueError("two-axis prediction and target shape mismatch")
    if not np.isfinite(predicted).all() or not np.isfinite(target).all():
        raise ValueError("nonfinite grouped comparison")
    per_group = [np.mean(np.abs(predicted[groups == group] - target[groups == group]), axis=0)
                 for group in np.unique(groups)]
    axis_mae = np.mean(per_group, axis=0)
    return float(axis_mae[0]), float(axis_mae[1]), float(np.mean(axis_mae))


def select_candidate(X: pd.DataFrame, raw: pd.DataFrame, reports: NDArray[np.float64],
                     groups: NDArray) -> Selection:
    """Refit target and feature transforms on every inner-training subset."""
    folds = inner_splits(groups)
    if not folds:
        return Selection({"name": "dummy_median"}, {}, "fixed_baseline_insufficient_groups", (),
                         {"inner_cv": "fewer than four independent training groups"})
    fold_targets = []
    calibrations = []
    for train, validation in folds:
        try:
            calibration = PopulationCalibrator.fit(raw.iloc[train])
            y_train = calibration.fused(raw.iloc[train], reports[train])
            y_validation = calibration.fused(raw.iloc[validation], reports[validation])
        except CalibrationUnavailable as exc:
            return Selection({"name": "dummy_median"}, {},
                             "fixed_baseline_uncalibratable_inner_target",
                             tuple(calibrations), {"inner_target": str(exc)})
        fold_targets.append((train, validation, y_train, y_validation))
        calibrations.append({"centers": calibration.centers, "scales": calibration.scales,
                             "training_indices": train.tolist(),
                             "validation_indices": validation.tolist()})
    scores: dict[str, float | None] = {}
    failures: dict[str, str] = {}
    for spec in candidate_specs():
        key = candidate_key(spec)
        group_scores = []
        try:
            for train, validation, y_train, y_validation in fold_targets:
                estimator = make_estimator(spec)
                estimator.fit(X.iloc[train], y_train)
                predicted = np.asarray(estimator.predict(X.iloc[validation]), dtype=float)
                for group in np.unique(groups[validation]):
                    mask = groups[validation] == group
                    group_scores.append(float(np.mean(np.abs(predicted[mask] - y_validation[mask]))))
            scores[key] = float(np.mean(group_scores))
        except (ValueError, TypeError) as exc:
            scores[key] = None
            failures[key] = str(exc)
    eligible = {key: value for key, value in scores.items() if value is not None}
    if not eligible:
        return Selection({"name": "dummy_median"}, scores,
                         "fixed_baseline_no_eligible_tuning", tuple(calibrations), failures)
    winner = choose_candidate(eligible)
    selected = next(spec for spec in candidate_specs() if candidate_key(spec) == winner)
    return Selection(selected, scores, "selected", tuple(calibrations), failures)


def evaluate_outer(X: pd.DataFrame, raw: pd.DataFrame, reports: NDArray[np.float64],
                   groups: NDArray) -> list[dict]:
    """Evaluate the inner-selection procedure on untouched held-out groups."""
    outcomes = []
    for train, test in outer_splits(groups):
        label = str(groups[test][0])
        try:
            selected = select_candidate(X.iloc[train], raw.iloc[train], reports[train], groups[train])
            calibration = PopulationCalibrator.fit(raw.iloc[train])
            y_train = calibration.fused(raw.iloc[train], reports[train])
            y_test = calibration.fused(raw.iloc[test], reports[test])
            estimator = make_estimator(selected.candidate)
            estimator.fit(X.iloc[train], y_train)
            predicted = np.asarray(estimator.predict(X.iloc[test]), dtype=float)
            valence_mae, arousal_mae, mean_mae = group_mae(predicted, y_test, groups[test])
            baselines = {}
            for name in ("dummy_median", "dummy_mean"):
                baseline = make_estimator({"name": name})
                baseline.fit(X.iloc[train], y_train)
                baseline_prediction = np.asarray(baseline.predict(X.iloc[test]), dtype=float)
                axis_one, axis_two, average = group_mae(
                    baseline_prediction, y_test, groups[test])
                baselines[name] = {"valence_mae": axis_one, "arousal_mae": axis_two,
                                   "mean_mae": average}
            r2 = {}
            for axis, name in enumerate(("valence", "arousal")):
                truth = y_test[:, axis]
                if len(truth) >= 2 and np.var(truth) > 1e-12:
                    r2[name] = float(1 - np.sum((truth - predicted[:, axis]) ** 2) /
                                     np.sum((truth - np.mean(truth)) ** 2))
                else:
                    r2[name] = None
            outcomes.append({"group": label, "status": "evaluated", "train_indices": train.tolist(),
                             "test_indices": test.tolist(), "selection": selected.candidate,
                             "selection_status": selected.status, "valence_mae": valence_mae,
                             "arousal_mae": arousal_mae, "mean_mae": mean_mae,
                             "r2_valence": r2["valence"], "r2_arousal": r2["arousal"],
                             "baseline_median_mae": baselines["dummy_median"]["mean_mae"],
                             "baseline_mean_mae": baselines["dummy_mean"]["mean_mae"],
                             "baselines": baselines,
                             "inner_selection": {
                                 "scores": selected.scores,
                                 "calibrations": selected.inner_fold_calibrations,
                                 "ineligibility_reasons": selected.ineligibility_reasons,
                             }})
        except (CalibrationUnavailable, ValueError) as exc:
            outcomes.append({"group": label, "status": "unavailable",
                             "train_indices": train.tolist(), "test_indices": test.tolist(),
                             "reason": str(exc)})
    return outcomes


def _permuted_training_rooms(X: pd.DataFrame, groups: NDArray,
                             rng: np.random.Generator) -> pd.DataFrame:
    """Move whole observed room-attribute vectors, preserving trial group labels."""
    room_ids = np.unique(groups)
    source = {}
    for room in room_ids:
        members = X.loc[groups == room]
        if len(members.drop_duplicates()) != 1:
            raise ValueError(f"room {room} has inconsistent source attributes")
        source[room] = members.iloc[0].copy()
    shuffled = rng.permutation(room_ids)
    output = X.copy()
    for destination, origin in zip(room_ids, shuffled, strict=True):
        output.loc[groups == destination, :] = source[origin].to_numpy()
    return output


def spatial_permutation_draw(X: pd.DataFrame, raw: pd.DataFrame,
                             reports: NDArray[np.float64], room_groups: NDArray,
                             *, draw: int, seed: int = 2718) -> dict:
    """One full-refit null draw across frozen held-out-room folds."""
    if draw < 0:
        raise ValueError("negative permutation draw")
    rng = np.random.default_rng(np.random.SeedSequence([seed, draw]))
    folds = []
    for train, test in outer_splits(room_groups):
        room = str(room_groups[test][0])
        try:
            shuffled = _permuted_training_rooms(X.iloc[train], room_groups[train], rng)
            selected = select_candidate(shuffled, raw.iloc[train], reports[train],
                                        room_groups[train])
            calibration = PopulationCalibrator.fit(raw.iloc[train])
            y_train = calibration.fused(raw.iloc[train], reports[train])
            y_test = calibration.fused(raw.iloc[test], reports[test])
            estimator = make_estimator(selected.candidate)
            estimator.fit(shuffled, y_train)
            prediction = np.asarray(estimator.predict(X.iloc[test]), dtype=float)
            valence, arousal, mean = group_mae(prediction, y_test, room_groups[test])
            folds.append({"group": room, "status": "evaluated", "candidate": selected.candidate,
                          "selection_status": selected.status, "valence_mae": valence,
                          "arousal_mae": arousal, "mean_mae": mean})
        except (CalibrationUnavailable, ValueError, TypeError) as exc:
            folds.append({"group": room, "status": "unavailable", "reason": str(exc)})
    evaluated = [fold for fold in folds if fold["status"] == "evaluated"]
    return {"draw": draw, "seed": seed, "folds": folds,
            "status": "evaluated" if len(evaluated) == len(folds) and folds else "unavailable",
            "mean_mae": float(np.mean([fold["mean_mae"] for fold in evaluated]))
            if len(evaluated) == len(folds) and folds else None}


def _room_subsets(rooms: list[str], k: int, rng: np.random.Generator) -> list[tuple[str, ...]]:
    all_count = comb(len(rooms), k)
    if all_count <= 100:
        return list(combinations(rooms, k))
    chosen: set[tuple[str, ...]] = set()
    while len(chosen) < 100:
        chosen.add(tuple(sorted(rng.choice(rooms, size=k, replace=False).tolist())))
    return sorted(chosen)


def room_learning_curve(X: pd.DataFrame, raw: pd.DataFrame,
                        reports: NDArray[np.float64], room_groups: NDArray,
                        *, seed: int = 2718) -> dict:
    """Unique seeded room subsets; every candidate is selected within its training rooms."""
    rooms = sorted(str(value) for value in np.unique(room_groups))
    result = {"seed": seed, "rooms": rooms, "points": [],
              "note": "Overlapping subsets are descriptive, not independent repetitions."}
    if len(rooms) < 5:
        return {**result, "status": "unavailable_insufficient_rooms"}
    rng = np.random.default_rng(seed)
    for k in range(4, len(rooms)):
        subsets = []
        for training_rooms in _room_subsets(rooms, k, rng):
            train = np.flatnonzero(np.isin(room_groups, training_rooms))
            test = np.flatnonzero(~np.isin(room_groups, training_rooms))
            try:
                calibration = PopulationCalibrator.fit(raw.iloc[train])
                y_train = calibration.fused(raw.iloc[train], reports[train])
                y_test = calibration.fused(raw.iloc[test], reports[test])
                selected = select_candidate(X.iloc[train], raw.iloc[train],
                                            reports[train], room_groups[train])
                estimator = make_estimator(selected.candidate)
                estimator.fit(X.iloc[train], y_train)
                prediction = np.asarray(estimator.predict(X.iloc[test]), dtype=float)
                valence, arousal, mean = group_mae(prediction, y_test, room_groups[test])
                baseline = make_estimator({"name": "dummy_median"})
                baseline.fit(X.iloc[train], y_train)
                baseline_prediction = np.asarray(baseline.predict(X.iloc[test]), dtype=float)
                _, _, baseline_mae = group_mae(baseline_prediction, y_test, room_groups[test])
                subsets.append({"training_rooms": training_rooms,
                                "test_rooms": sorted(set(room_groups[test])),
                                "status": "evaluated", "candidate": selected.candidate,
                                "selection_status": selected.status,
                                "valence_mae": valence, "arousal_mae": arousal,
                                "mean_mae": mean, "baseline_median_mae": baseline_mae})
            except (CalibrationUnavailable, ValueError, TypeError) as exc:
                subsets.append({"training_rooms": training_rooms,
                                "test_rooms": sorted(set(room_groups[test])),
                                "status": "unavailable", "reason": str(exc)})
        evaluated = [item for item in subsets if item["status"] == "evaluated"]
        result["points"].append({"training_room_count": k, "subsets": subsets,
                                 "evaluated_subsets": len(evaluated),
                                 "mean_mae": float(np.mean([item["mean_mae"] for item in evaluated]))
                                 if evaluated else None,
                                 "baseline_median_mae": float(np.mean([
                                     item["baseline_median_mae"] for item in evaluated]))
                                 if evaluated else None})
    result["status"] = "descriptive"
    return result
