"""Construct descriptive affect from gated signal evidence and original ratings."""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import asdict
from pathlib import Path

from pa.affect.fusion import construct_affect
from pa.affect.normalization import descriptive_components
from pa.affect.ratings import subjective_axes
from pa.config import RESULTS
from pa.io.checkpoint import require_science_checkpoint
from pa.io.metadata import Trial, load_trials
from pa.signals.common import decisions


def construct_affect_detail(trials: list[Trial], signal_rows: list[dict]) -> dict:
    signals = {(row["experiment"], row["participant_id"], row["room_id"]): row
               for row in signal_rows}
    if len(signals) != len(signal_rows) or len(signals) != len(trials):
        raise ValueError("signal and anchored-trial counts do not match")
    rows = []
    for trial in trials:
        key = trial.experiment, trial.subject_id, trial.room_id
        evidence = signals.get(key)
        if evidence is None:
            raise ValueError(f"missing signal evidence for {key}")
        eeg, ecg = evidence["eeg"], evidence["ecg"]
        rows.append({"id": evidence["id"], "experiment": trial.experiment,
                     "participant_id": trial.subject_id, "room_id": trial.room_id,
                     "comfort": trial.comfort, "subjective": subjective_axes(trial),
                     "faa": eeg["forehead_log_alpha_asymmetry"] if eeg["valid"] else None,
                     "beta_alpha": eeg["log_beta_alpha_ratio"] if eeg["valid"] else None,
                     "heart_rate_bpm": ecg["heart_rate_bpm"] if ecg["valid_hr"] else None,
                     "rmssd_ms": ecg["rmssd_ms"] if ecg["valid_rmssd"] else None})
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
            "trials": output, "descriptive_calibrations": calibrations,
            "cohorts": [{"experiment": experiment, "cohort": cohort, "trials": count}
                        for (experiment, cohort), count in sorted(cohorts.items())],
            "objective_subjective_disagreement": disagreements}


def write_affect(signal_path: Path = RESULTS / "signals_detail.json",
                 destination: Path = RESULTS / "affect_detail.json") -> dict:
    require_science_checkpoint()
    signal_rows = json.loads(signal_path.read_text())["trials"]
    result = construct_affect_detail(load_trials(), signal_rows)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    return result
