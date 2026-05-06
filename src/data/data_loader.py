"""
Data Loader Module
Aligned with: arxiv.org/html/2506.16448v1 (Section 3.3.1)

Loads spatial room data + EEG biometrics, applies paper preprocessing
(baseline removal + Z-score normalization) before creating tensors.

NOTE: This module provides both Streamlit-cached and standalone versions.
Use load_data() for Streamlit, load_data_standalone() for Rhino/other environments.
"""
import os
import logging
from typing import List, Tuple, Dict, Any, Optional

import numpy as np
import pandas as pd
import torch

# Optional Streamlit import - gracefully handles non-Streamlit environments
try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False
    st = None

from src.config import get_config
from src.data.emotion_engine import process_emotion_engine
from src.data.experiment_registry import discover_experiments
from src.data.preprocessing import preprocess_eeg_signal
from src.utils.cache_manager import get_cache_manager

logger = logging.getLogger(__name__)

# Define Base Directory (src parent)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, 'data')
SYNTHETIC_CACHE_FILE = os.path.join(DATA_DIR, 'processed', 'synthetic_data_fallback.pt')


def _first_existing_column(columns: List[str], candidates: List[str]) -> Optional[str]:
    """Return the first candidate column present in columns, else None."""
    available = set(columns)
    for candidate in candidates:
        if candidate in available:
            return candidate
    return None


def _extract_target_coords(
    row: pd.Series,
    objective_valence: float,
    objective_arousal: float,
    alpha: float = 0.6,
) -> Dict[str, Any]:
    """Multimodal affective fusion for ground-truth target generation.

    Combines objective biometric signals (FAA, RMSSD) with subjective
    self-reported scores using a weighted average controlled by ``alpha``.

    Fusion formulae:
        Target_V = alpha × FAA_Valence  + (1 - alpha) × Subjective_V
        Target_A = alpha × RMSSD_Arousal + (1 - alpha) × Subjective_A

    When subjective scores are unavailable, 100% objective is used (alpha=1.0).

    Returns a dict with:
        fused_valence, fused_arousal   — final ML ground truth
        objective_valence, objective_arousal — EEG/ECG derived
        subjective_valence, subjective_arousal — self-reported (or None)
        delta_valence, delta_arousal   — signed difference (obj - subj)
        euclidean_distance             — L2 norm between obj and subj
        alpha                          — weight used
    """
    val_col = _first_existing_column(
        list(row.index), ['Valence Score by Subject ', 'Valence Score by Subject'])
    aro_col = _first_existing_column(
        list(row.index), ['Arousal Score by Subject ', 'Arousal Score by Subject'])

    sub_v = float(row[val_col]) if val_col is not None and not pd.isna(row[val_col]) else None
    sub_a = float(row[aro_col]) if aro_col is not None and not pd.isna(row[aro_col]) else None

    obj_v = float(objective_valence)
    obj_a = float(objective_arousal)

    if sub_v is not None and sub_a is not None:
        fused_v = alpha * obj_v + (1.0 - alpha) * sub_v
        fused_a = alpha * obj_a + (1.0 - alpha) * sub_a
        delta_v = obj_v - sub_v
        delta_a = obj_a - sub_a
        euclidean = float(np.sqrt(delta_v ** 2 + delta_a ** 2))
    else:
        # No subjective data — use 100% objective
        fused_v = obj_v
        fused_a = obj_a
        delta_v = None
        delta_a = None
        euclidean = None

    return {
        'fused_valence': fused_v,
        'fused_arousal': fused_a,
        'objective_valence': obj_v,
        'objective_arousal': obj_a,
        'subjective_valence': sub_v,
        'subjective_arousal': sub_a,
        'delta_valence': delta_v,
        'delta_arousal': delta_a,
        'euclidean_distance': euclidean,
        'alpha': alpha,
    }


def _serialize_dataset(
    X_spatial: np.ndarray,
    y_va: np.ndarray,
    biometric_sequences: List[Tuple[torch.Tensor, List[float]]],
) -> Dict[str, Any]:
    """Serialize dataset into a torch-safe payload."""
    serialized_bio = []
    for signal_tensor, target_coords in biometric_sequences:
        serialized_bio.append(
            (
                signal_tensor.detach().cpu(),
                torch.tensor(target_coords, dtype=torch.float32),
            )
        )

    return {
        'X_spatial': torch.tensor(X_spatial, dtype=torch.float32),
        'y_va': torch.tensor(y_va, dtype=torch.float32),
        'biometric_sequences': serialized_bio,
    }


