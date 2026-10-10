# Interim independent science implementation review

**Review date:** 2026-10-10. **Reviewer:** fresh independent Codex worker, `gpt-6-astra`, reasoning `xhigh`, dispatched through native collaboration with explicit model/effort settings. **Scope:** settled CP-B integration, affect construction, grouped fused modeling, spatial controls/learning-curve implementation, and available rating/transfer products for change `261010-tadj-research-atlas-design-studio`.

**Interim verdict: one open must-fix export requirement; no identified numerical defect requiring interruption of the running spatial controls.** One descriptive-calibration mismatch was corrected during this review and independently verified. This is neither whole-change acceptance nor CP-C publication approval. The remaining catalogue, full 1,000-draw control artifact, learning-curve artifact, final cards, and website were still being completed; absence of an unfinished product was not classified as an implementation defect.

The review used AGENTS.md, project config/constitution/code-quality/code-review policy, the change requirements and T019–T025/T031–T037, the approved v1.2 source, CP-Spec/CP-B records, decision history, research memory, actual implementation/tests, and generated evidence. The approved source remains SHA-256 `51c01ef6ccdf2f4318ac786d1bb39afeb1aa2bcf3bc93039479a4ed2454603ac`. The user's explicit checkpoint delegation authorizes evidence-based AI disposition; this review does not invent personal owner inspection or introduce another permission stop.

## Open must-fix

### SCI-01 — Export the actual held-out fused predictions and target construction

**Location:** `backend/src/pa/modeling/evaluate.py:164` and `backend/src/pa/modeling/train.py:117` at the reviewed snapshot.

`evaluate_outer` computes the outer-training calibrator, held-out constructed targets, estimator predictions and both baseline predictions, but returns only errors, memberships, candidate selection and inner calibration diagnostics. `evaluate_and_fit` writes those incomplete folds unchanged. The actual `artifacts/results/model_evaluation.json` therefore contains no per-trial outer predictions/targets, baseline prediction vectors, or outer-training calibrator. Approved PD-006 expressly requires exported per-fold memberships, predictions, baselines and provenance. Aggregate MAE alone cannot show which held-out observations produced a reported result, and an inner calibrator is not the outer calibrator used for scoring.

**Required correction:** enrich each evaluated fold with IDs/memberships, both axes of held-out predictions and constructed targets, both baseline vectors, and the training-only outer component centers/scales. Verify that reconstructed group/axis MAEs reproduce the stored scores. An export helper can refit the already selected candidate on its recorded training membership without changing the numerical control implementation or invalidating the current control run. Research worker notified and accepted the correction; final enrichment had not yet been reviewed when this report was written.

## Corrected during review

### SCI-02 — Descriptive calibration used population eligibility thresholds

**Location:** `backend/src/pa/affect/normalization.py:39` and `:46` after correction.

The initial implementation required three distinct numeric values and borrowed the population scale cutoff of `1e-9`. Approved PD-004 requires at least three distinct eligible trials and a positive descriptive MAD scale; only PD-006's population model calibrator requires three distinct values and its specified minimum scale. Four distinct eligible trials with values `[0, 0, 1, 1]` have center `0.5` and robust scale `0.7413`, yet were incorrectly unavailable.

The research worker removed the numeric-uniqueness gate from descriptive calibration, required positive scale, and added a repeated-value regression. Independent verification after the fix found every normalized component on all 160 current records identical to the existing affect artifact, and the complete calibration-diagnostics mapping identical as well. No current cohort, target, or control input changes as a result. The population model rule remains unchanged.

## Reproduction concern to address before future control-cache reuse

`backend/src/pa/modeling/nulls.py` fingerprints the main numerical implementation, settings, affect input, QC ledger and dataset manifest, but does not fingerprint `build_cohort` and all feature-frame/schema/metadata-loading dependencies. On resume it rebuilds the current cohort without comparing its actual IDs, features, raw components, reports and group arrays with the saved cohort. A changed cohort builder could therefore combine old and new draws under an unchanged listed fingerprint. No evidence of mixed inputs was found in this active run, and this is not a reason to discard its valid computations. A deterministic digest of the actual serialized modeling inputs, checked when resuming, would close the gap without tying cache validity to unrelated export edits in `train.py`. Record actual dependency-lock/package provenance with the final control product. This concern was sent directly to the research worker.

## Verified scientific behavior and evidence

