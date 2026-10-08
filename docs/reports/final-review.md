# Independent final review — ymhz

Date: 2026-10-08. Reviewer: fresh native Codex `gpt-6-astra`, `xhigh`, as explicitly dispatched by the coordinator. Review mode: **full**; change type: `feat`. Reviewed HEAD: `d46c5afaa9d82f66c021d6a4b7daae155e9f776c`; merge base with `origin/main`: `41d6ba507965d5159a679e65962fb3d02963a551`.

**Reviewer verdict: FAIL.** Nine must-fix findings remain. All 30 tasks were checked at entry; independent acceptance review marks **43/52 passing, 9/52 failing, 0 N/A**. The passing automated suite does not exercise the reproduced failures below. This is the reviewer's returned verdict; the Fab coordinator owns stage transitions and adoption of the verdict.

## Scope and independently checked evidence

Read the project governance, intake and plan, scientific specification and decisions, relevant protocol/cards/checkpoint/reproduction records, stale website memory, authored backend/frontend code and tests, workflow/deployment configuration, and the holistic change against the merge base. Generated schema/output files and binary assets were checked through their contracts, provenance, hashes and representative behavior rather than reviewed line by line. No implementation, source data, commits or deployment was changed by this reviewer. The browser suite's incidental rewrite of one tracked Rooms screenshot was restored.

| Check run during this review | Observed result |
|---|---|
| `cd backend && uv run --frozen pytest -q` | **56 passed**, one upstream Starlette/httpx deprecation warning, 33.71 seconds. |
| `cd backend && uv run --frozen pa verify-data` | `Source inventory verified`; preservation inventory covers 315 original files. |
| Fresh Python process: `load_artifact()` and `code_tree_hash()` | Loaded `not_better_than_baseline`; current and artifact hashes both `11a6312a6084ebc2ff893ff623180faeddd9778cf019b1d01fe64854a3c7325f`. |
| Fresh Uvicorn on `127.0.0.1:8019`; `CI=true PA_LIVE_API_TEST=1 PA_API_URL=http://127.0.0.1:8019 LD_LIBRARY_PATH=/tmp/pa-browser-libs/root/usr/lib/x86_64-linux-gnu corepack pnpm test` from `frontend/` | **18 passed**, 40.3 seconds, including real fitted prediction and optimization. No pre-existing API process was used. |
| `make lint site` | Ruff, generated OpenAPI type comparison, TypeScript and production Vite build passed. |
| Independent real-fold reconstruction | All **10 room and 3 participant outer folds** have disjoint relevant groups; all **30 saved inner calibrations** exactly match centers/scales recomputed from their inner-training members. |
| Independent CORS and unavailable-state probe | Configured origin preflight 200; unconfigured origin 400. Explicit unavailable artifact state gives live health with `ready=false`, prediction 503. Malformed metadata has the separate failure FR-06 below. |
| `python3 scripts/compare_reproduction.py . /tmp/pa-repro-2hiv6grb/clean-clone` | All **15 JSON products and model metadata** match at absolute/relative tolerance `1e-8`. Inspected clean-clone script and actual `make all` log; the heavy pipeline was not gratuitously rerun here. The original isolated execution is prior evidence, not a new execution by this reviewer. |
| `gh run view 37800226492 --log-failed` | Confirmed CI stops while preparing actions because `astral-sh/setup-uv@v9` does not resolve. |
| Additional live-browser and direct Python probes | Reproduced FR-02 through FR-06 against the actual generated exports/current code, with values below. |

The numerical implementation retains conditional rate labels, missing feature values, contiguous ECG interval rules, separate descriptive/population target transforms, nested group selection, both baselines, and a visibly weak fitted model. No new leakage or fabricated nominal physiology was found. Existing synthetic tests check known-band asymmetry and RR/RMSSD mathematics, clipping, noise, gaps, short recordings, nonfinite components, physical geometry, scoring, bounded search and direct/CLI/API parity. The review does not establish physiological ground truth, acquisition-rate certainty or predictive usefulness.

The coordinator additionally reported HEAD requests for all 30 original-render GitHub links returning HTTP 200. That is **coordinator evidence**, not an independent network check by this reviewer. Local render identity/layout, derivatives and original-preservation checks were inspected here.

## Must-fix findings

### FR-01 — CI references a nonexistent action tag

