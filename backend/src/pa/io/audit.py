"""File-level acquisition audit with rate scenarios rather than asserted timing."""

from __future__ import annotations

import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path
from statistics import median

import numpy as np
from numpy.typing import NDArray

from pa.config import RESULTS, ROOT, SCHEMA_VERSION
from pa.io.checkpoint import require_science_checkpoint
from pa.io.metadata import Trial, load_rooms, load_trials
from pa.io.recordings import read_recording, recording_path
from pa.signals.common import decisions

TIMESTAMP = re.compile(r"-(\d{8})-(\d{6})\.csv$")


def counter_discontinuities(counter: NDArray[np.int64]) -> list[int]:
    """Positions whose modulo-256 step differs from one; wrap itself is normal."""
    return (np.flatnonzero(np.mod(np.diff(counter), 256) != 1) + 1).tolist()


def duration_assessment(samples: int, logged_seconds: float, rate_hz: int,
                        discrepancy_fraction: float | None = None) -> dict:
    if discrepancy_fraction is None:
        discrepancy_fraction = decisions()["rate"]["duration_disagreement_fraction"]
    observed_seconds = samples / rate_hz
    discrepancy = observed_seconds - logged_seconds
    return {
        "rate_hz": rate_hz, "sample_duration_s": round(observed_seconds, 4),
        "difference_from_logged_s": round(discrepancy, 4),
        "relative_difference": round(abs(discrepancy) / logged_seconds, 4),
        "duration_disagreement": abs(discrepancy) / logged_seconds > discrepancy_fraction,
    }


def _filename_time(trial: Trial) -> str | None:
    match = TIMESTAMP.search(trial.eeg_filename)
    if not match:
        return None
    date, clock = match.groups()
    return f"{date[:4]}-{date[4:6]}-{date[6:]}T{clock[:2]}:{clock[2:4]}:{clock[4:]}"


def audit_trials(trials: list[Trial] | None = None) -> dict:
    settings = decisions()
    primary_rate = settings["rate"]["primary_hz"]
    candidate_rates = [primary_rate, *settings["rate"]["sensitivity_hz"]]
    trials = trials if trials is not None else load_trials()
    files: list[dict] = []
    order_groups: dict[tuple[int, str], list[dict]] = defaultdict(list)
    for trial in trials:
        path = recording_path(trial)
        recording = read_recording(path)
        discontinuities = counter_discontinuities(recording.counter)
        filename_time = _filename_time(trial)
        ratios = recording.samples / trial.logged_duration_s
        row = {
            "experiment": trial.experiment, "subject_id": trial.subject_id,
            "room_id": trial.room_id, "source_file": path.relative_to(ROOT).as_posix(),
            "filename_time": filename_time, "timestamp_kind": "filename chronology, not event timestamp",
            "logged_duration_s": trial.logged_duration_s, "samples": recording.samples,
            "samples_per_logged_second": round(ratios, 5),
            "primary_onset_exclusion_s": settings["rate"]["onset_exclusion_primary_s"],
            "onset_sensitivity_exclusion_s": settings["rate"]["onset_exclusion_sensitivity_s"],
            "numeric_finite": True, "counter_discontinuity_count": len(discontinuities),
            "counter_discontinuity_indices": discontinuities,
            "counter_interpretation": "integrity flag only; no packet-loss count or timestamps inferred",
            "rate_scenarios": [duration_assessment(recording.samples, trial.logged_duration_s, rate)
                               for rate in candidate_rates],
        }
        files.append(row)
        order_groups[(trial.experiment, trial.subject_id)].append({
            "room_id": trial.room_id, "source_file": row["source_file"], "filename_time": filename_time,
        })
    trials_by_experiment = {str(exp): sum(t.experiment == exp for t in trials) for exp in (1, 2, 3)}
    sample_ratios = {str(exp): round(median(f["samples_per_logged_second"] for f in files
                                            if f["experiment"] == exp), 4) for exp in (1, 2, 3)}
    order = [{"experiment": exp, "subject_id": subject,
              "sequence": sorted(group, key=lambda item: item["filename_time"] or "")}
             for (exp, subject), group in sorted(order_groups.items())]
    return {
        "schema_version": SCHEMA_VERSION,
        "provenance": {
            "source": "original CSV recordings and metadata; no legacy processed artifact",
            "manifest_sha256": hashlib.sha256((ROOT / "data/MANIFEST.sha256").read_bytes()).hexdigest(),
            "rate_status": f"unconfirmed; {primary_rate} Hz conditional analytical scenario",
            "analysis_settings_version": settings["version"],
            "approved_spec_sha256": settings.get("approved_spec_sha256"),
            "rate_evidence": [
                "median sample/logged-duration ratios near 500 Hz; logged durations are not hardware timestamps",
                "manufacturer Chords-Web docs do not identify this recording's firmware or selected rate",
                "manufacturer 3-channel firmware documentation has a 250 Hz variant; Cardio app describes 500 Hz",
                "no acquisition settings, timestamp column or firmware version were supplied",
            ],
        },
        "summary": {
            "recordings": len(files), "participants": len({t.subject_id for t in trials}),
            "rooms": len({t.room_id for t in trials}), "room_metadata_rows": len(load_rooms()),
            "trials_by_experiment": trials_by_experiment,
            "median_samples_per_logged_second_by_experiment": sample_ratios,
            "counter_flagged_files_by_experiment": {str(exp): sum(f["experiment"] == exp and
                f["counter_discontinuity_count"] > 0 for f in files) for exp in (1, 2, 3)},
            "duration_disagreement_at_primary_rate": sum(
                next(scenario["duration_disagreement"] for scenario in file["rate_scenarios"]
                     if scenario["rate_hz"] == primary_rate) for file in files),
        },
        "trial_order": order,
        "files": files,
    }


