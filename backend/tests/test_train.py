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
                        "beta_alpha": np.arange(n) * 0.2,
                        "heart_rate_bpm": 60 + np.arange(n) * 2,
                        "rmssd_ms": 20 + np.arange(n) * 3})
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
