"""Frozen full-attribute cohort, grouped evaluation and final artifact selection."""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from numpy.typing import NDArray

from pa.config import MODEL, RESULTS
from pa.features.schema import RoomInput
from pa.io.checkpoint import require_science_checkpoint
from pa.io.metadata import load_rooms
from pa.modeling.artifact import build_metadata, save_artifact
from pa.modeling.evaluate import evaluate_outer, make_estimator, select_candidate
from pa.modeling.predict import feature_frame
from pa.modeling.targets import COMPONENTS, CalibrationUnavailable, PopulationCalibrator
from pa.results.schemas import MetricRecord, ModelRecord
from pa.signals.common import decisions


@dataclass(frozen=True)
class Cohort:
    ids: tuple[str, ...]
    X: pd.DataFrame
    raw: pd.DataFrame
    reports: NDArray[np.float64]
    room_groups: NDArray
    subject_groups: NDArray
    exclusions: dict[str, int]


def build_cohort(affect_detail: dict, spatial: list[dict]) -> Cohort:
    room_by_id = {room["room_id"]: room for room in spatial if room["experiment"] == 3}
    if len(room_by_id) != sum(room["experiment"] == 3 for room in spatial):
        raise ValueError("duplicate Experiment 3 room identity")
    rooms: list[RoomInput] = []
    raw_rows = []
    reports = []
    ids = []
    room_groups, subject_groups = [], []
    exclusions: Counter[str] = Counter()
    for row in affect_detail["trials"]:
        if row["experiment"] != 3:
            exclusions["not_experiment_3"] += 1
            continue
        missing = [name for name in COMPONENTS if row[name] is None]
        if missing:
            exclusions["missing_raw_component:" + ",".join(missing)] += 1
            continue
        axes = row["subjective"]
        if axes["valence"] is None or axes["arousal"] is None:
            exclusions["missing_original_rating_axis"] += 1
            continue
        source_room = room_by_id.get(row["room_id"])
        if source_room is None:
            exclusions["missing_room_metadata"] += 1
            continue
        room_input = {name: source_room[name] for name in RoomInput.model_fields}
        if any(value is None for value in room_input.values()):
            exclusions["incomplete_room_attributes"] += 1
            continue
        room = RoomInput.model_validate(room_input)
        rooms.append(room)
        raw_rows.append({name: row[name] for name in COMPONENTS})
        reports.append((axes["valence"], axes["arousal"]))
        ids.append(row["id"])
        room_groups.append(row["room_id"])
        subject_groups.append(row["participant_id"])
    return Cohort(tuple(ids), feature_frame(rooms), pd.DataFrame(raw_rows, columns=COMPONENTS),
                  np.asarray(reports, dtype=float).reshape((-1, 2)),
                  np.asarray(room_groups), np.asarray(subject_groups), dict(exclusions))


def _aggregate(folds: list[dict]) -> dict:
    evaluated = [fold for fold in folds if fold["status"] == "evaluated"]
    metric_names = ("valence_mae", "arousal_mae", "mean_mae",
                    "baseline_median_mae", "baseline_mean_mae")
    return {"evaluated_folds": len(evaluated), "unavailable_folds": len(folds) - len(evaluated),
            "mean_metrics": {name: (float(np.mean([fold[name] for fold in evaluated]))
                                    if evaluated else None) for name in metric_names},
            "unavailable_reasons": dict(Counter(fold["reason"] for fold in folds
                                                if fold["status"] == "unavailable"))}


def _model_record(result: dict) -> ModelRecord:
    status = result["status"]
    evaluation = result["evaluation"]
    metrics = []
    for group in ("room", "subject"):
        aggregate = evaluation[group]["aggregate"]
        for name, value in aggregate["mean_metrics"].items():
            metrics.append(MetricRecord(name=name, value=value, unit="constructed-coordinate MAE",
                                        n=aggregate["evaluated_folds"], group=f"held_out_{group}"))
    explanation = ("The complete Experiment 3 raw-component cohort is too sparse for a fitted "
                   "artifact under the frozen calibration rule."
                   if status == "unavailable" else
                   "Experimental population-constructed coordinate prediction from original "
                   "room attributes; grouped errors describe this small retrospective pilot.")
    return ModelRecord(status=status, explanation=explanation, metrics=metrics,
                       limitations=result["limitations"],
                       artifact_version="1.0.0" if status != "unavailable" else None)


