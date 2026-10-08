# Plan: Predictive Atmospheres Research Platform Rebuild

**Change**: 261008-ymhz-research-platform-rebuild
**Intake**: [intake.md](intake.md)
**Generated**: 2026-10-08
**Planning dispatch**: Codex `gpt-6-astra`, `high`

This plan covers the complete rebuild. Roadmap phases 0–9 remain milestones; the four execution phases below organize dependent work rather than replace those milestones. Local acceptance includes a working pipeline, actual research exports, evaluated artifacts or an evidence-backed unavailable-model outcome, and all seven pages. Account-dependent deployment, new licensing grants, DOI registration, and publication of named physiological records are separate release conditions, not pretend completed tasks. An unavailable scientific result must have a documented reason and an exercised implementation path; it is not permission to omit implementation.

## Requirements

### Governance: Reconciled roadmap and protected work

**R1.** `EXECUTION_PLAN.md` and project governance SHALL reflect the intake's protocol, full rebuild, research hypothesis, user-selected targets, dual themes, evidence gates, and exact AGENTS.md routing. Fab SHALL remain the workflow; the current Fab branch SHALL be used without renaming main or creating an unnecessary integration branch. A legacy snapshot reference SHALL identify the original committed tree without moving an existing tag. Original uncommitted work SHALL be inventoried and preserved separately from that Git snapshot.

GIVEN conflicting roadmap and intake instructions, WHEN implementation begins, THEN the roadmap is reconciled first and no baseline collection, confirmed-rate assertion, fixed emotional target, or mandatory validated-ground-truth claim survives as an active instruction.

**R2.** Cleanup SHALL delete only the four identified historical Fab change records (`a2td`, `bc1i`, `vwf1`, `rvq3`), including copies in archive if present, and proven references to those records. The current change, newly created rebuild records, `.agents/`, Fab tooling, unrelated records, original data, renders, thesis assets and user modifications MUST survive. Legacy source/runtime removal SHALL follow a responsibility and preservation inventory.

GIVEN untracked renders and old change directories, WHEN cleanup runs, THEN hashes account for preserved source assets and only the four historical changes disappear; no broad reset, directory purge, or history rewrite is used.

### Architecture: Reproducible package and evidence inventory

**R3.** The replacement SHALL use a headless `backend/src/pa/` package, uv-locked Python environment, pnpm-locked React/Vite/TypeScript frontend, `data/{metadata,raw,renders,processed}/`, and `artifacts/{model,results}/`. Supported interpreter/library versions SHALL be verified at setup. Configuration SHALL resolve paths independently of the launch directory. Torch and Streamlit SHALL leave the active replacement runtime. Frontend code MUST NOT compute physiological features or train models.

GIVEN a clean checkout and documented supported tools, WHEN dependencies are installed using frozen lockfiles, THEN backend CLI/tests and frontend build can run without importing legacy runtime modules.

**R4.** A manifest SHALL record source-relative paths, sizes, hashes, roles and migration destinations for recordings, metadata, all room renders, the existing frontend image collection and both thesis PDFs. Verification SHALL report absent/changed files without altering them. Generated products SHALL be separated from preserved originals. Inventory counts SHALL be recomputed rather than copied as research results.

GIVEN a modified source file or absent render, WHEN `pa verify-data` runs, THEN it fails with the specific discrepancy and never silently regenerates the source manifest to accept it.

### Research: Protocol, ingestion and acquisition audit

**R5.** Protocol documents and metadata ingestion SHALL preserve owner-reported Barcelona/NPG Lite/Chords/Quest 3 details, approximate right/left forehead channel placement, wrist ECG, unknown reference/ground details and units, variable exposures, no recorded baseline, post-exposure ratings, repeated identities and reported presentation-order randomization. Stored transformed ratings SHALL remain unchanged: Experiment 1 comfort is not valence; Experiments 2/3 have distinct elicitation provenance. Empty CSV rows SHALL be filtered explicitly; missing observations SHALL remain missing. No identities, questionnaires, simulation conditions, or unrecorded measurements SHALL be fabricated.

GIVEN already signed ratings and structurally absent CCT/sleep/self-report fields, WHEN ingestion runs, THEN values are neither transformed twice nor replaced by zero, and provenance/missingness remains available in exports.

**R6.** A read-only acquisition audit SHALL produce file-level sample counts, numeric integrity, modulo-counter transitions, logged-duration comparisons, filename-derived trial order and candidate-rate evidence. It SHALL distinguish observed facts, owner reports, inference and unresolved evidence. Near-500-Hz ratios SHALL NOT become confirmed settings. Counter discontinuities SHALL NOT automatically become packet-loss counts or timing corrections. Conditional analysis MAY use a documented candidate rate only with explicit status, alternative-rate sensitivity and per-file caveats; unsupported frequency/time claims SHALL remain unavailable.

GIVEN conflicting duration and sample-count evidence, WHEN the audit selects an analytical scenario, THEN its rate remains labelled inferred/conditional, disagreements remain visible, and no padding or rate selection to improve emotional/model results occurs.

**R7.** Before real signal processing, target construction and model comparisons, a versioned analysis specification SHALL document primary methodological sources, applicability, parameters, units, exclusion rules, alternatives, estimands, uncertainty, missing-modality handling and failure behavior. It SHALL address the limitations of two approximate forehead channels, unknown signal amplitude units, short ECG recordings, unmatched spatial simulation values and small dependent samples. An append-only decision log SHALL record later amendments and supersession; this reanalysis MUST NOT be called prospective preregistration. Audit and specification checkpoints SHALL have recorded evidence and independent review before dependent implementation/results are accepted.

GIVEN an exclusion rate or model result that is inconvenient, WHEN a method changes, THEN its amendment and affected rerun are recorded rather than silently relaxing thresholds or tuning the scientific claim.

### Research: Valid physiological features and constructed affect

