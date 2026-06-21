"""
Emotion Engine — Phase 2: Affective Fusion Target Calculation
Source of Truth: instructions/01_backend_data_pipeline.md §3–4
                 instructions/03_execution_roadmap.md Phase 2

Pipeline per trial:
  1. Load raw EEG/ECG CSV → truncate to T+10s–T+60s window (drops orienting reflex)
  2. Compute FAA (Frontal Alpha Asymmetry) → Objective Valence
  3. Compute RMSSD from R-peak intervals → Objective Arousal (mapped to [-1,1])
  4. Apply Multimodal Affective Fusion with α=0.6 (fallback α=1.0 when
     Subjective scores are NaN — e.g. Experiment 01)
  5. Calculate Euclidean distance (Δ) between Objective and Subjective coords
  6. Save full fused DataFrame to data/processed/fusion_analysis.parquet

No Streamlit, Rhino, C#, API, ONNX, or PostgreSQL dependencies.
"""

import logging
import os
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

import numpy as np
import pandas as pd
import scipy.signal
from src.config import get_config

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
FS: int = 256                    # EEG/ECG sampling rate (Hz)
WINDOW_50S: int = FS * 50        # 50-second analysis window length (samples); applied T+10s to T+60s

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_RAW_DIR = _PROJECT_ROOT / "data" / "raw"
_PROCESSED_DIR = _PROJECT_ROOT / "data" / "processed"

# ---------------------------------------------------------------------------
# EEG/ECG Signal Utilities
# ---------------------------------------------------------------------------

def _load_eeg_csv(path: Path) -> Optional[pd.DataFrame]:
    """Load a raw EEG/ECG CSV file. Returns None on failure."""
    try:
        df = pd.read_csv(path)
        # Flatten MultiIndex headers if present
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [" ".join(c).strip() for c in df.columns]
        df.columns = [c.strip() for c in df.columns]
        return df
    except Exception as exc:
        logger.error("Failed to load EEG file %s: %s", path, exc)
        return None


def _truncate_50s(signal: np.ndarray, fs: int = FS) -> np.ndarray:
    """
    50-second analysis window: T+10s to T+60s.

    The first 10 seconds are discarded to exclude the VR orienting reflex
    (initial novelty response that contaminates baseline affective state).
    This matches the temporal_truncation() window in preprocessing.py,
    ensuring training ground-truth and live inference operate on the same
    signal segment.

    Signals shorter than 60 s are returned from start_idx to end of signal.
    """
    start_idx = 10 * fs   # drop first 10 s — orienting artifact
    end_idx = 60 * fs     # keep next 50 s (T+10s to T+60s)
    return signal[start_idx:end_idx]


def _compute_eeg_features(signal_right: np.ndarray, signal_left: np.ndarray, fs: int = FS) -> Tuple[float, float]:
    """
    Computes objective Valence (FAA + FBA) and Arousal EEG component (Beta/Alpha ratio).
    """
    # 1.0 Hz High-pass filter to remove slow physical movement artifacts
    b, a = scipy.signal.butter(4, 1.0 / (0.5 * fs), btype='high')
    filtered_right = scipy.signal.filtfilt(b, a, signal_right)
    filtered_left = scipy.signal.filtfilt(b, a, signal_left)

    bands = {
        "Delta": (2.0, 4),
        "Theta": (4, 8),
        "Alpha": (8, 13),
        "Beta": (13, 30),
        "Gamma": (30, 100)
    }

    def _relative_powers(sig: np.ndarray) -> Tuple[float, float]:
        nperseg = min(fs, len(sig))
        if nperseg < 4:
            return 1e-6, 1e-6
        f, Pxx = scipy.signal.welch(sig, fs=fs, nperseg=nperseg)
        
        valid_idx = f >= 2.0
        f_clean = f[valid_idx]
        Pxx_clean = Pxx[valid_idx]
        
        powers = {}
        for band, (low, high) in bands.items():
            mask = (f_clean >= low) & (f_clean <= high)
            powers[band] = float(np.trapezoid(Pxx_clean[mask], f_clean[mask])) if np.any(mask) else 0.0
            
        total_power = sum(powers.values())
        if total_power > 0:
            return max(powers["Alpha"] / total_power, 1e-6), max(powers["Beta"] / total_power, 1e-6)
        return 1e-6, 1e-6

    alpha_R, beta_R = _relative_powers(filtered_right)
    alpha_L, beta_L = _relative_powers(filtered_left)
    
    faa = np.log(alpha_R + 1e-9) - np.log(alpha_L + 1e-9)
    fba = np.log(beta_R + 1e-9) - np.log(beta_L + 1e-9)
    raw_valence = (0.6 * faa) + (0.4 * fba)
    final_valence = float(np.clip(raw_valence, -1.0, 1.0))
    
    alpha_total = alpha_R + alpha_L
    beta_total = beta_R + beta_L
    arousal_eeg = float(np.log((beta_total + 1e-9) / (alpha_total + 1e-9)))
    
    return final_valence, arousal_eeg


