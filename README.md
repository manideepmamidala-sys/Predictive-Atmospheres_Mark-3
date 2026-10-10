# Predictive Atmospheres

Predictive Atmospheres is a reproducible pilot study of how people rated rendered rooms and what conditional EEG/ECG features could be extracted while they viewed them. The eight-route Research Atlas and Design Studio revision has passed local pipeline, model, catalogue and browser checks; its fresh source-only reproduction passed, while independent whole-change release review remains pending. Its [v1.2 analysis specification](docs/specs/analysis-v1.2-draft.md) received exact-source owner approval at CP-Spec; [CP-B](docs/reports/revision-2026-10/CP-B.md) records delegated AI signal review without claiming personal owner inspection. [CP-C](docs/reports/revision-2026-10/CP-C.md) approved qualified **baseline-only** publication with limits. The Design Studio is an experimental demonstration, not a validated measure of emotion or a design recommendation.

## What the repository contains

| Path | Role |
|---|---|
| `data/raw/`, `data/metadata/`, `data/renders/raw/` | Preserved original recordings, room/ratings metadata and Lumion renders; `data/source-inventory.json` and `data/MANIFEST.sha256` track retained source bytes. |
| `backend/` | Python 3.11 package for audit, conditional signal processing, descriptive affect analysis, grouped model evaluation, static exports and FastAPI. |
| `artifacts/results/`, `artifacts/model/` | Versioned research products and a trusted fitted model with compatibility metadata. |
| `frontend/` | React/Vite/TypeScript atlas. Research routes read schema-validated static exports; only prediction and optimization call the API. |
| `docs/protocol/`, `docs/specs/`, `docs/reports/` | Investigator provenance, predeclared method, checkpoints, independent review and browser evidence. |

The original study contains 160 room-viewing trials in three experiments across ten distinct participant source codes and 30 rooms. Experiment 1 records comfort, not valence/arousal. Source `Subj_*` codes link records without claiming a mapping to personal names. Descriptive, self-report, physiological and fused-model cohorts answer different questions; the [data card](docs/data_card.md), [model card](docs/model_card.md) and final validation report give their exact eligibility and limitations.

## Run locally

Use Python 3.11.11, uv 0.5.9, Node 22.22.1 and Corepack with the pinned pnpm 10.18.3 lock. From the repository root:

```sh
make setup
make verify-data
make pipeline
make lint test site
```

The pipeline regenerates the audit, conditional signal/affect/model results, learning curves, OpenAPI and browser products from preserved inputs. It verifies and can reuse an exact complete 1,000-draw spatial-null product; the [isolated source-only run](docs/reports/revision-2026-10/validation.md) computes the controls afresh. The 1,000 full-refit draws and 455 learning-curve subsets can take hours; do not lower those counts to claim a full reproduction. The site build checks product hashes against `artifacts/results/manifest.json` and validates all 28 catalogue products before staging research JSON; browser tests exercise the resulting pages. The root `Makefile` and [operations guide](docs/operations.md) give individual commands and setup details. On the current restricted host, Chromium needs the temporary native-library path documented in the operations guide.

Start the API and frontend in separate terminals after a successful pipeline:

```sh
cd backend && uv run --frozen uvicorn pa.api.app:app --host 127.0.0.1 --port 8000
cd frontend && corepack pnpm dev
```

Open the Vite URL printed by the frontend command. `/v1/health` reports process liveness and a separate model `ready` flag. The frontend remains useful without a live API; Design Studio explains when the service is unavailable. Configuration examples are at [.env.example](.env.example), [backend/.env.example](backend/.env.example), and [frontend/.env.example](frontend/.env.example). The public API schema is generated at `artifacts/results/openapi.json`; the client types in `frontend/src/api/schema.d.ts` are regenerated from it and checked for drift.

## Read the evidence

- [Acquisition and exposure](docs/protocol/acquisition.md), [ratings](docs/protocol/ratings.md), and [spatial/render provenance](docs/protocol/spatial-provenance.md) distinguish observed source fields from investigator report and unresolved settings.
- The [approved v1.2 analysis specification](docs/specs/analysis-v1.2-draft.md) fixes conditional sample-rate handling, QC, cohorts and evaluation decisions. The near-500 Hz source rate is a **conditional analytical scenario**, not a confirmed hardware setting; [CP-Spec](docs/reports/revision-2026-10/CP-Spec.md) records the approved source hash.
- [Data card](docs/data_card.md), [model card](docs/model_card.md), [catalogue guide](docs/research/analysis-catalogue.md), and [validation record](docs/reports/revision-2026-10/validation.md) describe generated counts, exclusions, all 28 figures, comparisons and limits. [Thesis source context](docs/research/thesis-source-context.md) preserves source provenance after duplicate personal documents were removed.
- [Website browser review](docs/reports/phase-8.md) retains the previous seven-route baseline evidence; [release readiness](docs/release-readiness.md) separates the eight-route local results from public-hosting and rights prerequisites.

The Neuro-Score is a declared distance to a **user-selected** valence/arousal target, not a probability of well-being. Approved v1.2 held-out tests, all 1,000 spatial-null controls and 455 learning subsets have completed locally; the selected room-held-out procedure did not beat fixed mean or median baselines. The fitted Studio predictor is constant. The fresh isolated rebuild matched all 53 result JSON products and fitted-model bytes against the final reference. No calibrated confidence interval or individual response guarantee is available.

## Status and use boundary

The GitHub repository is already **PUBLIC**, and the owner authorized public recordings, metadata, renders and results. `render.yaml` and `frontend/vercel.json` are free-tier **deployment candidates**, not an active site deployment. No blanket data/asset license, DOI or association of participant names with biometric records is asserted here; that named association lacks a verified mapping and specific permission. Review license scope, service limits and hosted behavior before those separate release actions. [Operations](docs/operations.md) records the local commands and proposed hosting settings.
