# Intake: Research Atlas and Fused Neuro-Score Design Studio

**Change**: 261010-tadj-research-atlas-design-studio
**Created**: 2026-10-10

## Origin

The owner invoked `/fab-new` after an extensive `/fab-discuss` review of `MARK3_REVISION_PLAN.md`, both thesis PDFs, the corrected protocol, and the current website. The description is supplied by that conversation: revise the Mark-3 research platform, communicate its thesis clearly, restore the full analysis catalogue and design-studio concept, and clean the current repository.

The owner's latest corrections are authoritative over the execution guide and earlier discussion proposals:

> “I want eeg,ecg to be primary and self report secondary, use fusion in the studio prediction but have a comparative analysis on both and differences.”
> “The fusion is the point on valance arousal graph, which is calculated from subjective(selfreport) and objective(physiology) valance and arousal.”
> “In the studio where user can give spatial data and predict the score, it should only predict fused, score.”
> “Room generation [is] part of design studio ... option to choose target neuroscore (it is not minimum but find the close one).”

This is a new feature/research revision after the completed `261008-ymhz-research-platform-rebuild`, not a reset of that change. Intake captures the whole agreed scope; implementation is divided into reviewable workstreams with checkpoints. The earlier instruction to wait for personal owner signoff was superseded on 2026-10-10 by the user's explicit `$fab-ff with your CP-B decidions` and then `$fab-ff approve all the future checkpoint automatically and continue the work`. These delegate CP-B and subsequent checkpoint dispositions to the agent workflow after concrete evidence review. They do not assert that the owner personally inspected panels, model results, copy or site captures; uncertainty and actual AI reviewer identity must be recorded. The approved CP-Spec source hash remains `51c01ef6ccdf2f4318ac786d1bb39afeb1aa2bcf3bc93039479a4ed2454603ac` and the CP-A storage choice is defer-LFS.

## Why

The current landing page leads with fusion cohorts and processing caveats rather than explaining the architectural question. The owner wants a thesis-jury/researcher audience to understand the concept, hypothesis, experiments and contribution before choosing a research page or Design Studio. Findings belong on the relevant pages, not as headline cards on the landing page.

The execution guide improves scientific reporting but conflicts with the owner's central design intention: it retires fusion and replaces prediction with nearest-room lookup. The accepted revision preserves a physiology-led investigation, compares physiology, self-report and fusion openly, and uses fused predictions for an experimental Neuro-Score studio. Scientific validity remains an evaluated outcome, not an assumed consequence of the chosen product focus.

The current Simulator has prediction and suggestion endpoints, but its suggestion action ignores entered dimensions, presents a weak studio workflow, and lacks the agreed closest-requested-score objective. Extend the shared backend contracts and validation rather than building a disconnected simulator. Preserve provenance, fold isolation and honest unavailable states.

## What Changes

### 1. Source review and precedence

Use `MARK3_REVISION_PLAN.md` workstreams A–E and catalogue as the baseline, except where this intake explicitly supersedes it. Before removing documents, inspect and preserve a detailed, source-referenced understanding of the thesis, original studio behaviour, formulas, experiment diagrams, implemented prototypes and relevant assets in maintained research documentation. Do not preserve obsolete execution narratives merely by moving them elsewhere inside the public repository.

Available sources:

- `docs/thesis/PredictiveAtmospheres_ManideepMamidala.pdf` (48-page presentation), `docs/thesis/ManideepMamidala_ThesisBooklet.pdf` (104-page booklet), root duplicate PDFs, `docs/thesis/ManideepMamidala_TextoftheThesis.docx`, and `docs/thesis/ManideepMamidala_ThesisBooklet Folder.zip` (93 entries including INDD/IDML/PDF and linked assets).
- Owner's originals: `D:\IAAC BARCELONA\MAA02\THESIS`, accessible at `/mnt/d/IAAC BARCELONA/MAA02/THESIS`. Confirmed folders include AI content, Abstract & Statement of Interest, Booklet, EXPERIMENT DESIGN, FINDINGS, From IAAC, Illustrations, Machine Learning, NotebookLM, PPA, Presentation, Rhino Integration, State of the Art, Time Field and Video. These originals are read-only inputs, never deletion targets.
- `docs/reports/project-review-2026-10.pdf`, current `docs/protocol/`, `docs/specs/analysis-v1.md`, `DECISIONS.md`, current source and legacy implementation/assets.
- Useful thesis references: presentation pp.2–4 motivation/question, p.12 method, p.14 experiment axonometrics, p.16 apparatus, p.34 pilot scale, pp.39/42/45 prototypes; booklet p.22 affect axes, p.38 experiments, pp.82–89 prototype tools.

