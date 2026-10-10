"""Reproducible representative trace/spectrum panels for human QC inspection."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy import signal

from pa.config import ROOT
from pa.io.checkpoint import require_science_checkpoint
from pa.io.metadata import load_trials
from pa.io.recordings import read_recording, recording_path
from pa.signals.common import decisions

SIGNALS = ROOT / "artifacts/results/signals_detail.json"
PANELS = ROOT / "docs/reports/signal-review"
QC_REVIEW = ROOT / "artifacts/review"
QC_QUEUE = ROOT / "artifacts/results/qc_review.json"
CP_B = ROOT / "docs/reports/revision-2026-10/CP-B.md"


def _selections(rows: list[dict]) -> list[tuple[str, dict]]:
    selected = []
    for experiment in (1, 2, 3):
        subset = [row for row in rows if row["experiment"] == experiment]
        examples = {
            "ecg_accepted": next((row for row in subset if row["ecg"]["valid_rmssd"]),
                                 next((row for row in subset if row["ecg"]["valid_hr"]), None)),
            "ecg_rejected": next((row for row in subset if "no_qrs_quality" in row["ecg"]["reasons"]),
                                 None),
            "eeg_flagged": next((row for row in subset if row["eeg"]["rejected_epochs"]), None),
        }
        selected.extend((label, row) for label, row in examples.items() if row is not None)
    worst = max(rows, key=lambda row: abs(row["sample_count"] /
                                        row["primary_rate_hz"] / row["logged_duration_s"] - 1))
    selected.append(("worst_duration_mismatch", worst))
    selected.extend(("rare_possible_clipping", row) for row in rows
                    if any("repeated_extrema_possible_clipping" in epoch["reasons"]
                           for epoch in row["eeg"]["rejected_epochs"]))
    return selected


def _eeg_window(raw, evidence: dict, rate: int, flagged: bool):
    width = round(decisions()["eeg"]["epoch_s"] * rate)
    rejected = {item["index"]: item["reasons"] for item in evidence["rejected_epochs"]}
    index = (min(rejected) if flagged and rejected else
             next((index for index in range(evidence["total_epochs"]) if index not in rejected), 0))
    start, stop = index * width, (index + 1) * width
    right, left = raw.right_forehead[start:stop], raw.left_forehead[start:stop]
    cleaned = None
    if index not in rejected and len(right) == width:
        cfg = decisions()["eeg"]
        sos = signal.butter(cfg["filter_order"], cfg["filter_hz"], btype="bandpass",
                            fs=rate, output="sos")
        cleaned = signal.sosfiltfilt(sos, right)
    return right, left, cleaned, start / rate, rejected.get(index, [])


def _ecg_window(raw, evidence: dict, rate: int):
    spans = evidence["quality"].get("segments", [])
    polarity = evidence["polarity"]
    chosen = next((span for span in spans if polarity in ("positive", "negative") and
                   span["candidates"][polarity]["admitted"]),
                  spans[0] if spans else None)
    start = chosen["start_sample"] if chosen else 0
    stop = min(start + round(4 * rate), chosen["stop_sample"] if chosen else len(raw.wrist_ecg))
    samples = raw.wrist_ecg[start:stop]
    cleaned = None
    peaks = []
    if chosen and stop > start:
        cfg = decisions()["ecg"]
        sos = signal.butter(cfg["filter_order"], cfg["qrs_filter_hz"], btype="bandpass",
                            fs=rate, output="sos")
        filtered = signal.sosfiltfilt(sos, raw.wrist_ecg[start:chosen["stop_sample"]])
        cleaned = filtered[:len(samples)]
        if polarity in ("positive", "negative"):
            peaks = [peak - start for peak in chosen["candidates"][polarity]["peak_indices"]
                     if start <= peak < stop]
    return samples, cleaned, peaks, start / rate


def _panel(label: str, row: dict, trial, destination: Path) -> dict:
    rate = row["primary_rate_hz"]
    raw = read_recording(recording_path(trial))
    eeg_right, eeg_left, eeg_clean, eeg_start, eeg_flags = _eeg_window(
        raw, row["eeg"], rate, label == "eeg_flagged")
    ecg_raw, ecg_clean, peaks, ecg_start = _ecg_window(raw, row["ecg"], rate)
    fig, axes = plt.subplots(2, 2, figsize=(13, 7), layout="constrained")
    fig.suptitle(f"{row['id']} — {label}; conditional {rate} Hz, raw units unverified")
    eeg_time = eeg_start + np.arange(len(eeg_right)) / rate
    axes[0, 0].plot(eeg_time, eeg_right, linewidth=0.65, label="Ch1 approximate right")
    axes[0, 0].plot(eeg_time, eeg_left, linewidth=0.65, alpha=0.65,
                    label="Ch2 approximate left")
    axes[0, 0].set(title=f"Raw EEG; QC: {', '.join(eeg_flags) or 'accepted epoch'}",
                   xlabel="Conditional seconds", ylabel="Unverified raw amplitude")
    axes[0, 0].legend(fontsize="small")
    if len(eeg_right) >= 500:
        frequency, psd = signal.welch(eeg_right, rate, nperseg=min(rate * 2, len(eeg_right)))
        axes[0, 1].semilogy(frequency, psd, label="raw right")
    if eeg_clean is not None:
        frequency, psd = signal.welch(eeg_clean, rate, nperseg=min(rate * 2, len(eeg_clean)))
        axes[0, 1].semilogy(frequency, psd, label="filtered right")
    axes[0, 1].set(xlim=(0, 65), title="EEG spectrum; residual 50 Hz must be inspected",
                   xlabel="Hz", ylabel="Power / Hz in squared raw units")
    axes[0, 1].legend(fontsize="small")
    ecg_time = ecg_start + np.arange(len(ecg_raw)) / rate
    axes[1, 0].plot(ecg_time, ecg_raw, linewidth=0.8)
    axes[1, 0].set(title="Raw Ch3 owner-reported wrist ECG", xlabel="Conditional seconds",
                   ylabel="Unverified raw amplitude")
    if ecg_clean is not None:
        axes[1, 1].plot(ecg_time, ecg_clean, linewidth=0.8, label="5–25 Hz filtered")
        if peaks:
            indices = np.asarray(peaks, dtype=int)
            axes[1, 1].scatter(ecg_time[indices], ecg_clean[indices], s=15, c="red",
                               label="admitted candidate peaks")
        axes[1, 1].legend(fontsize="small")
    else:
        axes[1, 1].text(0.5, 0.5, "No continuous segment to filter", ha="center", va="center",
                        transform=axes[1, 1].transAxes)
    record_flags = ', '.join(row["ecg"]["reasons"]) or "none"
    window_status = ("admitted candidate window" if peaks else "no admitted peaks in window")
    axes[1, 1].set(title=f"ECG window: {window_status}\nWhole-record flags: {record_flags}",
                   xlabel="Conditional seconds", ylabel="Unverified raw amplitude")
    fig.savefig(destination, dpi=135)
    plt.close(fig)
    return {"label": label, "trial_id": row["id"], "file": destination.name,
            "eeg_window_start_s": eeg_start, "eeg_window_flags": eeg_flags,
            "ecg_window_start_s": ecg_start, "ecg_reasons": row["ecg"]["reasons"]}


def write_review_panels(signals_path: Path = SIGNALS, destination: Path = PANELS) -> list[dict]:
    require_science_checkpoint(stage="qc")
    rows = json.loads(signals_path.read_text())["trials"]
    trials = {f"E{trial.experiment}:{trial.subject_id}:{trial.room_id}": trial
              for trial in load_trials()}
    destination.mkdir(parents=True, exist_ok=True)
    index = []
    for label, row in _selections(rows):
        slug = row["id"].replace(":", "-")
        index.append(_panel(label, row, trials[row["id"]], destination / f"{slug}-{label}.png"))
    (destination / "index.json").write_text(json.dumps(index, indent=2) + "\n")
    return index


def _review_entries(row: dict, timebase: dict | None) -> list[dict]:
    """Create one independently decidable entry for each flagged signal."""
    eeg = row["eeg"]
    entries = []
    trial_flags = list(eeg.get("trial_qc", {}).get("review_flags", []))
    if eeg.get("rejected_epochs"):
        trial_flags.append("eeg_rejected_epochs")
    for name in ("right", "left"):
        channel = eeg.get("channel_qc", {}).get(name, {})
        rejected = channel.get("rejected_epochs", [])
        epoch_reasons = {reason for item in rejected for reason in item["reasons"]}
        flags = sorted(set(channel.get("review_flags", []) +
                           (["channel_ineligible"] if not channel.get("eligible", False) else []) +
                           (["epoch_rejections"] if rejected else [])) | epoch_reasons)
        if flags:
            entries.append({"signal": f"eeg_{name}", "flags": flags,
                            "automated_eligible": bool(channel.get("eligible")),
                            "evidence": {"accepted_epochs": channel.get("accepted_epochs"),
                                         "total_epochs": channel.get("total_epochs"),
                                         "raw_epoch_std_median": channel.get("raw_epoch_std_median"),
                                         "amplitude_reference_raw_std": channel.get(
                                             "amplitude_reference_raw_std"),
                                         "line_noise_ratio": channel.get("line_noise_ratio"),
                                         "muscle_ratio": channel.get("muscle_ratio"),
                                         "rejected_epochs": rejected}})
    if trial_flags:
        entries.append({"signal": "eeg_trial", "flags": sorted(set(trial_flags)),
                        "automated_eligible": bool(eeg["valid"]),
                        "evidence": {"channel_imbalance_ratio": eeg.get("trial_qc", {}).get(
                            "channel_imbalance_ratio"), "rejected_epochs": len(eeg["rejected_epochs"])}})
    ecg = row["ecg"]
    ecg_flags = sorted(set(ecg["reasons"] +
                           ([] if ecg["valid_hr"] and ecg["valid_rmssd"] else
                            ["cardiac_coverage_or_quality_incomplete"])))
    if ecg_flags:
        entries.append({"signal": "ecg", "flags": ecg_flags,
                        "automated_eligible": bool(ecg["valid_hr"]),
                        "evidence": {"heart_rate_bpm": ecg["heart_rate_bpm"],
                                     "rmssd_ms": ecg["rmssd_ms"],
                                     "coverage": ecg.get("coverage", {}),
                                     "eligibility": ecg.get("eligibility", {})}})
    if timebase:
        time_flags = []
        if timebase["duration_mismatch_over_10pct"]:
            time_flags.append("duration_mismatch_over_10pct")
        if timebase["counter_discontinuity_count"]:
            time_flags.append("counter_discontinuity")
        if time_flags:
            entries.append({"signal": "timebase", "flags": time_flags,
                            "automated_eligible": None,
                            "evidence": {"samples_per_logged_second": timebase[
                                "samples_per_logged_second"],
                                "counter_discontinuity_count": timebase[
                                    "counter_discontinuity_count"]}})
    for entry in entries:
        entry["id"] = f"{row['id']}:{entry['signal']}"
        entry["trial_id"] = row["id"]
        entry["experiment"] = row["experiment"]
        entry["participant_id"] = row["participant_id"]
        entry["room_id"] = row["room_id"]
        entry["decision"] = {"status": "pending", "reason": None,
                             "reviewer": None, "reviewed_at": None}
    return entries


def _spectrum(axis, raw: np.ndarray, rate: int, *, clean: bool) -> None:
    if len(raw) < 2 * rate:
        axis.text(0.5, 0.5, "No full 2 s spectral window", ha="center", va="center",
                  transform=axis.transAxes)
        return
    frequency, psd = signal.welch(raw - np.mean(raw), fs=rate, nperseg=2 * rate,
                                  noverlap=rate, window="hann")
    axis.semilogy(frequency, np.maximum(psd, np.finfo(float).tiny),
                  label="raw", linewidth=0.8)
    if clean:
        cfg = decisions()["eeg"]
        sos = signal.butter(cfg["filter_order"], cfg["filter_hz"],
                            btype="bandpass", fs=rate, output="sos")
        filtered = signal.sosfiltfilt(sos, raw)
        frequency, psd = signal.welch(filtered, fs=rate, nperseg=2 * rate,
                                      noverlap=rate, window="hann")
        axis.semilogy(frequency, np.maximum(psd, np.finfo(float).tiny),
                      label="accepted filtered", linewidth=0.8)
    axis.set_xlim(0, 65)
    axis.legend(fontsize="x-small")


def _qc_panel(row: dict, trial, path: Path) -> None:
    raw = read_recording(recording_path(trial))
    rate = row["primary_rate_hz"]
    width = round(decisions()["eeg"]["epoch_s"] * rate)
    fig, axes = plt.subplots(3, 2, figsize=(14, 10), layout="constrained")
    fig.suptitle(f"{row['id']} — conditional {rate} Hz; amplitude units unknown; CP-B pending")
    for index, (name, samples) in enumerate((
        ("Ch1 approximate right", raw.right_forehead),
        ("Ch2 approximate left", raw.left_forehead),
    )):
        channel = row["eeg"].get("channel_qc", {}).get("right" if index == 0 else "left", {})
        rejected = {item["index"] for item in channel.get("rejected_epochs", [])}
        stride = max(1, len(samples) // 8000)
        t = np.arange(0, len(samples), stride) / rate
        axes[index, 0].plot(t, samples[::stride], linewidth=0.55)
        for epoch in rejected:
            axes[index, 0].axvspan(epoch * width / rate, (epoch + 1) * width / rate,
                                   alpha=0.12, color="red")
        axes[index, 0].set(title=f"{name} raw; shaded rejected epochs",
                           xlabel="Conditional seconds", ylabel="Unverified raw amplitude")
        accepted = next((i for i in range(row["eeg"]["total_epochs"]) if i not in rejected), None)
        if accepted is not None:
            epoch_samples = samples[accepted * width:(accepted + 1) * width]
            _spectrum(axes[index, 1], epoch_samples, rate, clean=True)
        else:
            axes[index, 1].text(0.5, 0.5, "No accepted epoch", ha="center", va="center",
                                transform=axes[index, 1].transAxes)
        axes[index, 1].set(title=f"{name} raw/accepted spectrum", xlabel="Hz",
                           ylabel="Power/Hz in squared raw units")
    examples = row.get("ecg_examples", [])
    example = next((item for item in examples if item.get("filtered") is not None),
                   examples[0] if examples else None)
    if example:
        values = np.array([v if v is not None else np.nan for v in example["raw"]])
        t = example["start_s"] + np.arange(len(values)) / rate
        axes[2, 0].plot(t, values, linewidth=0.7)
        if example.get("filtered") is not None:
            axes[2, 1].plot(t, example["filtered"], linewidth=0.7)
        else:
            axes[2, 1].text(0.5, 0.5, "No accepted filtered ECG window",
                            ha="center", va="center", transform=axes[2, 1].transAxes)
        label = example["kind"]
    else:
        axes[2, 0].text(0.5, 0.5, "No ECG review window", ha="center", va="center",
                        transform=axes[2, 0].transAxes)
        label = "unavailable"
    axes[2, 0].set(title=f"Wrist ECG raw: {label}", xlabel="Conditional seconds",
                   ylabel="Unverified raw amplitude")
    axes[2, 1].set(title="Wrist ECG 5–25 Hz accepted segment", xlabel="Conditional seconds",
                   ylabel="Unverified raw amplitude")
    fig.savefig(path, dpi=110)
    plt.close(fig)


def _eeg_detail(row: dict, raw, name: str, path: Path) -> None:
    """Full sample-resolution accepted and flagged windows for one EEG channel."""
    rate = row["primary_rate_hz"]
    width = round(decisions()["eeg"]["epoch_s"] * rate)
    samples = raw.right_forehead if name == "right" else raw.left_forehead
    channel = row["eeg"]["channel_qc"][name]
    rejected = {item["index"]: item for item in channel["rejected_epochs"]}
    selected: list[tuple[int, str, bool]] = []
    accepted = next((index for index in range(row["eeg"]["total_epochs"])
                     if index not in rejected), None)
    if accepted is not None:
        selected.append((accepted, "accepted", True))
    seen_reasons: set[str] = set()
    for index, item in sorted(rejected.items()):
        unseen = set(item["reasons"]) - seen_reasons
        if unseen:
            selected.append((index, ", ".join(item["reasons"]), False))
            seen_reasons.update(item["reasons"])
    if not selected:
        selected.append((0, "short / no full epoch", False))
    fig, axes = plt.subplots(len(selected), 2, figsize=(13, 3.3 * len(selected)),
                             squeeze=False, layout="constrained")
    for axes_row, (index, label, clean) in zip(axes, selected, strict=True):
        start, stop = index * width, min((index + 1) * width, len(samples))
        values = samples[start:stop]
        if len(values):
            t = np.arange(start, stop) / rate
            axes_row[0].plot(t, values, linewidth=0.7)
        axes_row[0].set(title=f"Epoch {index}, samples {start}:{stop}: {label}",
                        xlabel="Conditional seconds", ylabel="Unverified raw amplitude")
        # A counter gap invalidates a continuous PSD and is shown as a raw trace only.
        if "counter_discontinuity" not in label and len(values) >= 2 * rate:
            _spectrum(axes_row[1], values, rate, clean=clean)
        else:
            axes_row[1].text(0.5, 0.5, "Spectrum unavailable: gap or short window",
                             ha="center", va="center", transform=axes_row[1].transAxes)
        axes_row[1].set(title="Raw and QC-accepted filtered spectrum", xlabel="Hz",
                        ylabel="Power/Hz in squared raw units")
    fig.suptitle(f"{row['id']} {name} EEG — conditional {rate} Hz; CP-B pending")
    fig.savefig(path, dpi=130)
    plt.close(fig)


def _ecg_detail(row: dict, path: Path) -> None:
    """Show every accepted and flagged ECG example with traces and spectra."""
    examples = row.get("ecg_examples", [])
    if not examples:
        examples = [{"kind": "unavailable", "reason": "no_example", "start_sample": 0,
                     "stop_sample": 0, "start_s": 0, "raw": [], "filtered": None,
                     "raw_spectrum": None, "filtered_spectrum": None}]
    rate = row["primary_rate_hz"]
    fig, axes = plt.subplots(len(examples), 2, figsize=(13, 3.5 * len(examples)),
                             squeeze=False, layout="constrained")
    for axes_row, example in zip(axes, examples, strict=True):
        values = np.array([value if value is not None else np.nan for value in example["raw"]])
        times = example["start_s"] + np.arange(len(values)) / rate
        axes_row[0].plot(times, values, linewidth=0.75, label="raw")
        if example["filtered"] is not None:
            axes_row[0].plot(times, example["filtered"], linewidth=0.75,
                             alpha=0.8, label="accepted filtered")
            polarity = row["ecg"].get("polarity")
            spans = row["ecg"].get("quality", {}).get("segments", [])
            peaks = [peak for span in spans for peak in
                     span.get("candidates", {}).get(polarity, {}).get("peak_indices", [])
                     if example["start_sample"] <= peak < example["stop_sample"]]
            if peaks:
                local = np.asarray(peaks, dtype=int) - example["start_sample"]
                filtered = np.asarray(example["filtered"])
                axes_row[0].scatter(times[local], filtered[local], s=13, c="red",
                                     label="candidate peaks")
        axes_row[0].set(title=f"{example['kind']} ({example.get('reason') or 'none'}), "
                         f"samples {example['start_sample']}:{example['stop_sample']}",
                        xlabel="Conditional seconds", ylabel="Unverified raw amplitude")
        axes_row[0].legend(fontsize="x-small")
        for key, label in (("raw_spectrum", "raw"),
                           ("filtered_spectrum", "accepted filtered")):
            spectrum = example.get(key)
            if spectrum:
                axes_row[1].semilogy(spectrum["frequency_hz"],
                                     np.maximum(spectrum["power_per_hz"],
                                                np.finfo(float).tiny), label=label,
                                     linewidth=0.75)
        if example.get("raw_spectrum"):
            axes_row[1].legend(fontsize="x-small")
        else:
            axes_row[1].text(0.5, 0.5, "Spectrum unavailable across gap / invalid samples",
                             ha="center", va="center", transform=axes_row[1].transAxes)
        axes_row[1].set(title="Wrist ECG raw / accepted 5–25 Hz spectrum", xlim=(0, 40),
                        xlabel="Hz", ylabel="Power/Hz in squared raw units")
    fig.suptitle(f"{row['id']} wrist ECG — conditional {rate} Hz; CP-B pending")
    fig.savefig(path, dpi=130)
    plt.close(fig)


def write_qc_review(signals_path: Path = SIGNALS, timebase_path: Path = ROOT / "artifacts/results/timebase.json",
                    queue_path: Path = QC_QUEUE, panel_dir: Path = QC_REVIEW,
                    report_path: Path = CP_B) -> dict:
    """Generate a pending per-signal review queue and linked visual evidence."""
    require_science_checkpoint(stage="qc")
    if queue_path.exists():
        existing = json.loads(queue_path.read_text())
        if existing.get("eligibility_integrated"):
            expected = {
                "signals_sha256": hashlib.sha256(signals_path.read_bytes()).hexdigest(),
                "timebase_sha256": hashlib.sha256(timebase_path.read_bytes()).hexdigest(),
                "approved_spec_sha256": decisions()["approved_spec_sha256"],
                "method_version": decisions()["version"],
            }
            if any(existing.get(key) != value for key, value in expected.items()):
                raise RuntimeError("reviewed CP-B source/method changed; new evidence review required")
            if queue_path == QC_QUEUE and report_path == CP_B:
                from pa.io.checkpoint import load_reviewed_qc
                load_reviewed_qc()
            return existing
    signals = json.loads(signals_path.read_text())
    timebase = json.loads(timebase_path.read_text())
    approved_hash = decisions()["approved_spec_sha256"]
    if signals.get("approved_spec_sha256") != approved_hash or \
            timebase.get("approved_spec_sha256") != approved_hash:
        raise RuntimeError("QC inputs do not match the approved v1.2 specification")
    times = {row["trial_id"]: row for row in timebase["trials"]}
    trials = {f"E{trial.experiment}:{trial.subject_id}:{trial.room_id}": trial
              for trial in load_trials()}
    rows = signals["trials"]
    if set(trials) != {row["id"] for row in rows} or set(times) != set(trials):
        raise RuntimeError("QC review inputs do not cover exactly the source trials")
    entries = [entry for row in rows for entry in _review_entries(row, times[row["id"]])]
    by_trial = {row["id"]: [] for row in rows}
    for entry in entries:
        by_trial[entry["trial_id"]].append(entry)
    examples = []
    for experiment in (1, 2, 3):
        subset = [row for row in rows if row["experiment"] == experiment]
        for label, predicate in (
            ("eeg_automated_accepted", lambda r: r["eeg"]["valid"]),
            ("eeg_automated_rejected", lambda r: not r["eeg"]["valid"]),
            ("ecg_hr_automated_accepted", lambda r: r["ecg"]["valid_hr"]),
            ("ecg_hr_automated_rejected", lambda r: not r["ecg"]["valid_hr"]),
        ):
            row = next((row for row in subset if predicate(row)), None)
            if row:
                examples.append({"experiment": experiment, "kind": label, "trial_id": row["id"]})
    worst = max(rows, key=lambda row: abs(row["sample_count"] /
                                        row["primary_rate_hz"] / row["logged_duration_s"] - 1))
    example_ids = {item["trial_id"] for item in examples} | {worst["id"]}
    panel_ids = sorted({trial_id for trial_id, items in by_trial.items() if items} | example_ids)
    panel_dir.mkdir(parents=True, exist_ok=True)
    panels: dict[str, dict[str, str]] = {}
    row_by_id = {row["id"]: row for row in rows}
    for trial_id in panel_ids:
        row = row_by_id[trial_id]
        slug = trial_id.replace(":", "-")
        signals_needed = {entry["signal"] for entry in by_trial[trial_id]}
        representative = trial_id in example_ids
        paths: dict[str, str] = {}
        overview = panel_dir / f"{slug}-overview.png"
        right = panel_dir / f"{slug}-eeg-right.png"
        left = panel_dir / f"{slug}-eeg-left.png"
        ecg = panel_dir / f"{slug}-ecg.png"
        if "timebase" in signals_needed or representative:
            _qc_panel(row, trials[trial_id], overview)
            paths["overview"] = overview.relative_to(ROOT).as_posix()
        if "eeg_right" in signals_needed or "eeg_trial" in signals_needed or representative:
            raw = read_recording(recording_path(trials[trial_id]))
            _eeg_detail(row, raw, "right", right)
            paths["eeg_right"] = right.relative_to(ROOT).as_posix()
        if "eeg_left" in signals_needed or "eeg_trial" in signals_needed or representative:
            raw = read_recording(recording_path(trials[trial_id]))
            _eeg_detail(row, raw, "left", left)
            paths["eeg_left"] = left.relative_to(ROOT).as_posix()
        if "ecg" in signals_needed or representative:
            _ecg_detail(row, ecg)
            paths["ecg"] = ecg.relative_to(ROOT).as_posix()
        panels[trial_id] = paths
    for entry in entries:
        linked = panels[entry["trial_id"]]
        if entry["signal"] == "eeg_trial":
            entry["panels"] = [linked["eeg_right"], linked["eeg_left"]]
        elif entry["signal"] in linked:
            entry["panels"] = [linked[entry["signal"]]]
        elif entry["signal"] == "timebase":
            entry["panels"] = [linked["overview"]]
        else:
            entry["panels"] = [linked["ecg"]]
        entry["panel"] = entry["panels"][0]
    clusters = Counter(flag for entry in entries for flag in entry["flags"])
    product = {"schema_version": "1.0.0", "method_version": decisions()["version"],
               "approved_spec_sha256": approved_hash, "owner_verdict": "pending",
               "eligibility_integrated": False,
               "generated_date_utc": datetime.now(UTC).date().isoformat(),
               "signals_sha256": hashlib.sha256(signals_path.read_bytes()).hexdigest(),
               "timebase_sha256": hashlib.sha256(timebase_path.read_bytes()).hexdigest(),
               "summary": {"trials": len(rows), "queue_entries": len(entries),
                           "flagged_trials": sum(bool(v) for v in by_trial.values()),
                           "panels": sum(len(item) for item in panels.values()),
                           "flag_clusters": dict(sorted(clusters.items()))},
               "examples": examples, "worst_duration_mismatch": {
                   "trial_id": worst["id"],
                   "samples_per_logged_second": times[worst["id"]][
                       "samples_per_logged_second"],
                   "relative_difference": abs(worst["sample_count"] /
                                              worst["primary_rate_hz"] /
                                              worst["logged_duration_s"] - 1)},
               "trials": [{"trial_id": row["id"], "experiment": row["experiment"],
                            "eeg_bilateral_automated_eligible": row["eeg"]["valid"],
                            "ecg_hr_automated_eligible": row["ecg"]["valid_hr"],
                            "ecg_rmssd_automated_eligible": row["ecg"]["valid_rmssd"],
                            "entry_ids": [entry["id"] for entry in by_trial[row["id"]]],
                            "panel": panels.get(row["id"], {}).get("overview") or
                                     next(iter(panels.get(row["id"], {}).values()), None),
                            "signal_panels": panels.get(row["id"], {})} for row in rows],
               "entries": entries}
    queue_path.parent.mkdir(parents=True, exist_ok=True)
    queue_path.write_text(json.dumps(product, indent=2, allow_nan=False) + "\n")
    _write_cp_b(product, report_path)
    return product


def _write_cp_b(product: dict, path: Path) -> None:
    """Human-readable index; queue JSON carries every pending decision field."""
    def links(entry: dict) -> str:
        return ", ".join(f"[trace/spectrum {index + 1}](../../../{panel})"
                         for index, panel in enumerate(entry["panels"]))

    lines = ["# CP-B — signal-quality owner review", "",
             "**Owner verdict:** PENDING", "",
             f"Generated {product['generated_date_utc']} UTC from approved v1.2 QC products; owner signature pending.", "",
             f"Approved v1.2 source SHA-256: `{product['approved_spec_sha256']}`. Signal-product SHA-256: `{product['signals_sha256']}`; timebase SHA-256: `{product['timebase_sha256']}`. Automated flags are review prompts; they do not prove cortical or cardiac validity. Channel imbalance is the median across paired, nonflat, gap-free epochs of ordinary raw Ch1/Ch2 standard-deviation ratios; it is not a within-epoch MAD estimator. No owner trial/channel disposition has been recorded. Dependent affect and model work remains held.", "",
             f"Reviewed source coverage: {product['summary']['trials']} trials; {product['summary']['queue_entries']} pending per-signal entries across {product['summary']['flagged_trials']} flagged trials; {product['summary']['panels']} linked panels. Full machine queue: [qc_review.json](../../../artifacts/results/qc_review.json).", "",
             "## Flag clusters", "", "| Flag | Pending entries |", "| --- | ---: |"]
    lines += [f"| `{flag}` | {count} |" for flag, count in product["summary"]["flag_clusters"].items()]
    lines += ["", "## Required representative inspection", "",
              "| Experiment | Role | Trial and panel |", "| --- | --- | --- |"]
    for example in product["examples"]:
        trial_id = example["trial_id"]
        panel = next(row["panel"] for row in product["trials"] if row["trial_id"] == trial_id)
        lines.append(f"| E{example['experiment']} | {example['kind']} | [{trial_id}](../../../{panel}) |")
    worst = product["worst_duration_mismatch"]["trial_id"]
    panel = next(row["panel"] for row in product["trials"] if row["trial_id"] == worst)
    difference = product["worst_duration_mismatch"]["relative_difference"]
    lines += ["", f"Worst sample/logged-duration mismatch: [{worst}](../../../{panel}), {difference:.1%} at conditional 500 Hz.",
              "", "## Per-signal decisions", "",
              "The owner may reply by flag cluster and experiment, stating `accept`, `reject`, or `uncertain`, one rationale, and named trial/channel exceptions; T019 will expand that response into every matching queue entry with reviewer and time. Inspect the linked panels before assigning a group. Subj_F and Subj_H need explicit channel/trial exceptions where their evidence differs. All entries remain pending until owner sign-off.", "",
              "Here `accept` means retain the automated eligibility and flag as reviewed; `reject` excludes a signal that was automated eligible; `uncertain` leaves it unresolved and ineligible for reviewed physiology. Accepting an automatically invalid ECG retains its invalid HR/RMSSD status. No review choice can create a beat, repair a gap, or supply a missing measurement. A proposed reversal of automated invalidity needs a separately documented method decision and evidence.", "",
              "Suggested response: `E2 channel_imbalance: uncertain — inspect headset contact; exceptions: E2:Subj_F:Rm_020 eeg_trial reject because ...`. The owner can group entries with the same disposition and list exceptions, then sign a single CP-B verdict after every entry is resolved."]
    severe = {"repeated_extrema_possible_clipping", "absolute_amplitude_anomaly",
              "channel_imbalance", "duration_mismatch_over_10pct", "residual_line_noise",
              "high_frequency_muscle_candidate", "extreme_peak_to_peak", "abrupt_step"}
    rare = [entry for entry in product["entries"] if severe.intersection(entry["flags"])]
    lines += ["", "Rare or high-impact review flags are linked below; every matching trial also appears in the full decision table.",
              "", "| Trial | Signal | Severe flags | Panel |", "| --- | --- | --- | --- |"]
    for entry in rare:
        flags = ", ".join(sorted(severe.intersection(entry["flags"])))
        lines.append(f"| {entry['trial_id']} | {entry['signal']} | {flags} | {links(entry)} |")
    lines += ["", "## Complete queue", "", "| Trial | Signal | Flags | Automated eligible | Decision | Panel |",
              "| --- | --- | --- | --- | --- | --- |"]
    for entry in product["entries"]:
        lines.append(f"| {entry['trial_id']} | {entry['signal']} | {', '.join(entry['flags'])} | {entry['automated_eligible']} | pending | {links(entry)} |")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")
