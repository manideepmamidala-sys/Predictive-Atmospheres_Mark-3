"""Descriptive summaries with explicit crossed subject/room denominators."""

from __future__ import annotations

import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

from pa.config import RESULTS
from pa.io.checkpoint import require_science_checkpoint
from pa.io.metadata import load_rooms

VALIDITY_SEED = 2718
VALIDITY_BOOTSTRAP_DRAWS = 2000
VALIDITY_PAIRS = (
    ("eeg_composite", "report_arousal"),
    ("alpha_suppression", "report_arousal"),
    ("engagement", "report_arousal"),
    ("heart_rate", "report_arousal"),
    ("eeg_composite", "heart_rate"),
    ("faa", "report_valence"),
    ("ocular", "report_arousal"),
    ("ocular", "heart_rate"),
    ("muscle", "report_arousal"),
    ("muscle", "heart_rate"),
)


def _validity_value(row: dict, name: str) -> float | None:
    construction = row["construction"]
    components = row["normalized_components"]
    if name == "eeg_composite":
        return construction.get("eeg_arousal")
    if name in ("alpha_suppression", "engagement", "faa"):
        return components.get(name)
    if name == "heart_rate":
        return components.get("heart_rate_bpm")
    if name == "report_arousal":
        return row["subjective"]["arousal"]
    if name == "report_valence":
        return row["subjective"]["valence"]
    if name == "muscle":
        return row.get("muscle_activity")
    if name == "ocular":
        return row.get("ocular_activity")
    raise ValueError(f"unknown validity measure {name}")


def _person_spearman(values: list[tuple[float, float]]) -> float | None:
    if len(values) < 3:
        return None
    paired = np.asarray(values, dtype=float)
    if len(np.unique(paired[:, 0])) < 2 or len(np.unique(paired[:, 1])) < 2:
        return None
    return float(spearmanr(paired[:, 0], paired[:, 1]).statistic)


def _validity_pair(rows: list[dict], experiment: int, left: str, right: str) -> dict:
    by_person: dict[str, list[tuple[float, float]]] = defaultdict(list)
    rooms = set()
    for row in rows:
        if row["experiment"] != experiment:
            continue
        a, b = _validity_value(row, left), _validity_value(row, right)
        if _finite(a) and _finite(b):
            by_person[row["participant_id"]].append((a, b))
            rooms.add(row["room_id"])
    people = [{"participant_id": person, "n_trials": len(pairs),
               "spearman_rho": _person_spearman(pairs)}
              for person, pairs in sorted(by_person.items())]
    available = [item["spearman_rho"] for item in people
                 if item["spearman_rho"] is not None]
    result = {"experiment": experiment, "left": left, "right": right,
              "trials": sum(len(pairs) for pairs in by_person.values()),
              "participants": len(by_person), "rooms": len(rooms),
              "participant_results": people, "equal_participant_mean_rho": None,
              "interval_95": None, "interval_status": "interval_unavailable_insufficient_people",
              "bootstrap_unit": "participant_complete_observed_room_vector",
              "bootstrap_draws": VALIDITY_BOOTSTRAP_DRAWS}
    if not available:
        result["status"] = ("unavailable_detector_not_validated" if left == "ocular" else
                            "unavailable_few_or_constant_within_person_pairs")
        return result
    result["status"] = "descriptive"
    result["equal_participant_mean_rho"] = float(np.mean(available))
    if len(available) >= 4:
        rng = np.random.default_rng(VALIDITY_SEED)
        draws = np.mean(rng.choice(np.asarray(available),
                                   size=(VALIDITY_BOOTSTRAP_DRAWS, len(available)),
                                   replace=True), axis=1)
        result["interval_95"] = [float(value) for value in np.quantile(draws, [0.025, 0.975])]
        result["interval_status"] = "conditional_on_observed_rooms"
    return result


def _divergence(affect_detail: dict, experiment: int) -> list[dict]:
    records = []
    calibrations = affect_detail["descriptive_calibrations"]
    for row in affect_detail["trials"]:
        if row["experiment"] != experiment:
            continue
        key = f"E{experiment}:{row['participant_id']}"
        person = calibrations.get(key, {})
        raw = []
        for name in ("alpha_suppression", "engagement", "heart_rate_bpm"):
            calibration = person.get(name, {})
            value = row.get(name)
            if calibration.get("status") != "calibrated" or not _finite(value):
                raw.append(None)
            else:
                raw.append((value - calibration["center"]) / calibration["scale"])
        if any(value is None for value in raw):
            continue
        eeg_z = 0.5 * (raw[0] + raw[1])
        hr_z = raw[2]
        if eeg_z * hr_z < 0 and min(abs(eeg_z), abs(hr_z)) > 1:
            records.append({"trial_id": row["id"], "participant_id": row["participant_id"],
                            "room_id": row["room_id"], "eeg_robust_z": eeg_z,
                            "heart_rate_robust_z": hr_z,
                            "interpretation": "candidate disagreement; cause unknown"})
    return records


def validity_matrix(affect_detail: dict) -> dict:
    rows = affect_detail["trials"]
    return {"schema_version": "1.0.0", "method_version": affect_detail["method_version"],
            "approved_spec_sha256": affect_detail["approved_spec_sha256"],
            "qc_review_sha256": affect_detail.get("qc_review_sha256"),
            "comparisons": [_validity_pair(rows, experiment, left, right)
                            for experiment in (2, 3) for left, right in VALIDITY_PAIRS],
            "divergence": {str(experiment): _divergence(affect_detail, experiment)
                           for experiment in (2, 3)},
            "limitations": ["Approximate forehead EEG and wrist ECG candidates are not validated emotion measures.",
                            "Participant bootstrap intervals are conditional on the observed rooms.",
                            "E2 and E3 use different elicitation and are reported separately."]}


