# Update Repo Docs and Fix api.py PyTorch Hang
* 260915-bc1i-update-repo-docs-fix
* [Intake](intake.md)

## Requirements

### Documentation: README Updates
- **R1**: The README MUST reflect the removal of Streamlit and the transition to the headless FastAPI + React/Vite/Tailwind SPA architecture.
- **R2**: The README MUST state that there are 13 independent spatial variables.
- **R3**: The README MUST document how to run the frontend (`npm run dev`) and backend (`fastapi dev api.py`) separately.

### Backend: PyTorch Lazy Loading
- **R4**: The `ServiceContainer` MUST NOT implicitly trigger `import torch` on application startup.
- **R5**: PyTorch-dependent models (`SpatialFFNN`) SHOULD be conditionally loaded or lazy-loaded to prevent `KeyboardInterrupt` crashes and reduce overhead on Python 3.13.

## Tasks

- [x] T001 [P] Update `README.md` to reflect new architecture, 13 variables, and new run instructions. <!-- R1, R2, R3 -->
- [x] T002 [P] Refactor `src/models/architectures.py` and `src/services/container.py` to lazy-load PyTorch so `import torch` isn't executed globally. <!-- R4, R5 -->

## Acceptance

### Functional Completeness
- [ ] A-001 R1: README mentions FastAPI and React instead of Streamlit.
- [ ] A-002 R2: README specifies 13 spatial variables instead of 12.
- [ ] A-003 R3: README includes commands `npm run dev` and `fastapi dev api.py`.
- [ ] A-004 R4: `import torch` is removed from global scope in `architectures.py` and `container.py`, preventing startup hang.

### Code Quality
- [ ] A-005 Pattern consistency: Backend changes adhere to existing dependency injection patterns.
- [ ] A-006 No unnecessary duplication: Code is DRY.

## Assumptions

| # | Grade | Decision | Rationale | Scores |
|---|-------|----------|-----------|--------|
| 1 | Confident | Lazy-load `torch` inside `ServiceContainer` | Fixes the PyTorch 3.13 import hang while preserving functionality. | S:80 R:80 A:90 D:90 |
