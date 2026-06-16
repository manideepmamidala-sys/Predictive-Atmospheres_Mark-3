# Predictive Atmospheres — Current State Analysis

> **Audit Date:** 2026-05-05  
> **Auditor Role:** Senior Technical Auditor & Codebase Cartographer  
> **Constraint:** Strictly read-only. No improvements, no assumptions. Only what is written in code.

---

## 1. Project Definition

**Predictive Atmospheres** (v0.2.0) is a machine learning system that maps architectural spatial parameters to predicted human emotional states, expressed as Valence (pleasant ↔ unpleasant) and Arousal (calm ↔ excited) on Russell's Circumplex Model. The system ingests raw EEG and ECG biometric recordings collected from human subjects inside physical rooms, processes these signals through a multi-stage pipeline (temporal truncation, Z-score normalization, Welch's PSD, Frontal Alpha Asymmetry for Valence, RMSSD for Arousal), and derives ground-truth emotional targets. A trained neural network then learns to predict these emotional targets from the room's physical features alone — enabling spatial designers to anticipate the affective quality of an unbuilt space without requiring any biometric hardware at inference time.

The application is delivered as a **Streamlit web dashboard** with eight interactive pages (Design Studio, Human Metrics, Spatial Insights, Emotion Landscape, Affective Fusion, Demographic Insights, Environmental Impacts, Model Training) and a parallel **CLI** for headless training and prediction. The Design Studio page provides interactive sliders for 20+ spatial features (geometry, openings, daylight, condition), live affective predictions, and an inverse-design optimizer (differential evolution) that finds room configurations matching a target emotional score. The system supports multiple model architectures (PyTorch FFNN/MLP, scikit-learn Random Forest/Ridge/SVR), auto-discovers experimental datasets via a registry pattern, and includes a service-oriented backend decoupled from the UI (making it theoretically portable to Rhino, APIs, or other interfaces).

---

## 2. Directory Map

