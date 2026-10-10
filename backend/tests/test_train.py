import numpy as np
import pandas as pd

from pa.features.schema import RoomInput
from pa.modeling.predict import feature_frame
from pa.modeling.train import Cohort, evaluate_and_fit


def test_sparse_grouping_uses_recorded_baseline_fallback_and_reloadable_artifact(tmp_path):
    from pa.modeling.artifact import load_artifact

    n = 9
    rooms = [RoomInput(length=4 + i * 0.1, width=3, height=3, num_doors=1,
                       door_area=1.5, num_windows=1, window_area=2,
                       daylight_factor=2, illuminance=300 + i * 10, cct=5000,
                       walkable_floor_area=8, day_or_night="Day", space_type="Bedroom")
             for i in range(n)]
    raw = pd.DataFrame({"faa": np.arange(n) * 0.1,
                        "alpha_suppression": np.arange(n) * 0.2,
                        "engagement": np.arange(n) * 0.3,
                        "heart_rate_bpm": 60 + np.arange(n) * 2})
    cohort = Cohort(tuple(f"T{i}" for i in range(n)), feature_frame(rooms), raw,
                    np.column_stack((np.linspace(-0.5, 0.5, n), np.linspace(0.5, -0.5, n))),
                    np.array([f"R{i // 3}" for i in range(n)]),
                    np.array([f"P{i // 3}" for i in range(n)]), {})
    result = evaluate_and_fit(cohort, tmp_path)
    assert result["status"] == "baseline_only"
    assert result["final_selection"]["status"] == "fixed_baseline_insufficient_groups"
    assert result["evaluation"]["room"]["aggregate"]["evaluated_folds"] == 3
    for fold in result["evaluation"]["room"]["folds"]:
        assert fold["status"] == "evaluated"
        assert fold["baseline_mean_mae"] is not None
        assert fold["baseline_median_mae"] is not None
    loaded = load_artifact(tmp_path)
    assert loaded.metadata["model_status"] == "baseline_only"
    assert loaded.pipeline.predict(cohort.X.iloc[:1]).shape == (1, 2)


def test_singular_room_design_keeps_grouped_selection_finite():
    from pa.modeling.evaluate import select_candidate

    n = 12
    room = RoomInput(length=4, width=3, height=3, num_doors=1, door_area=1.5,
                     num_windows=1, window_area=2, daylight_factor=2,
                     illuminance=300, cct=5000, walkable_floor_area=8,
                     day_or_night="Day", space_type="Bedroom")
    X = feature_frame([room] * n)
    index = np.arange(n, dtype=float)
    raw = pd.DataFrame({"faa": index * 0.1,
                        "alpha_suppression": index * 0.2,
                        "engagement": index * 0.3,
                        "heart_rate_bpm": 60 + index * 2})
    reports = np.column_stack((np.linspace(-0.5, 0.5, n),
                               np.linspace(0.5, -0.5, n)))
    groups = np.array([f"R{i // 3}" for i in range(n)])
    result = select_candidate(X, raw, reports, groups)
    assert result.status == "selected"
    assert all(np.isfinite(value) for value in result.scores.values())
    assert X.nunique(dropna=False).max() == 1
