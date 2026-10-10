# Local operation and hosting candidates

The research pipeline and FastAPI service live in `backend/`. The eight-route React atlas lives in `frontend/`. The site reads generated, hash-checked `artifacts/results/bundle.json`, loads the versioned analysis catalogue on research routes and loads `signals.json` only when the Data Explorer opens signal traces. Prediction and optimization alone need the live API. This page describes local commands and **candidate** hosting configuration; it is not a deployment record.

## Reproduce locally

Use Python 3.11.11, uv 0.5.9, Node 22.22.1 and the project-pinned pnpm 10.18.3 through Corepack. From the repository root:

```sh
make setup
make verify-data
make pipeline
make lint test site
```

After the final reference products are generated, `make reproduce-isolated` creates a temporary source-only Git snapshot and clean clone, regenerates a pending QC queue and reconstructs the approved CP-B ledger from the two documented delegated AI decision files and recorded review time, checks its exact SHA-256 against the reference, runs `make all` in that clone and compares the outputs. The ledger cannot be inferred from raw signals alone; the script reconstructs it from actual reviewed decisions and does not copy the completed ledger, models, analysis products, signal products or the partial spatial-null checkpoint. Its default four-hour workflow timeout permits the prescribed 1000 full-refit null draws and 455 learning-curve fits. The comparator checks nested catalogue products and model bytes while excluding only recorded checkout provenance, explicit generation/wall times and the transient null checkpoint. Run this only after scientific sources and the reference products are stable. For an ordinary checkout missing all generated artifacts, `make restore-cp-b` runs setup/QC and reconstructs the same review input before `make pipeline`; it does not create a new human signoff.

The 2026-10-10 validation record distinguishes the completed **fresh** 1,000-draw/455-subset clone run from the later review correction. That correction affected exported CP-B provenance, Methods evidence and code-tree metadata; a separate final-source clone reused only the earlier clean scientific artifacts, rebuilt the affected products, and matched all 53 products and model bytes. This targeted replay does not replace a fresh-control run for a future change to scientific inputs or numerical code. Public trial status comes from the approved CP-B ledger: automated flags, reviewed component outcomes and reasons must remain distinguishable, especially HR versus RMSSD and uncertain timebase decisions.

`make verify-data` checks all 313 retained original files against `data/source-inventory.json` and `data/MANIFEST.sha256`, including extra/missing source detection by `scripts/build_source_manifest.py --check`. The older `docs/reports/migration-inventory.json` records historical pre-cleanup paths and removed thesis-document hashes, and is not a routine dependency on Windows originals. `make pipeline` regenerates the read-only audit, conditional signal processing, affect/model products and browser exports from preserved original data. It does not fetch participant data. `make site` requires the generated bundle, signal product and complete 28-card analysis catalogue, checks their manifest/schema evidence, then typechecks and builds. Direct Vite development can show explicit unavailable states while exports are incomplete. Generated `frontend/public/research/` and `frontend/dist/` are outputs, not authoritative source records. The model artifact is a trusted local joblib file; never deserialize an artifact from an unverified outside source.

For an export-only refresh after compatible analysis products already exist, run `cd backend && uv run --frozen pa export`; `cd backend && uv run --frozen pa openapi` refreshes the API document and room-input JSON schema. Then regenerate the frontend types with `cd frontend && corepack pnpm run api:types`. These commands do not replace the full pipeline when source data, methods or model code change.

Start two local processes after a successful pipeline:

```sh
cd backend && uv run --frozen uvicorn pa.api.app:app --host 127.0.0.1 --port 8000
cd frontend && corepack pnpm dev
```

Run these in separate terminals. Vite proxies `/v1` to `PA_API_URL` (default `http://127.0.0.1:8000`). A separately hosted frontend uses a public HTTPS `VITE_API_BASE_URL` at build time, and the API must list the exact frontend origin in `PA_CORS_ORIGINS`. See the scoped `.env.example` files. A Vite variable becomes browser-visible; do not put secrets in it. `VITE_REPOSITORY_REF` names the published branch or commit containing preserved original renders and controls the original-image links.

