# Independent full re-review — rework cycle 1

Date: 2026-10-08. Change: `261008-ymhz-research-platform-rebuild`. Review dispatch: Codex `gpt-6-astra` / `xhigh`, fresh single worker using Fab full-review behavior.

**Verdict: FAIL — one remaining must-fix, no should-fix or nice-to-have findings.** All 34 tasks are checked; acceptance is **49/52**. A-013, A-017 and A-041 remain unchecked for RR-01. The [initial review](final-review.md) is preserved as history.

Scope includes the total current tree against merge-base `41d6ba507965d5159a679e65962fb3d02963a551` with `origin/main`: committed changes through `d46c5afaa9d82f66c021d6a4b7daae155e9f776c`, uncommitted rework and authored untracked files. The reviewer inspected the plan, project policy, scientific specification and decision amendment, affected implementation/tests, scientific and API boundaries, preservation evidence and browser behavior. Prior review conclusions were not treated as proof of passing repairs.

## Remaining must-fix

### RR-01 — Artifact metadata validation still accepts an invalid public field

**Locations:** `backend/src/pa/modeling/artifact.py:108-129`; `backend/src/pa/api/app.py:59-76`. Remaining part of FR-06; requirements R13/R17, acceptance A-013/A-017/A-041.

The loader validates the JSON object, model status, limitations and compatibility hashes, but does not validate `artifact_version`, which `/v1/meta` consumes as a string. Independently reproduced using a temporary copy of the current valid `model.joblib` and metadata, changing only `metadata["artifact_version"] = []`:

1. `load_artifact(temp_directory)` succeeds with the invalid version.
2. A fresh API lifespan using that loader returns `/v1/health` HTTP 200 with `ready=true`.
3. `GET /v1/meta` returns HTTP **422**, `error.code=invalid_value`, with a Pydantic validation-error message. The request itself is valid; internal artifact state is invalid.

The original `metadata.json = []` startup crash is repaired, but malformed metadata still violates the unavailable-artifact contract. Validate every metadata field consumed by public responses before accepting the artifact, including the artifact version, and translate malformed metadata to `ArtifactUnavailable`. Add a regression proving liveness remains 200, readiness is false, metadata remains a valid unavailable response, and prediction/optimization return structured 503 errors. Regenerate compatible artifact metadata after the backend source changes; do not refit at startup or provide substitute predictions.

## Initial finding dispositions

| Finding | Re-review evidence | Result |
|---|---|---|
| FR-01 CI action | Independent `git ls-remote` resolves `v9.0.0` to the exact pinned `c771a70e6277c0a99b617c7a806ffedaca235ff9`. Workflow inputs and frozen commands inspected. | Local repair passes. New hosted execution remains pending the boundary push; no hosted pass is claimed. |
| FR-02 filter scope | Actual Subj_M/Experiment 1 displays ten trials, zero complete fusion and unavailable means. Affect excludes other participants' sensitivity/disagreement records. Real and synthetic browser regressions pass. | Pass |
| FR-03 demographics/sleep | All ten IDs retain source age/gender. Independent comparison validates all 16 participant/experiment summaries against source sleep observations, mean and range; 60 E3 observations remain distinct from E1/E2 absence. Unsupported anonymization wording removed. | Pass |
| FR-04 chart encodings | Computed-style tests pass in both themes for differing CCT colors, open partial markers and missing-CCT markers. Updated real Affect screenshot inspected. | Pass |
| FR-05 opening support | Original room is supported at distance zero; replacing door or window count with 99 gives `outside_range`, and omitting either gives `unavailable`. Eleven-input threshold is 1.4062989577434732. D-011/specification and regeneration match. | Pass |
| FR-06 metadata shape | Array/scalar metadata now raises `ArtifactUnavailable`; existing loader/lifespan regressions pass. Invalid `artifact_version` remains accepted: RR-01. | Partial; remains blocking |
| FR-07 model evidence | Generated product and browser expose 14 trials, three participants, ten rooms, exclusion counts, selected RF configuration, actual preprocessing, provenance hashes, detailed evidence links and participant-baseline fallback. | Pass |
| FR-08 inspection evidence | Signals participant controls scope trials and QC counts. Separate E1 comfort and generated disagreement tables preserve experiment/person, axis, cohort and available-pair denominator. Independent backend/browser checks pass. | Pass |
| FR-09 dead utility | `Trial.as_record` and its unused import are removed; source/test search has no remaining call or definition. Deletion Candidates updated. | Pass |

## Verification performed

- `uv run --frozen pytest -q`: **67 passed**; one existing Starlette/httpx deprecation warning.
- `make lint` and `git diff --check`: passed, including Ruff, generated OpenAPI type comparison and TypeScript.
- Fresh Uvicorn process on port 8012: current artifact loads with `ready=true`, `model_status=not_better_than_baseline`; backend source hash `8566633549d4dc8f60827f459fcf45858e6656ac3a872f65b33fcfe29f7483ea`.
- `CI=true PA_API_URL=http://127.0.0.1:8012 PA_LIVE_API_TEST=1 LD_LIBRARY_PATH=/tmp/pa-browser-libs/root/usr/lib/x86_64-linux-gnu corepack pnpm test`: passed; 26 collected tests, including real live prediction/optimization, source exports, filters, chart styles, seven routes, both themes, mobile/desktop, keyboard and reduced motion. Playwright completion metadata records `passed` with no failed tests. Screenshot outputs are byte-identical to the supplied source snapshot; reviewer API process was stopped afterward.
- `make verify-data`: source inventory verified. The coordinator's prior 30 original-render HTTP checks remain coordinator evidence, not a repeated reviewer network audit.
- Reproduction evidence independently checked without repeating the heavy pipeline: all **113** authored source/test/config/specification inputs checked match `/tmp/pa-repro-ln7bwob2/clean-clone`; `scripts/compare_reproduction.py` matches all **15 JSON products** and model metadata at `1e-8`; `cmp` confirms identical model bytes. The recorded clean-clone `make all` transcript supports its 67 backend/25 browser passes plus one intentional live-API skip and production build. See [reproduction record](reproduction.md).

The scientific boundary remains qualified: conditional sample rate, unavailable physiology retained as missing, descriptive versus population target calibration separated, grouped training-only selection, explicit baselines and weak-model status. These checks do not establish physiological ground truth or useful architectural prediction. No additional parsimony blocker was found.

Memory warning only: `docs/memory/website_architecture.md` remains stale pending the expressly planned hydrate stage. New hosted CI and external deployment/release conditions remain unverified. The reviewer changed only acceptance/deletion findings and this report, and performs no Fab stage transition.
