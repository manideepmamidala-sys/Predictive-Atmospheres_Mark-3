# Intake: Predictive Atmospheres Research Platform Rebuild

**Change**: 261008-ymhz-research-platform-rebuild
**Created**: 2026-10-08

## Origin

> User invoked `/fab-new` after an extensive `/fab-discuss EXECUTION_PLAN.md` discussion, a repository-wide read-only investigation, and explicit confirmation that the work includes a new backend, frontend, repository structure, cleanup and architecture.

The user's instructions define a complete research-platform rebuild. Run it through a fresh Fab workflow, delete old Fab changes, retain the tooling, and preserve the current AGENTS.md Codex model-routing policy. Completely redesign the website with light/dark switching, appropriate skills and dependencies, and all seven proposed pages. Unlock existing analytical methods and justify replacements scientifically. Keep multimodal fusion as the central hypothesis for **description of experience**. Neuro-Score targets are user-selected. Prediction and optimization remain labelled experimental demonstrators even if performance is weak. Retain free-tier hosting.

`EXECUTION_PLAN.md` is the initial roadmap, not an immutable specification. Its locked decisions and phase prompts predate the owner's corrections below. The first implementation deliverable is a reconciled roadmap and project governance; do not execute the old plan verbatim. This intake transfers the conversation to workers without requiring access to chat history.

## Why

The repository contains 160 raw EEG/ECG trial recordings, three experiments, ten distinct participants and thirty rooms, plus a Streamlit application and partially decoupled FastAPI backend. Documentation incorrectly describes an existing React/Vite implementation. Current processing, serving and presentation use inconsistent features and scientific definitions, so published-looking numbers cannot be treated as validated research results.

Specific observed problems include hardcoded 256 Hz processing despite sample-count/duration evidence near 500 Hz; neutral/baseline substitutes for failed physiological calculations; missing spatial data replaced by zero; several different Neuro-Score formulas; a saved sklearn artifact missing an outer scaler used during training; independently sampled derived and categorical optimizer inputs; and frontend calls inconsistent with API routes. Existing audits and thesis prose also disagree with current code and the owner's acquisition account.

A reproducible rebuild should preserve the source evidence and useful exploration while separating verified observations, owner-reported protocol, analytical assumptions and model predictions. The primary research question is how physiological signals and self-reported ratings jointly describe experience of rendered architectural spaces. Fusion is a hypothesis to evaluate, not automatically validated emotional ground truth. Architectural prediction is a secondary experimental product.

## What Changes

### 1. Fresh Fab workflow and reconciled roadmap

- Revise EXECUTION_PLAN.md to incorporate this intake, explicit dependencies, review checkpoints and meaningful acceptance checks. Retain phases 0–9 as roadmap milestones, with a justified analysis specification following the data audit and preceding scientific implementation/model comparisons.
- Use Fab intake/plan/apply/review/hydrate/ship tracking instead of the old manual copy-paste phase workflow. This change captures the complete objective; planning may split independently reviewable implementation units into fresh changes with explicit dependencies. Never interpret this intake as permission to skip phase evidence or run every phase without its stated prerequisites.
- Delete historical change records from the working branch, including archived records if present, and clear obsolete pointers/dispatch records. Preserve this new change and any newly created rebuild changes. Historical candidates observed: 260915-a2td-website-delivery, 260915-bc1i-update-repo-docs-fix, 260915-vwf1-migrate-react-frontend, 261008-rvq3-decouple-streamlit-fastapi. Do not rewrite Git history or delete branches/worktrees indiscriminately.
- Retain `.agents/` and `fab/`; update `fab/project/config.yaml`, constitution, context, quality/review guidance and documentation indexes to the actual target architecture. Replace stale dark-only/Tailwind-only and mandatory-ground-truth wording. Preserve useful separation and feature-integrity requirements.
- Keep the exact AGENTS.md routing: operator gpt-6-astra/max; intake/planning/architecture gpt-6-astra/high; implementation/debugging gpt-6-sol/high; independent review gpt-6-astra/xhigh; documentation/hydrate gpt-6-sol/high; ship gpt-6-luna/medium; PR feedback gpt-6-sol/high. Explicitly configure and report dispatch; use fresh review workers. Report unavailable routes rather than substitute.
- Use the Fab-created branch for this intake. Reconcile the roadmap's `rebuild/v1` integration-branch proposal with Fab branches before multi-change implementation. Preserve a legacy snapshot without force-moving an existing tag. Do not silently rename main or overwrite existing user work.

