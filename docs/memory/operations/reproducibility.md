---
type: memory
description: "Pinned source verification, v1.2 clean scientific reproduction, final-source replay, artifact drift checks, local validation and verified Vercel hosting boundaries."
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

The public atlas and Studio API share https://predictive-atmospheres.vercel.app in the `predictive-atmospheres` Vercel Hobby project under `manideep-personal`. Root `vercel.json` routes `/v1/*` to FastAPI and other paths to the Vite site, with service-local SPA fallback after static-file lookup. Research reproduction uses the canonical Python 3.11 backend project/lock; deployment uses isolated root Python 3.12 requirements and `VERCEL_SUPPORT_LARGE_FUNCTIONS=1`. The trusted model and its scientific source/dependency checks remain intact. Publication uses manual CLI prebuilt deployment; GitHub automatic deployment is not connected. The public production alias requires no login; preview and unique deployment URLs retain Standard protection.

The [deployment report](../../reports/revision-2026-10/deployment.md) records source revision `69e223fa0f42457c51cec0a6cad8e89c8f9d1d53`, the approved package audit, eight direct browser routes, visible contact links, live Studio prediction/generation and 20 unauthenticated HTTP checks with scoped response parity. Deployed memory, sustained latency, cold-start distribution and quota headroom remain unmeasured. The separate [hosting assessment](../../reports/revision-2026-10/hosting-assessment.md) describes the two-provider fallback represented by `frontend/vercel.json` and `render.yaml`; those files do not describe the active hosting split. Static research remains readable during API unavailability, which Studio reports explicitly.

The upload allowlist excludes private documents, raw recordings, original renders and local credentials. The render manifest is included for site compilation; derived WebP images and approved research exports serve the browser. Git ignores generated root `pyproject.toml` and `uv.lock`, while prebuilt upload includes them because the function map references them. The canonical lock/project remain under `backend/`. The [operations guide](../../operations.md) describes clean-source builds and auditing mapped files before publication.

The repository is public and the owner authorized public research recordings, metadata, renders and results. No custom domain, DOI or new license is established. Named biometric association lacks a verified participant-name mapping and specific permission; code/data/asset licenses and third-party rights remain separate release decisions.

## Design Decisions

### Preserve originals and verify derived products

**Decision**: Keep original inputs checksum-addressable and regenerate products with pinned tools and recorded methods.
**Why**: Source or method changes must be traceable through eligibility, model evaluation and browser claims.
**Rejected**: Treating historical figures or an unverified saved model as reproducible current evidence.
*Introduced by*: 261008-ymhz-research-platform-rebuild

### Verified hosting with explicit readiness

**Decision**: Keep static research independent of API readiness and publish both services on one verified Vercel origin with an isolated deployment runtime.
**Why**: Visitors can read the research during API outages, and hosting compatibility remains separate from canonical scientific reproduction. Recorded public checks support the deployment claim without implying model validity or unmeasured performance.
**Rejected**: Describing local configuration alone as proof of a hosted service, or changing scientific dependencies to fit hosting.
*Introduced by*: 261010-oom7-public-deployment-docs

### Separate fresh scientific and final-source evidence

**Decision**: Record the clean full-control reproduction and the targeted final-source replay with distinct source digests and execution scopes.
**Why**: Presentation/provenance corrections changed source identity after the fresh numerical run while leaving the approved scientific computation unchanged.
**Rejected**: Calling artifact reuse a second fresh null run or treating the earlier source digest as the final checkout identity.
*Introduced by*: 261010-tadj-research-atlas-design-studio