- **CP-B exact source/decision reconciliation:** the live science gate passes. Coverage is exactly 160 source trials and 346 queue entries, with 304 accepts, 31 rejects and 11 uncertain decisions. Derived eligibility counts are timebase 154, right EEG 132, left EEG 138, bilateral EEG 128, HR 66 and RMSSD 17. The gate checks approved-spec/source/reviewer hashes, reconstructs expected queue identities and integrated eligibility, and prevents rejected/uncertain or automatically invalid measurements from being promoted. The ledger identifies delegated AI reviewers and does not claim personal owner review.
- **Per-channel preservation and candidate equations:** independent re-derivation directly from source samples reproduced FAA and the trial median of accepted-epoch alpha-suppression/engagement/muscle expressions exactly, with zero numerical difference, for bilateral `E3:Subj_A:Rm_021`, single-left `E3:Subj_H:Rm_021`, and bilateral `E2:Subj_E:Rm_014` as applicable. This checks median-of-expression aggregation and review-driven single-channel recomputation rather than relying solely on helper tests.
- **Cohorts and fusion:** all 160 records remain accounted for; E1 comfort is not a valence axis. Descriptive complete fusion has 19 E2 and 21 E3 trials. The deployable raw-component model has 23 E3 trials across ten rooms and four people. The difference is intentional: descriptive within-person/experiment calibration is not a model-cohort gate. Fusion uses bilateral FAA, both cortical arousal components and HR, equal EEG/HR arousal, then equal physiology/report axes; RMSSD is not a primary eligibility requirement.
- **Deployment and comparator boundaries:** the fused cohort requires all 13 independent E3 room fields and uses the shared feature builder. The self-report comparator retains all 50 E2 and 60 E3 rating trials separately. E2 uses 17 common derived features and omits walkable area, walkable-area ratio and space type; E3 uses 20 features. The comparator is research-only and does not replace fused Studio targets.
- **Fold isolation:** all ten actual outer room folds have three inner grouped splits with disjoint room membership. The four actual outer person folds each have only three training people, so all four correctly take the prescribed baseline fallback without inner tuning. Inner target calibrators and feature pipelines fit only the current inner-training rows; outer calibration and fitting use only outer-training rows. Candidate selection averages equally over corresponding validation groups and both axes. An independent refit of the first stored actual outer-room selection reproduced its recorded MAE exactly: `0.24631254942022648`.
- **Honest current model outcome:** final full-data room-group selection is `dummy_mean`, status `baseline_only`. The nested held-out-room procedure's mean MAE is `0.3496435310666118`, versus median baseline `0.34605538214005377` and mean baseline `0.34043750113477267`. Held-out-person MAE is `0.3511803594208226`, equal to its median-baseline fallback. These results do not establish useful room-attribute prediction or justify a prediction-confidence percentage.
- **Spatial-control computation:** each seeded draw freezes the same outer leave-one-room-out groups, permutes whole training-room feature vectors among E3 training-room IDs, leaves held-out attributes/outcomes untouched, reruns inner population-target calibration, preprocessing and candidate selection, and refits the chosen estimator on outer training rows. Moving the complete deterministic feature vector preserves each source room's internally derived attributes. Scoring uses equal-axis/equal-held-out-room MAE. The code requests exactly 1,000 draws and labels them descriptive rather than calibrated population p-values. The checkpoint was still in progress during review; no final null finding is certified here.
- **Learning-curve design:** the seeded subset generator produces exactly 100, 100, 100, 100, 45 and 10 unique training-room subsets at k=4,5,6,7,8,9: 455 total. Each subset keeps the other rooms for testing and selects candidates/calibrates only within its training rooms. Overlap is explicitly descriptive, not independent replication. The final computed curve was not yet reviewed.
- **Ratings and known-room transfer:** the available research artifact has all 1,000 room-label-within-person controls for E1 comfort and each E2/E3 axis. Each E2/E3 axis has exactly ten unordered rater partitions and 1,000 transfer controls. Held-out observed means are used only to center each held-out person's evaluation vector; training room profiles use only other people. Transfer labels and outputs state the relative-response estimand and zero baseline.
- **Participant bootstrap:** validity summaries resample participant-level correlations, which is exactly equivalent to resampling their complete fixed room vectors and recomputing the equal-person statistic. Current contributing-person counts match available correlations. The room-mean bootstrap preserves repeated selections of the same participant as separate copies; a synthetic reference with four unequal participant profiles reproduced the direct-array 95% interval exactly (`[0.5, 7.0]`) and showed no participant-ID deduplication/weight collision. Fewer than four contributors produce unavailable intervals. The R2 seed drift from `2718 + experiment` to approved `2718` was also corrected while that catalogue product was being authored.

## Validation run by this reviewer

From `backend/`:

```text
.venv/bin/pytest -q tests/test_eeg.py tests/test_affect.py tests/test_science_gate.py tests/test_evaluation.py tests/test_rating_models.py tests/test_analysis.py tests/test_train.py
38 passed in 36.38s

.venv/bin/pytest -q tests/test_affect.py
4 passed in 0.56s
```

The second command checks the subsequent normalization correction. Additional read-only scripts independently checked current CP-B/cohort counts; compared every normalized row and calibration diagnostic before/after the correction; recomputed three selected source-signal candidate expressions; checked actual outer/inner memberships; refitted one stored outer selection; enumerated unique curve subsets; inspected all rating/control denominators; and compared bootstrap multiplicity with a direct-array calculation. They did not modify source evidence or implementation.

## Remaining review boundary

Before a publication checkpoint, review SCI-01's enriched folds, the completed 1,000 spatial-control draws, the computed learning curve, final catalogue mappings/denominators/provenance and cards, and the explicit separate negative-log-RMSSD sensitivity being added to B3. Fresh whole-change review remains required after apply completes. No task/Acceptance boxes or pipeline stage were marked complete by this interim review.
