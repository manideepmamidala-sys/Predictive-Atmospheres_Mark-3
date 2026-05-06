# Backend Schema — Predictive Atmospheres

## 1) Purpose
This document defines a backend schema for the project across three layers:
1. Training storage schema (research data and extracted features)
2. Inference API contract (Rhino/Streamlit to model service)
3. Model tensor schema (PyTorch and ONNX runtime inputs/outputs)

It is designed for both:
- Local-first workflow (CSV/Parquet/Pandas)
- Relational deployment (PostgreSQL)

---

## 2) Scope and Alignment with Current Project
This schema aligns with the current repository workflow:
- Raw biometric recordings in data/raw
- Room/experiment metadata in data/metadata
- Processed artifacts in data/processed and artifacts/reports
- Training/inference through src/data, src/models, and src/services

Current metadata format (split files per experiment):
- `experiment_XX_spatial data.csv`
- `experiment_XX_biometric data.csv`

Join key between the two metadata files: `Room_ID`.

Experiment lifecycle note:
- Future experiments can exist in `planned/template` state with partial or empty values before collection begins.

---

## 3) Canonical Entity Relationship Model

Core entities:
- Participants
- Spatial_Environments
- Biometric_Trials
- Spatial_Metadata_Staging
- Biometric_Metadata_Staging
- Experiment_Registry
- Extracted_Features
- Model_Runs
- Model_Artifacts
- Inference_Requests
- Inference_Results

High-level relations:
- One Participant has many Biometric_Trials
- One Spatial_Environment has many Biometric_Trials
- One Biometric_Trial has one Extracted_Features record (versioned extension possible)
- One Model_Run has many Model_Artifacts
- One Inference_Request has one Inference_Result

---

## 4) Training Storage Schema (Relational)

### 4.1 participants
Purpose: Baseline physiological profile and demographic context for normalization.

Fields:
- participant_id UUID PRIMARY KEY
- age INTEGER CHECK (age BETWEEN 5 AND 120)
- baseline_hrv DOUBLE PRECISION CHECK (baseline_hrv >= 0)
- baseline_eeg_alpha DOUBLE PRECISION CHECK (baseline_eeg_alpha >= 0)
- created_at TIMESTAMPTZ NOT NULL DEFAULT now()
- updated_at TIMESTAMPTZ NOT NULL DEFAULT now()

Indexes:
- idx_participants_age ON age

---

### 4.2 spatial_environments
Purpose: Independent spatial variables (X) for each tested design condition.

Fields:
- environment_id UUID PRIMARY KEY
- environment_name TEXT
- length_m DOUBLE PRECISION NOT NULL CHECK (length_m > 0)
- width_m DOUBLE PRECISION NOT NULL CHECK (width_m > 0)
- height_m DOUBLE PRECISION NOT NULL CHECK (height_m > 0)
- volume_m3 DOUBLE PRECISION GENERATED ALWAYS AS (length_m * width_m * height_m) STORED
- window_wall_ratio DOUBLE PRECISION CHECK (window_wall_ratio >= 0 AND window_wall_ratio <= 1)
- aspect_ratio DOUBLE PRECISION CHECK (aspect_ratio > 0)
- metadata JSONB DEFAULT '{}'::jsonb
- created_at TIMESTAMPTZ NOT NULL DEFAULT now()
- updated_at TIMESTAMPTZ NOT NULL DEFAULT now()

Indexes:
- idx_spatial_volume ON volume_m3
- idx_spatial_wwr ON window_wall_ratio

---

### 4.3 biometric_trials
Purpose: Junction between participant and environment, including raw file pointers and labels.

