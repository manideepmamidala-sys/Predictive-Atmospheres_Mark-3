# Intake: Decouple Streamlit + FastAPI — Full Website Deployment

**Change:** `261008-rvq3-decouple-streamlit-fastapi`
**Date:** 2026-10-08
**Type:** refactor

---

## Origin

User-initiated strategic pivot. The React/Vite frontend (`frontend/`) built under `260915-vwf1-migrate-react-frontend` is being abandoned. The existing Streamlit dashboard in `frontend_streamlit_archive/` is fully functional and will be promoted to the primary frontend. The ML backend will be fully decoupled into a standalone FastAPI service. Both will be deployed as always-on cloud services.

---

## Why

1. **The Streamlit archive already works.** All 9 interactive pages (Design Studio, Human Metrics, Spatial Insights, Emotion Landscape, Affective Fusion, Demographic Insights, Environmental Impacts, System Architecture, Model Training) are complete and functional. Maintaining a parallel React rewrite is unnecessary overhead for a thesis project.
2. **The current architecture has boundary violations.** `src/models/train.py` and `src/utils/cache_manager.py` import Streamlit directly. The frontend can bypass the service layer (`design_studio.py` line 281–288 raw PyTorch fallback). A clean API boundary is needed.
3. **The project needs a public-facing website** — not just a local dashboard. This requires an academic landing page, always-on backend hosting, and deployment infrastructure.
4. **The raw experimental data (`data/raw/`, `data/processed/`) must be published to GitHub** for research reproducibility.

---

## What Changes

### 1. Directory Restructure — Remove React, Promote Streamlit

- **Delete** `frontend/` (the React/Vite/Tailwind SPA) entirely — all of `frontend/src/`, `frontend/node_modules/`, `frontend/dist/`, `frontend/package.json`, `frontend/vite.config.ts`, etc.
- **Rename** `frontend_streamlit_archive/` → `frontend/`
- Update all internal Python imports accordingly: `from frontend_streamlit_archive.ui.X` → `from frontend.ui.X`
- Update `pyproject.toml` `[tool.setuptools.packages.find]` to reflect the new `frontend` package name

### 2. Streamlit App Rewrite — Landing Page + Tabs

Rewrite `frontend/app.py` to use `st.tabs()` instead of sidebar radio buttons:

- **Tab 1: "Predictive Atmospheres" (Landing Page)** — A rich, academic introduction page containing:
  - Project title, subtitle, and thesis abstract
  - Methodology overview (referencing the EEG/ECG biometric pipeline, FAA computation, RMSSD computation, Affective Fusion algorithm)
  - Visual media from `D:\IAAC BARCELONA\MAA02\THESIS\`:
    - `Illustrations/methodology - phases.png` — methodology pipeline diagram
    - `Illustrations/biometric collection.png` — the biometric data collection setup
    - `Illustrations/brain activity.png` — EEG frontal alpha asymmetry diagram
    - `Illustrations/spatial data.png` — spatial variable extraction
    - `Illustrations/BIM1.png` — BIM integration concept
    - `Illustrations/assistive predictive model.png` — predictive model diagram
    - `Illustrations/SOTA conclusions.png` — state of the art conclusions
    - `Illustrations/expected outcomes.png` — expected outcomes
    - `EXPERIMENT DESIGN/Experiment Setup Photos/Exp- 1.gif`, `Exp- 2.gif`, `Exp- 3.gif` — experiment recording GIFs
    - `EXPERIMENT DESIGN/Experiment Setup Photos/IMG_3592.jpg`, `IMG_3594.jpg`, `IMG_3597.jpg`, `IMG_3598.jpg`, `IMG_3599.jpg` — experiment photos
  - These files will be copied into `frontend/assets/` within the repository so they can be served in deployment.
- **Tab 2: Design Studio** — Existing `design_studio.render_page()`
- **Tab 3: Human Metrics** — Existing `human_metrics.render_page()`
- **Tab 4: Spatial Insights** — Existing `spatial_insights.render_page()`
- **Tab 5: Emotion Landscape** — Existing `emotion_landscape.render_page()`
- **Tab 6: Affective Fusion** — Existing `affective_fusion.render_page()`
- **Tab 7: Demographic Insights** — Existing `demographic_insights.render_page()`
- **Tab 8: Environmental Impacts** — Existing `environmental_impacts.render_page()`
- **Tab 9: System Architecture** — Existing `system_architecture.render_system_architecture()`
- **Tab 10: Model Training** — Existing `model_training.render_page()`

### 3. FastAPI Backend — Full Decoupling

Expand the existing `api.py` (root level) into a comprehensive FastAPI backend that serves **all** data the Streamlit frontend needs. The Streamlit app will make `requests.get()`/`requests.post()` calls to this API and will NOT import `src/` directly.

**Existing endpoints to keep (already in `api.py`):**
- `POST /predict` — room feature prediction (Valence, Arousal, NeuroScore, atmosphere label)
- `POST /inverse-optimize` — differential evolution room optimization

**New endpoints to add:**
- `GET /data/fusion` — serve `data/processed/fusion_analysis.parquet` as JSON for chart rendering (Affective Fusion, Emotion Landscape, Demographic Insights pages)
- `GET /data/spatial` — serve merged spatial metadata CSV as JSON (Spatial Insights page)
- `GET /data/experiments` — serve experiment registry summary (Human Metrics page)
- `GET /health` — health check endpoint for deployment monitoring
- `GET /config` — serve non-sensitive configuration (model type, feature list, fusion alpha)

**Backend changes:**
- Move `api.py` from root to `src/api.py` (keep a thin `api.py` at root that imports and re-exports for backward compat)
- Add `CORS` origins for Streamlit Community Cloud domain
- The `ServiceContainer` lifespan initialization stays as-is — it loads the model at startup

### 4. Frontend-Backend Wiring

Modify every Streamlit UI page (`frontend/ui/*.py`) to fetch data from the FastAPI backend via HTTP instead of importing `src/` modules directly:

- Replace `from src.config import get_config` with API calls to `GET /config`
- Replace direct `pd.read_parquet("data/processed/...")` with `requests.get(API_URL + "/data/fusion")`
- Replace `from src.services.container import ServiceContainer` with `requests.post(API_URL + "/predict", json=...)`
- The API base URL will be read from `st.secrets["API_URL"]` or an environment variable `PREDICTIVE_ATMOSPHERES_API_URL`
- Add `frontend/api_client.py` — a thin wrapper module providing `predict()`, `optimize()`, `get_fusion_data()`, etc. that all UI pages import

### 5. Git — Un-ignore Raw Data

Modify `.gitignore` to remove the exclusions for scientific data:
- Remove `data/raw/` from `.gitignore`
- Remove `data/processed/` from `.gitignore`
- Remove `*.pt`, `*.pth`, `*.pkl` from `.gitignore` (trained models should be pushed for reproducibility)
- Remove `*.pdf` from `.gitignore` (thesis PDFs should be in the repo)
- Keep `teaser video/` ignored (too large)
- Keep `.venv/`, `__pycache__/`, `node_modules/` ignored

### 6. Deployment Infrastructure

**Backend (FastAPI) — Render.com:**
- Create `Dockerfile.api` for the FastAPI backend specifically:
  ```dockerfile
  FROM python:3.11-slim
  WORKDIR /app
  COPY requirements.txt .
  RUN pip install --no-cache-dir -r requirements.txt
  COPY src/ src/
  COPY data/ data/
  COPY api.py .
  EXPOSE 8000
  CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
  ```
- Create `render.yaml` (Blueprint IaC) defining two services:
  1. `predictive-atmospheres-api` — Web Service, Docker, `Dockerfile.api`, health check at `/health`
  2. `predictive-atmospheres-app` — Web Service, Docker, `Dockerfile` (Streamlit), env var `PREDICTIVE_ATMOSPHERES_API_URL` pointing to the backend service URL

**Frontend (Streamlit) — Streamlit Community Cloud or Render:**
- Update existing `Dockerfile` to point to the renamed `frontend/app.py`
- Add `.streamlit/config.toml` with server configuration for cloud deployment
- Add `.streamlit/secrets.toml.example` documenting the required `API_URL` secret

### 7. Documentation Updates

- **`README.md`**: Complete rewrite to reflect the Streamlit + FastAPI architecture. Remove all React/Vite/Tailwind references. Document:
  - New architecture diagram (Streamlit → FastAPI → ML Backend)
  - Local development setup (how to run both services)
  - Deployment instructions (Render.com Blueprint)
  - Placeholder for live website URL (to be filled post-deployment)
- **`requirements.txt`**: Add `fastapi`, `uvicorn`, `httpx`/`requests` to the flat dependency list. Remove any React-specific tooling references.
- **`pyproject.toml`**: Update author info, add `fastapi` and `uvicorn` to dependencies, update `[tool.setuptools.packages.find]` to include new `frontend` path, bump version to `0.3.0`
- **`Dockerfile`**: Update CMD to use `frontend/app.py`

---

## Affected Memory

No memory domains exist yet (the memory index is empty). This change will be the first to populate memory during hydrate.

---

## Impact

- **Files created:** `frontend/assets/` (media copies), `frontend/api_client.py`, `Dockerfile.api`, `render.yaml`, `.streamlit/config.toml`, `.streamlit/secrets.toml.example`, `src/api.py`
- **Files modified:** `frontend/app.py` (full rewrite), all `frontend/ui/*.py` files (API wiring), `.gitignore`, `README.md`, `requirements.txt`, `pyproject.toml`, `Dockerfile`, `api.py`
- **Files deleted:** Entire `frontend/` directory (React app — `src/`, `node_modules/`, `dist/`, `public/`, config files)
- **Estimated scale:** ~15 files modified, ~1 directory deleted, ~10 files created, ~20 media assets copied
- **Risk:** Medium — the Streamlit pages are already working; the main risk is correctly wiring all data flows through the new API client without breaking existing chart rendering logic

---

## Open Questions

None — all questions were resolved during the `/fab-discuss` session.

---

## Assumptions

| # | Grade | Decision | Rationale | Scores |
|---|-------|----------|-----------|--------|
| 1 | Certain | Use `st.tabs()` for navigation, not multi-page or sidebar radio | Discussed — user explicitly chose this option | S:95 R:90 A:95 D:95 |
| 2 | Certain | Fully decouple: FastAPI serves both ML predictions AND dataset/chart data | Discussed — user explicitly chose full decoupling over hybrid | S:95 R:85 A:90 D:90 |
| 3 | Certain | Landing page is academic/research-focused, not portfolio/showcase | Discussed — user explicitly chose academic tone | S:95 R:90 A:90 D:95 |
| 4 | Certain | Deploy via Streamlit Community Cloud (frontend) + Render/HF (backend) | Discussed — user explicitly chose free/cheap tier | S:90 R:85 A:85 D:85 |
| 5 | Certain | Delete React frontend entirely, rename `frontend_streamlit_archive/` to `frontend/` | Discussed — user explicitly chose this cleanup approach | S:95 R:80 A:95 D:95 |
| 6 | Certain | Copy thesis media assets into `frontend/assets/` inside the repo | Discussed — user explicitly chose automatic copy over manual placeholders | S:95 R:85 A:90 D:90 |
| 7 | Certain | Un-ignore `data/raw/`, `data/processed/`, `*.pt`, `*.pkl`, `*.pdf` in `.gitignore` | Discussed — user wants everything possible pushed to git including raw data | S:95 R:80 A:90 D:90 |
| 8 | Certain | Update README, requirements.txt, pyproject.toml to reflect new architecture | Discussed — user explicitly requested all files updated to latest build | S:90 R:90 A:90 D:90 |
| 9 | Confident | Use `requests` library for Streamlit → FastAPI communication (not `httpx`) | Streamlit ecosystem standard; `requests` is synchronous which matches Streamlit's execution model | S:70 R:95 A:85 D:80 |
| 10 | Confident | Move API to `src/api.py` while keeping root `api.py` as a thin re-export | Keeps backward compat for anyone using `uvicorn api:app` | S:65 R:90 A:85 D:75 |
| 11 | Confident | Use `render.yaml` Blueprint for one-click deployment infrastructure | Standard Render.com IaC pattern; user confirmed Render as platform | S:75 R:90 A:80 D:80 |
| 12 | Confident | Bump version to 0.3.0 for this architectural change | Semantic versioning: minor bump for backward-incompatible frontend restructure | S:60 R:95 A:90 D:85 |

12 assumptions (8 certain, 4 confident, 0 tentative, 0 unresolved). Run /fab-clarify to review.
