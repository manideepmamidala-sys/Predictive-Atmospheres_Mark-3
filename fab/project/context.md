# Project Context

## Overview
Predictive Atmospheres is a neuro-architectural machine learning platform inferring human affective states (valence and arousal) from architectural spatial parameters through multimodal fusion of EEG/ECG biometrics and self-reported scores.

## Architecture
- `src/`: Headless ML backend with zero UI dependencies. Contains configuration (`src/config.py`), Pydantic core schemas (`src/core/data/`), ML architectures (`SpatialFFNN`, `SpatialMLP`, scikit-learn ensembles in `src/models/`), and inference/optimization services (`src/services/`).
- `frontend/`: React/Vite SPA (`frontend/`) consuming processed datasets (`data/processed/`) and backend services.
- `api.py`: FastAPI service exposing prediction, optimization, and training endpoints.
- `data/`: Raw EEG/ECG recordings, experiment metadata CSVs, and processed Parquet tensors.

## Tech Stack & Conventions
- **Language**: Python 3.10+
- **Deep Learning / ML**: PyTorch, scikit-learn, joblib
- **Data Engineering**: Pandas, NumPy, PyArrow (Parquet)
- **Signal Processing**: MNE, SciPy (FAA, RMSSD, PSD band-power extraction)
- **API & Validation**: FastAPI, Pydantic v2
- **UI**: React 18, Vite, and Tailwind CSS with custom design tokens and dark theme
- **Testing**: pytest (`tests/`), mypy strict typing
