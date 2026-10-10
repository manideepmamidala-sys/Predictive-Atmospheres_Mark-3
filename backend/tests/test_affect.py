import pytest

from pa.affect.fusion import construct_affect
from pa.affect.normalization import descriptive_components


def test_descriptive_calibration_is_within_person_and_experiment():
    rows = [
        {"experiment": experiment, "participant_id": "P1", "faa": value,
         "alpha_suppression": value / 2, "engagement": -value,
         "heart_rate_bpm": 60 + value, "rmssd_ms": 20 + value}
        for experiment, values in ((2, (1, 2, 3, 4)), (3, (101, 102, 103, 104)))
        for value in values
    ]
    rows[0]["rmssd_ms"] = None
    rows += [{"experiment": 2, "participant_id": "P2", "faa": 1.0,
              "alpha_suppression": None, "engagement": None,
              "heart_rate_bpm": None, "rmssd_ms": None} for _ in range(3)]
    normalized, diagnostic = descriptive_components(rows)
    assert normalized[0]["rmssd_ms"] is None
    assert normalized[3]["faa"] > normalized[1]["faa"]
    assert normalized[4]["faa"] < normalized[7]["faa"]
    assert diagnostic["E2:P1"]["rmssd_ms"]["status"] == "calibrated"
    assert diagnostic["E2:P2"]["faa"]["status"] == "zero_robust_scale"
    assert normalized[8]["faa"] is None


def test_descriptive_calibration_accepts_three_distinct_trials_with_two_values():
    values = [0.0, 0.0, 1.0, 1.0]
    rows = [{"experiment": 3, "participant_id": "P", "faa": value,
             "alpha_suppression": None, "engagement": None,
             "heart_rate_bpm": None, "rmssd_ms": None} for value in values]
    transformed, diagnostic = descriptive_components(rows)
    assert diagnostic["E3:P"]["faa"]["status"] == "calibrated"
    assert diagnostic["E3:P"]["faa"]["scale"] == pytest.approx(0.7413)
    assert transformed[0]["faa"] < 0 < transformed[-1]["faa"]


def test_fusion_uses_both_eeg_candidates_and_hr_not_rmssd():
    full = {"faa": 0.4, "alpha_suppression": 0.2, "engagement": 0.6,
            "heart_rate_bpm": 0.3, "rmssd_ms": -0.5}
    ratings = {"valence": -0.4, "arousal": 0.2}
    complete = construct_affect(full, ratings)
    assert complete.cohort == "complete_fusion"
    assert complete.eeg_arousal == pytest.approx(0.4)
    assert complete.objective["arousal"] == pytest.approx(0.35)
    assert complete.fused["valence"] == pytest.approx(0)
    without_rmssd = construct_affect({**full, "rmssd_ms": None}, ratings)
    assert without_rmssd.cohort == "complete_fusion"
    without_hr = construct_affect({**full, "heart_rate_bpm": None}, ratings)
    assert without_hr.cohort == "partial_modality_fusion"
    assert without_hr.physiology_scope == "partial_EEG"
    single_eeg = construct_affect({**full, "engagement": None}, ratings)
    assert single_eeg.eeg_arousal is None
    assert single_eeg.eeg_arousal_scope == "alpha_suppression_only"
    assert single_eeg.physiology_scope == "partial_HR"


def test_component_and_rating_only_states_do_not_become_complete():
    ratings = {"valence": -0.4, "arousal": 0.1}
    components = {"faa": 0.4, "alpha_suppression": None,
                  "engagement": None, "heart_rate_bpm": None, "rmssd_ms": None}
    partial = construct_affect(components, ratings, alpha=1)
    assert partial.fused["valence"] == pytest.approx(0.4)
    assert partial.fused["arousal"] is None
    with pytest.raises(ValueError):
        construct_affect(components, ratings, alpha=1.1)
    subjective = construct_affect({}, ratings)
    assert subjective.cohort == "subjective_only"
    assert subjective.fused == {"valence": None, "arousal": None}
    missing = construct_affect({}, {"valence": None, "arousal": None})
    assert missing.cohort == "unavailable"
