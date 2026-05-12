"""
Data Loader — Phase 1: Robust Multi-Experiment Data Ingestion
Source of Truth: instructions/01_backend_data_pipeline.md
                 instructions/03_execution_roadmap.md

Loads and unifies experiment_01, experiment_02, and experiment_03 biometric and
spatial CSVs into a single, cleansed DataFrame.  All Streamlit, Rhino, C#, API,
ONNX and PostgreSQL references have been removed.  This module is headless.
"""

import logging
import os
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Root paths — resolved relative to this file so the module is portable
# ---------------------------------------------------------------------------
_SRC_DIR = Path(__file__).resolve().parent.parent          # …/src
_PROJECT_ROOT = _SRC_DIR.parent                             # …/Predictive Atmospheres_Mark 3
_METADATA_DIR = _PROJECT_ROOT / "data" / "metadata"
_RAW_DIR = _PROJECT_ROOT / "data" / "raw"
_PROCESSED_DIR = _PROJECT_ROOT / "data" / "processed"


# ---------------------------------------------------------------------------
# Banned spatial metrics — must never enter the pipeline
# ---------------------------------------------------------------------------
BANNED_COLUMNS = {"UDI", "sDA", "ASE"}

# ---------------------------------------------------------------------------
# Column-name aliases produced by schema drift across experiments
# ---------------------------------------------------------------------------
_VALENCE_CANDIDATES = [
    "Valence Score by Subject",
    "Valence Score by Subject ",   # trailing space — Exp 02 artefact
]
_AROUSAL_CANDIDATES = [
    "Arousal Score by Subject",
    "Arousal Score by Subject ",
]

# ---------------------------------------------------------------------------
# Canonical output column names (spatial independent variables)
# ---------------------------------------------------------------------------
SPATIAL_COLS = {
    "Room_ID": "Room_ID",
    "Length (meter)": "Length_m",
    "Width (meter)": "Width_m",
    "Height (meter)": "Height_m",
    "Number of Door": "Num_Doors",
    "Door Area (sq.meter)": "Door_Area_m2",
    "Number of Windows": "Num_Windows",
    "Window Area (sq.meter)": "Window_Area_m2",
    "Daylight Factor (%)": "Daylight_Factor_pct",
    " Illuminance (lux)": "Illuminance_lux",     # leading space — Exp 02/03 artefact
    "Illuminance (lux)": "Illuminance_lux",
    "Correlated Color Temperature (Kelvin)": "CCT_K",
    "Walkable Floor Area (sq.meter)": "Walkable_Floor_Area_m2",
    "Day or Night": "Day_or_Night",
    "Type of Space": "Type_of_Space",
}


def _strip_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Strip trailing/leading whitespace from all column names."""
    df.columns = [c.strip() for c in df.columns]
    return df


def _drop_unnamed(df: pd.DataFrame) -> pd.DataFrame:
    """Drop every column whose name contains 'Unnamed'."""
    unnamed = [c for c in df.columns if "Unnamed" in str(c)]
    return df.drop(columns=unnamed)


def _drop_banned(df: pd.DataFrame) -> pd.DataFrame:
    """Remove any column matching the banned metrics list."""
    to_drop = [c for c in df.columns if any(b in c for b in BANNED_COLUMNS)]
    if to_drop:
        logger.warning("Dropping banned metric columns: %s", to_drop)
    return df.drop(columns=to_drop)


def _first_existing(candidates: list, available: set) -> Optional[str]:
    for c in candidates:
        if c in available:
            return c
    return None


# ===========================================================================
# Step 1 — Unify and Cleanse Biometric Data
# ===========================================================================

def _load_biometric(experiment_id: int) -> pd.DataFrame:
    """Load a single experiment's biometric CSV and normalise its schema."""
    csv_path = _METADATA_DIR / f"experiment_{experiment_id:02d}_biometric data.csv"
    if not csv_path.exists():
        logger.warning("Biometric CSV not found: %s", csv_path)
        return pd.DataFrame()

    df = pd.read_csv(csv_path)
    df = _strip_columns(df)
    df = _drop_unnamed(df)
    df["experiment_id"] = experiment_id

    available = set(df.columns)

    # ---- Normalise Valence / Arousal columns ----
    val_col = _first_existing(_VALENCE_CANDIDATES, available)
    aro_col = _first_existing(_AROUSAL_CANDIDATES, available)

    if val_col is not None:
        df.rename(columns={val_col: "Valence Score by Subject"}, inplace=True)
    else:
        # Experiment 01: only has "Score by Subject" — map to NaN for both axes
        if "Score by Subject" in available:
            logger.info("Exp %02d: mapping 'Score by Subject' → NaN for Valence & Arousal "
                        "(fusion fallback α=1.0 will apply).", experiment_id)
        df["Valence Score by Subject"] = np.nan

    if aro_col is not None:
        df.rename(columns={aro_col: "Arousal Score by Subject"}, inplace=True)
    else:
        df["Arousal Score by Subject"] = np.nan

    # ---- Sleep Hours (only present in Exp 03) ----
    if "Sleep Hours" not in df.columns:
        df["Sleep Hours"] = np.nan

    return df


