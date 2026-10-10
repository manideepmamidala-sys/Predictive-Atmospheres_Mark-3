"""Conditional-rate trial processing with inspectable modality and sensitivity evidence."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

import numpy as np

from pa.config import RESULTS, ROOT
from pa.io.checkpoint import require_science_checkpoint
from pa.io.metadata import Trial, load_trials
from pa.io.recordings import Recording, read_recording, recording_path
from pa.results.traces import ecg_window, eeg_window
from pa.signals.common import decisions
from pa.signals.ecg import ecg_review_examples, process_ecg
from pa.signals.eeg import experiment_amplitude_references, process_eeg


def process_trial(trial: Trial, recording: Recording,
                  amplitude_reference_raw_std: dict[str, float] | None = None) -> dict:
    """Compute all frozen scenarios from one original recording without default values."""
    cfg = decisions()
    rates = [cfg["rate"]["primary_hz"], *cfg["rate"]["sensitivity_hz"]]
    rate_results = []
    primary = None
    for rate in rates:
        eeg = process_eeg(recording.right_forehead, recording.left_forehead,
                          recording.counter, rate,
                          amplitude_reference_raw_std=amplitude_reference_raw_std)
        ecg = process_ecg(recording.wrist_ecg, rate, recording.counter)
        rate_results.append({"rate_hz": rate, "sample_duration_s": recording.samples / rate,
                             "eeg_valid": eeg.valid, "eeg_reasons": list(eeg.reasons),
                             "faa": eeg.forehead_log_alpha_asymmetry,
                             "beta_alpha": eeg.log_beta_alpha_ratio,
                             "alpha_suppression": eeg.alpha_suppression,
                             "engagement": eeg.engagement,
                             "muscle_activity": eeg.muscle_activity,
                             "ocular_activity_reason": eeg.ocular_activity_reason,
                             "arousal_channel_scope": eeg.arousal_channel_scope,
                             "ecg_valid_hr": ecg.valid_hr, "ecg_valid_rmssd": ecg.valid_rmssd,
                             "ecg_reasons": list(ecg.reasons),
                             "ecg_filterable_seconds": ecg.coverage["filterable_seconds"],
                             "ecg_valid_rr_seconds": ecg.coverage["valid_rr_seconds"],
                             "ecg_longest_valid_run": ecg.coverage["longest_valid_run"],
                             "heart_rate_bpm": ecg.heart_rate_bpm, "rmssd_ms": ecg.rmssd_ms})
        if rate == cfg["rate"]["primary_hz"]:
            primary = (eeg, ecg)
    assert primary is not None
    eeg, ecg = primary
    onset_seconds = cfg["rate"]["onset_exclusion_sensitivity_s"]
    onset_samples = round(onset_seconds * cfg["rate"]["primary_hz"])
    sensitivity = {"first_5_s_excluded": asdict(process_eeg(
        recording.right_forehead, recording.left_forehead, recording.counter,
        cfg["rate"]["primary_hz"], drop_initial_s=onset_seconds,
        amplitude_reference_raw_std=amplitude_reference_raw_std))}
    sensitivity["ecg_first_5_s_excluded"] = {
        "source_offset_samples": onset_samples,
        "source_offset_s_conditional": onset_seconds,
        "ecg": asdict(process_ecg(recording.wrist_ecg[onset_samples:],
                                cfg["rate"]["primary_hz"],
                                recording.counter[onset_samples:])),
    }
    for multiplier in cfg["eeg"]["threshold_sensitivity_multipliers"]:
        sensitivity[f"eeg_relative_threshold_x{multiplier}"] = asdict(process_eeg(
            recording.right_forehead, recording.left_forehead, recording.counter,
            cfg["rate"]["primary_hz"], threshold_multiplier=multiplier,
            amplitude_reference_raw_std=amplitude_reference_raw_std))
    for multiplier in cfg["qc"]["clipping_sensitivity_multipliers"]:
        sensitivity[f"eeg_clipping_threshold_x{multiplier}"] = asdict(process_eeg(
            recording.right_forehead, recording.left_forehead, recording.counter,
            cfg["rate"]["primary_hz"], clipping_multiplier=multiplier,
            amplitude_reference_raw_std=amplitude_reference_raw_std))
    for multiplier in cfg["eeg"]["review_ratio_sensitivity_multipliers"]:
        sensitivity[f"eeg_line_ratio_x{multiplier}"] = asdict(process_eeg(
            recording.right_forehead, recording.left_forehead, recording.counter,
            cfg["rate"]["primary_hz"], amplitude_reference_raw_std=amplitude_reference_raw_std,
            line_noise_ratio_threshold=cfg["eeg"]["raw_line_power_ratio_max"] * multiplier))
        sensitivity[f"eeg_muscle_ratio_x{multiplier}"] = asdict(process_eeg(
            recording.right_forehead, recording.left_forehead, recording.counter,
            cfg["rate"]["primary_hz"], amplitude_reference_raw_std=amplitude_reference_raw_std,
            muscle_ratio_threshold=cfg["eeg"]["filtered_muscle_power_ratio_max"] * multiplier))
    sensitivity["eeg_channel_imbalance_wide"] = asdict(process_eeg(
        recording.right_forehead, recording.left_forehead, recording.counter,
        cfg["rate"]["primary_hz"], amplitude_reference_raw_std=amplitude_reference_raw_std,
        channel_imbalance_bounds=tuple(cfg["eeg"]["channel_std_ratio_sensitivity_range"])))
    return {"id": f"E{trial.experiment}:{trial.subject_id}:{trial.room_id}",
            "experiment": trial.experiment, "participant_id": trial.subject_id,
            "room_id": trial.room_id,
            "source_file": str(recording_path(trial).relative_to(ROOT)),
            "logged_duration_s": trial.logged_duration_s,
            "sample_count": recording.samples, "rate_status": cfg["rate"]["primary_status"],
            "primary_rate_hz": cfg["rate"]["primary_hz"],
            "eeg": asdict(eeg), "ecg": asdict(ecg), "rate_scenarios": rate_results,
            "sensitivity": sensitivity,
            "ecg_examples": ecg_review_examples(recording.wrist_ecg, ecg),
            "eeg_trace": eeg_window(recording.right_forehead, eeg,
                                    cfg["rate"]["primary_hz"]).model_dump(mode="json"),
            "ecg_trace": (ecg_window(recording.wrist_ecg, ecg,
                                     cfg["rate"]["primary_hz"]).model_dump(mode="json")
                          if np.isfinite(recording.wrist_ecg).all() else None)}


def write_signals(destination: Path = RESULTS / "signals_detail.json") -> dict:
    require_science_checkpoint(stage="qc")
    trials = load_trials()
    first_pass: dict[int, list] = {1: [], 2: [], 3: []}
    primary_rate = decisions()["rate"]["primary_hz"]
    for trial in trials:
        recording = read_recording(recording_path(trial))
        first_pass[trial.experiment].append(process_eeg(
            recording.right_forehead, recording.left_forehead,
            recording.counter, primary_rate))
    amplitude_references = {experiment: experiment_amplitude_references(results)
                            for experiment, results in first_pass.items()}
    records = [process_trial(trial, read_recording(recording_path(trial)),
                             amplitude_references[trial.experiment]) for trial in trials]
    result = {"schema_version": "1.1.0", "method_version": decisions()["version"],
              "approved_spec_sha256": decisions().get("approved_spec_sha256"),
              "amplitude_reference_by_experiment": amplitude_references,
              "rate_status": decisions()["rate"]["primary_status"], "trials": records}
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    return result