```
Predictive Atmospheres_Mark 3/
├── .github/                          # CI/CD pipeline definitions
├── data/
│   ├── metadata/
│   │   ├── experiment_01_biometric data.csv    # Subject/Room/EEG mappings (Exp 01)
│   │   ├── experiment_01_spatial data.csv      # Room dimensions (Exp 01)
│   │   ├── experiment_02_biometric data.csv    # Subject/Room/EEG mappings (Exp 02)
│   │   ├── experiment_02_spatial data.csv      # Extended spatial features (Exp 02)
│   │   ├── experiment_03_biometric data.csv    # Subject/Room/EEG mappings (Exp 03)
│   │   └── experiment_03_spatial data.csv      # Extended spatial features (Exp 03)
│   ├── raw/
│   │   ├── experiment_01/            # Raw EEG CSV recordings (Subj_*.csv)
│   │   ├── experiment_02/            # Raw EEG CSV recordings (Subj_*.csv)
│   │   └── experiment_03/            # Raw EEG CSV recordings (Subj_*.csv)
│   ├── processed/                    # Cached tensors (cached_data.pt, synthetic_data_fallback.pt)
│   └── paper_data/                   # MDS coordinates for CognitiveBridge
│
├── src/
│   ├── app.py                        # Streamlit entry point. Boots ML backend, auto-trains, renders 6 pages.
│   ├── cli.py                        # CLI: `train`, `info`, `predict` subcommands.
│   ├── config.py                     # Centralized dataclass config (EEG, Model, Training, Room, Optimization, Emotion, etc.)
│   ├── neuro_architect.py            # Legacy re-export shim (backward compat only)
│   ├── py.typed                      # PEP 561 marker for type-checking
│   │
│   ├── data/
│   │   ├── data_loader.py            # Two-pass data loading: (1) temporal truncation & grouping, (2) within-subject norm & feature extraction.
│   │   ├── emotion_engine.py         # FAA-based Valence + RMSSD-based Arousal computation. Sliding-window PSD. Emotion distribution.
│   │   ├── preprocessing.py          # Temporal truncation, Z-score norm, Welch's PSD band extraction, ECG R-peak/HRV/RMSSD analysis.
│   │   └── experiment_registry.py    # Auto-discovers experiment_XX folders via glob on metadata CSVs.
│   │
│   ├── models/
│   │   ├── architectures.py          # MultiScaleEEGCNN, SpatialMLP, SpatialFFNN, CognitiveMapMLP definitions.
│   │   ├── train.py                  # Trainer class (FFNN/MLP/RF/Ridge). Full-feature dataset builder. Reports. Streamlit wrapper.
│   │   ├── cognitive_bridge.py       # MDS-space trajectory mapping. 13-category cognitive map. TEM grid discretization.
│   │   ├── sklearn_models.py         # SklearnModelWrapper (RandomForest, Ridge, SVR) with PyTorch-like interface.
│   │   ├── adapter.py                # ModelAdapter wrapping PyTorch and scikit-learn interfaces (MC Dropout, SHAP).
│   │   └── adapters.py               # Legacy model adapters (deprecated).
│   │
│   ├── services/
│   │   ├── __init__.py               # Public API exports.
│   │   ├── container.py              # ServiceContainer: lazy DI for Prediction, Optimization, Neural, SpaCE services.
│   │   ├── orchestrator.py           # NeuroArchitectureOrchestrator: EEG → Optimization → Prediction pipeline.
│   │   ├── prediction_service.py     # predict(L,W,H) and predict_full(features_dict). Emotion weight computation.
│   │   ├── optimization_service.py   # Differential evolution, Monte Carlo, gradient-based room optimization.
│   │   ├── neural_processing_service.py  # Wraps emotion_engine + preprocessing for EEG/ECG processing.
│   │   └── space_capability_service.py   # SpaCE capability model (SR/CK/EI) from pickled sklearn model.
│   │
│   ├── ui/
│   │   ├── theme.py                  # Dark-mode CSS, PALETTE dict, style_figure helper, render_hero/panel_header components.
│   │   ├── state_utils.py            # Centralized full-feature extraction from st.session_state.
│   │   ├── base_visualization.py     # ABC for visualization pages (load_data → process_data → build_charts).
│   │   ├── data_utils.py             # Data loading and formatting utilities.
│   │   ├── design_studio.py          # Interactive room design + live prediction + inverse optimization + affective map.
│   │   ├── human_metrics.py          # Population-level EEG/ECG biometric analytics (stress, HR, HRV, PSD).
│   │   ├── spatial_insights.py       # Correlation analysis: feature vs NeuroScore scatterplots + heatmap.
│   │   ├── emotion_landscape.py      # 3D spatial distribution, V-A density field, volume quartile analysis.
│   │   ├── affective_fusion.py       # Multimodal affective fusion visualization (EEG/ECG vs Subjective).
│   │   ├── demographic_insights.py   # Analysis of demographic features (e.g., Gender, Sleep Hours).
│   │   ├── environmental_impacts.py  # Environmental metric evaluation.
│   │   └── model_training.py         # Training convergence viewer, architecture info, retrain controls.
│   │
│   ├── core/
│   │   └── data/
│   │       └── validators.py         # Pydantic models: RoomDimensions, EEGSignal validation.
│   │
│   ├── utils/
│   │   ├── cache_manager.py          # CacheManager with memory + disk pickle caching. Streamlit/standalone dual-mode.
│   │   └── rendering.py              # 3D room cuboid renderer + 2D affective map (quadrant chart) in Plotly.
│   │
│   └── test/                         # 10 test files covering emotion engine, cognitive bridge, validators, services, etc.
│
├── artifacts/                        # Generated reports (model_comparison.json, training_findings.md, etc.)
├── pyproject.toml                    # Package definition, dependencies, mypy/pytest config
├── requirements.txt                  # Flat dependency list (mirrors pyproject.toml + supplemental tools)
├── Dockerfile                        # Docker image for Streamlit deployment
├── GEMINI.md                         # AI assistant context rules
└── README.md                         # Project overview documentation
```

---

## 3. Data Pipeline Reality

### 3.1 Raw Data Format
- **3-channel CSV files** (`Channel1`, `Channel2`, `Channel3`): Channels 1 & 2 are EEG (Right Frontal, Left Frontal), Channel 3 is ECG.
- **Sampling rate:** 256 Hz (configured in `EEGConfig.sample_rate`).
- **3 experiment datasets** discovered: `experiment_01`, `experiment_02`, `experiment_03`.

