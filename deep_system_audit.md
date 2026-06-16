# Deep System Audit — Predictive Atmospheres Mark 3
**Audit Date:** 2026-06-15  
**Auditor:** Antigravity (Principal Systems Architect Mode)  
**Version:** 0.2.0  
**Status:** UNVARNISHED BASELINE — read-only, no code was modified

---

## 1. Architectural Integrity Check

### 1.1 Boundary Definition

| Layer | Path | Role |
|---|---|---|
| **Headless ML Backend** | `src/` | Data loading, signal processing, model training, prediction, optimization |
| **Streamlit UI** | `frontend/` | Visualization, user input, session state management |

### 1.2 Boundary Violations — What Was Found

**VIOLATION 1 — `src/models/train.py` imports Streamlit directly (Line 592)**  
The `Trainer` class itself is fully headless and correct. However, the convenience wrapper `train_models_streamlit()` — which lives in `train.py` — contains a hard `import streamlit as st` inside the function body. This is a deliberate architectural compromise (thin wrapper, local import), not a module-level contamination. It is **tolerable but technically a violation** of the "src/ must have zero Streamlit dependencies" rule.

```python
# src/models/train.py, line 592
def train_models_streamlit(model_type=None, feature_mode=None) -> TrainResult:
    import streamlit as st   # ← Streamlit inside src/
    ...
```

**VIOLATION 2 — `src/utils/cache_manager.py` performs a lazy Streamlit import (Lines 31–36)**  
`_get_streamlit()` does a try/except `import streamlit as st` at runtime. The intent is graceful degradation, but the file belongs to `src/` and carries an ambient Streamlit dependency.

**CLEAN — All other `src/` modules**  
`src/data/preprocessing.py`, `src/data/emotion_engine.py`, `src/data/data_loader.py`, `src/services/prediction_service.py`, `src/services/optimization_service.py`, `src/services/neural_processing_service.py`, `src/services/container.py`, `src/config.py` — **zero Streamlit imports**, fully headless.

**CLEAN — Frontend does not execute raw ML math**  
`frontend/ui/` reads from `st.session_state` (which holds trained models) and calls `src.services.*`. The one exception is `frontend/ui/spatial_insights.py` which instantiates a `RandomForestRegressor` directly (lines 331–335) **for a visualization-only feature importance analysis** on the loaded parquet data. This is a legitimate UI-side computation, not backend logic leaking in.

**EXCEPTION — `frontend/ui/design_studio.py` line 281–288: raw PyTorch inference fallback**  
In the `else` branch (when `services` is `None`), the UI calls `model(input_tensor)` directly. This is a safe fallback path guarded by `if services is None`, but it means the frontend can bypass the service layer.

---

## 2. The True Data Pipeline

### 2.1 Raw Data Structure

```
data/
├── metadata/
│   ├── Subject Data.csv                        (subject demographics)
│   ├── experiment_01_biometric data.csv         (Subj A-D, no V/A scores)
│   ├── experiment_01_spatial data.csv
│   ├── experiment_02_biometric data.csv         (Subj A-D, V/A scores present)
│   ├── experiment_02_spatial data.csv
│   ├── experiment_03_biometric data.csv         (Subj M, V/A scores, Sleep Hours)
│   └── experiment_03_spatial data.csv
├── raw/
│   ├── experiment_01/                           (50 CSV files: Subj_A/B/C/D/M)
│   ├── experiment_02/
│   └── experiment_03/
└── processed/
    └── fusion_analysis.parquet                  (the ground-truth training dataset)
```

**Raw CSV format:** Each file is a multi-channel recording at 256 Hz.  
Channel mapping (confirmed uniform across all experiments):
- `Channel1` → EEG Right Frontal (F4)
- `Channel2` → EEG Left Frontal (F3)
- `Channel3` → ECG

### 2.2 Execution Path: Raw CSV → Fusion Parquet

**Entry point:** `src/data/emotion_engine.py` → `run_fusion_pipeline(merged_df)`

