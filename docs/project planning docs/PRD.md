# PRD Draft — Predictive Atmospheres (v1)

## 1) Product Summary
- Predictive Atmospheres is a decision-support platform that predicts likely human emotional response to architectural spaces using biometric-informed ML.
- It helps architects/researchers simulate affective outcomes (Valence/Arousal + emotion distribution) from room parameters before physical construction.
- Primary surfaces: interactive design app and CLI pipeline for training, prediction, and experiment management.

## 2) Problem Statement
- Spatial design decisions are usually evaluated with aesthetics, cost, and code compliance, but emotional impact is hard to quantify early.
- Existing workflows rely on post-occupancy feedback, which is late and expensive to iterate on.
- Teams need a repeatable, data-driven way to estimate emotional response during concept and schematic design.

## 3) Goals & Success Criteria
- Enable users to input room geometry and receive interpretable emotional predictions in < 3 seconds for inference.
- Provide end-to-end reproducible training from experiment data with clear model metrics.
- Support inverse design: suggest room parameter candidates for target emotional profiles.
- Success metrics:
  - Model: stable convergence on baseline dataset; predefined regression/error thresholds.
  - Product: >80% task completion for core flows (train, predict, compare designs).
  - Reliability: >99% successful inference requests in local runs.

## 4) Target Users
- **Primary:** Computational architects and neuro-architecture researchers.
- **Secondary:** Design students, evidence-based design consultants, lab technicians running experiments.
- **Tertiary:** Product/design engineers integrating emotional simulation into broader digital twins.

## 5) User Stories
- As a researcher, I upload experiment metadata and recordings to retrain the model with new cohorts.
- As an architect, I input room dimensions and get predicted Valence/Arousal and emotion mix.
- As a designer, I define a target emotion and receive candidate geometry options.
- As a reviewer, I inspect model performance, data provenance, and benchmark views before trusting outputs.

## 6) Scope (MVP)
- **In scope**
  - Data ingestion from split experiment metadata files (`*_spatial data.csv` + `*_biometric data.csv`) + raw EEG/ECG recordings.
  - Signal preprocessing and feature extraction pipeline.
  - Training/inference for at least one neural model and one classical ML baseline.
  - Interactive UI pages for design prediction, human metrics, spatial insights, and training.
  - CLI commands for `train`, `predict`, and experiment info.
- **Out of scope (MVP)**
  - Real-time wearable streaming.
  - Multi-building BIM plugin integrations.
  - Clinical-grade diagnosis claims.
  - Cloud multi-tenant deployment.

## 7) Functional Requirements
- **FR-1 Data Management**
  - Discover experiments automatically from expected folder/metadata conventions.
  - Validate required split schemas for room and biometric references.
  - Join biometric and spatial metadata using `Room_ID` before preprocessing/training.
  - Support experiment lifecycle states (`planned`, `ready`, `collected`, `processed`) so incomplete future experiments can be registered without blocking current workflows.
  - Support extensible optional metadata parameters (new spatial or biometric columns) without requiring code changes for every new field.
- **FR-2 Preprocessing**
  - Apply baseline removal and normalization.
  - Extract model-ready features and cache processed outputs.
- **FR-3 Emotion Engine**
  - Map processed signals to Valence/Arousal.
  - Produce category-level emotion distribution.
- **FR-4 Modeling**
  - Train selectable model types (MLP + baseline alternatives).
  - Persist model artifacts and training metrics.
- **FR-5 Prediction**
  - Input: room dimensions (and optional covariates).
  - Output: Valence, Arousal, neuro-score, confidence/uncertainty indicator.
- **FR-6 Optimization**
  - Input: target emotional profile.
  - Output: candidate room geometries satisfying constraints.
- **FR-7 Visualization**
  - 3D room preview and affective-space plotting.
  - Comparison view across candidate designs.
- **FR-8 CLI**
  - Commands for model training, prediction, and dataset introspection.

## 8) Non-Functional Requirements
- **Performance:** local inference p95 < 3s for single room query.
- **Reproducibility:** deterministic seeds/config snapshots for training runs.
- **Reliability:** graceful failure on missing/corrupt data with actionable errors.
- **Usability:** onboarding flow allows first prediction within 15 minutes.
- **Security/Privacy:** no hardcoded PII; local data handling defaults; documented anonymization expectations.
- **Maintainability:** modular services, typed data models, baseline tests on core pipeline.

## 9) Data & ML Requirements
- Inputs include split metadata files (`experiment_XX_spatial data.csv` and `experiment_XX_biometric data.csv`) + synchronized EEG/ECG recordings.
- Required metadata fields:
  - Spatial file: `Room_ID`, `Length (meter)`, `Width (meter)`, `Height (meter)`
  - Biometric file: `Subject_ID`, `Room_ID`, `Time spent by the subject in the room (seconds)`, `EEG_Filename`, plus either
    - `Score by Subject_(0-10)` (legacy/combined label), or
    - `Valence Score by Subject (0-10)` and `Arousal Score by Subject (0-10)` (preferred split labels)
 - Optional metadata fields:
  - Any additional spatial or biometric columns are allowed and should be captured as optional features for future experiments.
- Required data quality checks:
  - Sampling-rate conformity,
  - missing-value policy,
  - per-subject/session traceability.
  - Distinguish `planned template` rows (empty values allowed) from `collected data` rows (required fields enforced).
- Evaluation protocol:
  - train/validation/test split at subject or experiment level,
  - report MAE/RMSE (regression) and calibration diagnostics.
- Model governance:
  - version model + preprocessing config together,
  - track experiment IDs used per run.

## 10) UX Requirements
- Clear mode navigation: Design Studio, Human Metrics, Spatial Insights, Emotion Landscape, Benchmark, Training.
- Frontend visual system follows a purple-first color strategy:
  - Purple shades as default interaction and chart palette,
  - Complementary yellow-gold when one non-purple accent is needed,
  - Triadic teal + orange when two additional accents are required for comparisons.
- Prediction cards must include:
  - numeric values,
  - intuitive labels,
  - interpretation helper text.
- Benchmark/training views must expose metric trends and model selection rationale.
- Error states should tell users exactly what to fix (missing file, schema mismatch, etc.).

## 11) Milestones
- **M1 (2–3 weeks):** stabilize ingestion + preprocessing + baseline training.
- **M2 (2 weeks):** productionize prediction + optimization services.
- **M3 (2 weeks):** finalize UI flows and benchmark pages.
- **M4 (1 week):** QA, documentation, reproducibility pack, release candidate.

## 12) Risks & Mitigations
- **Limited dataset size:** use strict validation, regularization, and uncertainty reporting.
- **Sensor noise variability:** robust preprocessing and quality flags.
- **Over-interpretation by users:** add explicit “decision-support, not diagnosis” messaging.
- **Concept drift across cohorts:** scheduled retraining + per-cohort performance tracking.

## 13) Acceptance Criteria (Release v1)
- User can run full pipeline from fresh data to trained model.
- User can predict emotional profile from room dimensions via UI and CLI.
- User can run target-emotion optimization with configurable constraints.
- Core tests pass and documentation enables reproducible setup/run by a new team member.
