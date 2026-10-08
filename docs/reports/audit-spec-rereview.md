# Independent pre-results checkpoint re-review

Date: 2026-10-08. Change: `261008-ymhz-research-platform-rebuild`. Checkpoint: **T007**, analysis specification **v1.1.0**.

**Checkpoint verdict: PASS. No must-fix methodology findings remain.** The amendments close the three prior method blockers and the three prior should-fix findings. This is a defensible, explicitly conditional retrospective analysis contract. It does not establish that accepted recordings are artifact-free, validate constructed affect, accept unfinished implementation tasks, or replace the final Fab review. The coordinator owns the recorded gate verdict and continuation.

Routing: fresh native Codex worker, `gpt-6-astra` / `xhigh`, explicitly selected through the native dispatch options. The coordinator supplied the matching verified Fab resolution (`provider: codex`, `model: gpt-6-astra`, `effort: xhigh`, empty `model_alias`, no `dispatch` key). This worker made no substitution or further delegation. Only this report was written; no task, acceptance, Fab state, commit, or scientific-result generation action was performed.

## Disposition of the previous findings

| Prior finding | Disposition and evidence |
| --- | --- |
| M1: sustained EEG clipping | **Resolved.** `docs/specs/analysis-v1.md:21`, `backend/src/pa/decisions.yaml:10`, and `backend/src/pa/signals/qc.py:12` define a raw repeated-extrema screen with explicit thresholds and sensitivity. QC precedes filtering; accepted epochs are filtered separately; gaps reject epochs; persistent contamination and visual-review limits are explicit at specification line 23. The original clipped-sinus failure is rejected at all four candidate rates. D-007 preserves the supersession rationale. |
| M2: ECG quality, gaps, and usable duration | **Resolved.** Specification lines 27–33 and machine settings define block rejection, segment filtering, prominence, morphology, polarity, local interval checks, contiguous runs, and complete 10/20/30-second coverage/count rules. `backend/src/pa/signals/ecg.py:183` retains segment boundaries, both candidate peak sets and morphology evidence; lines 222 and 248 preserve continuity and choose qualifying runs. Gaussian noise no longer yields nominal physiology; fragmented coverage does not qualify as a continuous 30-second run. D-008 records the amendment. |
| M3: nested selection and calibration | **Resolved as a method contract.** Specification lines 39 and 45–49 plus `decisions.yaml:53` freeze median/MAD calibration, degeneracy, grouping, candidate configurations, group/axis weighting, simplicity order, low-group fallback, and full-data artifact selection independently of outer scores. `backend/src/pa/modeling/evaluate.py:89` refits target construction inside each inner-training fold and line 103 fits each feature pipeline there. Mutation probes and independent unequal-group scoring confirm these essential protections. Remaining T014 completion items below do not reopen the choice of method. D-009 records the contract. |
| Should-fix 1: 50 Hz wording/order | **Resolved.** Specification line 19 correctly describes attenuation and the order-eight band-pass produced by the order-four prototype. Independent frequency-response calculation gives **10.969286 dB** forward/backward attenuation at 50 Hz, consistent with the text. Residual spectral inspection is required. |
| Should-fix 2: SHA-manifest verification | **Resolved.** `backend/src/pa/io/manifest.py:30` verifies exact manifest/inventory agreement, rejects missing/malformed/duplicate entries, and checks retained source/destination bytes. Missing or mismatched manifest tests pass. The preservation rule accepts a checksum-equivalent migrated destination when the original path has been retired, and checks every copy that remains; it does not require both paths to exist forever. `pa verify-data` succeeds on the current tree. |
| Should-fix 3: shared audit settings | **Resolved.** `backend/src/pa/io/audit.py:28`, line 50, and line 106 read versioned thresholds/rates and identify the primary scenario by rate. The audit records the settings version. Its remaining textual references to historical near-500 evidence are evidence descriptions, not independently hardcoded processing settings. The setting-mutation test passes. |