**Step 1 — Grand Join (`src/data/data_loader.py`)**
1. `load_biometric_df()` — reads all 3 `experiment_XX_biometric data.csv` files, normalizes column names, imputes missing Sleep Hours with dataset median, fills Valence/Arousal with `np.nan` for Exp 01
2. `load_spatial_df()` — reads all 3 `experiment_XX_spatial data.csv` files, drops banned columns (`UDI`, `sDA`, `ASE`), renames to canonical names via `SPATIAL_COLS` dict, imputes continuous features with `0.0` and categorical with `"Unspecified"`
3. Join: `bio_df.merge(subject_df, on="Subject_ID", how="left")` then `.merge(spatial_no_expid, on="Room_ID", how="left")`
4. One-hot encode: `Type_of_Space` → 6 columns, `Day_or_Night` → 3 columns, `gender` → dynamic columns

**Step 2 — Per-Trial EEG/ECG Extraction (`src/data/emotion_engine.py`)**

For each row in the merged DataFrame:

**EEG — FAA Computation:**
```
_extract_biometrics() → _compute_faa(ch_right, ch_left)
  1. Truncate to first 50s: signal[:50*256] = signal[:12800 samples]
  2. High-pass filter: Butterworth order=4, cutoff=1.0Hz
  3. Welch PSD on each channel: fs=256, nperseg=min(256, len(sig))
  4. Mask f >= 2.0 Hz to exclude sub-2Hz leakage
  5. Relative Alpha Power = Alpha_power / total_5_band_power
  6. FAA = ln(α_right) - ln(α_left), clipped to [-1, 1]
```

**ECG — RMSSD Computation:**
```
_extract_biometrics() → _compute_rmssd(ch_ecg)
  1. Truncate to first 50s: ch_ecg[:12800]
  2. Band-pass filter: SOS Butterworth order=4, [0.5Hz, 5.0Hz]
  3. R-peak detection: find_peaks(), height_threshold=75th percentile of |filtered|
     min_distance = int(256 * 0.4) = 102 samples = 400ms gap (max 150 BPM)
  4. RR intervals: np.diff(peaks) / 256 * 1000 → ms
  5. Valid RR filter: 300ms <= rr <= 1200ms (50–200 BPM physiological range)
  6. Successive diffs: np.diff(valid_rr)
  7. Outlier mask: |diff| < 150ms
  8. RMSSD = sqrt(mean(valid_diffs^2)) in ms
```

**Arousal Mapping from RMSSD:**
```
Arousal = clip(1.0 - (RMSSD_ms / 50.0), -1, 1)
  Baseline = 50ms (RMSSD_BASELINE_MS constant, hardcoded in emotion_engine.py line 35)
  High HRV (relaxed) → low arousal
  RMSSD = 50ms → Arousal = 0.0 (neutral)
  RMSSD = 100ms → Arousal = -1.0 (max calm)
  RMSSD = 0ms → Arousal = +1.0 (max stressed)
```

**Step 3 — Multimodal Affective Fusion (`_fuse()` function)**

```
α = 0.6  (ALPHA_DEFAULT constant, emotion_engine.py line 33, also in config.py FusionConfig.alpha)

If Subjective scores are NOT NaN (Experiments 02, 03):
  Target_Valence = 0.6 × FAA + 0.4 × Subjective_Valence
  Target_Arousal = 0.6 × RMSSD_Arousal + 0.4 × Subjective_Arousal
  Δ_Valence      = FAA - Subjective_Valence
  Δ_Arousal      = RMSSD_Arousal - Subjective_Arousal
  Euclidean_Δ    = sqrt(Δ_V² + Δ_A²)

If Subjective scores ARE NaN (Experiment 01 — no V/A scores):
  Target_Valence = 1.0 × FAA         (α forced to 1.0)
  Target_Arousal = 1.0 × RMSSD_Arousal
  delta_* = None, euclidean_distance = None
```

**Step 4 — Derived Spatial Features (`_add_derived_features()`)**

Computed after fusion, added to the parquet:
```
Length_to_Width_Ratio  = Length_m / (Width_m + 1e-9)
Floor_Area_m2          = Length_m × Width_m
Wall_Area_m2           = 2 × (Length_m + Width_m) × Height_m
Volume_m3              = Length_m × Width_m × Height_m
Door_to_Wall_Ratio     = Door_Area_m2 / Wall_Area_m2
Window_to_Wall_Ratio   = Window_Area_m2 / Wall_Area_m2
Walkable_to_Floor_Ratio = Walkable_Floor_Area_m2 / Floor_Area_m2
```
All denominators are guarded with `.replace(0, 1e-9)`.

**Output:** `data/processed/fusion_analysis.parquet` — one row per trial with ~35+ columns.

### 2.3 Preprocessing Module (`src/data/preprocessing.py`) — Parallel / Legacy Path

