# Project Context

Predictive Atmospheres is a pilot research platform for describing experiences of rendered architectural rooms with approximate bilateral forehead EEG, wrist ECG and self-report. Thirty rooms, ten subject IDs and 160 recordings span three experiments. The owner-reported protocol and source caveats are documented in `docs/protocol/`; `docs/specs/analysis-v1.md` governs derived analyses once reviewed.

The replacement backend lives in `backend/src/pa/` and uses Python 3.11, uv, NumPy, SciPy, pandas, scikit-learn, Pydantic and FastAPI as justified by the scientific specification. It owns ingestion, acquisition audit, signals, affect, room features, modeling, scoring, optimization, research export and the `/v1` API. Source files stay under `data/`; generated results and models live under `artifacts/`.

The React/Vite/TypeScript frontend lives in `frontend/src/`. It reads versioned static research exports for research pages and calls the live API only for the experimental Design Studio. The eight pages are Predictive Atmospheres, The Study, Rooms & Experience, Body & Experience, Prediction & Findings, Design Studio, Data Explorer and Methods & Research Context. Light, Dark and System preferences share a token-based design system.

Use `make setup`, `make verify-data`, `make pipeline`, `make test`, `make site` and `make all` as reproducible entry points. The current Fab change plan owns dependencies and milestones. Original data and renders are checksum preserved; the Python package and React atlas are the active runtime. Local reproduction and release conditions are recorded in `docs/operations.md` and `docs/release-readiness.md`.