### 2. New repository and component architecture

```text
backend/
  pyproject.toml
  uv.lock
  src/pa/
    config.py
    decisions.yaml
    io/
    signals/
    affect/
    features/
    modeling/
    scoring/
    optimize/
    results/
    api/
    cli.py
  tests/
frontend/
  src/{api,content,design,figures,pages,lib}/
  public/rooms/
  tests/
data/{metadata,raw,renders,processed}/
artifacts/{model,results}/
docs/{protocol,reports,history,thesis}/
docs/memory/
docs/specs/
fab/
.agents/
.github/workflows/
```

Python research processing is headless. The React/Vite/TypeScript frontend consumes schema-validated static research exports; only prediction and optimization require the live versioned FastAPI service. One room schema and feature builder serve training, API and optimizer. Preserve model preprocessing with the fitted artifact. No frontend physiological processing or opportunistic model fitting during rendering.

Use uv and a locked Python environment, pnpm and a compatible locked frontend environment. The original Python 3.11 and Node 22 proposals are compatibility starting points, not excuses to install incompatible current dependencies. Verify supported versions during setup. Retire torch/Streamlit from the replacement runtime; select scientific libraries according to documented methods rather than package availability alone.

Inventory and checksum recordings, metadata, room renders and thesis assets before moves/deletions. Keep original sources intact; generated caches and reports are distinguishable and reproducible. Remove obsolete source trees, root API/pipeline entry points, duplicate configs/preprocessing, stale packaging outputs, logs and caches only after replacement responsibilities are accounted for. Historical documentation may mention retired packages: removal checks target active dependencies/imports, not arbitrary prose.

### 3. Owner-reported acquisition protocol

These facts were supplied directly during discussion and supersede contradictory thesis text. Label the provenance accurately rather than claiming independent verification:

- Location: Barcelona, not India.
- Hardware/software: Upside Down Labs NPG Lite recorded through Chords; same hardware/channel arrangement across experiments. Sampling-rate setting is not remembered. Firmware, app version and acquisition signal units remain unverified.
- Channel 1: right forehead, approximately corresponding to Fp2. Channel 2: left forehead, approximately corresponding to Fp1. Placement was approximate, not measured using a verified 10–20 placement procedure. Describe bilateral forehead EEG; do not assert exact cortical localization or use F3/F4.
- Ear attachment: owner described behind the ear at the earlobe. Exact reference-versus-ground wiring and side were not separately established; do not invent them.
- Channel 3: wrist ECG throughout, following the earlier channel description and confirmation of consistent setup.
- Meta Quest 3 gallery displayed non-interactive 360-degree room renders. Participants stood and turned to view the rooms and remained silent.
- Recording began when participants opened their eyes in the headset, and stopped before headset removal. Afterwards participants sat, closed their eyes and supplied ratings. Those transitions/ratings were outside the trial recording.
- Exposures were intended to be approximately 60 seconds; the researcher sometimes stopped by personal judgment. Do not describe uniformly fixed durations or infer why a particular trial ended early.
- No rest or neutral-room baseline recordings were collected. Remove requests for baseline files and any promised baseline-subtraction path. Do not describe within-participant standardization as recorded-baseline correction.
- Repeated subject IDs across experiments are the same people. The researcher reports choosing presentation order randomly; document that account without inventing a randomization algorithm or allocation record.
- Other questionnaires listed in thesis prose were background material, not administered measurements. Do not publish fabricated SAM/POMS/etc. response analyses.

### 4. Rating conversion and provenance

Preserve the provided transformed CSV values; ingestion MUST NOT apply these conversions twice. Original ratings/forms/conversion spreadsheet are unavailable. The investigator entered the converted responses. Preserve missing values and construct distinctions.

| Experiment | Original response | Stored interpretation |
|---|---|---|
| 1 | Comfort score s in 0–10 | comfort = s/5 - 1; never relabel as valence |
| 2 | Separate valence and arousal s in 0–10 | each axis = s/5 - 1 |
| 3 | Pleasant/unpleasant selection, then intensity s in 0–10 | pleasant valence = +s/10; unpleasant valence = -s/10 |
| 3 | Calm/excited selection, then intensity s in 0–10 | calm arousal = -s/10; excited arousal = +s/10 |