This module has its **own independent preprocessing pipeline** that is slightly different from `emotion_engine.py`:

| Concern | `preprocessing.py` | `emotion_engine.py` |
|---|---|---|
| Truncation | T+10s to T+60s (drops first 10s) | T+0 to T+50s (NO 10s drop) |
| Band definitions | Gamma: 30–100 Hz | Same |
| Delta low bound | 2.0 Hz | Same |
| ECG bandpass | 0.5–5.0 Hz | Same |
| ECG strict length check | Yes — raises `ValueError` if not exactly 50s | No — fallback |

**Critical discrepancy:** `preprocessing.py:temporal_truncation()` drops the first 10 seconds and keeps T+10s to T+60s (50s window). `emotion_engine.py:_truncate_50s()` takes `signal[:50*256]` — i.e., T+0 to T+50s with NO 10-second drop. **These are not the same 50-second window.** The actual training pipeline uses `emotion_engine.py` (confirmed by `run_fusion_pipeline`). The `preprocessing.py` truncation is only used by `neural_processing_service.py` → `process_eeg` (live signal analysis path).

---

## 3. Machine Learning Reality

### 3.1 Models Actually Wired Into Training

| Model | Class | Source File | Instantiated in `_fit()`? |
|---|---|---|---|
| **SpatialFFNN** | `SpatialFFNN` | `src/models/architectures.py` | ✅ Yes — `model_type == 'PyTorch FFNN'` |
| **SpatialMLP** | `SpatialMLP` | `src/models/architectures.py` | ✅ Yes — `model_type == 'PyTorch MLP'` AND in `_write_full_mode_reports()` for baseline comparison |
| **Random Forest** | `sklearn Pipeline` | `src/models/sklearn_models.py` | ✅ Yes — `model_type == 'Random Forest'` |
| **Ridge Regression** | `sklearn Pipeline` | `src/models/sklearn_models.py` | ✅ Yes — `model_type == 'Ridge Regression'` |

**Default:** `Config.model.default_model_type = 'PyTorch FFNN'`, `Config.training.default_feature_mode = 'full'`

### 3.2 Dead Code — Models Defined but Never Used in Production Training

| Entity | Location | Status |
|---|---|---|
| `PyTorchAdapter` class | `src/models/adapters.py` | **DEAD** — never instantiated anywhere. `train.py` uses `ModelAdapter` (from `adapter.py`), not this class. |
| `SKLearnAdapter` class | `src/models/adapters.py` | **DEAD** — same. `train.py` uses `ModelAdapter`. |
| `SklearnModelWrapper` class | `src/models/sklearn_models.py` | **DEAD** — defined but `get_random_forest_model()` and `get_ridge_model()` return raw `sklearn.pipeline.Pipeline` objects, not `SklearnModelWrapper`. |
| `CognitiveBridge` class | `src/models/cognitive_bridge.py` | **DEAD** — class is defined, instantiated in `__main__` block only. Never called from any service, trainer, or UI page. The `eeg_to_trajectory()` and `map_to_grid()` methods have zero callers in the production codebase. |
| `BaseModelAdapter` ABC | `src/models/adapters.py` | **DEAD** — the abstract class exists but its concrete subclasses are also dead. |
| `NeuroArchitectureOrchestrator` | `src/services/orchestrator.py` | **DEAD** — class is defined and exported but never instantiated or called from `frontend/`, CLI, or tests. |
| `SpaceCapabilityService` | `src/services/space_capability_service.py` | **ZOMBIE** — instantiated in `ServiceContainer` (line 81) but `has_model()` returns False unless a pickle exists at `artifacts/models/space_eval_capability_model.pkl`. This file does not exist. The service silently has no capability and `predict()` raises `FileNotFoundError`. |
| `ModelConfig.cognitive_shared_sizes/cognitive_num_categories` | `src/config.py` | **GHOST** — config fields for a `CognitiveMapMLP` that does not exist anywhere in the codebase. |
| `ModelConfig.eeg_in_channels/eeg_temporal_len/...` | `src/config.py` | **GHOST** — config fields for a `MultiScaleEEGCNN` that does not exist anywhere in the codebase. |

### 3.3 The Adapter Layer — Two Parallel, Incompatible Systems

There are two adapter files that implement the same concept:

