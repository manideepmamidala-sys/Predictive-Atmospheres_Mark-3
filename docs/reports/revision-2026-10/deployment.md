# Production deployment — 2026-10-10

The research atlas and Design Studio API are deployed together at
<https://predictive-atmospheres.vercel.app>. This is the public Production
alias of Vercel Services project `predictive-atmospheres` in the
`manideep-personal` Hobby account. Deployment
`E76dnEmkeL1dAgCc1pTrzDNs7RcA` reached **READY**; its immutable URL is
<https://predictive-atmospheres-2i9piibxk-manideep-personal.vercel.app>.
The source revision is `69e223fa0f42457c51cec0a6cad8e89c8f9d1d53` on
`261010-tadj-research-atlas-design-studio`.

This was a manual CLI deployment of a prebuilt Production output. The Vercel
project is not connected to GitHub for automatic deployments. Production's
alias is publicly accessible without a Vercel login; Preview deployments
retain Standard protection. No custom domain was purchased and no paid plan
was selected.

The root `vercel.json` routes `/v1/*` to a Python 3.12 FastAPI service and
other paths to the Vite site, whose service-local rewrite supports SPA deep
links after static-file lookup. `VERCEL_SUPPORT_LARGE_FUNCTIONS=1` is set for
Production and Preview because the scientific Python dependency package
exceeds the standard function packaging threshold. The isolated deployment
profile pins artifact-compatible dependency versions while retaining the
canonical Python 3.11 backend project, source and fitted-model bytes.

The prebuilt output came from a clean, allowlisted source copy. Its site has
136 static files totaling 18.43 MB. The Python function maps 7,233 existing
files totaling 257.97 MiB, including the exact canonical API source, fitted
model, approved QC ledger, data manifest and specification. The function map
contains no raw recordings, reports, Fab files, frontend source, or local
environment files. Vercel-generated root `pyproject.toml` and `uv.lock` were
admitted to the prebuilt upload because that map references them; they are
Git-ignored build files, not replacements for `backend/pyproject.toml` or
`backend/uv.lock`. Independent local bundle review passed before publication.

An unauthenticated request to the public Production alias returned HTTP 200
from `/v1/health`, with `ready=true` and `model_status=baseline_only`. The
first observed request took about 7.6 seconds; this is one observation, not
a cold-start or latency benchmark. The artifact remains a qualified
baseline-only research demonstration: 23 E3 trials, four people, ten rooms,
and no observed room-held-out gain over fixed baselines. It must not be
presented as a validated design recommendation.

An unauthenticated production-browser check loaded all eight routes directly
with HTTP 200 and the expected page headings. At 390 px width, the pages had
no horizontal overflow. The public email appeared in both intended links,
Studio reported the live API as ready, preset prediction returned `ok` with
`baseline_only`, and generation returned five candidates. The browser
reported no page errors. Desktop and mobile screenshots were captured locally;
the desktop capture was visually inspected. They are not committed as
deployment artifacts.

Independent unauthenticated HTTP verification made 20 requests, all returning
200 without an authentication redirect. All eight HTML routes matched the
built site. The research bundle, signals, catalogue index, Methods JSON,
JavaScript, CSS, room image and portrait bytes matched the build output.
`/v1/health`, `/v1/meta`, prediction and deterministic two-candidate
optimization JSON matched the isolated Python 3.12 reference. The live API
metadata reported `ready=true`; Vercel's deployment metadata records the
source revision stated above. These requests establish deployed response
parity for the checked inputs, not general model validity.

The current evidence does not measure deployed memory use, sustained latency
or quota headroom. See [release readiness](../../release-readiness.md)
for scientific and publication limits and [operations](../../operations.md)
for build and recovery steps.