Historical thesis claims are not automatic method authority: booklet baseline, breaks, questionnaires and 250 Hz descriptions conflict with the corrected investigator protocol. Preserve source distinctions. Do not reintroduce objective-valence certainty, fused ground truth, random-forest epochs, proven privacy masking or validated causal architectural control. Grasshopper and AI rendering were implemented proofs of concept; represent them as thesis demonstrations, not unbuilt future tools or new live integrations.

### 2. Workstream A: current-repository cleanup

One repository remains. No separate private repository is wanted. Remove obsolete plans, personal document copies and thesis PDF/ZIP/DOCX copies from current tracked/project contents only after source review, checksum inventory and preservation of required derived knowledge/assets. Owner says originals remain on their PC. Verify the relevant originals before removal. Do not rewrite Git history or modify/delete files under the owner's Windows folders.

The guide's blanket `docs/archive/` migration does not meet the user's intent for obsolete personal/planning material. Retain current scientific methods, model/data cards, provenance, research decisions and reproducibility docs; avoid blindly deleting all `docs/reports/`. Active Fab artifacts are necessary workflow records; obsolete standalone plans may be retired only after their agreed requirements are captured. `AGENTS.md` and working Fab machinery remain.

Hash-check duplicated rooms, legacy images and thesis documents before deduplication. Repoint `scripts/build_source_manifest.py`, `data/MANIFEST.sha256` and consumers to retained canonical locations. For removed thesis documents, retain an appropriate provenance/checksum record without making routine builds depend on private PC paths. Never delete unique raw recordings, metadata or scientific evidence as cleanup. Keep derived assets distinguishable from originals, preserve third-party attribution, repair relative links, update CHANGELOG and prevent accidental re-addition of removed documents.

Evaluate remaining large-file storage/LFS only after inventory and current free-tier checks; present the concrete choice at CP-A. Fix regenerated-artifact drift checks and isolate volatile git-revision metadata from scientific content hashing where appropriate. Preserve meaningful reproducibility guarantees rather than demanding unchanged hashes for intentionally changed scientific products.

### 3. Workstream B: physiology-led analysis and fusion

EEG/ECG are the primary research focus; self-report is the secondary comparison. Keep separate physiology-derived, self-reported and fused valence–arousal coordinates in charts/findings. Fusion combines the subjective and physiology-derived coordinates into a point in the same declared coordinate system. Research emphasis does not automatically prescribe numeric weights.

Inspect original formulas and implementations before proposing mapping, normalization, modality weights, fusion weights and missingness rules. Write a retrospective specification amendment (planned v1.2) and decision provenance BEFORE dependent new analyses. CP-Spec requires owner approval of those concrete methods. Do not infer a preferred weight from better model results. Maintain coordinate meanings, units, transform provenance and complete/partial distinctions. Component-only analyses retain usable observations; missing or rejected modalities never become plausible defaults. “Use all the data” means account for every record and use it in each eligible analysis, not waive validity or invent measurements.

Carry forward the guide's timebase audit, channel imbalance/absolute amplitude/line-noise/EMG checks, raw trace plus spectrum review queue, EEG candidate table, cardiac validity review, validity matrix, and disagreement analyses. Treat guide values as proposals for the spec checkpoint, not settled scientific facts. In particular: counter continuity alone does not confirm sampling rate; derive evidence for the proposed primary 500 Hz rate and report uncertainty/sensitivities. Reconcile first-five-second exclusion with the existing spec. Define exact log engagement expression and line-noise measurement stage unambiguously.

