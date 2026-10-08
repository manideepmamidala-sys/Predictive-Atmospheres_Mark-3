"""Approximate bilateral-forehead spectral features, not direct emotional labels."""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray
from scipy import signal

from pa.signals.common import decisions, signal_reason
from pa.signals.qc import epoch_reasons


@dataclass(frozen=True)
class EEGResult:
    valid: bool
    reasons: tuple[str, ...]
    sample_rate_hz: float
    raw_unit: str
    total_epochs: int
    accepted_epochs: int
    rejected_epochs: tuple[dict, ...]
    alpha_right: float | None = None
    alpha_left: float | None = None
    beta_right: float | None = None
    beta_left: float | None = None
    forehead_log_alpha_asymmetry: float | None = None
    log_beta_alpha_ratio: float | None = None


def _band_power(frequencies: NDArray[np.float64], psd: NDArray[np.float64],
                limits: tuple[float, float]) -> float | None:
    keep = (frequencies >= limits[0]) & (frequencies <= limits[1])
    if keep.sum() < 2:
        return None
    power = float(np.trapezoid(psd[keep], frequencies[keep]))
    return power if math.isfinite(power) and power > 0 else None


def process_eeg(right: NDArray[np.float64], left: NDArray[np.float64], counter: NDArray[np.int64],
                sample_rate_hz: float, *, drop_initial_s: float = 0,
                threshold_multiplier: float = 1.0,
                clipping_multiplier: float = 1.0) -> EEGResult:
    cfg = decisions()["eeg"]
    inputs = (np.asarray(right, dtype=float), np.asarray(left, dtype=float), np.asarray(counter))
    right, left, counter = inputs
    reasons = [reason for channel in (right, left) if (reason := signal_reason(channel, sample_rate_hz))]
    if reasons:
        return EEGResult(False, tuple(sorted(set(reasons))), sample_rate_hz, "unverified raw amplitude",
                         0, 0, ())
    if len(right) != len(left) or len(right) != len(counter):
        return EEGResult(False, ("channel_length_mismatch",), sample_rate_hz,
                         "unverified raw amplitude", 0, 0, ())
    if drop_initial_s < 0 or threshold_multiplier <= 0 or clipping_multiplier <= 0:
        raise ValueError("invalid EEG sensitivity setting")
    sample_offset = round(drop_initial_s * sample_rate_hz)
    right, left, counter = right[sample_offset:], left[sample_offset:], counter[sample_offset:]
    if sample_rate_hz / 2 <= cfg["filter_hz"][1]:
        return EEGResult(False, ("nyquist_below_filter",), sample_rate_hz,
                         "unverified raw amplitude", 0, 0, ())
    epoch_size = round(cfg["epoch_s"] * sample_rate_hz)
    total = len(right) // epoch_size
    if total == 0:
        return EEGResult(False, ("too_short_for_epoch",), sample_rate_hz,
                         "unverified raw amplitude", 0, 0, ())
    raw_epochs = [(right[i * epoch_size:(i + 1) * epoch_size],
                   left[i * epoch_size:(i + 1) * epoch_size]) for i in range(total)]
    ptps = [max(float(np.ptp(r)), float(np.ptp(l))) for r, l in raw_epochs]
    steps = [max(float(np.max(np.abs(np.diff(r)))), float(np.max(np.abs(np.diff(l)))))
             for r, l in raw_epochs]
    med_ptp = float(np.median(ptps))
    med_step = float(np.median(steps))
    jump_indices = np.flatnonzero(np.mod(np.diff(counter), 256) != 1) + 1
    sos = signal.butter(cfg["filter_order"], cfg["filter_hz"], btype="bandpass",
                        fs=sample_rate_hz, output="sos")
    nperseg = round(cfg["welch_segment_s"] * sample_rate_hz)
    noverlap = round(nperseg * cfg["welch_overlap_fraction"])
    powers: list[tuple[float, float, float, float]] = []
    rejected: list[dict] = []
    for index, (raw_right, raw_left) in enumerate(raw_epochs):
        start, stop = index * epoch_size, (index + 1) * epoch_size
        jumps = bool(np.any((jump_indices >= start) & (jump_indices < stop)))
        epoch_flags = epoch_reasons(raw_right, raw_left, jumps, med_ptp, med_step,
                                    threshold_multiplier, clipping_multiplier)
        if epoch_flags:
            rejected.append({"index": index, "start_s": drop_initial_s + start / sample_rate_hz,
                             "end_s": drop_initial_s + stop / sample_rate_hz, "reasons": epoch_flags})
            continue
        values = []
        for raw in (raw_right, raw_left):
            cleaned = signal.sosfiltfilt(sos, raw)
            frequencies, psd = signal.welch(cleaned, fs=sample_rate_hz,
                                            nperseg=nperseg, noverlap=noverlap)
            alpha = _band_power(frequencies, psd, tuple(cfg["alpha_hz"]))
            beta = _band_power(frequencies, psd, tuple(cfg["beta_hz"]))
            values.extend((alpha, beta))
        if any(value is None for value in values):
            rejected.append({"index": index, "start_s": drop_initial_s + start / sample_rate_hz,
                             "end_s": drop_initial_s + stop / sample_rate_hz,
                             "reasons": ["nonpositive_or_unresolved_band_power"]})
            continue
        powers.append((values[0], values[1], values[2], values[3]))
    accepted = len(powers)
    if accepted < cfg["min_valid_epochs"] or accepted / total < cfg["min_valid_fraction"]:
        return EEGResult(False, ("insufficient_valid_epochs",), sample_rate_hz,
                         "unverified raw amplitude", total, accepted, tuple(rejected))
    alpha_right, beta_right, alpha_left, beta_left = np.median(np.array(powers), axis=0)
    asymmetry = math.log(alpha_right) - math.log(alpha_left)
    ratio = math.log((beta_right + beta_left) / (alpha_right + alpha_left))
    return EEGResult(True, (), sample_rate_hz, "squared unverified raw amplitude",
                     total, accepted, tuple(rejected), float(alpha_right), float(alpha_left),
                     float(beta_right), float(beta_left), float(asymmetry), float(ratio))