def write_audit(destination: Path = RESULTS / "audit.json") -> dict:
    result = audit_trials()
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    return result


def write_timebase(audit: dict, destination: Path = RESULTS / "timebase.json") -> dict:
    """Export inspectable rate evidence without asserting a hardware clock."""
    require_science_checkpoint(stage="qc")
    settings = decisions()
    rows = []
    for row in audit["files"]:
        primary = next(item for item in row["rate_scenarios"]
                       if item["rate_hz"] == settings["rate"]["primary_hz"])
        rows.append({
            "trial_id": f"E{row['experiment']}:{row['subject_id']}:{row['room_id']}",
            "experiment": row["experiment"], "source_file": row["source_file"],
            "samples": row["samples"], "logged_duration_s": row["logged_duration_s"],
            "samples_per_logged_second": row["samples_per_logged_second"],
            "counter_discontinuity_count": row["counter_discontinuity_count"],
            "counter_discontinuity_indices": row["counter_discontinuity_indices"],
            "duration_mismatch_over_10pct": primary["duration_disagreement"],
            "rate_scenarios": row["rate_scenarios"],
            "onset": {
                "primary_excluded_s": settings["rate"]["onset_exclusion_primary_s"],
                "sensitivity_excluded_s": settings["rate"]["onset_exclusion_sensitivity_s"],
                "event_marker_available": False,
            },
        })
    result = {
        "schema_version": SCHEMA_VERSION,
        "method_version": settings["version"],
        "approved_spec_sha256": settings.get("approved_spec_sha256"),
        "rate_status": settings["rate"]["primary_status"],
        "rate_evidence": audit["provenance"]["rate_evidence"],
        "summary": {"recordings": len(rows), "duration_mismatch_over_10pct": sum(
            row["duration_mismatch_over_10pct"] for row in rows),
            "counter_flagged": sum(row["counter_discontinuity_count"] > 0 for row in rows)},
        "trials": rows,
    }
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    return result
