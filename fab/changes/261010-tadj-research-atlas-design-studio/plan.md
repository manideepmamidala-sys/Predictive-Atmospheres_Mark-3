# Plan: Research Atlas and Fused Neuro-Score Design Studio

**Change**: 261010-tadj-research-atlas-design-studio
**Intake**: [intake.md](intake.md)
**Created**: 2026-10-10

The intake overrides conflicting instructions and numerical expectations in the original revision guide. The owner approved the exact v1.2 source at CP-Spec (SHA-256 `51c01ef6ccdf2f4318ac786d1bb39afeb1aa2bcf3bc93039479a4ed2454603ac`) and chose CP-A defer-LFS. On 2026-10-10 the user explicitly instructed, `$fab-ff with your CP-B decidions`, followed by `$fab-ff approve all the future checkpoint automatically and continue the work`. These instructions delegate CP-B, CP-C, CP-E1 and CP-E2 dispositions to the agent workflow and supersede the earlier personal-owner signoff requirement for those checkpoints. This is authorization to make evidence-based decisions after concrete review, not a claim of human inspection or permission to invent evidence. Tasks are checked only with completion evidence; unresolved scientific uncertainty stays unavailable or explicitly limited. External deployment, purchase and history rewriting remain outside this delegation.

## Requirements

### Research provenance: source understanding and preservation

#### R1: Preserve source-referenced research knowledge
The implementation SHALL inspect the presentation, booklet, DOCX, linked booklet assets, corrected protocol, legacy formulas/code and original demonstrations before retiring repository copies. `docs/research/thesis-source-context.md` SHALL preserve page/file references, motivation, question, hypothesis, experiment diagrams, original formulas, original studio behavior, prototype evidence and retained asset provenance. Historical claims, owner reports and observed data MUST remain distinct; inconsistent baseline, breaks, questionnaires and rate descriptions MUST NOT replace the corrected protocol.

- **GIVEN** contradictory thesis and investigator accounts, **WHEN** research context is distilled, **THEN** both sources and the conflict are identified without inventing resolution or upgrading a demonstration into validated science.

#### R2: Verify every cleanup candidate
Cleanup SHALL inventory hashes, sizes, roles, canonical counterparts, relevant read-only PC originals and required knowledge/assets before removal. Unique recordings, metadata and scientific evidence MUST be preserved. Personal thesis PDF/ZIP/DOCX copies and obsolete plans SHALL be removed from current project contents only where verification is complete; they MUST NOT merely be relocated to a public archive. Scientific methods, decisions, cards, useful reports, active Fab records, working machinery and unrelated user edits SHALL remain protected. Routine builds MUST NOT depend on Windows paths.

- **GIVEN** a duplicate with matching retained bytes and verified PC original where required, **WHEN** its knowledge/assets are preserved, **THEN** authorized current-tree removal and link repair may proceed without another deletion approval.
- **GIVEN** missing/mismatched originals or unique evidence, **WHEN** cleanup runs, **THEN** that item is retained with an explicit reason; no Windows file or Git history is modified.

#### R3: Inventory-led storage choice
CP-A SHALL present measured remaining storage and a concrete retain-Git/LFS choice, current dated official free-tier limits, bandwidth/build implications and reproducibility consequences. Any new storage migration MUST await the owner's recorded choice. Git-history rewriting and a second repository are excluded.

- **GIVEN** CP-A is pending, **WHEN** cleanup or draft methods are ready, **THEN** those authorized tasks may proceed, but LFS tracking/migration cannot.

#### R4: Reproducibility through cleanup and version changes
Canonical source locations SHALL drive `scripts/build_source_manifest.py`, `data/MANIFEST.sha256` and consumers; retired document hashes SHALL remain in provenance records outside the runtime manifest. CI SHALL detect regenerated scientific-artifact drift. Volatile revision metadata SHALL be separated from scientific content identity without weakening model compatibility or losing revision provenance. Intentional method changes SHALL produce new versioned artifacts, not forced old hashes.

- **GIVEN** only source paths change, **WHEN** verification and unchanged-method reproduction run, **THEN** retained source bytes and scientific outputs agree within documented comparison rules, with attributable path/provenance differences.

### Scientific method: proposal, approval and execution

#### R5: Explicit CP-Spec method barrier
A separately marked retrospective v1.2 **DRAFT** SHALL propose concrete mappings, normalizations, modality/fusion weights, eligibility, QC, rate/onset handling, inference and evaluation settings with evidence, alternatives and consequences. `DECISIONS.md` proposals SHALL be unmistakably pending. The reviewed v1.1 specification and executable settings MUST remain authoritative until the owner explicitly approves a version/hash at CP-Spec; a plan, intake score or pipeline invocation is not approval. Source inspection and unchanged-method regression are allowed; new dependent signal, affect, validity, model or catalogue analysis is not.

- **GIVEN** an unapproved numerical proposal, **WHEN** a worker reaches CP-Spec, **THEN** it reports the reviewable draft and stops dependent execution without treating the proposal as policy or marking its implementation complete.

#### R6: Evidence-aware timebase and EEG QC
After CP-Spec, signal processing SHALL implement the approved timebase audit and rate sensitivities, sample/logged-duration discrepancies, counter continuity, channel imbalance, absolute amplitude, clipping/flat/gap, line-noise and EMG checks. Counter continuity alone MUST NOT confirm rate. The draft MUST reconcile retained versus excluded first five seconds, specify whether line noise is measured before filtering and its numerator/denominator frequency bands, and define the exact logarithmic engagement expression. Alpha suppression, engagement, ocular blink and muscle measures SHALL remain independently visible; any approved composite is exploratory.

- **GIVEN** a dead or high-gain channel or a truncated/gapped recording, **WHEN** QC runs under approved settings, **THEN** reproducible channel/epoch/trial reasons and coverage are emitted without invented samples, preordained participant exclusions or neutral replacements.

#### R7: Manual QC and cardiac validity
Each flagged signal SHALL have raw trace/spectrum review material and an inspectable decision entry. Under the user's explicit delegation, CP-B SHALL record actual AI-assisted accept/reject/uncertain dispositions, reviewer identity, rationale, inspected evidence and limitations before reviewed eligibility feeds downstream interpretation. Subj_F/Subj_H SHALL be inspected per channel/trial, not excluded to reproduce guide expectations. ECG SHALL retain independent quality and contiguous-run gates, valid-seconds coverage and representative raw/filtered examples. HR is the main cardiac comparison; eligible RMSSD remains descriptive under approved CP-Spec.

