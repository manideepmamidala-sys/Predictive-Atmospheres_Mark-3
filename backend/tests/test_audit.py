import numpy as np

from pa.io.audit import counter_discontinuities, duration_assessment, write_timebase


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


def test_timebase_exports_conditional_scenarios_and_onset_without_clock_claim(tmp_path,
                                                                               monkeypatch):
    settings = {"version": "1.2.0", "approved_spec_sha256": "a" * 64,
                "rate": {"primary_hz": 500, "primary_status": "conditional_unconfirmed",
                         "onset_exclusion_primary_s": 0, "onset_exclusion_sensitivity_s": 5}}
    monkeypatch.setattr("pa.io.audit.decisions", lambda: settings)
    monkeypatch.setattr("pa.io.audit.require_science_checkpoint", lambda **_: None)
    audit = {"provenance": {"rate_evidence": ["no hardware timestamp"]}, "files": [{
        "experiment": 2, "subject_id": "P1", "room_id": "R1", "source_file": "raw.csv",
        "samples": 30_000, "logged_duration_s": 50,
        "samples_per_logged_second": 600, "counter_discontinuity_count": 1,
        "counter_discontinuity_indices": [100],
        "rate_scenarios": [duration_assessment(30_000, 50, 500, 0.1),
                           duration_assessment(30_000, 50, 250, 0.1)],
    }]}
    product = write_timebase(audit, tmp_path / "timebase.json")
    assert product["trials"][0]["duration_mismatch_over_10pct"]
    assert product["trials"][0]["onset"] == {
        "primary_excluded_s": 0, "sensitivity_excluded_s": 5,
        "event_marker_available": False,
    }
    assert product["summary"]["counter_flagged"] == 1
    assert product["approved_spec_sha256"] == "a" * 64