Fields:
- trial_id UUID PRIMARY KEY
- participant_id UUID NOT NULL REFERENCES participants(participant_id)
- environment_id UUID NOT NULL REFERENCES spatial_environments(environment_id)
- trial_timestamp TIMESTAMPTZ
- raw_eeg_filepath TEXT NOT NULL
- raw_ecg_filepath TEXT
- sample_rate_hz INTEGER CHECK (sample_rate_hz > 0)
- time_spent_seconds INTEGER CHECK (time_spent_seconds > 0)
- self_reported_score_0_10 DOUBLE PRECISION CHECK (self_reported_score_0_10 >= 0 AND self_reported_score_0_10 <= 10)
- self_reported_valence_0_10 DOUBLE PRECISION CHECK (self_reported_valence_0_10 >= 0 AND self_reported_valence_0_10 <= 10)
- self_reported_arousal_0_10 DOUBLE PRECISION CHECK (self_reported_arousal_0_10 >= 0 AND self_reported_arousal_0_10 <= 10)
- derived_valence DOUBLE PRECISION CHECK (derived_valence >= -1.0 AND derived_valence <= 1.0)
- derived_arousal DOUBLE PRECISION CHECK (derived_arousal >= -1.0 AND derived_arousal <= 1.0)
- quality_flag TEXT CHECK (quality_flag IN ('ok','warning','artifacted','rejected')) DEFAULT 'ok'
- notes TEXT
- created_at TIMESTAMPTZ NOT NULL DEFAULT now()
- updated_at TIMESTAMPTZ NOT NULL DEFAULT now()

Indexes:
- idx_trials_participant ON participant_id
- idx_trials_environment ON environment_id
- idx_trials_timestamp ON trial_timestamp

---

### 4.4 extracted_features
Purpose: Processed feature table used directly for model training.

Fields:
- feature_id UUID PRIMARY KEY
- trial_id UUID NOT NULL UNIQUE REFERENCES biometric_trials(trial_id)
- pipeline_version TEXT NOT NULL
- eeg_frontal_alpha_asymmetry DOUBLE PRECISION
- eeg_beta_power DOUBLE PRECISION
- eeg_theta_power DOUBLE PRECISION
- eeg_alpha_power DOUBLE PRECISION
- ecg_rmssd DOUBLE PRECISION CHECK (ecg_rmssd >= 0)
- ecg_sdnn DOUBLE PRECISION CHECK (ecg_sdnn >= 0)
- ecg_mean_hr DOUBLE PRECISION CHECK (ecg_mean_hr >= 0)
- feature_vector JSONB NOT NULL DEFAULT '{}'::jsonb
- created_at TIMESTAMPTZ NOT NULL DEFAULT now()

Indexes:
- idx_features_trial ON trial_id
- idx_features_pipeline_version ON pipeline_version

---

### 4.4a spatial_metadata_staging
Purpose: Raw ingest table mirroring `experiment_XX_spatial data.csv` before normalization.

Fields:
- staging_id UUID PRIMARY KEY
- experiment_id TEXT NOT NULL
- room_id TEXT NOT NULL
- length_meter DOUBLE PRECISION CHECK (length_meter > 0)
- width_meter DOUBLE PRECISION CHECK (width_meter > 0)
- height_meter DOUBLE PRECISION CHECK (height_meter > 0)
- dynamic_spatial_attributes JSONB NOT NULL DEFAULT '{}'::jsonb
- source_file TEXT NOT NULL
- ingested_at TIMESTAMPTZ NOT NULL DEFAULT now()

Note:
- In `planned` experiments, dimension fields may be null (template rows).
- In `ready/collected` experiments, dimension fields are required and must be positive.

Indexes:
- idx_spatial_staging_exp_room ON (experiment_id, room_id)

---

### 4.4b biometric_metadata_staging
Purpose: Raw ingest table mirroring `experiment_XX_biometric data.csv` before normalization.

