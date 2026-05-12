"""
Emotion Engine — Phase 2: Affective Fusion Target Calculation
Source of Truth: instructions/01_backend_data_pipeline.md §3–4
                 instructions/03_execution_roadmap.md Phase 2

Pipeline per trial:
  1. Load raw EEG/ECG CSV → truncate to 50-second window (strict)
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

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
FS: int = 256                    # EEG/ECG sampling rate (Hz)
ALPHA_DEFAULT: float = 0.6       # Fusion weight for objective biometric layer
WINDOW_50S: int = FS * 50        # 50-second truncation window (samples)
RMSSD_BASELINE_MS: float = 50.0  # Neutral RMSSD reference for Arousal mapping

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
    Strict 50-second truncation window as required by the manifest.
    Takes samples [0 : 50*fs].  Signals shorter than 50 s are returned as-is.
    """
    max_samples = fs * 50
    return signal[:max_samples]


def _compute_faa(signal_right: np.ndarray, signal_left: np.ndarray, fs: int = FS) -> float:
    """
    Frontal Alpha Asymmetry: FAA = ln(α_right) - ln(α_left)

    Uses Welch's PSD to estimate alpha band power (8–13 Hz) for both
    hemispheres.  Result is clipped to [-1, 1].
    """
    alpha_band = (8.0, 13.0)

    def _alpha_power(sig: np.ndarray) -> float:
        nperseg = min(fs, len(sig))
        if nperseg < 4:
            return 1e-6
        f, Pxx = scipy.signal.welch(sig, fs=fs, nperseg=nperseg)
        mask = (f >= alpha_band[0]) & (f <= alpha_band[1])
        power = float(np.trapezoid(Pxx[mask], f[mask])) if np.any(mask) else 0.0
        return max(float(np.nan_to_num(power, nan=0.0, posinf=0.0, neginf=0.0)), 1e-6)

    alpha_r = _alpha_power(signal_right)
    alpha_l = _alpha_power(signal_left)
    faa = np.log(alpha_r) - np.log(alpha_l)
    return float(np.clip(faa, -1.0, 1.0))


def _detect_r_peaks(ecg: np.ndarray, fs: int = FS) -> np.ndarray:
    """Simple R-peak detector using scipy.signal.find_peaks on filtered ECG."""
    # Band-pass 5–40 Hz to isolate QRS complex
    nyq = fs / 2.0
    try:
        sos = scipy.signal.butter(4, [5.0 / nyq, 40.0 / nyq], btype="band", output="sos")
        filtered = scipy.signal.sosfiltfilt(sos, ecg)
    except Exception:
        filtered = ecg  # fallback: unfiltered

    # Min distance = 0.3 s between peaks (max ~200 bpm)
    min_dist = max(int(fs * 0.3), 1)
    height_threshold = np.percentile(np.abs(filtered), 75)
    peaks, _ = scipy.signal.find_peaks(filtered, distance=min_dist, height=height_threshold)
    return peaks


def _compute_rmssd(ecg: np.ndarray, fs: int = FS) -> float:
    """
    RMSSD from successive R-R interval differences (time-domain HRV).
    Returns RMSSD in milliseconds.  Returns RMSSD_BASELINE_MS on failure.
    """
    try:
        peaks = _detect_r_peaks(ecg, fs=fs)
        if len(peaks) < 2:
            logger.warning("Fewer than 2 R-peaks detected — using RMSSD baseline.")
            return RMSSD_BASELINE_MS
        rr_intervals_ms = np.diff(peaks) / fs * 1000.0  # convert to ms
        successive_diffs = np.diff(rr_intervals_ms)
        rmssd = float(np.sqrt(np.mean(successive_diffs ** 2)))
        return max(rmssd, 0.0)
    except Exception as exc:
        logger.warning("RMSSD computation failed: %s. Using baseline.", exc)
        return RMSSD_BASELINE_MS


def _rmssd_to_arousal(rmssd_ms: float) -> float:
    """
    Map RMSSD (ms) to arousal on [-1, 1].

    Higher HRV (high RMSSD) → parasympathetic dominance → lower arousal.
    Formula: Arousal = 1.0 - (RMSSD / BASELINE), clipped to [-1, 1].
    """
    return float(np.clip(1.0 - (rmssd_ms / RMSSD_BASELINE_MS), -1.0, 1.0))


# ---------------------------------------------------------------------------
# Per-Trial Feature Extraction
# ---------------------------------------------------------------------------

