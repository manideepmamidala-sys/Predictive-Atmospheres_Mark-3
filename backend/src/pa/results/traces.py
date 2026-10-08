"""Bounded source-order trace windows for browser inspection, never feature fitting."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray
from scipy import signal

from pa.results.schemas import TraceRecord
from pa.signals.common import decisions
from pa.signals.ecg import ECGResult
from pa.signals.eeg import EEGResult


def browser_trace(trace: dict | None, *, target_rate_hz: float = 100) -> dict | None:
    """Anti-alias browser-only display arrays; preserve exact analysis-rate provenance."""
    if trace is None:
        return None
    rate = trace.get("sample_rate_hz")
    if rate is None or rate <= 0:
        return trace
    down = max(1, round(rate / target_rate_hz))
    displayed = {**trace, "source_sample_rate_hz": rate,
                 "sample_rate_hz": rate / down}
    for key in ("raw", "cleaned"):
        values = np.asarray(trace.get(key) or [], dtype=float)
        displayed[key] = signal.resample_poly(values, 1, down).tolist() if len(values) else []
    return displayed


def eeg_window(right: NDArray[np.float64], result: EEGResult,
               sample_rate_hz: float) -> TraceRecord:
    """Display first full epoch; only filter a QC-admitted epoch."""
    width = round(decisions()["eeg"]["epoch_s"] * sample_rate_hz)
    raw = np.asarray(right[:width], dtype=float)
    if len(raw) != width:
        return TraceRecord(sample_rate_hz=sample_rate_hz, unit="unverified raw amplitude",
                           channel="Channel1 / approximate right forehead", raw=raw.tolist())
    rejected = any(item["index"] == 0 for item in result.rejected_epochs)
    cleaned = []
    if not rejected and result.total_epochs > 0:
        cfg = decisions()["eeg"]
        sos = signal.butter(cfg["filter_order"], cfg["filter_hz"], btype="bandpass",
                            fs=sample_rate_hz, output="sos")
        cleaned = signal.sosfiltfilt(sos, raw).tolist()
    return TraceRecord(sample_rate_hz=sample_rate_hz, unit="unverified raw amplitude",
                       channel="Channel1 / approximate right forehead", raw=raw.tolist(),
                       cleaned=cleaned,
                       rejected_segments=[(0.0, width / sample_rate_hz)] if rejected else [])


def ecg_window(raw_ecg: NDArray[np.float64], result: ECGResult,
               sample_rate_hz: float) -> TraceRecord:
    """Show the first four source seconds; do not bridge rejected/gap segments."""
    width = min(len(raw_ecg), round(4 * sample_rate_hz))
    raw = np.asarray(raw_ecg[:width], dtype=float)
    duration = len(raw) / sample_rate_hz
    rejected = [(max(0.0, item["start_s"]), min(duration, item["end_s"]))
                for item in result.excluded_segments
                if item["start_s"] < duration and item["end_s"] > 0]
    accepted_span = next((item for item in result.quality.get("segments", [])
                          if item["start_sample"] <= 0 and item["stop_sample"] >= width), None)
    cleaned = []
    if accepted_span is not None and not rejected and width > 0:
        cfg = decisions()["ecg"]
        sos = signal.butter(cfg["filter_order"], cfg["qrs_filter_hz"],
                            btype="bandpass", fs=sample_rate_hz, output="sos")
        filtered = signal.sosfiltfilt(sos, raw_ecg[:accepted_span["stop_sample"]])
        cleaned = filtered[:width].tolist()
    return TraceRecord(sample_rate_hz=sample_rate_hz, unit="unverified raw amplitude",
                       channel="Channel3 / owner-reported wrist ECG", raw=raw.tolist(),
                       cleaned=cleaned, rejected_segments=rejected)