### 3.2 Preprocessing Pipeline (as written in `preprocessing.py`)

#### Step 1: Temporal Truncation
```
File: src/data/preprocessing.py → temporal_truncation()

Formula:
    start_idx = int(start_sec × fs)    # Default: start_sec = 10
    end_idx   = int(max_sec × fs)      # Default: max_sec = 60

    truncated_signal = signal[start_idx : min(len(signal), end_idx)]

Effect: Drops first 10 seconds (VR Orienting Reflex artifact),
        keeps samples from T+10s to T+60s maximum.
        Resulting window: exactly 50 seconds (12,800 samples at 256 Hz).
```

#### Step 2: Z-Score Normalization
```
File: src/data/preprocessing.py → zscore_normalize()

Formula:
    Z = (x - μ) / (σ + 1e-6)

Where:
    μ = global_mean (per-subject mean across all trials) OR signal mean
    σ = global_std  (per-subject std across all trials)  OR signal std
    ε = 1e-6 (epsilon to prevent division by zero)
```

#### Step 3: Within-Subject Normalization (in `data_loader.py`)
```
File: src/data/data_loader.py → _load_data_impl()

Pass 1: Group all trials by Subject_ID, apply temporal truncation per-channel.
Pass 2: For each subject, concatenate ALL trials to compute:
    global_mean_ch = np.mean(all_trials_channel_N)
    global_std_ch  = np.std(all_trials_channel_N)
Then normalize each trial's channels using these subject-level statistics.
```

### 3.3 EEG Feature Extraction (as written in `emotion_engine.py`)

#### Band Power Extraction (Welch's Method)
```
File: src/data/emotion_engine.py → process_emotion_engine()

Sliding Window PSD:
    window_size = fs (= 256 samples = 1 second)
    step_size   = max(fs // 2, 1) = 128 samples (50% overlap)
    num_windows = max((len(signal) - window_size) // step_size + 1, 1)

For each window:
    f, Pxx = scipy.signal.welch(chunk, fs=fs, nperseg=max(len(chunk)//2, 8))

Frequency Bands:
    Delta:  0.5 –   4 Hz
    Theta:    4 –   8 Hz
    Alpha:    8 –  13 Hz
    Beta:    13 –  30 Hz
    Gamma:   30 – 100 Hz

Band Power = np.trapezoid(Pxx[mask], f[mask])   (trapezoidal integration)
```

#### Valence Computation — Frontal Alpha Asymmetry (FAA)
```
File: src/data/emotion_engine.py → process_emotion_engine()

Per sliding window:
    alpha_R = max(band_powers_right['Alpha'], 1e-6)
    alpha_L = max(band_powers_left['Alpha'], 1e-6)

    FAA = ln(alpha_R) - ln(alpha_L)

    Valence = clip(FAA, -1.0, 1.0)

Final Valence = mean of all window Valence values.
```

#### Arousal Computation — ECG RMSSD
```
File: src/data/emotion_engine.py → process_emotion_engine()
      src/data/preprocessing.py → analyze_ecg()

ECG Processing:
    1. Temporal truncation (T+10s to T+60s)
    2. Validation: signal must be exactly 50 seconds (12,800 samples)
    3. Bandpass filter: 0.5 – 40 Hz (Butterworth, order 4)
    4. Z-score normalize for consistent peak detection
    5. R-peak detection: scipy.signal.find_peaks(height=1.5, distance=0.4×fs)
    6. RR intervals = np.diff(peaks) / fs  (in seconds)
    7. BPM = 60 / mean(RR_intervals)
    8. RMSSD = sqrt(mean(diff(RR_intervals)²)) × 1000  (in milliseconds)

Arousal Mapping:
    Arousal = clip(1.0 - (RMSSD / 50.0), -1.0, 1.0)

    Interpretation:
        Higher RMSSD → parasympathetic dominance → lower arousal
        Lower RMSSD  → sympathetic dominance    → higher arousal
        Baseline assumption: ~50 ms RMSSD = neutral (0 arousal)
```

#### Stress Index (auxiliary)
```
File: src/data/emotion_engine.py → calculate_stress_index()

Formula:
    ratio = Beta / (Alpha + 1e-6)
    stress = 1 / (1 + exp(-(ratio - 1.0) × 3))    (sigmoid normalization)

Output: probability of stress (0.0 to 1.0)
```