**R8.** Signal processing SHALL implement justified filters, artifact/QC handling, channel-specific band-power/asymmetry and ECG peak/interval features with original-unit conventions, valid-duration/beat counts, modality validity and machine-readable reasons. Filters SHALL respect candidate sampling rates and Nyquist limits; short segments, flat/saturated signals and discontinuities SHALL be handled explicitly. Failed calculations MUST NOT become nominal heart rate, neutral affect, invented baseline correction or interpolated synthetic trials. Derived asymmetry SHALL be named as forehead log-power asymmetry with declared channel order, not established emotional valence or exact cortical localization.

GIVEN synthetic band-limited signals and known ECG peak times, WHEN processing runs, THEN relevant powers/ratios and beat intervals match mathematical expectations within declared tolerances; corrupted/insufficient input yields reasons and missing values rather than plausible fabricated values.

**R9.** Affect analysis SHALL retain self-report, physiological components and fused coordinates as distinct descriptive products, identify full/partial/single-modality cohorts, display disagreement, and evaluate declared alpha sensitivity. Physiological mapping to coordinates SHALL be explicitly hypothetical. Experiment 1 comfort SHALL remain separate. Experiment 2/3 pooling SHALL require an explicit rationale with experiment-stratified sensitivity; range equality or a nonsignificant test SHALL NOT establish measurement equivalence. Descriptive participant standardization and deployment/evaluation target transformations SHALL be distinct, with held-out outcomes excluded from fitting normalization.

GIVEN a trial without self-report or one invalid physiological modality, WHEN fusion exports are generated, THEN its component availability and construction are explicit and no fictitious circumplex starting position or homogeneous complete-fusion label is assigned.

**R10.** Descriptive statistical reports SHALL identify participant/room/experiment dependence, observational confounding, cohort sizes and uncertainty. Resampling/permutation procedures, if used, SHALL preserve the dependence relevant to their estimand. Small effective sample sizes, singular/nonconvergent models, missing modalities and absent interval-calibration evidence SHALL yield qualified or unavailable inference. No causal effect or validated emotion detector SHALL be claimed from these recordings. Unsupported optional inferential methods SHALL be omitted with reasons rather than added for appearance.

GIVEN repeated trials from ten people across three experiments, WHEN reporting associations or uncertainty, THEN trial counts are distinguished from independent participant/room counts and the assumptions of every interval/test are documented.

### Modeling: Shared physical schema and honest evaluation

**R11.** One Pydantic `RoomInput` and backend feature builder SHALL serve ingestion, training, CLI, API and optimizer. Independent dimensions, integer opening counts, already-total opening areas, supplied lighting, walkable area and valid categoricals SHALL retain documented missingness. Derived dimensions/ratios SHALL not be independent inputs. Validation SHALL reject nonfinite values, contradictory geometry/count-area combinations and impossible walkable/opening area; physical validity and studied support SHALL be distinct. Purged UDI/sDA/ASE features SHALL remain absent.

GIVEN two doors with a supplied total area, WHEN features are built through any consumer, THEN opening ratio uses that total once and ordered model features agree; changing volume independently is rejected.

**R12.** Evaluation SHALL compare training-fold baselines and a small declared sklearn candidate set using held-out-room and held-out-participant splits as separate generalization questions where supported. Repeated subject IDs across experiments SHALL share grouping. Imputation, encoding, scaling, target normalization and tuning SHALL be fitted on training partitions only. Hyperparameter/model selection SHALL not reuse the outer evaluation fold. Reports SHALL include fold memberships, eligibility/exclusions, per-axis metrics, baseline comparisons, alpha/experiment sensitivity and honest uncertainty status. No model is required to outperform baseline.

GIVEN a changed held-out outcome or covariate distribution, WHEN evaluation reruns, THEN fitted training transforms remain unchanged and no participant/room crosses its relevant grouping boundary.

**R13.** The saved model artifact SHALL include the complete fitted preprocessing/model pipeline and compatible metadata: ordered schema, dependency versions, dataset/specification hashes, code revision, training/evaluation scope, metrics and limitations. Reload/direct/CLI/API prediction SHALL agree within declared tolerances. Invalid/missing/incompatible artifacts SHALL cause an explicit unavailable state. A weak but valid artifact MAY serve an experimental demonstration with its performance status; no heuristic confidence percentage or unsupported calibrated interval SHALL be emitted.

GIVEN a serialized artifact with a mismatched feature schema, WHEN the service starts or predicts, THEN readiness identifies incompatibility and prediction fails clearly rather than fitting a replacement or returning a fallback emotion.

**R14.** Neuro-Score SHALL measure proximity to a user-selected target in the signed valence/arousal square. Use `clip(1 - ||point-target||₂ / sqrt(8), 0, 1)` with documented domain, bounds and interpretation; score is one at the target and decreases with distance. Points and targets SHALL be finite and in the declared domain; out-of-domain raw predictions require an explicit recorded projection policy before scoring. Space type SHALL not dictate the emotional preference.

GIVEN two points along increasing distance from the same valid target, WHEN scored, THEN the nearer point never scores lower; selecting a different target changes scoring without retraining.

**R15.** The experimental optimizer SHALL sample independent variables and observed-compatible categorical combinations, derive all features centrally, enforce physical and studied-support checks, use bounded work and a reproducible seed, deduplicate candidates and rank by the same user-target score. Default proposals SHALL remain inside declared supported ranges with multivariate support evidence; marginal bounds alone SHALL not be labelled proof of a studied combination. No valid candidates or unavailable model SHALL produce a specific outcome. Weak-model limitations SHALL remain visible without deleting the demonstrator.

GIVEN a narrow feasible search or weak valid model, WHEN optimizing, THEN results are distinct and reproducible or return a truthful empty reason, and every result carries support and model-status context.

### Delivery: Versioned static products and API

