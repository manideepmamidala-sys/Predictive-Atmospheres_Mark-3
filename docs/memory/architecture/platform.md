---
type: memory
description: "Python research pipeline, reviewed signal evidence, versioned exports, trusted fused-model artifact, shared room contract and live API."
---
# Platform Architecture

**Domain**: architecture

## Overview

`backend/src/pa/` owns source ingestion, conditional signal processing and review integration, constructed affect, room features, grouped evaluation, model persistence, research exports and the FastAPI service. The [website](/architecture/website.md) reads versioned static products for research and calls `/v1` only for Design Studio prediction and search. Original inputs remain under `data/`; derived results and the fitted model remain under `artifacts/`.

## Requirements

### Source and export boundary

`data/MANIFEST.sha256` verifies retained originals. The pipeline writes audit, signal, reviewed QC, affect, validity, model and comparator results; six website products and a joined bundle; and a 28-product analysis catalogue with a hash manifest. Strict browser staging validates schemas, paths and product hashes. The catalogue contains 27 available products and an explicit unavailable P4 because the selected estimator is constant. The larger Signals browser product loads on its route; full-rate recordings and detailed analysis products remain outside the browser bundle. Generated products carry method, approved-specification and source provenance. The [analysis memory](/research/analysis.md) records scientific eligibility and limits.

Each public trial carries separate automated and reviewed status, reasons and decision provenance for timebase, right EEG, left EEG, bilateral EEG, heart rate and RMSSD. Final eligibility reconciles with the approved CP-B ledger; an uncertain or rejected component remains unavailable. Heart rate and RMSSD have independent gates, so eligible heart rate does not imply eligible RMSSD. See the [data card](../../data_card.md) and [CP-B record](../../reports/revision-2026-10/CP-B.md).

### One room and prediction contract

`RoomInput` contains independent physical and supplied room attributes; optional absent attributes stay missing. One feature builder serves fitting, direct inference, CLI, API and constrained search. Studio prediction requires complete Experiment 3 independent inputs, without filling absent Experiment 1 or 2 fields. Physical validity and empirical studied support are separate: support checks eleven observed numeric inputs, including both opening counts, and observed day/night and space-type combinations. Unsupported inputs receive explicit status rather than an accuracy guarantee.

The trusted artifact contains fitted preprocessing, an estimator, ordered features, training-fold target calibration and provenance hashes. The current E3 artifact selects `dummy_mean` and returns the same constructed fused point, `[0.19933647676353913, -0.07416070665631107]`, for different valid rooms. Its status is `baseline_only`; it establishes no learned spatial gain. Prediction retains raw and clipped coordinates. For a visitor-selected signed target `t`, the API returns `clip(1 − ||clipped prediction − t|| / sqrt(8), 0, 1)` on a 0–1 scale; the Studio displays 0–100. The requested numerical score for generation is a separate 0–100 input. Search minimizes absolute achieved-versus-requested score difference over physically valid, empirically supported candidates, respecting locks, ranges and categorical constraints. A seeded search ranks ties by support distance and stable room-field order and may return an explicit empty result; it does not guarantee a global optimum.

### Trusted service boundary

The loader checks artifact metadata, schema, package versions, code/data/specification/decision/lock hashes and model bytes before trusted deserialization. The service never fits during a request. `/v1/health` separates process liveness from `ready`; `/v1/meta` reports status and limitations. `/v1/predict` and `/v1/optimize` return structured unavailable errors when the artifact is absent or incompatible. The [model card](../../model_card.md) defines the fitted cohort, evaluation and score interpretation.

## Design Decisions

### Shared physical and predictive contract

**Decision**: Use one validated room input and feature builder across model fitting, direct inference, CLI, API and optimization.
**Why**: Predictions and search need the same independent inputs and derived geometry.
**Rejected**: Separately supplied derived geometry or endpoint-specific feature calculations that can contradict source attributes.
*Introduced by*: 261008-ymhz-research-platform-rebuild

### Fitted artifact compatibility gate

**Decision**: Treat fitted model files as trusted local artifacts and validate their metadata and bytes before loading.
**Why**: Served predictions must correspond to the recorded source, methods and artifact.
**Rejected**: Request-time refitting or permissive loading of stale or malformed artifacts.
*Introduced by*: 261008-ymhz-research-platform-rebuild

### Separate reviewed components in public evidence

**Decision**: Export automated and CP-B-reviewed status and reasons for each signal component, including heart rate and RMSSD independently.
**Why**: A single trial flag hides which measurements survive review and can imply an invalid cardiac or bilateral result is available.
**Rejected**: Inferring component quality in the browser from a combined eligibility flag.
*Introduced by*: 261010-tadj-research-atlas-design-studio

### Closest requested score under constraints

**Decision**: Keep the emotional target point separate from a requested numerical Neuro-Score and rank feasible candidates by absolute score difference.
**Why**: A requested score describes a numerical goal, while the target point defines what proximity means.
**Rejected**: Maximizing score regardless of the requested value or silently relaxing locks and ranges.
*Introduced by*: 261010-tadj-research-atlas-design-studio
