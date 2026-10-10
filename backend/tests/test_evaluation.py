import numpy as np
import pandas as pd
import pytest

from pa.modeling.splits import (
    candidate_key,
    candidate_specs,
    choose_candidate,
    inner_splits,
    outer_splits,
)
from pa.modeling.targets import CalibrationUnavailable, PopulationCalibrator


def components(n=16):
    i = np.arange(n, dtype=float)
    return pd.DataFrame({"faa": np.sin(i), "alpha_suppression": np.cos(i),
                         "engagement": np.sin(i / 3), "heart_rate_bpm": 60 + i})


def test_training_only_calibration_ignores_held_out_mutations():
    raw = components()
    training = raw.iloc[:12]
    first = PopulationCalibrator.fit(training)
    changed = raw.copy()
    changed.loc[12:, "faa"] += 1000
    changed.loc[12:, "engagement"] *= 10
    second = PopulationCalibrator.fit(changed.iloc[:12])
    assert first == second
    report = np.stack((np.linspace(-0.5, 0.5, 16), np.zeros(16)), axis=1)
    assert not np.allclose(first.fused(raw.iloc[12:], report[12:]),
                           second.fused(changed.iloc[12:], report[12:]))


def test_uncalibratable_training_component_is_unavailable():
    raw = components()
    raw["faa"] = 0
    with pytest.raises(CalibrationUnavailable, match="faa"):
        PopulationCalibrator.fit(raw)


@pytest.mark.parametrize("component", ("faa", "alpha_suppression", "engagement", "heart_rate_bpm"))
@pytest.mark.parametrize("invalid", (float("inf"), float("-inf")))
def test_nonfinite_heldout_raw_component_cannot_saturate_into_valid_target(component, invalid):
    raw = components()
    calibration = PopulationCalibrator.fit(raw.iloc[:12])
    heldout = raw.iloc[12:13].copy()
    heldout.loc[12, component] = invalid
    with pytest.raises(CalibrationUnavailable, match="nonfinite component"):
        calibration.fused(heldout, np.zeros((1, 2)))


def test_room_and_subject_groups_never_cross_fold_and_ties_are_stable():
    room = np.array([f"R{i//2}" for i in range(12)])
    person = np.array([f"P{i//3}" for i in range(12)])
    for labels in (room, person):
        for train, test in outer_splits(labels):
            assert set(labels[train]).isdisjoint(labels[test])
            for inner_train, inner_test in inner_splits(labels[train]):
                assert set(labels[train][inner_train]).isdisjoint(labels[train][inner_test])
    specs = candidate_specs()
    scores = {candidate_key(spec): 0.2 for spec in specs}
    assert choose_candidate(scores) == candidate_key(specs[0])
    scores[candidate_key(specs[-1])] = 0.19
    assert choose_candidate(scores) == candidate_key(specs[-1])
    chained = {candidate_key(spec): float("inf") for spec in specs}
    chained[candidate_key(specs[0])] = 0.2
    chained[candidate_key(specs[1])] = 0.1999995
    chained[candidate_key(specs[2])] = 0.1999988
    assert choose_candidate(chained) == candidate_key(specs[1])


def test_nested_selection_refits_calibration_and_excludes_outer_heldout():
    from pa.features.schema import RoomInput
    from pa.modeling.evaluate import evaluate_outer, select_candidate
    from pa.modeling.predict import feature_frame

    n = 20
    raw = components(n)
    reports = np.stack((np.sin(np.arange(n)) * 0.3, np.cos(np.arange(n)) * 0.2), axis=1)
    rooms = [RoomInput(length=4 + i / 10, width=3 + i / 20, height=3,
                       num_doors=1, door_area=1.5, num_windows=1, window_area=2,
                       daylight_factor=2, illuminance=300 + i, cct=5000,
                       walkable_floor_area=8, day_or_night="Day", space_type="Bedroom")
             for i in range(n)]
    X = feature_frame(rooms)
    groups = np.array([f"R{i//4}" for i in range(n)])
    outer_train, outer_test = outer_splits(groups)[0]
    selected = select_candidate(X.iloc[outer_train], raw.iloc[outer_train],
                                reports[outer_train], groups[outer_train])
    assert selected.status == "selected"
    for fold in selected.inner_fold_calibrations:
        assert set(fold["training_indices"]).isdisjoint(fold["validation_indices"])
    held_inner = selected.inner_fold_calibrations[0]
    inner_validation_global = outer_train[held_inner["validation_indices"]]
    changed_inner_raw = raw.copy()
    changed_inner_raw.loc[inner_validation_global, "faa"] += 1_000
    changed_inner_raw.loc[inner_validation_global, "engagement"] *= 10
    changed_inner_reports = reports.copy()
    changed_inner_reports[inner_validation_global] = [-1, 1]
    changed_inner_X = X.copy()
    changed_inner_X.loc[inner_validation_global, "length"] = 50
    changed_inner = select_candidate(changed_inner_X.iloc[outer_train],
                                     changed_inner_raw.iloc[outer_train],
                                     changed_inner_reports[outer_train], groups[outer_train])
    assert changed_inner.inner_fold_calibrations[0] == held_inner
    changed_raw = raw.copy()
    changed_raw.loc[outer_test, "faa"] = 1_000
    changed_report = reports.copy()
    changed_report[outer_test] = [-1, 1]
    changed_X = X.copy()
    changed_X.loc[outer_test, "length"] = 50
    selected_after = select_candidate(changed_X.iloc[outer_train], changed_raw.iloc[outer_train],
                                      changed_report[outer_train], groups[outer_train])
    assert selected == selected_after
    first = evaluate_outer(X, raw, reports, groups)[0]
    second = evaluate_outer(changed_X, changed_raw, changed_report, groups)[0]
    assert first["selection"] == second["selection"]
    assert first["train_indices"] == second["train_indices"]


def test_spatial_null_shuffles_whole_training_room_rows_and_keeps_test_untouched():
    from pa.modeling.evaluate import _permuted_training_rooms

    groups = np.array(["R1", "R1", "R2", "R2", "R3", "R3", "R4", "R4"])
    X = pd.DataFrame({"length": [1, 1, 2, 2, 3, 3, 4, 4],
                      "space_type": ["A", "A", "B", "B", "C", "C", "D", "D"]})
    first = _permuted_training_rooms(X, groups, np.random.default_rng(2718))
    assert len(first.drop_duplicates()) == 4
    assert sorted(first["length"].tolist()) == sorted(X["length"].tolist())
    assert first.groupby(groups).nunique().max().max() == 1
    assert X["length"].tolist() == [1, 1, 2, 2, 3, 3, 4, 4]