def _deserialize_dataset(payload: Dict[str, Any]) -> Tuple[np.ndarray, np.ndarray, List[Tuple[torch.Tensor, List[float]]]]:
    """Deserialize torch payload back to project dataset format."""
    if not isinstance(payload, dict):
        raise ValueError("Cache payload must be a dictionary.")

    required_keys = {'X_spatial', 'y_va', 'biometric_sequences'}
    if not required_keys.issubset(payload.keys()):
        raise ValueError(f"Cache payload missing required keys: {required_keys - set(payload.keys())}")

    X_spatial = payload['X_spatial'].detach().cpu().numpy()
    y_va = payload['y_va'].detach().cpu().numpy()

    biometric_sequences: List[Tuple[torch.Tensor, List[float]]] = []
    for signal_tensor, target_tensor in payload['biometric_sequences']:
        biometric_sequences.append((signal_tensor, target_tensor.detach().cpu().tolist()))

    return X_spatial, y_va, biometric_sequences


def load_data(force_reload: bool = False):
    """
    Loads spatial room data and corresponding EEG biometrics.

    Preprocessing applied per paper §3.3.1:
      1. Baseline removal per channel
      2. Z-score normalization per channel

    This function uses Streamlit caching when available.

    Returns:
        X_spatial: numpy array (N, 3) of [Length, Width, Height]
        y_va: numpy array (N, 2) of [Valence, Arousal] targets
        biometric_sequences: list of (Tensor(3, 500), [V, A])
    """
    if _is_streamlit_runtime():
        return _load_data_streamlit(force_reload)
    return load_data_standalone(force_reload)


def _is_streamlit_runtime() -> bool:
    """Return True only when executing under an active Streamlit runtime."""
    if not STREAMLIT_AVAILABLE or st is None:
        return False

    runtime = getattr(st, 'runtime', None)
    if runtime is None or not hasattr(runtime, 'exists'):
        return False

    try:
        return bool(runtime.exists())
    except Exception:
        return False


def _load_data_streamlit(force_reload: bool = False):
    """Streamlit-cached version of data loading."""

    @st.cache_data(ttl=3600, show_spinner=False)
    def _cached_load():
        return _load_data_impl()

    if force_reload:
        _cached_load.clear()

    return _cached_load()


def load_data_standalone(force_reload: bool = False):
    """
    Standalone data loading for non-Streamlit environments (e.g., Rhino).

    Uses the cache_manager for caching.
    """
    cache_manager = get_cache_manager()
    if force_reload:
        cache_manager.clear('main_data')
        return _load_data_impl()
    return cache_manager.get_or_compute('main_data', _load_data_impl)