**R16.** Research exports SHALL be schema-versioned JSON/CSV/Parquet products as appropriate, with a compact browser bundle, provenance manifest and finite/null serialization. They SHALL include inventory, room metadata/renders, bounded trace/QC examples and selectable trace products, affect/components/sensitivity, participant summaries and model reports. Figure counts/metrics SHALL originate in generated products. Static pages SHALL function with the API offline. Schema generation/validation SHALL prevent backend/frontend drift; source raw recordings SHALL not be shipped wholesale in the browser bundle.

GIVEN absent live API and a valid export bundle, WHEN research pages load, THEN actual study results and explicit missingness remain usable with traceable source/schema versions.

**R17.** FastAPI SHALL expose `/v1/health`, `/v1/meta`, `/v1/predict`, `/v1/optimize`, generated OpenAPI and structured errors. Readiness SHALL reflect artifact compatibility independently of process liveness. Targets SHALL be present in scoring/optimization contracts; metadata SHALL expose model/data/schema versions and status. CORS SHALL be configurable, synchronous CPU work SHALL avoid blocking async handlers, and public requests SHALL have bounds. Training, arbitrary file loading and arbitrary output paths SHALL not be public routes. Frontend client/types SHALL be generated from OpenAPI with drift checks.

GIVEN invalid geometry, unavailable artifact, incompatible schema, or excessive candidate count, WHEN an API request is submitted, THEN it returns the documented structured error/status without a server traceback or fabricated response.

### Website: Complete accessible redesign

**R18.** A new design system SHALL provide Light/Dark/System preference, persistent explicit selection, system-change following in System mode, responsive layouts, readable charts/equations/3D, keyboard focus, meaningful labels and reduced motion. Seven routes SHALL be The study, Rooms, Signals, Affect, People, Room simulator and Model report. A styleguide checkpoint and final screenshot evidence SHALL cover both themes and desktop/mobile. Dependencies and relevant available skills SHALL be inspected at their point of use; install only maintained compatible tooling that materially helps.

GIVEN a saved System preference and an OS theme change, WHEN the app is open, THEN theme follows the OS; an explicit Light/Dark choice persists and remains legible across routes.

**R19.** The study and Rooms SHALL present an accurate research narrative, protocol/provenance/limitations, generated study counts, experiment filters, comparable room attributes and all thirty preserved room renders. A manifest SHALL verify actual panorama layout before choosing a view; unknown stereo eye conventions SHALL remain labelled. Panorama exploration SHALL have a keyboard/table or ordinary-image alternative; room comparison SHALL preserve missing lighting values. A schematic room view SHALL not masquerade as an original Lumion render.

GIVEN a room without measured CCT and a stacked panorama, WHEN opened or compared, THEN CCT is explicitly missing and panorama view convention is documented, with the original accessible.

**R20.** Signals, Affect and People SHALL expose experiment/participant filters, raw/cleaned/QC information, physiological validity, self-report distinctions, fused/partial coordinates, alpha sensitivity, disagreement, sample counts, method context and honest uncertainty. Accessible tables SHALL accompany circumplex/plots. People SHALL use existing participant IDs; no unverified name mapping or demographic/physiological privacy claim SHALL be invented.

GIVEN filters selecting only Experiment 1 or invalid ECG trials, WHEN pages render, THEN comfort remains distinct from valence, modality exclusions remain visible and empty selections have explicit states.

**R21.** Room simulator SHALL support validated independent room input, a user-selected affective target, prediction, score and bounded optimization with visible experimental/support/performance status. Model report SHALL be read-only and expose real grouped evaluations, baselines, preprocessing, missingness, artifact metadata and limitations. API sleeping/offline/unavailable states SHALL be actionable and retain user input. All retained/replaced/removed legacy interactions SHALL be mapped, including removal of System Architecture and live Model Training pages.

GIVEN a weak model or sleeping API, WHEN a user enters a room and target, THEN limitations and request state are clear; failed requests preserve inputs and do not display invented results.

### Reproducibility: Tests, evidence and release preparation

**R22.** Root entry points SHALL cover setup, verification, audit, pipeline, backend/frontend tests, site build and complete reproduction. CI SHALL use frozen environments and meaningful synthetic, contract, leakage, failure, serialization and browser tests; normal CI SHALL not require a paid service or external deployment account. A clean-checkout reproduction SHALL rebuild generated numerical results within declared tolerances from preserved sources and record actual commands/results. Expensive work SHALL be explicit and not run during imports, UI rendering or API startup.

GIVEN a checkout without caches/model/results, WHEN the documented full workflow runs with available source data, THEN it regenerates the validated products or reports a scientifically justified unavailable result, with no dependence on stale legacy artifacts.

**R23.** Documentation SHALL describe actual implemented behavior, with protocol, analysis specification, data/model cards, decision amendments, changelog, source manifest, phase evidence and indexed memory/specs. Historical figures/results SHALL be clearly historical. Read-only reviewers SHALL return findings; coordinators SHALL record verdicts. The final independent reviewer SHALL be a fresh `gpt-6-astra/xhigh` worker, implementation/debugging `gpt-6-sol/high`, hydrate `gpt-6-sol/high`; any unavailable route SHALL be reported instead of substituted.

GIVEN a check that was not run or a deployment that was not made, WHEN reports/cards are finalized, THEN it remains explicitly unverified/pending and is never recorded as passing/released.

**R24.** Free-tier deployment configurations and an operations/release runbook SHALL be locally reviewable for a static frontend and CPU API. Existing public repository state SHALL not be treated as authorization to invent ownership/consent/licences. External prerequisites SHALL separately identify hosting authentication/project access and current limits, any domain/DNS setup, source ownership/licensing decisions, DOI registration and evidence needed for any named-recording release. Local implementation SHALL continue using IDs and preserve existing third-party licensing. This fab-ff SHALL stop at hydrate; actual deployment/DOI/named release and ship evidence SHALL not be claimed.

GIVEN no hosting credentials or unsettled licence proposals, WHEN local acceptance completes, THEN reproducible build/configuration evidence is available and the concrete external prerequisites remain visibly pending.

