"""Auditable comparison summary for delegated CP-C review and research pages."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

from pa.config import MODEL, RESULTS, ROOT
from pa.io.checkpoint import require_science_checkpoint
from pa.modeling.artifact import load_artifact

INPUTS = ("model_evaluation.json", "self_report_comparator.json", "rating_research.json",
          "validity.json", "model_null.json", "model_learning_curve.json")


def build_model_poc(products: dict[str, dict], metadata: dict) -> dict:
    model = products["model_evaluation.json"]
    comparator = products["self_report_comparator.json"]
    ratings = products["rating_research.json"]
    validity = products["validity.json"]
    null = products["model_null.json"]
    curve = products["model_learning_curve.json"]
    if null.get("status") != "complete" or len(null.get("null_mean_mae", [])) != 1000:
        raise ValueError("CP-C summary requires 1,000 complete full-refit null draws")
    subsets = sum(len(point["subsets"]) for point in curve.get("points", []))
    if len(set(null["cohort"]["trial_ids"]) - set(model["cohort"]["ids"])) or \
            set(null["cohort"]["trial_ids"]) != set(model["cohort"]["ids"]):
        raise ValueError("null/model cohort trial identities disagree")
    if subsets != 455 or curve.get("cohort_ids") != model["cohort"]["ids"]:
        raise ValueError("learning curve is incomplete or uses different trial identities")
    room = model["evaluation"]["room"]["aggregate"]
    person = model["evaluation"]["subject"]["aggregate"]
    room_metrics = room["mean_metrics"]
    spatial_null = np.asarray(null["null_mean_mae"], dtype=float)
    if not np.isfinite(spatial_null).all():
        raise ValueError("nonfinite spatial null draw")
    report_comparison = []
    for experiment in comparator["experiments"]:
        report_comparison.append({"experiment": experiment["experiment"],
                                  "target_type": experiment["target_type"],
                                  "deployment": experiment["deployment"],
                                  "trials": experiment["rows"],
                                  "participants": experiment["participants"],
                                  "rooms": experiment["rooms"],
                                  "features": experiment["features"],
                                  "status": experiment["status"],
                                  "room_question": {key: experiment["evaluation"]["room"][key]
                                                    for key in ("mean_mae", "median_baseline_mae",
                                                                "mean_baseline_mae")},
                                  "person_question": {key: experiment["evaluation"]["subject"][key]
                                                      for key in ("mean_mae", "median_baseline_mae",
                                                                  "mean_baseline_mae")}})
    room_rating = []
    for entry in ratings["analyses"]:
        if entry["experiment"] not in (2, 3):
            continue
        crossed = entry["crossed_additive"]
        relative = entry["known_room_relative_transfer"]
        room_rating.append({"experiment": entry["experiment"], "axis": entry["axis"],
                            "trials": len(entry["source_rows"]),
                            "room_incremental_share": crossed.get("room_incremental_share"),
                            "person_share": crossed.get("person_share",
                                                       1-crossed["person_only_residual_share"]),
                            "residual_share": crossed.get("residual_share"),
                            "unique_rater_partitions": len(entry["rater_partitions"].get("partitions", [])),
                            "known_room_relative_mae": relative.get("observed_mean_mae"),
                            "relative_zero_baseline_mae": relative.get("zero_baseline_mean_mae"),
                            "rating_null_draws": len(crossed.get("null_room_share", [])),
                            "transfer_null_draws": len(relative.get("null_mean_mae", []))})
    observed = room_metrics["mean_mae"]
    if not np.isclose(observed, null["observed"]["mean_mae"], atol=1e-12, rtol=1e-12):
        raise ValueError("observed room MAE differs between evaluation and negative control")
    return {"schema_version": "1.0.0", "method_version": model["method_version"],
            "approved_spec_sha256": model["approved_spec_sha256"],
            "source_manifest_sha256": metadata["dataset_manifest_sha256"],
            "model_status": model["status"], "final_candidate": model["final_selection"]["candidate"],
            "fused_target": {"type": model["target_type"], "mapping": model["target_mapping"],
                             "E3_trials": model["cohort"]["rows"],
                             "participants": model["cohort"]["participants"],
                             "rooms": model["cohort"]["rooms"]},
            "fused_grouped_comparison": {
                "held_out_room": room_metrics, "room_folds": room["evaluated_folds"],
                "held_out_person": person["mean_metrics"], "person_folds": person["evaluated_folds"],
                "prediction_evidence": "artifacts/results/model_evaluation.json#/outer_prediction_evidence"},
            "self_report_only_research_comparators": report_comparison,
            "rating_and_relative_transfer_questions": room_rating,
            "component_relationships": [{"experiment": item["experiment"],
                                         "left": item["left"], "right": item["right"],
                                         "trials": item["trials"],
                                         "participants": item["participants"],
                                         "equal_participant_mean_rho": item["equal_participant_mean_rho"],
                                         "status": item["status"]}
                                        for item in validity["comparisons"]],
            "spatial_negative_control": {"status": "descriptive", "draws": 1000,
                                         "observed_mae": observed,
                                         "null_median_mae": float(np.median(spatial_null)),
                                         "null_2_5_percentile_mae": float(np.quantile(spatial_null, 0.025)),
                                         "null_97_5_percentile_mae": float(np.quantile(spatial_null, 0.975)),
                                         "interpretation": "whole training-room attribute shuffle with full refit; not a calibrated population p-value"},
            "room_learning_curve": {"status": curve["status"], "unique_subsets": subsets,
                                    "points": [{"training_room_count": item["training_room_count"],
                                                "subsets": len(item["subsets"]),
                                                "evaluated_subsets": item["evaluated_subsets"],
                                                "mean_mae": item["mean_mae"],
                                                "baseline_median_mae": item["baseline_median_mae"]}
                                               for item in curve["points"]],
                                    "interpretation": "overlapping descriptive room subsets, not independent replications"},
            "artifact": {"model_sha256": metadata["model_sha256"],
                         "code_tree_sha256": metadata["code_tree_sha256"],
                         "decisions_sha256": metadata["decisions_sha256"],
                         "uv_lock_sha256": metadata["uv_lock_sha256"]},
            "limitations": model["limitations"] + [
                "Final Studio fit is baseline-only; no spatial gain or personal-accuracy claim.",
                "E2 and E3 report-only comparators use different targets and are not interchangeable with fused error.",
                "Neither null distribution nor learning subsets define a population p-value or forecasted improvement."],
            "source_artifacts": {}}


def write_model_poc(destination: Path = RESULTS / "model_poc.json") -> dict:
    require_science_checkpoint()
    load_artifact()
    products = {name: json.loads((RESULTS / name).read_text()) for name in INPUTS}
    metadata_path = MODEL / "metadata.json"
    metadata = json.loads(metadata_path.read_text())
    result = build_model_poc(products, metadata)
    result["source_artifacts_digest_rule"] = (
        "Canonical sorted JSON; omit only wall-clock run timing in model_null/model_learning_curve "
        "and checkout revision/status in model metadata.")
    result["source_artifacts"] = {}
    for name in INPUTS:
        source = dict(products[name])
        if name == "model_null.json":
            for field in ("started_at_utc", "updated_at_utc", "completed_at_utc",
                          "elapsed_wall_seconds"):
                source.pop(field, None)
        elif name == "model_learning_curve.json":
            source.pop("elapsed_wall_seconds", None)
        canonical = json.dumps(source, sort_keys=True, separators=(",", ":"),
                               allow_nan=False).encode()
        result["source_artifacts"][name] = hashlib.sha256(canonical).hexdigest()
    metadata_canonical = {key: value for key, value in metadata.items()
                          if key not in ("base_git_revision", "source_snapshot_status")}
    result["source_artifacts"]["artifacts/model/metadata.json"] = hashlib.sha256(
        json.dumps(metadata_canonical, sort_keys=True, separators=(",", ":"),
                   allow_nan=False).encode()).hexdigest()
    result["source_artifacts"]["data/MANIFEST.sha256"] = hashlib.sha256(
        (ROOT / "data/MANIFEST.sha256").read_bytes()).hexdigest()
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    return result