- **GIVEN** a flag without a supported delegated disposition, **WHEN** downstream processing requests final eligibility, **THEN** it remains pending/ineligible until CP-B is recorded; uncertainty never promotes a signal.

#### R8: Separate components, fusion and cohorts
EEG/ECG SHALL lead the research narrative, with self-report as secondary comparison and fusion a constructed point from subjective and physiology-derived coordinates in the declared system. Emphasis MUST NOT silently set numerical weights. Approved descriptive versus fold-fitted transformations and complete/partial/component-only states SHALL remain explicit. Every record SHALL be accounted for and used where eligible; E1 comfort MUST remain separate from valence, while E2/E3's different rating procedures require separate-first analyses and a stated pooling justification.

- **GIVEN** usable EEG but rejected ECG or absent self-report, **WHEN** affect exports are constructed, **THEN** usable components remain available, missing axes remain missing, and no partial record is mislabeled complete fusion.

#### R9: Complete physiology validity and disagreement reporting
The approved validity matrix SHALL report all prespecified EEG arousal/self-report, EEG/HR, HR/self-report, blink/EMG and FAA/valence relationships separately for E2/E3, with eligible trial/person/room counts and justified uncertainty or explicit unavailable reasons. Disagreement and component/fusion density products SHALL be descriptive; no proven privacy masking, causal design control or objective emotion certainty may be claimed.

- **GIVEN** a null association or too few independent groups, **WHEN** results are exported, **THEN** the planned result remains visible with its limitations or reasoned unavailable status.

### Models and Design Studio contracts

#### R10: Honest comparative model evaluation
The pipeline SHALL answer room-rating consistency, known-room relative-profile transfer to held-out people, room-attribute generalization to unseen rooms, and physiological agreement with report; it SHALL also evaluate the fused-target model used by the studio. Specified cohorts, families/search, group splits, preprocessing, target calibration, baselines, nulls, uncertainty and learning curves MUST be fixed at CP-Spec. Learned transforms SHALL fit within each training partition, including inner folds. Centering with held-out observed ratings SHALL be labeled relative-response evaluation, not an absolute prediction for an unobserved person. Guide F1–F10 and expected statistics are reproduction questions, never acceptance targets.

- **GIVEN** a weak or unfit fused model, **WHEN** evaluation completes, **THEN** model/data cards and exports report actual baseline comparison or unavailable status without fabricated intervals or suppression of nulls.

#### R11: One trusted physical and prediction contract
`RoomInput`, shared derived-feature construction, fitted preprocessing and model artifact SHALL serve training, CLI, API and generation. No request-time fitting or parallel room schema is allowed. Physical validity and empirical support SHALL remain separate, including opening counts and categorical combinations. Artifact version/byte/dependency checks and structured unavailable readiness SHALL remain intact. CP-C MUST precede publication of new model findings.

- **GIVEN** identical valid input and a compatible artifact, **WHEN** direct, CLI, API and generation inference run, **THEN** they use identical features and prediction/score semantics.

#### R12: Fused target-distance scoring
Studio forward prediction SHALL expose only the fused point and Neuro-Score, with a user-selected emotional target `t` in `[-1,1]^2`. Displayed score SHALL be `100 * clip(1 - ||p-t|| / sqrt(8), 0, 1)`; API 0–1 and UI 0–100 conversions SHALL be explicitly versioned/documented and tested. Raw/clipped prediction provenance SHALL follow the approved spec. Score MUST be explained as proximity, not confidence, health, design quality or success probability.

- **GIVEN** fused position equal to the target, **WHEN** scored, **THEN** UI displays 100; opposite corners display 0, and no component-mode selector changes the prediction target.

#### R13: Closest requested score with constraints
Generation SHALL accept a separate requested numeric score `s` in `[0,100]` relative to the same emotional target and minimize `abs(predicted_neuro_score-s)` over bounded, seeded feasible search. Locks, allowed ranges, room type and lighting constraints MUST be respected, derived geometry coherent, and empirical support reported. Deterministic tie handling and duplicate treatment SHALL be documented. Results SHALL report requested/achieved/difference, fused point, parameters and studied reference without claiming global optimality.

- **GIVEN** feasible scores 64.5 and 95 and request 65, **WHEN** candidates rank, **THEN** 64.5 ranks first.
- **GIVEN** impossible locks/ranges, **WHEN** search runs, **THEN** an explained empty result is returned without relaxing constraints.

### Research atlas: complete exports and communication

#### R14: Complete versioned analysis catalogue
Backend exports SHALL cover S1–S5, R1–R9, B1–B8, P1–P5 and Methods, including fused comparisons and studio evaluation. Each product SHALL contain question, evidence-based takeaway or unavailable message, counts/units, method, caveat, validity, schema/spec/data provenance and chart data. S2 MUST represent branching eligibility, not false nested attrition. Every legacy chart SHALL map to a current route/export or reasoned replacement/unavailability. Frontend schemas MUST validate products; frontend code MUST NOT calculate research statistics.

- **GIVEN** any catalogue ID including an unsupported analysis, **WHEN** exports build, **THEN** it has a validated current product and route mapping rather than silent omission or historical numerical reuse.

#### R15: Eight-page information architecture
The site SHALL expose `/` Predictive Atmospheres, `/study` The Study, `/rooms` Rooms & Experience, `/body` Body & Experience, `/prediction` Prediction & Findings, `/studio` Design Studio, `/explore` Data Explorer and `/methods` Methods & Research Context. Horizontal navigation, URL filters, useful old-route redirects and a real 404 SHALL work. Project policy wording SHALL match eight pages without weakening scientific rules. Static research SHALL remain readable independently of API availability.

- **GIVEN** a valid old deep link, **WHEN** followed, **THEN** it resolves to the corresponding current view with useful filters; unknown routes show a real 404.

