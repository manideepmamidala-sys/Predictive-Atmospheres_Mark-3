---
type: memory
description: "Python research pipeline, validated room schema, versioned exports, fitted artifact, and live API boundaries."
---
# Platform Architecture

**Domain**: architecture

## Overview

`backend/src/pa/` owns source ingestion, acquisition audit, signal and affect analysis, room features, grouped evaluation, model persistence, scoring, optimization, research exports and the FastAPI service. Preserved inputs live under `data/`; derived results and the fitted model live under `artifacts/`. The [website](/architecture/website.md) consumes the exports and API.

## Requirements

### Reproducible data boundary

`data/MANIFEST.sha256` identifies original source bytes. Pipeline outputs include versioned research JSON, `artifacts/results/manifest.json`, OpenAPI and room-input schema, and `artifacts/model/model.joblib` with compatibility metadata. Generated browser products are checked against their manifest before the site build. Source files and derived presentation assets remain distinct.

### One room and inference contract

`RoomInput` accepts independent physical and supplied room attributes; missing optional attributes stay unavailable. The shared feature builder derives ratios and geometry for training and inference. Physical validation and empirical studied support are separate. Support uses eleven observed numeric inputs, including both opening counts, plus observed day/night and space-type combinations; missing values or out-of-range values receive explicit status. A user-selected signed valence/arousal target drives Neuro-Score, `clip(1 - distance / sqrt(8), 0, 1)`.

### Artifact and service behavior

The saved artifact includes fitted preprocessing, estimator, ordered features, training target calibration and provenance hashes. The loader checks public metadata fields, schema, package versions, code/data/specification/decision/lock hashes and model bytes before trusted deserialization. `/v1/health` separates process liveness from model readiness; `/v1/meta` reports status and limitations. `/v1/predict` and `/v1/optimize` return structured unavailable errors when the artifact is missing or incompatible. The service does not fit at request time.

## Design Decisions

### Shared physical and predictive contract

**Decision**: Use one validated room input and feature builder across model fitting, direct inference, CLI, API and optimization.
**Why**: The same independent inputs and derived features are required for reproducible predictions and physically valid search.
**Rejected**: Separately supplied derived geometry or parallel endpoint-specific feature calculations, which can contradict source attributes.
*Introduced by*: 261008-ymhz-research-platform-rebuild

### Fitted artifact compatibility gate

**Decision**: Treat fitted model files as trusted local artifacts and validate their metadata and bytes before loading.
**Why**: Readiness and displayed model evidence must correspond to the source, methods and artifact actually served.
**Rejected**: Startup refitting or permissive loading of stale or malformed artifacts, which would obscure the model used for a response.
*Introduced by*: 261008-ymhz-research-platform-rebuild