Inspect flagged channels/trials before final Subj_F/Subj_H exclusions; do not precommit blanket exclusions to reproduce expected outcomes. The owner will review/sign CP-B. Keep alpha suppression and engagement individually visible; any arousal composite is exploratory and accompanied by its components. Blink and EMG are ocular/muscle measurements, not interchangeable cortical signals. HR remains the proposed main cardiac comparison and RMSSD descriptive where eligible. Report all prespecified candidate relationships, uncertainty, independent people/rooms and experiment-specific results.

E1 comfort is distinct from valence. Only E2/E3 (20 rooms, 110 original trial ratings) have valence–arousal self-report; all 30 rooms cannot appear as comparable self-report affect points. E2/E3 used different rating procedures; preserve separate-first analysis and explicitly justify any pooling. Pilot totals are 10 unique participant IDs, 30 rooms and 160 recordings, subject to inventory verification; report eligible counts for each analysis.

### 4. Workstream C: model evaluation and experimental prediction

Retain the guide's four questions: room-rating consistency; transfer of known-room relative profiles to held-out people; room-attribute prediction for held-out rooms; physiological agreement with self-report. The guide's F1–F10 and expected percentages/correlations/errors are exploratory claims requiring reproduction, not acceptance targets or guaranteed results. Report nulls and all planned outcomes. Explain that centering with held-out person's observed ratings supports relative-response evaluation, not an absolute prediction for an entirely unobserved person.

Add/retain the fused-target model required by the studio; self-report-only modelling must not replace it. Evaluate it honestly alongside the relevant component/self-report research analyses. Fit preprocessing and learned target transformations within training folds; retain grouped room/person validation, baselines and justified permutation/uncertainty methods. Specify the model family/search, cohort eligibility, cross-experiment handling and learning-curve design before evaluation. No fabricated error radius, confidence probability or promised improvement from more data. Produce model/data cards, comparison exports and CP-C result review before publishing new model findings.

One physical input schema and feature builder serves training, CLI, API and generation. Maintain static research exports and a versioned experimental API; do not fit models at request time. Historical model artefacts may be kept with scientific version provenance where useful; thesis and private planning document removal is not permission to destroy scientific reproducibility.

### 5. Design Studio: fused-only forward prediction and closest-score generation

Both actions belong on the SAME Design Studio page. No physiology/self-report/fusion mode selector is present in the studio. Component comparisons belong on research pages.

Forward flow: enter valid spatial attributes (with studied-room presets), select an emotional target on the valence–arousal plane, predict the fused position, and show Neuro-Score on 0–100 plus a schematic 3D view and comparable studied rooms. Explain valence and arousal in plain language. Score is target proximity, not emotion-detection confidence, health, design quality or success probability.

Preserve the existing target-distance concept: for fused position p and user emotional target t in [-1,1]^2, displayed score is `100 * clip(1 - ||p-t|| / sqrt(8), 0, 1)`. The emotional target t and requested numerical score s are DIFFERENT inputs. Preserve/explicitly version API 0–1 versus UI 0–100 boundaries; avoid accidental scale mismatch. Keep raw/clipped prediction provenance according to the approved specification.

Generation flow: choose a desired score s in [0,100] relative to the same emotional target, lock selected attributes and set allowable ranges for others, then search feasible candidate configurations minimizing `abs(predicted_neuro_score - s)`. It is NOT a minimum-score threshold and NOT unconditional maximization. Example: requested 65 should prefer a candidate at 64.5 over one at 95 if both are feasible. Show requested score, achieved score and difference. Return the closest supported candidates found, not a guarantee of a global optimum or exact match. If none are feasible, explain why without relaxing user locks.

Respect locked dimensions, type and lighting constraints; keep derived dimensions/features coherent and flag empirical support. Do not copy the current optimization UI behaviour that ignores entered room dimensions. Fixed seed/bounded search and meaningful tie handling should be specified. Results include parameter sets, schematic 3D geometry, fused position, Neuro-Score and closest studied-room reference. Studied imagery must not masquerade as a generated render. AI imagery and Grasshopper remain linked/explained historical demonstrations only.

