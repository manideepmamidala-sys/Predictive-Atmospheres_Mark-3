# Independent CP-C scientific checkpoint review

**Original review date:** 2026-10-10. **Original reviewer:** fresh Codex agent `/root/model_checkpoint_review`, dispatched with model `gpt-6-astra` and reasoning effort `xhigh`, following AGENTS.md. This is an evidence-based AI review under the user's standing checkpoint delegation, not personal owner inspection.

**Original final status: PASS for the qualified CP-C research-publication scope**, recorded 2026-10-10T12:36:53Z. The complete control/comparison evidence and corrected final export contract support [CP-C's delegated baseline-only disposition](CP-C.md); no open must-fix remained in that slice. This did not certify whole-change release or completed clean reproduction. The running spatial null was not interrupted, and that reviewer changed no implementation, numerical inputs, task boxes or pipeline state.

**Earlier release-validation refresh status: PASS for the same qualified scope**, recorded 2026-10-10T13:10:07Z by fresh independent reviewer `/root/science_receipt_refresh`, natively dispatched as `gpt-6-astra` with `xhigh` reasoning. The [dated refresh below](#release-validation-refresh--2026-10-10t131007z) reviews the changed summary, B5 wording and artifact provenance. Original findings and hashes are retained as historical evidence; they are not rewritten as if the original reviewer inspected later bytes.

**Current rework status: PASS for the same qualified scope**, recorded 2026-10-10T16:08:42Z by fresh native Codex `gpt-6-astra`/`xhigh` reviewer `/root/checkpoint_refresh`. The [dated rework receipt](#rework-receipt--2026-10-10t160842z) is limited to nonnumerical rework and artifact identity.

## Resolved findings

**SCI-01 — held-out prediction export: resolved.** `model_evaluation.json#/outer_prediction_evidence` now records all ten room and four person folds, exact training/test trial and group identities, both axes of the constructed held-out targets, selected predictions, mean and median baseline predictions, and the corresponding outer-training component centers/scales. These are deterministic refits of each recorded selection; they are not mislabeled new model-selection experiments.

Independent arithmetic rebuilt each target directly with NumPy median, `1.4826 × MAD`, `tanh`, the approved component weights and original E3 signed ratings. All 14 outer calibrators/targets, 28 fixed-baseline prediction vectors and MAEs, 14 selected-estimator refits and 30 inner-training calibrators agree with the exported evidence. Train/test group disjointness and complete 23-trial membership were checked in every outer fold. All four held-out-person folds correctly use the prescribed training-median fallback with three remaining people. The equal-axis/equal-group aggregate errors agree with the report.

**SCI-03 — mixed comparator units and denominators in P3: resolved in the generated product.** Initially, the E2/E3 self-report comparator rows inherited the fused product's 23-trial caption and constructed-coordinate error unit without their own denominators. The implementation worker added row-specific target type, error unit and trial/person/room counts. E2 is 50/5/10 and E3 is 60/6/10 on the signed source rating scale; fused rows are 23/4/10 on constructed-coordinate units. The caption now explicitly describes the primary fused cohort, and the comparator remains research-only. Independent final inspection checked all 24 exported P3 rows against their respective learning, outer-fold or comparator source. This reporting correction does not change numerical control inputs.

## Independently verified numeric evidence

| Question | Selected procedure MAE | Median baseline MAE | Mean baseline MAE | Held-out groups |
| --- | ---: | ---: | ---: | ---: |
| New E3 room | 0.3496435310666118 | 0.34605538214005377 | 0.34043750113477267 | 10 rooms |
| New E3 person | 0.3511803594208226 | 0.3511803594208226 | 0.38000579365828807 | 4 people |

All **455** stored learning subsets were independently checked for unique identities, requested k, disjoint training/test rooms, complete room coverage and evaluated status. For each subset, the reviewer independently rebuilt the target calibrator and fixed median prediction, refitted the recorded selected estimator, and recomputed equal-room/equal-axis errors. This verifies every stored selected result without claiming to have independently rerun all candidate-selection searches. The maximum absolute numerical difference across these checks and the outer-fold checks was **2.7755575615628914e-16**.

| Training rooms | Distinct evaluated subsets | Selected procedure MAE | Median baseline MAE |
| ---: | ---: | ---: | ---: |
| 4 | 100 | 0.37603750375398365 | 0.358276870810502 |
| 5 | 100 | 0.3581741464046671 | 0.3477303221033 |
| 6 | 100 | 0.3529965627896744 | 0.3467005969665316 |
| 7 | 100 | 0.34197344090418835 | 0.33822189268677966 |
| 8 | 45 | 0.34268900098740246 | 0.3420852105130109 |
| 9 | 10 | 0.3496435310666118 | 0.34605538214005377 |

The selected procedure is worse than the fixed median baseline at every k. Overlapping subsets are descriptive, not independent replicates or evidence of eventual improvement.

The serialized full-data fit selects `dummy_mean` and is correctly labeled **`baseline_only`** in metadata and evaluation. Loading the exact trusted local model and predicting all 23 source rows returns the same coordinates, `[0.19933647676353913, -0.07416070665631107]`, equal to the independently computed full-data target mean. It has no learned room-attribute response. Prediction and Studio source code display explicit baseline-only notices; P4 correctly withholds feature importance for the constant model.

## Provenance and remaining boundary

The approved specification hash remains `51c01ef6ccdf2f4318ac786d1bb39afeb1aa2bcf3bc93039479a4ed2454603ac`. The current effective-input guard exactly matches the reconstructed trial IDs, feature frame, raw components, reports, group arrays and declared dependency hashes. The guarded CLI rejects changed inputs before consuming cached draws.

The active null run began before this guard existed. A later match of source fingerprints, trial identities and observed folds does **not** prove the historical feature matrix at draw zero. No mixed numerical input was identified, and no rerun was demanded for an unrelated presentation edit. The planned clean source-only reproduction must create the guard before draw zero, compute all 1,000 draws and all 455 subsets, and compare every scientific record before anyone claims a completed clean reproduction. The present review is not that reproduction.

Read-only validation command:

```text
PYTHONPATH=backend/src backend/.venv/bin/python /tmp/tadj-cpc-review.py
# exit 0; all 14 outer folds and 455 recorded learning fits verified
# maximum absolute difference 2.7755575615628914e-16
```

The script was a reviewer scratch check, not a retained pipeline entry point. Final read-only control validation used:

```text
PYTHONPATH=backend/src backend/.venv/bin/python -u /tmp/tadj-cpc-null-check.py
# exit 0; all 1000 draw identities and 10000 evaluated room folds verified
# current-source full-refit draws 0 and 999 match all saved fields exactly
```

The final control has all requested draw IDs 0–999, seed 2718, ten frozen room folds per draw, finite axis/group scores and exact aggregation. Observed folds equal the main model evaluation; original source fingerprints and current effective-input guard match their files. All 1,000 ordered `null_mean_mae` values equal their per-draw records. Null median is **0.34899592858756306**, mean **0.3522848315810652**, and 2.5th/97.5th percentiles are **0.3334784641674735 / 0.4101804617224629**. The observed **0.3496435310666118** is close to that median. These quantiles describe the shuffled control distribution and are not a population confidence/prediction interval.

Full draw 0 regenerated to MAE **0.3392660539326268** and draw 999 to **0.35080905976086685**, with every nested identity, candidate, status and score exactly equal to the saved records. These are two sampled current-source regenerations. They do not establish that all original draws used an independently authenticated historical feature matrix or constitute a clean 1,000-draw reproduction.

The reviewer independently recomputed all eight source digests declared by `model_poc.json`, retaining every scientific value while omitting only its declared timing/checkout fields; all match. Its grouped scores, null quantiles, cohort and learning counts match the detailed products. The settled metadata passes the real artifact loader's code/data/spec/package/byte compatibility checks. Final model/data cards were read against those products, including the completed-control paragraph and explicit baseline-only interpretation.

All 28 generated catalogue products pass their strict schema: 27 are available, and only P4 is unavailable for the scientifically justified constant-model importance reason. Additional source-to-export checks covered all 22 P1 transfer records; all nine P2 histograms, independently rebinned from their 1,000 source values with observed and median markers verified; every P3 comparison's target/unit/denominator/value; and R7's 120 distinct trial-axis observations plus ten function means and associated room/person counts. P5 preserves the 160-source/60-E3/23-complete-trial path and separately labels ten room groups. This is a scientific export review, not a visual rendering inspection.

Original final staging found and corrected an index-path contract mismatch. The reviewer then verified all 28 canonical `/research/analysis/{ID}.json` paths and strict index/product schemas, all ten original final file-byte hashes in CP-C, the refreshed model loader compatibility, then-current effective-input guard and all eight comparison source digests. The code-dependent metadata/comparison hashes changed as expected; model bytes, evaluation, null, learning curve, input guard, cards and canonical scientific catalogue content remained identical to the checked evidence at that disposition. The original final code-tree hash was `3d9b4a8e8306c944a08a616ac0f09515eeda8169fb550cc9c88192a9a7cd8c99`.

Exact reviewed files at the numeric-check snapshot:

| File | SHA-256 |
| --- | --- |
| `artifacts/results/model_evaluation.json` | `d419789fa076bbb6e816e3090647c3230409547a829310c7879719fd0a2641a6` |
| `artifacts/results/model_learning_curve.json` | `f6568570c9bc44cdb03f70943a788c1ccc3b092fa120ab6fe431b597bf22387e` |
| `artifacts/results/model_null_input.json` | `8f256372cb6acaeadd40807e33a7bba18e9bc7a5ced278241a0c5f195ab64a77` |
| `artifacts/model/model.joblib` | `17bfa472c30a9bb24034dd3800c85cd1fa9db36fec8c4a6cba2b8070b6b3544d` |

The numeric-check snapshot above remained unchanged at the original final review. [CP-C](CP-C.md#exact-reviewed-versions) retains the additional exact original final model metadata, null, comparison, catalogue-index and card byte hashes, plus the original canonical scientific identity for the complete catalogue. That catalogue digest was `58636603a84d5250f748d424e6a6f69b4d8d72cce41be78fe2efeb9cf278ecd5` (ID-to-product mapping; sorted compact JSON; only each `provenance.generated_at_utc` omitted).

**Remaining limitation, not a fabricated completion:** the first null run predates its effective-input guard. No input mixture or numerical defect was identified; sampled regenerations add consistency evidence without removing that historical limitation. Clean source-only full reproduction, fresh whole-change review and release/visual checks remain separate obligations. This review approves honest baseline-only presentation with those limits retained and claims no human-owner inspection.

## Release-validation refresh — 2026-10-10T13:10:07Z

**Verdict: PASS / APPROVED_FOR_BASELINE_ONLY_PUBLICATION_WITH_LIMITATIONS.** Fresh reviewer `/root/science_receipt_refresh` used the requested native `gpt-6-astra`/`xhigh` route. Scope is the affected scientific receipt after the release worker's in-place pipeline and B5 correction. It is not the formal whole-change review, an acceptance decision or a claim of personal owner inspection. The user's existing automatic-checkpoint delegation supplies authorization; the concrete checks below supply the disposition evidence.

**Refresh finding RSCI-01 — stale affect summary: resolved.** The retained pre-pipeline reference `/tmp/pa-reference-canonical-k22dtm_0` matches the original CP-C artifact receipts. Its `affect_analysis.json` was still version `1.1.0` with five experiment/cohort groups, although `affect_detail.json` and the reviewed descriptive catalogue already followed v1.2. The successful in-place pipeline regenerated the summary from the approved v1.2 source. This refresh explicitly reviews that previously stale summary rather than silently treating it as a timestamp change.

The reviewer read the approved method and independently rebuilt 800 normalized component values for all 160 unique trials using participant-and-experiment median, `1.4826 × MAD`, minimum eligible observations, positive-scale checks and `tanh`; undefined values remained unavailable. Original source self-report axes were checked through the metadata loader. Independent arithmetic then rebuilt all objective/fused axes and cohort labels, all 43 experiment/room/person summary records, 18 signed/absolute disagreement summaries and all four room-level descriptive associations. No interval or p-value was introduced. The summary groups are:

| Experiment | Objective only | Complete fusion | Partial modality | Partial axis | Subjective only | Total |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| E1 | 50 | 0 | 0 | 0 | 0 | 50 |
| E2 | 0 | 19 | 18 | 1 | 12 | 50 |
| E3 | 0 | 21 | 20 | 14 | 5 | 60 |

These are nine nonempty experiment/cohort groups covering every source record. E1 is not given self-report affect axes. The 21 complete descriptive E3 records are distinct from the model's 23 raw complete-component records, whose target calibration remains within training partitions.

**Refresh finding RSCI-02 — B5 displayed versus correlated denominators: resolved.** All 52 plotted pairs were matched to trial evidence. E2 displays and correlates 19 pairs/three people. E3 displays 33 raw-HR pairs/five people; correlation uses 31 normalized-HR pairs/four people. `E3:Subj_D:Rm_022` and `E3:Subj_D:Rm_023` have raw HR but no calibrated HR because only two eligible observations are available for that person/experiment. The final takeaway, method and added caveat identify this distinction.

The reviewer independently ranked the paired observations, recomputed all seven contributing participant correlations, their equal-person means (**−0.02204558976695528** in E2 and **−0.4447660238127104** in E3), and E3's 2,000 seeded participant-bootstrap interval. E2 correctly has no interval because only three people contribute. Across these and the affect checks, the maximum absolute numerical difference was **5.551115123125783e-17**. The B5 chart rows, values, existing caveats and all statistics are unchanged; only the takeaway, method and one additional caveat differ.

**Strict identity and compatibility checks: pass.** All 53 result JSON paths were compared to the pre-pipeline reference using exact value equality after the repository's narrowly declared generation/elapsed-time normalization, rather than a numerical tolerance. Only six JSON products changed substantively: the corrected affect summary; B5 explanatory text; the model comparison's code hash and metadata digest; the public model and bundle code hashes; and their corresponding manifest hashes. Model metadata changed only its code-tree hash. This comparison does not omit scientific values or general provenance fields.

The model bytes, held-out evaluation, completed null, effective-input guard, affect detail and validity are byte-identical to the original reference. All 455 learning subsets, memberships, selections, errors and aggregate values are exactly equal after omitting only the learning run's elapsed time. The refreshed check revalidated 1,000 evaluated null identities and 10,000 finite room folds and their mean aggregation, all 455 evaluated unique subset identities, equality of null observed folds with model evaluation, and exact equality of the current effective-input guard. It did not rerun the original sampled null draws or claim an independent full null reproduction.

The trusted real artifact loader passes current byte/data/spec/package/code compatibility checks. The unchanged fitted model predicts `[0.19933647676353913, -0.07416070665631107]` for every one of the 23 source training rows, preserving `baseline_only` behavior. All 28 products and the index pass strict schemas and canonical route/path validation: 27 available, with P4 unavailable because constant-model importance is unsupported. All eight `model_poc.json` source digests independently recompute under the declared digest rule. The unchanged model/data cards agree with the reviewed results and limitations.

Read-only reviewer scratch commands (both exit 0):

```text
PYTHONPATH=backend/src backend/.venv/bin/python /tmp/tadj-cpc-refresh-affect-check.py
# all160 trials,9 groups,43 summaries,18 disagreements,4 associations; B5 rows/ranks/bootstrap checked
# max_abs_difference 5.551115123125783e-17
PYTHONPATH=backend/src backend/.venv/bin/python /tmp/tadj-cpc-refresh-artifact-check.py
# strict53-product comparison; exact model/heldout/null identities;455 learning records unchanged
# compatible model;28 strict catalogue products;8 source digests; exact byte hashes
```

These scripts are temporary review evidence, not maintained reproduction entry points. The release worker separately reported `make pipeline` exit 0, with all 455 learning subsets recomputed and the exactly matched completed 1,000-draw null reused. This reviewer inspected the resulting records and identities; it does not claim to have launched that pipeline.

The subsequently frozen release reference `/tmp/pa-reference-final-329s8k69` was independently checked against this reviewed state: all 53 result JSON files and all four files under `artifacts/model/` match byte-for-byte. `python3 scripts/compare_reproduction.py /tmp/pa-reference-final-329s8k69 .` also exits 0. This confirms the release reference uses the reviewed bytes; it is not a comparison against a completed source-only reproduction.

The [current CP-C hash table](CP-C.md#release-validation-refresh--2026-10-10t131007z) records all 17 exact reviewed files, including the corrected affect summary and B5. Current code-tree SHA-256 is `9e6bd7cb97f84003d1777a09ca40517c43342117360cd193c3125216380438ce`; current canonical catalogue SHA-256 is `ca5f6029517b16e57e313c8c88e310fe00cb102218b1c505245a05c9c4632d3e`. The latter differs from the original only because of B5 explanatory text under the unchanged ID-to-product, sorted-compact-JSON rule excluding only `provenance.generated_at_utc`. Approved method and source evidence remain unchanged.

**Remaining boundary:** no unresolved must-fix was identified in this refresh. Clean source-only full reproduction is still pending; it must compute all 1,000 draws with the effective-input guard present before draw zero and all 455 subsets. The original historical-null limitation remains. No task/acceptance boxes or pipeline stages were changed by this reviewer; only this report and CP-C were edited, followed by the requested artifact-derived Fab status refresh.

## Rework receipt — 2026-10-10T16:08:42Z

**Verdict: PASS / APPROVED_FOR_BASELINE_ONLY_PUBLICATION_WITH_LIMITATIONS.** This fresh independent AI check follows the first formal review's QC/Methods presentation rework. It is separate from the forthcoming formal whole-change review. Native dispatch used Codex `gpt-6-astra` with `xhigh` reasoning, as required by AGENTS.md and confirmed by the parent dispatch; no nested reviewer was spawned. The user's standing checkpoint delegation supplies authorization, not a claim of personal owner inspection.

The reviewer independently compared all 53 result JSON paths with exact parsed equality after the existing narrowly defined generation/run-time normalization. Six products change: Methods adds approved evidence; signals and bundle add reviewed component provenance/reasons; model and comparison propagate the new code hash/metadata digest; manifest records the corresponding public-product hashes. Removing only those enumerated additions and provenance fields leaves every prior trial value, eligibility, trace, coordinate, cohort and sensitivity exactly equal. The other 27 catalogue products are unchanged apart from generation time. The raw model, evaluation, null, learning curve, input guard, affect detail/summary, validity, signal detail, timebase and CP-B ledger bytes exactly match the frozen pre-rework reference.

All five changed backend Python paths were compared with the completed isolated clone: `analysis/catalogue.py`, `results/build.py`, `results/disposition.py`, `results/export.py` and `results/schemas.py`. The catalogue/export changes attach optional Methods evidence while preserving existing product shapes elsewhere. The active `integrate_decisions`, `_digest`, `_index` and `_check_decision` syntax trees are unchanged after the unused writer/report helper removal. Approved spec, decisions YAML, source manifest and both reviewer decision files are byte-identical to the isolated snapshot. No numerical model or signal implementation changed.

The real `load_reviewed_qc()` reconciliation succeeds for all 346 queued entries and 160 trials. Independent export-to-ledger/source-decision comparison checked every component eligibility and every exported reviewed status/reason. It verified `E2:Subj_E:Rm_018` carries the uncertain timebase reason, `E1:Subj_B:Rm_010` has HR eligible and RMSSD ineligible, and all 49 HR-only trials preserve that distinction. Existing numerical eligibility decisions are retained. Methods' 22 settings were read against unchanged approved settings wiring; its decision counts match the integrated ledger, ten sensitivity rows exactly equal the existing affect export, and all six canonical referenced files exist.

Current artifact loading succeeds with backend code-tree hash `e4e4e8ebd2ab891945769a0d91d18070f0b9f6803fabc3d79132ac375b161a7d`. All 23 E3 training rows predict the same exact point `[0.19933647676353913, -0.07416070665631107]`. A real FastAPI application lifespan returns HTTP 200 and `ready=true` for health and `baseline_only` for metadata. All 1,000 null identities and the 455 unique learning subsets remain complete; the current reconstructed effective-input guard equals the stored guard. All eight comparison source digests, seven public manifest hashes, 28 strict catalogue schemas and canonical paths were independently checked. These checks do not perform new null draws or new learning fits.

Read-only reviewer scratch command, exit 0:

```text
PYTHONPATH=backend/src backend/.venv/bin/python /tmp/tadj-cpc-rework-check.py
# strict 53-path comparison; unchanged scientific bytes and old trial fields
# 160 QC records;49 HR-only trials;loader/API readiness;23 constant predictions
# exact effective guard;8 comparison digests;7 public manifest hashes;28 schemas
```

The temporary script and `/tmp/tadj-cpc-rework-evidence.json` are reviewer scratch evidence, not maintained pipeline entry points. [CP-C's dated hash table](CP-C.md#rework-receipt--2026-10-10t160842z) records 19 exact reviewed files and canonical catalogue digest `f638e143185965f6d61914791cfcc81ca58c2bbd1157657220ed6681c4089d3b`. The Methods extension accounts for the catalogue-content digest change; it is not scientific drift or an unchanged full manifest claim.

The actual isolated run's exit code, run log, full `make all` log and 150-file source manifest were inspected. Every recorded source input still matches the immutable original clone at `/tmp/pa-final-repro-run-1y3bl3n6/reproduction/clean-clone`. Snapshot `a4f4850f77e6f6d5eb3d1d0634e0a602f89650f9`, input digest `936cd86add14e0406dc563d97a5d536a41b5d33b036b5008f3bb4b245d2dcc93`, reconstructed CP-B bytes, matching pre-draw guard and logs establish the completed 1,000-fresh-draw/455-subset scientific reproduction. The run passed in 7,672.0 seconds. Scientific records match the current result exactly after declared timing normalization. This closes the earlier receipt's then-pending clean scientific reproduction; it does **not** authenticate the changed current source as the original 150-input snapshot or claim another full rerun after rework.

**Boundary:** no unresolved finding in this scoped receipt. Final-source delta validation, current browser/CP-E2 evidence and independent formal review remain separate. Model status and limitations remain baseline-only. Only CP-C and this supplemental review were edited for this receipt; no source/artifact, task checkbox or stage transition was changed.

## Card-only supplement — 2026-10-10T16:17:53Z

**PASS; existing qualified disposition retained.** After the 16:08 artifact receipt, the release worker appended one provenance paragraph to the model card and one QC-evidence paragraph to the data card. This reviewer inspected both exact diffs against the original clean clone and independently counted all six public QC components: 33 trials have a review downgrade and 49 have eligible HR with ineligible RMSSD. Both named examples and the unchanged-science account agree with the earlier checks. The [CP-C card supplement](CP-C.md#card-only-supplement--2026-10-10t161753z) records the two new exact hashes; all 17 scientific/product hashes from the prior receipt still match. No scientific input, artifact or visual site content changed in this card-only supplement.