def load_biometric_df() -> pd.DataFrame:
    """Load, cleanse, and concatenate biometric data from all 3 experiments."""
    frames = [_load_biometric(i) for i in [1, 2, 3]]
    frames = [f for f in frames if not f.empty]

    if not frames:
        raise FileNotFoundError("No biometric CSVs found under %s" % _METADATA_DIR)

    bio_df = pd.concat(frames, ignore_index=True)

    # ---- Impute missing Sleep Hours with dataset median ----
    # The column may arrive as strings ('8', '8.5', ' ') — coerce to numeric first
    bio_df["Sleep Hours"] = pd.to_numeric(bio_df["Sleep Hours"], errors="coerce")
    sleep_median = bio_df["Sleep Hours"].median()
    n_imputed = bio_df["Sleep Hours"].isna().sum()
    bio_df["Sleep Hours"] = bio_df["Sleep Hours"].fillna(sleep_median)
    logger.info("Imputed %d missing Sleep Hours with median %.1f.", n_imputed, sleep_median)

    logger.info("Biometric DataFrame: %d rows, %d columns.", *bio_df.shape)
    return bio_df


# ===========================================================================
# Step 2 — Unify and Cleanse Spatial Data
# ===========================================================================

def _load_spatial(experiment_id: int) -> pd.DataFrame:
    """Load a single experiment's spatial CSV and normalise its schema."""
    csv_path = _METADATA_DIR / f"experiment_{experiment_id:02d}_spatial data.csv"
    if not csv_path.exists():
        logger.warning("Spatial CSV not found: %s", csv_path)
        return pd.DataFrame()

    df = pd.read_csv(csv_path)
    df = _strip_columns(df)
    df = _drop_unnamed(df)
    df = _drop_banned(df)
    df["experiment_id"] = experiment_id

    # Rename to canonical column names
    rename_map = {}
    for raw_name, canonical in SPATIAL_COLS.items():
        if raw_name in df.columns:
            rename_map[raw_name] = canonical
    df.rename(columns=rename_map, inplace=True)

    return df


