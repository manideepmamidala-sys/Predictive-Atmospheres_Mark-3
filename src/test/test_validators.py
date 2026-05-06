import numpy as np
import pytest

from src.core.data.validators import RoomDimensions, EEGSignal


def test_room_dimensions_valid():
    room = RoomDimensions(length=10.0, width=8.0, height=3.5)
    assert room.length == 10.0


def test_room_dimensions_invalid_height():
    with pytest.raises(Exception):
        RoomDimensions(length=10.0, width=8.0, height=2.0)


def test_eeg_signal_valid_1d():
    sig = EEGSignal(data=np.random.randn(256 * 5), sample_rate=256, channels=1, duration_sec=5.0)
    assert sig.sample_rate == 256


def test_eeg_signal_invalid_all_nan():
    with pytest.raises(ValueError, match="no finite values"):
        EEGSignal(data=np.full(128, np.nan), sample_rate=256, channels=1, duration_sec=1.0)