The specified filters and peak primitives agree with the [SciPy Butterworth documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.butter.html) and [peak-finding documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.find_peaks.html). Those primitives do not validate the selected QC thresholds or prove that numerical peaks are cardiac beats. The separate training, validation and outer-test transformations implement the principle in [scikit-learn's leakage guidance](https://scikit-learn.org/stable/common_pitfalls.html); the untouched outer evaluations assess the selection procedure as described in its [nested evaluation example](https://scikit-learn.org/stable/auto_examples/model_selection/plot_nested_cross_validation_iris.html).

## Prioritized downstream implementation observations

These are concrete corrections for the still-unfinished T014 implementation, not new scientific-method decisions or blockers to T007. They should be addressed before real model comparisons are accepted. The checkpoint pass must not be used to mark T014 or its acceptance criteria complete.

1. **Preserve nonfinite component invalidity before `tanh`.** At `backend/src/pa/modeling/targets.py:56`, non-RMSSD components are transformed without first masking/rejecting infinity. `tanh(inf)` is finite, so the later check at line 73 misses the invalid input. A synthetic held-out row with `faa=inf` and valence report zero produced fused valence **0.5** instead of an unavailable target. Reject or mask nonfinite raw components before mapping, and cover both signs of infinity across the component columns. The reviewed signal paths reject nonfinite recordings; this probe demonstrates an unchecked target-construction boundary, not evidence of an affected participant result.
2. **Implement ties relative to the global minimum.** At `backend/src/pa/modeling/splits.py:35`, the running incumbent can skip a simpler candidate that lies within tolerance of the eventual minimum. Scores `median=0.2`, `mean=0.1999995`, `Ridge(10)=0.1999988` select Ridge, although the mean baseline is within `1e-6` of the minimum and precedes Ridge in the specified simplicity order. Find the finite minimum first, then take the first ordered candidate within its tolerance. Add this chained-near-tie case. This is a deterministic, very small tolerance-boundary defect; the candidate set, objective and intended tie policy are already frozen.

Ordinary T014/T015 completion also still includes both outer baseline reports, retained selection/exclusion evidence, the final full-data fitting path, artifact metadata and actual eligible-cohort evaluations. For example, `backend/src/pa/modeling/evaluate.py:135` currently exports only the median baseline comparison. These are implementation deliverables explicitly left incomplete by the plan, not grounds to fail a pre-implementation method checkpoint.

## Reproduced checks and synthetic evidence

The following command ran successfully in `backend/`:

```text
uv run --frozen ruff check src tests && uv run --frozen pytest -q && uv run --frozen pa verify-data
All checks passed!
40 passed, 1 warning in 29.76s
Source inventory verified
```

The warning was the existing Starlette TestClient/httpx deprecation. Additional independently constructed inline Python probes used the frozen environment and synthetic data only:

| Probe | Observed result |
| --- | --- |
| EEG known bands at 250/256/500/512 Hz | For 24-second right `2 sin(2π10t)+0.5 sin(2π20t)` and left `sin(2π10t)+0.5 sin(2π20t)`, all six epochs passed; maximum absolute asymmetry error from `log(4)` was **3.05×10⁻⁸**. Right alpha power was approximately **2** and beta power **0.12485–0.12493**, as expected for these synthetic amplitudes after filtering. |
| Sustained EEG clipping | `clip(100 sin(2π10t), -1, 1)` was rejected in **6/6 epochs at every candidate rate**. Repository tests separately cover an isolated spike, flat input and a counter jump at an epoch boundary. |
| ECG known timing/polarity | Gaussian pulses of width 0.012 s with alternating 0.8/0.9 s intervals recovered **70.588235 bpm**, **100 ms RMSSD**, and **30.6 seconds** usable interval coverage. The repository inversion test passed. |
| Noise-only ECG | All **30** Gaussian-noise seeds 0–29, each 36 seconds at 500 Hz, were rejected for HR and RMSSD. This is a finite adverse test set, not proof against all artifact families. |
| ECG counter fragmentation | Counter jumps every 6, 12 or 18 seconds split the 36-second synthetic recording into 6, 3 or 2 segments. Primary RMSSD was unavailable in every case. Six-second segments also failed both shorter scenarios; 12/18-second segments supported only the 10-second scenario. Stored peak indices remained inside their recorded segment bounds. |
| ECG dropout and usable-duration rules | Two-second flat blocks at either zero or a high constant level broke primary coverage. Repository tests independently show that a 36-second file with less than 30 seconds of accepted intervals cannot produce primary RMSSD. |
| Inner-validation mutation | Instrumented all **nine** candidate pipelines. Changing one inner-validation fold's features, raw components and reports left that fold's fitted component calibration, training targets, and numeric scaler means unchanged for all nine candidates. Other folds may legitimately use those records for training. |
| Unequal validation-group sizes | With group sizes **2, 3, 4, 5, 6**, manually recomputed equal-group/equal-axis median-baseline MAE was **0.2594918271117355**, exactly matching selection output. |
| Outer-held-out mutation | The repository nested-selection test passed: changing held-out features/components/reports leaves outer-training selection and training membership unchanged. |

The two adverse target/tie probes above are deliberately reported despite the passing suite. A green suite does not establish completion of T014.

## Limits and subsequent evidence

The reviewed choices are operational screens and descriptive hypotheses. Raw-unit uncertainty, unknown acquisition filtering/reference, approximate electrode placement, motion/ocular/muscle contamination, short ECG, rate uncertainty, crossed room/participant dependence and differing rating elicitation remain real limitations. Exact-extrema screening need not detect clipping subsequently smoothed by unknown acquisition processing; morphology consistency need not distinguish every repeated artifact from QRS. The specification acknowledges these boundaries and requires visual evidence rather than declaring automated acceptance to be physiological truth.

Before interpretation, complete the specified raw/cleaned trace, spectrum, peak and gap review; retain reviewed examples and unresolved contamination. Generate rate/onset/QC/duration/alpha sensitivities, cohort exclusions and unavailable outcomes as specified. No threshold may be relaxed in response to inconvenient eligibility or results without a dated amendment and affected rerun. No participant signal features, fused results, model comparisons or public scientific exports were generated by this reviewer. This report does not certify work outside the listed frozen files or any subsequently amended bytes.

## Reviewed snapshot

The following SHA-256 values were captured before substantive probes and checked again before this report was written. **All 15 frozen files were unchanged.** The suite also included concurrently added independent tests, accounting for its total of 40; passing those tests is not a full review of their modules.

```text
docs/specs/analysis-v1.md                 c176952a1a10fd14c49da32e061a06ca8fd9184eb0b2ad37d0c42f7ae9fb1ca7
backend/src/pa/decisions.yaml             b0231530f24632abf39fc803e006068b2fe71b3aa22bd207bc753e20a312b3e8
DECISIONS.md                              2b676d1fc15c3244fc7c3b2c4acdb17433b0cd18dee4bac950d7faa65e878a31
backend/src/pa/signals/qc.py              2322f7bbeae71568b928bac2a8b7bfbd21281ba9f2dfa9a2bc76f133da0d0f06
backend/src/pa/signals/eeg.py             84908fb61938429154b7ac427b1be51e09b4ec48d00f820f362d297f74f801f0
backend/src/pa/signals/ecg.py             031a7e113055d8aacec1e3d205c10050375e9e1945594cedfeda3782707925a1
backend/src/pa/modeling/targets.py        e004cbda5f09634d8eb056e69011656beef3fe8a5d0099dee8447f5ac9568f17
backend/src/pa/modeling/splits.py         e665ed9e077ce2a16b76d527b2f0a7b17828c50ea66d9bd63264af7140e9fbbb
backend/src/pa/modeling/evaluate.py       2433cf9fd221ca74fd2b56faa4d0b9683f4cf130af9f7cf3aa772c6f3b175627
backend/src/pa/io/manifest.py             236b741445b6c462b2d67ab7738c818c1d72802e9c643cc00a82456d1ed5e060
backend/src/pa/io/audit.py                1bab00db3f7b996a0d111dba86105623b285fa360bbc372810eec92c86d56702
backend/tests/test_eeg.py                 507e71b996daf1b392984cd3884094cca041d52ffa6e73b3e2bbb79a13b2c8a8
backend/tests/test_ecg.py                 399a9fff7beee15ac5c71b4721ccc1251bc4aca9354812fcf0bd3e9680af5dc7
backend/tests/test_evaluation.py          4624efe147bfed28c2ccee8471231ff41378632dd985eb770044d088865c52fc
backend/tests/test_manifest.py            31b6a7b77392ec90db741912e37a23f04d7185eca2800287846c1bccf917f4fd
```
