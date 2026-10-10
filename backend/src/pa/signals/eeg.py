"""Approximate forehead spectra and independent, raw-QC-gated candidates."""

from __future__ import annotations

import math
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field

import numpy as np
from numpy.typing import NDArray
from scipy import signal

from pa.signals.common import decisions, signal_reason
from pa.signals.qc import channel_epoch_reasons


@dataclass(frozen=True)
class EEGResult:
    # The original fields remain available to existing signal/result consumers.
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
    theta_right: float | None = None
    theta_left: float | None = None
    high_frequency_right: float | None = None
    high_frequency_left: float | None = None
    alpha_suppression: float | None = None
    engagement: float | None = None
    muscle_activity: float | None = None
    ocular_activity: float | None = None
    ocular_activity_reason: str = "unavailable_detector_not_validated"
    arousal_channel_scope: str = "unavailable"
    channel_qc: dict[str, dict] = field(default_factory=dict)
    trial_qc: dict = field(default_factory=dict)


def experiment_amplitude_references(results: Iterable[EEGResult]) -> dict[str, float]:
    """Pool nonflat trial medians from one experiment, separately by channel.

    The caller groups recordings by experiment. A first pass without references
    supplies these medians; a second pass applies the fixed experiment values.
    """
    values: dict[str, list[float]] = {"right": [], "left": []}
    for result in results:
        for name, channel_values in values.items():
            median = result.channel_qc.get(name, {}).get("raw_epoch_std_median")
            if median is not None and math.isfinite(median) and median > 0:
                channel_values.append(median)
    return {name: float(np.median(medians)) for name, medians in values.items() if medians}


def _band_power(frequencies: NDArray[np.float64], psd: NDArray[np.float64],
                limits: tuple[float, float], *, allow_zero: bool = False) -> float | None:
    keep = (frequencies >= limits[0]) & (frequencies <= limits[1])
    if keep.sum() < 2:
        return None
    power = float(np.trapezoid(psd[keep], frequencies[keep]))
    return power if math.isfinite(power) and (power >= 0 if allow_zero else power > 0) else None


def _ratio(numerator: float | None, denominator: float | None) -> float | None:
    if numerator is None or denominator is None or denominator <= 0:
        return None
    value = numerator / denominator
    return value if math.isfinite(value) else None


def _median(values: list[float]) -> float | None:
    return float(np.median(values)) if values else None


