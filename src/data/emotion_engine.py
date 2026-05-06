"""
EEG Emotion Engine
Aligned with: arxiv.org/html/2506.16448v1

Pipeline:
  1. Preprocessing (baseline removal + Z-score normalization)
  2. Sliding-window PSD analysis (Welch's method)
  3. Valence/Arousal computation via band-power ratios + sigmoid mapping
  4. Probabilistic emotion distribution using inverse-distance weighting
     on Russell's circumplex model (13 emotion centroids)
"""
import numpy as np
import scipy.signal
from typing import Any, Dict
from src.data.preprocessing import temporal_truncation, zscore_normalize, analyze_ecg
from src.config import get_config


def _validate_signal(signal_data: np.ndarray, fs: int) -> np.ndarray:
    """Validate and sanitize a 1D EEG signal."""
    signal = np.asarray(signal_data, dtype=np.float64)

    if signal.ndim != 1:
        raise ValueError(f"Expected 1D signal array, got shape {signal.shape}")
    if fs <= 0:
        raise ValueError(f"Sampling rate must be positive, got {fs}")
    if signal.size < fs:
        raise ValueError(f"Signal too short: {signal.size} samples, expected at least {fs}")
    if not np.any(np.isfinite(signal)):
        raise ValueError("Signal contains no finite values")

    signal = np.nan_to_num(signal, nan=0.0, posinf=0.0, neginf=0.0)
    if np.allclose(signal, 0.0):
        raise ValueError("Signal is degenerate (all zeros after sanitization)")

    return signal