def _extract_biometrics(eeg_filename: str, experiment_id: int) -> Tuple[float, float]:
    """
    Load the raw EEG/ECG file for a single trial and return (faa, arousal).

    Channel mapping (consistent across all experiments):
      Channel1 → EEG Right Frontal (F4)
      Channel2 → EEG Left Frontal  (F3)
      Channel3 → ECG

    Returns (0.0, 0.0) on any unrecoverable failure so the pipeline does not crash.
    """
    raw_path = _RAW_DIR / f"experiment_{experiment_id:02d}" / eeg_filename.strip()
    df = _load_eeg_csv(raw_path)
    if df is None:
        return 0.0, 0.0

    required = ["Channel1", "Channel2", "Channel3"]
    if not all(c in df.columns for c in required):
        logger.warning("Missing required channels in %s — skipping.", raw_path.name)
        return 0.0, 0.0

    ch_right = _truncate_50s(df["Channel1"].values.astype(float), fs=FS)
    ch_left  = _truncate_50s(df["Channel2"].values.astype(float), fs=FS)
    ch_ecg   = _truncate_50s(df["Channel3"].values.astype(float), fs=FS)

    # Minimum length guard: at least 5 seconds of signal required
    min_samples = FS * 5
    if len(ch_right) < min_samples or len(ch_left) < min_samples or len(ch_ecg) < min_samples:
        logger.warning("Signal too short in %s (%d samples) — skipping.",
                       raw_path.name, len(ch_right))
        return 0.0, 0.0

    faa = _compute_faa(ch_right, ch_left, fs=FS)
    rmssd_ms = _compute_rmssd(ch_ecg, fs=FS)
    arousal = _rmssd_to_arousal(rmssd_ms)

    return faa, arousal


# ---------------------------------------------------------------------------
# Affective Fusion Core
# ---------------------------------------------------------------------------

def _fuse(
    obj_valence: float,
    obj_arousal: float,
    subj_valence: Optional[float],
    subj_arousal: Optional[float],
    alpha: float = ALPHA_DEFAULT,
) -> Dict[str, Any]:
    """
    Multimodal Affective Fusion.

    Target_V = α × FAA + (1 - α) × Subjective_V
    Target_A = α × RMSSD_Arousal + (1 - α) × Subjective_A

    If Subjective scores are NaN, α is forced to 1.0 (100% objective).
    """
    has_subjective = (subj_valence is not None) and (subj_arousal is not None)

    if has_subjective:
        alpha_used = alpha
        fused_v = alpha_used * obj_valence + (1.0 - alpha_used) * subj_valence
        fused_a = alpha_used * obj_arousal + (1.0 - alpha_used) * subj_arousal
        delta_v = obj_valence - subj_valence
        delta_a = obj_arousal - subj_arousal
        euclidean = float(np.sqrt(delta_v ** 2 + delta_a ** 2))
    else:
        # Fallback: Experiment 01 — no subjective data
        alpha_used = 1.0
        fused_v = obj_valence
        fused_a = obj_arousal
        delta_v = None
        delta_a = None
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
    L = df.get("Length_m", pd.Series(np.zeros(len(df))))
    W = df.get("Width_m",  pd.Series(np.zeros(len(df))))
    H = df.get("Height_m", pd.Series(np.zeros(len(df))))

    df["Length_to_Width_Ratio"]       = L / (W + eps)
    df["Floor_Area_m2"]               = L * W
    df["Wall_Area_m2"]                = 2.0 * (L + W) * H
    df["Volume_m3"]                   = L * W * H

    door_area  = df.get("Door_Area_m2",     pd.Series(np.zeros(len(df))))
    window_area = df.get("Window_Area_m2",  pd.Series(np.zeros(len(df))))
    walkable    = df.get("Walkable_Floor_Area_m2", pd.Series(np.zeros(len(df))))

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
            obj_v, obj_a = _extract_biometrics(str(eeg_filename), int(experiment_id))
        except Exception as exc:
            logger.error("Biometric extraction failed for row %d (%s): %s", idx, eeg_filename, exc)
            failed += 1
            continue

        # Retrieve subjective scores (may be NaN for Exp 01)
        raw_sub_v = row.get("Valence Score by Subject")
        raw_sub_a = row.get("Arousal Score by Subject")
        sub_v = float(raw_sub_v) if raw_sub_v is not None and not pd.isna(raw_sub_v) else None
        sub_a = float(raw_sub_a) if raw_sub_a is not None and not pd.isna(raw_sub_a) else None

        fusion = _fuse(obj_v, obj_a, sub_v, sub_a, alpha=ALPHA_DEFAULT)

        record = {
            "Subject_ID":    row.get("Subject_ID"),
            "Room_ID":       row.get("Room_ID"),
            "experiment_id": int(experiment_id),
            "EEG_Filename":  str(eeg_filename),
            "age":           row.get("age"),
            "occupation":    row.get("occupation"),
            "Sleep_Hours":   row.get("Sleep Hours"),
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
    sig_r = _truncate_50s(signal_right, fs) if apply_truncation else signal_right
    sig_l = _truncate_50s(signal_left, fs) if apply_truncation else signal_left
    sig_e = _truncate_50s(signal_ecg, fs) if apply_truncation else signal_ecg

    faa = _compute_faa(sig_r.astype(float), sig_l.astype(float), fs)
    rmssd_ms = _compute_rmssd(sig_e.astype(float), fs)
    arousal = _rmssd_to_arousal(rmssd_ms)

    return {
        "MDS": {
            "Valence_X": [faa],
            "Arousal_Y": [arousal],
        },
        "Bands": {},
        "Emotion_Distribution": {},
    }
