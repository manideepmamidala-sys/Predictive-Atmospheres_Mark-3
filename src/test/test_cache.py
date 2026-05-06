import os

from src.data.data_loader import load_data, DATA_DIR


def test_load_data_returns_expected_shapes():
    X, y, bio = load_data(force_reload=True)

    assert X.ndim == 2
    assert y.ndim == 2
    assert X.shape[1] == 3
    assert y.shape[1] == 2
    assert len(bio) == len(X)


def test_load_data_uses_cached_result_when_available():
    cache_file = os.path.join(DATA_DIR, 'processed', 'cached_data.pt')
    load_data(force_reload=True)

    assert os.path.exists(cache_file)

    X1, y1, _ = load_data(force_reload=False)
    X2, y2, _ = load_data(force_reload=False)

    assert X1.shape == X2.shape
    assert y1.shape == y2.shape