Zero intensity maps to zero regardless of selected direction; the direction cannot be recovered from zero alone. Do not reconstruct original verbal responses or assert precise questionnaire wording not supplied. Experiments 2 and 3 share signed ranges but used different elicitation procedures; assess pooling explicitly rather than treating range similarity as proof of measurement equivalence.

### 5. Verified data inventory and actual audit targets

Read-only repository inspection found:

| Experiment | Trials/raw files | Participants | Rooms | Logged duration |
|---|---:|---:|---:|---|
| 1 | 50 | 5 | 10 | 60 seconds |
| 2 | 50 | 5 | 10 | 25–60 seconds |
| 3 | 60 | 6 | 10 | 51–60 seconds |

Overall: ten distinct participants, thirty distinct rooms, all 160 referenced recordings present and no duplicate subject-room pairs. Raw headers are Counter, Channel1, Channel2, Channel3; inspection found finite numeric values, not proof of physiological quality. Four empty biometric rows and fourteen empty spatial rows explain the plan's supposed Experiment 3 anomalies. Filter empty records explicitly; remove the unsupported retake/lost-trial questions.

Median sample-count/logged-duration ratios are approximately 500, 500 and 499.52 Hz. These are inferences, not confirmed hardware configuration. Several Experiment 3 files disagree substantially with logged duration; the shortest has 7,961 samples. Thirty-eight Experiment 1 files contain one non-unit modulo-256 counter transition, including 37 interior transitions. Counter behavior is acquisition evidence, not a standalone timestamp or guaranteed packet-loss count.

Audit candidate rates using device/export evidence, sample counts and durations, spectral evidence where informative, and physiological plausibility without selecting a rate to improve desired results. Preserve unresolved-rate status if the evidence is insufficient. Store file-level duration discrepancies and quality flags. Use actual available recordings, not padded fixed-length trials; choose onset exclusions and minimum valid duration through the justified method specification.

Filename timestamps joined to metadata reconstruct observed order: Experiment 1 has three ascending and two descending room sequences; Experiment 2 has five distinct sequences; Experiment 3 has three ascending and three descending sequences. Export trial_order per participant/experiment, preserve source filenames, and distinguish file chronology from verified event timestamps.

Experiment 1 spatial metadata contains dimensions only; Experiment 2 adds openings/lighting; Experiment 3 adds walkable area/space type. Sleep is recorded only in Experiment 3. Preserve these structural missingness patterns instead of converting missing observations to zero or presenting imputed sleep as measured.

### 6. Spatial provenance and render preservation

The owner used Lumion renders and Grasshopper with Ladybug/Honeybee for supplied spatial/environmental values. The renders were sample images and calculations/extraction conditions were not matched to the visual stimuli. Retain the supplied values as requested, document uncertain extraction/simulation provenance, and avoid claims that illuminance/CCT values are calibrated retinal/headset exposures or controlled experimental manipulations. Do not invent sky, date/time, simulation settings or source files.

All thirty renders are present, currently untracked, in root `rooms/`:

- `Mark 01_ 360 Renders/`: Rm_001–010 PNG, 4096×2048.
- `Mark 02_ 360 Renders/`: Rm_011–020 JPG, 4096×4096.
- `Mark 03_ 360 Renders/`: Rm_021–030 JPG, 4096×4096.

Filename stems match all populated Room_IDs, so generate the manifest without requesting manual pairing. Representative later images contain stacked panoramas, apparently stereo over/under; inspect export layout before selecting an eye or generating perspective previews. Preserve originals and distinguish panorama display from schematic massing. Preserve 116 existing frontend image assets and the two root thesis PDFs before replacing frontend/. Older figures are historical evidence, not validated new results.

### 7. Evidence-led scientific specification

Unlock the old EEG/ECG filters, rejection thresholds, durations, component mappings, fusion weights, scoring and statistical recipes. Before implementing analytical choices, research primary methods/library documentation and write a versioned specification recording rationale, assumptions, applicability to these recordings, sensitivity analyses and failure handling. After relevant analysis begins, changes are documented amendments, not silent tuning. This is a reanalysis of existing data; do not imply prospective preregistration before original data collection.

