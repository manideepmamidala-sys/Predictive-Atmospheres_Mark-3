"""Construct descriptive affect from gated signal evidence and original ratings."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from dataclasses import asdict
from pathlib import Path

from pa.affect.fusion import construct_affect
from pa.affect.normalization import descriptive_components
from pa.affect.ratings import subjective_axes
from pa.config import RESULTS, ROOT
from pa.io.checkpoint import load_reviewed_qc, require_science_checkpoint
from pa.io.metadata import Trial, load_trials
from pa.io.recordings import read_recording, recording_path
from pa.signals.common import decisions
from pa.signals.eeg import process_eeg


def construct_affect_detail(trials: list[Trial], signal_rows: list[dict],
                            review: dict | None = None) -> dict:
    signals = {(row["experiment"], row["participant_id"], row["room_id"]): row
               for row in signal_rows}
    if len(signals) != len(signal_rows) or len(signals) != len(trials):
        raise ValueError("signal and anchored-trial counts do not match")
    reviewed = ({row["trial_id"]: row for row in review["trials"]}
                if review is not None else None)
    if reviewed is not None and (len(reviewed) != len(trials) or
                                 set(reviewed) != {row["id"] for row in signal_rows}):
        raise ValueError("reviewed eligibility does not cover every anchored trial")
    rows = []
    for trial in trials:
        key = trial.experiment, trial.subject_id, trial.room_id
        evidence = signals.get(key)
        if evidence is None:
            raise ValueError(f"missing signal evidence for {key}")
        eeg, ecg = evidence["eeg"], evidence["ecg"]
        state = reviewed[evidence["id"]]["reviewed_eligibility"] if reviewed else None
        right_ok = (state["eeg_right"] if state else eeg.get("channel_qc", {}).get(
            "right", {}).get("eligible", eeg["valid"]))
        left_ok = (state["eeg_left"] if state else eeg.get("channel_qc", {}).get(
            "left", {}).get("eligible", eeg["valid"]))
        bilateral_ok = state["eeg_bilateral"] if state else eeg["valid"]
        eeg_features = eeg
        if reviewed and (right_ok != eeg.get("channel_qc", {}).get("right", {}).get("eligible") or
                         left_ok != eeg.get("channel_qc", {}).get("left", {}).get("eligible")):
            recording = read_recording(recording_path(trial))
            derived = process_eeg(recording.right_forehead, recording.left_forehead,
                                  recording.counter, evidence["primary_rate_hz"],
                                  allowed_channels=frozenset(name for name, ok in
                                                             (("right", right_ok), ("left", left_ok))
                                                             if ok))
            eeg_features = {"alpha_suppression": derived.alpha_suppression,
                            "engagement": derived.engagement,
                            "muscle_activity": derived.muscle_activity,
                            "arousal_channel_scope": derived.arousal_channel_scope}
        eeg_component_ok = (right_ok or left_ok) and (
            not reviewed or reviewed[evidence["id"]]["reviewed_disposition"]["eeg_trial"] == "accept" or
            right_ok != left_ok)
        hr_ok = state["ecg_hr"] if state else ecg["valid_hr"]
        rmssd_ok = state["ecg_rmssd"] if state else ecg["valid_rmssd"]
        rows.append({"id": evidence["id"], "experiment": trial.experiment,
                     "participant_id": trial.subject_id, "room_id": trial.room_id,
                     "comfort": trial.comfort, "subjective": subjective_axes(trial),
                     "faa": eeg["forehead_log_alpha_asymmetry"] if bilateral_ok else None,
                     "alpha_suppression": eeg_features.get("alpha_suppression")
                     if eeg_component_ok else None,
                     "engagement": eeg_features.get("engagement") if eeg_component_ok else None,
                     "muscle_activity": eeg_features.get("muscle_activity")
                     if eeg_component_ok else None,
                     "ocular_activity": None,
                     "ocular_activity_reason": eeg.get("ocular_activity_reason",
                                                       "unavailable_detector_not_validated"),
                     "eeg_channel_scope": eeg_features.get("arousal_channel_scope", "unavailable")
                     if eeg_component_ok else "unavailable",
                     "heart_rate_bpm": ecg["heart_rate_bpm"] if hr_ok else None,
                     "rmssd_ms": ecg["rmssd_ms"] if rmssd_ok else None,
                     "reviewed_eligibility": state,
                     "eligibility_source": "delegated_CP-B" if reviewed else "automated_unreviewed"})
    normalized, calibrations = descriptive_components(rows)
    alpha_grid = decisions()["affect"]["alpha_sensitivity"]
    output = []
    for row, components in zip(rows, normalized, strict=True):
        primary = construct_affect(components, row["subjective"])
        sensitivity = {str(alpha): asdict(construct_affect(
            components, row["subjective"], alpha)) for alpha in alpha_grid}
        disagreement = {axis: (primary.objective[axis] - primary.subjective[axis]
                               if primary.objective[axis] is not None and
                               primary.subjective[axis] is not None else None)
                        for axis in ("valence", "arousal")}
        output.append({**row, "normalized_components": components,
                       "construction": asdict(primary), "alpha_sensitivity": sensitivity,
                       "objective_minus_subjective": disagreement})
    cohorts = Counter((row["experiment"], row["construction"]["cohort"]) for row in output)
    disagreements = []
    for experiment in (1, 2, 3):
        for cohort in ("complete_fusion", "partial_modality_fusion", "partial_axis_overlap"):
            for axis in ("valence", "arousal"):
                paired = [row["objective_minus_subjective"][axis] for row in output
                          if row["experiment"] == experiment and
                          row["construction"]["cohort"] == cohort and
                          row["objective_minus_subjective"][axis] is not None]
                disagreements.append({"experiment": experiment, "cohort": cohort,
                                      "axis": axis, "n_pairs": len(paired),
                                      "mean_signed": sum(paired) / len(paired) if paired else None,
                                      "mean_absolute": (sum(abs(value) for value in paired) /
                                                        len(paired) if paired else None)})
    return {"schema_version": "1.0.0", "method_version": decisions()["version"],
            "approved_spec_sha256": decisions()["approved_spec_sha256"],
            "trials": output, "descriptive_calibrations": calibrations,
            "cohorts": [{"experiment": experiment, "cohort": cohort, "trials": count}
                        for (experiment, cohort), count in sorted(cohorts.items())],
            "objective_subjective_disagreement": disagreements}


def write_affect(signal_path: Path = RESULTS / "signals_detail.json",
                 destination: Path = RESULTS / "affect_detail.json") -> dict:
    require_science_checkpoint()
    signal_rows = json.loads(signal_path.read_text())["trials"]
    review = load_reviewed_qc()
    result = construct_affect_detail(load_trials(), signal_rows, review)
    result["qc_review_sha256"] = hashlib.sha256((ROOT / "artifacts/results/qc_review.json").read_bytes()).hexdigest()
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    return result
