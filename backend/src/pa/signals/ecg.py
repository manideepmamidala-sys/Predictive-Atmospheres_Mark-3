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
    coverage: dict = field(default_factory=dict)
    eligibility: dict = field(default_factory=dict)


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
           excluded: list[dict] | None = None, quality: dict | None = None,
           segments: list[_Segment] | None = None) -> ECGResult:
    coverage = _coverage(duration, rate, segments or [], [], None, None)
    reason = reasons[0] if reasons else "no_qrs_quality"
    return ECGResult(False, False, tuple(dict.fromkeys(reasons)), rate, duration,
                     None, 0, 0, None, None, excluded_segments=tuple(excluded or []),
                     quality=quality or {}, coverage=coverage,
                     eligibility={"heart_rate": {"automated_eligible": False, "reason": reason},
                                  "rmssd_30s": {"automated_eligible": False, "reason": reason},
                                  "human_review": "pending_cp_b"})


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


def _run_summary(run: _Run | None, rate: float) -> dict | None:
    if run is None:
        return None
    return {"start_s": run.start_sample / rate,
            "end_s": run.start_sample / rate + run.covered_seconds,
            "covered_seconds": run.covered_seconds,
            "valid_intervals": len(run.intervals)}


def _coverage(duration: float, rate: float, segments: list[_Segment],
              runs: list[_Run], hr_run: _Run | None, rmssd_run: _Run | None) -> dict:
    """Separate filterable source seconds from seconds covered by accepted RR runs."""
    filterable = sum((segment.stop - segment.start) / rate for segment in segments)
    valid_rr = sum(run.covered_seconds for run in runs)
    longest = max(runs, key=lambda run: (run.covered_seconds, -run.start_sample), default=None)
    return {"source_seconds": duration, "filterable_seconds": filterable,
            "filterable_fraction": filterable / duration if duration else 0.0,
            "valid_rr_seconds": valid_rr,
            "valid_rr_fraction": valid_rr / duration if duration else 0.0,
            "filterable_segment_count": len(segments), "valid_run_count": len(runs),
            "longest_valid_run": _run_summary(longest, rate),
            "heart_rate_run": _run_summary(hr_run, rate),
            "rmssd_30s_run": _run_summary(rmssd_run, rate)}


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
        return _empty(sample_rate_hz, duration, [reason], excluded, quality, segments)
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
                           "run": _run_summary(chosen, sample_rate_hz),
                           "reason": None if chosen else "no_qualifying_contiguous_run"}
    primary = scenarios["primary"]
    reasons = [segment["reason"] for segment in excluded]
    if hr is None:
        reasons.append("insufficient_contiguous_beats_for_hr")
    if not primary["valid"]:
        reasons.append("insufficient_contiguous_coverage_for_rmssd")
    rmssd_run = _select_run(runs, cfg["rmssd_scenarios"]["primary"]["min_intervals"],
                            cfg["rmssd_scenarios"]["primary"]["duration_s"])
    coverage = _coverage(duration, sample_rate_hz, segments, runs, hr_run, rmssd_run)
    eligibility = {
        "heart_rate": {"automated_eligible": hr is not None,
                       "reason": None if hr is not None else "insufficient_contiguous_beats_for_hr"},
        "rmssd_30s": {"automated_eligible": primary["valid"],
                      "reason": None if primary["valid"] else "insufficient_contiguous_coverage_for_rmssd"},
        "human_review": "pending_cp_b",
    }
    return ECGResult(hr is not None, primary["valid"], tuple(dict.fromkeys(reasons)),
                     sample_rate_hz, duration, polarity, len(peaks), sum(valid), hr,
                     primary["rmssd_ms"], tuple(peaks), tuple(rr), tuple(valid),
                     tuple(excluded), quality, scenarios, coverage, eligibility)


def ecg_review_examples(raw: NDArray[np.float64], result: ECGResult) -> list[dict]:
    """Provide bounded, source-indexed ECG examples for human trace/spectrum review.

    Filtering is repeated only inside a QC-admitted continuous segment. Rejected
    blocks and counter gaps keep raw evidence, with no synthetic filtered trace.
    """
    rate = result.sample_rate_hz
    raw = np.asarray(raw, dtype=float)
    if not math.isfinite(rate) or rate <= 0 or len(raw) == 0:
        return []
    cfg = decisions()["ecg"]
    width = max(1, round(4 * rate))

    def spectrum(values: NDArray[np.float64]) -> dict | None:
        if len(values) < 2 or not np.isfinite(values).all():
            return None
        size = min(len(values), max(2, round(2 * rate)))
        frequency, power = signal.welch(values, fs=rate, window="hann",
                                         nperseg=size, noverlap=size // 2,
                                         detrend="constant")
        return {"frequency_hz": frequency.tolist(), "power_per_hz": power.tolist(),
                "power_unit": "unverified raw amplitude squared per Hz"}

    def example(kind: str, start: int, stop: int, reason: str | None,
                cleaned: NDArray[np.float64] | None = None) -> dict:
        values = raw[start:stop]
        filtered = cleaned.tolist() if cleaned is not None else None
        crosses_counter_gap = any(
            start < round(item["start_s"] * rate) < stop
            for item in result.excluded_segments
            if item["reason"] == "counter_discontinuity"
        )
        return {"kind": kind, "reason": reason, "start_sample": start,
                "stop_sample": stop, "start_s": start / rate, "end_s": stop / rate,
                "sample_rate_hz": rate, "rate_status": decisions()["rate"]["primary_status"],
                "amplitude_unit": "unverified raw amplitude",
                "raw": [float(value) if math.isfinite(value) else None for value in values],
                "filtered": filtered,
                "raw_spectrum": None if crosses_counter_gap else spectrum(values),
                "filtered_spectrum": spectrum(cleaned) if cleaned is not None else None}

    examples: list[dict] = []
    accepted = result.quality.get("segments", [])
    longest = result.coverage.get("longest_valid_run")
    target = round(longest["start_s"] * rate) if longest else None
    span = next((item for item in accepted
                 if target is not None and item["start_sample"] <= target < item["stop_sample"]),
                accepted[0] if accepted else None)
    if span is not None:
        segment_start, segment_stop = span["start_sample"], span["stop_sample"]
        start = min(max(target if target is not None else segment_start, segment_start),
                    max(segment_start, segment_stop - width))
        stop = min(start + width, segment_stop)
        sos = signal.butter(cfg["filter_order"], cfg["qrs_filter_hz"],
                            btype="bandpass", fs=rate, output="sos")
        filtered_segment = signal.sosfiltfilt(sos, raw[segment_start:segment_stop])
        examples.append(example("accepted_run" if longest else "filterable_segment",
                                start, stop, None,
                                filtered_segment[start - segment_start:stop - segment_start]))

    seen_reasons: set[str] = set()
    for item in result.excluded_segments:
        reason = item["reason"]
        if reason in seen_reasons:
            continue
        seen_reasons.add(reason)
        center = round(item["start_s"] * rate)
        start = max(0, center - width // 2)
        stop = min(len(raw), start + width)
        start = max(0, stop - width)
        examples.append(example("flagged_source", start, stop, reason))
    if not result.valid_hr and not any(item["kind"] == "flagged_source" for item in examples):
        invalid = np.flatnonzero(~np.isfinite(raw))
        center = int(invalid[0]) if len(invalid) else 0
        start = min(max(0, center - width // 2), max(0, len(raw) - width))
        examples.append(example("flagged_source", start, min(len(raw), start + width),
                                result.eligibility.get("heart_rate", {}).get("reason")))
    return examples
