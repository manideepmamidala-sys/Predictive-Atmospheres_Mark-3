# Implementation Plan — Predictive Atmospheres (Execution Roadmap)

## 1) Objective
This plan translates the current planning documents into an executable, phased delivery roadmap with small tasks, clear dependencies, and validation gates.

Source inputs consolidated:
- PRD
- Tech stack document
- Backend schema
- Front-end guidelines
- Design doc (dark theme redesign)
- App flow

---

## 2) Delivery Strategy
- Build in vertical slices: **ingestion → preprocessing → training → inference → UI**.
- Keep backward compatibility with Experiment 01 while enabling extensibility for future experiments.
- Ship usable increments at each phase gate.
- Defer non-MVP items (full Rhino plugin packaging, optional LLM assistants) until core workflow is stable.

---

## 3) Phase 0 — Project Setup & Governance
**Goal:** establish execution baseline, coding standards, and traceability.

### Tasks
- [ ] Create execution tracker with milestones and owners.
- [ ] Define branch/PR convention and commit labels (`feat`, `fix`, `docs`, `schema`, `ml`).
- [ ] Add/update quality tooling config (ruff, mypy, pytest, pre-commit).
- [ ] Define environment matrix (Windows local, optional Docker).
- [ ] Create `docs/project planning docs/implementation-status.md` for progress logs.

### Outputs
- Working conventions and quality gates documented.

### Exit Criteria
- Lint/type/test commands run successfully in baseline environment.

---

## 4) Phase 1 — Data Contract & Ingestion Foundation
**Goal:** implement robust split-CSV ingestion with lifecycle states and extensible columns.

### Tasks
- [ ] Implement metadata file discovery for:
  - `experiment_XX_spatial data.csv`
  - `experiment_XX_biometric data.csv`
- [ ] Implement schema validators for required columns.
- [ ] Implement backward-compatible label strategy parser:
  - Legacy: `Score by Subject_(0-10)`
  - Preferred: `Valence Score by Subject (0-10)` + `Arousal Score by Subject (0-10)`
- [ ] Implement `Room_ID` join with integrity checks.
- [ ] Implement optional-column collector into dynamic feature dictionaries.
- [ ] Implement experiment readiness classifier:
  - `planned`, `ready`, `collected`, `processed`
- [ ] Implement ingestion report artifact (missing fields, invalid rows, optional columns found).

### Outputs
- Canonical joined dataset builder and validation report.

### Exit Criteria
- Experiment 01 ingests as `ready/collected`.
- Experiment 02 template ingests as `planned` without pipeline crash.

---

## 5) Phase 2 — Schema Persistence Layer
**Goal:** wire logical backend schema to storage models (local-first, DB-ready).

### Tasks
- [ ] Create local canonical table writers (Parquet) for:
  - `spatial_metadata_raw_df`, `biometric_metadata_raw_df`, `biometric_trials_df`, `extracted_features_df`
- [ ] Add schema version field in stored manifests.
- [ ] Add artifact manifest structure (`model`, `scaler`, `feature-order`, `run-id`).
- [ ] Implement optional SQL model stubs/migrations aligned with `backend-schema.md` tables.
- [ ] Add `experiment_registry` persistence with lifecycle status updates.

### Outputs
- Reproducible local storage contract with version tags.

### Exit Criteria
- Ingested outputs can be reloaded deterministically from stored snapshots.

---

## 6) Phase 3 — Preprocessing Pipeline Hardening
**Goal:** make EEG/ECG preprocessing resilient and auditable.

### Tasks
- [ ] Implement stage-wise pipeline orchestration (EEG preprocess, ECG preprocess, feature extraction).
- [ ] Add per-trial quality flags and artifact reasons.
- [ ] Add support for optional dynamic metadata feature propagation into training matrix.
- [ ] Add caching policy for processed tensors/features.
- [ ] Generate preprocessing summary report (counts, dropped rows, warnings).

### Outputs
- Stable feature dataset ready for model training.

### Exit Criteria
- Pipeline succeeds on valid data and returns actionable warnings on degraded data.

---

## 7) Phase 4 — Model Training & Evaluation
**Goal:** train reproducible baseline models and export deployable artifacts.

### Tasks
- [ ] Implement normalized feature matrix builder with strict feature-order registry.
- [ ] Implement MLP training run with deterministic seeds.
- [ ] Implement benchmark models (RF/Ridge/SVM as configured).
- [ ] Implement evaluation metrics (MAE/RMSE + category diagnostics if applicable).
- [ ] Add run logging (metrics, params, split refs, experiment IDs).
- [ ] Export ONNX and TorchScript with metadata bundle.
- [ ] Add model selection policy (`best_by_metric`, optional override).

### Outputs
- Versioned model artifacts and training reports.

### Exit Criteria
- `train` command produces model + scaler + schema bundle reliably.

---

## 8) Phase 5 — Inference Service Contract
**Goal:** provide stable prediction service for Streamlit and Rhino integration.

### Tasks
- [ ] Define Pydantic request/response models per backend schema.
- [ ] Implement preprocessing for inference payloads (validation + normalization).
- [ ] Implement inference path for ONNX runtime (primary) and fallback runtime.
- [ ] Implement response payload composer:
  - dimensional affect
  - categorical affect
  - model/version/latency metadata
