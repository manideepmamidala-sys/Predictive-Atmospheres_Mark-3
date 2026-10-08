"""Reproducible representative trace/spectrum panels for human QC inspection."""

from __future__ import annotations

import json
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
    require_science_checkpoint()
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
