---
type: memory
description: "Pinned source verification, v1.2 clean scientific reproduction, final-source replay, artifact drift checks, local validation and candidate hosting boundaries."
---
# Reproducibility and Release

**Domain**: operations

## Overview

The root `Makefile` drives setup, source verification, pipeline, lint, tests and site build. Backend `uv.lock` and the frontend lockfile pin dependencies. The [operations guide](../../operations.md) gives commands and environment variables; [release readiness](../../release-readiness.md) records external conditions. The current research pipeline and browser build use preserved originals and validated generated products.

## Requirements

### Preserved source and document boundary

`data/source-inventory.json` and `data/MANIFEST.sha256` identify 313 retained originals: 160 recordings, seven metadata CSVs, thirty room renders and 116 historical site assets. `python3 scripts/build_source_manifest.py --check` verifies their hashes. Browser WebP room previews are derivatives. Project-tree duplicate thesis PDFs and the booklet ZIP were removed only after their bytes and relevant Windows originals were verified and their research context captured in [thesis source context](../../research/thesis-source-context.md). The DOCX text lacks a verified exact external original, so it remains untracked and outside the public manifest/site. There was no Git-history purge. The [source inventory](../../reports/revision-2026-10/source-inventory.md) records hashes and cleanup decisions.

### Rebuild and drift checks

`make pipeline` regenerates audit, conditional signal and reviewed QC results, affect, grouped model evaluation, fitted artifact, the 28-card catalogue, research exports and API schema. `make site` strictly validates source-product schemas, paths and hashes before staging browser JSON and building the site. CI checks regenerated scientific-artifact drift; model loading checks bytes and source, method, dependency and code provenance. Volatile checkout and elapsed-time fields are excluded only by declared comparison rules. A method or source change requires an approved decision, affected reruns and updated cards rather than forced old hashes.

The v1.2 source-only clean run reconstructed the approved CP-B ledger byte-for-byte, generated the effective-input guard before draw zero, ran all 1,000 fresh full-refit spatial-null draws and 455 unique learning subsets, and passed `make all` with exit code zero. The comparator matched 53 result JSON products, fitted metadata and model bytes at `1e-8` absolute/relative tolerance. Its temporary source snapshot digest is `936cd86add14e0406dc563d97a5d536a41b5d33b036b5008f3bb4b245d2dcc93`. The [validation record](../../reports/revision-2026-10/validation.md) identifies its logs and exact scope.

A subsequent final-source replay used clean scientific artifacts from that run and refreshed public QC/Methods exports, model code provenance and POC after review corrections. Its source-input digest is `f6a5420fe9f5dad42684d3dcdd82100359ce6a919a7d5d47089e03ad4a0c4ed5`. It passed lint/site and 123 backend tests and matched the final checkout's 53 JSON products and model bytes. It did not repeat the 1,000 null draws or 455 subset fits. The numerical evaluation and serialized model bytes remained unchanged; the [CP-C receipt](../../reports/revision-2026-10/CP-C.md) keeps the `baseline_only` limit attached to the final artifact.

### Local site, API and release status

Final local checks passed source verification, lint, strict site staging/build, 123 backend tests, 32 browser tests with two expected opt-in live skips, and two separately enabled live Studio tests. The approved screenshot manifest hashes 80 captures; Lighthouse 13.5.0 reported accessibility 100 on each of eight built routes. Independent [CP-E2](../../reports/revision-2026-10/CP-E2.md) records its delegated presentation check. A local no-dev API install loaded the trusted model and returned `ready=true` and `model_status=baseline_only`; local RSS was 215,688 KiB. These are local checks, not hosted service results.

`frontend/vercel.json` and `render.yaml` configure Vercel Hobby static-site and Render Free API **candidates**. The static atlas remains readable during API cold starts; Studio exposes unavailability. [Hosting assessment](../../reports/revision-2026-10/hosting-assessment.md) records dated provider constraints and local asset measurements. No production deployment, custom domain, DOI or new license is established by the configuration. The repository is public and the owner authorized public research recordings, metadata, renders and results. Named biometric association lacks a verified participant-name mapping and specific permission; code/data/asset licenses and third-party rights require separate release decisions. Hosted readiness requires actual build, origin/CORS, API, memory, cold-start and asset checks at the deployed URLs.

## Design Decisions

### Preserve originals and verify derived products

**Decision**: Keep original inputs checksum-addressable and regenerate products with pinned tools and recorded methods.
**Why**: Source or method changes must be traceable through eligibility, model evaluation and browser claims.
**Rejected**: Treating historical figures or an unverified saved model as reproducible current evidence.
*Introduced by*: 261008-ymhz-research-platform-rebuild

### Candidate hosting with explicit readiness

**Decision**: Keep static research reading independent of API readiness and label hosting files as deployment candidates.
**Why**: Free-tier service availability and external account behavior cannot be established by a local build.
**Rejected**: Claiming a deployed or validated hosted model service from configuration files alone.
*Introduced by*: 261008-ymhz-research-platform-rebuild

### Separate fresh scientific and final-source evidence

**Decision**: Record the clean full-control reproduction and the targeted final-source replay with distinct source digests and execution scopes.
**Why**: Presentation/provenance corrections changed source identity after the fresh numerical run while leaving the approved scientific computation unchanged.
**Rejected**: Calling artifact reuse a second fresh null run or treating the earlier source digest as the final checkout identity.
*Introduced by*: 261010-tadj-research-atlas-design-studio