- Preserve physiological features in documented units and retain validity/reason codes per modality and trial. No missing/failed feature becomes a neutral value, nominal heart rate, synthetic trial or unflagged target.
- Implement and test filtering, peak detection, artifact/QC handling and feature extraction appropriate to approximate forehead EEG and wrist ECG. No fixed 20-second or 30-beat criterion is locked solely because the old plan named it.
- Keep fusion central as a hypothesis for describing experience. Report physiological-only, self-report-only and fused descriptions and disagreement. State assumptions behind mappings to common coordinates; their numeric ranges do not validate emotional interpretation.
- Evaluate alpha sensitivity; the old alpha=0.6 and sensitivity set {0, 0.25, 0.5, 0.6, 0.75, 1} are candidate starting choices to justify, not conclusions. Distinguish objective-only/subjective-only/partial-modality records; do not mix them silently into one apparently homogeneous target.
- Justify pooling versus experiment-specific analyses, repeated-measure handling, participant/room effects, uncertainty estimates and any agreement analysis. No causal claims from the current observational associations and unmatched environmental values.
- Define learned normalization and target construction with respect to evaluation splits. Never use held-out outcome distributions as if available for an uncalibrated new participant. Separate descriptive within-person standardization from deployment evaluation assumptions.
- Determine bootstrap resampling units, null/permutation structure, model-selection procedure and interval calibration from the experimental dependence structure. The original plan's p<0.05 and 80% interval recipes are not automatically valid specifications.

### 8. Unified room schema, model artifact and experimental optimization

Use a validated RoomInput with independent geometry, opening counts/total areas, supplied lighting variables, walkable area, day/night and space type (including general/unknown where justified). Derive length-width ratio, floor/wall area, volume and opening/walkable ratios in one backend builder. Never accept independent contradictory volume or multiply already-total opening area by opening count. Spreadsheet ratio comparisons support total-area semantics within rounding tolerance.

Preserve documented missing inputs where valid, reject infinity and invalid geometry, and require complete model-ready values only after the declared preprocessing. Define physical checks and studied support separately. Model selection starts with simple baselines and suitable sklearn models; serialize the entire preprocessing/model pipeline with ordered feature schema, versions, data hash, code revision, metrics and limitations.

Evaluate generalization by held-out rooms/participants as justified, not random rows alone. Report baselines and actual uncertainty/calibration evidence. Ensure serialized reload predictions match training-time pipeline predictions, and direct/CLI/API predictions share features and outputs. Replace the current doubly multiplied heuristic confidence percentage with properly labelled evidence; no automatic 100% confidence fallback.

Neuro-Score measures closeness to a USER-SELECTED valence/arousal target. Remove fixed supposedly ideal room-type coordinates and all historical stretch constants. Document distance, scaling and bounds; validate target inputs and test monotonicity and score=1 at target. Space type can constrain the room search but does not dictate the user's emotional preference.

Optimizer samples only independent variables and valid categorical combinations, derives features through the shared builder, applies physical and data-support checks, and returns reproducible distinct candidates. Default results should remain within supported search bounds; any extrapolation is explicit and not silently described as studied. Preserve a labelled experimental simulator/optimizer even if no predictive model beats baseline. Show performance status and limitations consistently; do not promise useful designs or manufacture calibrated intervals when unsupported. A failed or invalid model may make prediction unavailable rather than return fabricated values.

### 9. API, exports and redesigned website

Build schema-versioned research exports under artifacts/results/ and versioned `/v1/health`, `/v1/meta`, `/v1/predict`, `/v1/optimize` API contracts. Include user-selected target coordinates in score/optimization contracts. Metadata exposes artifact/schema/data versions and model status. Startup/readiness validates actual artifact compatibility. Errors are structured; CORS is configured; CPU operations use appropriate execution; OpenAPI generates frontend types/client and drift checks.

Retain the seven pages: The study, Rooms, Signals, Affect, People, Room simulator, Model report. The old System Architecture page is dropped; Model Training becomes read-only reporting. Inventory legacy interactions and explicitly map retained/replaced functionality. Raw/cleaned traces, QC, fusion sensitivity and uncertainty are new validated data products, not decorative republishing of old figures.

