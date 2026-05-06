import numpy as np
import pytest

from src.data.emotion_engine import process_emotion_engine

def test_process_emotion_engine_basic():
    signal = np.random.randn(256 * 60)
    ecg = np.random.randn(256 * 60)
    result = process_emotion_engine(signal, signal, ecg, fs=256)

    assert 'Bands' in result
    assert 'Emotion_Distribution' in result
    assert 'MDS' in result

    assert len(result['Bands']) == 5
    assert len(result['Emotion_Distribution']) == 13


def test_process_emotion_engine_nan_input_raises():
    signal = np.array([np.nan, np.nan])
    with pytest.raises(ValueError):
        process_emotion_engine(signal, signal, signal)


def test_process_emotion_engine_short_signal_raises():
    signal = np.array([1.0, 2.0, 3.0]) # too short for fs=256
    with pytest.raises(ValueError):
        process_emotion_engine(signal, signal, signal, fs=256)


def test_emotion_distribution_sums_to_100():
    signal = np.random.randn(256 * 60)
    ecg = np.random.randn(256 * 60)
    result = process_emotion_engine(signal, signal, ecg)

    total = sum(v[0] for v in result['Emotion_Distribution'].values())
    assert 99 < total < 101
