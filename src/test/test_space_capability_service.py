import numpy as np

from src.services.space_capability_service import SpaceCapabilityService


def test_feature_vector_shape_and_values():
    vec = SpaceCapabilityService._feature_vector(length=10.0, width=8.0, height=3.5)

    assert vec.shape == (1, 11)
    assert np.isclose(vec[0, 0], 10.0)
    assert np.isclose(vec[0, 1], 8.0)
    assert np.isclose(vec[0, 2], 3.5)
    assert np.isclose(vec[0, 3], 80.0)  # area
    assert np.isclose(vec[0, 4], 280.0)  # volume