Fields:
- staging_id UUID PRIMARY KEY
- experiment_id TEXT NOT NULL
- subject_id TEXT NOT NULL
- room_id TEXT NOT NULL
- time_spent_seconds INTEGER CHECK (time_spent_seconds > 0)
- eeg_filename TEXT
- score_by_subject_0_10 DOUBLE PRECISION CHECK (score_by_subject_0_10 >= 0 AND score_by_subject_0_10 <= 10)
- valence_score_0_10 DOUBLE PRECISION CHECK (valence_score_0_10 >= 0 AND valence_score_0_10 <= 10)
- arousal_score_0_10 DOUBLE PRECISION CHECK (arousal_score_0_10 >= 0 AND arousal_score_0_10 <= 10)
- dynamic_biometric_attributes JSONB NOT NULL DEFAULT '{}'::jsonb
- source_file TEXT NOT NULL
- ingested_at TIMESTAMPTZ NOT NULL DEFAULT now()

Note:
- In `planned` experiments, `eeg_filename` and label fields may be null.
- In `ready/collected` experiments, `eeg_filename` is required and at least one label strategy must exist:
  - legacy combined score (`score_by_subject_0_10`), or
  - split labels (`valence_score_0_10` and `arousal_score_0_10`).

Indexes:
- idx_biometric_staging_exp_room ON (experiment_id, room_id)
- idx_biometric_staging_subject ON subject_id

---

### 4.4c experiment_registry
Purpose: Tracks whether an experiment is planned, ready, or already collected/processed.

Fields:
- experiment_id TEXT PRIMARY KEY
- status TEXT NOT NULL CHECK (status IN ('planned','ready','collected','processed','archived'))
- spatial_metadata_file TEXT NOT NULL
- biometric_metadata_file TEXT NOT NULL
- notes TEXT
- created_at TIMESTAMPTZ NOT NULL DEFAULT now()
- updated_at TIMESTAMPTZ NOT NULL DEFAULT now()

Indexes:
- idx_experiment_registry_status ON status

---

### 4.5 model_runs
Purpose: Reproducibility and model lineage.

Fields:
- run_id UUID PRIMARY KEY
- run_name TEXT
- model_type TEXT NOT NULL CHECK (model_type IN ('pytorch_mlp','random_forest','svm','ridge','other'))
- framework_version TEXT
- data_snapshot_ref TEXT
- train_split_ref TEXT
- hyperparameters JSONB NOT NULL DEFAULT '{}'::jsonb
- metrics JSONB NOT NULL DEFAULT '{}'::jsonb
- status TEXT NOT NULL CHECK (status IN ('queued','running','completed','failed'))
- started_at TIMESTAMPTZ
- completed_at TIMESTAMPTZ
- created_at TIMESTAMPTZ NOT NULL DEFAULT now()

Indexes:
- idx_model_runs_status ON status
- idx_model_runs_started_at ON started_at

---

### 4.6 model_artifacts
Purpose: Track exported model binaries and associated scaler/schema.

Fields:
- artifact_id UUID PRIMARY KEY
- run_id UUID NOT NULL REFERENCES model_runs(run_id)
- artifact_type TEXT NOT NULL CHECK (artifact_type IN ('onnx','torchscript','pytorch_state_dict','scaler','schema','report'))
- artifact_uri TEXT NOT NULL
- artifact_hash TEXT
- is_active BOOLEAN NOT NULL DEFAULT false
- created_at TIMESTAMPTZ NOT NULL DEFAULT now()

Indexes:
- idx_artifacts_run_id ON run_id
- idx_artifacts_active ON is_active

---

### 4.7 inference_requests
Purpose: Audit request payloads from Rhino/Streamlit surfaces.

Fields:
- request_id UUID PRIMARY KEY
- source_surface TEXT NOT NULL CHECK (source_surface IN ('rhino','streamlit','api','other'))
- model_artifact_id UUID REFERENCES model_artifacts(artifact_id)
- geometry_data JSONB NOT NULL
- requested_at TIMESTAMPTZ NOT NULL DEFAULT now()

Indexes:
- idx_inference_requests_source ON source_surface
- idx_inference_requests_time ON requested_at

