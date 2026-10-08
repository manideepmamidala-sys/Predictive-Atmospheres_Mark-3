import numpy as np

from pa.io.audit import counter_discontinuities, duration_assessment


def test_counter_wrap_is_normal_but_jump_is_flagged():
    assert counter_discontinuities(np.array([254, 255, 0, 1])) == []
    assert counter_discontinuities(np.array([254, 255, 2, 3])) == [2]


def test_rate_duration_conflict_is_a_scenario_not_a_hardware_claim():
    matched = duration_assessment(30_000, 60, 500)
    conflicting = duration_assessment(30_000, 60, 250)
    assert matched["sample_duration_s"] == 60
    assert conflicting["sample_duration_s"] == 120
    assert conflicting["duration_disagreement"]


def test_duration_flag_uses_versioned_setting(monkeypatch):
    monkeypatch.setattr("pa.io.audit.decisions", lambda: {"rate": {
        "duration_disagreement_fraction": 0.25}})
    assert not duration_assessment(54_000, 100, 500)["duration_disagreement"]
    assert duration_assessment(30_000, 100, 500)["duration_disagreement"]