The complete redesign must provide Light/Dark/System selection, persistent preference, responsive desktop/mobile layouts, keyboard accessibility, reduced motion, and readable chart/equation/3D treatments in both themes. Section 9's light-as-data concept, Source Serif 4/Public Sans and reading-column/figure layout are a starting design proposal, not a constraint to preserve old visuals. Scientific figures need captions, sample counts, units, method/source context and uncertainty where applicable. Missing CCT or self-report requires explicit visual states; do not invent starting positions for trials without self-report in circumplex animation.

All numerical research claims flow from generated results; methodological constants and UI labels should not be mistaken for hardcoded result claims by lint rules. Provide traceable static exports so research pages work without the live API. Include panorama room exploration, room comparison, accessible circumplex/table alternatives, signal QC, experiment/participant filters, model reports and a clearly experimental simulator. Prefer a design-system/styleguide checkpoint and a final screenshot review. Test both themes and mobile/desktop layouts.

Inspect and install relevant maintained skills and compatible dependencies at their implementation stage. Available curated candidates observed include playwright, playwright-interactive, screenshot, pdf, jupyter-notebook, render-deploy and vercel-deploy; use Figma-specific skills only if that workflow is chosen. Skills improve execution, not scientific validity. Do not install irrelevant bundles or require paid services.

### 10. Reproducibility, release and completion evidence

Create reproducible setup/data verification/pipeline/test/site/all entry points, backend and frontend lockfiles, CI, schemas and synthetic/contract/parity tests. Test scientific correctness and actual failure handling, not just shapes/ranges or magic-literal absence. Record real command output, artifacts and review findings per phase. Repeated runs in the pinned environment must reproduce reported results within declared numerical tolerances.

Use methods/data/model cards, append-only decision history with supersession, changelog, manifest and generated metrics. Reconcile stale docs/memory and specs indexes without presenting proposed architecture as already implemented. Reviewer returns findings; coordinator records verdicts rather than giving contradictory no-edit/append instructions.

User explicitly wants a public academic repository and public recordings, metadata, renders and results, and later requested names too. Do not invent documented consent, ethics approval, institutional endorsement or missing participant identities. Supplied subject metadata contains IDs rather than a verified name mapping. Public author credits differ from named biometric records. Permission to associate participant names with physiological recordings was asked but not established; retain IDs in implementation and treat a named release as a separate evidence-dependent release condition. This must not block unrelated planning/rebuild work or cause repeated intake questions.

Retain free-tier hosting; Vercel frontend and Render API remain the roadmap's candidate deployment. Verify service limits at deployment. MIT code / CC BY 4.0 data-assets-docs and Zenodo DOI are inherited proposals, not user-confirmed licensing decisions; review source ownership and existing third-party licences before finalizing. Do not bundle third-party data under a new blanket licence. No production deployment, GitHub visibility change or named-data publication occurs as part of `/fab-new`.

Completion requires a clean-checkout reproduction, consistent derived inputs and saved-model inference, honest descriptive/predictive reports, a functioning accessible dual-theme seven-page site, migrated source evidence, updated docs and independently reviewed implementation. Scientific inability to compute a measure or support a claim is reported as a limitation, not hidden to satisfy a success criterion.

## Affected Memory

- `website_architecture`: (modify/migrate) Existing unindexed root memory describes absent React code; reconcile into `architecture/website` after implementation.
- `architecture/platform`: (new) Repository boundaries, Python research pipeline, versioned artifacts, API and frontend contracts.
- `architecture/website`: (new) Seven-page site, themes, assets and static/live data boundaries.
- `research/protocol`: (new) Owner-reported acquisition, rating conversions, data provenance and unresolved evidence.
- `research/analysis`: (new) Implemented signal/QC, fusion, evaluation and scoring choices with limitations.
- `operations/reproducibility`: (new) Tooling, data manifests, checks, deployment and release process.

## Impact

This is a broad replacement of `src/`, Streamlit `frontend/`, root API/pipeline scripts, runtime dependencies and deployment configuration. It affects `data/`, untracked `rooms/`, model/results artifacts, tests, documentation and Fab governance. It is not a cosmetic theme edit or a patch to existing inference alone.

