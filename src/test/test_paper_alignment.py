"""
Smoke tests for paper-aligned changes (arxiv 2506.16448v1).

Run from project root:
    python -m src.test.test_paper_alignment
"""

import torch
import numpy as np


def test_imports():
    from src.models.architectures import MultiScaleEEGCNN, SpatialMLP
    from src.data.preprocessing import temporal_truncation, zscore_normalize, preprocess_eeg_signal, analyze_eeg_bands, analyze_ecg
    from src.data.emotion_engine import process_emotion_engine, calculate_stress_index
    from src.data.data_loader import generate_synthetic_data
    print("[PASS] All imports OK")


def test_cnn_forward():
    from src.models.architectures import MultiScaleEEGCNN
    model = MultiScaleEEGCNN()
    x = torch.randn(2, 3, 500)
    out = model(x)
    assert out.shape == (2, 2), f"Expected (2,2), got {out.shape}"
    print(f"[PASS] CNN forward: {x.shape} -> {out.shape}")


def test_mlp_forward():
    from src.models.architectures import SpatialMLP
    mlp = SpatialMLP()
    x = torch.randn(2, 3)
    out = mlp(x)
    assert out.shape == (2, 2), f"Expected (2,2), got {out.shape}"
    print(f"[PASS] MLP forward: {x.shape} -> {out.shape}")


def test_preprocessing():
    from src.data.preprocessing import temporal_truncation, zscore_normalize, preprocess_eeg_signal
    sig = np.random.randn(1000 * 256)  # Create a signal long enough for 10s truncation
    sig_trunc = temporal_truncation(sig, fs=256, start_sec=10, max_sec=60)
    sig_z = zscore_normalize(sig_trunc)
    sig_full = preprocess_eeg_signal(sig, fs=256)
    assert abs(np.mean(sig_z)) < 0.01, "Z-score mean should be near 0"
    print(f"[PASS] Preprocessing: zscore mean={np.mean(sig_z):.6f}")


def test_band_analysis_has_delta():
    from src.data.preprocessing import analyze_eeg_bands
    sig = np.random.randn(1000)
    bands, f, pxx = analyze_eeg_bands(sig, fs=256)
    for band in ['Delta', 'Theta', 'Alpha', 'Beta', 'Gamma']:
        assert band in bands, f"{band} band missing!"
    print(f"[PASS] Band analysis: {list(bands.keys())}")


def test_emotion_engine():
    from src.data.emotion_engine import process_emotion_engine
    sig = np.random.randn(256 * 60)
    ecg = np.random.randn(256 * 60)
    result = process_emotion_engine(sig, sig, ecg, fs=256)
    assert 'Delta' in result['Bands'], "Delta missing from emotion engine"
    assert len(result['MDS']['Valence_X']) > 0, "No trajectory points"
    print(f"[PASS] Emotion engine: {len(result['Bands'])} bands, {len(result['MDS']['Valence_X'])} points")


def test_synthetic_data():
    from src.data.data_loader import generate_synthetic_data
    X, y, bio = generate_synthetic_data(10)
    assert X.shape == (10, 3)
    assert y.shape == (10, 2)
    assert len(bio) == 10
    print(f"[PASS] Synthetic data: X={X.shape}, y={y.shape}")


if __name__ == "__main__":
    tests = [
        test_imports,
        test_cnn_forward,
        test_mlp_forward,
        test_preprocessing,
        test_band_analysis_has_delta,
        test_emotion_engine,
        test_synthetic_data,
    ]
    passed = 0
    failed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except Exception as e:
            print(f"[FAIL] {t.__name__}: {e}")
            failed += 1

    print(f"\n{'='*40}")
    print(f"Results: {passed} passed, {failed} failed")
    if failed == 0:
        print("ALL TESTS PASSED")
