"""Nested grouped model comparison with fold-fitted affect targets and preprocessing."""

from __future__ import annotations

from dataclasses import dataclass

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
