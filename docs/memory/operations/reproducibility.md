---
type: memory
description: "Pinned local reproduction, source and artifact checks, CI, hosting candidates, and release evidence boundaries."
---
# Reproducibility and Release

**Domain**: operations

## Overview

The root `Makefile` drives setup, source verification, pipeline, lint, tests and site build. Backend `uv.lock` and frontend lockfile pin dependencies; CI runs local quality and browser checks. The [operations guide](../../operations.md) gives commands and environment variables; [release readiness](../../release-readiness.md) records external conditions.

## Requirements

### Local reproduction

`make verify-data` checks preserved source bytes. `make pipeline` regenerates audit, conditional signal and affect results, grouped model evaluation, fitted artifact, research exports and API schema. `make site` checks generated product hashes before staging browser JSON and building the frontend. A clean source-snapshot `make all` run passed 80 backend tests, 25 browser tests with one intentional live-API skip, and the production build. Fifteen JSON products and model metadata matched reference outputs within 1e-8 absolute/relative tolerance; model bytes matched exactly. See [reproduction evidence](../../reports/reproduction.md).

### Hosting and publication

`render.yaml` is a free-tier Python API candidate and `frontend/vercel.json` is a static SPA candidate. Local builds and service checks do not establish a hosted deployment. The repository is already public and the owner authorized public source recordings, metadata, renders and results. Final code/data/asset licensing scope, DOI registration, hosting account limits and named biometric association are separate release decisions; no verified participant-name mapping or specific named-recording permission is documented. Existing third-party rights remain in scope.

## Design Decisions

### Preserve originals and verify derived products

**Decision**: Keep original inputs checksum-addressable and regenerate products with pinned tools and recorded method decisions.
**Why**: A source or method change must be traceable through signal eligibility, model evaluation and browser claims.
**Rejected**: Treating historical generated figures or an unverified saved model as reproducible current evidence.
*Introduced by*: 261008-ymhz-research-platform-rebuild

### Candidate hosting with explicit readiness

**Decision**: Keep static research reading independent of API readiness and label hosting files as deployment candidates.
**Why**: Free-tier service availability and external account settings cannot be established by a local build.
**Rejected**: Claiming deployment or validated model service from configuration files alone.
*Introduced by*: 261008-ymhz-research-platform-rebuild