### 3.4 Probabilistic Emotion Distribution
```
File: src/data/emotion_engine.py → process_emotion_engine()

Given final (avg_valence, avg_arousal) and 13 emotion centroids:

For each emotion:
    dist = sqrt((V - centroid_x)² + (A - centroid_y)²)
    weight = exp(-dist × decay)    # decay = 8.0 (from config)

Normalized:
    probability(emotion) = weight / sum(all_weights) × 100.0%

13 Emotion Centroids (from config):
    Anger:            (-0.7,  0.7)     Anxiety:      (-0.4,  0.6)
    Fear:             (-0.6,  0.8)     Surprise:     ( 0.3,  0.8)
    Guilt:            (-0.5,  0.3)     Disgust:      (-0.6,  0.4)
    Sad:              (-0.7, -0.4)     Regard:       ( 0.3,  0.2)
    Satisfaction:     ( 0.7, -0.3)     WarmHeartedness: (0.6, -0.2)
    Happiness:        ( 0.8,  0.5)     Pride:        ( 0.7,  0.6)
    Love:             ( 0.8,  0.3)
```

### 3.5 Target Coordinate Extraction
```
File: src/data/data_loader.py → _extract_target_coords()

Priority:
    1. Use "Valence Score by Subject" for valence, "Arousal Score by Subject" for arousal (from metadata CSV)
    2. Fallback: Use "Score by Subject" for both valence AND arousal
    3. Final fallback: Use EEG-derived values (mean of FAA trajectory for V, global RMSSD arousal for A)
```

### 3.6 Full-Feature Dataset Construction
```
File: src/models/train.py → _load_full_feature_dataset()

Feature Engineering:
    1. Merge biometric + spatial metadata CSVs per experiment
    2. Handle column name aliases (e.g., "Length (meter)" vs "Length (m)")
    3. One-hot encode "Day or Night" → "Day or Night_Day", "Day or Night_Night"
    4. Fill NaN with median per column
    5. Replace ±Inf with NaN → 0.0
    6. Apply StandardScaler (mean=0, std=1) across all features

Feature Categories (from SpatialFeatureConfig):
    Geometry:  Length, Width, Height, L:W Ratio, Wall Area, Floor Area, Volume
    Openings:  Door count, Door area, Door ratio, Window count, Window area, Window ratio
    Daylight:  Daylight Factor, Illuminance, UDI, sDA, ASE, CCT
    Condition: Day or Night, Type of Space (one-hot)
    Demographics: Gender (one-hot)
```

---

## 4. Machine Learning Reality

### 4.1 Model Architectures (all defined in `architectures.py`)

#### SpatialFFNN (DEFAULT — `PyTorch FFNN`)
```
Purpose: Predicts (Valence, Arousal) from 20+ extended spatial features.
Status:  IMPLEMENTED. Used as default model for full-feature mode.

Architecture:
    Input(D) → Linear(D, 64) → BatchNorm(64) → ReLU → Dropout(0.3)
             → Linear(64, 128) → BatchNorm(128) → ReLU → Dropout(0.2)
             → Linear(128, 64) → BatchNorm(64) + RESIDUAL from Layer 1
             → ReLU → Dropout(0.1)
             → Linear(64, 32) → ReLU → Linear(32, 2) → Tanh

Output: 2 values in [-1, 1] (Valence, Arousal)
Default input_dim: 20
Residual connection: Layer 1 output added to Layer 3 (pre-activation)
```

#### SpatialMLP (LEGACY — `PyTorch MLP`)
```
Purpose: Predicts (Valence, Arousal) from basic room dimensions.
Status:  IMPLEMENTED. Available as alternative / baseline comparator.

Architecture:
    Input(D) → Linear(D, 16) → ReLU
             → Linear(16, 32) → ReLU
             → Linear(32, 2) → Tanh

Output: 2 values in [-1, 1]
Default input_dim: 3
```

