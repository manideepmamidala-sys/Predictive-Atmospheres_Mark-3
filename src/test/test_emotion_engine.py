import numpy as np
import pytest

from src.data.emotion_engine import process_emotion_engine, _fuse, _compute_faa, _compute_rmssd

def test_process_emotion_engine_valid_arrays():
    """Test that providing valid 50-second EEG/ECG arrays outputs FAA and RMSSD-based values."""
    fs = 256
    num_samples = 50 * fs  # 50 seconds
    
    # Generate mock signals
    signal_right = np.random.randn(num_samples)
    signal_left = np.random.randn(num_samples)
    signal_ecg = np.random.randn(num_samples)
    
    result = process_emotion_engine(signal_right, signal_left, signal_ecg, fs=fs)
    
    # Check output structure
    assert "MDS" in result
    assert "Valence_X" in result["MDS"]
    assert "Arousal_Y" in result["MDS"]
    
    valence = result["MDS"]["Valence_X"][0]
    arousal = result["MDS"]["Arousal_Y"][0]
    
    # Validate types and ranges
    assert isinstance(valence, float)
    assert isinstance(arousal, float)
    assert -1.0 <= valence <= 1.0
    assert -1.0 <= arousal <= 1.0

    # Also test the sub-functions directly
    faa = _compute_faa(signal_right, signal_left, fs=fs)
    rmssd = _compute_rmssd(signal_ecg, fs=fs)
    
    assert isinstance(faa, float)
    assert isinstance(rmssd, float)
    assert rmssd >= 0.0


def test_affective_fusion_calculation():
    """Test the Affective Fusion calculation formula.
    Ensure Target = (alpha * Objective) + ((1 - alpha) * Subjective) computes accurately.
    """
    alpha = 0.6
    obj_valence = 0.5
    obj_arousal = -0.2
    subj_valence = 0.8
    subj_arousal = 0.4
    
    result = _fuse(
        obj_valence=obj_valence,
        obj_arousal=obj_arousal,
        subj_valence=subj_valence,
        subj_arousal=subj_arousal,
        alpha=alpha
    )
    
    # Hand-calculate expected values
    expected_valence = alpha * obj_valence + (1.0 - alpha) * subj_valence
    expected_arousal = alpha * obj_arousal + (1.0 - alpha) * subj_arousal
    
    assert pytest.approx(result["fused_valence"]) == expected_valence
    assert pytest.approx(result["fused_arousal"]) == expected_arousal
    assert pytest.approx(result["objective_valence"]) == obj_valence
    assert pytest.approx(result["objective_arousal"]) == obj_arousal
    assert pytest.approx(result["subjective_valence"]) == subj_valence
    assert pytest.approx(result["subjective_arousal"]) == subj_arousal
    assert result["alpha_used"] == alpha


def test_process_emotion_engine_nan_input_raises():
    """Test that inputting arrays containing NaN correctly raises a ValueError."""
    fs = 256
    num_samples = 50 * fs
    
    signal_right = np.random.randn(num_samples)
    signal_left = np.random.randn(num_samples)
    signal_ecg = np.random.randn(num_samples)
    
    # Inject NaN
    signal_right[100] = np.nan
    
    with pytest.raises(ValueError, match="contain NaN"):
        process_emotion_engine(signal_right, signal_left, signal_ecg, fs=fs)


def test_process_emotion_engine_short_signal_raises():
    """Test that inputting arrays shorter than 50 seconds correctly raises a ValueError."""
    fs = 256
    num_samples = 49 * fs  # 49 seconds (shorter than expected)
    
    signal_right = np.random.randn(num_samples)
    signal_left = np.random.randn(num_samples)
    signal_ecg = np.random.randn(num_samples)
    
    with pytest.raises(ValueError, match="at least"):
        process_emotion_engine(signal_right, signal_left, signal_ecg, fs=fs)