### Deprecated Requirements

**R25.** Replacement delivery SHALL retire active Streamlit/torch runtime paths, duplicate preprocessing/scoring/configuration, unversioned legacy API and training endpoints, stale packaging outputs/caches/logs and unsupported fixed emotional targets/confidence heuristics after responsibility mapping. Historical source is recoverable from Git; original evidence/assets SHALL remain preserved. Removal checks SHALL target executable/configured surfaces rather than historical prose.

GIVEN a fresh environment using only replacement dependencies, WHEN documented entry points run, THEN no active imports or entry points require removed `src/`, Python `frontend/`, root `api.py`, `run_pipeline.py`, or legacy archive applications.

### Design Decisions

- **Decision**: Use one Fab change with ordered evidence checkpoints; task groups may be delegated with disjoint ownership. **Why**: Full scope is authorized and this avoids artificial docs-only completion or conflicting branches. **Rejected**: Executing the old phase prompts verbatim; marking future work done. *Introduced by*: 261008-ymhz-research-platform-rebuild.
- **Decision**: Separate descriptive target construction from deployable fold-fitted target construction, and report room/participant holdouts separately. **Why**: Within-person descriptive calibration and new-person inference answer different questions. **Rejected**: Global standardization followed by random-row evaluation. *Introduced by*: 261008-ymhz-research-platform-rebuild.
- **Decision**: Keep unavailable states first-class across features, statistics, artifacts and UI. **Why**: Scientific failure is an observable result, not a neutral measurement. **Rejected**: Success-shaped fallback values. *Introduced by*: 261008-ymhz-research-platform-rebuild.
- **Decision**: Use Euclidean target distance normalized by the square's fixed diameter for Neuro-Score. **Why**: Gives a simple monotone bounded proximity measure consistent across user targets; it is not a calibrated health/quality outcome. **Rejected**: Space-type preferences and historical stretch constants. *Introduced by*: 261008-ymhz-research-platform-rebuild.
- **Decision**: Static research exports plus a small prediction/optimization API. **Why**: Research remains readable when a free-tier API sleeps and raw signal computation stays reproducible offline. **Rejected**: Browser signal processing or on-request fitting. *Introduced by*: 261008-ymhz-research-platform-rebuild.

### Scientific implementation starting evidence

The audit/specification task must extend these primary sources with device and physiological-method evidence before fixing analytical settings. This is a method-selection scaffold, not validation of these particular recordings:

- Fit imputation/scaling/encoding within training folds and serialize the full fitted pipeline; see [scikit-learn common pitfalls](https://scikit-learn.org/stable/common_pitfalls.html) and [composite estimators](https://scikit-learn.org/stable/modules/compose.html).
- Group held-out samples by the generalization question; separate subject and room evaluations rather than implying one split estimates both. See [scikit-learn grouped cross-validation](https://scikit-learn.org/stable/modules/cross_validation.html#cross-validation-iterators-for-grouped-data).
- SciPy provides SOS filtering, Welch PSD and peak-property primitives; the method specification must justify their parameters and validate recovery on known synthetic signals. See [SciPy signal reference](https://docs.scipy.org/doc/scipy/reference/signal.html).
- Distinguish artifact identification/rejection, filtering and reference assumptions; do not treat standard multichannel correction examples as evidence that two unknown-reference forehead channels support equivalent correction. See [MNE preprocessing documentation](https://mne.tools/stable/auto_tutorials/preprocessing/index.html). This limitation is a project inference requiring explicit discussion in the specification.

## Tasks

### Phase 1: Setup

- [x] T001 Reconcile `EXECUTION_PLAN.md`, `fab/project/constitution.md`, `fab/project/context.md`, `fab/project/config.yaml`, `fab/project/code-quality.md`, and `fab/project/code-review.md`; preserve exact AGENTS.md routing, meaningful source/test paths and roadmap phases 0–9; record branch/snapshot and existing-work inventory in `docs/reports/phase-0.md`. Do not broaden source paths to `.` to bypass PR staging review. <!-- R1 -->
- [x] T002 Implement preservation inventory/manifest in `data/MANIFEST.sha256` and `docs/reports/migration-inventory.json`; inventory metadata, recordings, `rooms/`, `frontend/assets/IMAGES/`, thesis PDFs and existing user changes before any move. Migrate originals only with checksum-equivalent destinations in `data/renders/raw/` and `docs/thesis/`; retain a machine-readable path map. <!-- R4 -->
- [x] T003 Remove only the four named old records under `fab/changes/` and associated obsolete pointers/dispatch references; preserve current/new changes and tooling. Record exact removed paths and evidence preservation in `docs/reports/phase-0.md`. <!-- R2 -->
- [x] T004 Create `backend/pyproject.toml`, `backend/uv.lock`, `backend/.python-version`, `backend/src/pa/{__init__.py,config.py,cli.py}`, `frontend/package.json`, `frontend/pnpm-lock.yaml`, and root `Makefile`; validate supported versions, minimal dependencies, editable package/CLI and frozen installs. Add basic path/config checks under `backend/tests/`. <!-- R3 -->
- [x] T005 Implement manifest verification and faithful CSV/raw readers in `backend/src/pa/io/{manifest.py,metadata.py,recordings.py}` with `backend/tests/test_ingestion.py` and `backend/tests/test_manifest.py`; create `docs/protocol/{acquisition.md,ratings.md,spatial-provenance.md}` preserving intake facts and missingness. <!-- R5 -->
- [x] T006 Implement `pa audit` in `backend/src/pa/io/audit.py`, synthetic audit tests in `backend/tests/test_audit.py`, and generate `artifacts/results/audit.json` plus `docs/reports/phase-1.md`; research device/export evidence, rate scenarios, counter/duration caveats and reconstructed trial order without executing the legacy pipeline. <!-- R6 -->
- [x] T007 Write evidence-led `docs/specs/analysis-v1.md`, initial `backend/src/pa/decisions.yaml`, `DECISIONS.md` and `docs/reports/analysis-checkpoint.md`; specify conditional rate handling, EEG/ECG/QC/mapping settings, cohort eligibility, normalization, pooling, dependence/uncertainty and modeling protocol. Obtain fresh independent audit/specification review and have coordinator record findings/verdict before downstream scientific results. <!-- R7 -->

### Phase 2: Core Implementation

- [x] T008 Implement EEG filtering/QC/features in `backend/src/pa/signals/{common.py,eeg.py,qc.py}` and analytical-recovery/failure tests in `backend/tests/test_eeg.py`; produce actual per-trial outputs and representative raw/cleaned/QC products linked to rate/specification status. <!-- R8 -->
- [x] T009 Implement ECG peak/interval/QC processing in `backend/src/pa/signals/ecg.py` and known-interval/corruption/short-recording tests in `backend/tests/test_ecg.py`; integrate modality reason codes, counts and signal review evidence in `docs/reports/phase-2.md`. <!-- R8 -->
- [x] T010 Implement self-report/component/fusion construction in `backend/src/pa/affect/{ratings.py,normalization.py,fusion.py}` and `backend/tests/test_affect.py`; export component availability, experiment cohorts, partial states, disagreements and alpha sensitivity without global held-out target fitting. <!-- R9 -->
- [x] T011 Implement declared descriptive/association and uncertainty analyses in `backend/src/pa/affect/analysis.py`, dependence/degenerate-case tests in `backend/tests/test_analysis.py`, and actual results with limitations in `docs/reports/phase-3.md`. Report unavailable optional inference explicitly; do not substitute naive trial-iid intervals. <!-- R10 -->
- [x] T012 Implement `backend/src/pa/features/{schema.py,builder.py,support.py}`, schema exports and `backend/tests/test_features.py`; map supplied spatial metadata, total opening-area semantics, categoricals and missingness; separate physical checks from data support. <!-- R11 -->
- [x] T013 Implement `backend/src/pa/scoring/neuro_score.py` and target/domain/monotonicity tests in `backend/tests/test_scoring.py`; expose one declared scoring function and recorded handling of raw predictions outside the coordinate square. <!-- R14 -->
- [x] T014 Implement grouped evaluation in `backend/src/pa/modeling/{splits.py,targets.py,evaluate.py,train.py}` with simple baselines and bounded candidate search; add fold-isolation/normalization leakage tests in `backend/tests/test_evaluation.py`; generate actual fold-level results and `docs/reports/phase-5.md`. <!-- R12 -->
- [x] T015 Implement complete fitted artifact persistence/loading/prediction in `backend/src/pa/modeling/{artifact.py,predict.py}`; write `artifacts/model/metadata.json`, valid pipeline artifact where justified, `docs/model_card.md` and `backend/tests/test_artifact.py`; verify reload parity and incompatible/missing states. <!-- R13 -->
- [x] T016 Implement seeded constrained candidate search in `backend/src/pa/optimize/search.py`, bound/support/deduplication/empty-state tests in `backend/tests/test_optimize.py`, and actual representative runs in `docs/reports/phase-6.md`. <!-- R15 -->
- [x] T017 Implement validated research export schemas/builders in `backend/src/pa/results/{schemas.py,export.py,traces.py}`, `backend/tests/test_exports.py`, and `artifacts/results/manifest.json`; build real browser research products with provenance and bounded traces from the new pipeline. <!-- R16 -->

### Phase 3: Integration & Edge Cases

- [x] T018 Implement `backend/src/pa/api/{app.py,schemas.py,errors.py}`, CLI prediction/export commands, `backend/tests/test_api.py` and `backend/tests/test_prediction_parity.py`; expose versioned contracts, readiness, configured CORS, bounded requests and actual direct/CLI/API parity. Generate `artifacts/results/openapi.json`. <!-- R17 -->
- [x] T019 Scaffold `frontend/src/{main.tsx,App.tsx}`, `frontend/src/design/{tokens.css,ThemeProvider.tsx,Styleguide.tsx}`, accessible navigation/layout, and `frontend/tests/theme.spec.ts`; inspect/install relevant maintained frontend/browser tooling and record rationale; capture styleguide light/dark/mobile/desktop checkpoint in `docs/reports/design-checkpoint.md`. <!-- R18 -->
- [x] T020 Generate `frontend/src/api/{schema.d.ts,client.ts}` from OpenAPI, validate static exports in `frontend/src/lib/research.ts`, and implement request/status handling. Add contract drift and offline-static-loading checks under `frontend/tests/` with no manual competing request schema. <!-- R16 -->
- [x] T021 Build `frontend/src/pages/{Study.tsx,Rooms.tsx}`, `frontend/src/figures/{Panorama.tsx,RoomComparison.tsx}`, and `data/renders/manifest.json`; inspect render layouts, create browser derivatives in `frontend/public/rooms/`, retain originals, and test room filtering/comparison/keyboard fallback in `frontend/tests/rooms.spec.ts`. <!-- R19 -->
- [x] T022 Build `frontend/src/pages/Signals.tsx` and `frontend/src/figures/SignalTrace.tsx` with real selectable raw/cleaned/QC products, units/rate caveats and counts; add filter/missing/invalid-data coverage in `frontend/tests/signals.spec.ts`. <!-- R20 -->
- [x] T023 Build `frontend/src/pages/{Affect.tsx,People.tsx}` and `frontend/src/figures/{Circumplex.tsx,Sensitivity.tsx}` with experiment/participant filters, accessible tables, component/cohort distinctions and honest uncertainty; add tests in `frontend/tests/affect-people.spec.ts`. <!-- R20 -->
- [x] T024 Build `frontend/src/pages/{Simulator.tsx,ModelReport.tsx}`, target and physical input forms, model/support/error states and read-only evaluation views. Map old interactions in `docs/reports/interaction-map.md`; test valid prediction/optimization and offline/unavailable/weak-model states in `frontend/tests/simulator.spec.ts`. <!-- R21 -->
- [x] T025 Complete all-route responsive/keyboard/reduced-motion/theme checks in `frontend/tests/site.spec.ts`, capture final screenshots in `docs/reports/screenshots/`, and record design/accessibility findings and resolutions in `docs/reports/phase-8.md`; correct meaningful overflow/contrast/control issues in the actual site. <!-- R18 -->

### Phase 4: Polish and Reproduction

- [x] T026 Complete `Makefile`, `backend/src/pa/cli.py`, `.github/workflows/ci.yml`, frontend scripts and scientific test fixtures for setup/verify/audit/pipeline/test/site/all; use frozen locks, deterministic seeds, declared numeric tolerances, export/client drift checks and bounded browser tests. <!-- R22 -->
- [x] T027 Finish responsibility-mapped retirement of legacy `src/`, Python `frontend/`, `frontend_streamlit_archive/`, root `api.py`/`run_pipeline.py`, stale root packaging/config/log/cache outputs and obsolete runtime dependencies; preserve evidence paths from T002 and record active-reference/removal verification in `docs/reports/phase-4.md`. <!-- R25 -->
- [x] T028 Run clean-checkout reproduction from available original data with no legacy processed/artifact caches; record actual command outputs, regenerated-product comparison tolerances, performance/resource notes and failures/resolutions in `docs/reports/reproduction.md` and `docs/reports/phase-9.md`. <!-- R22 -->
- [x] T029 Prepare `render.yaml`, `frontend/vercel.json`, environment examples and `docs/operations.md` with locally validated build/start commands and free-tier deployment candidate settings; create `docs/release-readiness.md` separating verified local evidence from actual hosting/login/limits, ownership/licensing, DOI and named-release prerequisites. No release claim or deployment is required here. <!-- R24 -->
- [x] T030 Reconcile `README.md`, `CHANGELOG.md`, `docs/data_card.md`, `docs/model_card.md`, `docs/protocol/`, `docs/reports/phase-0.md` through `phase-9.md`, and `docs/specs/index.md`; prepare actual behavior and decision evidence for hydrate, including replacing inaccurate `docs/memory/website_architecture.md` with indexed architecture/research/operations memory during hydrate. Record independent findings and coordinator verdicts accurately. <!-- R23 -->

### Review rework cycle 1: Complete scientific presentation and failure contracts

- [x] T031 <!-- rework: cycle 2 RR-01; validate consumed artifact metadata fields before readiness, regenerate compatible artifact and verify affected contracts --> Resolve FR-03/05/06/07/08/09 backend contracts from `docs/reports/final-review.md`: preserve validated ID-based demographics and experiment-scoped sleep; publish filterable participant summaries, disagreement and generated model cohort/preprocessing/provenance; include opening counts in studied-support checks; validate artifact metadata shape; remove the unused `Trial.as_record`. Record any support-method amendment before regenerated outputs, and add focused regression tests. Coordinate export shape with T032. <!-- R5 R9 R11 R13 R15 R16 R17 R20 R21 -->
- [x] T032 Resolve FR-02/03/04/07/08 frontend behavior: scope People and Affect summaries to active filters, display measured demographics/sleep and separate comfort/disagreement, add Signals participant filtering, repair effective cohort/CCT chart styles, expose generated model evidence, and remove unsupported anonymization wording. Add targeted browser regressions and refresh affected screenshots/report evidence. <!-- R18 R20 R21 R23 -->
- [x] T033 Resolve FR-01 by pinning a verified setup-uv action revision, validate its inputs and remaining CI setup, and record the shared cause of both failed hosted checks. Implementation evidence: `docs/reports/ci-repair.md`. Hosted execution verification remains pending until the next stage-boundary push; this checkbox records the local repair, not a successful hosted run. <!-- R22 -->
- [x] T034 <!-- rework: cycle 2 RR-01; validate consumed artifact metadata fields before readiness, regenerate compatible artifact and verify affected contracts --> Regenerate compatible model/results after final backend changes; verify fresh-process artifact loading, complete relevant tests and clean-checkout reproduction, update affected reports/cards, and return evidence for a fresh independent full review. Do not mark acceptance on the reviewer's behalf. <!-- R13 R16 R22 R23 -->

## Execution Order

T001–T007 are evidence gates: preservation precedes deletion/migration; audit precedes analysis specification; the recorded independent audit/specification review precedes real signal/fusion/model comparison results. Review may expose valid limitations without inventing owner confirmation. Any changed method is an amendment before the affected rerun.

T008/T009 share signal/QC interfaces, so agree those interfaces before splitting ownership. T012/T013 can be implemented while scientific processing proceeds, but modeling T014 depends on T007, T010–T012. T014 must implement a fold-fitted construction path and cannot simply train on globally participant-normalized descriptive targets. T015 depends on actual evaluation and artifact validation; T016 depends on T012/T013/T015.

T019 can start after T004 using typed fixtures explicitly marked synthetic in tests only; public research pages T021–T024 require T017 products. T020 follows T017/T018. T025 requires all seven pages. T027 happens only after replacement responsibilities and source hashes are accounted for; T028 runs after cleanup and full tests. Final independent full review and hydrate are owned by the Fab coordinator after apply; T007 is an additional prerequisite checkpoint, not a substitute. No unchecked acceptance may be satisfied by screenshots of placeholder numbers.

## Acceptance

### Functional Completeness

- [x] A-001 R1: Reconciled roadmap/governance, actual branch/snapshot record and preserved model routing match intake; phase milestones and evidence gates are executable.
- [x] A-002 R2: Exact cleanup evidence identifies only the four authorized historical changes and their obsolete references; current/new work and tooling survive.
- [x] A-003 R3: Frozen backend/frontend installations, package/CLI and site build work with declared compatible versions and no active torch/Streamlit dependency.
- [x] A-004 R4: Source manifest and migration map account for recordings, metadata, thirty renders, prior image assets and thesis PDFs; verification detects tampering/missing files.
- [x] A-005 R5: Ingestion/protocol tests preserve owner provenance, unchanged ratings, separate comfort and structural missingness; no invented protocol or identities appear.
- [x] A-006 R6: Actual file-level audit exports rates as evidence-bearing scenarios, flags duration/counter discrepancies and reconstructs observed order without false timing certainty.
- [x] A-007 R7: Versioned specification, primary sources, parameter rationale, sensitivity/failure rules and recorded independent checkpoint precede affected analysis; amendments are traceable.
- [x] A-008 R8: EEG/ECG synthetic recovery and invalid-input tests pass; actual per-trial validity/reasons and raw/cleaned/QC products exist with declared units/rate caveats.
- [x] A-009 R9: Real component/fused/partial products and alpha/experiment sensitivity preserve constructs and missingness; fold-target construction is separate from descriptive normalization.
- [x] A-010 R10: Actual descriptive reports identify effective groups, uncertainty assumptions, confounding and unavailable inference without causal/validated-emotion claims.
- [x] A-011 R11: One physical schema/builder controls all consumers; total opening-area, derived-feature, categorical, finite-value and missingness tests pass.
- [x] A-012 R12: Fold memberships, training-only transforms/tuning, baselines and real room/participant evaluation results or specific eligibility failures are exported; leakage tests pass.
- [x] A-013 R13: Complete artifact metadata and pipeline load consistently; trained/reloaded/direct/CLI/API parity and incompatible/missing artifact tests pass. Weak status is honest. <!-- final-rereview-cycle-2: RR-01 resolved; fresh valid-artifact readiness/parity and 25 malformed-field variants across all four public routes pass. See docs/reports/final-rereview-cycle-2.md. -->
- [x] A-014 R14: Finite domain validation, score-at-target, bounds and monotonicity tests pass for the documented fixed-diameter score and user-selected targets.
- [x] A-015 R15: Seeded optimization returns distinct valid supported candidates or truthful empty/unavailable outcomes; score and model status agree with prediction.
- [x] A-016 R16: Browser exports validate, carry provenance and contain actual research data; all research pages function with API disabled, including missing/empty states.
- [x] A-017 R17: Versioned API/OpenAPI, structured error/readiness/CORS/request-bound tests and generated-client drift checks pass without public training/file-loading routes. <!-- final-rereview-cycle-2: RR-01 resolved; fresh valid-artifact readiness/parity and 25 malformed-field variants across all four public routes pass. See docs/reports/final-rereview-cycle-2.md. -->
- [x] A-018 R18: Seven routes share working persistent Light/Dark/System modes; recorded styleguide/final desktop/mobile screenshots and keyboard/reduced-motion checks show usable controls and content.
- [x] A-019 R19: Study/Rooms use generated counts and all mapped renders; comparison/filtering and panorama fallback work while unknown CCT/view conventions remain explicit.
- [x] A-020 R20: Signals/Affect/People expose actual QC/components/sensitivity and ID-based filtering, accessible tables and explicit missing/invalid/empty states.
- [x] A-021 R21: Simulator target/prediction/optimizer and read-only Model report work; weak/offline/unavailable states preserve inputs and interaction mapping accounts for legacy features.
- [x] A-022 R22: Meaningful backend/frontend/contract/browser checks pass in frozen environments; clean-checkout regeneration and numerical-tolerance evidence are recorded without stale caches.
- [x] A-023 R23: README/cards/phase reports/specs and hydrate-ready evidence reflect actual implementation; commands and independent review findings/verdicts are not fabricated.
- [x] A-024 R24: Locally validated deployment preparation and release runbook clearly separate external hosting/licensing/DOI/named-release conditions; actual deployment is not claimed.
- [x] A-025 R25: Documented runtime and tests use replacement paths only; legacy responsibility map, preserved-source hashes and active-reference checks support removal.

### Behavioral Correctness

- [x] A-026 R5: Already transformed signed ratings remain numerically identical after ingestion; missing spatial/sleep values remain missing and Experiment 1 comfort is never an affect-axis surrogate.
- [x] A-027 R8: Failed/short/flat/corrupt physiology yields invalidity and reason codes, not nominal physiological values, neutral targets or invented baseline correction.
- [x] A-028 R11: Opening count does not multiply already-total area, contradictory derived inputs are rejected, and all consumers produce the same ordered features.
- [x] A-029 R12: Altering held-out outcomes/covariates does not change fitted training transforms or selected training-only settings; participant and room folds meet their separate contracts.
- [x] A-030 R14: Space type never silently changes the selected emotional target, and all score consumers use the same formula and projection policy.

### Removal Verification

- [x] A-031 R25: Active dependencies/imports/routes contain no legacy Streamlit/torch app, unversioned inference/training route, duplicate score, fixed type-target or heuristic-confidence fallback.
- [x] A-032 R2: Current Fab records, `.agents/`, original user files and source hashes survive historical-change cleanup; deletion scope is reviewable from exact paths.

### Scenario Coverage

- [x] A-033 R6: Synthetic audit tests cover modulo wrap, discontinuity and rate/duration conflict without asserting that sample-count/logged-duration alone proves hardware rate.
- [x] A-034 R8: Known-band EEG and known RR interval fixtures validate feature mathematics and channel/sign/unit conventions, beyond shape/range checks.
- [x] A-035 R13: At least one fitted synthetic test artifact exercises save/reload/CLI/API parity even if the real dataset cannot support a usable model.
- [x] A-036 R18: Every route is exercised in both themes at representative mobile/desktop widths; System preference, persistence, keyboard focus and reduced motion are covered.
- [x] A-037 R21: Browser tests cover user-selected target, valid responses and offline/unavailable/weak-model responses without hardcoded public research metrics.

### Edge Cases & Error Handling

- [x] A-038 R9: No-self-report, partial-modality, single eligible trial and absent cohort cases remain explicit; no fictitious animation origin or complete-fusion label appears.
- [x] A-039 R11: NaN/infinity, zero/negative dimensions, excessive walkable/opening area, contradictory count/area and invalid categoricals fail clearly; documented optional omissions remain valid inputs.
- [x] A-040 R15: Exhausted candidate budget, impossible support/constraints and duplicates terminate deterministically with a truthful result, not an unbounded loop.
- [x] A-041 R17: Invalid/missing/incompatible artifacts and invalid requests return documented statuses without exposing tracebacks; process liveness is distinguished from prediction readiness. <!-- final-rereview-cycle-2: RR-01 resolved; fresh valid-artifact readiness/parity and 25 malformed-field variants across all four public routes pass. See docs/reports/final-rereview-cycle-2.md. -->
- [x] A-042 R10: Insufficient independent groups, singular analysis and absent calibration evidence produce unavailable/qualified inference rather than fabricated intervals or p-values.

### Code Quality

- [x] A-043 Pattern consistency: Replacement naming, layering and interfaces follow the documented package/frontend conventions.
- [x] A-044 No unnecessary duplication: Shared schema, feature builder, score, export contract and utility behavior have single ownership.
- [x] A-045 Readability: Domain transformations and failure paths are understandable, typed at boundaries and documented where scientific interpretation matters.
- [x] A-046 Existing patterns: Deviations from useful retained conventions are justified by replacement architecture rather than accidental parallel abstractions.
- [x] A-047 Composition: Processing, artifact loading, API and presentation are composed through clear interfaces rather than unnecessary inheritance.
- [x] A-048 Function scope: Functions longer than fifty lines have a clear domain reason or are decomposed into cohesive units.
- [x] A-049 Utility reuse: Existing suitable utilities are reused/migrated or explicitly replaced; repeated implementations do not survive cleanup.
- [x] A-050 Named configuration: Scientific settings and protocol categories use named/configured values with decision provenance; useful equations and ordinary UI constants are not prohibited by blanket literal linting.

### Security

- [x] A-051 R17: Public API accepts bounded validated scientific inputs, configured origins and trusted local artifacts only; no upload, arbitrary path, training or deserialization endpoint exists.
- [x] A-052 R24: Credentials are absent from tracked artifacts; third-party licences remain preserved; release readiness does not assert unverified permission to associate participant names with physiological records.

## Verification and Release Notes

Each task names its verification file or recorded command evidence; acceptance maps back to its R identifier. Review checks actual results, not task checkbox assertions. Synthetic fixtures test algorithms and failure paths but MUST NOT populate the public research pages. Avoid extra heavy infrastructure: bounded sklearn comparisons, local generated bundles, a small FastAPI app and targeted browser checks suffice. CI may use small synthetic fixtures; clean-checkout reproduction separately exercises available real data.

Externally pending release work is not checked off as locally completed: hosting account/project access, current free-tier limits, production URLs/domain/DNS, final source-specific licensing approval, DOI registration, and evidence for any named biometric release. The repository is already public and existing recordings are tracked; do not manufacture a private-to-public step or require an external data archive merely to reproduce locally. Preserve supplied assets in repository-accessible form and document delivery-size constraints based on measured sizes.

## Assumptions

| # | Grade | Decision | Rationale | Scores |
|---|-------|----------|-----------|--------|
| 1 | Certain | Keep one full-scope Fab change with ordered evidence gates and disjoint delegated tasks | Intake authorizes full rebuild; preserves traceability without inventing independent releases | S:95 R:85 A:90 D:90 |
| 2 | Certain | Use current Fab branch and a non-overwriting legacy reference plus an uncommitted-file inventory | Existing user work and coordinator-established branch must survive | S:95 R:90 A:95 D:90 |
| 3 | Confident | Permit explicitly conditional rate scenarios after audit/specification review when hardware setting cannot be confirmed | Allows honest reanalysis without turning inference into fact or blocking unrelated implementation | S:85 R:75 A:75 D:80 |
| 4 | Confident | Fix Neuro-Score normalization to the signed square's diameter sqrt(8) | Intake requests documented monotone bounded proximity; fixed normalization avoids target-dependent scales | S:75 R:80 A:80 D:75 |
| 5 | Certain | Separate room-held-out and participant-held-out claims and fold-fitted target construction | Data dependence and unknown new-person calibration prohibit global descriptive target leakage | S:90 R:80 A:90 D:85 |
| 6 | Confident | Select exact signal/statistical settings in the evidence-led specification instead of freezing legacy settings in this plan | Hardware/unit/quality evidence remains incomplete; method gate explicitly requested | S:95 R:65 A:70 D:85 |
| 7 | Certain | A scientifically unavailable real model can pass only with implemented/evaluated paths, explicit evidence and synthetic parity tests | Intake forbids fabricated inference while requiring a working experimental interface | S:95 R:90 A:95 D:95 |
| 8 | Confident | Use a compact static research bundle and selectable bounded traces instead of shipping all raw samples to browsers | Preserves source data and useful exploration while respecting free-tier delivery and mobile use | S:75 R:80 A:80 D:75 |
| 9 | Certain | Local acceptance covers deployment preparation; real external release prerequisites remain separately pending | Coordinator confirms public repo and available local originals; hosting/licensing/named consent evidence cannot be invented | S:100 R:90 A:95 D:95 |
| 10 | Certain | Preserve current routing and require an additional audit/specification review before scientific results | AGENTS.md requires fresh independent review; intake requires scientific specification before implementation | S:100 R:85 A:95 D:90 |

10 assumptions (6 certain, 4 confident, 0 tentative).

## Deletion Candidates

None — the unused `Trial.as_record` wrapper and import identified by FR-09 have been removed. Planned legacy retirement already removed the redundant runtime applications; checksum-equivalent source evidence copies remain intentionally preserved.