def load_spatial_df() -> pd.DataFrame:
    """
    Load, cleanse, and concatenate spatial data from all 3 experiments.

    Imputation rules (01_backend_data_pipeline.md §2):
      • Missing continuous spatial features → 0.0
      • Missing categorical features        → "Unspecified"
    """
    frames = [_load_spatial(i) for i in [1, 2, 3]]
    frames = [f for f in frames if not f.empty]

    if not frames:
        raise FileNotFoundError("No spatial CSVs found under %s" % _METADATA_DIR)

    spatial_df = pd.concat(frames, ignore_index=True)

    # ---- Impute continuous independent variables ----
    continuous_cols = [
        "Num_Doors", "Door_Area_m2", "Num_Windows", "Window_Area_m2",
        "Daylight_Factor_pct", "Illuminance_lux", "CCT_K",
        "Walkable_Floor_Area_m2",
    ]
    for col in continuous_cols:
        if col in spatial_df.columns:
            n_missing = spatial_df[col].isna().sum()
            if n_missing:
                spatial_df[col] = spatial_df[col].fillna(0.0)
                logger.info("Imputed %d missing values in '%s' with 0.0.", n_missing, col)
        else:
            spatial_df[col] = 0.0
            logger.info("Column '%s' entirely absent — added and set to 0.0.", col)

    # ---- Ensure Length/Width/Height are present ----
    for dim_col in ["Length_m", "Width_m", "Height_m"]:
        if dim_col not in spatial_df.columns:
            raise ValueError(f"Required spatial dimension column '{dim_col}' is missing.")

    # ---- Impute categorical variables ----
    for cat_col in ["Type_of_Space", "Day_or_Night"]:
        if cat_col in spatial_df.columns:
            n_missing = spatial_df[cat_col].isna().sum()
            if n_missing:
                spatial_df[cat_col] = spatial_df[cat_col].fillna("Unspecified")
                logger.info("Imputed %d missing '%s' values with 'Unspecified'.", n_missing, cat_col)
        else:
            spatial_df[cat_col] = "Unspecified"
            logger.info("Column '%s' entirely absent — added as 'Unspecified'.", cat_col)

    logger.info("Spatial DataFrame: %d rows, %d columns.", *spatial_df.shape)
    return spatial_df


# ===========================================================================
# Step 3 — The Grand Join
# ===========================================================================

def load_and_merge() -> pd.DataFrame:
    """
    Grand Join:
      1. Load Subject Data
      2. Merge with bio_df on Subject_ID
      3. Merge with spatial_df on Room_ID
      4. Drop rows with NaN Room_ID or Subject_ID
      5. One-hot encode categorical variables

    Returns a fully unified, cleansed DataFrame — ready for Affective Fusion.
    """
    # ---- Load Subject Data ----
    subject_csv = _METADATA_DIR / "Subject Data.csv"
    if not subject_csv.exists():
        raise FileNotFoundError("Subject Data.csv not found at %s" % subject_csv)
    subject_df = pd.read_csv(subject_csv)
    subject_df = _strip_columns(subject_df)
    logger.info("Subject Data: %d subjects.", len(subject_df))

    # ---- Biometric data ----
    bio_df = load_biometric_df()

    # ---- Spatial data ----
    spatial_df = load_spatial_df()

    # ---- Join subject demographics into biometrics ----
    merged = bio_df.merge(subject_df, on="Subject_ID", how="left")

    # ---- Join spatial data ----
    # Drop experiment_id duplicate from spatial before merging
    spatial_no_expid = spatial_df.drop(columns=["experiment_id"], errors="ignore")
    merged = merged.merge(spatial_no_expid, on="Room_ID", how="left")

    # ---- Drop rows with no anchor keys ----
    before = len(merged)
    merged = merged.dropna(subset=["Room_ID", "Subject_ID"])
    dropped = before - len(merged)
    if dropped:
        logger.warning("Dropped %d rows with NaN Room_ID or Subject_ID.", dropped)

    # ---- One-hot encode categorical variables ----
    cat_cols = {
        "Type_of_Space": ["Bedroom", "Living Room", "Workplace",
                          "Classroom", "Cafeteria", "Unspecified"],
        "Day_or_Night": ["Day", "Night", "Unspecified"],
        "gender": None,      # dynamic from data
    }

    for col, categories in cat_cols.items():
        if col not in merged.columns:
            logger.warning("Categorical column '%s' not found — skipping OHE.", col)
            continue
        merged[col] = merged[col].fillna("Unspecified")
        if categories is not None:
            dummies = pd.get_dummies(
                pd.Categorical(merged[col], categories=categories),
                prefix=col
            )
        else:
            dummies = pd.get_dummies(merged[col], prefix=col)
        merged = pd.concat([merged.drop(columns=[col]), dummies], axis=1)

    logger.info("Grand Join complete: %d rows × %d columns.", *merged.shape)
    return merged


# ===========================================================================
# Public API
# ===========================================================================

def get_raw_eeg_path(experiment_id: int, eeg_filename: str) -> Path:
    """Resolve the full path to a raw EEG CSV file."""
    return _RAW_DIR / f"experiment_{experiment_id:02d}" / eeg_filename.strip()
