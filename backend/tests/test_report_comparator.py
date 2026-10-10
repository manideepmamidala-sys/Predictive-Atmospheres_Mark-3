"""Research-only self-report comparison remains separate by source experiment."""

import json

import pytest

from pa.config import RESULTS
from pa.io.metadata import load_rooms
from pa.modeling.report_comparator import build_report_cohort


def test_e2_drops_structurally_unrecorded_inputs_and_e3_keeps_full_schema():
    source = json.loads((RESULTS / "affect_detail.json").read_text())
    spatial = load_rooms()
    e2 = build_report_cohort(source, spatial, 2)
    e3 = build_report_cohort(source, spatial, 3)
    assert len(e2[0]) == 50 and len(e3[0]) == 60
    assert "walkable_floor_area" not in e2[5]
    assert "walkable_floor_ratio" not in e2[5]
    assert "space_type" not in e2[5]
    assert {"walkable_floor_area", "walkable_floor_ratio", "space_type"} <= set(e3[5])
    assert set(e2[0]).isdisjoint(e3[0])


def test_report_comparator_rejects_a_pooled_or_unsupported_experiment_scope():
    source = json.loads((RESULTS / "affect_detail.json").read_text())
    with pytest.raises(ValueError, match="E2/E3 separate-first"):
        build_report_cohort(source, load_rooms(), 0)


def test_saved_report_comparator_has_group_isolated_fold_memberships_and_predictions():
    result = json.loads((RESULTS / "self_report_comparator.json").read_text())
    assert result["pooling"] == "not_performed_different_elicitation"
    for item in result["experiments"]:
        assert item["status"] == "evaluated"
        for question in ("room", "subject"):
            folds = item["evaluation"][question]["folds"]
            assert len(folds) == item["rooms" if question == "room" else "participants"]
            for fold in folds:
                assert set(fold["train_indices"]).isdisjoint(fold["test_indices"])
                assert len(fold["prediction"]) == len(fold["observed"]) == len(fold["test_indices"])
                assert len(fold["baseline_predictions"]["dummy_median"]) == len(fold["test_indices"])
                assert len(fold["baseline_predictions"]["dummy_mean"]) == len(fold["test_indices"])