#### R16: Thesis-led landing and researcher context
Landing copy SHALL explain concept, motivation, question, hypothesis, Form/Lighting/Function experiments, linked human–spatial metrics, approach and contribution, with calls to research and studio. It MUST NOT contain result-summary cards or a featured findings plot. Concrete copy SHALL await CP-E1. Methods/context SHALL describe Grasshopper and AI rendering as implemented thesis demonstrations, not new integrations or unbuilt promises. Public content SHALL use Manideep Mamidala, supplied email/LinkedIn/IAAC links and an appropriately derived authorized portrait; no invented biography or thesis/CV/portfolio download links.

- **GIVEN** a first-time visitor, **WHEN** reading the landing, **THEN** the thesis idea and study approach are clear without requiring results or interpreting engineering caveats.

#### R17: Accessible evidence-led research views
Charts SHALL have interpretable title/subtitle, axes/ticks/units, legends, counts, justified uncertainty, how-to-read help and filtered data links. Signed affect plots SHALL include −1/0/1 ticks, quadrants and keyboard access. Demographic dots replace unjustified violins; spectral, HR/eligible-HRV, density/target-vector, contrast, correlation, disagreement, importance and parallel-coordinate ideas SHALL be restored with current evidence. Light/Dark/System, keyboard access, reduced motion and responsive layout SHALL remain supported. Charting and optional panorama modules SHALL load by route; signal details SHALL show load/error progress.

- **GIVEN** a keyboard or small-screen visitor in either theme, **WHEN** reading charts or room detail, **THEN** information and controls remain usable without hover-only evidence or color-only encoding.

#### R18: Integrated Design Studio interaction
One Studio page SHALL support both fused forward prediction and closest-score generation, studied-room presets, target selection, locks/ranges, schematic 3D geometry, comparison rooms and clear result provenance. Studied imagery MUST NOT impersonate generated renders. Offline readiness SHALL be shown before submit; static comparisons SHOULD remain available. Buttons, loading/error/empty states, numeric input wheel behavior and navigation SHALL be tested.

- **GIVEN** entered dimensions are locked, **WHEN** generation submits, **THEN** the request and every returned candidate preserve them; if the API is unavailable no prediction is fabricated.

### Delivery: review, reproduction and release

#### R19: Checkpoint and validation evidence
CP-A, CP-Spec, CP-B, CP-C, CP-E1 and CP-E2 SHALL retain dated concrete proposals/results, the user's actual delegation or direct decision, agent dispositions where delegated, and affected versions. A delegated disposition requires concrete evidence and named AI review; it MUST NOT be represented as the owner's personal inspection. Reviewable workstream slices SHALL retain branch ancestry and unrelated edits. Tests SHALL cover scientific adverse cases, fold isolation, score scales, closeness ranking, constraints/no-solution/offline states, exports/manifests and navigation. Playwright SHALL exercise every route at 1440×900 and 390×844 in both themes, keyboard and number controls; Lighthouse accessibility target is at least 95 per route. CP-E2 MUST precede release.

- **GIVEN** only the preparation slice is finished, **WHEN** reporting progress, **THEN** its checks are recorded and downstream tasks/whole-change completion remain open.

#### R20: Honest reproducible release
README, CHANGELOG, cards, operations, release readiness and affected memory SHALL describe actual approved implementation/results. `make verify-data`, `make pipeline`, `make lint test site` SHALL remain viable at workstream boundaries; pre-CP-Spec pipeline runs may only reproduce current approved methods. Hosting SHALL be chosen from actual dated free-tier needs/limits without promising perpetual always-on compute. Public trial data/renders/photographs are authorized; participant display codes SHALL replace named associations. No domain purchase or new licensing terms are authorized by this plan. Fresh independent review SHALL use the AGENTS.md model routing; deployment/ship status SHALL reflect actual checks and authorized actions.

- **GIVEN** a successful local build but no verified hosted service, **WHEN** release readiness is written, **THEN** it reports local success and outstanding hosting facts separately.

### Non-Goals

- Git history rewriting, a second repository, editing Windows originals, blanket report deletion or silently staging pre-existing edits.
- Choosing scientific thresholds/weights to obtain preferred correlations, treating fusion as ground truth, or guaranteeing causal control or model improvement.
- New live Grasshopper/AI-rendering integrations, invented profile credentials, personal-document downloads or a domain purchase.

### Design Decisions

#### Separate proposed and executable science
**Decision**: Store the v1.2 proposal separately as `docs/specs/analysis-v1.2-draft.md`; retain the current approved runtime settings until CP-Spec explicitly approves a hash/version.
**Why**: Reviewable method preparation must not silently authorize a reanalysis.
**Rejected**: Overwriting the current reviewed method and running a pipeline before owner approval.
*Introduced by*: 261010-tadj-research-atlas-design-studio

#### Extend the existing fitted contract
**Decision**: Extend the existing room/schema, score and search modules, retaining API 0–1 score compatibility while adding explicit UI 0–100 requested-score conversion and contract metadata.
**Why**: Existing clients and artifact parity should remain inspectable while generation gains the requested objective.
**Rejected**: A disconnected studio estimator, a second room feature implementation, or silent API scale changes.
*Introduced by*: 261010-tadj-research-atlas-design-studio

#### Canonical exports and route-split charting
**Decision**: Use backend analysis products with shared frontend schemas and route-split Observable Plot/d3-contour presentation after dependency validation; geometry/layout operations may occur in the browser, research statistics may not.
**Why**: This fits the current static-export architecture and the guide's reversible charting proposal.
**Rejected**: Recomputing statistics in views or copying obsolete chart values.
*Introduced by*: 261010-tadj-research-atlas-design-studio

## Tasks

### Phase 1: Setup — authorized preparation and proposals

