# Local operation and hosting candidates

The research pipeline and FastAPI service live in `backend/`. The seven-page React site lives in `frontend/`. The site reads generated, hash-checked `artifacts/results/bundle.json` on every research route and loads `signals.json` only on Signals. Prediction and optimization alone need the live API. This page describes locally exercised commands and **candidate** hosting configuration; it is not a deployment record.

## Reproduce locally

Use Python 3.11.11, uv 0.5.9, Node 22.22.1 and the project-pinned pnpm 10.18.3 through Corepack. From the repository root:

```sh
make setup
make verify-data
make pipeline
make lint test site
```

`make pipeline` regenerates the read-only audit, conditional signal processing, affect/model products and browser exports from preserved original data. It does not fetch participant data. `make site` stages the bundle and signal product only when the generated manifest SHA-256 values match, then typechecks and builds. The frontend build can be made explicitly dependent on these products with `PA_REQUIRE_RESEARCH_EXPORT=1` from `frontend/`. Generated `frontend/public/research/` and `frontend/dist/` are outputs, not authoritative source records. The model artifact is a trusted local joblib file; never deserialize an artifact from an unverified outside source.

For an export-only refresh after compatible analysis products already exist, run `cd backend && uv run --frozen pa export`; `cd backend && uv run --frozen pa openapi` refreshes the API document and room-input JSON schema. Then regenerate the frontend types with `cd frontend && corepack pnpm run api:types`. These commands do not replace the full pipeline when source data, methods or model code change.

Start two local processes after a successful pipeline:

```sh
cd backend && uv run --frozen uvicorn pa.api.app:app --host 127.0.0.1 --port 8000
cd frontend && corepack pnpm dev
```

Run these in separate terminals. Vite proxies `/v1` to `PA_API_URL` (default `http://127.0.0.1:8000`). A separately hosted frontend uses a public HTTPS `VITE_API_BASE_URL` at build time, and the API must list the exact frontend origin in `PA_CORS_ORIGINS`. See the scoped `.env.example` files. A Vite variable becomes browser-visible; do not put secrets in it. `VITE_REPOSITORY_REF` names the published branch or commit containing preserved original renders and controls the original-image links.

`GET /v1/health` confirms the process is alive and separately reports `ready`. A 200 response with `ready=false` means the trusted artifact was absent or incompatible; `/v1/meta` reports model status and limitations. Check both before testing `/v1/predict` and `/v1/optimize`. The current generated artifact reports `not_better_than_baseline`; the API may demonstrate inference, but it is not a validated design recommendation. If a build fails, check `artifacts/results/manifest.json`, its product hashes, the data/specification hashes in `artifacts/model/metadata.json`, and run `make pipeline` after an intentional source/method change. Do not fit a replacement model at service startup.

For local Chromium tests on the present Ubuntu host, Playwright 1.64.0 required native `libnspr4`, `libnss3` and `libasound2t64`. The coordinator extracted package libraries temporarily under `/tmp/pa-browser-libs/root/usr/lib/x86_64-linux-gnu`; this path is **not** a repository dependency or portable setup. On a normal supported host or CI, install Chromium with `cd frontend && corepack pnpm exec playwright install --with-deps chromium`. CI uses that route. On the current restricted host only, the verified browser command sets `LD_LIBRARY_PATH=/tmp/pa-browser-libs/root/usr/lib/x86_64-linux-gnu` before `corepack pnpm test`; recreate the temporary libraries if that path disappears.

## Candidate hosting configuration

`render.yaml` describes one Render **free Python API** service. It pins Python 3.11.11, installs the frozen backend lock, starts Uvicorn on Render's `$PORT`, and leaves automatic deployment off. It never starts analysis or training at request time. A hosting build therefore requires a trusted, compatible `artifacts/model/` and the source data/hash inputs the loader verifies to be present in the connected revision. The equivalent local isolated `uv sync --frozen --no-dev` succeeded; after regenerating the final artifact, a fresh no-dev Uvicorn process reported `ready=true`. Its `/v1/health` HTTP check alone does not prove `ready=true`. Set `PA_CORS_ORIGINS` to the actual HTTPS frontend origin in the hosting dashboard. The legacy Streamlit service has no active candidate.

`frontend/vercel.json` describes a Vite static SPA build, pinned package installation and a deep-link rewrite. Set the Vercel project Root Directory to `frontend` and enable **Include source files outside of the Root Directory in the Build Step**, because staging reads `../artifacts/results/`; the required-export build flag fails closed if those files are missing. Configure `VITE_API_BASE_URL` to the actual API HTTPS origin and `VITE_REPOSITORY_REF` to an accessible source revision. The rewrite is for client-side routes; verify that existing `/research/` JSON and `/rooms/` image assets still resolve as static files. These settings have passed local build and browser tests, not a Vercel or Render deployment.

Render's [Blueprint reference](https://render.com/docs/blueprint-spec) documents the fields used here; its [Python version guide](https://render.com/docs/python-version) requires an explicit full version for `PYTHON_VERSION`. Vercel's [Vite SPA guide](https://vercel.com/docs/frameworks/frontend/vite) documents deep-link rewrites and its [monorepo guide](https://vercel.com/docs/monorepos/monorepo-faq) documents outside-root build access. At the time of this plan, Render [documents idle spin-down and ephemeral free-service files](https://render.com/docs/free), and Vercel [documents Hobby limits](https://vercel.com/docs/limits); review current terms, source size, latency and quota in each account before release.

## Recovery and release boundary

Keep originals under `data/raw/`, `data/metadata/` and `data/renders/raw/` unchanged. Validate source hashes with `make verify-data`; regenerate downstream products using `make pipeline` after an approved method amendment. A static site can still show research pages when the API is asleep, while the simulator shows a service error and preserves inputs. If a published revision becomes incompatible, roll back the static and API revision together to a previously verified pair rather than bypassing hash checks. Browser screenshot and interaction evidence is in [phase-8.md](reports/phase-8.md). Outstanding authorization and hosting checks are in [release-readiness.md](release-readiness.md).