def evaluate_and_fit(cohort: Cohort, artifact_dir: Path = MODEL) -> dict:
    limitations = [
        "Acquisition rate, channel units/reference and physiological validity remain unconfirmed.",
        "Only observed Experiment 3 complete raw-component trials enter this model.",
        "Small repeated participant/room sample; no causal or clinical interpretation.",
        "No calibrated prediction interval or individual response guarantee is available.",
    ]
    evaluation = {}
    for name, labels in (("room", cohort.room_groups), ("subject", cohort.subject_groups)):
        folds = evaluate_outer(cohort.X, cohort.raw, cohort.reports, labels)
        evaluation[name] = {"folds": folds, "aggregate": _aggregate(folds)}
    result = {"schema_version": "1.0.0", "method_version": decisions()["version"],
              "approved_spec_sha256": decisions()["approved_spec_sha256"],
              "target_type": "E3_complete_fusion_population_calibrated",
              "target_mapping": ("FAA and equal alpha-suppression/engagement EEG arousal; "
                                 "equal EEG/HR physiology arousal; 0.5 physiology + 0.5 E3 reports"),
              "cohort": {"rows": len(cohort.ids), "ids": list(cohort.ids),
                         "rooms": len(set(cohort.room_groups)),
                         "participants": len(set(cohort.subject_groups)),
                         "exclusions": cohort.exclusions},
              "evaluation": evaluation, "status": "unavailable", "final_selection": None,
              "limitations": limitations}
    if len(cohort.ids) < 3:
        result["unavailable_reason"] = "fewer than three complete raw-component trials"
    else:
        try:
            selected = select_candidate(cohort.X, cohort.raw, cohort.reports,
                                        cohort.room_groups)
            calibration = PopulationCalibrator.fit(cohort.raw)
            target = calibration.fused(cohort.raw, cohort.reports)
            estimator = make_estimator(selected.candidate)
            estimator.fit(cohort.X, target)
            room_metrics = evaluation["room"]["aggregate"]["mean_metrics"]
            if selected.candidate["name"].startswith("dummy_"):
                status = "baseline_only"
            elif (room_metrics["mean_mae"] is None or
                  room_metrics["baseline_median_mae"] is None or
                  room_metrics["mean_mae"] >= room_metrics["baseline_median_mae"]):
                status = "not_better_than_baseline"
            else:
                status = "experimental"
            result["status"] = status
            result["final_selection"] = {"candidate": selected.candidate,
                                         "status": selected.status, "scores": selected.scores,
                                         "inner_fold_calibrations": selected.inner_fold_calibrations,
                                         "ineligibility_reasons": selected.ineligibility_reasons,
                                         "target_calibration": {"centers": calibration.centers,
                                                                "scales": calibration.scales,
                                                                "component_order": list(COMPONENTS),
                                                                "mapping": result["target_mapping"]}}
            metadata = build_metadata(
                model_status=status,
                training_scope={"cohort": "experiment_03_complete_raw_components_full_room_attributes",
                                "trial_ids": list(cohort.ids), "participants": result["cohort"]["participants"],
                                "rooms": result["cohort"]["rooms"],
                                "final_selection": result["final_selection"]},
                metrics={name: info["aggregate"] for name, info in evaluation.items()},
                limitations=limitations)
            save_artifact(estimator, metadata, artifact_dir)
        except (CalibrationUnavailable, ValueError) as exc:
            result["unavailable_reason"] = str(exc)
    if result["status"] == "unavailable":
        artifact_dir.mkdir(parents=True, exist_ok=True)
        for path in (artifact_dir / "model.joblib", artifact_dir / "metadata.json"):
            path.unlink(missing_ok=True)
        (artifact_dir / "unavailable.json").write_text(json.dumps({
            "status": "unavailable", "reason": result.get("unavailable_reason"),
            "cohort": result["cohort"]}, indent=2) + "\n")
    result["model_record"] = _model_record(result).model_dump(mode="json")
    return result


def write_model_evaluation(affect_path: Path = RESULTS / "affect_detail.json",
                           destination: Path = RESULTS / "model_evaluation.json") -> dict:
    from pa.modeling.evidence import outer_prediction_evidence

    require_science_checkpoint()
    cohort = build_cohort(json.loads(affect_path.read_text()), load_rooms())
    result = evaluate_and_fit(cohort)
    result["outer_prediction_evidence"] = outer_prediction_evidence(cohort, result["evaluation"])
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    return result
