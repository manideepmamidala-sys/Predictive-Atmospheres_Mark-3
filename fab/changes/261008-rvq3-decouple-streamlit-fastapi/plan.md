# Plan: Decouple Streamlit + FastAPI — Full Website Deployment

**Change:** `261008-rvq3-decouple-streamlit-fastapi`
**Intake:** [intake.md](intake.md)

---

## Requirements

### R1: Directory Restructure
The React `frontend/` directory SHALL be deleted entirely. The `frontend_streamlit_archive/` directory SHALL be renamed to `frontend/`. All Python imports referencing `frontend_streamlit_archive` SHALL be updated to `frontend`.

GIVEN the React frontend exists at `frontend/`
WHEN the restructure is applied
THEN `frontend/` contains only the Streamlit app (app.py, ui/, assets/) and zero React/Node artifacts

### R2: Streamlit Tabs + Landing Page
The Streamlit app SHALL use `st.tabs()` for navigation with an academic landing page as the first tab. The landing page SHALL include the thesis methodology, biometric pipeline description, and embedded visual media from the thesis assets.

GIVEN a user opens the deployed Streamlit app
WHEN the page loads
THEN 10 tabs are visible: Landing Page, Design Studio, Human Metrics, Spatial Insights, Emotion Landscape, Affective Fusion, Demographic Insights, Environmental Impacts, System Architecture, Model Training

### R3: FastAPI Full Decoupling
The FastAPI backend SHALL serve both ML predictions AND dataset/chart data. New endpoints SHALL be added for fusion data, spatial data, experiment metadata, health checks, and configuration. The Streamlit frontend SHALL NOT import any `src/` modules directly.

GIVEN the Streamlit app needs data
WHEN any UI page renders charts or predictions
THEN all data flows through HTTP requests to the FastAPI backend

### R4: Git Un-ignore Scientific Data
The `.gitignore` SHALL be updated to allow `data/raw/`, `data/processed/`, `*.pt`, `*.pkl`, and `*.pdf` to be tracked. The `teaser video/` directory SHALL remain ignored.

GIVEN the updated `.gitignore`
WHEN `git status` is run
THEN raw EEG CSVs, processed parquets, trained models, and thesis PDFs appear as trackable files

### R5: Deployment Infrastructure
A `render.yaml` Blueprint, `Dockerfile.api`, and Streamlit config files SHALL be created for one-click cloud deployment. The README SHALL be rewritten to document the new architecture.

GIVEN the deployment files exist in the repo
WHEN a user connects the repo to Render.com via Blueprint
THEN both the FastAPI backend and Streamlit frontend deploy automatically

### Non-Goals
- Modifying the ML training pipeline or model architectures
- Changing the EEG/ECG signal processing logic
- Adding new Streamlit pages beyond the landing page
- Implementing authentication or user management

### Design Decisions

**Decision:** Use `st.tabs()` over Streamlit Multi-Page App
**Why:** User prefers all content on a single page with tab navigation for a cohesive website experience
**Rejected:** Multi-page app (sidebar navigation, separate URLs) — introduces routing complexity unnecessary for a thesis project
*Introduced by:* /fab-discuss session

**Decision:** Full API decoupling (predictions + data serving)
**Why:** Clean separation of concerns; frontend becomes a pure presentation layer; enables independent scaling
**Rejected:** Hybrid approach (API for predictions only, direct file reads for charts) — partial coupling defeats the purpose
*Introduced by:* /fab-discuss session

---

## Tasks

### Phase 1: Setup & Cleanup
- [x] T001 [P] Delete the React `frontend/` directory and rename `frontend_streamlit_archive/` to `frontend/` — update all Python imports in `frontend/app.py` and `frontend/ui/*.py`
- [x] T002 [P] Copy thesis media assets from `D:\IAAC BARCELONA\MAA02\THESIS\` into `frontend/assets/` (illustrations, experiment photos, GIFs)
- [x] T003 [P] Update `.gitignore` to un-ignore `data/raw/`, `data/processed/`, `*.pt`, `*.pkl`, `*.pdf`

### Phase 2: Core Implementation
- [x] T004 Expand `api.py` with new data-serving endpoints (`GET /data/fusion`, `GET /data/spatial`, `GET /data/experiments`, `GET /health`, `GET /config`) and update CORS <!-- R3 -->
- [x] T005 Create `frontend/api_client.py` — thin HTTP wrapper module providing `predict()`, `optimize()`, `get_fusion_data()`, `get_spatial_data()`, `get_config()` <!-- R3 -->
- [x] T006 Rewrite `frontend/app.py` — replace sidebar radio with `st.tabs()`, create the academic landing page as Tab 1 with thesis media, wire remaining 9 tabs <!-- R2 -->

### Phase 3: Integration & Wiring
- [x] T007 Rewire all `frontend/ui/*.py` files to fetch data from `frontend/api_client.py` instead of importing `src/` modules directly <!-- R3 -->

### Phase 4: Polish & Deployment
- [x] T008 Create `Dockerfile.api`, update existing `Dockerfile`, create `render.yaml` Blueprint, create `.streamlit/config.toml` and `.streamlit/secrets.toml.example` <!-- R5 -->
- [x] T009 Rewrite `README.md`, update `requirements.txt` and `pyproject.toml` to reflect the new Streamlit + FastAPI architecture <!-- R5 -->

---

## Acceptance

### Functional Completeness
- [x] A-001 R1: The `frontend/` directory contains only Streamlit files (app.py, ui/, assets/, __init__.py) and zero React/Node artifacts (no package.json, no tsconfig, no node_modules)
- [x] A-002 R2: `frontend/app.py` uses `st.tabs()` with 10 tabs, first tab is a landing page with embedded thesis media
- [x] A-003 R3: `api.py` exposes `/predict`, `/inverse-optimize`, `/data/fusion`, `/data/spatial`, `/data/experiments`, `/health`, `/config`
- [x] A-004 R3: No file in `frontend/` imports any module from `src/` — all data flows through `frontend/api_client.py` HTTP calls
- [x] A-005 R4: `.gitignore` no longer excludes `data/raw/`, `data/processed/`, `*.pt`, `*.pkl`, `*.pdf`
- [x] A-006 R5: `render.yaml`, `Dockerfile.api`, `.streamlit/config.toml` exist and are syntactically valid

### Code Quality
- [x] A-007 Pattern consistency: all UI pages use the same `api_client` interface pattern
- [x] A-008 No unnecessary duplication: API base URL is configured in one place

---

## Assumptions

| # | Grade | Decision | Rationale | Scores |
|---|-------|----------|-----------|--------|
| 1 | Certain | Reuse existing `ServiceContainer` lifespan pattern in expanded API | Already working in `api.py`, proven pattern | S:90 R:90 A:95 D:95 |
| 2 | Confident | Serve parquet data as JSON via pandas `.to_dict(orient='records')` | Standard pattern for FastAPI + pandas; performance sufficient for thesis-scale data (~300 rows) | S:70 R:90 A:85 D:80 |
| 3 | Confident | Use `st.secrets` for API URL configuration in deployment | Streamlit Community Cloud native secrets mechanism | S:75 R:90 A:85 D:85 |

3 assumptions (1 certain, 2 confident, 0 tentative).