def process_eeg(right: NDArray[np.float64], left: NDArray[np.float64], counter: NDArray[np.int64],
                sample_rate_hz: float, *, drop_initial_s: float = 0,
                threshold_multiplier: float = 1.0,
                clipping_multiplier: float = 1.0,
                allowed_channels: frozenset[str] | None = None,
                amplitude_reference_raw_std: Mapping[str, float] | None = None,
                line_noise_ratio_threshold: float | None = None,
                muscle_ratio_threshold: float | None = None,
                channel_imbalance_bounds: tuple[float, float] | None = None) -> EEGResult:
    """Screen each channel independently; ``valid`` means bilateral FAA coverage.

    Amplitude reference medians must be calculated over nonflat recordings in the
    same experiment by the caller. Review flags never change automatic eligibility.
    """
    cfg = decisions()["eeg"]
    quality = decisions()["qc"]
    if line_noise_ratio_threshold is None:
        line_noise_ratio_threshold = float(cfg["raw_line_power_ratio_max"])
    if muscle_ratio_threshold is None:
        muscle_ratio_threshold = float(cfg["filtered_muscle_power_ratio_max"])
    if channel_imbalance_bounds is None:
        channel_imbalance_bounds = tuple(cfg["channel_std_ratio_range"])
    right, left = np.asarray(right, dtype=float), np.asarray(left, dtype=float)
    counter = np.asarray(counter)
    reasons = [reason for channel in (right, left)
               if (reason := signal_reason(channel, sample_rate_hz)) and
               reason != "nonfinite_samples"]
    if reasons:
        return EEGResult(False, tuple(sorted(set(reasons))), sample_rate_hz,
                         "unverified raw amplitude", 0, 0, ())
    if counter.ndim != 1 or len(right) != len(left) or len(right) != len(counter):
        return EEGResult(False, ("channel_length_mismatch",), sample_rate_hz,
                         "unverified raw amplitude", 0, 0, ())
    if not np.issubdtype(counter.dtype, np.number) or not np.isfinite(counter).all():
        return EEGResult(False, ("invalid_counter",), sample_rate_hz,
                         "unverified raw amplitude", 0, 0, ())
    low, high = channel_imbalance_bounds
    if (drop_initial_s < 0 or threshold_multiplier <= 0 or clipping_multiplier <= 0 or
            line_noise_ratio_threshold <= 0 or muscle_ratio_threshold <= 0 or
            not (0 < low < high) or not all(math.isfinite(value) for value in
                                             (drop_initial_s, threshold_multiplier,
                                              clipping_multiplier, line_noise_ratio_threshold,
                                              muscle_ratio_threshold, low, high))):
        raise ValueError("invalid EEG sensitivity setting")
    if sample_rate_hz / 2 <= max(cfg["filter_hz"][1], cfg["raw_line_hz"][1]):
        return EEGResult(False, ("nyquist_below_qc_band",), sample_rate_hz,
                         "unverified raw amplitude", 0, 0, ())
    sample_offset = round(drop_initial_s * sample_rate_hz)
    right, left, counter = right[sample_offset:], left[sample_offset:], counter[sample_offset:]
    epoch_size = round(cfg["epoch_s"] * sample_rate_hz)
    total = len(right) // epoch_size
    if total == 0:
        return EEGResult(False, ("too_short_for_epoch",), sample_rate_hz,
                         "unverified raw amplitude", 0, 0, (),
                         trial_qc={"discarded_tail_samples": len(right)})

    names = ("right", "left")
    if allowed_channels is not None and not allowed_channels <= set(names):
        raise ValueError("unknown allowed EEG channel")
    arrays = {"right": right, "left": left}
    raw_epochs = {name: [raw[i * epoch_size:(i + 1) * epoch_size]
                         for i in range(total)] for name, raw in arrays.items()}
    # The robust recording reference is a median of finite epoch metrics. A bad
    # epoch cannot inflate the rejection threshold for its neighbors.
    baselines: dict[str, tuple[float, float]] = {}
    for name in names:
        finite = [epoch for epoch in raw_epochs[name] if np.isfinite(epoch).all()]
        ptps = [float(np.ptp(epoch)) for epoch in finite]
        steps = [float(np.max(np.abs(np.diff(epoch)))) for epoch in finite]
        baselines[name] = (_median(ptps) or 0.0, _median(steps) or 0.0)

    jumps = np.flatnonzero(np.mod(np.diff(counter), 256) != 1) + 1
    sos = signal.butter(cfg["filter_order"], cfg["filter_hz"], btype="bandpass",
                        fs=sample_rate_hz, output="sos")
    nperseg = round(cfg["welch_segment_s"] * sample_rate_hz)
    noverlap = round(nperseg * cfg["welch_overlap_fraction"])
    channel_rejected: dict[str, list[dict]] = {name: [] for name in names}
    channel_powers: dict[str, dict[int, dict[str, float]]] = {name: {} for name in names}
    channel_raw_std: dict[str, list[float]] = {name: [] for name in names}
    channel_line: dict[str, list[float]] = {name: [] for name in names}
    channel_muscle: dict[str, list[float]] = {name: [] for name in names}
    paired_rejected: list[dict] = []
    imbalance_ratios: list[float] = []

    for index in range(total):
        start, stop = index * epoch_size, (index + 1) * epoch_size
        gap = bool(np.any((jumps >= start) & (jumps < stop)))
        epoch_flags: dict[str, list[str]] = {}
        for name in names:
            raw = raw_epochs[name][index]
            ptp, step = baselines[name]
            flags = channel_epoch_reasons(raw, gap, ptp, step,
                                          threshold_multiplier, clipping_multiplier)
            epoch_flags[name] = flags
            if np.isfinite(raw).all() and not gap:
                standard_deviation = float(np.std(raw))
                if standard_deviation >= quality["flat_std_raw_units"]:
                    channel_raw_std[name].append(standard_deviation)
        right_raw, left_raw = raw_epochs["right"][index], raw_epochs["left"][index]
        if not gap and all(np.isfinite(raw).all() and
                           float(np.std(raw)) >= quality["flat_std_raw_units"]
                           for raw in (right_raw, left_raw)):
            imbalance_ratios.append(float(np.std(right_raw) / np.std(left_raw)))

        for name in names:
            if epoch_flags[name]:
                continue
            raw = raw_epochs[name][index]
            raw_f, raw_psd = signal.welch(raw - np.mean(raw), fs=sample_rate_hz,
                                         window="hann", nperseg=nperseg, noverlap=noverlap)
            raw_total = _band_power(raw_f, raw_psd, tuple(cfg["raw_reference_hz"]))
            raw_line = _band_power(raw_f, raw_psd, tuple(cfg["raw_line_hz"]), allow_zero=True)
            line_ratio = _ratio(raw_line, raw_total)
            cleaned = signal.sosfiltfilt(sos, raw)
            frequencies, psd = signal.welch(cleaned, fs=sample_rate_hz, window="hann",
                                            nperseg=nperseg, noverlap=noverlap)
            powers = {"theta": _band_power(frequencies, psd, tuple(cfg["theta_hz"])),
                      "alpha": _band_power(frequencies, psd, tuple(cfg["alpha_hz"])),
                      "beta": _band_power(frequencies, psd, tuple(cfg["beta_hz"])),
                      "high_frequency": _band_power(frequencies, psd, tuple(cfg["muscle_hz"]))}
            filtered_total = _band_power(frequencies, psd, tuple(cfg["filter_hz"]))
            muscle_ratio = _ratio(powers["high_frequency"], filtered_total)
            if any(value is None for value in powers.values()):
                epoch_flags[name].append("nonpositive_or_unresolved_band_power")
                continue
            channel_powers[name][index] = {key: float(value) for key, value in powers.items()}
            if line_ratio is not None:
                channel_line[name].append(line_ratio)
            if muscle_ratio is not None:
                channel_muscle[name].append(muscle_ratio)
            if line_ratio is None or muscle_ratio is None:
                # A ratio failure is review evidence, not a made-up zero.
                channel_powers[name][index]["qc_ratio_unavailable"] = 1.0

        start_s = drop_initial_s + start / sample_rate_hz
        end_s = drop_initial_s + stop / sample_rate_hz
        for name in names:
            if epoch_flags[name]:
                channel_rejected[name].append({"index": index, "start_s": start_s,
                                               "end_s": end_s, "reasons": epoch_flags[name]})
        if any(epoch_flags.values()):
            paired_rejected.append({"index": index, "start_s": start_s, "end_s": end_s,
                                    "reasons": sorted(set(epoch_flags["right"] +
                                                          epoch_flags["left"])),
                                    "channel_reasons": epoch_flags})

    minimum_count = cfg["min_valid_epochs"]
    minimum_fraction = cfg["min_valid_fraction"]
    channel_qc: dict[str, dict] = {}
    for name in names:
        accepted = len(channel_powers[name])
        eligible = accepted >= minimum_count and accepted / total >= minimum_fraction
        line_ratio = _median(channel_line[name])
        muscle_ratio = _median(channel_muscle[name])
        raw_std = _median(channel_raw_std[name])
        flags: list[str] = []
        if accepted and (len(channel_line[name]) != accepted or
                         len(channel_muscle[name]) != accepted):
            flags.append("qc_ratio_unavailable")
        if line_ratio is not None and line_ratio > line_noise_ratio_threshold:
            flags.append("residual_line_noise")
        if muscle_ratio is not None and muscle_ratio > muscle_ratio_threshold:
            flags.append("high_frequency_muscle_candidate")
        reference = ((amplitude_reference_raw_std or {}).get(name))
        reference_valid = (reference is not None and math.isfinite(reference) and reference > 0)
        amplitude_low, amplitude_high = cfg["amplitude_experiment_median_ratio_range"]
        lower = amplitude_low * reference if reference_valid else None
        upper = amplitude_high * reference if reference_valid else None
        if reference_valid and raw_std is not None and (raw_std < lower or raw_std > upper):
            flags.append("absolute_amplitude_anomaly")
        if amplitude_reference_raw_std is not None and not reference_valid:
            flags.append("amplitude_reference_unavailable")
        channel_qc[name] = {
            "eligible": eligible, "total_epochs": total, "accepted_epochs": accepted,
            "accepted_fraction": accepted / total, "rejected_epochs": channel_rejected[name],
            "reasons": [] if eligible else ["insufficient_valid_epochs"],
            "raw_epoch_std_median": raw_std,
            "amplitude_reference_raw_std": float(reference) if reference_valid else None,
            "amplitude_lower_threshold": lower, "amplitude_upper_threshold": upper,
            "line_noise_ratio": line_ratio, "line_noise_threshold": line_noise_ratio_threshold,
            "muscle_ratio": muscle_ratio, "muscle_threshold": muscle_ratio_threshold,
            "review_flags": flags,
            "powers": {band: _median([entry[band] for entry in channel_powers[name].values()])
                       if eligible else None for band in ("theta", "alpha", "beta", "high_frequency")},
        }

    paired_indices = sorted(set(channel_powers["right"]) & set(channel_powers["left"]))
    paired_count = len(paired_indices)
    valid = (all(channel_qc[name]["eligible"] and
                 (allowed_channels is None or name in allowed_channels) for name in names) and
             paired_count >= minimum_count and paired_count / total >= minimum_fraction)
    imbalance = _median(imbalance_ratios)
    trial_flags = []
    if imbalance is None:
        trial_flags.append("qc_ratio_unavailable")
    elif imbalance < low or imbalance > high:
        trial_flags.append("channel_imbalance")
    for name in names:
        trial_flags.extend(flag for flag in channel_qc[name]["review_flags"]
                           if flag not in trial_flags)
    trial_qc = {
        "accepted_fraction": paired_count / total,
        "discarded_tail_samples": len(right) - total * epoch_size,
        "channel_imbalance_ratio": imbalance, "channel_imbalance_bounds": [low, high],
        "review_flags": trial_flags,
        "counter_discontinuities": len(jumps),
        "candidate_aggregation": "median_of_accepted_epoch_expression",
        "faa_aggregation": "median_of_paired_epoch_log_alpha_difference",
    }
    eligible_names = [name for name in names if channel_qc[name]["eligible"] and
                      (allowed_channels is None or name in allowed_channels)]
    if valid:
        scope = "bilateral"
    elif len(eligible_names) == 2:
        scope = "independent_right_left"
    elif len(eligible_names) == 1:
        scope = f"single_{eligible_names[0]}"
    else:
        scope = "unavailable"
    contributors = {"both": 0, "right_only": 0, "left_only": 0}
    for index in range(total):
        present = [name for name in eligible_names if index in channel_powers[name]]
        if scope == "bilateral" and len(present) != 2:
            continue
        if len(present) == 2:
            contributors["both"] += 1
        elif present:
            contributors[f"{present[0]}_only"] += 1
    trial_qc["candidate_epoch_contributors"] = contributors

    def median_candidate(bands: tuple[str, ...], expression: str) -> float | None:
        if scope == "unavailable":
            return None
        values: list[float] = []
        for index in range(total):
            if scope == "bilateral" and index not in paired_indices:
                continue
            entries = [channel_powers[name][index] for name in eligible_names
                       if index in channel_powers[name]]
            if not entries:
                continue
            means = [float(np.mean([entry[band] for entry in entries])) for band in bands]
            if expression == "alpha_suppression":
                values.append(-math.log(means[0]))
            elif expression == "engagement":
                values.append(math.log(means[0] / (means[1] + means[2])))
            else:
                values.append(math.log(means[0]))
        return _median(values)

    alpha_suppression = median_candidate(("alpha",), "alpha_suppression")
    engagement = median_candidate(("beta", "alpha", "theta"), "engagement")
    muscle_activity = median_candidate(("high_frequency",), "muscle")
    paired_powers = {name: {band: _median([channel_powers[name][i][band] for i in paired_indices])
                            for band in ("alpha", "beta")} for name in names} if valid else None
    alpha_right = (paired_powers["right"]["alpha"] if valid else
                   channel_qc["right"]["powers"]["alpha"])
    alpha_left = (paired_powers["left"]["alpha"] if valid else
                  channel_qc["left"]["powers"]["alpha"])
    beta_right = (paired_powers["right"]["beta"] if valid else
                  channel_qc["right"]["powers"]["beta"])
    beta_left = (paired_powers["left"]["beta"] if valid else
                 channel_qc["left"]["powers"]["beta"])
    faa = _median([
        math.log(channel_powers["right"][i]["alpha"]) -
        math.log(channel_powers["left"][i]["alpha"])
        for i in paired_indices]) if valid else None
    legacy_ratio = _median([
        math.log((channel_powers["right"][i]["beta"] +
                  channel_powers["left"][i]["beta"]) /
                 (channel_powers["right"][i]["alpha"] +
                  channel_powers["left"][i]["alpha"]))
        for i in paired_indices]) if valid else None
    return EEGResult(valid, () if valid else ("insufficient_valid_epochs",), sample_rate_hz,
                     "squared unverified raw amplitude", total, paired_count,
                     tuple(paired_rejected), alpha_right, alpha_left, beta_right, beta_left,
                     faa, legacy_ratio,
                     channel_qc["right"]["powers"]["theta"],
                     channel_qc["left"]["powers"]["theta"],
                     channel_qc["right"]["powers"]["high_frequency"],
                     channel_qc["left"]["powers"]["high_frequency"],
                     alpha_suppression, engagement, muscle_activity,
                     ocular_activity_reason=cfg["ocular_detector"],
                     arousal_channel_scope=scope, channel_qc=channel_qc, trial_qc=trial_qc)
