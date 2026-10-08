# Predictive Atmospheres

Predictive Atmospheres is a reproducible pilot study of how people rated rendered rooms and what conditional EEG/ECG features could be extracted while they viewed them. The seven-page research atlas presents source-matched rooms, signal quality, descriptive affect cohorts, participant summaries, and a held-out model report. Its room simulator is an **experimental demonstration**: the current fitted model is **not better than a median baseline** on held-out rooms, and its output is not a validated measure of emotion or a design recommendation.

## What the repository contains

| Path | Role |
|---|---|
| `data/raw/`, `data/metadata/`, `data/renders/raw/` | Preserved original recordings, room/ratings metadata and Lumion renders; `data/MANIFEST.sha256` tracks source bytes. |
| `backend/` | Python 3.11 package for audit, conditional signal processing, descriptive affect analysis, grouped model evaluation, static exports and FastAPI. |
| `artifacts/results/`, `artifacts/model/` | Versioned research products and a trusted fitted model with compatibility metadata. |
| `frontend/` | React/Vite/TypeScript atlas. Research routes read schema-validated static exports; only prediction and optimization call the API. |
| `docs/protocol/`, `docs/specs/`, `docs/reports/` | Investigator provenance, predeclared method, checkpoints, independent review and browser evidence. |

The original study contains 160 room-viewing trials in three experiments across ten distinct participant IDs and 30 rooms. Experiment 1 records comfort, not valence/arousal. Complete **descriptive** fusion is available for 14 trials from two people: 4 in Experiment 2 and 10 in Experiment 3, each experiment's complete records coming from one person. Another 96 records use partial modalities and are labelled separately. The model instead uses 14 Experiment 3 trials from three people under a training-fold-fitted target procedure. These cohorts answer different questions and should not be pooled. [The data card](docs/data_card.md) and [model card](docs/model_card.md) explain eligibility and limitations.

## Run locally

Use Python 3.11.11, uv 0.5.9, Node 22.22.1 and Corepack with the pinned pnpm 10.18.3 lock. From the repository root:

```sh
make setup
make verify-data
make pipeline
make lint test site
```

The pipeline regenerates the audit, conditional signal/affect/model results, OpenAPI and browser products from preserved inputs. The site build checks product hashes against `artifacts/results/manifest.json` and validates research JSON in the browser. The root `Makefile` and [operations guide](docs/operations.md) give individual commands and setup details.

Start the API and frontend in separate terminals after a successful pipeline:

```sh
cd backend && uv run --frozen uvicorn pa.api.app:app --host 127.0.0.1 --port 8000
cd frontend && corepack pnpm dev
```

Open the Vite URL printed by the frontend command. `/v1/health` reports process liveness and a separate model `ready` flag. The frontend remains useful without a live API; the simulator explains when the service is unavailable. Configuration examples are at [.env.example](.env.example), [backend/.env.example](backend/.env.example), and [frontend/.env.example](frontend/.env.example). The public API schema is generated at `artifacts/results/openapi.json`; the client types in `frontend/src/api/schema.d.ts` are regenerated from it and checked for drift.

## Read the evidence

- [Acquisition and exposure](docs/protocol/acquisition.md), [ratings](docs/protocol/ratings.md), and [spatial/render provenance](docs/protocol/spatial-provenance.md) distinguish observed source fields from investigator report and unresolved settings.
- [Analysis specification](docs/specs/analysis-v1.md) fixes conditional sample-rate handling, QC, cohorts and evaluation decisions. The near-500 Hz source rate is a **conditional analytical scenario**, not a confirmed hardware setting.
- [Data card](docs/data_card.md), [model card](docs/model_card.md), and [phase reports](docs/reports/) describe generated counts, exclusions, comparisons and limits.
- [Website browser review](docs/reports/phase-8.md) contains real-export screenshots and an 18-test Chromium run; [release readiness](docs/release-readiness.md) separates local evidence from public-hosting and rights prerequisites.

The model's held-out-room mean absolute error on constructed coordinates is 0.4304 versus 0.4099 for the median baseline. The subject holdout is limited by only three eligible people. No calibrated confidence interval or individual response guarantee is available. The Neuro-Score is a declared distance to a **user-selected** valence/arousal target, not a probability of well-being.

## Status and use boundary

The GitHub repository is already **PUBLIC**, and the owner authorized public recordings, metadata, renders and results. `render.yaml` and `frontend/vercel.json` are free-tier **deployment candidates**, not an active site deployment. No blanket data/asset license, DOI or association of participant names with biometric records is asserted here; that named association lacks a verified mapping and specific permission. Review license scope, service limits and hosted behavior before those separate release actions. [Operations](docs/operations.md) records the local commands and proposed hosting settings.
