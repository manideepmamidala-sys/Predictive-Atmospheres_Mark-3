import math

import pytest
from pydantic import ValidationError

from pa.scoring.neuro_score import AffectPoint, neuro_score, score_percentage, score_prediction


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


def test_api_score_scale_conversion_rejects_wrong_scale():
    assert score_percentage(0.65) == pytest.approx(65)
    for invalid in (-0.01, 1.01, 65, float("nan")):
        with pytest.raises(ValueError, match="0–1 scale"):
            score_percentage(invalid)


def test_projection_and_score_are_bounded_at_numeric_edges():
    target = AffectPoint(valence=1, arousal=1)
    opposite = score_prediction(-1 + 1e-12, -1 + 1e-12, target)
    assert 0 < opposite.neuro_score < 1e-9
    projected = score_prediction(1 + 1e-12, 1 + 1e-12, target)
    assert projected.projected
    assert projected.point_used == target
    assert score_percentage(projected.neuro_score) == 100