Handle offline/unavailable API state before submission; retain static browsing and nearest-room comparison where possible. Never fabricate predictions to maintain appearance. Correct button actions, routing, loading/error states and unintended number changes from wheel scrolling.

### 6. Workstream D: complete catalogue and chart restoration

Implement the full guide catalogue, adapted to the accepted fusion scope. No omission simply because a result is null or a cohort small; provide explicit unavailable outcomes when unsupported. All statistics and chart data originate in versioned backend exports, schema validated on the frontend, with question, takeaway, sample units/counts, method, caveat and provenance.

- S1 participant × room exposure/validity; S2 analysis eligibility flow (branching cohorts rather than falsely nested attrition); S3 gallery and room profiles; S4 room-attribute correlations; S5 participant characteristics.
- R1 person/room/residual variation; R2 ranked ratings; R3 self-report affect positions/densities; R4 rater agreement; R5 rating styles; R6 lighting relationships and appropriate paired contrasts; R7 function; R8 E1 comfort/form; R9 participant characteristics including sleep.
- B1 QC; B2 EEG spectra/band balance; B3 HR/eligible HRV and trace examples; B4 EEG vs reported arousal; B5 EEG vs HR; B6 FAA vs reported valence; B7 disagreement; B8 physiology/self-report density comparisons. Include fused coordinates/densities and component comparisons in research pages as required by the owner, rather than relegating all fusion to a legacy appendix.
- P1 known-room transfer; P2 null comparisons; P3 unseen-room performance and justified learning curves; P4 model importance beside performance limits; P5 training diagram. Include the fused studio model evaluation.
- Methods: timebase, QC thresholds, sensitivity analyses, specification/decisions, versioned models and limitations.

Restore all legacy chart ideas through valid current analyses: density fields/target vectors, demographic dots replacing unjustified violins, EEG spectra/bands, valid HR/HRV, lighting contrasts, attribute correlation, disagreement maps, model importance and parallel-coordinate room profiles. Do not reuse obsolete numbers or titles implying proof. Map every legacy item and catalogue ID to a current route/export or explicit availability explanation.

### 7. Workstream E: eight-page research website

| Page | Proposed route | Purpose/subtitle |
|---|---|---|
| Predictive Atmospheres | `/` | Thesis concept, motivation, research questions, hypothesis, approach and contribution |
| The Study | `/study` | Experimental framework: Form, Lighting, Function, participants, apparatus and protocol |
| Rooms & Experience | `/rooms` | Spatial metrics and self-report: room gallery, attributes, ratings and findings |
| Body & Experience | `/body` | Human metrics and fusion: EEG, ECG, self-report/fusion comparisons and disagreements |
| Prediction & Findings | `/prediction` | Model evaluation: training, baselines, predictive findings and limitations |
| Design Studio | `/studio` | Fused prediction and closest-target-Neuro-Score room generation |
| Data Explorer | `/explore` | Filters, detailed records, traces and tables |
| Methods & Research Context | `/methods` | Methods, provenance, evolving thesis research and implemented PoC demonstrations |

Page names and purpose were agreed; routes are implementation proposals. Redirect useful old deep links and include a real 404. Update the constitution/context/review-policy seven-page wording to reflect the authorized eight-page structure without weakening scientific principles.

The landing is entirely for explaining the concept, idea, research question, hypothesis, experiments, approach and contribution of linked human–spatial metrics. NO proposed three-results cards or featured findings plot on the landing. Visitors freely navigate, with primary calls to explore rooms/findings and Design Studio. Maintain clear academic prose and distinguish original thesis from evolving reanalysis. A balanced architectural/immersive design combines diagrams, room imagery and optional panorama interactions. Preserve ideas while redrawing visuals for the site.