def write_validity(affect_path: Path = RESULTS / "affect_detail.json",
                   destination: Path = RESULTS / "validity.json") -> dict:
    require_science_checkpoint()
    result = validity_matrix(json.loads(affect_path.read_text()))
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    return result


def _finite(value: object) -> bool:
    return isinstance(value, (int, float)) and math.isfinite(value)


def group_summary(rows: list[dict], group_field: str, value_fields: tuple[str, ...]) -> list[dict]:
    """Averages describe observed records only; no trial-independent intervals."""
    groups: dict[object, list[dict]] = defaultdict(list)
    for row in rows:
        groups[row[group_field]].append(row)
    result = []
    for group, members in sorted(groups.items(), key=lambda item: str(item[0])):
        record = {group_field: group, "trials": len(members),
                  "participants": len({row["participant_id"] for row in members}),
                  "rooms": len({row["room_id"] for row in members}),
                  "experiments": sorted({row["experiment"] for row in members}),
                  "interval_status": "not_estimated_crossed_dependence"}
        for field in value_fields:
            values = [row.get(field) for row in members if _finite(row.get(field))]
            record[f"n_{field}"] = len(values)
            record[f"mean_{field}"] = float(np.mean(values)) if values else None
        result.append(record)
    return result


def room_level_association(rows: list[dict], predictor: str,
                           outcome: str, *, experiment: int) -> dict:
    """Room-level Pearson description only; no p-value or causal interpretation."""
    study = [row for row in rows if row["experiment"] == experiment]
    room = group_summary(study, "room_id", (predictor, outcome))
    pairs = [(record[f"mean_{predictor}"], record[f"mean_{outcome}"])
             for record in room if record[f"mean_{predictor}"] is not None
             and record[f"mean_{outcome}"] is not None]
    participant_count = len({row["participant_id"] for row in study
                             if _finite(row.get(predictor)) and _finite(row.get(outcome))})
    result = {"experiment": experiment, "predictor": predictor, "outcome": outcome,
              "unit": "room", "n_rooms": len(pairs), "n_participants": participant_count,
              "pearson_r": None,
              "interval": None, "p_value": None}
    if len(pairs) < 3:
        result["status"] = "unavailable_insufficient_rooms"
        return result
    values = np.asarray(pairs, dtype=float)
    if min(float(np.std(values[:, 0])), float(np.std(values[:, 1]))) <= 1e-12:
        result["status"] = "unavailable_constant_axis"
        return result
    result["status"] = ("descriptive_only_single_participant" if participant_count == 1
                        else "descriptive_only")
    result["pearson_r"] = float(np.corrcoef(values[:, 0], values[:, 1])[0, 1])
    return result


def analyze_affect(affect_detail: dict, spatial: list[dict]) -> dict:
    """Stratified descriptive output; all intervals and p-values remain unavailable."""
    room_by_id = {room["room_id"]: room for room in spatial}
    if len(room_by_id) != len(spatial):
        raise ValueError("duplicate spatial room identity")
    rows = []
    for source in affect_detail["trials"]:
        room = room_by_id.get(source["room_id"])
        if room is None or room["experiment"] != source["experiment"]:
            raise ValueError(f"missing or mismatched room for {source['id']}")
        construction = source["construction"]
        complete = construction["cohort"] == "complete_fusion"
        partial = construction["cohort"] == "partial_modality_fusion"
        rows.append({"experiment": source["experiment"],
                     "participant_id": source["participant_id"],
                     "room_id": source["room_id"],
                     "self_valence": construction["subjective"]["valence"],
                     "self_arousal": construction["subjective"]["arousal"],
                     "complete_fused_valence": (construction["fused"]["valence"]
                                                if complete else None),
                     "complete_fused_arousal": (construction["fused"]["arousal"]
                                                if complete else None),
                     "partial_fused_valence": (construction["fused"]["valence"]
                                               if partial else None),
                     "partial_fused_arousal": (construction["fused"]["arousal"]
                                               if partial else None),
                     "illuminance": room["illuminance"],
                     "cohort": construction["cohort"]})
    measures = ("self_valence", "self_arousal", "complete_fused_valence",
                "complete_fused_arousal", "partial_fused_valence", "partial_fused_arousal")
    associations = [room_level_association(rows, "illuminance", outcome,
                                           experiment=experiment)
                    for experiment in (2, 3)
                    for outcome in ("self_valence", "complete_fused_valence")]
    return {"schema_version": "1.0.0", "method_version": affect_detail["method_version"],
            "experiments": group_summary(rows, "experiment", measures),
            "rooms": group_summary(rows, "room_id", measures),
            "people": group_summary(rows, "participant_id", measures),
            "cohorts_by_experiment": affect_detail["cohorts"],
            "objective_subjective_disagreement": affect_detail[
                "objective_subjective_disagreement"],
            "associations": associations,
            "inference_status": "descriptive_only_crossed_dependence",
            "interval_status": "unavailable_no_validated_crossed_group_interval_method",
            "p_value_status": "not_computed"}


def write_analysis(affect_path: Path = RESULTS / "affect_detail.json",
                   destination: Path = RESULTS / "affect_analysis.json") -> dict:
    require_science_checkpoint()
    result = analyze_affect(json.loads(affect_path.read_text()), load_rooms())
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    return result