---

### 4.8 inference_results
Purpose: Store prediction outputs and latency.

Fields:
- result_id UUID PRIMARY KEY
- request_id UUID NOT NULL UNIQUE REFERENCES inference_requests(request_id)
- processing_time_ms INTEGER CHECK (processing_time_ms >= 0)
- valence DOUBLE PRECISION CHECK (valence >= -1.0 AND valence <= 1.0)
- arousal DOUBLE PRECISION CHECK (arousal >= -1.0 AND arousal <= 1.0)
- dominant_emotion TEXT
- confidence_scores JSONB NOT NULL DEFAULT '{}'::jsonb
- created_at TIMESTAMPTZ NOT NULL DEFAULT now()

Indexes:
- idx_inference_results_valence ON valence
- idx_inference_results_arousal ON arousal

---

## 5) Local DataFrame / File Schema (Pandas + Parquet)

Minimum canonical DataFrames:

spatial_metadata_raw_df columns:
- Room_ID, Length (meter), Width (meter), Height (meter)
- Plus optional spatial columns (stored in `dynamic_spatial_attributes` if not mapped to canonical fields)

biometric_metadata_raw_df columns:
- Subject_ID, Room_ID, Time spent by the subject in the room (seconds), EEG_Filename
- Label options:
  - Legacy: Score by Subject_(0-10)
  - Preferred: Valence Score by Subject (0-10), Arousal Score by Subject (0-10)
- Plus optional biometric columns (stored in `dynamic_biometric_attributes` if not mapped to canonical fields)

participants_df columns:
- participant_id, age, baseline_hrv, baseline_eeg_alpha

spatial_environments_df columns:
- environment_id, environment_name, length_m, width_m, height_m, volume_m3, window_wall_ratio, aspect_ratio

biometric_trials_df columns:
- trial_id, participant_id, environment_id, raw_eeg_filepath, raw_ecg_filepath, time_spent_seconds, self_reported_score_0_10, self_reported_valence_0_10, self_reported_arousal_0_10, derived_valence, derived_arousal, quality_flag

extracted_features_df columns:
- trial_id, pipeline_version, eeg_frontal_alpha_asymmetry, eeg_beta_power, ecg_rmssd, plus additional engineered features

Storage recommendation:
- Use Parquet for all processed/intermediate tables
- Keep raw path references as relative project paths where possible
- Use one manifest table per experiment for deterministic rebuilds
- Always merge spatial and biometric metadata on `Room_ID` before generating training rows

---

## 6) Inference Data Contract (API Schema)

### 6.1 Request: SpatialInput
JSON shape:

{
  "geometry_data": {
    "length": 12.5,
    "width": 8.0,
    "height": 3.2,
    "volume": 320.0,
    "window_to_wall_ratio": 0.25,
    "aspect_ratio": 1.56
  },
  "context": {
    "model_version": "2026.03.03-mlp-v1",
    "source": "rhino"
  }
}

Validation rules:
- length, width, height > 0
- volume > 0
- window_to_wall_ratio in [0, 1]
- aspect_ratio > 0
- If volume is provided, optionally verify near-equality to length * width * height within tolerance

### 6.2 Response: AffectiveOutput
JSON shape:

{
  "prediction_id": "req-98765",
  "processing_time_ms": 42,
  "dimensional_affect": {
    "valence": 0.65,
    "arousal": -0.20
  },
  "categorical_affect": {
    "dominant_emotion": "Calm",
    "confidence_scores": {
      "Calm": 0.78,
      "Focused": 0.15,
      "Anxious": 0.05,
      "Bored": 0.02
    }
  },
  "model_info": {
    "model_version": "2026.03.03-mlp-v1",
    "runtime": "onnx"
  }
}

Validation rules:
- valence and arousal in [-1, 1]
- confidence_scores values in [0, 1]
- confidence_scores sum approximately 1.0 (tolerance allowed)
- processing_time_ms >= 0

