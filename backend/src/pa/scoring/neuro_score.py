"""Bounded proximity to a user-selected valence/arousal target, not health quality."""

from __future__ import annotations

import math
from dataclasses import dataclass

from pydantic import BaseModel, Field

DIAMETER = math.sqrt(8.0)


class AffectPoint(BaseModel):
    valence: float = Field(ge=-1, le=1, allow_inf_nan=False)
    arousal: float = Field(ge=-1, le=1, allow_inf_nan=False)


@dataclass(frozen=True)
class ScoreResult:
    neuro_score: float
    projected: bool
    point_used: AffectPoint


def neuro_score(point: AffectPoint, target: AffectPoint) -> float:
    distance = math.hypot(point.valence - target.valence, point.arousal - target.arousal)
    return min(1.0, max(0.0, 1.0 - distance / DIAMETER))


def score_percentage(normalized_score: float) -> float:
    """Convert the API's 0–1 Neuro-Score to the Studio's 0–100 scale."""
    if not math.isfinite(normalized_score) or not 0 <= normalized_score <= 1:
        raise ValueError("normalized Neuro-Score must be on the 0–1 scale")
    return 100.0 * normalized_score


def score_prediction(raw_valence: float, raw_arousal: float, target: AffectPoint) -> ScoreResult:
    if not math.isfinite(raw_valence) or not math.isfinite(raw_arousal):
        raise ValueError("nonfinite model prediction")
    valence = min(1.0, max(-1.0, raw_valence))
    arousal = min(1.0, max(-1.0, raw_arousal))
    point = AffectPoint(valence=valence, arousal=arousal)
    return ScoreResult(neuro_score(point, target),
                       valence != raw_valence or arousal != raw_arousal, point)
