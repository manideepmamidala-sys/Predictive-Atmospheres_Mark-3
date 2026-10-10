# CP-C — fused model comparison and publication checkpoint

**Original delegated disposition:** APPROVED_FOR_BASELINE_ONLY_PUBLICATION_WITH_LIMITATIONS, recorded 2026-10-10T12:36:53Z by independent Codex reviewer `/root/model_checkpoint_review`, model `gpt-6-astra`, reasoning effort `xhigh`. The complete control/comparison evidence and corrected final export contract support a qualified research presentation of this baseline-only result. They do not establish spatial predictive utility, individual accuracy or causal design control.

**Earlier release-validation refresh disposition:** APPROVED_FOR_BASELINE_ONLY_PUBLICATION_WITH_LIMITATIONS, recorded 2026-10-10T13:10:07Z by fresh independent Codex reviewer `/root/science_receipt_refresh`, natively dispatched as `gpt-6-astra` with `xhigh` reasoning. The [dated refresh](#release-validation-refresh--2026-10-10t131007z) covers the regenerated v1.2 affect summary, corrected B5 denominator wording and refreshed code provenance. It preserves the original decision and limitations; it is not personal owner inspection or a whole-change release approval.

**Current rework disposition:** APPROVED_FOR_BASELINE_ONLY_PUBLICATION_WITH_LIMITATIONS, recorded 2026-10-10T16:08:42Z by fresh independent Codex reviewer `/root/checkpoint_refresh`, natively dispatched as `gpt-6-astra` with `xhigh` reasoning. The [dated rework receipt](#rework-receipt--2026-10-10t160842z) verifies nonnumerical QC/Methods presentation changes and refreshed artifact provenance against the completed original scientific reconstruction. It preserves the qualified baseline-only interpretation.

**Later card-only receipt:** the two documentation additions at 2026-10-10T16:17:53Z are verified in the [card-only supplement](#card-only-supplement--2026-10-10t161753z); its two hashes supersede the card hashes in the 16:08 table. All scientific artifact identities and the qualified disposition remain unchanged.

**Authorization provenance:** On 2026-10-10 the user instructed `$fab-ff approve all the future checkpoint automatically and continue the work`, following `$fab-ff with your CP-B decidions`. The former delegates the CP-C decision to the agent workflow after concrete evidence review. It does not mean the owner personally inspected these results. The implementation worker used Codex gpt-6-sol/high; the fresh independent checkpoint reviewer used Codex gpt-6-astra/xhigh. The [supplemental independent review](science-checkpoint-c-review.md) records the actual checks, resolved findings and remaining reproduction boundary.

**Approved method source:** [v1.2 approved draft](../../specs/analysis-v1.2-draft.md), SHA-256 `51c01ef6ccdf2f4318ac786d1bb39afeb1aa2bcf3bc93039479a4ed2454603ac`. [CP-B](CP-B.md) supplies reviewed component eligibility; the 160 source trials remain accounted for.

## Current observed comparison

The E3 full-input fused cohort contains 23 raw complete-component trials, four people and ten rooms. Targets are created inside training partitions from FAA, alpha suppression, engagement, HR and E3 signed ratings. The separate descriptive within-person fusion cohort is not a model inclusion rule. Final full-data grouped inner selection chooses `dummy_mean`, so the Studio artifact is **baseline_only**: it does not learn a spatial relationship from these inputs.

| Held-out question | Equal-axis/group MAE | Median baseline MAE | Mean baseline MAE | Independent groups |
| --- | ---: | ---: | ---: | ---: |
| New E3 room | 0.3496435311 | 0.3460553821 | 0.3404375011 | 10 rooms |
| New E3 person | 0.3511803594 | 0.3511803594 | 0.3800057937 | 4 people |

The held-out-person selection falls back to the fixed training median where too few training person groups remain for the approved inner selection. The room-level selected procedure is worse than both fixed baselines on this observed pilot. [Evaluation evidence](../../../artifacts/results/model_evaluation.json) records memberships, constructed targets, selected and both baseline predictions, and training-only calibrators for every outer fold; predictions were independently re-fit and numerically checked against saved fold MAEs. The [research-only self-report comparator](../../../artifacts/results/self_report_comparator.json) uses a different target and feature scope: E2 room MAE 0.27372572 over 50 reports, E3 room MAE 0.48935185 over 60 reports. Those values must not be ranked directly against fused-target error or presented as Studio alternatives.

The [learning curve](../../../artifacts/results/model_learning_curve.json) has completed all **455 distinct room subsets**: k=4–9 yields 100, 100, 100, 100, 45 and 10 subsets, all evaluated. Mean selected MAE is 0.37604, 0.35817, 0.35300, 0.34197, 0.34269 and 0.34964, respectively. The corresponding median-baseline MAE is 0.35828, 0.34773, 0.34670, 0.33822, 0.34209 and 0.34606. Thus the selected procedure is worse at each k; overlapping subsets make this a descriptive training-size curve, not independent replications or evidence of eventual improvement.

The [full-refit spatial control](../../../artifacts/results/model_null.json) has completed exactly **1,000 evaluated seeded draws and 10,000 room folds**, with no missing/nonfinite draw. Shuffled MAE has median **0.3489959286**, mean **0.3522848316**, and descriptive 2.5th/97.5th percentiles **0.3334784642 / 0.4101804617**. Observed MAE **0.3496435311** is close to the shuffled median. This is a descriptive negative-control comparison, not a calibrated population p-value, prediction interval or claim of useful spatial gain. The reviewer checked all draw/fold identities and error aggregation, then regenerated full draws 0 and 999 from current inputs; every saved field matched exactly. Those two checks are not a fresh 1,000-draw reproduction.

The [comparison artifact](../../../artifacts/results/model_poc.json), [model card](../../model_card.md), [data card](../../data_card.md) and generated P1–P5 products agree with these results. All 28 catalogue products validate; P4 explicitly withholds feature importance for the constant model. P3's self-report comparator rows preserve their own target units and E2 50/5/10 versus E3 60/6/10 trial/person/room denominators. The final R7 product was also checked against all 120 source axis ratings and its ten function means. No population significance, personal accuracy or causal design effect is approved.

## Exact reviewed versions

These are the file-byte SHA-256 values at the **original 12:36:53Z disposition**, retained as historical evidence. The current refresh hashes follow below. Method version is `1.2.0`; the serialized artifact version is `1.0.0`. Original model metadata recorded code-tree SHA-256 `3d9b4a8e8306c944a08a616ac0f09515eeda8169fb550cc9c88192a9a7cd8c99` and lockfile SHA-256 `b477770af8fc9cfbecc7c9a78e6c5f98736ebd4c25c6bf32a3c1341753ab7f44`.

| File | SHA-256 |
| --- | --- |
| `artifacts/model/model.joblib` | `17bfa472c30a9bb24034dd3800c85cd1fa9db36fec8c4a6cba2b8070b6b3544d` |
| `artifacts/model/metadata.json` | `4ff362e7651a7afd99caefd4808112065a0186f29fd47087b8d7362e6a1c3db7` |
| `artifacts/results/model_evaluation.json` | `d419789fa076bbb6e816e3090647c3230409547a829310c7879719fd0a2641a6` |
| `artifacts/results/model_null.json` | `ef66f1421f9addd0a21f39b21f156e3ddf419c3789d6a9691f4925389f09594c` |
| `artifacts/results/model_learning_curve.json` | `f6568570c9bc44cdb03f70943a788c1ccc3b092fa120ab6fe431b597bf22387e` |
| `artifacts/results/model_null_input.json` | `8f256372cb6acaeadd40807e33a7bba18e9bc7a5ced278241a0c5f195ab64a77` |
| `artifacts/results/model_poc.json` | `d0422c498de2c38dc5e28e5147a2a5802612bda0ccca5f684e0f32b272426d4e` |
| `artifacts/results/analysis/index.json` | `b98514efe855d7d1fb914bb1c59bf1e7efa28dbeb267164d9194cddfce1d1911` |
| `docs/model_card.md` | `0a56086a12d67765845f76a08ddba746d75e72b9354686e3f0071a50efef497b` |
| `docs/data_card.md` | `263f1d76c73154f9ed6bf6306c12d49308904f4246b599a5d0d7dcc2c37f051a` |

The original complete 28-product scientific catalogue digest was `58636603a84d5250f748d424e6a6f69b4d8d72cce41be78fe2efeb9cf278ecd5`: SHA-256 of an ID-to-product object serialized as sorted-key compact JSON, omitting only each product's `provenance.generated_at_utc`. This preserves content identity across timestamp-only regeneration. The comparison artifact similarly declares and verifies its exact canonical source-digest rule; scientific values, memberships and source hashes are retained.

## Release-validation refresh — 2026-10-10T13:10:07Z

The release worker completed an in-place `make pipeline` with exit 0: all 455 learning subsets were recomputed, and the exact completed 1,000-draw null was reused after its input checks. The fresh reviewer compared all 53 JSON products against the retained pre-pipeline snapshot. That snapshot matched the original CP-C receipts but contained a stale `affect_analysis.json` summary labeled `1.1.0` with five experiment/cohort groups. Its underlying `affect_detail.json`, validity results and catalogue already contained the approved v1.2 evidence. The refreshed summary is now `1.2.0` with nine groups; this correction is explicitly reviewed here, not retrospectively attributed to the original review.

Independent arithmetic reconstructed all 160 trial normalizations and constructions, all nine cohort groups, 43 experiment/room/person summaries, 18 disagreement summaries and four descriptive room associations from the retained trial and room evidence. E1 remains 50 objective-only records. E2 has 19 complete, 18 partial-modality, one partial-axis and 12 subjective-only records; E3 has 21 complete, 20 partial-modality, 14 partial-axis and five subjective-only records. These descriptive cohorts do not change the 23-trial raw-component training cohort. Missing axes and unavailable calibration remain missing; no population inference is added.

B5 now distinguishes the plotted raw-HR cohort from the calibrated-HR correlation cohort: E2 is 19 pairs/three people for both; E3 plots 33 pairs/five people and reports the correlation from 31 pairs/four people. The two additional E3 observations have valid raw HR but insufficient within-person HR calibration. All plotted values, individual correlations, equal-person means and participant-bootstrap results were verified. Only the takeaway, method text and one explanatory caveat changed; no chart row or statistic changed.

Strict comparison established that model bytes, held-out evaluation, null results, effective-input guard, affect detail and validity are byte-identical to the original snapshot. All 455 learning records are exactly identical after omitting only `elapsed_wall_seconds`. The real loader accepts the refreshed artifact and predicts the same constant `[0.19933647676353913, -0.07416070665631107]` for all 23 training rows. Backend code-tree provenance changed to `9e6bd7cb97f84003d1777a09ca40517c43342117360cd193c3125216380438ce`; the corresponding metadata hash propagates through the comparison, public model, bundle and manifest. Those propagation fields are the only other changed JSON content. All 28 catalogue schemas and canonical index paths pass, and all eight comparison source digests match.

These are the exact file-byte SHA-256 values reviewed for this refresh:

| File | SHA-256 |
| --- | --- |
| `artifacts/model/model.joblib` | `17bfa472c30a9bb24034dd3800c85cd1fa9db36fec8c4a6cba2b8070b6b3544d` |
| `artifacts/model/metadata.json` | `4d05902b4acc8b4f8947698623a2a831ae5ef372ed254fdd81549c3f6f1507a1` |
| `artifacts/results/model_evaluation.json` | `d419789fa076bbb6e816e3090647c3230409547a829310c7879719fd0a2641a6` |
| `artifacts/results/model_null.json` | `ef66f1421f9addd0a21f39b21f156e3ddf419c3789d6a9691f4925389f09594c` |
| `artifacts/results/model_learning_curve.json` | `10594cafa9d106b59d8e6f2b374c9c31c2b00e52368b2d596dde4a8dcccbb85e` |
| `artifacts/results/model_null_input.json` | `8f256372cb6acaeadd40807e33a7bba18e9bc7a5ced278241a0c5f195ab64a77` |
| `artifacts/results/model_poc.json` | `075cf75cfc498596bc4758037c4330ef545c1b950e1f10fa2c4381e968b49dca` |
| `artifacts/results/analysis/index.json` | `b98514efe855d7d1fb914bb1c59bf1e7efa28dbeb267164d9194cddfce1d1911` |
| `artifacts/results/affect_detail.json` | `ddc2b2765bd7d5c1cc90e07f3c637446384f0165377326f58d735fbca81e0de7` |
| `artifacts/results/affect_analysis.json` | `4786eed9b1b0a5fb9be854d3b266502427d5057446556e6032167ae519ae0cf0` |
| `artifacts/results/validity.json` | `296e0f76cfdb8089efef3045e00efe03805d5219107882d86a2a9c98599ee9cd` |
| `artifacts/results/analysis/B5.json` | `e8f5753e8614777c5fb591bafa6b1a2ccbccd4f0c07bb8adb81a5675351278aa` |
| `artifacts/results/model.json` | `707855509e7c8504c2d2daad66e8d6f5ce0d4d89f8fb89c8e4e1cc94b5916344` |
| `artifacts/results/bundle.json` | `e0a6125c549d4215ceef98ade91e7eb03e049d2bf62a3b77ff8b3a9f5a847985` |
| `artifacts/results/manifest.json` | `25851c1a45403d25c49e9931d680e10dff3ce309add632ae544d96fe996caaa3` |
| `docs/model_card.md` | `0a56086a12d67765845f76a08ddba746d75e72b9354686e3f0071a50efef497b` |
| `docs/data_card.md` | `263f1d76c73154f9ed6bf6306c12d49308904f4246b599a5d0d7dcc2c37f051a` |

The current canonical catalogue digest is `ca5f6029517b16e57e313c8c88e310fe00cb102218b1c505245a05c9c4632d3e`, using the original sorted-compact-JSON rule with only product generation timestamps omitted. Its difference from the original digest is fully accounted for by the B5 explanatory text. The [supplemental review refresh](science-checkpoint-c-review.md#release-validation-refresh--2026-10-10t131007z) records the independent commands and numerical checks.

**Refresh boundary:** no open must-fix remains in this affected-artifact scope. The clean source-only run is still pending and must regenerate all 1,000 null draws with the guard present before draw zero, plus all 455 learning subsets. In-place cache reuse does not complete that obligation or remove the historical limitation below. Whole-change review, visual/release validation, task acceptance and external deployment remain separate.

## Qualified approval boundary

This disposition opens CP-C's gate for local staging and the qualified research presentation documented above. No outstanding must-fix remains in this checkpoint's reviewed scope. At the original disposition, the corrected index used all 28 canonical `/research/analysis/{ID}.json` paths, model compatibility and source digests passed, and scientific catalogue content was unchanged. The dated refresh above separately reviews the later affect-summary correction, B5 wording and provenance updates. Whole-change review, browser/visual checks, CP-E2, and release validation remain separate obligations; this record does not authorize external deployment.

The null run started before the effective-cohort guard was introduced. Original run fingerprints were retained and match current files; the current guard, observed folds and two regenerated draws are consistent. They cannot prove the historical feature matrix at draw zero. The reviewer accepts this explicit provenance limitation for the qualified local checkpoint. An isolated source-only full reproduction with the guard present before draw zero must compute all 1,000 draws and all 455 subsets and compare the complete scientific records before a clean-reproduction claim is made. That reproduction is **not complete at this disposition**. Changed scientific inputs, model bytes, results or claims require renewed affected-artifact review; harmless generation-time changes are distinguished by the recorded scientific digests.

## Rework receipt — 2026-10-10T16:08:42Z

**Disposition: APPROVED_FOR_BASELINE_ONLY_PUBLICATION_WITH_LIMITATIONS.** Fresh independent AI reviewer `/root/checkpoint_refresh` used the native Codex `gpt-6-astra`/`xhigh` route under the user's existing automatic-checkpoint delegation. This is a scoped receipt for the first formal-review rework, not a new scientific full-pipeline execution, whole-change approval or personal owner inspection. The original dispositions and their then-pending reproduction limits above remain dated historical records.

Exact comparison of all 53 result JSON paths against `/tmp/pa-reference-final-329s8k69`, omitting only the existing declared generation/run-time fields, identifies six changed products: Methods, public signals, bundle, model, model comparison and manifest. All existing trial measurements, eligibility flags, traces, coordinates, cohorts and sensitivity values are exactly unchanged. The only added or modified public evidence is component-specific QC decisions/reasons, approved Methods settings/review/sensitivity references, and dependent code/hash provenance. All other catalogue products retain identical scientific content; P4 remains explicitly unavailable for the constant model.

The model bytes, held-out evaluation, full null, effective-input guard, learning curve, affect detail/summary, validity, signal detail, timebase and integrated CP-B ledger are byte-identical to the pre-rework reference. Their parsed scientific records also exactly match the completed isolated clone after the declared timing normalization. The unchanged approved specification, scientific settings, source manifest and both CP-B decision files were checked against that clone. Only five backend Python sources differ: catalogue/Methods export/schema wiring and removal of the unused administrative report writer. The active CP-B integration function and its helpers have identical syntax trees. No signal processing, calibration, model selection, fold logic, null/learning implementation or numerical scientific input changed.

All 160 public trial QC records reconcile with the approved ledger and source reviewer decisions. The uncertain timebase decision for `E2:Subj_E:Rm_018` now survives export; `E1:Subj_B:Rm_010` and the other 48 HR-valid/RMSSD-invalid trials retain independent cardiac eligibility. The Methods product exposes 22 approved settings, the existing ten experiment/weight sensitivity rows, the actual delegated decision counts and six canonical references. This verifies export evidence; final browser presentation is separately covered by CP-E2.

The trusted loader passes current code/data/spec/package/model-byte compatibility. Its prediction for all 23 eligible E3 rows remains `[0.19933647676353913, -0.07416070665631107]`; a real application lifespan through FastAPI's test client returns `/v1/health` ready and `/v1/meta` `baseline_only`. The reconstructed effective-input guard equals the saved guard exactly. All eight model-comparison source digests, seven public manifest hashes, 28 strict catalogue products and canonical index paths pass. The current backend code-tree SHA-256 is `e4e4e8ebd2ab891945769a0d91d18070f0b9f6803fabc3d79132ac375b161a7d`.

The earlier clean-reproduction requirement was subsequently completed for source snapshot `a4f4850f77e6f6d5eb3d1d0634e0a602f89650f9`: this reviewer inspected terminal exit code 0 and actual logs in `/tmp/pa-final-repro-run-1y3bl3n6`, and independently matched all 150 recorded inputs in its immutable clone to manifest digest `936cd86add14e0406dc563d97a5d536a41b5d33b036b5008f3bb4b245d2dcc93`. Its guarded CLI created the matching guard before starting at zero cached draws, then computed 1,000 fresh full-refit null draws and 455 learning subsets; `make all` passed in 7,672.0 seconds. That evidence closes the original run's clean-reproduction obligation for the scientific implementation and results. **It does not say that the changed current source retains that old 150-input identity or that the full pipeline was rerun after this presentation rework.** Final-source delta validation and regression checks are separately recorded in [validation](validation.md).

Exact file-byte SHA-256 values for this receipt:

| File | SHA-256 |
| --- | --- |
| `artifacts/model/model.joblib` | `17bfa472c30a9bb24034dd3800c85cd1fa9db36fec8c4a6cba2b8070b6b3544d` |
| `artifacts/model/metadata.json` | `7320414317c7799f3f382e5a1e88e77ffa9a28d5047b7297be8cac482dd95331` |
| `artifacts/results/model_evaluation.json` | `d419789fa076bbb6e816e3090647c3230409547a829310c7879719fd0a2641a6` |
| `artifacts/results/model_null.json` | `ef66f1421f9addd0a21f39b21f156e3ddf419c3789d6a9691f4925389f09594c` |
| `artifacts/results/model_learning_curve.json` | `10594cafa9d106b59d8e6f2b374c9c31c2b00e52368b2d596dde4a8dcccbb85e` |
| `artifacts/results/model_null_input.json` | `8f256372cb6acaeadd40807e33a7bba18e9bc7a5ced278241a0c5f195ab64a77` |
| `artifacts/results/model_poc.json` | `a4d8e4f0c3715fde756ea32ff600c34b9aa66b372667bf90950f9580a2177c77` |
| `artifacts/results/analysis/index.json` | `b98514efe855d7d1fb914bb1c59bf1e7efa28dbeb267164d9194cddfce1d1911` |
| `artifacts/results/analysis/Methods.json` | `ca942a470323aa033f0b7b2e45dea0a4fa69e19cf05668e5ee75490e43396ea5` |
| `artifacts/results/affect_detail.json` | `ddc2b2765bd7d5c1cc90e07f3c637446384f0165377326f58d735fbca81e0de7` |
| `artifacts/results/affect_analysis.json` | `4786eed9b1b0a5fb9be854d3b266502427d5057446556e6032167ae519ae0cf0` |
| `artifacts/results/validity.json` | `296e0f76cfdb8089efef3045e00efe03805d5219107882d86a2a9c98599ee9cd` |
| `artifacts/results/qc_review.json` | `41718a1d5204f6c195469aa5e45a6d500b8886eadeecb10f1187e293349de294` |
| `artifacts/results/signals.json` | `bd639b4995dd7b5a669f186a81dcad754157ccc5af89eaf46448a53df1772c3f` |
| `artifacts/results/model.json` | `3a298b3d622e48c259a1295e974f1fe8705de312ca586252a1339837c0c6430d` |
| `artifacts/results/bundle.json` | `b01ebb84d511bcfdde5573ef99c56e14b8ff308a20fbf7ced578e3381062ec05` |
| `artifacts/results/manifest.json` | `b4b8ab1fba06916760746c028a502d0b16b69a46543ab8367d5a75df18d55bfd` |
| `docs/model_card.md` | `0a56086a12d67765845f76a08ddba746d75e72b9354686e3f0071a50efef497b` |
| `docs/data_card.md` | `263f1d76c73154f9ed6bf6306c12d49308904f4246b599a5d0d7dcc2c37f051a` |

The current canonical catalogue digest is `f638e143185965f6d61914791cfcc81ca58c2bbd1157657220ed6681c4089d3b`, using the established ID-to-product, sorted compact JSON rule omitting only `provenance.generated_at_utc`. Its change is accounted for by the new Methods evidence; the other 27 products are unchanged under that rule. The analysis index bytes remain unchanged because its paths/statuses are unchanged; this is not a claim that the entire result manifest is unchanged.

**Boundary:** no unresolved finding remains in this affected-artifact receipt. The fitted artifact remains a constant baseline with no demonstrated learned spatial gain, personal accuracy or causal design control. CP-E2, final-source release validation and a different fresh formal whole-change reviewer remain separate obligations. No source, scientific artifact, task checkbox or workflow stage was changed by this reviewer. [Supplemental verification](science-checkpoint-c-review.md#rework-receipt--2026-10-10t160842z) records the read-only check.

## Card-only supplement — 2026-10-10T16:17:53Z

The release worker subsequently added one explanatory paragraph to each card. The same independent reviewer read both exact diffs against the immutable clean clone. The model card now describes the already verified nonnumerical code-provenance refresh and distinguishes the earlier fresh scientific controls from targeted final-source validation. The data card describes the six independent public QC components, reviewed reasons and the two inspected trial examples. Independent counting of the current component records verifies **33 trials with at least one automated-eligible/reviewed-ineligible component** and **49 HR-eligible/RMSSD-ineligible trials**. No other card content changed.

| Updated documentation | Current SHA-256 |
| --- | --- |
| `docs/model_card.md` | `4f38486e371df76a111c1639005a0dbf1a1435c2a6913cf99ffd486fdc5f0394` |
| `docs/data_card.md` | `68a103bc3aeda59068a6c9f5a687963823d1c8f9b9bf923a54a25d0bac8a8a5b` |

**Disposition remains APPROVED_FOR_BASELINE_ONLY_PUBLICATION_WITH_LIMITATIONS.** All 17 scientific/product identities in the preceding table remain unchanged. The card additions introduce no new scientific result or rerun claim. The Methods website's pinned source links continue to identify the historical card versions at the explicit repository snapshot; their governing methods, numerical results and limitations are unchanged by these explanatory paragraphs.