- [ ] Implement runtime safeguards (NaN/Inf guard, schema mismatch guard).
- [ ] Add structured error responses with actionable codes.

### Outputs
- Local FastAPI service with stable contract.

### Exit Criteria
- Inference p95 target met for single-request local benchmark.

---

## 9) Phase 6 — Streamlit UX Implementation
**Goal:** implement the dark-theme research dashboard with required workflow states.

### Tasks
- [ ] Implement design tokens in centralized CSS overrides using purple-first color-theory rules.
- [ ] Implement dashboard shell + sidebar navigation pages.
- [ ] Build ingestion panel with:
  - explicit split CSV inputs
  - readiness chips (`Planned/Ready`)
  - optional parameter tags
- [ ] Build signal processing status panel with circular progress indicators.
- [ ] Build affective mapping visuals (circumplex, radar, confidence views).
- [ ] Build training/results panel (metrics feed, charts, artifact status).
- [ ] Implement session-state persistence for uploaded paths and configs.
- [ ] Add error/empty/loading states from design spec.
- [ ] Enforce accent usage policy in charts/components:
  - purple shades by default,
  - complementary accent for single non-purple emphasis,
  - triadic accents only for multi-series comparison.

### Outputs
- End-to-end researcher workflow in Streamlit.

### Exit Criteria
- User can complete ingest → preprocess → train → export in UI with no blocking UI failures.

---

## 10) Phase 7 — Optimization & Design Prediction UX
**Goal:** support architecture decision workflows in app.

### Tasks
- [ ] Implement scenario comparison view (multiple room variants).
- [ ] Implement target-emotion optimization controls and result listing.
- [ ] Add feature contribution visualization for selected scenario.
- [ ] Implement save/load design snapshots with prediction metadata.

### Outputs
- Actionable design feedback features in dashboard.

### Exit Criteria
- Architect/researcher can compare scenarios and iterate toward target affect profile.

---

## 11) Phase 8 — Rhino Bridge (Prototype to Production Path)
**Goal:** enable real-time geometry-to-affect loop in Rhino ecosystem.

### Tasks (Prototype)
- [ ] Define geometry JSON contract and sample payload fixtures.
- [ ] Implement API endpoint compatibility test for Rhino clients.
- [ ] Add Hops/bridge test harness and latency logging.

### Tasks (Plugin Path)
- [ ] Define docked panel UX spec for Eto.Forms.
- [ ] Define async inference interaction contract (debounce/cancel/retry).
- [ ] Define viewport overlay protocol (temporary, non-baked display data).

### Outputs
- Working bridge spec and tested prototype endpoints.

### Exit Criteria
- Geometry update can trigger valid inference and UI update in prototype flow.

---

## 12) Phase 9 — Observability, QA, and Hardening
**Goal:** make the system reliable and release-ready.

### Tasks
- [ ] Add test suites:
  - ingestion validation tests
  - schema evolution tests (optional columns)
  - training smoke tests
  - inference contract tests
- [ ] Add performance checks for preprocessing and inference latency.
- [ ] Add telemetry/logging structure for run + prediction tracing.
- [ ] Validate frontend accessibility checklist from guidelines.
- [ ] Execute regression test pass for Experiment 01 compatibility.

### Outputs
- Quality baseline and reliability evidence.

### Exit Criteria
- All critical tests pass; acceptance criteria from PRD and app flow are met.

---

## 13) Phase 10 — Documentation & Release Packaging
**Goal:** ensure reproducibility and handoff readiness.

### Tasks
- [ ] Update README quickstart for split metadata workflow.
- [ ] Add data-contract appendix mapping CSV fields to canonical schema.
- [ ] Add troubleshooting guide for planned/ready experiment status.
- [ ] Add model export/import operational guide (Streamlit ↔ Rhino).
- [ ] Create release checklist and tag v1 candidate.

### Outputs
- Complete implementation and operational documentation.

### Exit Criteria
- New team member can run full pipeline from docs only.

---

## 14) Cross-Phase Dependency Map
- Phase 1 blocks Phases 3, 4, 6.
- Phase 2 should complete before Phase 4 artifact governance is finalized.
- Phase 4 blocks Phase 5 and Phase 8.
- Phase 5 partially blocks Phase 6 prediction views and Phase 8 bridge.
- Phase 9 runs continuously but final sign-off happens after Phases 6–8.

---

## 15) Suggested Execution Order (Immediate Next Tasks)
1. Implement ingestion validator + `Room_ID` join + readiness classifier.
2. Add optional-column capture and canonical joined dataset export.
3. Update training input builder to support both legacy and split label modes.
4. Lock model artifact bundle contract (model/scaler/feature-order/version).
5. Implement API contract tests before extending UI components.

---

## 16) Definition of Done (Program Level)
- All PRD in-scope requirements are implemented and testable.
- Split metadata workflow supports both current and future experiments.
- Planned template experiments are supported without breaking current runs.
- Streamlit workflow and inference service are stable and documented.
- Rhino bridge prototype contract is validated end-to-end.
