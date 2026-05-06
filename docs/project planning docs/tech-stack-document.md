# Tech Stack Document — Predictive Atmospheres (2026)

## 1) Purpose
This document proposes a production-ready tech stack for a neuro-architecture affective prediction platform that ingests EEG/ECG + spatial metadata, trains ML models, provides interactive analytics, and integrates with Rhino/Grasshopper for design-time feedback.

It incorporates your requested stack and extends it with updated recommendations for reliability, reproducibility, performance, and long-term maintainability.

---

## 2) Guiding Principles
- **Scientific validity first**: preserve reproducibility and traceability from raw signal to prediction.
- **Fast design loop**: near-real-time inference for geometry iteration.
- **Modular architecture**: independent evolution of UI, ML training, and CAD integration.
- **Deployment flexibility**: run locally for thesis/lab use, and scale to shared server later.
- **LLM-augmented workflows**: support literature synthesis, experiment QA, and explainability summaries.

---

## 3) Recommended Stack (Target)

### 3.1 Core Data Processing & Machine Learning
- **Language**: Python 3.11 (minimum 3.10)
- **Numerical stack**: NumPy, SciPy, Pandas
- **EEG processing**: MNE-Python
- **ECG/HRV processing**: NeuroKit2
- **ML/DL framework**: PyTorch
- **Classical ML baselines**: scikit-learn (Random Forest, SVM, Ridge, calibration)
- **Feature store format**: Parquet + Arrow
- **Experiment tracking**: MLflow (metrics, artifacts, model registry)
- **Data/version lineage**: DVC (or LakeFS if scaling team-wide)
- **Config management**: Pydantic Settings + YAML profiles (dev/lab/prod)
- **Metadata ingestion contract**: split CSV adapter (`*_spatial data.csv` + `*_biometric data.csv`) merged by `Room_ID`
- **Schema evolution policy**: core required columns + extensible optional columns auto-captured as dynamic features

### 3.2 Web Application & Visual Analytics
- **Primary app framework**: Streamlit (rapid research UI and operations dashboard)
- **Interactive charts**: Plotly (3D mesh, radar, dark-theme, high interactivity)
- **Declarative statistical charts**: Altair (distribution plots, model diagnostics)
- **State/caching**: Streamlit cache + Redis (optional when multi-user)
- **UI design system**: tokenized dark theme with purple-first color-theory rules (semantic colors, spacing, typography)

### 3.3 Backend API & Real-Time Inference Layer
- **API framework**: FastAPI
- **Server runtime**: Uvicorn/Gunicorn (depending on Windows/Linux host)
- **Inference serialization**:
  - Primary: TorchScript for tight PyTorch integration
  - Alternative: ONNX Runtime for lower-latency cross-platform serving
- **Schema contracts**: Pydantic request/response models
- **Async jobs**: Celery + Redis (for long training jobs and report generation)

### 3.4 Architectural Integration (Rhino)
- **Rapid prototyping**: Grasshopper + Hops to call FastAPI endpoints
- **Production plugin**: C# + RhinoCommon API
- **Communication**: async HTTP/gRPC calls to inference API
- **Geometry contract**: normalized JSON schema (dimensions, topology descriptors, constraints)

### 3.5 Data Layer
- **Primary analytics storage**: Parquet files (columnar, fast, reproducible)
- **Local analytical DB**: DuckDB (excellent for research-scale OLAP over Parquet)
- **Operational metadata DB**: PostgreSQL (runs, users, scenario snapshots)
- **Object storage (optional scale)**: S3/MinIO for models and larger artifacts

### 3.6 MLOps, Quality, and Observability
- **Training orchestration**: Prefect (lightweight) or Airflow (if enterprise scheduling needed)
- **Testing**: Pytest + Hypothesis (property-based tests for signal transformations)
- **Static checks**: Ruff + MyPy + pre-commit
- **Monitoring**:
  - App/API: Prometheus + Grafana
  - Logs: OpenTelemetry + Loki/ELK
  - Model drift: Evidently AI

### 3.7 Containerization & Environments
- **Packaging**: Poetry or uv + pyproject.toml
- **Containerization**: Docker + Docker Compose
- **GPU option**: CUDA-enabled base images for model training
- **Environment management**: `.env` + secret manager for API keys

### 3.8 LLM-Enabled Capabilities (Recommended)
- **Use cases**:
  - Literature-to-feature mapping assistant
  - Auto-generated experiment QA summaries
  - Human-readable interpretation of model predictions and uncertainty
  - Query assistant over processed runs and reports
- **Architecture**:
  - Retrieval layer over internal docs/research notes (RAG)
  - Guardrails for scientific claims (citation + confidence prompts)
- **Model options**:
  - Cloud APIs (high quality): OpenAI/Anthropic
  - On-prem/local privacy path: Llama 3.x / Mistral via vLLM/Ollama
- **Vector storage**: pgvector (PostgreSQL extension) or Qdrant

---