def _compute_faa(signal_right: np.ndarray, signal_left: np.ndarray, fs: int = FS) -> float:
    """Backward-compatible FAA helper returning valence-like FAA output."""
    final_valence, _ = _compute_eeg_features(signal_right, signal_left, fs=fs)
    return float(final_valence)


def _detect_r_peaks(ecg: np.ndarray, fs: int = FS) -> np.ndarray:
    """Simple R-peak detector using scipy.signal.find_peaks on filtered ECG."""
    # Band-pass 0.5-5.0 Hz to isolate QRS complex and remove wander
    nyq = fs / 2.0
    try:
        sos = scipy.signal.butter(4, [0.5 / nyq, 5.0 / nyq], btype="band", output="sos")
        filtered = scipy.signal.sosfiltfilt(sos, ecg)
    except Exception:
        filtered = ecg  # fallback: unfiltered

    # Min distance = 0.4 s between peaks (max 150 bpm)
    min_distance = int(fs * 0.4)
    height_threshold = np.percentile(np.abs(filtered), 75)
    from typing import cast
    peaks, _ = scipy.signal.find_peaks(filtered, distance=min_distance, height=height_threshold)
    return cast(np.ndarray, peaks)


def _compute_rmssd(ecg: np.ndarray, fs: int = FS) -> float:
    """
    RMSSD from successive R-R interval differences (time-domain HRV).
    Returns RMSSD in milliseconds. Returns RMSSD reference on failure.
    """
    baseline = get_config().emotion.rmssd_baseline_ms
    try:
        peaks = _detect_r_peaks(ecg, fs=fs)
        if len(peaks) < 2:
            logger.warning("Fewer than 2 R-peaks detected — using RMSSD baseline.")
            return baseline
        rr_intervals_sec = np.diff(peaks) / fs
        rr_intervals_ms = rr_intervals_sec * 1000.0  # convert to ms
        
        valid_rr = np.array([rr for rr in rr_intervals_ms if 300 <= rr <= 1200])
        if len(valid_rr) < 2:
            logger.warning("Valid RR intervals < 2 after mask — using RMSSD baseline.")
            return baseline
            
        successive_diffs = np.diff(valid_rr)
        valid_diffs = successive_diffs[np.abs(successive_diffs) < 150]
        
        if len(valid_diffs) == 0:
            return 0.0
            
        rmssd = float(np.sqrt(np.mean(valid_diffs ** 2)))
        return max(rmssd, 0.0)
    except Exception as exc:
        logger.warning("RMSSD computation failed: %s. Using baseline.", exc)
        return baseline


# ---------------------------------------------------------------------------
# Per-Trial Feature Extraction
# ---------------------------------------------------------------------------