- [x] T001 Record initial branch/HEAD, unrelated edits, tracked/untracked source inventory, sizes and SHA-256 values in `docs/reports/revision-2026-10/source-inventory.json`; identify cleanup dispositions and relevant PC-original matches without modifying originals. <!-- R2 -->
- [x] T002 Complete `docs/research/thesis-source-context.md` from presentation/booklet/DOCX/legacy code and linked assets, including original formulas, studio/prototype behavior, page references, corrected-protocol conflicts and retained-asset mapping. <!-- R1 -->
- [x] T003 Capture the guide's full catalogue/legacy-chart crosswalk and agreed overrides in `docs/research/analysis-catalogue.md` before removing `MARK3_REVISION_PLAN.md`; distinguish exploratory guide claims from required outcomes. <!-- R14 -->
- [x] T004 Update `scripts/build_source_manifest.py`, `backend/src/pa/io/manifest.py` and `backend/tests/test_manifest.py` to use verified canonical locations, preserve source digest correspondence and separate retired private-document provenance from routine verification. <!-- R4 -->
- [x] T005 Remove only verified current-tree duplicates/obsolete personal and planning documents recorded by T001–T004; regenerate `data/MANIFEST.sha256`, preserve retained raw/metadata/renders and needed assets, and record every removed/retained disposition in `docs/reports/revision-2026-10/cleanup.md`. <!-- R2 -->
- [x] T006 Repair affected links and ignore rules in `.gitignore`, `README.md`, `docs/` and `CHANGELOG.md`; retain required scientific reports, third-party attribution, `AGENTS.md`, active Fab records and unrelated edits. <!-- R2 -->
- [x] T007 Repair `.github/workflows/ci.yml`, `scripts/compare_reproduction.py` and `backend/src/pa/modeling/artifact.py` as needed for regenerated-artifact drift and separate volatile revision provenance; add targeted compatibility/drift tests in `backend/tests/test_artifact.py` and `backend/tests/test_exports.py`. <!-- R4 -->
- [x] T008 Write `docs/reports/revision-2026-10/CP-A.md` with measured remaining assets, dated official storage/LFS free limits, concrete retain-Git/LFS recommendation and impact; explicitly leave owner choice pending and history rewrite excluded. <!-- R3 -->
- [x] T009 Draft timebase, onset, EEG/ECG QC, manual-review, candidate-expression and inference/sensitivity sections in `docs/specs/analysis-v1.2-draft.md`, citing source evidence and proposing concrete settings without modifying executable `backend/src/pa/decisions.yaml`. <!-- R5 -->
- [x] T010 Complete that draft's coordinate mappings, normalization, modality/fusion weights, missingness/cohorts, separate-first pooling, model families/search/folds, null/uncertainty and feasible learning-curve design; append clearly pending proposals in `DECISIONS.md`. <!-- R5 -->
- [x] T011 Write `docs/reports/revision-2026-10/CP-Spec.md` with the exact draft/version/hash, decision matrix, rationale/alternatives, source unknowns and affected reruns; retain pending status and current reviewed methods. <!-- R5 -->
- [x] T012 Record preparation validation in `docs/reports/revision-2026-10/preparation-validation.md`: source digests, PC-original checks, link checks, targeted tests and viable current-method make commands, explaining intentional provenance-only differences and outstanding tasks. <!-- R19 -->

### Phase 2: Core Implementation — after the named checkpoints

- [x] T013 Record the actual CP-A owner choice in `docs/reports/revision-2026-10/CP-A.md`; apply only the selected current-tree storage policy to `.gitattributes`, CI retrieval and `docs/operations.md`, or document the explicit retain-Git choice without migration. <!-- R3 -->
- [x] T014 Record explicit CP-Spec approval of the concrete version/hash in `docs/reports/revision-2026-10/CP-Spec.md`; only then promote approved methods into `docs/specs/analysis-v1.md`, `docs/specs/index.md`, `DECISIONS.md` and `backend/src/pa/decisions.yaml`, preserving prior scientific provenance. <!-- R5 -->
- [x] T015 Extend `backend/src/pa/io/audit.py` and `backend/tests/test_audit.py` for approved timebase evidence/status, onset policy and rate scenarios; export `artifacts/results/timebase.json` with spec provenance. <!-- R6 -->
- [x] T016 Implement approved channel/epoch/trial QC and independent arousal candidates in `backend/src/pa/signals/qc.py`, `backend/src/pa/signals/eeg.py` and `backend/tests/test_eeg.py`; cover known bands, flat/dead/gain/noise/blink/gap/short cases without outcome-tuned thresholds. <!-- R6 -->
- [x] T017 Extend `backend/src/pa/signals/ecg.py`, `backend/src/pa/signals/run.py` and `backend/tests/test_ecg.py` for approved cardiac coverage/eligibility and examples, preserving contiguous-run failure rules. <!-- R7 -->
- [x] T018 Generate the approved QC review queue through `backend/src/pa/results/review.py`, `artifacts/results/qc_review.json` and `artifacts/review/`; write concrete flagged-channel evidence in `docs/reports/revision-2026-10/CP-B.md` with pending owner decisions. <!-- R7 -->
- [x] T019 Record delegated evidence-based CP-B agent dispositions and per-trial/channel decisions in `docs/reports/revision-2026-10/CP-B.md` and `artifacts/results/qc_review.json`; integrate only those decisions into reviewed eligibility. <!-- R7 --> <!-- rework: M2 remove unused administrative writer; preserve active CP-B integration -->
- [x] T020 Implement approved descriptive coordinates, fusion and partial/component-only cohorts in `backend/src/pa/affect/normalization.py`, `backend/src/pa/affect/fusion.py`, `backend/src/pa/affect/run.py` and `backend/tests/test_affect.py`; account for all records and E1/E2/E3 boundaries. <!-- R8 -->
- [x] T021 Implement approved validity, disagreement and component/composite comparisons in `backend/src/pa/affect/analysis.py` and `backend/tests/test_analysis.py`; export `artifacts/results/validity.json` and reasoned unavailable outcomes. <!-- R9 -->
- [x] T022 Add room/person/residual, agreement and known-room relative-transfer analyses to `backend/src/pa/analysis/ratings.py` and `backend/src/pa/analysis/transfer.py`, with grouped baseline/null/centering tests in `backend/tests/test_analysis.py`. <!-- R10 -->
- [x] T023 Extend `backend/src/pa/modeling/targets.py`, `backend/src/pa/modeling/splits.py` and `backend/src/pa/modeling/evaluate.py` for approved component/self-report/fused cohorts and fold-contained transformations; test adversarial held-out mutations in `backend/tests/test_evaluation.py`. <!-- R10 -->
- [x] T024 Implement approved unseen-room candidate evaluation, learning curves and importance in `backend/src/pa/modeling/evaluate.py` and `backend/src/pa/modeling/train.py`; test insufficient groups, constants, singular fits and unsupported pooling in `backend/tests/test_train.py`. <!-- R10 -->
- [x] T025 Persist the fitted fused artifact and actual model comparisons in `backend/src/pa/modeling/artifact.py`, `artifacts/model/` and `artifacts/results/model_poc.json`; update `docs/model_card.md`, `docs/data_card.md` and `docs/reports/revision-2026-10/CP-C.md` with actual results and pending publication review. <!-- R11 --> <!-- rework: Refresh artifact provenance after nonnumerical export/helper source corrections -->
- [x] T026 Record delegated evidence-based CP-C agent disposition of exact comparison/model versions in `docs/reports/revision-2026-10/CP-C.md` before new model findings are staged for public pages. <!-- R11 --> <!-- rework: Record current hashes and unchanged numerical evidence after rework -->
- [x] T027 Extend shared `backend/src/pa/features/schema.py`, `backend/src/pa/features/builder.py` and `backend/src/pa/features/support.py` only as required for approved studio inputs, locks/ranges and support; verify geometry/count/type consistency in `backend/tests/test_features.py`. <!-- R11 -->
- [x] T028 Extend `backend/src/pa/scoring/neuro_score.py`, `backend/src/pa/api/schemas.py` and `backend/tests/test_scoring.py` for explicit target/score scale boundaries and approved raw/clipped provenance without changing the distance formula. <!-- R12 -->
- [x] T029 Implement bounded seeded closest-requested-score candidate ranking, locks/ranges, deterministic ties, deduplication and reasoned no-solution output in `backend/src/pa/optimize/search.py`; verify request 65 ranks 64.5 ahead of 95 and respects locked dimensions in `backend/tests/test_optimize.py`. <!-- R13 -->
- [x] T030 Wire shared prediction/generation contracts through `backend/src/pa/api/app.py`, `backend/src/pa/api/errors.py` and `backend/src/pa/cli.py`; regenerate `frontend/src/api/schema.d.ts` and verify direct/CLI/API parity and artifact failures in `backend/tests/test_prediction_parity.py` and `backend/tests/test_api.py`. <!-- R11 -->

