"""Versioned processing settings and shared input checks."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import numpy as np
import yaml
from numpy.typing import NDArray

SETTINGS = Path(__file__).resolve().parents[1] / "decisions.yaml"


@lru_cache(maxsize=1)
def decisions() -> dict:
    return yaml.safe_load(SETTINGS.read_text())


def signal_reason(signal: NDArray[np.float64], sample_rate_hz: float) -> str | None:
    if not np.isfinite(sample_rate_hz) or sample_rate_hz <= 0:
        return "invalid_sample_rate"
    if signal.ndim != 1 or len(signal) == 0:
        return "empty_or_wrong_shape"
    if not np.isfinite(signal).all():
        return "nonfinite_samples"
    return None