## 4) Why This Is Better for This Project
- **MNE + NeuroKit2** directly fit EEG/ECG biomedical workflows better than generic signal tools.
- **PyTorch + ONNX/TorchScript** covers both research flexibility and low-latency serving.
- **FastAPI + Streamlit split** avoids forcing Streamlit to do backend-service duties.
- **DuckDB + Parquet** drastically improves local analytics speed and reproducibility for thesis workflows.
- **MLflow + DVC** provides auditability required for publication-quality experiments.
- **Rhino Hops → C# RhinoCommon path** enables fast prototype now, robust plugin later.
- **LLM RAG layer** adds value for interpretation and documentation without compromising scientific pipeline control.
- **Extensible metadata contract** supports future experiments with new spatial/biometric parameters without breaking existing pipelines.

---

## 5) Suggested Reference Architecture
1. Raw EEG/ECG + split metadata CSVs (`experiment_XX_spatial data.csv`, `experiment_XX_biometric data.csv`) ingested to staging storage.
2. Ingestion adapter validates schemas and joins records on `Room_ID`.
3. Preprocessing service (MNE/NeuroKit2) outputs standardized feature tables (Parquet).
4. Training pipeline logs metrics/artifacts to MLflow and versions data/model with DVC.
5. Best model exported as TorchScript/ONNX and deployed behind FastAPI.
6. Streamlit dashboard consumes API + metadata DB for visual analytics.
7. Grasshopper Hops/C# plugin sends geometry to API and receives affective predictions.
8. Monitoring stack tracks API latency, model drift, and run health.

---

## 6) Performance Targets (Recommended)
- Single inference request: **p95 < 500 ms** (API-only, warmed model)
- Batch scenario eval (100 geometries): **< 5 s** (CPU baseline)
- Dashboard first meaningful paint: **< 2.5 s** on lab workstation
- Retraining baseline model: **< 10 min** for current dataset scale

---

## 7) Security, Privacy, and Compliance Baseline
- Store only pseudonymized subject IDs in operational stores.
- Encrypt model/data artifacts at rest on shared infrastructure.
- Restrict API with token-based auth for Rhino clients.
- Log data access and model export actions for audit.
- LLM outputs must include uncertainty framing and no clinical diagnosis wording.

---

## 8) Implementation Plan (Pragmatic)

### Phase A — Foundation (1–2 weeks)
- Standardize environment to Python 3.11
- Add Ruff/MyPy/pre-commit
- Introduce MLflow tracking
- Move processed outputs to Parquet + DuckDB

### Phase B — Service Split (1–2 weeks)
- Introduce FastAPI inference service
- Add TorchScript/ONNX export path
- Point Streamlit prediction calls to API contracts

### Phase C — CAD Bridge (2–3 weeks)
- Implement Grasshopper Hops endpoints
- Define geometry JSON contract + validation
- Add async inference queue for heavy requests

### Phase D — Production Hardening (2 weeks)
- Add Prometheus/Grafana + drift monitoring
- Add auth, rate limiting, structured logs
- Optimize latency and stress-test concurrency

### Phase E — LLM Augmentation (optional, 1–2 weeks)
- Build RAG index over docs/reports
- Add experiment-summary assistant
- Add citation-aware response templates

---

## 9) Tooling Decision Matrix

| Layer | Recommended | Alternative | Use Recommended When |
|---|---|---|---|
| EEG Processing | MNE-Python | SciPy custom | You need robust EEG domain methods |
| ECG Processing | NeuroKit2 | biosppy | You need HRV + clean physiological APIs |
| DL Training | PyTorch | JAX/TensorFlow | You prioritize flexibility and ecosystem fit |
| API | FastAPI | Flask | You need async + typed contracts + speed |
| Model Runtime | TorchScript/ONNX | Pickle joblib | You need safe, performant serving |
| Dashboard | Streamlit | Dash/React | You need rapid iteration with Python-only team |
| Analytics DB | DuckDB | SQLite | You query large Parquet datasets locally |
| Tracking | MLflow | Weights & Biases | You want self-hosted lineage and model registry |
| CAD Integration | Hops + RhinoCommon | Direct scripting only | You need prototype-to-product path |
| LLM Retrieval | pgvector/Qdrant | FAISS local only | You need persistent searchable knowledge |

---

## 10) Minimal Stack if You Need to Ship Fast
- Python 3.11
- MNE-Python, NeuroKit2, NumPy/Pandas
- PyTorch + scikit-learn
- Streamlit + Plotly
- FastAPI + TorchScript
- DuckDB + Parquet
- MLflow
- Grasshopper Hops

This subset is enough for a robust thesis-grade system with clear upgrade paths.

---

## 11) Final Recommendation
Adopt a **two-surface architecture** immediately:
- **Surface 1**: Streamlit for analyst/research UI and visual exploration.
- **Surface 2**: FastAPI inference service for Rhino and future integrations.

Keep the data/ML backbone in Python, enforce reproducibility with MLflow + DVC, and add LLM features only as an explainability/research layer (not as a replacement for deterministic inference).