**`src/models/adapter.py`** — `ModelAdapter` class (ACTIVE):
- Used by `train.py` (line 338–340)
- Used by `prediction_service.py` (line 106, 215)
- `predict(X, batch=False, return_array=False)` — handles both PyTorch and sklearn

**`src/models/adapters.py`** — `BaseModelAdapter / PyTorchAdapter / SKLearnAdapter` (DEAD):
- Only referenced in `optimization_service.py:gradient_optimize()` (line 347 `from src.models.adapters import PyTorchAdapter`) — but `gradient_optimize()` itself is unreachable in practice because `ServiceContainer` wraps models in `ModelAdapter`, not `PyTorchAdapter`.
- No other callers.

### 3.4 The Exact Feature Vector (Full Mode)

The `Trainer._build_features()` method constructs the feature matrix in alphabetical order (`sorted(feature_df.columns)`). The actual feature set depends on what OHE columns exist in the parquet. Based on `data_loader.py` OHE and `train.py:_build_features()`:

**11 Independent Numeric Features:**
```
CCT_K, Daylight_Factor_pct, Door_Area_m2, Height_m, Illuminance_lux,
Length_m, Num_Doors, Num_Windows, Walkable_Floor_Area_m2, Width_m, Window_Area_m2
```

**2 Day/Night OHE Columns:**
```
Day_or_Night_Day, Day_or_Night_Night
```

**5 Space Type OHE Columns:**
```
Type_of_Space_Bedroom, Type_of_Space_Cafeteria, Type_of_Space_Classroom,
Type_of_Space_Living Room, Type_of_Space_Workplace
```

**Total: 18 features** (sorted alphabetically as the model input vector).  
> **Note:** The `frontend/ui/model_training.py` help text says "20+ parameters" and the docstring of `SpatialFFNN` says "20+ parameters." The actual count is **18** (confirmed by tracing `_build_features()`). The `SpatialFFNN.input_dim` default of `20` is a docstring/default mismatch — the real `input_dim` is determined at runtime from the actual feature count.

**Derived features (`Floor_Area_m2`, `Wall_Area_m2`, `Volume_m3`, `Length_to_Width_Ratio`, `Door_to_Wall_Ratio`, `Window_to_Wall_Ratio`, `Walkable_to_Floor_Ratio`) are NOT in the model input.** They are written to the parquet but `_build_features()` only collects the 11 independent numerics + OHE columns.

**Baseline mode (3 features):** `Height_m`, `Length_m`, `Width_m` — used with `SpatialMLP`.

**StandardScaler** is applied to the full 18-feature matrix before training. The scaler is persisted in `st.session_state.scaler` and applied at inference time in `prediction_service.py`.

---

## 4. Technical Debt & Discrepancy Ledger

### 4.1 Dependency Bloat — Packages in `requirements.txt` Never Imported

The following packages are installed but have **zero import statements** anywhere in `src/` or `frontend/`:

| Package | Version | Status |
|---|---|---|
| `mne` | 1.11.0 | **UNUSED** — no `import mne` anywhere. All EEG processing uses `scipy.signal`. |
| `PyPDF2` | 3.0.1 | **UNUSED** — no import. `pdfminer.six`, `pdfplumber`, `PyMuPDF` (`fitz`), `pypdf` are all also installed. Total of 5 PDF libraries, none confirmed used. |
| `neurokit2` | 0.2.13 | **UNUSED** — no `import neurokit2`. R-peak detection is done manually via `scipy.signal.find_peaks`. |
| `openneuro-py` | 2026.1.0 | **UNUSED** — no import. |
| `gradio` | 6.5.1 | **UNUSED** — no import. UI is 100% Streamlit. |
| `faiss-cpu` | 1.13.2 | **UNUSED** — no import. |
| `sentence-transformers` | 5.2.3 | **UNUSED** — no import. |
| `transformers` | 5.2.0 | **UNUSED** — no import. |
| `huggingface_hub` | 1.4.1 | **UNUSED** — no import. |
| `lightgbm` | 4.6.0 | **UNUSED** — no import. Only RF and Ridge are in `sklearn_models.py`. |
| `xgboost` | 3.2.0 | **UNUSED** — no import. |
| `openai` | 2.24.0 | **UNUSED** — no import. |
| `google-genai` | 1.64.0 | **UNUSED** — no import in project code. |
| `ifcopenshell` | 0.8.4 | **UNUSED** — no import. |
| `seaborn` | 0.13.2 | **UNUSED** — no `import seaborn`. All charts use Plotly. |
| `tensorboard` | 2.20.0 | **UNUSED** — no import. PyTorch training loop does not log to TensorBoard. |
| `PyWavelets` | 1.9.0 | **UNUSED** — no import. |
| `shapely` | 2.1.2 | **UNUSED** — no import. |
| `feedparser` | 6.0.11 | **UNUSED** — no import. |