### Phase 3: Integration & Edge Cases — exports and atlas

- [x] T031 Define the catalogue product envelope and explicit unavailable schemas in `backend/src/pa/results/schemas.py`, `backend/src/pa/analysis/__init__.py`, `frontend/src/lib/research.ts` and `backend/tests/test_exports.py`; enforce version/provenance/count/unit fields. <!-- R14 --> <!-- rework: M1 preserve reviewed component status and reason provenance in public schema -->
- [x] T032 Implement S1–S5 exposure, branching eligibility, room profiles/attribute correlation and per-person characteristics in `backend/src/pa/analysis/study.py` with products under `artifacts/results/analysis/`. <!-- R14 -->
- [x] T033 Implement R1–R5 variance, ranking, self-report positions/densities, agreement and rating-style products in `backend/src/pa/analysis/ratings.py`; keep independent-unit uncertainty and E2/E3 boundaries explicit. <!-- R14 -->
- [x] T034 Implement R6–R9 lighting/paired contrasts, function, separate E1 comfort/form and person-characteristic/sleep products in `backend/src/pa/analysis/rooms.py`, covering unsupported small cohorts explicitly. <!-- R14 -->
- [x] T035 Implement B1–B8 QC, EEG spectra/balance, valid HR/HRV, candidate relationships, FAA, disagreement and physiology/self-report/fusion density products in `backend/src/pa/analysis/body.py`. <!-- R14 -->
- [x] T036 Implement P1–P5 transfer, null comparisons, unseen-room curves, importance and training-diagram products plus fused model evaluation in `backend/src/pa/analysis/prediction.py`; expose only CP-C-reviewed new model findings for publication. <!-- R14 -->
- [x] T037 Integrate catalogue and Methods products into `backend/src/pa/results/build.py`, `backend/src/pa/results/export.py` and frontend staging; complete `docs/research/analysis-catalogue.md` mappings and real-export/schema tests in `frontend/tests/real-exports.spec.ts`. <!-- R14 --> <!-- rework: M3 complete approved Methods evidence export -->
- [x] T038 Update `frontend/src/App.tsx`, `frontend/src/ui.tsx`, `frontend/src/lib/repository.ts` and `fab/project/{constitution,context,code-review}.md` for eight routes, horizontal navigation, filter-preserving redirects, accessible loading/error boundaries and real 404. <!-- R15 -->
- [x] T039 Pin/validate chart dependencies in `frontend/package.json` and its lockfile; implement shared accessible plot/glossary components in `frontend/src/figures/ResearchChart.tsx` and `frontend/src/ui.tsx`, with theme tokens and readable formatting. <!-- R17 -->
- [x] T040 Draft concrete landing/researcher copy in `docs/research/landing-copy.md`; derive the authorized portrait into `frontend/public/images/researcher.webp`, preserve source provenance, and prepare `docs/reports/revision-2026-10/CP-E1.md` with exact copy and pending review. <!-- R16 -->
- [x] T041 Record delegated evidence-based CP-E1 agent disposition and approved copy/version in `docs/reports/revision-2026-10/CP-E1.md`; implement `frontend/src/pages/Landing.tsx` with concept-led content and no findings cards/plot or private-document links. <!-- R16 -->
- [x] T042 Implement The Study and Rooms & Experience in `frontend/src/pages/Study.tsx` and `frontend/src/pages/Rooms.tsx`, mapping S/R products, room gallery/profiles and responsive sticky/detail sheet behavior to filtered explorer links. <!-- R17 -->
- [x] T043 Implement Body & Experience and Prediction & Findings in `frontend/src/pages/Body.tsx` and `frontend/src/pages/Prediction.tsx`, showing the full component/fusion catalogue, nulls and CP-C-reviewed limits without repeated caveat walls. <!-- R17 -->
- [x] T044 Implement Data Explorer and Methods & Research Context in `frontend/src/pages/Explore.tsx` and `frontend/src/pages/Methods.tsx`, including URL filters, lazy signal progress, codes, protocol/spec provenance and implemented thesis demonstrations. <!-- R15 -->
- [x] T045 Implement forward fused prediction in `frontend/src/pages/Studio.tsx`, `frontend/src/api/client.ts` and `frontend/src/figures/Massing.tsx` with target selection, presets, 0–100 score conversion, schematic geometry and studied comparisons. <!-- R18 -->
- [x] T046 Add closest-score generation to the same `frontend/src/pages/Studio.tsx`, preserving entered locked attributes/ranges and target, showing requested/achieved/difference and candidate provenance; provide pre-submit offline/readiness and no-solution states. <!-- R18 -->
- [x] T047 Complete signed affect keyboard interactions, theme contrast, legends and data alternatives in `frontend/src/figures/Circumplex.tsx`; implement route-split optional panorama behavior in `frontend/src/figures/Panorama.tsx` with reduced-motion handling and nonimmersive fallback. <!-- R17 -->
- [x] T048 Extend `frontend/tests/simulator.spec.ts` and `frontend/tests/live-api.spec.ts` for forward/generation payloads, exact scale boundaries, lock preservation, closest-score ordering, wheel behavior, no-solution and offline-before-submit behavior. <!-- R18 -->
- [x] T049 Extend `frontend/tests/site.spec.ts`, `frontend/tests/chart-encoding.spec.ts` and `frontend/tests/theme.spec.ts` for all eight routes, redirects, 404, keyboard charts, filters, anchors/buttons and both viewport/theme combinations; retain relevant existing test coverage. <!-- R19 -->