#### MultiScaleEEGCNN
```
Purpose: EEG-based emotion recognition from raw temporal signals.
Status:  IMPLEMENTED (class defined). NOT USED in any active training pipeline.

Architecture:
    Input(3, 500) → 5× Multi-scale T-kernels (Conv1d, ratios: [0.5, 0.25, 0.125, 0.0625, 0.03125])
                  → Concatenate → AvgPool1d(2)
                  → Spatial Global Conv1d(40→16, k=3) + Spatial Hemisphere Conv1d(40→16, k=1)
                  → Fusion Conv1d(32→24, k=3)
                  → Flatten → Dropout(0.3) → Linear(24×250, 64) → ReLU
                  → Dropout(0.2) → Linear(64, 2)

Note: This model is defined but never instantiated in train.py or any training loop.
```

#### CognitiveMapMLP
```
Purpose: Dual-head prediction of 13 emotion categories + 2D affective space.
Status:  IMPLEMENTED (class defined). NOT USED in any active training pipeline.

Architecture:
    Input(D) → Shared: Linear(D, 32) → ReLU → Linear(32, 64) → ReLU
    Branch 1 (Categories): Linear(64, 32) → ReLU → Linear(32, 13) → Softmax
    Branch 2 (Affective):  Linear(64, 16) → ReLU → Linear(16, 2)  → Tanh

Note: Referenced in evaluation code (dict output handling) but no training path exists.
```

### 4.2 Scikit-Learn Models (defined in `sklearn_models.py`)

#### Random Forest Regressor
```
Status:  IMPLEMENTED. Available via model selector.
Pipeline: StandardScaler → MultiOutputRegressor(RandomForestRegressor(n_estimators=100, random_state=42))
Wrapper:  SklearnModelWrapper (provides PyTorch-like __call__, eval(), train() interface)
```

#### Ridge Regression
```
Status:  IMPLEMENTED. Available via model selector.
Pipeline: StandardScaler → MultiOutputRegressor(Ridge(alpha=1.0))
Wrapper:  SklearnModelWrapper
```

### 4.3 Loss Functions & Optimizers

| Component | Value |
|---|---|
| **Loss Function** | `nn.MSELoss()` (Mean Squared Error) — used for both FFNN and MLP |
| **Optimizer** | `optim.Adam` — FFNN uses `weight_decay=1e-4`, MLP uses default |
| **Learning Rate** | 0.005 (default from `TrainingConfig`) |
| **LR Scheduler** | `ReduceLROnPlateau(mode='min', factor=0.5, patience=25)` |
| **Epochs** | 300 (default) |
| **Train/Val Split** | 80/20 via `sklearn.train_test_split(random_state=42)` |
| **Convergence Check** | `abs(loss[-1] - loss[-window]) < threshold`, window=20, threshold=0.001 |

### 4.4 Evaluation Metrics (computed in `train.py`)
```
For both train and validation sets:
    MSE       = mean((predictions - targets)²)
    MAE       = mean(|predictions - targets|)
    R²        = 1 - (SS_res / (SS_tot + 1e-6))
    RMSE      = sqrt(MSE)
    Valence_MAE  = mean(|pred_v - target_v|)
    Arousal_MAE  = mean(|pred_a - target_a|)
```

### 4.5 Feature Importance
```
File: src/models/train.py → _compute_feature_importance()

For Random Forest: sklearn.inspection.permutation_importance(n_repeats=10, scoring='neg_mean_absolute_error')
For PyTorch:       Manual permutation — shuffle column i, measure MAE delta vs baseline.
```

### 4.6 Model Validation Sanity Check
```
File: src/models/train.py → _validate_model()

Probe: Two fixed input vectors passed through the model.
Check: No NaN/Inf outputs. All outputs within [-2.0, 2.0] range.
```

### 4.7 Model Adapters (in `adapter.py`)
```
ModelAdapter — Unified wrapper for PyTorch and scikit-learn models. Provides `predict`, `predict_mc_dropout` (for uncertainty and confidence scoring), and `explain_prediction` (via SHAP).
```

### 4.8 Optimization Algorithms (in `optimization_service.py`)

| Method | Status | Details |
|---|---|---|
| **Differential Evolution** | IMPLEMENTED (default) | `scipy.optimize.differential_evolution`, maxiter=35, popsize=10, polish=True |
| **Full-Feature DE** | IMPLEMENTED | maxiter=50, popsize=15, optimizes across all non-fixed spatial features |
| **Monte Carlo Sampling** | IMPLEMENTED (fallback) | Random uniform sampling within dimension bounds, N=2000 default |
| **Gradient-Based** | IMPLEMENTED | Adam optimizer on input dims with `torch.no_grad` clamping, max_iterations=100 |
| **V-A Joint Optimization** | IMPLEMENTED | Monte Carlo with Euclidean distance to (target_V, target_A) |