def _extract_biometrics(eeg_filename: str, experiment_id: int) -> Tuple[float, float, float]:
    """
    Load the raw EEG/ECG file for a single trial and return (valence, arousal, neuro_score).

    Channel mapping (consistent across all experiments):
      Channel1 → EEG Right Frontal (F4)
      Channel2 → EEG Left Frontal  (F3)
      Channel3 → ECG

    Returns (0.0, 0.0, 0.5) on any unrecoverable failure so the pipeline does not crash.
    """
    raw_path = _RAW_DIR / f"experiment_{experiment_id:02d}" / eeg_filename.strip()
    df = _load_eeg_csv(raw_path)
    if df is None:
        return 0.0, 0.0, 0.5

    required = ["Channel1", "Channel2", "Channel3"]
    if not all(c in df.columns for c in required):
        logger.warning("Missing required channels in %s — skipping.", raw_path.name)
        return 0.0, 0.0, 0.5

    ch_right = _truncate_50s(np.asarray(df["Channel1"], dtype=float), fs=FS)
    ch_left  = _truncate_50s(np.asarray(df["Channel2"], dtype=float), fs=FS)
    ch_ecg   = _truncate_50s(np.asarray(df["Channel3"], dtype=float), fs=FS)

    # Minimum length guard: at least 5 seconds of signal required
    min_samples = FS * 5
    if len(ch_right) < min_samples or len(ch_left) < min_samples or len(ch_ecg) < min_samples:
        logger.warning("Signal too short in %s (%d samples) — skipping.",
                       raw_path.name, len(ch_right))
        return 0.0, 0.0, 0.5

    final_valence, arousal_eeg = _compute_eeg_features(ch_right, ch_left, fs=FS)
    rmssd_ms = _compute_rmssd(ch_ecg, fs=FS)
    
    arousal_ecg = 1.0 - (rmssd_ms / 50.0)
    raw_arousal = (0.5 * arousal_ecg) + (0.5 * arousal_eeg)
    final_arousal = float(np.clip(raw_arousal, -1.0, 1.0))

    v_scaled = (final_valence + 1.0) / 2.0
    a_inverted_scaled = (1.0 - final_arousal) / 2.0
    neuro_score = (v_scaled + a_inverted_scaled) / 2.0

    return final_valence, final_arousal, float(neuro_score)


# ---------------------------------------------------------------------------
# Affective Fusion Core
# ---------------------------------------------------------------------------