Research pages use question-led titles and descriptive subtitles retaining concepts such as Human metrics and Spatial metrics, so visitors understand the data, analysis and findings underneath. Horizontal navigation; supporting explorer/methods links easy to find. Preserve Light/Dark/System, responsive keyboard-accessible charts, reduced motion and readable contrast. Retain palette and Source Serif/Public Sans unless visual review justifies adjustment. Route-split charting (proposed Observable Plot + d3-contour), axis labels/units/ticks/legends, sample counts, uncertainty where justified, how-to-read help and filtered data links. Avoid repeated caveat walls without hiding relevant limits. Add glossary, responsive room details, optional lazy panorama viewer, error boundaries, signal-load progress, shared UI and readable formatted components. Audit clicks, navigation, anchors, buttons and number-scroll behaviour.

### 8. Researcher identity and public scope

Use Manideep Mamidala, `manideepmamidala2@gmail.com`, `https://www.linkedin.com/in/manideepmamidala`, and the institutional project article `https://blog.iaac.net/predictive-atmospheres/`. LinkedIn could not be retrieved; do not invent biography/credentials from it. Public profile content may be committed; private document copies should not be.

Portrait source: `D:\RUNNING FILES\Portfolio 2.0\IMG_2644.png`, verified accessible at `/mnt/d/RUNNING FILES/Portfolio 2.0/IMG_2644.png`. Produce an appropriately sized derived web asset while preserving the original. Owner authorized photograph reuse. Do not add CV, portfolio or thesis booklet/presentation download links; the latest agreed scope retains the IAAC article only among those document/project links.

Proposed two-sentence RESEARCH STATEMENT (not a biography), subject to landing-copy review:

> Through Predictive Atmospheres, I investigate how architectural space relates to physiological responses and reported experience, developing a linked methodology for human–spatial metrics. My aim is to explore how these metrics can inform design through comparative analysis and proof-of-concept tools that score proposed rooms and suggest spatial configurations toward a chosen experiential target.

Owner authorizes publication of the research data, including trial-level data, raw signals, ratings, demographics and renders, and public use of photographs. Use participant display codes rather than publishing named identities; retain provenance and limitations of those codes. This authorization does not require public personal CV/PDF files. Free deployment is the goal; a modest domain purchase is acceptable but no purchase is authorized now. No deadline. Select hosting after checking actual needs and free limits; do not promise free always-on compute.

### 9. Execution order, checkpoints and validation

Source understanding precedes destructive current-tree cleanup. Then use workstreams A (cleanup), specification, B (signals and validity), C (models/studio engine), D (exports) and E (website). Prepare small reviewable workstream commits/PR slices; this intake is the coordinating change, not permission to combine every workstream into one opaque release. Preserve the guide's preference for workstream branches when implementation is split; do not create extra workstreams/branches during this intake invocation.

Owner explicitly retained these checkpoints:

1. CP-A: present inventory and the concrete storage/LFS choice before making any new storage migration. Current-tree cleanup is already authorized subject to source understanding, checksum/original verification and knowledge preservation above; no second deletion-approval gate is implied. History rewrite is already rejected.
2. CP-Spec: approve methods and decision log BEFORE new dependent analyses. Intake readiness is not method approval.
3. CP-B: owner reviews/signs signal-quality queue.
4. CP-C: review new model results before website publication.
5. CP-E1: review concrete landing copy.
6. CP-E2: final desktop/mobile visual review before release.

Record checkpoint evidence and decisions without publishing obsolete personal/process documents unnecessarily. Do not bypass checkpoints with automatic defaults or autonomous pipeline modes.

Keep `make verify-data`, `make pipeline`, `make lint test site` working for the staged changes. Meaningful tests cover bad/partial signals, fold isolation, fused scoring scale, target-score closeness rather than maximization, locks/ranges/physical consistency, no-solution/offline cases, export schemas, manifests and navigation. Playwright covers every route at 1440×900 and 390×844, both themes, keyboard interactions and number input behaviour. Target Lighthouse accessibility >=95 for each route. Maintain reproducibility, model/data cards, README, CHANGELOG and operations/release documentation.

Use AGENTS.md routing: planning gpt-6-astra/high; implementation gpt-6-sol/high; fresh independent review gpt-6-astra/xhigh; hydrate gpt-6-sol/high; ship gpt-6-luna/medium. Report actual dispatch settings; no silent substitutions. The parent session cannot be changed via instructions.

## Affected Memory

