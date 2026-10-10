# Decision history

This is an append-only record for this retrospective rebuild. A new decision may supersede an old one but does not erase it. The generated scientific settings are in `backend/src/pa/decisions.yaml`; the narrative method contract is `docs/specs/analysis-v1.md`. No entry claims prospective preregistration.

## D-001 — 2026-10-08 — Preserve source evidence before replacement

**Decision:** Inventory and hash original recordings, metadata, thirty renders, legacy images and thesis PDFs before migration or cleanup. Keep equivalent destination copies and a path map.
**Reason:** Current files include tracked and untracked source evidence, and the old app will be retired.
**Evidence:** `docs/reports/migration-inventory.json`, `data/MANIFEST.sha256`, `docs/reports/phase-0.md`.
**Supersedes:** None.

## D-002 — 2026-10-08 — Conditional acquisition timeline

**Decision:** Use 500 Hz as a conditional primary analysis rate, with 250/256/512 Hz sensitivity and per-file duration/counter flags. Do not call the setting confirmed.
**Reason:** Median count/logged-duration ratios are near 500, but the files contain no timebase/settings and manufacturer firmware/application variants differ.
**Evidence:** `artifacts/results/audit.json`, `docs/reports/phase-1.md`, manufacturer links in `docs/specs/analysis-v1.md`.
**Supersedes:** Historical 256 Hz hardcode and old roadmap's confirmed-rate language.

## D-003 — 2026-10-08 — Explicit signal validity

**Decision:** Analyze available samples with documented conditional rate, 4-second EEG epochs, 1–45 Hz SOS filtering, positive alpha/beta power, and 5–25 Hz QRS ECG processing. Record flat/artifact/duration/beat/interval reasons. No neutral or nominal physiological replacement.
**Reason:** Two approximate forehead channels, wrist ECG, unknown units and variable short trials require conservative, inspectable QC.
**Evidence:** `docs/specs/analysis-v1.md` and its cited primary methods; synthetic tests and real QC report pending implementation.
**Supersedes:** Legacy fixed 256 Hz, 10-second onset removal and RMSSD fallback.

## D-004 — 2026-10-08 — Keep measured ratings and constructed affect distinct

**Decision:** Preserve transformed CSV scores unchanged. Experiment 1 comfort stays separate; objective components and subjective/fused coordinates have explicit modality cohorts. Primary alpha is 0.5, with 0/0.25/0.75/1 sensitivity and stratified experiment reporting.
**Reason:** Fusion is a descriptive hypothesis and the rating elicitation differs between experiments.
**Evidence:** Owner report in `docs/protocol/ratings.md`; `docs/specs/analysis-v1.md`.
**Supersedes:** Historical fixed 0.6 fusion and automatic ground-truth label.

## D-005 — 2026-10-08 — Fold-contained prediction and user-selected scoring

**Decision:** Use distinct held-out-room and held-out-subject evaluation, training-fold preprocessing/target transforms, simple baselines before candidates, and a complete serialized pipeline. Neuro-Score is fixed-diameter Euclidean proximity to a selected target; raw predictions outside the signed square are projected only for scoring and flagged.
**Reason:** Repeated participants/rooms and novel-user inference invalidate global target normalization and random-row evaluation; fixed room-type preferences were not owner intent.
**Evidence:** `docs/specs/analysis-v1.md`, Fab plan R12–R15.
**Supersedes:** Historical fixed space-type targets, stretch formula and heuristic confidence.

## D-006 — 2026-10-08 — Descriptive inference remains qualified

**Decision:** Report crossed participant/room counts and descriptive associations; issue no automatic trial-iid intervals, p-values or causal claims. Explicitly mark unavailable inference/calibration.
**Reason:** Ten participants, thirty rooms, modality exclusions and unmatched simulated covariates do not support nominal independent-trial inference.
**Evidence:** `docs/specs/analysis-v1.md`.
**Supersedes:** Old roadmap's default mixed-model, bootstrap and p-value recipes.

## D-007 — 2026-10-08 — Supersede incomplete EEG artifact rule before real analysis

**Decision:** Reject raw epochs with repeated exact extrema at the stated single/both-extrema fractions, before per-epoch filtering. Keep relative spike/step QC, counter-gap exclusion and independent filtering of accepted epochs. Inspect raw/cleaned spectra for residual line noise; the 45 Hz filter attenuates but does not eliminate 50 Hz.
**Reason:** The first independent checkpoint showed a consistently clipped synthetic sinus passed every relative epoch rule. Unknown signal units prevent a microvolt threshold, but exact repeated extrema are a raw-unit-independent warning for possible clipping. Relative rules cannot prove absence of persistent contamination.
**Evidence:** `docs/reports/audit-spec-review.md` M1 and should-fix 1; amended `docs/specs/analysis-v1.md`, synthetic regression tests.
**Supersedes:** D-003's incomplete EEG QC wording; the original D-003 remains historical. No participant-level result preceded this amendment.

## D-008 — 2026-10-08 — Supersede underspecified ECG admission and duration

**Decision:** Segment at counter gaps/dropouts, reject repeated-extrema signals and noise-only morphology, use frozen peak/prominence/template/polarity/local-RR rules, and require one qualifying contiguous usable interval run for HR/RMSSD with full 10/20/30-second scenarios. Record raw peak/RR/quality evidence; accepted RR is not verified NN.
**Reason:** Noise-only synthetic recordings passed the previous numerical detector, and total file duration/interval count could overstate usable HRV coverage.
**Evidence:** `docs/reports/audit-spec-review.md` M2; amended `docs/specs/analysis-v1.md`, synthetic regression tests.
**Supersedes:** D-003's incomplete ECG criterion. No participant-level result preceded this amendment.