### Phase 4: Polish — evidence, delegated visual review and release

- [x] T050 Run `make verify-data`, `make pipeline`, `make lint test site` against approved methods and perform isolated reproduction through `scripts/reproduce_isolated.py`; record actual commands/results, source/artifact comparisons and scientific version changes in `docs/reports/revision-2026-10/validation.md`. <!-- R20 --> <!-- rework: Verify rework delta against completed clean scientific reproduction and rerun affected checks -->
- [x] T051 Capture every route at 1440×900 and 390×844 in both themes using `frontend/tests/site-capture.spec.ts`; store current captures under `docs/screenshots/` and record per-route Lighthouse accessibility results and fixed issues in `docs/reports/revision-2026-10/CP-E2.md`. <!-- R19 --> <!-- rework: Refresh visual evidence for changed Explorer and Methods content -->
- [x] T052 Record evidence-based delegated CP-E2 agent desktop/mobile review of the concrete site/captures in `docs/reports/revision-2026-10/CP-E2.md`; resolve observed corrections before release. <!-- R19 --> <!-- rework: Review corrected presentation under delegated CP-E2 authorization -->
- [x] T053 Update `README.md`, `CHANGELOG.md`, `docs/data_card.md`, `docs/model_card.md`, `docs/operations.md` and `docs/release-readiness.md` to final approved evidence, checkpoint outcomes, participant-code policy, limitations and reproduction commands; identify the affected memory domains and actual implementation evidence for the later hydrate handoff in `docs/release-readiness.md`. <!-- R20 --> <!-- rework: S1/S2 correct historical snapshot and checkpoint wording; record final rework validation -->
- [x] T054 Validate current hosting free-tier limits and deployment needs; update `render.yaml`, `frontend/vercel.json` and `docs/release-readiness.md` with a concrete free-hosting choice, static/API readiness checks and outstanding external decisions without purchasing a domain. <!-- R20 -->

## Execution Order

1. **Currently authorized preparation:** T001 → T002/T003 → T004 → T005 → T006; T007 follows verified inventory and current contracts. T008 uses measured post-cleanup storage. T009–T011 consume source understanding and must remain drafts. T012 verifies this slice. Complete safe items even if a different cleanup candidate lacks original verification; retain and report the unverified item.
2. **CP-A storage barrier:** T008 is proposal completion, not approval. T013 requires an explicit owner choice. This barrier blocks new storage migration only; it does not block authorized verified cleanup, CP-Spec preparation, or science after its separate approval. No history rewrite task exists.
3. **CP-Spec execution barrier:** T014 requires explicit owner approval of T011's concrete methods/hash. Before that, stop at T012 and report pending owner decisions; do not modify current executable scientific settings or perform T015 onward. Unchanged approved-method regression remains permissible and must not be represented as v1.2 results. There is no timeout/default/autonomous-mode bypass.
4. After CP-Spec: T015–T018 generate the inspectable approved QC products. **CP-B barrier:** T019 records evidence-based delegated decisions before T020–T025 use reviewed physiology eligibility. The 2026-10-10 user instructions quoted above authorize agent disposition of CP-B; no speculative F/H exclusion or personal-owner signature fabrication is allowed.
5. T020 → T021; T022–T024 implement/evaluate the prespecified research and fused models. T025 prepares actual results. **CP-C publication barrier:** T026 records a concrete evidence-based delegated CP-C decision before staging/publishing new model findings through T036/T037/T043. Engine work T027–T030 may proceed after its scientific prerequisites without claiming publication approval. T029 depends on T027/T028 and compatible model inference.
6. T031 supplies schemas; T032–T036 supply the complete catalogue; T037 verifies/stages it. T038–T049 integrate the approved products. **CP-E1 barrier:** T040 prepares concrete copy; T041 records an evidence-based delegated copy decision. T045/T046 depend on T027–T030; T048 checks both flows.
7. T050 validates final artifacts; T051 supplies concrete screenshots/accessibility evidence. **CP-E2 release barrier:** T052 records an evidence-based delegated desktop/mobile review before release. T053–T054 may prepare documentation and hosting while that decision is pending; no final release is inferred from a passing build.
8. **Post-apply sequencing, not Apply Tasks:** completing T001–T054 permits the parent to enter formal review; T001–T012 alone does not. A fresh independent reviewer checks the changed files and acceptance, records findings in `docs/reports/revision-2026-10/independent-review.md`, and follows the bounded rework/escalation rules in `fab/project/code-review.md`. Only after review passes and acceptance is satisfied does hydrate update actual behavior in `docs/memory/architecture/{platform,website}.md`, `docs/memory/research/{analysis,protocol}.md`, `docs/memory/operations/reproducibility.md` and indexes/logs. Ship follows hydrate and applicable release conditions, checks ancestry/allowed staging, and records actual PR/deployment status in `docs/release-readiness.md`. Small workstream commits/PR slices are coordinated by the parent; creating a slice does not complete this whole change. Formal review, hydrate and ship are never prerequisites for checking an implementation task complete.
9. Model routing: planning `gpt-6-astra`/`high`, implementation/debugging `gpt-6-sol`/`high`, fresh independent review `gpt-6-astra`/`xhigh`, hydrate `gpt-6-sol`/`high`, ship `gpt-6-luna`/`medium`. Verify/report dispatch settings; do not silently substitute or attempt to change a running session through instructions.

