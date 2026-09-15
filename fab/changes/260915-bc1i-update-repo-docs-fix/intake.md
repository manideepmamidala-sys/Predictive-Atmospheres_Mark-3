# Update Repo Docs and Fix api.py PyTorch Hang
* 260915-bc1i-update-repo-docs-fix
* 2026-09-15

## Origin
Discussed in previous `/fab-discuss` session. Authored as a follow-up to the React/FastAPI frontend migration (change 260915-vwf1).

## Why
1. The `README.md` is outdated. It references the legacy Streamlit `frontend/app.py` script instead of the new React/Vite/Tailwind SPA architecture, and it mentions 12 spatial variables when there are now 13 (after consolidating the Pydantic schema in the latest backend change).
2. Running `python api.py` currently hangs and causes a `KeyboardInterrupt` crash during startup on Python 3.13 due to a slow or incompatible `torch` import happening globally when the server starts. Since `api.py` only currently requires `joblib` (scikit-learn models), we must decouple `ServiceContainer` from `architectures.py` (which imports `torch`) to fix the crash and drastically reduce startup time and memory overhead.

## What Changes

### Documentation (README.md)
- Update "Architecture" section to document the headless FastAPI backend and React 18 / Vite / Tailwind UI.
- Update "Tech Stack & Conventions" section to reflect the removal of Streamlit.
- Update the number of spatial variables mentioned in the Spatial Input schema (from 12 to 13).
- Update the "Run the App" instructions to describe `npm run dev` in `frontend/` and `fastapi dev api.py` instead of `streamlit run`.

### Backend Initialization (src/services/container.py and api.py)
- Refactor `src/services/container.py` (and potentially `api.py`) to lazy-load or conditional-load PyTorch models. 
- Ensure that importing `ServiceContainer` does not implicitly trigger `import torch` from `src.models.architectures` during app startup when only traditional ML algorithms are requested.

## Affected Memory
- Architecture

## Impact
- `README.md` (moderate modifications)
- `src/services/container.py` (minor modifications for lazy loading)
- `src/models/architectures.py` (minor modifications if needed)

## Open Questions
- None.

## Assumptions

| # | Grade | Decision | Rationale | Scores |
|---|-------|----------|-----------|--------|
| 1 | Confident | Lazy-load `torch` inside `ServiceContainer` | Fixes the PyTorch 3.13 import hang while preserving functionality. | S:80 R:80 A:90 D:90 |

1 assumptions (0 certain, 1 confident, 0 tentative, 0 unresolved).
