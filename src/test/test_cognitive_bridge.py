import json
import numpy as np
import pytest

from src.models.cognitive_bridge import CognitiveBridge


def test_bridge_loads_default_13_category_coordinates():
    bridge = CognitiveBridge()
    assert len(bridge.mds_coords) == 13
    for category in bridge.categories:
        coords = np.asarray(bridge.mds_coords[category])
        assert coords.shape == (2,)
        assert np.all(np.isfinite(coords))
        assert np.all(coords >= -1.0)
        assert np.all(coords <= 1.0)


def test_bridge_trajectory_output_shape_for_vector_input():
    bridge = CognitiveBridge()
    probs = np.full((13,), 1.0 / 13.0, dtype=np.float64)

    out = bridge.eeg_to_trajectory(probs)
    assert out.shape == (1, 2)


def test_bridge_rejects_out_of_bounds_coordinates(tmp_path):
    bad_file = tmp_path / "bad_coords.json"
    data = {
        "amusing": [2.0, 0.0],
        "angry": [-0.7, 0.7],
        "anxious": [-0.5, 0.8],
        "awful": [-0.8, 0.5],
        "boring": [-0.4, -0.6],
        "calm": [0.7, -0.7],
        "disgusting": [-0.7, 0.3],
        "exciting": [0.8, 0.8],
        "happy": [0.9, 0.4],
        "interesting": [0.4, 0.3],
        "pleasant": [0.8, -0.1],
        "sad": [-0.7, -0.4],
        "scary": [-0.6, 0.7]
    }
    bad_file.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(ValueError, match="out of bounds"):
        CognitiveBridge(mds_path=str(bad_file))