## Acceptance

Fresh independent full review iteration 2 reassessed all 57 items as met; the final disposition and evidence are recorded in `docs/reports/revision-2026-10/code-review.md`.

### Functional Completeness

- [x] A-001 R1: Maintained research context provides traceable thesis/prototype/formula/diagram references and corrected-protocol distinctions before corresponding source retirement.
- [x] A-002 R2: Every cleanup removal has source/hash/original/knowledge-preservation evidence; unique scientific data, Windows originals, active Fab and unrelated edits remain protected.
- [x] A-003 R3: CP-A contains measured storage, dated official limits and an explicit owner choice before any new migration; no history rewrite or second repository occurs.
- [x] A-004 R4: Canonical source verification, retired-document provenance, meaningful artifact drift detection and model compatibility work without private-PC runtime dependencies.
- [x] A-005 R5: CP-Spec contains a concrete method/decision proposal and explicit approval of the applied version/hash; no dependent v1.2 analysis predates approval.
- [x] A-006 R6: Timebase, QC and candidate exports implement approved settings with explicit uncertainty, stage-specific noise definitions and component provenance.
- [x] A-007 R7: Flagged review entries have matching evidence and delegated CP-B dispositions; ECG validity remains independent and contiguous-run based.
- [x] A-008 R8: Physiology, self-report and fusion are separate declared coordinates; complete/partial eligibility and E1/E2/E3 distinctions account for all source records.
- [x] A-009 R9: Every prespecified validity/disagreement result appears with eligible counts, justified uncertainty or an explicit unavailable reason.
- [x] A-010 R10: All four research questions and the fused studio model have honest prespecified comparisons, grouped isolation and actual model-card evidence.
- [x] A-011 R11: One validated room/feature/fitted-artifact contract serves training, CLI, API and search; CP-C review precedes new model finding publication.
- [x] A-012 R12: Studio predicts fused coordinates only and applies the exact target-distance formula with tested API/UI scales and raw/clipped provenance.
- [x] A-013 R13: Generation minimizes absolute distance from requested score while preserving locks/ranges and returns requested/achieved/difference with supported-search limitations.
- [x] A-014 R14: S1–S5, R1–R9, B1–B8, P1–P5 and Methods each have validated products and route mapping, including unavailable results and fused comparisons. Methods now publishes approved numerical settings, CP-B review provenance, computed sensitivity and versioned references.
- [x] A-015 R15: Eight named routes, horizontal navigation, useful redirects, URL filters, static offline reading and real 404 are implemented; policy wording matches.
- [x] A-016 R16: CP-E1-approved landing is thesis-led with no results cards/featured findings plot; profile/contact/portrait and prototype descriptions match authorized sources.
- [x] A-017 R17: Research charts include units/counts/legends/help/data links and accessible alternatives; both themes, reduced motion and responsive layouts preserve meaning.
- [x] A-018 R18: One Studio page supports both actions, presets/targets/locks/ranges, schematic geometry, studied references and pre-submit unavailable handling.
- [x] A-019 R19: CP-A/CP-Spec have actual owner outcomes; later checkpoints have documented user delegation, evidence-based agent dispositions and no false human-inspection claim. Final browser/viewports/themes and accessibility evidence is recorded, and the changed-file scope and validation outputs are ready for fresh independent review.
- [x] A-020 R20: Implementation commands, cards, README, CHANGELOG, operations and release-readiness documents describe actual approved implementation with honest hosting status and no unauthorized purchases; the post-review memory handoff identifies affected domains without claiming hydrate or ship is already complete.

### Behavioral Correctness

- [x] A-021 R5: An unapproved draft does not alter the reviewed current method or executable science; pending decisions are visibly pending rather than implied by checked preparation tasks.
- [x] A-022 R8: E1 comfort never becomes a valence axis and only eligible E2/E3 self-report records appear on comparable self-report affect planes.
- [x] A-023 R10: Held-out-person-centered results are explicitly relative; no held-out distribution fits learned preprocessing/target calibration in model evaluation.
- [x] A-024 R13: With request 65, feasible score 64.5 ranks ahead of 95; default ranking does not maximize scores or treat the request as a minimum threshold.
- [x] A-025 R18: Entered locked dimensions reach the backend and remain identical in every generated candidate, including after presets and action changes.
- [x] A-026 R14: S2 shows independent branching eligibility and sample denominators distinguish trials, people and rooms; the browser does not compute research statistics.

### Removal Verification

- [x] A-027 R2: Verified obsolete personal/planning copies are absent from current project/public asset contents and ignored where appropriate; no blanket public archive relocation substitutes for removal.
- [x] A-028 R16: Thesis/CV/portfolio download links, invented biography, findings-led landing elements and descriptions of implemented prototypes as unbuilt future work are absent.
- [x] A-029 R15: Superseded seven-page navigation and stale route targets are removed or deliberately redirected without breaking useful deep links.

### Scenario Coverage

- [x] A-030 R6: Synthetic known bands, dead and ×10-gain channels, blinks, noise, flats, counter gaps and short recordings exercise approved reason/coverage paths.
- [x] A-031 R7: Signed and unsigned manual-review cases and ECG gap/ambiguous/short cases demonstrate no unreviewed eligibility promotion or plausible replacement measure.
- [x] A-032 R10: Group-membership and held-out-mutation tests demonstrate outer/inner fold isolation, training-only transformations and honest insufficient-group behavior.
- [x] A-033 R11: Direct, CLI, API and search prediction parity tests pass with the same fitted artifact; incompatible or altered artifact bytes fail readiness safely.
- [x] A-034 R12: Equal points, opposite corners, axis boundaries and out-of-square raw predictions verify exact score scale and approved clipping semantics.
- [x] A-035 R13: Tests exercise locks/ranges/type/lighting consistency, requested-score extremes, deterministic ties, duplicates, fixed seeds and impossible constraints.
- [x] A-036 R19: Playwright covers all eight routes at 1440×900 and 390×844 in both themes, keyboard controls, numeric wheel behavior, real 404 and action/loading/error states.
- [x] A-037 R17: Every route meets the Lighthouse accessibility target of at least 95 with stored actual measurements; visual artifacts support delegated CP-E2 review.

