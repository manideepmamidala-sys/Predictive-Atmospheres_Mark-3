"""Shared fitted-artifact inference for direct, CLI and API calls."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from pa.features.builder import FEATURE_ORDER, build_features
from pa.features.schema import RoomInput
from pa.modeling.artifact import LoadedArtifact
from pa.scoring.neuro_score import AffectPoint, score_prediction


@dataclass(frozen=True)
class Prediction:
    valence: float
    arousal: float
    raw_valence: float
    raw_arousal: float
    projected: bool
    neuro_score: float


def feature_frame(rooms: list[RoomInput]) -> pd.DataFrame:
    return pd.DataFrame([build_features(room) for room in rooms], columns=FEATURE_ORDER)


def predict_room(artifact: LoadedArtifact, room: RoomInput, target: AffectPoint) -> Prediction:
    output = np.asarray(artifact.pipeline.predict(feature_frame([room])), dtype=float)
    if output.shape != (1, 2) or not np.isfinite(output).all():
        raise ValueError("model returned invalid valence/arousal shape or values")
    raw_valence, raw_arousal = map(float, output[0])
    scored = score_prediction(raw_valence, raw_arousal, target)
    return Prediction(scored.point_used.valence, scored.point_used.arousal,
                      raw_valence, raw_arousal, scored.projected, scored.neuro_score)
