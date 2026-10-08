"""Descriptive summaries with explicit crossed subject/room denominators."""

from __future__ import annotations

import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np

from pa.config import RESULTS
from pa.io.checkpoint import require_science_checkpoint
from pa.io.metadata import load_rooms


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
