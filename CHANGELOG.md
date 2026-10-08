# Changelog

## Unreleased — research-platform rebuild (2026-10-08)

- Preserved original recordings, metadata, room renders, legacy presentation assets and thesis PDFs with a source hash manifest and migration inventory.
- Replaced the prior Streamlit/PyTorch runtime with a Python 3.11 research package, frozen `uv` environment, versioned FastAPI service and a seven-route React/Vite/TypeScript atlas. Legacy retirement and final independent review are tracked in the active Fab change.
- Added a read-only acquisition audit, explicit conditional-rate EEG/ECG processing and QC, separate descriptive complete/partial fusion cohorts, grouped model comparison against simple baselines, trusted fitted artifact metadata and source-derived static exports.
- Added a user-selected target Neuro-Score and a bounded seeded room search. The evaluated model remains labelled `not_better_than_baseline`; no confidence percentage or training-on-request fallback is offered.
- Added Light/Dark/System themes, source-linked panorama derivatives, signal/affect/people views with accessible tables, offline static research pages, typed API client and locally validated browser checks.
- Added candidate free-tier hosting configuration and operations/release-readiness records. No deployment, public-data license or DOI is part of this unreleased entry.

See [the active implementation plan](fab/changes/261008-ymhz-research-platform-rebuild/plan.md), [phase reports](docs/reports/) and [release readiness](docs/release-readiness.md) for exact evidence and remaining work.
