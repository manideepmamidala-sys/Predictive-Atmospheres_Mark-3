# App Flow Document — Predictive Atmospheres (Web + Rhino)

## 1) Purpose
This document defines a possible end-to-end application flow for two primary user groups:
- **Researchers** using the Streamlit web application for data processing and model training.
- **Architects/Designers** using a Rhino plugin for real-time spatial affective feedback.

The flow is aligned with the dark-theme, professional dashboard direction and the model-serving architecture (PyTorch training + ONNX runtime inference).

---

## 2) System Context
- **Training surface**: Streamlit application connected to Python ML/data pipelines.
- **Inference surface**: Rhino plugin (C# + RhinoCommon) using local ONNX Runtime.
- **Data sources**: split metadata CSVs (`experiment_XX_spatial data.csv` + `experiment_XX_biometric data.csv`) + EEG/ECG raw recordings referenced by metadata.
- **Primary outputs**: Valence, Arousal, emotion category probabilities, confidence indicators.

---

## 3) Researcher Journey (Web Application Flow)

### Step 1 — Data Ingestion & Setup
**User Action**
- Researcher opens **Experiment Metadata** panel in the web dashboard.
- Selects metadata directory containing both `experiment_XX_spatial data.csv` and `experiment_XX_biometric data.csv`, plus raw signal directories.

**System Response**
- Validates folder structure, required split files, required columns, and subject/run consistency.
- Joins biometric rows to spatial rows via `Room_ID`.
- Detects experiment readiness state:
	- `Planned`: template rows exist but required numeric values are not populated yet
	- `Ready/Collected`: required values and file references are present
- Registers run context (experiment ID, timestamp, selected profile).

**UI State**
- Circular neon-purple loading gauges show ingest progress.
- Status chips indicate: `Loaded`, `Missing`, `Schema mismatch`, `Planned (Template)`, or `Ready`.

**Exit Criteria**
- If status is `Ready`, dataset becomes eligible for preprocessing.
- If status is `Planned (Template)`, experiment is registered but preprocessing is disabled until required fields are complete.

---

### Step 2 — Signal Preprocessing
**User Action**
- Clicks **Run Preprocessing Pipeline**.

**System Response**
- Executes EEG preprocessing with MNE-Python (baseline correction, filtering, spectral extraction).
- Executes ECG processing with NeuroKit2 (signal cleaning, HR/HRV features).
- Stores processed features into structured tables for downstream mapping/training.

**UI State**
- **Signal Processing Status** panel updates each stage in near real-time.
- Complementary yellow-gold warnings and orange-critical alerts flag high-artifact participant sessions.
- Panel provides actionable error details (subject ID, channel, affected stage).

**Exit Criteria**
- Processed features are saved and quality checks marked complete.

---

### Step 3 — Affective Mapping
**User Action**
- Opens **Feature Landscape** visualization.

**System Response**
- Maps processed biometric features to affective representation linked to spatial metadata.
- Includes optional additional spatial/biometric parameters when present (without requiring schema rewrites).
- Computes distributions and intermediate embeddings for visual inspection.

**UI State**
- Interactive 3D topographic wireframe renders feature distribution clusters.
- User can rotate/zoom/pan and switch feature-band overlays.
- Side panel shows selected cluster metadata and summary statistics.

**Exit Criteria**
- User confirms mapped data integrity and proceeds to modeling.

---

### Step 4 — Model Training & Export
**User Action**
- Sets PyTorch MLP hyperparameters and clicks **Train Model**.

**System Response**
- Trains model to learn non-linear mapping from room features to Valence/Arousal outputs.
- Evaluates against validation split and logs metrics/artifacts.
- Exports validated model as `.onnx` (and optional TorchScript).

**UI State**
- **Results Feed** logs epoch progress, convergence, and validation outcomes.
- Purple-shade gradient bar charts update accuracy/performance across emotion categories.
- Final card shows export location, model version, and readiness status.

**Exit Criteria**
- Model is validated, versioned, and available for Rhino inference.

---

## 4) Architect Journey (Rhinoceros 3D Flow)

### Step 1 — Plugin Initialization
**User Action**
- Architect starts **Neuro-Architecture** plugin from Rhino command line.

**System Response**
- C# plugin loads exported `.onnx` model into local ONNX Runtime.
- Initializes geometry listeners and plugin UI state.

**UI State**
- Docked dark-themed panel appears beside Rhino properties.
- Status indicator shows `System Ready` when runtime and model are loaded.

**Exit Criteria**
- Plugin reports healthy runtime and active model session.

---

### Step 2 — Spatial Manipulation
**User Action**
- Architect draws/scales/modifies room geometry in Rhino viewport.

**System Response**
- Event listeners detect geometry changes continuously.
- Plugin debounces updates to avoid over-triggering inference.

**UI State**
- Subtle live indicator shows `Geometry Updated` and inference pending.

**Exit Criteria**
- New geometry state is captured for feature extraction.

---

### Step 3 — Feature Extraction & Inference
**System Response**
- RhinoCommon computes spatial descriptors (volume, ceiling height, WWR, proportions, etc.).
- Plugin transforms descriptors into model input schema.
- Local ONNX inference returns Valence, Arousal, and category probabilities.

**UI State**
- Inference card updates with latest score + confidence and timestamp.
- If geometry is invalid/incomplete, UI displays precise correction guidance.

**Exit Criteria**
- New predictive state is available for design feedback.

---

### Step 4 — Real-Time Design Feedback
**System Response**
- Plugin dashboard immediately reflects psychological implications of the latest geometry.

**UI State**
- Radar chart morphs to show feature contribution profile.
- Gradient bars shift across purple shades (with complementary/triadic accents only where comparison requires it) to indicate emotional state probabilities.
- Trend sparkline shows change deltas from previous design iteration.

**User Action**
- Architect iterates geometry until desired affective target is reached.

**Exit Criteria**
- User saves design snapshot with prediction metadata.

---

## 5) Cross-Surface Handoff (Web → Rhino)
1. Researcher exports validated ONNX model from Streamlit workflow.
2. Model package includes version, feature schema, normalization stats, and date.
3. Rhino plugin loads exact package version for deterministic inference.
4. Saved Rhino snapshots can be re-imported into web dashboard for analysis/benchmarking.

---

## 6) Error and Recovery Flow
- **Data ingestion errors**: highlight missing files/columns; block downstream steps until fixed.
- **Preprocessing artifacts**: allow participant-level exclusion with audit log.
- **Training instability**: fallback to benchmark model and suggest hyperparameter presets.
- **Plugin inference failure**: show degraded mode with reconnect/reload model actions.

---

## 7) Performance Targets (Suggested)
- Web preprocessing stage feedback update interval: every 250–500 ms.
- Rhino local inference target: p95 under 500 ms for single geometry updates.
- UI feedback latency target after geometry change: under 150 ms for panel refresh.

---

## 8) Acceptance Criteria
- Researcher can complete ingestion → preprocessing → mapping → training → ONNX export in one guided flow.
- Architect can iterate geometry and receive continuously updated affective predictions in-plugin.
- Both surfaces share a consistent model schema and versioning contract.
- Error states are explicit, actionable, and do not silently fail.
