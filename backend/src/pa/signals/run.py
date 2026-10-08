"""Conditional-rate trial processing with inspectable modality and sensitivity evidence."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from pa.config import RESULTS, ROOT
from pa.io.checkpoint import require_science_checkpoint
from pa.io.metadata import Trial, load_trials
from pa.io.recordings import Recording, read_recording, recording_path
from pa.results.traces import ecg_window, eeg_window
from pa.signals.common import decisions
from pa.signals.ecg import process_ecg
from pa.signals.eeg import process_eeg


def process_trial(trial: Trial, recording: Recording) -> dict:
    """Compute all frozen scenarios from one original recording without default values."""
    cfg = decisions()
    rates = [cfg["rate"]["primary_hz"], *cfg["rate"]["sensitivity_hz"]]
    rate_results = []
    primary = None
    for rate in rates:
        eeg = process_eeg(recording.right_forehead, recording.left_forehead,
                          recording.counter, rate)
        ecg = process_ecg(recording.wrist_ecg, rate, recording.counter)
        rate_results.append({"rate_hz": rate, "sample_duration_s": recording.samples / rate,
                             "eeg_valid": eeg.valid, "eeg_reasons": list(eeg.reasons),
                             "faa": eeg.forehead_log_alpha_asymmetry,
                             "beta_alpha": eeg.log_beta_alpha_ratio,
                             "ecg_valid_hr": ecg.valid_hr, "ecg_valid_rmssd": ecg.valid_rmssd,
                             "ecg_reasons": list(ecg.reasons),
                             "heart_rate_bpm": ecg.heart_rate_bpm, "rmssd_ms": ecg.rmssd_ms})
        if rate == cfg["rate"]["primary_hz"]:
            primary = (eeg, ecg)
    assert primary is not None
    eeg, ecg = primary
    sensitivity = {"first_5_s_excluded": asdict(process_eeg(
        recording.right_forehead, recording.left_forehead, recording.counter,
        cfg["rate"]["primary_hz"], drop_initial_s=cfg["rate"]["onset_exclusion_sensitivity_s"]))}
    for multiplier in cfg["eeg"]["threshold_sensitivity_multipliers"]:
        sensitivity[f"eeg_relative_threshold_x{multiplier}"] = asdict(process_eeg(
            recording.right_forehead, recording.left_forehead, recording.counter,
            cfg["rate"]["primary_hz"], threshold_multiplier=multiplier))
    for multiplier in cfg["qc"]["clipping_sensitivity_multipliers"]:
        sensitivity[f"eeg_clipping_threshold_x{multiplier}"] = asdict(process_eeg(
            recording.right_forehead, recording.left_forehead, recording.counter,
            cfg["rate"]["primary_hz"], clipping_multiplier=multiplier))
    return {"id": f"E{trial.experiment}:{trial.subject_id}:{trial.room_id}",
            "experiment": trial.experiment, "participant_id": trial.subject_id,
            "room_id": trial.room_id,
            "source_file": str(recording_path(trial).relative_to(ROOT)),
            "logged_duration_s": trial.logged_duration_s,
            "sample_count": recording.samples, "rate_status": cfg["rate"]["primary_status"],
            "primary_rate_hz": cfg["rate"]["primary_hz"],
            "eeg": asdict(eeg), "ecg": asdict(ecg), "rate_scenarios": rate_results,
            "sensitivity": sensitivity,
            "eeg_trace": eeg_window(recording.right_forehead, eeg,
                                    cfg["rate"]["primary_hz"]).model_dump(mode="json"),
            "ecg_trace": ecg_window(recording.wrist_ecg, ecg,
                                    cfg["rate"]["primary_hz"]).model_dump(mode="json")}


def write_signals(destination: Path = RESULTS / "signals_detail.json") -> dict:
    require_science_checkpoint()
    records = [process_trial(trial, read_recording(recording_path(trial)))
               for trial in load_trials()]
    result = {"schema_version": "1.0.0", "method_version": decisions()["version"],
              "rate_status": decisions()["rate"]["primary_status"], "trials": records}
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    return result