## D-009 — 2026-10-08 — Freeze nested selection and calibration before model results

**Decision:** Use the specified training-median/MAD population mapping and degeneracy rule, refit it with feature transforms in each inner-training partition, compare the exact baseline/Ridge/RandomForest candidates by equal-group/equal-axis MAE, resolve ties in fixed simplicity order, fall back to median baseline with fewer than four groups, and select the final full-data artifact through room-group inner CV independently of outer evaluations.
**Reason:** The first checkpoint found the prior "small bounded" and "consistently better" phrases left material choices to implementation after seeing results.
**Evidence:** `docs/reports/audit-spec-review.md` M3; amended `docs/specs/analysis-v1.md`, fold-isolation tests pending implementation.
**Supersedes:** D-005's incomplete selection contract. No participant-level model result preceded this amendment.

## D-010 — 2026-10-08 — Record the independent checkpoint outcome

**Decision:** Mark specification v1.1.0 as reviewed for conditional retrospective analysis after the fresh independent re-review and coordinator PASS. This is an administrative status update only; no analytical setting or method changed after review. Preserve the reviewed snapshot hashes in the review report and regenerate artifact metadata against the current source bytes.
**Reason:** A stale "pending" label would contradict the recorded gate outcome.
**Evidence:** `docs/reports/audit-spec-rereview.md` and `docs/reports/analysis-checkpoint.md`.
**Supersedes:** The pending-status labels only; D-007 through D-009 methodology remains in force.

## D-011 — 2026-10-08 — Include opening counts in empirical room support

**Decision:** Assess studied support against all nine previously checked numeric attributes plus `num_doors` and `num_windows`. A candidate missing either opening count has unavailable support; a count outside the observed complete-room range is outside range. Recompute the normalized nearest-room distance and leave-one-room threshold using these eleven attributes. Physical validity remains a separate check.
**Reason:** Opening counts are model inputs. Omitting them let a room with 99 doors be labelled an exact studied room.
**Evidence:** `docs/reports/final-review.md` FR-05; focused support regression and regenerated result/artifact evidence will follow this amendment.
**Supersedes:** The narrower numeric support neighborhood in the initial implementation. This amendment precedes regeneration; it does not alter source observations or physiological analysis.

## Approved v1.2 amendment — 2026-10-10

The owner approved the entire unchanged [v1.2 source snapshot](docs/specs/analysis-v1.2-draft.md) at [CP-Spec](docs/reports/revision-2026-10/CP-Spec.md), SHA-256 `51c01ef6ccdf2f4318ac786d1bb39afeb1aa2bcf3bc93039479a4ed2454603ac`. The original proposal text and filename remain byte-identical to the approved target. The following decisions supersede conflicting v1.1 method details while preserving D-001–D-011 and historical v1.1 outputs. CP-B remains unsigned; approval of methods is not approval of individual signal validity.

### D-012 — Conditional timebase and review-only signal flags

**Decision:** Retain conditional 500 Hz, 250/256/512 sensitivities and first-five-seconds-included primary analysis. Export per-file timebase evidence; add the exact v1.2 channel-imbalance, amplitude, raw line-noise and filtered muscle review flags and sensitivity thresholds. A flagged channel/trial has a pending CP-B disposition; no participant-wide exclusion is presumed.
**Reason:** Counter continuity and logged duration do not prove hardware rate; unknown units and reference placement require inspectable screening and owner review.
**Evidence:** Approved v1.2 source PD-002/003 and CP-Spec hash above.
**Supersedes:** D-002/D-003/D-007 only where v1.2 adds review evidence. Their historical status remains intact.

### D-013 — Complete and partial physiology/fusion definitions

**Decision:** Expose FAA, alpha suppression, engagement, muscle and ocular-unavailable candidates separately. Require bilateral FAA, both cortical candidates and valid HR for complete physiology; RMSSD is descriptive. Within-participant/experiment descriptive mapping is separate from fold-fitted population calibration. Use equal EEG/HR arousal and equal physiology/report primary fusion, with declared partial labels and 0/0.25/0.75/1 fusion sensitivities.
**Reason:** The approved contract retains EEG/ECG-led comparison without hiding component disagreement or replacing missing measurements.
**Evidence:** Approved v1.2 source PD-001/004/005 and CP-Spec hash above.
**Supersedes:** D-004's old RMSSD-gated complete objective and v1.1 beta/alpha candidate definition; historical outputs keep those meanings.

### D-014 — E3-only deployed fused model and fixed evaluation

**Decision:** The Studio's deployable target is complete fused E3 response with full independent Function-room attributes. E2 stays in common-feature research analysis. Fit all component calibrators within each nested training partition, use grouped room/person questions, fixed baselines and negative controls, and report unsupported tiers as unavailable.
**Reason:** E2 has no walkable area or space type and the Studio request has no experiment input; an imputed or pooled target would change the deployment estimand.
**Evidence:** Approved v1.2 source PD-006 and CP-Spec hash above.
**Supersedes:** D-005/D-009's broader unspecified full-attribute cohort wording. Existing model artifacts remain v1.1.

### D-015 — Requested numerical Studio score

**Decision:** Keep API Neuro-Score on 0–1 and display it on 0–100. Bounded generation minimizes absolute distance from the visitor's requested score under locks, physical validity and studied support, exposing achieved difference and unavailable status.
**Reason:** The score request is an objective, separate from the visitor's emotional target.
**Evidence:** Approved v1.2 source PD-007 and CP-Spec hash above.
**Supersedes:** D-005's optimizer objective only; score geometry is preserved.