def _load_data_impl():
    """Core data loading implementation - no caching logic."""
    processed_dir = os.path.join(DATA_DIR, 'processed')
    cache_file = os.path.join(processed_dir, 'cached_data.pt')

    if os.path.exists(cache_file):
        try:
            payload = torch.load(cache_file, weights_only=True)
            return _deserialize_dataset(payload)
        except Exception as e:
            logger.warning(f"Failed to load cache: {e}. Re-processing data...")

    experiments = discover_experiments(DATA_DIR)
    if not experiments:
        logger.warning(f"No split metadata files found in {os.path.join(DATA_DIR, 'metadata')}. Using Synthetic Data Generator.")
        if STREAMLIT_AVAILABLE and st is not None:
            st.warning("No split metadata files found. Using Synthetic Data Generator.")
        return _load_or_generate_synthetic_data()

    try:
        X_spatial: List[List[float]] = []
        y_va: List[List[float]] = []
        biometric_sequences: List[Tuple[torch.Tensor, List[float]]] = []

        valid_rows = 0
        config = get_config()
        fs = config.eeg.sample_rate
        target_len = config.eeg.target_length
        fusion_alpha = config.fusion.alpha

        subject_data = {}
        fusion_records: List[Dict[str, Any]] = []

        # Pass 1: Load and group by Subject_ID, applying Temporal Truncation
        for experiment in experiments:
            biometric_df = pd.read_csv(experiment.biometric_csv)
            spatial_df = pd.read_csv(experiment.spatial_csv)

            if biometric_df.empty or spatial_df.empty:
                continue

            merged_df = biometric_df.merge(spatial_df, on='Room_ID', how='left')

            length_col = _first_existing_column(list(merged_df.columns), ['Length (meter)', 'Length (m)'])
            width_col = _first_existing_column(list(merged_df.columns), ['Width (meter)', 'Width (m)'])
            height_col = _first_existing_column(list(merged_df.columns), ['Height (meter)', 'Height (m)'])

            if length_col is None or width_col is None or height_col is None:
                logger.warning(f"Skipping {experiment.name}: missing one or more spatial dimension columns.")
                continue

            for _, row in merged_df.iterrows():
                eeg_filename = row.get('EEG_Filename')
                if pd.isna(eeg_filename):
                    continue

                subj_id = row.get('Subject_ID', 'Unknown')

                l = row.get(length_col)
                w = row.get(width_col)
                h = row.get(height_col)
                if pd.isna(l) or pd.isna(w) or pd.isna(h):
                    continue

                eeg_path = os.path.join(experiment.raw_dir, str(eeg_filename).strip())
                if not os.path.exists(eeg_path):
                    continue

                try:
                    eeg_df = pd.read_csv(eeg_path)

                    if not all(col in eeg_df.columns for col in ['Channel1', 'Channel2', 'Channel3']):
                        if isinstance(eeg_df.columns, pd.MultiIndex):
                            eeg_df.columns = eeg_df.columns.map(' '.join).str.strip()
                        if not all(col in eeg_df.columns for col in ['Channel1', 'Channel2', 'Channel3']):
                            continue

                    # Apply Temporal Truncation: Ignore first 10 seconds, limit to 60s
                    from src.data.preprocessing import temporal_truncation
                    
                    ch1_trunc = temporal_truncation(eeg_df['Channel1'].values, fs=fs, start_sec=10, max_sec=60)
                    ch2_trunc = temporal_truncation(eeg_df['Channel2'].values, fs=fs, start_sec=10, max_sec=60)
                    ch3_trunc = temporal_truncation(eeg_df['Channel3'].values, fs=fs, start_sec=10, max_sec=60)

                    if len(ch1_trunc) == 0:
                        logger.warning(f"File {eeg_filename} too short after temporal truncation.")
                        continue

                    # Create a new df with the truncated arrays
                    eeg_df = pd.DataFrame({
                        'Channel1': ch1_trunc,
                        'Channel2': ch2_trunc,
                        'Channel3': ch3_trunc
                    })

                    subject_data.setdefault(subj_id, []).append({
                        'row': row,
                        'eeg_df': eeg_df,
                        'spatial': [float(l), float(w), float(h)],
                        'experiment': experiment.name,
                        'room_id': row.get('Room_ID', 'Unknown'),
                    })

                except Exception as e:
                    logger.error(f"Error processing {eeg_filename} in {experiment.name}: {e}")
                    continue

        # Pass 2: Within-Subject Normalization and Feature Extraction
        for subj_id, trials in subject_data.items():
            # Concatenate all trials for this subject to find global mean/std
            all_ch1 = np.concatenate([t['eeg_df']['Channel1'].values for t in trials])
            all_ch2 = np.concatenate([t['eeg_df']['Channel2'].values for t in trials])
            all_ch3 = np.concatenate([t['eeg_df']['Channel3'].values for t in trials])

            mean_1, std_1 = np.mean(all_ch1), np.std(all_ch1)
            mean_2, std_2 = np.mean(all_ch2), np.std(all_ch2)
            mean_3, std_3 = np.mean(all_ch3), np.std(all_ch3)

            for t in trials:
                try:
                    eeg_df = t['eeg_df']
                    ch1_raw = eeg_df['Channel1'].values
                    ch2_raw = eeg_df['Channel2'].values
                    ch3_raw = eeg_df['Channel3'].values

                    # Compute Emotion Features (using FAA for Valence and RMSSD for Arousal)
                    emotion_result = process_emotion_engine(
                        signal_right=ch1_raw, 
                        signal_left=ch2_raw, 
                        signal_ecg=ch3_raw,
                        fs=fs,
                        global_mean_r=mean_1, global_std_r=std_1,
                        global_mean_l=mean_2, global_std_l=std_2,
                        apply_truncation=False
                    )

                    mds_x_target = float(np.mean(emotion_result['MDS']['Valence_X']))
                    mds_y_target = float(np.mean(emotion_result['MDS']['Arousal_Y']))

                    # Multimodal Affective Fusion
                    fusion_result = _extract_target_coords(
                        t['row'],
                        objective_valence=mds_x_target,
                        objective_arousal=mds_y_target,
                        alpha=fusion_alpha,
                    )

                    target_coords = [fusion_result['fused_valence'], fusion_result['fused_arousal']]

                    # Record fusion metadata for frontend consumption
                    fusion_records.append({
                        'subject_id': subj_id,
                        'room_id': t.get('room_id', 'Unknown'),
                        'experiment': t.get('experiment', 'Unknown'),
                        **fusion_result,
                    })

                    # Apply preprocessing using subject-level normalizers
                    ch1 = preprocess_eeg_signal(ch1_raw, fs=fs, global_mean=mean_1, global_std=std_1, apply_truncation=False)
                    ch2 = preprocess_eeg_signal(ch2_raw, fs=fs, global_mean=mean_2, global_std=std_2, apply_truncation=False)
                    ch3 = preprocess_eeg_signal(ch3_raw, fs=fs, global_mean=mean_3, global_std=std_3, apply_truncation=False)
                    
                    signal_data = np.stack([ch1, ch2, ch3], axis=1)

                    if len(signal_data) > target_len:
                        signal_data = signal_data[:target_len]
                    elif len(signal_data) < target_len:
                        padding = np.zeros((target_len - len(signal_data), 3))
                        signal_data = np.vstack([signal_data, padding])

                    signal_tensor = torch.tensor(signal_data.T, dtype=torch.float32)

                    X_spatial.append(t['spatial'])
                    y_va.append(target_coords)
                    biometric_sequences.append((signal_tensor, target_coords))
                    valid_rows += 1

                except Exception as e:
                    logger.error(f"Error extracting features for subject {subj_id}: {e}")
                    continue

        if valid_rows == 0:
            logger.error("No valid data rows processed. Using synthetic data.")
            if STREAMLIT_AVAILABLE and st is not None:
                st.error("No valid data rows processed. Using synthetic data.")
            return _load_or_generate_synthetic_data()

        X_spatial_np = np.array(X_spatial)
        y_va_np = np.array(y_va)

        # Build fusion DataFrame for frontend visualization
        fusion_df = pd.DataFrame(fusion_records) if fusion_records else pd.DataFrame()

        try:
            os.makedirs(processed_dir, exist_ok=True)
            torch.save(_serialize_dataset(X_spatial_np, y_va_np, biometric_sequences), cache_file)
            # Also persist fusion data
            if not fusion_df.empty:
                fusion_df.to_csv(os.path.join(processed_dir, 'fusion_analysis.csv'), index=False)
        except Exception as e:
            logger.warning(f"Failed to save data cache: {e}")
            if STREAMLIT_AVAILABLE and st is not None:
                st.warning(f"Failed to save data cache: {e}")

        logger.info(f"Successfully loaded {valid_rows} aligned data points.")
        if STREAMLIT_AVAILABLE and st is not None:
            st.success(f"Successfully loaded {valid_rows} aligned data points.")
        return X_spatial_np, y_va_np, biometric_sequences

    except Exception as e:
        logger.error(f"Critical error loading data: {e}")
        if STREAMLIT_AVAILABLE and st is not None:
            st.error(f"Critical error loading data: {e}")
        return _load_or_generate_synthetic_data()