`GET /v1/health` confirms the process is alive and separately reports `ready`. A 200 response with `ready=false` means the trusted artifact was absent or incompatible; `/v1/meta` reports the actual model status and limitations. Check both before testing `/v1/predict` and `/v1/optimize`. A baseline-only or below-baseline model may demonstrate the inference contract but is not a validated design recommendation. If a build fails, check `artifacts/results/manifest.json`, its product hashes, the data/specification hashes in `artifacts/model/metadata.json`, and run `make pipeline` after an intentional source/method change. Do not fit a replacement model at service startup.

For local Chromium tests on the present Ubuntu host, Playwright 1.64.0 required native `libnspr4`, `libnss3` and `libasound2t64`. The coordinator extracted package libraries temporarily under `/tmp/pa-browser-libs/root/usr/lib/x86_64-linux-gnu`; this path is **not** a repository dependency or portable setup. On a normal supported host or CI, install Chromium with `cd frontend && corepack pnpm exec playwright install --with-deps chromium`. CI uses that route. On the current restricted host only, the verified browser command sets `LD_LIBRARY_PATH=/tmp/pa-browser-libs/root/usr/lib/x86_64-linux-gnu` before `corepack pnpm test`; recreate the temporary libraries if that path disappears.

## Candidate hosting configuration

`vercel.json` at the repository root defines one Vercel Services project with a Vite
site and a Python FastAPI service. Set the Vercel project Root Directory to the
repository root and Framework Preset to **Services**. Its ordered rewrites send
`/v1/*` to the API and other paths to the site, keeping Studio calls on the
same origin. The site service separately rewrites deep links to `index.html`
after checking static files. Leave `VITE_API_BASE_URL` unset for this deployment;
the site build command pins `VITE_REPOSITORY_REF` to the published branch.
The frontend service requires all manifest-matched static exports. The API
service loads the trusted fitted artifact; neither trains at request time.

