import math

import pytest
from pydantic import ValidationError

from pa.scoring.neuro_score import AffectPoint, neuro_score, score_prediction


def test_score_at_target_and_monotonicity():
    target = AffectPoint(valence=0.4, arousal=-0.2)
    assert neuro_score(target, target) == 1
    assert neuro_score(AffectPoint(valence=0.5, arousal=-0.2), target) > neuro_score(
        AffectPoint(valence=0.9, arousal=-0.2), target)
    assert neuro_score(AffectPoint(valence=-1, arousal=1), AffectPoint(valence=1, arousal=-1)) == 0


def test_user_target_and_projection_are_explicit():
    target = AffectPoint(valence=0, arousal=0)
    result = score_prediction(2, 0, target)
    assert result.projected and result.point_used.valence == 1
    assert result.neuro_score == pytest.approx(1 - 1 / math.sqrt(8))
    assert neuro_score(AffectPoint(valence=1, arousal=0), target) != neuro_score(
        AffectPoint(valence=1, arousal=0), AffectPoint(valence=1, arousal=0))
    with pytest.raises(ValueError):
        score_prediction(float("nan"), 0, target)
    with pytest.raises(ValidationError):
        AffectPoint(valence=2, arousal=0)