def _fuse(
    obj_valence: float,
    obj_arousal: float,
    subj_valence: Optional[float],
    subj_arousal: Optional[float],
    alpha: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Multimodal Affective Fusion.

    Target_V = α × FAA + (1 - α) × Subjective_V
    Target_A = α × RMSSD_Arousal + (1 - α) × Subjective_A

    If Subjective scores are NaN, α is forced to 1.0 (100% objective).
    """
    if alpha is None:
        alpha = get_config().fusion.alpha
    import math
    if subj_valence is None or math.isnan(subj_valence):
        target_v = obj_valence
        alpha_used_v = 1.0
        delta_v = None
    else:
        target_v = (alpha * obj_valence) + ((1.0 - alpha) * subj_valence)
        alpha_used_v = alpha
        delta_v = obj_valence - subj_valence

    if subj_arousal is None or math.isnan(subj_arousal):
        target_a = obj_arousal
        alpha_used_a = 1.0
        delta_a = None
    else:
        target_a = (alpha * obj_arousal) + ((1.0 - alpha) * subj_arousal)
        alpha_used_a = alpha
        delta_a = obj_arousal - subj_arousal

    alpha_used = alpha_used_v  # Assuming alpha_used is the same for both if valid
    fused_v = target_v
    fused_a = target_a

    if delta_v is not None and delta_a is not None:
        euclidean = float(np.sqrt(delta_v ** 2 + delta_a ** 2))
    else:
        euclidean = None

    return {
        "fused_valence": float(fused_v),
        "fused_arousal": float(fused_a),
        "objective_valence": float(obj_valence),
        "objective_arousal": float(obj_arousal),
        "subjective_valence": subj_valence,
        "subjective_arousal": subj_arousal,
        "delta_valence": delta_v,
        "delta_arousal": delta_a,
        "euclidean_distance": euclidean,
        "alpha_used": alpha_used,
    }


# ---------------------------------------------------------------------------
# Derived Spatial Features (01_backend_data_pipeline.md §3.D)
# ---------------------------------------------------------------------------

def _add_derived_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute derived spatial features from independent variables.
    All divisions guard against zero denominators.
    """
    df = df.copy()
    eps = 1e-9

    # Core dimensions
    L = df.get("Length_m", pd.Series(0.0, index=df.index))
    W = df.get("Width_m",  pd.Series(0.0, index=df.index))
    H = df.get("Height_m", pd.Series(0.0, index=df.index))

    df["Length_to_Width_Ratio"]       = L / (W + eps)
    df["Floor_Area_m2"]               = L * W
    df["Wall_Area_m2"]                = 2.0 * (L + W) * H
    df["Volume_m3"]                   = L * W * H

    door_area  = df.get("Door_Area_m2",     pd.Series(0.0, index=df.index))
    window_area = df.get("Window_Area_m2",  pd.Series(0.0, index=df.index))
    walkable    = df.get("Walkable_Floor_Area_m2", pd.Series(0.0, index=df.index))

    wall_area_safe  = df["Wall_Area_m2"].replace(0, eps)
    floor_area_safe = df["Floor_Area_m2"].replace(0, eps)

    df["Door_to_Wall_Ratio"]            = door_area   / wall_area_safe
    df["Window_to_Wall_Ratio"]          = window_area / wall_area_safe
    df["Walkable_to_Floor_Ratio"]       = walkable    / floor_area_safe

    return df


# ---------------------------------------------------------------------------
# Public API: run_fusion_pipeline
# ---------------------------------------------------------------------------

def run_fusion_pipeline(merged_df: pd.DataFrame) -> pd.DataFrame:
    """
    Execute the full Affective Fusion pipeline on the merged DataFrame.

    Parameters
    ----------
    merged_df : pd.DataFrame
        Output of data_loader.load_and_merge()

    Returns
    -------
    pd.DataFrame
        One row per trial, including all spatial features, demographics,
        biometric targets, and fusion results.  Saved to
        data/processed/fusion_analysis.parquet.
    """
    records = []
    failed = 0
    total = len(merged_df)

    for idx, row in merged_df.iterrows():
        eeg_filename = row.get("EEG_Filename")
        experiment_id = row.get("experiment_id")

        if pd.isna(eeg_filename) or pd.isna(experiment_id):
            failed += 1
            continue

        try:
            obj_v, obj_a, neuro_score = _extract_biometrics(str(eeg_filename), int(experiment_id))
        except Exception as exc:
            logger.error("Biometric extraction failed for row %d (%s): %s", idx, eeg_filename, exc)
            failed += 1
            continue

        # Retrieve subjective scores (may be NaN for Exp 01)
        raw_sub_v = row.get("Valence Score by Subject")
        raw_sub_a = row.get("Arousal Score by Subject")
        sub_v = float(raw_sub_v) if raw_sub_v is not None and not pd.isna(raw_sub_v) else None
        sub_a = float(raw_sub_a) if raw_sub_a is not None and not pd.isna(raw_sub_a) else None

        fusion = _fuse(obj_v, obj_a, sub_v, sub_a)

        record = {
            "Subject_ID":    row.get("Subject_ID"),
            "Room_ID":       row.get("Room_ID"),
            "experiment_id": int(experiment_id),
            "EEG_Filename":  str(eeg_filename),
            "age":           row.get("age"),
            "occupation":    row.get("occupation"),
            "Sleep_Hours":   row.get("Sleep Hours"),
            "NeuroScore":    neuro_score,
            # Raw spatial inputs
            "Length_m":            row.get("Length_m"),
            "Width_m":             row.get("Width_m"),
            "Height_m":            row.get("Height_m"),
            "Num_Doors":           row.get("Num_Doors"),
            "Door_Area_m2":        row.get("Door_Area_m2"),
            "Num_Windows":         row.get("Num_Windows"),
            "Window_Area_m2":      row.get("Window_Area_m2"),
            "Daylight_Factor_pct": row.get("Daylight_Factor_pct"),
            "Illuminance_lux":     row.get("Illuminance_lux"),
            "CCT_K":               row.get("CCT_K"),
            "Walkable_Floor_Area_m2": row.get("Walkable_Floor_Area_m2"),
        }

        # Append OHE columns that were generated by data_loader
        ohe_cols = [c for c in row.index if (
            c.startswith("Day_or_Night_") or
            c.startswith("Type_of_Space_") or
            c.startswith("gender_")
        )]
        for ohe_col in ohe_cols:
            record[ohe_col] = row.get(ohe_col)

        # Merge fusion results
        record.update(fusion)
        records.append(record)

    logger.info("Fusion pipeline complete: %d/%d trials processed (%d skipped).",
                len(records), total, failed)

    if not records:
        raise RuntimeError("Fusion pipeline produced zero records — check raw data and EEG filenames.")

    fusion_df = pd.DataFrame(records)

    # ---- Derive spatial computed features ----
    fusion_df = _add_derived_features(fusion_df)

    # ---- Save to Parquet ----
    _PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    parquet_path = _PROCESSED_DIR / "fusion_analysis.parquet"
    fusion_df.to_parquet(parquet_path, index=False, engine="pyarrow")
    logger.info("Saved fusion_analysis.parquet → %s  (%d rows × %d cols)",
                parquet_path, *fusion_df.shape)

    return fusion_df


# ---------------------------------------------------------------------------
# Legacy shim — keeps process_emotion_engine importable for any remaining callers
# ---------------------------------------------------------------------------

def process_emotion_engine(
    signal_right: np.ndarray,
    signal_left: np.ndarray,
    signal_ecg: np.ndarray,
    fs: int = FS,
    global_mean_r: Optional[float] = None,
    global_std_r: Optional[float] = None,
    global_mean_l: Optional[float] = None,
    global_std_l: Optional[float] = None,
    apply_truncation: bool = True,
) -> Dict[str, Any]:
    """
    Legacy shim: compute FAA + RMSSD from raw arrays (no CSV I/O).
    Returns a dict compatible with old callers.
    """
    if np.any(np.isnan(signal_right)) or np.any(np.isnan(signal_left)) or np.any(np.isnan(signal_ecg)):
        raise ValueError("Input signals contain NaN values.")

    expected_len = 50 * fs
    if len(signal_right) < expected_len or len(signal_left) < expected_len or len(signal_ecg) < expected_len:
        raise ValueError(f"Signals must be at least {expected_len} samples (50 seconds at {fs} Hz).")

    sig_r = _truncate_50s(signal_right, fs) if apply_truncation else signal_right
    sig_l = _truncate_50s(signal_left, fs) if apply_truncation else signal_left
    sig_e = _truncate_50s(signal_ecg, fs) if apply_truncation else signal_ecg

    final_valence, arousal_eeg = _compute_eeg_features(sig_r.astype(float), sig_l.astype(float), fs)
    rmssd_ms = _compute_rmssd(sig_e.astype(float), fs)
    
    arousal_ecg = 1.0 - (rmssd_ms / 50.0)
    raw_arousal = (0.5 * arousal_ecg) + (0.5 * arousal_eeg)
    final_arousal = float(np.clip(raw_arousal, -1.0, 1.0))

    return {
        "MDS": {
            "Valence_X": [final_valence],
            "Arousal_Y": [final_arousal],
        },
        "Bands": {},
        "Emotion_Distribution": {},
    }