- **Location:** `.github/workflows/ci.yml:17`.
- **Reproduction:** `gh run view 37800226492 --log-failed` ends with `Unable to resolve action astral-sh/setup-uv@v9, unable to find version v9`. The job never reaches checkout or any reproduction/test step.
- **Impact:** The required frozen CI workflow cannot run, despite local checks passing.
- **Repair:** Pin a verified existing action revision. The coordinator independently verified intended `v9.0.0` at `c771a70e6277c0a99b617c7a806ffedaca235ff9`; verify the chosen revision and observe the resulting hosted run. No unrelated major upgrade is needed.
- **Requirement / acceptance / task:** R22; A-022; T026.

### FR-02 — Experiment/participant filters leave unrelated aggregate results visible

- **Locations:** `frontend/src/pages/People.tsx:9-14`; `frontend/src/pages/Affect.tsx:16`; `backend/src/pa/results/build.py:131-150`.
- **Reproduction:** Open `/people`, select Experiment 1. The actual table shows `Subj_M` with **30 trials, 4 complete-fusion records, valence −0.38 and arousal 0.04**. Experiment 1 contains only 10 trials for this person and has no self-reported affect axes or fused records. The filter only tests membership in `row.experiments`; it never selects experiment-specific counts or means. On `/affect`, select `Subj_B`: the headline correctly has **0 complete** and 10 partial positions, but sensitivity still shows Experiment 2 **n=4** and Experiment 3 **n=10** from other people. `Subj_B` has no Experiment 2 trial.
- **Impact:** Filtered views attribute outcomes and denominators to the wrong study subset.
- **Repair:** Export or select summaries for the chosen experiment/person, and keep sensitivity scoped consistently with its controls. Alternatively, a deliberately global sensitivity panel must be explicitly separate and labelled as unaffected by participant filtering. Add a multi-experiment/person regression fixture and verify actual Experiment 1 has no fused means.
- **Requirement / acceptance / task:** R20; A-020; T023.

### FR-03 — Measured demographic/sleep fields are discarded and presented as unrecorded

- **Locations:** `backend/src/pa/results/build.py:135-139`; `backend/src/pa/io/metadata.py`; `frontend/src/pages/People.tsx:13`; `frontend/src/pages/Study.tsx:20`.
- **Reproduction:** `data/metadata/Subject Data.csv` directly maps all ten supplied IDs to age/gender; for example `Subj_B,26,Female,Architect`. `load_trials()` has **60 non-null sleep observations**, all in Experiment 3. Yet all ten `bundle.people` records have `age=null`, `gender=null`, `sleep_hours=null`. The builder never reads Subject Data or passes these values to `PersonRecord`. The page describes blanks as not measured or not safely mapped, although these IDs match directly. The Study page also calls these source IDs “anonymized”, contrary to the data card's explicit evidence boundary.
- **Impact:** Observed data is falsely represented as unavailable, and the identity wording overstates a privacy property that was not established.
- **Repair:** Ingest and validate the existing ID-based demographic mapping; export measured fields with provenance. Preserve per-experiment sleep availability, and define a visible aggregation/range policy if a participant has differing recorded sleep rather than inventing a global value. Remove the unsupported anonymization claim. Add real/synthetic coverage for measured and structurally missing fields; do not add names.
- **Requirement / acceptance / tasks:** R5/R16/R20/R23; A-016, A-020, A-023; T005, T017, T023, T030.

### FR-04 — CSS erases the chart's cohort and CCT encodings

- **Locations:** `frontend/src/design/tokens.css:9` (`.point` rule); `frontend/src/figures/Circumplex.tsx:17-19`.
- **Reproduction:** In the live `/affect` chart, a `partial_modality_fusion` circle has SVG `fill="var(--plot)"` and a CCT-dependent stroke, but `getComputedStyle(circle)` returns fill **`rgb(49, 93, 157)`** and stroke **`rgb(247, 248, 246)`**. The CSS `.point{fill:var(--sky);stroke:var(--paper);stroke-width:2}` overrides every presentation attribute. All tested low/high-CCT and partial points render solid blue, while the legend promises warm/cool/grey colors and open partial-cohort markers.
- **Impact:** The central scientific figure visually conflates partial and complete fusion and misstates its lighting encoding.
- **Repair:** Give cohort/CCT visual properties a single effective owner (styles, CSS variables or distinct classes), while retaining focus styling. Assert computed fill/stroke for complete, partial and missing-CCT points in both themes and recapture affected evidence.
- **Requirement / acceptance / tasks:** R18/R20/R23; A-018, A-020, A-023; T019, T023, T025, T030.

