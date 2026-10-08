# Phase 4 — legacy runtime retirement

Date: 2026-10-08. This is a responsibility-mapped source cleanup, not a data cleanup. [The exact inventory](legacy-runtime-inventory.json) records the path, byte count, SHA-256, Git-tracked status and replacement responsibility for each of the 87 removed files. All 87 were verified against that inventory immediately before deletion. The prior committed tree remains available at `41d6ba507965d5159a679e65962fb3d02963a551`; the inventory is the direct audit trail for the deletion diff.

| Retired responsibility | Replacement |
|---|---|
| `src/`, `api.py`, `run_pipeline.py` | `backend/src/pa/` versioned CLI, science pipeline and FastAPI |
| Python files in `frontend/` and `frontend_streamlit_archive/` | React/Vite site in `frontend/src/` |
| root `pyproject.toml`, `requirements.txt`, egg-info | `backend/pyproject.toml`, frozen `backend/uv.lock` |
| two legacy Dockerfiles | proposed backend Render service and static Vercel build, documented in operations |
| old processed cache, PyTorch tensor, parquet, model and bounds pickle | regenerated validated products in `artifacts/results/` and compatible fitted model in `artifacts/model/` |
| `pytest.log`, `test_output.txt` | current automated backend/frontend test results and phase reports |

The original 160 recordings, seven metadata CSVs, 30 room renders, 116 frontend images and two thesis PDFs remain governed by `data/MANIFEST.sha256` and [the preservation map](migration-inventory.json). Original renders, images and PDFs also have checksum-equivalent copies in their new evidence destinations. Existing user-authored `AGENTS.md`, `PROJECT_REPORT.md`, `EXECUTION_PLAN.md` and Fab work survive. Historical root narrative files remain available as history; they are not active runtime documentation.

After removal, `pa verify-data` returned `Source inventory verified`, and `make lint` passed backend Ruff, OpenAPI-generated client drift and frontend type checks. The active Python package imports `pa` rather than `src`, and the new frontend has no active Python/Streamlit entrypoint. The root `Makefile` and CI no longer invoke old `src/test`, Streamlit, Torch or legacy cached outputs. Historical docs and the retirement inventory intentionally mention those names to explain provenance; they are not executable references. Full clean-source reproduction and browser checks are recorded separately in [reproduction.md](reproduction.md) and [phase-9.md](phase-9.md).