def _load_or_generate_synthetic_data(n_samples: int = 50):
    """Load deterministic synthetic fallback from cache or generate and persist it."""
    os.makedirs(os.path.dirname(SYNTHETIC_CACHE_FILE), exist_ok=True)
    if os.path.exists(SYNTHETIC_CACHE_FILE):
        try:
            payload = torch.load(SYNTHETIC_CACHE_FILE, weights_only=True)
            return _deserialize_dataset(payload)
        except Exception as exc:
            logger.warning(f"Failed to load synthetic cache: {exc}. Regenerating.")

    data = generate_synthetic_data(n_samples=n_samples, seed=42)
    try:
        torch.save(_serialize_dataset(*data), SYNTHETIC_CACHE_FILE)
    except Exception as exc:
        logger.warning(f"Failed to save synthetic fallback cache: {exc}")
    return data


def generate_synthetic_data(n_samples: int = 50, seed: int = 42):
    """Generates synthetic data for testing/demo purposes."""
    rng = np.random.default_rng(seed)
    X_spatial = rng.random((n_samples, 3)) * [48, 48, 8] + [2, 2, 2]
    y_va = (rng.random((n_samples, 2)) - 0.5) * 2.0

    biometric_sequences = []
    for y in y_va:
        signal = torch.randn(3, 500)
        biometric_sequences.append((signal, y))

    return X_spatial, y_va, biometric_sequences