### Edge Cases & Error Handling

- [x] A-038 R2: Missing originals or hash mismatches retain affected candidates with reasons and cannot silently destroy evidence or block unrelated safe preparation.
- [x] A-039 R8: Missing/constant/uncalibratable modalities stay unavailable; complete and partial rows remain separable and usable components survive other-modality rejection.
- [x] A-040 R9: Tiny groups, undefined correlation, singular models and unsupported uncertainty yield explicit unavailable states without adjusting methods after seeing outcomes.
- [x] A-041 R18: Offline/missing/incompatible API states are visible before submit, produce no fabricated predictions, and leave static research/comparisons available where supported.
- [x] A-042 R14: Malformed/stale/missing export products produce readable errors and fail validation rather than rendering plausible numerical defaults.

### Code Quality

- [x] A-043 Pattern consistency: New code follows surrounding naming, package, schema and error-handling patterns.
- [x] A-044 No unnecessary duplication: Existing shared utilities are reused wherever applicable.
- [x] A-045 Readability: Scientific and UI code uses clear, maintainable functions and formatted components over clever compression. Reviewed page forms and tables are formatted as readable JSX with focused tests.
- [x] A-046 Existing patterns: Deviations from established repository patterns have a concrete documented reason.
- [x] A-047 Composition: New behavior is composed through existing modules/components rather than unnecessary inheritance.
- [x] A-048 Evidence distinction: Source values, derived features, constructed coordinates and predictions remain identifiable in types, products and prose.
- [x] A-049 Fold-contained transforms: Learned preprocessing and target transforms fit only on training members and travel with serialized model provenance.
- [x] A-050 Explicit failure: Unavailable measurements and unsupported claims carry status/reason codes through API, exports and UI. Public trial exports and Explorer retain reviewed rejection/uncertainty reasons and independent HR/RMSSD status.
- [x] A-051 Function scope: Functions longer than 50 lines have a clear reason or are decomposed into meaningful units.
- [x] A-052 Utility reuse: The change introduces no duplicate manifest, chart-formatting, room-feature or inference utilities where existing ones suffice.
- [x] A-053 Named settings: Scientific thresholds, API versions, seeds and units use named constants/settings with decision provenance rather than unexplained magic values.
- [x] A-054 No invented numbers: Placeholder research claims, nominal physiological replacements and fabricated prediction-confidence values are absent.
- [x] A-055 Contract reuse: Room features, Neuro-Score and API requests have one shared canonical definition rather than parallel schemas.

### Security

- [x] A-056 R20: Public exports and profile assets obey authorized scope, use participant display codes and do not publish named-recording associations, PC personal documents or secrets.
- [x] A-057 R11: Invalid API constraints and untrusted/incompatible model artifacts cannot bypass validation or trigger request-time training.

## Notes

The Tasks section contains only implementation/preparation work. Formal review assesses acceptance after those tasks complete; hydrate and ship are later sequencer obligations under Execution Order and MUST NOT be prerequisites for apply completion or review acceptance.

Check a task only when that specific deliverable is complete and verified. CP-A/CP-Spec required direct owner decisions, already recorded; CP-B/CP-C/CP-E require concrete evidence-based agent disposition under the user's standing delegation. Unavailable scientific results can satisfy a result-reporting requirement only when the approved analysis was actually attempted or its unsupported prerequisite was demonstrated; pending checkpoint work cannot be relabeled unavailable to complete the plan. Whole-change acceptance remains unchecked until reviewed. Maintain actual command output and deviations in the relevant workstream evidence rather than recreating obsolete process documents.

## Deletion Candidates

- `backend/src/pa/signals/qc.py:55` — Reconfirmed in review iteration 2: existing `epoch_reasons` wrapper has no remaining caller after independent channel QC moved callers to `channel_epoch_reasons`.
- `backend/src/pa/results/review.py:140` — Reconfirmed in review iteration 2: existing `write_review_panels` and its exclusive `_selections`/`_panel` helpers have no remaining caller after the CLI adopted the complete `write_qc_review` path; confirm no supported external entry point before removal.

## Assumptions

| # | Grade | Decision | Rationale | Scores |
|---|-------|----------|-----------|--------|
| 1 | Certain | Keep draft methods separate from reviewed runtime methods until explicit CP-Spec approval. | Intake expressly requires a pre-analysis checkpoint and constitution requires versioned scientific authority. | S:100 R:95 A:95 D:100 |
| 2 | Certain | CP-A blocks storage migration only; verified current-tree cleanup and draft-method preparation may proceed. | Intake explicitly authorizes cleanup without a second approval and rejects history rewrite. | S:100 R:95 A:95 D:100 |
| 3 | Certain | Use the eight proposed paths with preserved old-route redirects. | Page purposes are settled; routes are a reversible implementation proposal using the existing router. | S:90 R:95 A:90 D:90 |
| 4 | Confident | Keep API normalized score compatibility and convert explicitly at the Studio 0–100 boundary. | Intake permits preserving or explicitly versioning existing API semantics; compatibility minimizes disruption. | S:75 R:80 A:80 D:75 |
| 5 | Confident | Use Observable Plot/d3-contour after dependency validation and backend-precomputed statistical data. | The guide proposes this stack and intake accepts reversible charting decisions; accessibility still needs implementation verification. | S:80 R:80 A:75 D:75 |
| 6 | Certain | Store concise checkpoint evidence under docs/reports/revision-2026-10 rather than moving personal plans into a public archive. | Intake rejects blanket archive migration while requiring retained current scientific/checkpoint evidence. | S:95 R:95 A:90 D:90 |
| 7 | Certain | Every downstream scientific task remains contingent on concrete approved methods; no numerical scientific choice is adopted by this plan. | The user's designated CP-Spec process is a deliverable and execution barrier, not an unanswered product requirement to guess. | S:100 R:95 A:95 D:100 |

7 assumptions (5 certain, 2 confident, 0 tentative).
