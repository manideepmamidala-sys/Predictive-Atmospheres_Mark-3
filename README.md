# Predictive Atmospheres

> Neuro-Architectural Design Platform — Machine learning framework that infers human emotional states from architectural spatial features using multimodal affective fusion of EEG/ECG biometrics and self-reported scores.

---

## Architecture

```
Predictive Atmospheres/
├── src/                    ← Headless ML Backend (FastAPI, Scikit-learn, zero UI dependencies)
│   ├── config.py           ← Centralised configuration (EEG, model, training, fusion, spatial)
│   ├── cli.py              ← Command-line interface (train / predict / info)
│   ├── data/               ← Data ingestion, EEG/ECG processing, emotion engine
│   ├── models/             ← SpatialFFNN, SpatialMLP, sklearn wrappers, training loop
│   ├── services/           ← Prediction, optimisation, neural processing services
│   ├── core/data/          ← Pydantic validators (SpatialInput, EEGSignal)
│   └── utils/              ← Caching, 3D rendering helpers
│
├── frontend/               ← React 18 / Vite / Tailwind SPA (Consumes FastAPI)
│   ├── src/ui/             ← Pages: Design Studio, Emotion Landscape, etc.
│   ├── src/components/     ← Reusable Tailwind UI components
│   └── src/store/          ← Zustand state management and API integration
│
├── api.py                  ← FastAPI entry point for all frontend/backend communication
├── data/                   ← Experimental datasets (raw EEG CSVs + metadata)
│   ├── raw/                ← experiment_01/, experiment_02/, experiment_03/
│   ├── metadata/           ← Biometric + spatial CSVs per experiment
│   ├── paper_data/         ← MDS coordinates and emotion ratings for CognitiveBridge
│   └── processed/          ← Cached tensors + fusion_analysis.parquet (Parquet format)
│
└── pyproject.toml          ← Package definition + dependencies
```

**Separation principle:** `src/` is a pure Python ML backend with zero UI imports. `frontend/` is a Vite SPA that consumes the backend as a REST API. The backend can also be imported from CLI, Rhino, or any external system.

---

## Spatial Input Schema

The model accepts exactly **12 independent variables** (+ 1 categorical). All derived features are computed by the backend — the frontend never supplies them.

### Independent Features (raw inputs)

| #   | Feature             | Unit | Range        |
| --- | ------------------- | ---- | ------------ |
| 1   | Length              | m    | 2.0 – 50.0   |
| 2   | Width               | m    | 2.0 – 50.0   |
| 3   | Height              | m    | 2.0 – 10.0   |
| 4   | Number of Doors     | –    | 0 – 10       |
| 5   | Door Area           | m²   | 0 – 30       |
| 6   | Number of Windows   | –    | 0 – 30       |
| 7   | Window Area         | m²   | 0 – 250      |
| 8   | Daylight Factor     | %    | 0 – 20       |
| 9   | Illuminance         | lux  | 0 – 2000     |
| 10  | CCT                 | K    | 2000 – 10000 |
| 11  | Walkable Floor Area | m²   | 0 – 500      |
| 12  | Room Volume         | m³   | 0 – 25000    |

### Categorical Features (one-hot encoded)

| Feature       | Categories                                            |
| ------------- | ----------------------------------------------------- |
| Type of Space | Bedroom, Living Room, Workplace, Classroom, Cafeteria |

### Derived Features (computed by backend)

| Feature                             | Formula                          |
| ----------------------------------- | -------------------------------- |
| Length to Width Ratio               | L / W                            |
| Floor Area                          | L × W                            |
| Wall Area                           | 2(L + W) × H                     |
| Volume                              | L × W × H                        |
| Door Area to Wall Area Ratio        | Door Area / Wall Area            |
| Window Area to Wall Area Ratio      | Window Area / Wall Area          |
| Walkable Floor to Total Floor Ratio | Walkable Floor Area / Floor Area |

**Purged metrics:** UDI (Useful Daylight Illuminance), sDA (Spatial Daylight Autonomy), and ASE (Annual Sunlight Exposure) are permanently excluded from all data paths.

