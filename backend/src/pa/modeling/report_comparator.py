"""Research-only self-report comparator, separate by elicitation experiment."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from numpy.typing import NDArray
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from pa.config import RESULTS
from pa.features.builder import FEATURE_ORDER, build_features
from pa.features.schema import RoomInput
from pa.io.checkpoint import require_science_checkpoint
from pa.io.metadata import load_rooms
from pa.modeling.evaluate import group_mae, make_estimator
from pa.modeling.splits import (
    candidate_key,
    candidate_specs,
    choose_candidate,
    inner_splits,
    outer_splits,
)

COMMON_FEATURE_ORDER = tuple(name for name in FEATURE_ORDER if name not in
                             {"walkable_floor_area", "space_type", "walkable_floor_ratio"})


def _estimator(spec: dict, columns: tuple[str, ...]) -> Pipeline:
    """Reuse candidate family while excluding E2 attributes never recorded."""
    numeric = Pipeline([("impute", SimpleImputer(strategy="median", add_indicator=True,
                                                keep_empty_features=True)),
                        ("scale", StandardScaler())])
    categorical = Pipeline([("impute", SimpleImputer(strategy="most_frequent")),
                            ("encode", OneHotEncoder(handle_unknown="ignore"))])
    preprocess = ColumnTransformer([
        ("numeric", numeric, [name for name in columns if name != "day_or_night" and
                              name != "space_type"]),
        ("categorical", categorical, [name for name in columns if name in
                                      {"day_or_night", "space_type"}]),
    ])
    return Pipeline([("preprocess", preprocess),
                     ("model", make_estimator(spec).named_steps["model"])])


def build_report_cohort(affect_detail: dict, spatial: list[dict], experiment: int) -> tuple:
    if experiment not in (2, 3):
        raise ValueError("self-report spatial comparator is E2/E3 separate-first")
    by_room = {row["room_id"]: row for row in spatial if row["experiment"] == experiment}
    columns = COMMON_FEATURE_ORDER if experiment == 2 else FEATURE_ORDER
    rows = []
    for trial in affect_detail["trials"]:
        if trial["experiment"] != experiment:
            continue
        axes = trial["subjective"]
        if axes["valence"] is None or axes["arousal"] is None:
            continue
        source = by_room.get(trial["room_id"])
        if source is None:
            raise ValueError(f"missing room for {trial['id']}")
        room = RoomInput.model_validate({name: source.get(name) for name in RoomInput.model_fields})
        features = build_features(room)
        rows.append((trial["id"], trial["room_id"], trial["participant_id"],
                     [axes["valence"], axes["arousal"]],
                     {name: features[name] for name in columns}))
    ids = [row[0] for row in rows]
    return (ids, pd.DataFrame([row[4] for row in rows], columns=columns),
            np.asarray([row[3] for row in rows], dtype=float).reshape((-1, 2)),
            np.asarray([row[1] for row in rows]), np.asarray([row[2] for row in rows]),
            columns)


def select_report_candidate(X: pd.DataFrame, y: NDArray[np.float64],
                            groups: NDArray, columns: tuple[str, ...]) -> dict:
    folds = inner_splits(groups)
    if not folds:
        return {"candidate": {"name": "dummy_median"},
                "status": "fixed_baseline_insufficient_groups", "scores": {}}
    scores = {}
    for spec in candidate_specs():
        per_group = []
        try:
            for train, validation in folds:
                estimator = _estimator(spec, columns)
                estimator.fit(X.iloc[train], y[train])
                prediction = np.asarray(estimator.predict(X.iloc[validation]), dtype=float)
                for group in np.unique(groups[validation]):
                    mask = groups[validation] == group
                    per_group.append(float(np.mean(np.abs(prediction[mask] - y[validation][mask]))))
            scores[candidate_key(spec)] = float(np.mean(per_group))
        except (ValueError, TypeError):
            scores[candidate_key(spec)] = None
    eligible = {key: score for key, score in scores.items() if score is not None}
    if not eligible:
        return {"candidate": {"name": "dummy_median"},
                "status": "fixed_baseline_no_eligible_tuning", "scores": scores}
    winner = choose_candidate(eligible)
    return {"candidate": next(spec for spec in candidate_specs()
                              if candidate_key(spec) == winner),
            "status": "selected", "scores": scores}


def _outer(X: pd.DataFrame, y: NDArray[np.float64], groups: NDArray,
           columns: tuple[str, ...]) -> list[dict]:
    folds = []
    for train, test in outer_splits(groups):
        selected = select_report_candidate(X.iloc[train], y[train], groups[train], columns)
        estimator = _estimator(selected["candidate"], columns)
        estimator.fit(X.iloc[train], y[train])
        prediction = np.asarray(estimator.predict(X.iloc[test]), dtype=float)
        valence, arousal, mean = group_mae(prediction, y[test], groups[test])
        baselines = {}
        for baseline_name in ("dummy_median", "dummy_mean"):
            baseline = _estimator({"name": baseline_name}, columns)
            baseline.fit(X.iloc[train], y[train])
            baseline_prediction = np.asarray(baseline.predict(X.iloc[test]), dtype=float)
            _, _, baseline_mae = group_mae(baseline_prediction, y[test], groups[test])
            baselines[baseline_name] = {"mean_mae": baseline_mae,
                                        "prediction": baseline_prediction.tolist()}
        folds.append({"group": str(groups[test][0]), "train_indices": train.tolist(),
                      "test_indices": test.tolist(), "selection": selected,
                      "valence_mae": valence, "arousal_mae": arousal,
                      "mean_mae": mean, "baseline_mae": {
                          name: value["mean_mae"] for name, value in baselines.items()},
                      "baseline_predictions": {
                          name: value["prediction"] for name, value in baselines.items()},
                      "prediction": prediction.tolist(), "observed": y[test].tolist()})
    return folds


def compare_reports(affect_detail: dict, spatial: list[dict]) -> dict:
    experiments = []
    for experiment in (2, 3):
        ids, X, y, rooms, people, columns = build_report_cohort(affect_detail, spatial,
                                                                experiment)
        result = {"experiment": experiment, "target_type": "original_signed_self_report",
                  "deployment": "research_only", "rows": len(ids), "ids": ids,
                  "rooms": len(set(rooms)), "participants": len(set(people)),
                  "features": list(columns), "status": "unavailable_insufficient_groups"}
        if len(set(rooms)) >= 2 and len(set(people)) >= 2 and len(ids) >= 3:
            result["evaluation"] = {}
            for question, groups in (("room", rooms), ("subject", people)):
                folds = _outer(X, y, groups, columns)
                result["evaluation"][question] = {
                    "folds": folds,
                    "mean_mae": float(np.mean([fold["mean_mae"] for fold in folds])),
                    "median_baseline_mae": float(np.mean([
                        fold["baseline_mae"]["dummy_median"] for fold in folds])),
                    "mean_baseline_mae": float(np.mean([
                        fold["baseline_mae"]["dummy_mean"] for fold in folds])),
                }
            result["status"] = "evaluated"
        experiments.append(result)
    return {"schema_version": "1.0.0", "method_version": affect_detail["method_version"],
            "approved_spec_sha256": affect_detail["approved_spec_sha256"],
            "experiments": experiments,
            "pooling": "not_performed_different_elicitation",
            "note": "Self-report comparator uses all eligible source ratings independently of physiology; E2 drops independent attributes never recorded and is research-only."}


def write_report_comparator(affect_path: Path = RESULTS / "affect_detail.json",
                            destination: Path = RESULTS / "self_report_comparator.json") -> dict:
    require_science_checkpoint()
    result = compare_reports(json.loads(affect_path.read_text()), load_rooms())
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    return result