Existing worktree changes at intake creation: modified fab/.fab-version and fab/.kit-migration-version; untracked AGENTS.md, EXECUTION_PLAN.md, EXECUTION_PLAN.md:Zone.Identifier, PROJECT_REPORT.md and rooms/. Preserve these during branch creation and migration; do not reset/stash/delete them as incidental cleanup.

Read-only investigation parsed seventy Python sources successfully. It did not run the app, train models or establish a passing test suite. Static tests include imports/calls to removed interfaces. The default environment lacked core scientific/PDF packages; isolated cached pypdf tooling extracted the 48-page presentation and 104-page booklet with some PDF parsing warnings. No exhaustive image/privacy audit or processed parquet/artifact provenance verification was completed. The new pipeline must verify rather than inherit historical results.

## Open Questions

No additional owner answers are needed to begin the reconciled roadmap and rebuild planning. The following are explicit work items or release conditions, not silently resolved facts:

- Determine acquisition rate and units, and explain counter/duration discrepancies where evidence permits; otherwise retain uncertainty and bound affected analyses.
- Exact reference/ground wiring, firmware/app versions, original questionnaire wording, simulation conditions and original ratings are not established. Report unavailable details without fabricating reconstruction.
- Select justified signal/QC/fusion/statistical methods after evidence review; design validity checks and specify amendment handling before affected comparisons.
- Verify stacked panorama layout/eye convention and generate a render manifest from existing IDs.
- Named participant-to-recording release permission remains unverified despite owner authorization for a public repo; implement with existing IDs and revisit only before such a release.
- Final licensing and DOI hosting are proposals to settle at release; free-tier cost is the user's confirmed constraint. No deadline was supplied.

## Assumptions

| # | Grade | Decision | Rationale | Scores |
|---|-------|----------|-----------|--------|
| 1 | Certain | This intake covers the complete architecture/backend/frontend/repository rebuild, starting with a reconciled roadmap | Discussed — user explicitly confirmed full scope immediately before invoking fab-new | S:100 R:85 A:90 D:100 |
| 2 | Certain | Keep Fab tooling, remove historical change records during migration, preserve current/new records and Git history | Discussed — user requested fresh Fab and deletion of old changes; precise cleanup is reversible in Git | S:100 R:90 A:95 D:95 |
| 3 | Certain | Preserve current Codex role/model/effort routing and independent review | Explicit AGENTS.md policy supersedes old workflow defaults | S:100 R:95 A:100 D:100 |
| 4 | Certain | Protocol and rating facts above override conflicting thesis prose with owner-reported provenance | Discussed — multiple explicit answers; no assumption of independent verification or exact localization | S:100 R:90 A:85 D:95 |
| 5 | Certain | Fusion stays central for describing experience; targets are constructed hypotheses, not automatic ground truth | Discussed — user chose description of experience and central fusion while unlocking methods | S:100 R:85 A:90 D:95 |
| 6 | Certain | Neuro-Score target is user-selected; weak-model simulator remains labelled experimental | Discussed — explicit selections replace fixed room-type targets and disabling the demonstrator | S:100 R:90 A:95 D:100 |
| 7 | Certain | Retain seven pages, complete dual-theme redesign, source assets and free-tier deployment | Discussed — explicit owner requirements and verified assets | S:100 R:90 A:95 D:100 |
| 8 | Confident | Research methods and numerical defaults are selected through a documented audit/specification stage | Discussed — methods unlocked and agent tasked to justify them; actual outcomes remain unknown | S:95 R:60 A:70 D:85 |
| 9 | Certain | Use the proposed Python package, React/TypeScript and static-export/live-API boundaries, validating dependency versions | Architecture was discussed and accepted; exact implementation choices remain reversible | S:90 R:70 A:90 D:85 |
| 10 | Certain | Continue implementation with subject IDs; named-recording publication awaits separate evidence | Asked — public release authorized, named participant permission not established; no names mapping found; defer only that release action | S:75 R:90 A:80 D:70 |
| 11 | Confident | Keep licensing/DOI proposals explicit and verify at release rather than assume user confirmation | User confirmed free tiers only; release can be prepared independently of final licence assignment | S:65 R:85 A:85 D:75 |

11 assumptions (9 certain, 2 confident, 0 tentative, 0 unresolved). Research unknowns remain explicit audit tasks; release conditions do not authorize inventing evidence.