### FR-05 — Studied support ignores model input opening counts

- **Locations:** `backend/src/pa/features/support.py:12-13,45-60`.
- **Reproduction:** Load `load_studied_support()`, copy `support.rooms[0]`, replace only `num_doors` with **99**, validate through `RoomInput`, and call `support.assess(candidate)`. It returns **`supported`, nearest `Rm_021`, distance 0.0**. Observed door counts are `[1,1,3,4,1,1,2,1,1,1]`. `num_windows` is likewise absent from support checks. These fields remain model inputs and can also be omitted without making this support claim unavailable.
- **Impact:** The simulator can label an unstudied model covariate combination as the exact studied room, defeating the promised distinction between physical validity and empirical support.
- **Repair:** Include opening-count range/missingness in the declared support contract and its multivariate assessment, or explicitly qualify a narrower support status so it does not claim full-input support. Keep physical validity separate. Test omitted and out-of-observed-range counts, update method/provenance if the support metric changes, and regenerate compatible artifacts after backend source changes.
- **Requirement / acceptance / tasks:** R11/R15/R21; A-021; T012, T016, T024. Existing bounded optimizer defaults themselves passed their current determinism/deduplication checks (A-015/A-040).

### FR-06 — Invalid metadata JSON can crash startup instead of reporting unavailability

- **Locations:** `backend/src/pa/modeling/artifact.py:104-123`; `backend/src/pa/api/app.py:31-37`.
- **Reproduction:** Copy the current trusted `model.joblib` into a temporary directory, write the valid JSON value `[]` to its `metadata.json`, then call `load_artifact(directory)`. It raises **`AttributeError: 'list' object has no attribute 'get'`**, not `ArtifactUnavailable`. API lifespan catches only `ArtifactUnavailable`, so this invalid metadata would abort startup instead of exposing live health with `ready=false` and structured 503 prediction responses.
- **Impact:** The explicit invalid-artifact readiness contract is not satisfied. Existing tests cover missing files, hashes and feature-order mismatch, but not metadata document shape.
- **Repair:** Validate metadata's document/type contract before field access and translate expected malformed-artifact failures to `ArtifactUnavailable`; add the corresponding loader and lifespan/readiness regression. Do not refit or provide a fallback prediction.
- **Requirement / acceptance / tasks:** R13/R17; A-013, A-017, A-041; T015, T018.

### FR-07 — Model report omits required eligibility and preprocessing evidence

- **Locations:** `frontend/src/pages/ModelReport.tsx:8-11`; `backend/src/pa/results/schemas.py:128-133`; `backend/src/pa/modeling/train.py:93-109`.
- **Reproduction:** The actual browser model product has only `status`, `explanation`, `metrics`, `limitations`, `artifact_version`. `/model` cannot show the 14-trial/three-participant/ten-room training cohort, exclusion/missingness counts, selected RF configuration, feature preprocessing or artifact provenance hashes. Its artifact box contains only version/schema/source/method prose; generic fold-normalization text is not a description of the fitted imputer/scaler/encoder. The separately retained model card/evaluation/metadata do have this evidence, but the page does not expose or link those records.
- **Impact:** The required read-only Model report is incomplete, particularly for understanding the tiny effective sample and the participant evaluation's fixed-baseline fallback.
- **Repair:** Extend the versioned static model product with a concise generated cohort/exclusion/preprocessing/selection/provenance summary, explain the participant-baseline fallback, and render it with links to retained detailed evidence. Preserve unavailable values and offline operation; do not hardcode current results into JSX.
- **Requirement / acceptance / tasks:** R21; A-021; T015, T017, T024.

### FR-08 — Required research inspection controls/evidence are not exposed