---

## Affective Fusion: Ground-Truth Target Generation

The system uses **multimodal affective fusion** to combine two independent emotional measurements into a single ground-truth target for model training.

### Signal Sources

| Source                       | Method                                             | Axis    |
| ---------------------------- | -------------------------------------------------- | ------- |
| **Objective** (biometric)    | Frontal Alpha Asymmetry (FAA) = ln(α_R) − ln(α_L)  | Valence |
| **Objective** (biometric)    | RMSSD from ECG R-peaks: Arousal = 1 − (RMSSD / 50) | Arousal |
| **Subjective** (self-report) | "Valence Score by Subject" from metadata CSV       | Valence |
| **Subjective** (self-report) | "Arousal Score by Subject" from metadata CSV       | Arousal |

### Fusion Algorithm

Given a tunable parameter **α** (default: 0.6, configurable in `src/config.py → FusionConfig`):

```
Target_Valence = α × FAA_Valence  + (1 − α) × Subjective_Valence
Target_Arousal = α × RMSSD_Arousal + (1 − α) × Subjective_Arousal
```

### Variance Metrics

For each subject/room pair, the pipeline also computes:

```
Δ_Valence = Objective_V − Subjective_V
Δ_Arousal = Objective_A − Subjective_A
Euclidean_Distance = √(Δ_V² + Δ_A²)
```

When subjective scores are unavailable, 100% objective is used (α = 1.0).

All fusion metadata is persisted to `data/processed/fusion_analysis.parquet` and visualised in the **Affective Fusion** tab of the frontend.

---

## Running the Application

### Prerequisites

```bash
pip install -e .          # Production
pip install -e .[dev]     # Development (includes pytest, mypy, flake8)
```

### Launch Backend (FastAPI)

```bash
fastapi dev api.py
```

### Launch Frontend (React SPA)

```bash
cd frontend
npm install
npm run dev
```

Models are trained automatically on first launch or loaded dynamically via joblib. The fusion analysis parquet is generated during training.

### CLI (Headless Backend)

```bash
# Train default model (PyTorch FFNN, full features)
python -m src.cli train

python run_pipeline.py

# Train alternative architecture
python -m src.cli train --model "Random Forest"

# Predict emotional response for a room
python -m src.cli predict 10.0 8.0 3.5

# Dataset info
python -m src.cli info
```

### Docker

```bash
docker build -t predictive-atmospheres .
docker run -p 8501:8501 predictive-atmospheres
```

### Testing

```bash
python -m pytest src/test/ -v
mypy -m src.data.emotion_engine -m src.models.train -m src.core.data.validators
```

---

## Configuration

All parameters are centralised in `src/config.py` using Python dataclasses. Key tunable parameters:

| Parameter                  | Location         | Default      | Description                    |
| -------------------------- | ---------------- | ------------ | ------------------------------ |
| `fusion.alpha`             | `FusionConfig`   | 0.6          | Objective vs subjective weight |
| `training.epochs`          | `TrainingConfig` | 300          | Training iterations            |
| `training.learning_rate`   | `TrainingConfig` | 0.005        | Adam learning rate             |
| `eeg.sample_rate`          | `EEGConfig`      | 256          | EEG sampling frequency (Hz)    |
| `model.default_model_type` | `ModelConfig`    | PyTorch FFNN | Default architecture           |

Environment variable overrides:

- `PREDICTIVE_ATMOSPHERES_LEARNING_RATE`
- `PREDICTIVE_ATMOSPHERES_EPOCHS`
- `PREDICTIVE_ATMOSPHERES_CONFIG` (path to JSON config file)

---

## Technology Stack

| Layer             | Technologies                                       |
| ----------------- | -------------------------------------------------- |
| ML Core           | PyTorch, scikit-learn, NumPy, SciPy                |
| Signal Processing | Welch's PSD, Butterworth filters, R-peak detection |
| Data              | Pandas, Pydantic validation                        |
| API               | FastAPI                                            |
| Frontend          | React 18, Vite, Tailwind CSS, Zustand              |
| Infrastructure    | Docker, GitHub Actions CI                          |