---

## 7) Pydantic Reference Models (FastAPI)

SpatialInput model:
- geometry_data: GeometryData
- context: optional PredictionContext

GeometryData fields:
- length: float > 0
- width: float > 0
- height: float > 0
- volume: float > 0
- window_to_wall_ratio: float >= 0 and <= 1
- aspect_ratio: float > 0

AffectiveOutput model:
- prediction_id: string
- processing_time_ms: int >= 0
- dimensional_affect: DimensionalAffect
- categorical_affect: CategoricalAffect
- model_info: optional ModelInfo

DimensionalAffect fields:
- valence: float in [-1, 1]
- arousal: float in [-1, 1]

CategoricalAffect fields:
- dominant_emotion: string
- confidence_scores: dict<string, float>

---

## 8) Model Tensor Schema (PyTorch / ONNX)

### 8.1 Input Tensor
- Shape: [1, N]
- N = number of spatial features (typically 6)
- Dtype: float32
- Preprocessing: z-score normalization using saved training scaler
- Feature order (strict):
  1) length
  2) width
  3) height
  4) volume
  5) window_to_wall_ratio
  6) aspect_ratio

### 8.2 Output Tensor (Regression)
- Shape: [1, 2]
- Dtype: float32
- Semantics:
  - index 0 = valence
  - index 1 = arousal

### 8.3 Output Tensor (Classification)
- Shape: [1, K]
- Dtype: float32
- Softmax probabilities over K emotion categories
- Sum over K should be approximately 1.0

### 8.4 Runtime Safeguards
- Reject NaN/Inf inputs before tensor conversion
- Enforce feature-order checksum/version in model metadata
- Log scaler version + model version with each prediction

---

## 9) Suggested SQL DDL Snippet (Starter)

CREATE TABLE participants (...);
CREATE TABLE spatial_environments (...);
CREATE TABLE biometric_trials (...);
CREATE TABLE spatial_metadata_staging (...);
CREATE TABLE biometric_metadata_staging (...);
CREATE TABLE experiment_registry (...);
CREATE TABLE extracted_features (...);
CREATE TABLE model_runs (...);
CREATE TABLE model_artifacts (...);
CREATE TABLE inference_requests (...);
CREATE TABLE inference_results (...);

Note: Implement exact DDL from section definitions with checks and indexes in migration files.

---

## 10) Data Quality and Constraints
- Every biometric_trials row must map to exactly one participant and one environment.
- Every extracted_features row must map to one valid trial and pipeline_version.
- `self_reported_score_0_10` must remain in [0, 10].
- If split labels are present, `self_reported_valence_0_10` and `self_reported_arousal_0_10` must remain in [0, 10].
- For `ready/collected` trials, enforce label completeness as either:
  - legacy combined score, or
  - both split valence and split arousal scores.
- If derived dimensional labels are used, `derived_valence` and `derived_arousal` must remain in [-1, 1].
- Artifacted sessions should be flagged, not silently dropped.
- Planned template experiments are allowed to contain null optional values but must be marked `planned` until required training fields are complete.
- All model exports must include:
  - model file
  - scaler parameters
  - feature order schema
  - training run identifier

---

## 11) Versioning and Migration Policy
- Use schema_version in metadata tables or migration tooling (Alembic recommended).
- Breaking change rules:
  - Increment major schema version
  - Provide compatibility transform scripts for old Parquet/CSV snapshots
- Model compatibility:
  - Inference service must verify incoming feature schema matches active model artifact

---

## 12) Definition of Done (Backend Schema)
- Relational tables or equivalent DataFrame schemas exist for all entities above.
- API request/response validation blocks malformed payloads.
- Model runtime receives fixed-order normalized tensors only.
- Inference and training runs are auditable by ID, artifact, and version.
- Schema supports both current local workflow and future service deployment.