- **Locations:** `frontend/src/pages/Signals.tsx:10-17`; `frontend/src/pages/Affect.tsx:19-23`; `backend/src/pa/results/export.py:53-60`.
- **Reproduction:** Signals offers Experiment, Trial and Trace but no participant filter. Affect's Experiment 1 records show unavailable affect axes while their preserved `comfort` values are never rendered. `objective_minus_subjective` and its paired/cohort summaries exist in `affect_detail.json`/`affect_analysis.json`, but the browser bundle discards that analysis and Affect has no disagreement view. Switching two point layers is not the requested explicit disagreement product.
- **Impact:** R20's participant inspection, separate self-report construct and disagreement requirements are missing from the delivered seven-page site even though parts of the backend evidence already exist.
- **Repair:** Add participant filtering to Signals, expose Experiment 1 comfort as its own labelled field/table, and publish/render generated disagreement evidence with axis, cohort and available-pair denominator. Keep scope aligned with the chosen filters and retain unavailable states; no physiological processing belongs in the browser.
- **Requirement / acceptance / tasks:** R9/R20; A-020; T017, T022, T023.

### FR-09 — Newly added utility has no call sites

- **Location:** `backend/src/pa/io/metadata.py:61-62`, `Trial.as_record`.
- **Reproduction:** `rg -n 'as_record' .` finds only this definition; no source or test uses it. Its `asdict` import exists only to support the unused wrapper.
- **Impact / classification:** Tiny but concrete parsimony finding: **`zero-call-sites`**, which `_review/SKILL.md` explicitly assigns **must-fix** severity. This is a workflow requirement rather than a scientific failure.
- **Repair:** Remove the unused method/import unless a concrete required caller is identified. Do not create a test or artificial call merely to retain dead code.
- **Task:** T005. No separate plan acceptance item specifically targets unused new symbols; the full-review parsimony contract still applies.

## Other findings and memory drift

`should_fix: []`; `nice_to_have: []`.

Memory warning only: `docs/memory/website_architecture.md` still describes the superseded cinematic/brutalist site and outdated interactions. The intake/T030 explicitly defers its replacement and new domain indexes to hydrate, so this is not an additional review blocker. Keep source evidence copies and historical originals: their intentional checksum-equivalent duplication is preservation, not redundant runtime code. New licensing, DOI, deployment and named biometric publication remain external release work and are not falsely marked completed here.

## Acceptance evidence ledger

The plan contains the authoritative checkmarks and inline reasons for failures. Passing entries below describe independently inspected/run evidence, not merely task assertions.

