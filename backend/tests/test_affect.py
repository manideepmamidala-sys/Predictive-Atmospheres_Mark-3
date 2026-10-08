import pytest

from pa.affect.fusion import construct_affect
from pa.affect.normalization import descriptive_components


def test_descriptive_calibration_does_not_replace_missing_or_constant_components():
    rows = [{"participant_id": "P1", "faa": value, "beta_alpha": value / 2,
             "heart_rate_bpm": 60 + value, "rmssd_ms": 20 + value}
            for value in (1.0, 2.0, 3.0, 4.0)]
    rows[0]["rmssd_ms"] = None
    rows += [{"participant_id": "P2", "faa": 1.0, "beta_alpha": None,
              "heart_rate_bpm": None, "rmssd_ms": None} for _ in range(3)]
    normalized, diagnostic = descriptive_components(rows)
    assert normalized[0]["rmssd_ms"] is None
    assert normalized[3]["faa"] > normalized[1]["faa"]
    assert diagnostic["P1"]["rmssd_ms"]["status"] == "calibrated"
    assert diagnostic["P2"]["faa"]["status"] == "zero_robust_scale"
    assert normalized[4]["faa"] is None


def test_fusion_retains_partial_modalities_and_self_report_only_state():
    full = {"faa": 0.4, "beta_alpha": 0.2, "heart_rate_bpm": 0.3,
            "rmssd_ms": -0.5}
    ratings = {"valence": -0.4, "arousal": 0.2}
    complete = construct_affect(full, ratings)
    assert complete.cohort == "complete_fusion"
    assert complete.objective["arousal"] == pytest.approx((0.2 + 0.3 + 0.5) / 3)
    assert complete.fused["valence"] == pytest.approx(0)
    partial = construct_affect({**full, "rmssd_ms": None}, ratings)
    assert partial.cohort == "partial_modality_fusion"
    assert partial.fused["arousal"] is not None
    assert partial.available_components == ("faa", "beta_alpha", "heart_rate_bpm")
    subjective = construct_affect({}, ratings)
    assert subjective.cohort == "subjective_only"
    assert subjective.fused == {"valence": None, "arousal": None}
    missing = construct_affect({}, {"valence": None, "arousal": None})
    assert missing.cohort == "unavailable"


def test_alpha_sensitivity_is_declared_not_implicitly_adjusted_for_missingness():
    components = {"faa": 0.4, "beta_alpha": None,
                  "heart_rate_bpm": None, "rmssd_ms": None}
    ratings = {"valence": -0.4, "arousal": 0.1}
    objective_only = construct_affect(components, ratings, alpha=1)
    assert objective_only.fused["valence"] == pytest.approx(0.4)
    assert objective_only.fused["arousal"] is None
    with pytest.raises(ValueError):
        construct_affect(components, ratings, alpha=1.1)


def test_affect_detail_keeps_experiment_one_comfort_separate_and_no_ecg_substitute():
    from pa.affect.run import construct_affect_detail
    from pa.io.metadata import Trial

    trials = [Trial(1, "P1", f"R{i}", f"synthetic-{i}.csv", 60, 0.2, None, None,
                    None, "synthetic_test_fixture") for i in range(4)]
    signals = [{"id": f"E1:P1:R{i}", "experiment": 1, "participant_id": "P1",
                "room_id": f"R{i}",
                "eeg": {"valid": True, "forehead_log_alpha_asymmetry": float(i),
                        "log_beta_alpha_ratio": float(i) / 2},
                "ecg": {"valid_hr": False, "valid_rmssd": False,
                        "heart_rate_bpm": None, "rmssd_ms": None}}
               for i in range(4)]
    result = construct_affect_detail(trials, signals)
    assert len(result["trials"]) == 4
    assert result["trials"][0]["comfort"] == 0.2
    assert result["trials"][0]["subjective"] == {"valence": None, "arousal": None}
    assert result["trials"][0]["construction"]["cohort"] == "objective_only"
    assert result["trials"][0]["construction"]["fused"]["valence"] is None
    assert result["trials"][0]["rmssd_ms"] is None
