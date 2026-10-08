"""Raw-unit-free EEG epoch quality flags."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from pa.signals.common import decisions


def repeated_extrema_possible_clipping(raw: NDArray[np.float64], multiplier: float = 1.0) -> bool:
    """Flag long exact plateaus at raw extrema without assuming voltage units."""
    settings = decisions()["qc"]
    if raw.size == 0 or not np.isfinite(raw).all():
        return False
    maximum, minimum = float(np.max(raw)), float(np.min(raw))
    top = float(np.mean(raw == maximum))
    bottom = float(np.mean(raw == minimum))
    one = settings["repeated_one_extremum_fraction"] * multiplier
    both = settings["repeated_both_extrema_fraction"] * multiplier
    substantial = settings["extremum_magnitude_fraction"] * max(abs(maximum), abs(minimum))
    one_sided = (top >= one and abs(maximum) >= substantial) or \
        (bottom >= one and abs(minimum) >= substantial)
    return one_sided or min(top, bottom) >= both


def epoch_reasons(right: NDArray[np.float64], left: NDArray[np.float64],
                  discontinuity: bool, median_ptp: float, median_step: float,
                  threshold_multiplier: float = 1.0,
                  clipping_multiplier: float = 1.0) -> list[str]:
    settings = decisions()["eeg"]
    quality = decisions()["qc"]
    reasons: list[str] = []
    if discontinuity:
        reasons.append("counter_discontinuity")
    if not np.isfinite(right).all() or not np.isfinite(left).all():
        reasons.append("nonfinite_samples")
        return reasons
    if min(float(np.std(right)), float(np.std(left))) < quality["flat_std_raw_units"]:
        reasons.append("flat_channel")
    if repeated_extrema_possible_clipping(right, clipping_multiplier) or \
            repeated_extrema_possible_clipping(left, clipping_multiplier):
        reasons.append("repeated_extrema_possible_clipping")
    peak_to_peak = max(float(np.ptp(right)), float(np.ptp(left)))
    step = max(float(np.max(np.abs(np.diff(right)))), float(np.max(np.abs(np.diff(left)))))
    if median_ptp > 0 and peak_to_peak > (settings["max_peak_to_peak_median_multiple"] *
                                           threshold_multiplier * median_ptp):
        reasons.append("extreme_peak_to_peak")
    if median_step > 0 and step > settings["max_step_median_multiple"] * threshold_multiplier * median_step:
        reasons.append("abrupt_step")
    return reasons