- `architecture/platform`: (modify) exports, fused model contracts, score scale and constrained target-score search.
- `architecture/website`: (modify) eight-page IA, researcher content, fused-only studio and interaction standards.
- `research/analysis`: (modify) approved QC, component/fusion mapping, cohorts, evaluation and complete catalogue.
- `research/protocol`: (modify) source review, evidence distinctions, thesis provenance and additional recovered protocol evidence.
- `operations/reproducibility`: (modify) manifest/document cleanup, artifact drift, release checks and free-hosting setup.

## Impact

Broad feature revision across `backend/src/pa/`, `backend/tests/`, `frontend/src/`, frontend tests, analysis/model/results artifacts, source manifests and scripts, CI, current research documentation, and project policy wording. Reuse existing Python/React/TypeScript/schema infrastructure. Charting additions and hosting details require technical validation. Raw recordings/metadata/unique renders and Windows originals remain preserved. Existing unrelated local edits are not part of automatic cleanup or staging.

At intake start the checkout is `261008-ymhz-research-platform-rebuild` at `5d87d49`; `origin/main` is `41d6ba5`. New branch inherits current HEAD under fab-new rules; inspect ancestry before PR creation rather than resetting user work. Existing changes: `artifacts/model/metadata.json`, previous change `.history.jsonl`, and untracked revision guide, review PDF, thesis DOCX and InDesign ZIP. Do not commit these indiscriminately.

## Open Questions

No unanswered product question blocks intake. The owner explicitly chose a source-review/specification checkpoint for numerical methods: transformations/weights, partial-fusion eligibility, signal thresholds/timebase, pooled analysis, evaluation and learning curves must be investigated and presented there. This is a planned deliverable, not an assumed scientific decision or permission to run analyses first. Any newly discovered missing source fact is raised at that checkpoint. Hosting/LFS choice follows inventory at CP-A; domain selection/purchase is deferred to release planning.

## Assumptions

| # | Grade | Decision | Rationale | Scores |
|---|-------|----------|-----------|--------|
| 1 | Certain | Latest discussion overrides conflicting guide: physiology-led research, comparative findings, fused-only studio and closest requested score. | Owner repeatedly specified and corrected these exact behaviours. | S:100 R:85 A:95 D:100 |
| 2 | Certain | Landing explains thesis; eight pages separate findings and studio; no public thesis/CV/portfolio links. | Owner accepted IA and explicitly replaced findings-led landing/document links. | S:100 R:95 A:95 D:95 |
| 3 | Certain | Keep target-distance Neuro-Score, display 0–100, constrain generation by locks/ranges; keep emotional target distinct from numeric requested score. | Owner accepted the formula concept and corrected minimum-score search to closest-score search. | S:95 R:85 A:95 D:95 |
| 4 | Certain | Preserve usable data and complete/partial distinctions; exact scientific methods require CP-Spec and manual QC CP-B. | Owner accepted this process; constitution forbids invented or invalid replacement measurements. | S:100 R:80 A:95 D:95 |
| 5 | Certain | One repository, current-tree cleanup only, read originals before removal, preserve Windows sources and scientific documentation. | Owner explicitly rejected history rewrite, additional repository and personal document publication. | S:100 R:80 A:95 D:95 |
| 6 | Certain | Full catalogue/legacy chart ideas, public research data, profile image/contact and IAAC link; prototypes remain demonstrations. | Explicit discussion answers and supplied paths/contact details. | S:100 R:90 A:95 D:95 |
| 7 | Confident | Coordinate whole revision in this intake, implement reviewable workstream slices and preserve all six checkpoints. | fab-new follows the complete discussion; guide prefers per-workstream branches, so branch/PR sequencing remains an implementation-planning detail. | S:80 R:80 A:75 D:75 |
| 8 | Certain | Proposed routes/charting choices may be finalized during planning while retaining accepted page names, scope and accessibility. | Owner accepted page structure and guide defaults; these reversible technical details do not alter the product contract. | S:85 R:95 A:90 D:85 |

8 assumptions (7 certain, 1 confident, 0 tentative, 0 unresolved).