**Used packages confirmed by source tracing:** `streamlit`, `pandas`, `numpy`, `scipy`, `plotly`, `torch`, `scikit-learn`, `pydantic`, `shap`, `matplotlib` (for SHAP waterfall plot), `pyarrow` (parquet I/O).

### 4.2 Ghost Import — `calculate_stress_index` in `src/neuro_architect.py`

`src/neuro_architect.py` (line 9) exports `calculate_stress_index` from `src.data.emotion_engine`, but **`calculate_stress_index` is not defined anywhere in `emotion_engine.py`**. This will raise an `ImportError` at runtime if `neuro_architect.py` is imported. The `__all__` list also exports it.

```python
# src/neuro_architect.py
from src.data.emotion_engine import process_emotion_engine, calculate_stress_index  # ← ImportError
```

### 4.3 Duplicated Feature Collection Logic

The exact same logic for building a `Dict[str, float]` of independent spatial features from `st.session_state` exists in **two** places:

1. **`frontend/ui/state_utils.py`** → `get_current_features_from_state(config)`
2. **`frontend/ui/design_studio.py`** → `_collect_full_features(config)` (lines 109–158)

These are functionally near-identical. `_collect_full_features` reads the `condition` key (`st.session_state.get('condition', 'Day')`) while `get_current_features_from_state` reads `is_day` (`st.session_state.get('is_day', True)`). They use **different session state keys** for the same concept, meaning they are not interchangeable without a bug. `design_studio.py` uses `_collect_full_features` exclusively; `state_utils.py:get_current_features_from_state` has **zero callers** in the codebase — it is dead utility code.

### 4.4 Debug `print()` Statements Left in Production Training Code

`src/models/train.py` contains two bare `print()` debug statements that will spam stdout on every training run:

```python
# train.py line 319
print(f"DEBUG: Checking model type: {type(model)}, attributes: {dir(model)}")
# train.py line 329
print(f"DEBUG: Checking model type: {type(model)}, attributes: {dir(model)}")
# train.py line 342
print(f"DEBUG DIAGNOSTIC: type={type(adapter)}, dir={dir(adapter)}")
```

### 4.5 Hardcoded Magic Numbers

| Location | Value | Purpose | Risk |
|---|---|---|---|
| `emotion_engine.py:35` | `RMSSD_BASELINE_MS = 50.0` | Neutral HRV reference for arousal mapping | Biologically arbitrary — cited as assumption, not literature value |
| `emotion_engine.py:33` | `ALPHA_DEFAULT = 0.6` | Fusion weight α | Duplicated in `config.py:FusionConfig.alpha = 0.6` — two sources of truth |
| `preprocessing.py:107` | `1.0 / (0.5 * fs)` | High-pass filter Wn | Numerically equivalent to `2.0/fs` — unusual form |
| `preprocessing.py:111` | `"Gamma": (30, 100)` | Gamma band upper bound is 100Hz | But `config.py:EEGConfig.gamma_range = (30, 100)` defines same value — not used by preprocessing |
| `train.py:223` | `test_size=0.2, random_state=42` | Train/val split | Hardcoded, not in `Config` |
| `optimization_service.py:122` | `target_valence = target_score * 1.99 - 0.99` | Maps [0,1] → [-0.99, 1.0] | Not exactly [-1, 1]; target max is 1.0 but min is -0.99, not -1.0. This is a precision bug. |
| `config.py:ModelConfig.default_model_type` | `'PyTorch FFNN'` | Default architecture | Correct, matches `SpatialFFNN` |
| `config.py:TrainingConfig.epochs` | `300` | Training epochs | Not tuned per architecture |
| `config.py:TrainingConfig.learning_rate` | `0.005` | Initial LR | Fixed across all PyTorch models |

### 4.6 Truncation Window Inconsistency (Critical Signal Processing Bug)

**This is a silent data integrity issue.**

