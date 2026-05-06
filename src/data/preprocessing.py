"""
EEG & ECG Preprocessing Module
Aligned with: arxiv.org/html/2506.16448v1 (Section 3.3.1 Data Preprocess)

Preprocessing Pipeline:
  1. Strict Temporal Truncation — drop first 10s (VR Orienting Reflex), keep up to 60s
  2. Z-Score Normalization  — Z = (x - μ) / σ
  3. Bandpass Filtering  — for ECG artifact removal
  4. Band Power Extraction  — Delta, Theta, Alpha, Beta, Gamma (all 5 bands)
"""
import numpy as np
import scipy.signal


# =============================================================================
# Paper-aligned preprocessing functions (Section 3.3.1)
# =============================================================================

def temporal_truncation(signal_data, fs=256, start_sec=10, max_sec=60):
    """
    Strict temporal truncation:
    Drops the first `start_sec` seconds to eliminate the VR Orienting Reflex artifact.
    Limits processing window to T+10s to T+max_sec.

    Args:
        signal_data: 1D numpy array of samples
        fs: sampling frequency (Hz)
        start_sec: seconds to drop from the beginning
        max_sec: maximum seconds to keep overall
    Returns:
        truncated signal (1D numpy array)
    """
    start_idx = int(start_sec * fs)
    end_idx = int(max_sec * fs)

    if len(signal_data) <= start_idx:
        return np.array([])
        
    return signal_data[start_idx:min(len(signal_data), end_idx)]


def zscore_normalize(signal_data, global_mean=None, global_std=None):
    """
    Z-Score Normalization (Paper §3.3.1, Equation 8):
        Z = (x - μ) / σ

    Ensures signals from different channels/individuals are comparable.
    Helps models converge faster since input features have similar scales.

    Args:
        signal_data: 1D or 2D numpy array of EEG samples
        global_mean: Optional global mean for within-subject normalization
        global_std: Optional global std for within-subject normalization
    Returns:
        Z-score normalized signal
    """
    mean_val = global_mean if global_mean is not None else np.mean(signal_data)
    std_val = global_std if global_std is not None else np.std(signal_data)
    return (signal_data - mean_val) / (std_val + 1e-6)


def preprocess_eeg_signal(signal_data, fs=256, global_mean=None, global_std=None, apply_truncation=True):
    """
    Rewritten EEG Preprocessing Pipeline:
      1. Strict Temporal Truncation (T+10s to T+60s)
      2. Within-Subject Z-Score Normalization

    Args:
        signal_data: 1D numpy array
        fs: sampling frequency
        global_mean: subject-level mean
        global_std: subject-level standard deviation
        apply_truncation: whether to apply temporal truncation (False if already applied)
    Returns:
        preprocessed signal (1D numpy array)
    """
    if apply_truncation:
        signal_trunc = temporal_truncation(signal_data, fs=fs, start_sec=10, max_sec=60)
    else:
        signal_trunc = signal_data

    if len(signal_trunc) == 0:
        return signal_trunc

    signal_norm = zscore_normalize(signal_trunc, global_mean, global_std)
    return signal_norm


# =============================================================================
# Band Power Analysis (Paper §3.3.1 — all 5 standard EEG bands)
# =============================================================================

def analyze_eeg_bands(signal_data, fs=256):
    """
    Extracts power in all 5 EEG frequency bands per the paper:
      Delta (0.5–4 Hz), Theta (4–8 Hz), Alpha (8–13 Hz),
      Beta (13–30 Hz), Gamma (30–45 Hz)

    Also computes key ratios used for emotion indices.

    Returns:
        powers: dict of band powers + ratios
        f: frequency axis from Welch
        Pxx: power spectral density from Welch
    """
    bands = {
        "Delta": (0.5, 4),
        "Theta": (4, 8),
        "Alpha": (8, 13),
        "Beta": (13, 30),
        "Gamma": (30, 100)
    }

    f, Pxx = scipy.signal.welch(signal_data, fs=fs, nperseg=fs * 2)

    powers = {}
    for band, (low, high) in bands.items():
        mask = (f >= low) & (f <= high)
        if np.any(mask):
            powers[band] = np.trapezoid(Pxx[mask], f[mask])
        else:
            powers[band] = 0.0

    # Ratios (used for V/A mapping)
    powers['Beta/Alpha'] = powers['Beta'] / (powers['Alpha'] + 1e-6)
    powers['Theta/Beta'] = powers['Theta'] / (powers['Beta'] + 1e-6)

    return powers, f, Pxx


# =============================================================================
# Bandpass Filter (for ECG / artifact removal)
# =============================================================================

def butter_bandpass(lowcut, highcut, fs, order=4):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = scipy.signal.butter(order, [low, high], btype='band')
    return b, a


def butter_bandpass_filter(data, lowcut, highcut, fs, order=4):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = scipy.signal.filtfilt(b, a, data)
    return y


# =============================================================================
# ECG Analysis
# =============================================================================

def analyze_ecg(signal_data, fs=256, apply_truncation=True):
    """
    Analyzes ECG (Channel 3) for Heart Rate and HRV.
    Includes Bandpass filtering (0.5–40 Hz) to remove motion artifacts.
    """
    # 0. Temporal Truncation (T+10s to T+60s)
    if apply_truncation:
        signal_trunc = temporal_truncation(signal_data, fs=fs, start_sec=10, max_sec=60)
    else:
        signal_trunc = signal_data

    if len(signal_trunc) == 0:
        return {"BPM": 0, "HRV": 0}, [], signal_data

    # 0.5. Validation Check: Ensure exactly 50 seconds
    expected_samples = 50 * fs
    if len(signal_trunc) != expected_samples:
        raise ValueError(f"ECG signal length post-truncation must be exactly 50 seconds ({expected_samples} samples), but got {len(signal_trunc)} samples.")

    # 1. Bandpass Filter (0.5Hz - 40Hz)
    try:
        filtered_signal = butter_bandpass_filter(signal_trunc, 0.5, 40.0, fs, order=4)
        clean_signal = filtered_signal
    except Exception:
        clean_signal = signal_trunc  # Fallback

    # 2. Peak Detection (Z-score normalize for consistent thresholding)
    sig_norm = zscore_normalize(clean_signal)

    # Find R-peaks
    peaks, _ = scipy.signal.find_peaks(sig_norm, height=1.5, distance=fs * 0.4)

    if len(peaks) < 2:
        return {"BPM": 0, "HRV": 0}, peaks, clean_signal

    # Calculate RR intervals in seconds
    rr_intervals = np.diff(peaks) / fs

    bpm = 60 / np.mean(rr_intervals)
    
    # Calculate RMSSD (Root Mean Square of Successive Differences) for Arousal
    if len(rr_intervals) > 1:
        diff_rr = np.diff(rr_intervals)
        hrv = np.sqrt(np.mean(diff_rr**2)) * 1000  # RMSSD in ms
    else:
        hrv = 0.0

    return {"BPM": bpm, "HRV": hrv}, peaks, clean_signal