def process_emotion_engine(
    signal_right: np.ndarray, 
    signal_left: np.ndarray, 
    signal_ecg: np.ndarray,
    fs: int = 256,
    global_mean_r: float = None, global_std_r: float = None,
    global_mean_l: float = None, global_std_l: float = None,
    apply_truncation: bool = True
) -> Dict[str, Dict[str, Any]]:
    """
    Full Multi-Modal Emotion pipeline.
    Computes Valence via FAA (Frontal Alpha Asymmetry): ln(Alpha_R) - ln(Alpha_L).
    Computes Arousal via ECG RMSSD.

    Part 1: Preprocessing (Paper §3.3.1)
        - Baseline Removal
        - Z-Score Normalization (with optional subject-level mean/std)
    Part 2: Sliding Window PSD → Band Powers
    Part 3: V/A Mapping → Emotion Distribution

    Returns dict with keys:
        'Bands': final window band powers (average of right and left)
        'Emotion_Distribution': probability per emotion (%)
        'MDS': {'Valence_X': [...], 'Arousal_Y': [...]}  trajectory
    """
    sig_r = _validate_signal(signal_right, fs)
    sig_l = _validate_signal(signal_left, fs)
    sig_ecg = _validate_signal(signal_ecg, fs)

    # --- Part 1: Preprocessing (Paper §3.3.1) ---
    if apply_truncation:
        sig_r_trunc = temporal_truncation(sig_r, fs=fs, start_sec=10, max_sec=60)
        sig_l_trunc = temporal_truncation(sig_l, fs=fs, start_sec=10, max_sec=60)
        sig_ecg_trunc = temporal_truncation(sig_ecg, fs=fs, start_sec=10, max_sec=60)
    else:
        sig_r_trunc = sig_r
        sig_l_trunc = sig_l
        sig_ecg_trunc = sig_ecg

    if len(sig_r_trunc) == 0:
        raise ValueError("Right signal is too short after temporal truncation")
    sig_r_norm = zscore_normalize(sig_r_trunc, global_mean_r, global_std_r)
    sig_r_norm = np.nan_to_num(sig_r_norm, nan=0.0, posinf=0.0, neginf=0.0)

    if len(sig_l_trunc) == 0:
        raise ValueError("Left signal is too short after temporal truncation")
    sig_l_norm = zscore_normalize(sig_l_trunc, global_mean_l, global_std_l)
    sig_l_norm = np.nan_to_num(sig_l_norm, nan=0.0, posinf=0.0, neginf=0.0)

    # --- Part 1.5: Global ECG Arousal Calculation ---
    ecg_metrics, _, _ = analyze_ecg(sig_ecg_trunc, fs=fs, apply_truncation=False)
    rmssd = float(ecg_metrics['HRV'])
    
    # Map RMSSD to [-1, 1] linearly. Assuming ~50ms is baseline (0 arousal).
    # Higher HRV = Parasympathetic dominance = Lower Arousal.
    # Formula: Arousal = 1.0 - (RMSSD / 50.0). Capped at [-1, 1].
    global_arousal = float(np.clip(1.0 - (rmssd / 50.0), -1.0, 1.0))

    # --- Part 2: Sliding Window PSD Trajectories (Valence) ---
    window_size = fs
    step_size = max(fs // 2, 1)

    if len(sig_r_norm) < window_size:
        sig_r_norm = np.pad(sig_r_norm, (0, window_size - len(sig_r_norm)))
        sig_l_norm = np.pad(sig_l_norm, (0, window_size - len(sig_l_norm)))

    num_windows = max((len(sig_r_norm) - window_size) // step_size + 1, 1)

    mds_x_list = []
    mds_y_list = []
    final_band_powers = None

    bands_def = {
        'Delta': (0.5, 4), 'Theta': (4, 8), 'Alpha': (8, 13),
        'Beta': (13, 30), 'Gamma': (30, 100)
    }

    for i in range(num_windows):
        start_idx = i * step_size
        end_idx = start_idx + window_size
        chunk_r = sig_r_norm[start_idx:end_idx]
        chunk_l = sig_l_norm[start_idx:end_idx]

        f_r, Pxx_r = scipy.signal.welch(chunk_r, fs=fs, nperseg=max(len(chunk_r) // 2, 8))
        f_l, Pxx_l = scipy.signal.welch(chunk_l, fs=fs, nperseg=max(len(chunk_l) // 2, 8))

        band_powers_r = {}
        band_powers_l = {}
        for band, (low, high) in bands_def.items():
            mask_r = (f_r >= low) & (f_r <= high)
            power_r = np.trapezoid(Pxx_r[mask_r], f_r[mask_r]) if np.any(mask_r) else 0.0
            band_powers_r[band] = float(np.nan_to_num(power_r, nan=0.0, posinf=0.0, neginf=0.0))

            mask_l = (f_l >= low) & (f_l <= high)
            power_l = np.trapezoid(Pxx_l[mask_l], f_l[mask_l]) if np.any(mask_l) else 0.0
            band_powers_l[band] = float(np.nan_to_num(power_l, nan=0.0, posinf=0.0, neginf=0.0))

        alpha_r = max(band_powers_r['Alpha'], 1e-6)
        alpha_l = max(band_powers_l['Alpha'], 1e-6)

        # FAA for Valence: ln(Alpha_Right) - ln(Alpha_Left)
        faa = np.log(alpha_r) - np.log(alpha_l)
        
        mds_x = float(np.clip(faa, -1.0, 1.0))
        mds_y = global_arousal  # Global arousal from ECG

        mds_x_list.append(mds_x)
        mds_y_list.append(mds_y)
        final_band_powers = {k: (band_powers_r[k] + band_powers_l[k])/2 for k in bands_def.keys()}

    if final_band_powers is None:
        raise RuntimeError("Band power computation failed")

    # --- Part 3: Probabilistic Emotion Distribution ---
    centroids = get_config().emotion.centroids
    decay = get_config().emotion.distance_decay

    avg_mds_x = float(np.mean(mds_x_list))
    avg_mds_y = float(np.mean(mds_y_list))

    raw_weights = {}
    for emotion, coords in centroids.items():
        dist = np.sqrt((avg_mds_x - coords[0]) ** 2 + (avg_mds_y - coords[1]) ** 2)
        raw_weights[emotion] = float(np.exp(-dist * decay))

    total_weight = sum(raw_weights.values())
    emotion_distribution = {
        k: (w / total_weight) * 100.0 if total_weight > 0 else 100.0 / 13.0
        for k, w in raw_weights.items()
    }

    if not np.isfinite(sum(emotion_distribution.values())):
        raise RuntimeError("Emotion distribution contains non-finite values")

    return {
        'Bands': {k: [v] for k, v in final_band_powers.items()},
        'Emotion_Distribution': {k: [v] for k, v in emotion_distribution.items()},
        'MDS': {'Valence_X': mds_x_list, 'Arousal_Y': mds_y_list}
    }


def calculate_stress_index(beta, alpha):
    """
    Beta/Alpha Stress Index with sigmoid normalization.
    Returns a probability of stress (0.0 to 1.0).
    """
    ratio = beta / (alpha + 1e-6)
    stress = 1 / (1 + np.exp(-(ratio - 1.0) * 3))
    return stress
