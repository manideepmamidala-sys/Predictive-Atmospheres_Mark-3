"""Operational wrist-ECG beat evidence; automated intervals are not verified NN beats."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from itertools import pairwise

import numpy as np
from numpy.typing import NDArray
from scipy import signal

from pa.signals.common import decisions, signal_reason
from pa.signals.qc import repeated_extrema_possible_clipping


@dataclass(frozen=True)
class ECGResult:
    valid_hr: bool
    valid_rmssd: bool
    reasons: tuple[str, ...]
    sample_rate_hz: float
    sample_duration_s: float
    polarity: str | None
    peak_count: int
    valid_interval_count: int
    heart_rate_bpm: float | None
    rmssd_ms: float | None
    peak_indices: tuple[int, ...] = ()
    rr_intervals_s: tuple[float, ...] = ()
    valid_rr_mask: tuple[bool, ...] = ()
    excluded_segments: tuple[dict, ...] = ()
    quality: dict = field(default_factory=dict)
    rmssd_scenarios: dict = field(default_factory=dict)


@dataclass(frozen=True)
class _PeakCandidate:
    peaks: NDArray[np.int64]
    correlations: NDArray[np.float64]
    ratio: float
    median_correlation: float
    morphology_fraction: float
    plausible_rr_fraction: float
    score: float
    admitted: bool


@dataclass(frozen=True)
class _Segment:
    start: int
    stop: int
    filtered: NDArray[np.float64]
    positive: _PeakCandidate
    negative: _PeakCandidate


@dataclass(frozen=True)
class _Run:
    start_sample: int
    intervals: NDArray[np.float64]

    @property
    def covered_seconds(self) -> float:
        return float(np.sum(self.intervals))


def _empty(rate: float, duration: float, reasons: list[str],
           excluded: list[dict] | None = None, quality: dict | None = None) -> ECGResult:
    return ECGResult(False, False, tuple(dict.fromkeys(reasons)), rate, duration,
                     None, 0, 0, None, None, excluded_segments=tuple(excluded or []),
                     quality=quality or {})


def _continuous_segments(raw: NDArray[np.float64], counter: NDArray[np.int64],
                         rate: float) -> tuple[list[tuple[int, int]], list[dict]]:
    cfg, qc = decisions()["ecg"], decisions()["qc"]
    n = len(raw)
    block_size = max(1, round(cfg["dropout_window_s"] * rate))
    invalid = np.zeros(n, dtype=bool)
    excluded: list[dict] = []
    cuts = {0, n}
    jumps = np.flatnonzero(np.mod(np.diff(counter), 256) != 1) + 1
    for jump in jumps:
        cuts.add(int(jump))
        excluded.append({"start_s": float(jump / rate), "end_s": float(jump / rate),
                         "reason": "counter_discontinuity"})
    for start in range(0, n, block_size):
        stop = min(start + block_size, n)
        block = raw[start:stop]
        reason = None
        if float(np.std(block)) < qc["flat_std_raw_units"]:
            reason = "flat_dropout"
        elif repeated_extrema_possible_clipping(block):
            reason = "repeated_extrema_possible_clipping"
        if reason:
            invalid[start:stop] = True
            cuts.update((start, stop))
            excluded.append({"start_s": start / rate, "end_s": stop / rate, "reason": reason})
    result = []
    ordered = sorted(cuts)
    for start, stop in pairwise(ordered):
        if invalid[start:stop].any():
            continue
        if (stop - start) / rate >= cfg["minimum_filter_segment_s"]:
            result.append((start, stop))
        elif stop > start:
            excluded.append({"start_s": start / rate, "end_s": stop / rate,
                             "reason": "short_continuous_segment"})
    return result, excluded


def _peak_candidate(filtered: NDArray[np.float64], rate: float, sign: int) -> _PeakCandidate:
    cfg = decisions()["ecg"]
    oriented = filtered * sign
    prominence = cfg["prominence_multiplier"] * float(np.quantile(np.abs(oriented),
                                                                     cfg["prominence_quantile"]))
    prominence = max(prominence, 1e-12)
    peaks, _ = signal.find_peaks(oriented, distance=max(1, round(
        cfg["minimum_peak_distance_s"] * rate)), prominence=prominence)
    half = max(1, round(cfg["template_half_window_s"] * rate))
    peaks = peaks[(peaks >= half) & (peaks + half < len(oriented))]
    if len(peaks) < 2:
        return _PeakCandidate(np.array([], dtype=np.int64), np.array([]), 0, 0, 0, 0, 0, False)
    windows = np.array([oriented[peak - half:peak + half + 1] for peak in peaks])
    windows = windows - windows.mean(axis=1, keepdims=True)
    norms = np.linalg.norm(windows, axis=1)
    if np.any(norms <= 1e-12):
        return _PeakCandidate(peaks.astype(np.int64), np.zeros(len(peaks)), 0, 0, 0, 0, 0, False)
    windows /= norms[:, None]
    template = np.median(windows, axis=0)
    template -= template.mean()
    template_norm = float(np.linalg.norm(template))
    correlations = windows @ (template / template_norm) if template_norm > 1e-12 else np.zeros(len(peaks))
    background = max(float(np.median(np.abs(filtered))), 1e-12)
    ratio = float(np.median(np.abs(filtered[peaks])) / background)
    median_correlation = float(np.median(correlations))
    morphology_fraction = float(np.mean(correlations >= cfg["individual_template_correlation"]))
    rr = np.diff(peaks) / rate
    plausible = float(np.mean((rr >= cfg["rr_range_s"][0]) &
                              (rr <= cfg["rr_range_s"][1])))
    admitted = (ratio >= cfg["minimum_peak_background_ratio"] and
                median_correlation >= cfg["minimum_median_template_correlation"] and
                morphology_fraction >= cfg["minimum_morphology_pass_fraction"])
    score = ratio * median_correlation * plausible if admitted else 0.0
    return _PeakCandidate(peaks.astype(np.int64), correlations, ratio, median_correlation,
                          morphology_fraction, plausible, score, admitted)


def _filtered_segments(raw: NDArray[np.float64], counter: NDArray[np.int64],
                       rate: float) -> tuple[list[_Segment], list[dict]]:
    cfg = decisions()["ecg"]
    spans, excluded = _continuous_segments(raw, counter, rate)
    sos = signal.butter(cfg["filter_order"], cfg["qrs_filter_hz"], btype="bandpass",
                        fs=rate, output="sos")
    segments = []
    for start, stop in spans:
        filtered = signal.sosfiltfilt(sos, raw[start:stop])
        segments.append(_Segment(start, stop, filtered,
                                 _peak_candidate(filtered, rate, 1),
                                 _peak_candidate(filtered, rate, -1)))
    return segments, excluded


def _polarity(segments: list[_Segment]) -> tuple[str | None, dict]:
    cfg = decisions()["ecg"]
    scores = {}
    for name in ("positive", "negative"):
        candidates = [getattr(segment, name) for segment in segments]
        admitted = [candidate for candidate in candidates if candidate.admitted]
        scores[name] = (float(np.average([candidate.score for candidate in admitted],
                                          weights=[len(candidate.peaks) for candidate in admitted]))
                        if admitted else 0.0)
    ordered = sorted(scores, key=scores.get, reverse=True)
    best, other = ordered
    if scores[best] <= 0:
        return None, scores
    if scores[other] > 0 and (scores[best] - scores[other]) / scores[best] < cfg["polarity_tie_fraction"]:
        return "ambiguous", scores
    return best, scores


def _quality_evidence(segments: list[_Segment], scores: dict) -> dict:
    evidence = []
    for segment in segments:
        candidates = {}
        for name in ("positive", "negative"):
            candidate = getattr(segment, name)
            candidates[name] = {
                "admitted": candidate.admitted,
                "peak_indices": (candidate.peaks + segment.start).tolist(),
                "peak_template_correlations": candidate.correlations.tolist(),
                "peak_background_ratio": candidate.ratio,
                "median_template_correlation": candidate.median_correlation,
                "morphology_pass_fraction": candidate.morphology_fraction,
                "plausible_rr_fraction": candidate.plausible_rr_fraction,
            }
        evidence.append({"start_sample": segment.start, "stop_sample": segment.stop,
                         "candidates": candidates})
    return {"polarity_scores": scores, "segments": evidence}


def _valid_intervals(candidate: _PeakCandidate, rate: float) -> NDArray[np.bool_]:
    cfg = decisions()["ecg"]
    rr = np.diff(candidate.peaks) / rate
    base = (rr >= cfg["rr_range_s"][0]) & (rr <= cfg["rr_range_s"][1])
    base &= (candidate.correlations[:-1] >= cfg["individual_template_correlation"]) & \
            (candidate.correlations[1:] >= cfg["individual_template_correlation"])
    local = base.copy()
    radius = cfg["rr_local_neighbor_radius"]
    for index, value in enumerate(rr):
        neighbors = [rr[j] for j in range(max(0, index - radius), min(len(rr), index + radius + 1))
                     if j != index and base[j]]
        if not neighbors:
            local[index] = False
            continue
        center = float(np.median(neighbors))
        local[index] &= abs(value - center) / center <= cfg["rr_outlier_fraction_from_local_median"]
    return local


def _runs(segments: list[_Segment], polarity: str, rate: float) -> tuple[list[_Run], list[int],
                                                                         list[float], list[bool]]:
    runs: list[_Run] = []
    all_peaks: list[int] = []
    all_rr: list[float] = []
    all_valid: list[bool] = []
    for segment in segments:
        candidate = getattr(segment, polarity)
        if not candidate.admitted:
            continue
        rr = np.diff(candidate.peaks) / rate
        valid = _valid_intervals(candidate, rate)
        all_peaks.extend((candidate.peaks + segment.start).tolist())
        all_rr.extend(rr.tolist())
        all_valid.extend(valid.tolist())
        start = None
        for index in range(len(valid) + 1):
            good = index < len(valid) and bool(valid[index])
            if good and start is None:
                start = index
            if not good and start is not None:
                runs.append(_Run(int(candidate.peaks[start] + segment.start), rr[start:index]))
                start = None
    return runs, all_peaks, all_rr, all_valid


def _select_run(runs: list[_Run], minimum_intervals: int, minimum_seconds: float) -> _Run | None:
    qualifying = [run for run in runs if len(run.intervals) >= minimum_intervals and
                  run.covered_seconds >= minimum_seconds]
    return max(qualifying, key=lambda run: (run.covered_seconds, -run.start_sample),
               default=None)


def process_ecg(raw: NDArray[np.float64], sample_rate_hz: float,
                counter: NDArray[np.int64]) -> ECGResult:
    cfg = decisions()["ecg"]
    raw = np.asarray(raw, dtype=float)
    counter = np.asarray(counter)
    reason = signal_reason(raw, sample_rate_hz)
    duration = len(raw) / sample_rate_hz if sample_rate_hz > 0 and math.isfinite(sample_rate_hz) else 0.0
    if reason:
        return _empty(sample_rate_hz, duration, [reason])
    if len(counter) != len(raw) or not np.isfinite(counter).all():
        return _empty(sample_rate_hz, duration, ["invalid_or_missing_counter"])
    if sample_rate_hz / 2 <= cfg["qrs_filter_hz"][1]:
        return _empty(sample_rate_hz, duration, ["nyquist_below_filter"])
    segments, excluded = _filtered_segments(raw, counter, sample_rate_hz)
    if not segments:
        return _empty(sample_rate_hz, duration,
                      ["no_usable_continuous_segment", *(item["reason"] for item in excluded)],
                      excluded)
    polarity, scores = _polarity(segments)
    quality = _quality_evidence(segments, scores)
    if polarity is None or polarity == "ambiguous":
        reason = "no_qrs_quality" if polarity is None else "ambiguous_polarity"
        return _empty(sample_rate_hz, duration, [reason], excluded, quality)
    runs, peaks, rr, valid = _runs(segments, polarity, sample_rate_hz)
    hr_run = _select_run(runs, cfg["min_hr_beats"] - 1, cfg["min_hr_usable_duration_s"])
    hr = float(60 / np.median(hr_run.intervals)) if hr_run is not None else None
    scenarios = {}
    for name, limits in cfg["rmssd_scenarios"].items():
        chosen = _select_run(runs, limits["min_intervals"], limits["duration_s"])
        value = (float(np.sqrt(np.mean((np.diff(chosen.intervals) * 1000) ** 2)))
                 if chosen is not None else None)
        scenarios[name] = {"valid": chosen is not None, "rmssd_ms": value,
                           "usable_duration_s": chosen.covered_seconds if chosen else None,
                           "valid_intervals": len(chosen.intervals) if chosen else 0,
                           "reason": None if chosen else "no_qualifying_contiguous_run"}
    primary = scenarios["primary"]
    reasons = [segment["reason"] for segment in excluded]
    if hr is None:
        reasons.append("insufficient_contiguous_beats_for_hr")
    if not primary["valid"]:
        reasons.append("insufficient_contiguous_coverage_for_rmssd")
    return ECGResult(hr is not None, primary["valid"], tuple(dict.fromkeys(reasons)),
                     sample_rate_hz, duration, polarity, len(peaks), sum(valid), hr,
                     primary["rmssd_ms"], tuple(peaks), tuple(rr), tuple(valid),
                     tuple(excluded), quality, scenarios)