| Module | Function | Window Used |
|---|---|---|
| `emotion_engine.py` | `_truncate_50s()` | `signal[0 : 50*256]` = samples 0–12799 (T+0s to T+50s) |
| `preprocessing.py` | `temporal_truncation()` | `signal[10*256 : 60*256]` = samples 2560–15359 (T+10s to T+60s) |

The **training ground-truth is computed on T+0 to T+50s**. The **live signal analysis path (`NeuralProcessingService`)** uses the `preprocessing.py` path which processes T+10s to T+60s. These do not cover the same temporal window of neural data. Any live-mode EEG analysis will be operating on a different segment than what the model was trained on.

### 4.7 `SklearnModelWrapper` vs. Raw Pipeline in `sklearn_models.py`

`get_random_forest_model()` and `get_ridge_model()` return `sklearn.pipeline.Pipeline` objects, NOT `SklearnModelWrapper` instances. However, `SklearnModelWrapper` is defined in the same file and is never used. Inside `train.py`, sklearn models are wrapped by `ModelAdapter(model, framework='sklearn')` after fitting.

The `SklearnModelWrapper.parameters()` yields a dummy gradient tensor — this was clearly written to allow these models to be accidentally passed to a PyTorch optimizer without a crash. This defensive pattern is unnecessary given the current architecture.

### 4.8 `prev_H` Set Twice in `design_studio.py`

```python
# design_studio.py lines 348–351
st.session_state["prev_L"] = length
st.session_state["prev_W"] = width
st.session_state["prev_H"] = height   # line 350
st.session_state["prev_H"] = height   # line 351 — exact duplicate
```

`prev_W` is never written. `prev_H` is written twice. The resize-detection logic (lines 205–208) compares against `prev_L`, `prev_W`, `prev_H` but `prev_W` is never updated, causing the `resized` flag to fire incorrectly on first render (since `prev_W` defaults to the width value at that moment, which is always equal to `width`).

### 4.9 `services/__init__.py` — Exports vs. Reality

```python
# src/services/__init__.py
from src.services.container import ServiceContainer
from src.services.prediction_service import PredictionService
from src.services.optimization_service import OptimizationService
from src.services.neural_processing_service import NeuralProcessingService
```

`SpaceCapabilityService` and `NeuroArchitectureOrchestrator` are **not exported** from `__init__.py` even though they exist in the services package. This is consistent with their dead/zombie status.

### 4.10 `ModelConfig` — Orphaned Configuration Fields

`src/config.py:ModelConfig` contains 8 fields for two models that do not exist:

- `cognitive_shared_sizes`, `cognitive_num_categories` → no `CognitiveMapMLP` class
- `eeg_in_channels`, `eeg_temporal_len`, `eeg_num_t_filters`, `eeg_ratios`, `eeg_dropout` → no `MultiScaleEEGCNN` class

These appear to be planned architectures from an earlier design phase that were never implemented.

---

## 5. Summary Scorecard

| Category | Status | Severity |
|---|---|---|
| `src/` → Streamlit boundary | Mostly clean, 2 soft violations | Low |
| Frontend executes ML math | One guarded fallback path in design_studio | Low |
| Training pipeline integrity | Working end-to-end | Clean |
| FAA computation | Correct: ln(α_R) - ln(α_L), clipped [-1,1] | Clean |
| RMSSD computation | Correct: successive diffs, valid RR filter | Clean |
| Fusion formula | Correct: α=0.6 weighted avg | Clean |
| Truncation consistency | **Mismatch** — training uses T+0–50s, live uses T+10–60s | **High** |
| Dead code (models) | `CognitiveBridge`, `adapters.py` classes, `SklearnModelWrapper` | Medium |
| Dead code (services) | `NeuroArchitectureOrchestrator`, zombie `SpaceCapabilityService` | Medium |
| Ghost import | `calculate_stress_index` in `neuro_architect.py` | **High** (runtime crash) |
| Feature count mismatch | Docs say 20+, actual is 18 | Low |
| Duplicate feature collection | `state_utils.py` dead, `design_studio.py` active | Low |
| Debug print statements | 3 in `train.py` | Low |
| Magic number — α | Defined in 2 places (engine hardcode + config) | Medium |
| Magic number — RMSSD baseline | 50ms hardcoded, no literature citation | Medium |
| Optimization range bug | Max neuro score maps to target_valence=1.0 not 1.0, min maps to -0.99 | Low |
| Unused dependencies | 18+ packages never imported | Medium |
| `prev_H` double-write bug | `prev_W` never updated in design_studio | Low |