| Acceptance | Result | Evidence |
|---|---|---|
| A-001 | Pass | Reconciled roadmap, immutable legacy commit, preservation inventory and exact Codex routing. |
| A-002 | Pass | Deletion diff contains only the four named historical changes and obsolete `.active`; current records/tooling remain. |
| A-003 | Pass | Frozen commands, supported locks, backend CLI/tests and production build; isolated setup log inspected. |
| A-004 | Pass | All source hashes verify; tamper/missing tests pass; 315-file path/role inventory. |
| A-005 | Pass | Source readers preserve rating values, sleep omissions, comfort distinction and reported protocol. Export loss is FR-03. |
| A-006 | Pass | Actual 160-file audit retains per-rate scenarios, jumps, filename chronology and uncertainty. |
| A-007 | Pass | Versioned specification, primary references, recorded initial FAIL/amendment/fresh PASS gate before dependent results. |
| A-008 | Pass | Known-signal and adverse tests; real per-trial signal/QC/reason and trace products. |
| A-009 | Pass | Backend retains components, partial/full cohorts, alpha/experiment products; distinct population calibration. |
| A-010 | Pass | Descriptive group/association outputs retain independent-unit counts and unavailable intervals/p-values. |
| A-011 | Pass | One `RoomInput`/builder; total areas, feature ordering, physical invalidity and optional inputs tested. |
| A-012 | Pass | Independent real group audit and 30 calibration reconstructions; nested tests and exported baseline/per-axis evidence. |
| A-013 | Fail | Normal fresh load/parity passes, malformed metadata violates unavailable contract: FR-06. |
| A-014 | Pass | Single signed-domain fixed-diameter scorer; bounds, target equality, monotonicity/projection tests. |
| A-015 | Pass | Current default search draws observed-range counts, deduplicates and terminates with tested deterministic/empty outcomes. Broader prediction support issue: FR-05. |
| A-016 | Fail | Validated/offline exports work, but measured demographic/sleep observations become null: FR-03. |
| A-017 | Fail | Versioned routes, CORS, bounds and generated types pass; invalid-artifact readiness gap: FR-06. |
| A-018 | Fail | Themes/responsiveness/keyboard pass; scientific marker/color content is overridden: FR-04. |
| A-019 | Pass | Thirty manifest-mapped renders, layout caveats, original links, room filters/comparison and keyboard panorama. |
| A-020 | Fail | Filter scope, lost observed metadata, erased visual encodings and missing inspection evidence: FR-02/03/04/08. |
| A-021 | Fail | Live prediction/search/offline handling work; support and model report are incomplete: FR-05/07. |
| A-022 | Fail | Local 56/18 tests and reproduction comparison pass; hosted CI cannot start: FR-01. |
| A-023 | Fail | Commands/checkpoint history are supported, but current presentation claims/evidence need correction after FR-03/04. Hydrate remains explicitly pending. |
| A-024 | Pass | Locally reviewable Render/Vercel configs and runbook separate pending external release conditions. |
| A-025 | Pass | Responsibility inventory, replacement-only imports/entrypoints and source preservation verify retirement. |
| A-026 | Pass | Numeric ingestion and structural omission tests; no comfort-to-axis conversion. |
| A-027 | Pass | Flat/short/clipped/noise/gap/nonfinite failure tests preserve missing physiological/target values. |
| A-028 | Pass | Builder, schema and direct/CLI/API parity all share the same derived ordered inputs. |
| A-029 | Pass | Held-out mutations, nested training ownership, real membership and calibration checks. |
| A-030 | Pass | One score/projection function; target stays explicit through CLI/API/search/UI. |
| A-031 | Pass | Active runtime scan finds no legacy Torch/Streamlit/import/training routes or confidence fallback. |
| A-032 | Pass | Exact Fab deletion diff, retained current records and source hash verification. |
| A-033 | Pass | Audit tests cover modulo wrap/jumps/duration mismatch with explicitly conditional rate. |
| A-034 | Pass | Known alpha amplitude ratio/log sign and alternating RR/RMSSD fixtures test mathematics. |
| A-035 | Pass | Synthetic fitted pipeline exercises persistence, reload and CLI/API parity separately from real fit. |
| A-036 | Pass | Fresh browser suite covers seven routes × two widths × two themes, System changes, focus and reduced motion. |
| A-037 | Pass | Fresh live test plus synthetic weak/offline/unavailable/target cases; user input retained. |
| A-038 | Pass | Backend/UI retain missing axes and partial labels; no invented origin or complete-fusion count. Visual marker defect is FR-04. |
| A-039 | Pass | Physical schema rejects invalid domains and contradictory geometry/areas; omissions remain allowed. |
| A-040 | Pass | Fixed budget and deduplication; unsupported category, absent model and empty paths tested. |
| A-041 | Fail | Missing/hash/schema failures work; metadata document shape escapes readiness handling: FR-06. |
| A-042 | Pass | No fabricated inferential intervals or p-values; degeneracy/unavailability encoded. |
| A-043 | Pass | Replacement package/frontend layers and public boundaries are consistent. |
| A-044 | Pass | Schema/features/scoring/model inference have single owners; no parallel legacy implementations remain. |
| A-045 | Pass | Scientific transformations/failures are typed at boundaries with explicit interpretation docs. |
| A-046 | Pass | Architectural departures match the authorized runtime replacement and responsibility map. |
| A-047 | Pass | Pipeline composition and small API/presentation interfaces; no unnecessary inheritance. |
| A-048 | Pass | Longer signal/evaluation/export functions perform cohesive documented domain operations. |
| A-049 | Pass | Suitable shared routines own common behavior; legacy duplicates retired. Separate dead wrapper: FR-09. |
| A-050 | Pass | Scientific settings centralized in decisions/specification with provenance; ordinary UI/math constants remain legitimate. |
| A-051 | Pass | Bounded typed public inputs, configured CORS, trusted local artifact; no upload/path/train endpoint. |
| A-052 | Pass | No tracked credentials found in changed authored configuration; existing rights retained and named publication remains unasserted. |

## Rework and verification scope

Reopen the affected implementation tasks; correct these bounded contracts, add regressions for the reproduced cases, regenerate exports and compatible artifact metadata, and update affected screenshots/report claims. Any backend source change changes `code_tree_sha256`, so final evidence must again use a **fresh process**. Observe hosted CI after fixing its action reference. Repeat the affected checks and have a fresh `gpt-6-astra/xhigh` worker verify the fixes; do not infer a pass from this report or from the existing 56/18 green suite. The coordinator, not this reviewer, performs all Fab transitions.
