"""Fold-fitted population affect construction; never use held-out calibration data."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from numpy.typing import NDArray

from pa.signals.common import decisions

COMPONENTS = ("faa", "alpha_suppression", "engagement", "heart_rate_bpm")


class CalibrationUnavailable(ValueError):
    """Training partition cannot identify a required component scale."""


@dataclass(frozen=True)
class PopulationCalibrator:
    centers: dict[str, float]
    scales: dict[str, float]

    @classmethod
    def fit(cls, raw: pd.DataFrame) -> PopulationCalibrator:
        cfg = decisions()["affect"]
        centers: dict[str, float] = {}
        scales: dict[str, float] = {}
        for name in COMPONENTS:
            if name not in raw:
                raise CalibrationUnavailable(f"missing component {name}")
            values = raw[name].to_numpy(dtype=float)
            values = values[np.isfinite(values)]
            if len(np.unique(values)) < cfg["min_population_distinct_values"]:
                raise CalibrationUnavailable(f"uncalibratable component {name}: too few distinct values")
            center = float(np.median(values))
            scale = float(np.median(np.abs(values - center)) * cfg["robust_scale_mad_factor"])
            if scale < cfg["min_population_scale"]:
                raise CalibrationUnavailable(f"uncalibratable component {name}: zero robust scale")
            centers[name], scales[name] = center, scale
        return cls(centers, scales)

    def components(self, raw: pd.DataFrame) -> NDArray[np.float64]:
        values = []
        for name in COMPONENTS:
            component = raw[name].to_numpy(dtype=float)
            mapped = np.full(component.shape, np.nan, dtype=float)
            valid = np.isfinite(component)
            mapped[valid] = np.tanh((component[valid] - self.centers[name]) /
                                    self.scales[name])
            values.append(mapped)
        return np.stack(values, axis=1)

    def fused(self, raw: pd.DataFrame, reports: NDArray[np.float64],
              alpha: float | None = None) -> NDArray[np.float64]:
        alpha = decisions()["affect"]["primary_alpha"] if alpha is None else alpha
        if not 0 <= alpha <= 1:
            raise ValueError("alpha outside [0,1]")
        if reports.shape != (len(raw), 2):
            raise ValueError("self-report shape mismatch")
        components = self.components(raw)
        eeg_arousal = 0.5 * (components[:, 1] + components[:, 2])
        objective = np.stack((components[:, 0],
                              0.5 * eeg_arousal + 0.5 * components[:, 3]), axis=1)
        if not np.isfinite(objective).all() or not np.isfinite(reports).all():
            raise CalibrationUnavailable("missing or nonfinite component/report in complete target cohort")
        if np.any(np.abs(reports) > 1):
            raise ValueError("self-report outside transformed signed range")
        return alpha * objective + (1 - alpha) * reports