### 4.9 SpaCE-Eval Integration

| Component | Status |
|---|---|
| **SpaCEEvalHeuristics** | REMOVED. `space_eval_integration.py` was deleted during project recalibration to ML constraints. |
| **SpaceCapabilityService** | IMPLEMENTED. Loads a pickled sklearn model from `artifacts/models/`. Model file may or may not exist at runtime. |

---

## 5. Dependencies

### 5.1 Core Runtime Stack

| Library | Version Constraint | Role |
|---|---|---|
| **Python** | ≥ 3.9 | Runtime |
| **PyTorch** | ≥ 2.1.0 | Neural network architectures, tensor operations, model training |
| **scikit-learn** | ≥ 1.3.0 | Random Forest, Ridge, StandardScaler, train_test_split, permutation_importance |
| **Streamlit** | ≥ 1.31.0 | Web application framework (UI) |
| **Pandas** | ≥ 2.1.0 | Data loading, CSV parsing, DataFrame operations |
| **NumPy** | ≥ 1.26.0 | Numerical computation, array operations |
| **SciPy** | ≥ 1.11.0 | Welch's PSD, Butterworth filters, peak detection, differential_evolution |
| **Plotly** | ≥ 5.18.0 | All charts (3D rooms, affective maps, radar, scatter, bar, heatmap) |
| **MNE-Python** | ≥ 1.6.0 | Listed as dependency but **NOT directly imported in any source file** |
| **Pydantic** | ≥ 2.8.0 | Data validation (RoomDimensions, EEGSignal models) |

### 5.2 Supplemental Tools (in requirements.txt only)

| Library | Role |
|---|---|
| **PyPDF2** | PDF extraction (used by knowledge/literature scripts) |
| **matplotlib** | Supplemental visualization (not used in main app) |
| **seaborn** | Supplemental visualization (not used in main app) |

### 5.3 Dev Dependencies

| Library | Role |
|---|---|
| **pytest** ≥ 7.4.0 | Test framework |
| **flake8** ≥ 6.1.0 | Linter |
| **mypy** ≥ 1.11.0 | Static type checker |

### 5.4 Infrastructure

| Component | Details |
|---|---|
| **Build System** | setuptools ≥ 61.0 + wheel |
| **Dockerfile** | python:3.9-slim, exposes port 8501 |
| **CI** | GitHub Actions (`.github/workflows/ci.yml`) |

---

## 6. Key Observations (facts only, no suggestions)

| # | Observation |
|---|---|
| 1 | **MultiScaleEEGCNN** is fully defined (297 lines) but has zero active call sites — it is never instantiated in `train.py` or any training path. |
| 2 | **CognitiveMapMLP** is defined and its dict output is handled in evaluation code, but no training loop exists for it. |
| 3 | **ONNXAdapter** is implemented but no ONNX export/conversion code exists anywhere in the codebase. |
| 4 | **MNE-Python** is declared as a dependency (both pyproject.toml and requirements.txt) but is **not imported** in any source file under `src/`. |
| 5 | The CLI `predict` command always trains a `PyTorch MLP` in `baseline` mode before predicting, regardless of what models are available. |
| 6 | The ECG `analyze_ecg()` function enforces **exactly 50 seconds** (12,800 samples) post-truncation and raises `ValueError` otherwise. |
| 7 | Three experiment datasets exist (`experiment_01`, `experiment_02`, `experiment_03`) with paired biometric + spatial metadata CSVs. |
| 8 | `state_utils.py` and `design_studio.py` both contain `_collect_full_features` / `get_current_features_from_state` with overlapping logic — the `state_utils.py` version is missing UDI, sDA, and ASE features that are present in `design_studio.py`. |
| 9 | `NeuroKnowledgeBase` and all documentation (`docs/`, `scripts/`, `knowledge/`) were recently purged from the codebase during recalibration to strict ML constraints. |
| 10 | The default training mode is `full` features with `PyTorch FFNN`, auto-triggered on first Streamlit launch. |