Vercel's Python runtime supports Python 3.12, so the root
`.python-version` and `requirements.txt` form an isolated deployment
profile with the artifact-checked package versions. The canonical
`backend/pyproject.toml`, `backend/uv.lock`, fitted artifact and scientific
source bytes remain unchanged. The root `.vercelignore` allowlists the
minimum source, static assets, result exports, metadata, approved specification
and trusted model needed for the two services. It excludes raw recordings,
original renders, unrelated reports and local generated outputs from CLI
uploads. The Python function separately excludes frontend files and all
research result products except the approved QC ledger. An isolated Python
3.12 local check loaded the artifact with `ready=true` and returned the same
health, metadata, prediction and deterministic optimization JSON as the
canonical Python 3.11 environment, including from an allowlisted source copy.
The scientific Python dependencies exceed the CLI's standard-function
packaging threshold. Set `VERCEL_SUPPORT_LARGE_FUNCTIONS=1` for Production
and Preview on the Vercel project before building or deploying; the same flag
must be present for a local `vercel build`. Vercel's
[Large Functions announcement](https://vercel.com/changelog/vercel-functions-can-now-be-up-to-5-gb-in-package-size-7yAwSyCig0IQDXUIDistvS/eadf06d6c3)
documents the larger package path. Inspect the resulting function bundle and
verify hosted startup, memory and latency rather than assuming the larger
package alone makes the API ready. The local Vercel build passed; hosted
request checks are still required.

For a local provider build, start from a clean copy of the `.vercelignore`
allowlist, copy the existing `.vercel/project.json` link into that copy and
verify it points to the intended project **before** running `vercel pull`.
Then pull the Production environment and run `vercel build --target production`
with `VERCEL_SUPPORT_LARGE_FUNCTIONS=1`. The CLI may create a root `_uv/`,
`pyproject.toml` and `uv.lock` as build scratch; these are ignored locally and
are not the canonical backend project or lockfile. Audit the function output
for excluded files before publishing its prebuilt output. The 2026-10-10
clean-copy Production build passed: the Python 3.12 function mapped 7,233
existing files totaling 257.97 MiB, and the site emitted 136 files totaling
18.43 MB. The function map contained no raw recordings, reports, Fab files,
frontend files or local environment files; the canonical source, fitted model
and hash inputs matched the repository byte-for-byte. Deploy the prebuilt
output from the same clean copy because its function map references files
relative to that source root.

After deployment, verify all eight deep links and representative
`/research/` JSON and `/rooms/` images as static responses; check
`/v1/health` for JSON `ready=true`, then `/v1/meta`, prediction and
optimization through the public origin. Inspect the deployed function bundle
size, memory, cold start, errors and account limits. Vercel Services is
currently a beta feature available on all plans; the local checks do not
guarantee account eligibility or hosted behavior.

`render.yaml` and `frontend/vercel.json` remain the earlier two-provider
candidate if the one-project build cannot satisfy the hosted limits.
`render.yaml` describes one Render **free Python API** service. It pins Python 3.11.11, installs the frozen backend lock without dev packages, starts Uvicorn on Render's `$PORT`, and leaves automatic deployment off. It never starts analysis or training at request time. A hosting build therefore requires a trusted, compatible `artifacts/model/` and the source data/hash inputs the loader verifies to be present in the connected revision. The final-source local `uv sync --frozen --no-dev` environment loaded the trusted `baseline_only` artifact and served `/v1/health` with JSON `ready=true` plus `/v1/meta`; observed RSS was 215,688 KiB on this host. This does not establish Render's cold-start memory or response times. Its `/v1/health` HTTP check alone does not prove `ready=true`; inspect that field separately. Set `PA_CORS_ORIGINS` to the actual HTTPS frontend origin in the hosting dashboard. The legacy Streamlit service has no active candidate.

`frontend/vercel.json` describes a Vite static SPA build, pinned package installation and a deep-link rewrite. Set the Vercel project Root Directory to `frontend` and enable **Include source files outside of the Root Directory in the Build Step**, because staging reads `../artifacts/results/`; the required-export build flag fails closed if those files are missing. Configure `VITE_API_BASE_URL` to the actual API HTTPS origin and `VITE_REPOSITORY_REF` to an accessible source revision. The rewrite is for client-side routes; verify that existing `/research/` JSON and `/rooms/` image assets still resolve as static files. The final local preview served all eight deep links and representative `/research/` JSON as HTTP 200; 134 built static files total 15,347,819 bytes, with `research/signals.json` the largest at 7,610,410 bytes. These settings have passed local build and browser tests, not a Vercel or Render deployment.

Render's [Blueprint reference](https://render.com/docs/blueprint-spec) documents the fields used here; its [Python version guide](https://render.com/docs/python-version) requires an explicit full version for `PYTHON_VERSION`. Vercel's [Vite SPA guide](https://vercel.com/docs/frameworks/frontend/vite) documents deep-link rewrites and its [monorepo guide](https://vercel.com/docs/monorepos/monorepo-faq) documents outside-root build access. At the time of this plan, Render [documents idle spin-down and ephemeral free-service files](https://render.com/docs/free), and Vercel [documents Hobby limits](https://vercel.com/docs/limits); review current terms, source size, latency and quota in each account before release.

## Recovery and release boundary

Keep originals under `data/raw/`, `data/metadata/` and `data/renders/raw/` unchanged. Validate source hashes with `make verify-data`; regenerate downstream products using `make pipeline` after an approved method amendment. A static site can still show research pages when the API is asleep, while Design Studio shows a service error and preserves inputs. If a published revision becomes incompatible, roll back the static and API revision together to a previously verified pair rather than bypassing hash checks. Browser screenshot and interaction evidence is in [phase-8.md](reports/phase-8.md). Outstanding authorization and hosting checks are in [release-readiness.md](release-readiness.md).

The owner approved [CP-A](reports/revision-2026-10/CP-A.md)'s ordinary-Git choice on 2026-10-10. Canonical originals continue through standard Git checkout and the existing manifest check; no LFS installation, fetch, tracking migration or history rewrite is part of this revision. The owner also approved the exact [v1.2 method source](specs/analysis-v1.2-draft.md) at [CP-Spec](reports/revision-2026-10/CP-Spec.md). [CP-B](reports/revision-2026-10/CP-B.md) records delegated AI review of exact signal decisions and their limits; it is not a personal owner signoff. Dependent v1.2 products require that integrated ledger. Independent [CP-C](reports/revision-2026-10/CP-C.md) approves only qualified baseline-model publication. The current [validation record](reports/revision-2026-10/validation.md) records the local pass and completed fresh clean-clone comparison; [release readiness](release-readiness.md) tracks CP-E2 and external decisions. The free-hosting needs and provider limits checked on 2026-10-10 are recorded in the [hosting assessment](reports/revision-2026-10/hosting-assessment.md).
