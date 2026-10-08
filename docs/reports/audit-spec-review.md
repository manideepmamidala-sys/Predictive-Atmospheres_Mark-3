# Independent acquisition audit and analysis-specification review

Date: 2026-10-08. Change: `261008-ymhz-research-platform-rebuild`. Checkpoint: T007, **before real signal, affect and model results**.

**Verdict: FAIL — three must-fix findings.** Source preservation, protocol provenance and the acquisition counts pass the checks below. The scientific method contract needs amendments before downstream real results are accepted. This verdict does not treat unfinished downstream tasks as failures and is not the final Fab review.

Routing: fresh native Codex review agent, explicitly dispatched as `gpt-6-astra` / `xhigh`. The coordinator supplied the verified Fab resolution (`provider: codex`, `model: gpt-6-astra`, `effort: xhigh`, empty `model_alias`, no `dispatch` key); this worker used that native route without substitution or further delegation. The review changed only this report and performed no Fab state, task or acceptance transitions.

## Must-fix findings

### M1 — Specify rejection of sustained clipping/saturation, not only relative epoch outliers

**Locations:** `docs/specs/analysis-v1.md:19`; `backend/src/pa/decisions.yaml:20`; requirement `fab/changes/261008-ymhz-research-platform-rebuild/plan.md:48`.

The EEG specification rejects constant channels and epochs with peak-to-peak or step values several times their recording's median. It supplies no saturation/clipping criterion. A consistently clipped recording is nonconstant and has ordinary values relative to its own equally clipped epochs, so these rules admit it. R8 explicitly requires saturated signals to be handled.

A supplemental synthetic probe of the in-progress implementation confirmed the consequence: 30 seconds at 500 Hz of `clip(100*sin(2*pi*10*t), -1, 1)`, on both channels with a normal modulo counter, has **96% of samples at the two rails** but returns `valid=True`, seven accepted epochs out of seven, and no reasons. This is not a result from any participant. The finding concerns the missing method rule; the concurrent signal implementation is not being given a final-review verdict.

**Required correction:** add a specified, raw-unit-compatible clipping/plateau rule, its rationale, threshold(s), sensitivity and explicit rejection reason. State the limitation that relative epoch thresholds cannot establish freedom from persistent motion, ocular or muscle contamination. Freeze whether QC is computed before filtering, the filtering/epoch boundary treatment, and which examples require visual review before interpretation. Include adverse synthetic coverage for repeated clipped waveforms as well as isolated spikes and known-band recovery. The [MNE epoch-quality example](https://mne.tools/stable/auto_examples/preprocessing/plot_epoch_quality.html) supports inspecting epoch outliers; it does not validate the current numerical thresholds or establish that sustained contamination is clean.

### M2 — Make ECG signal quality and usable interval duration enforceable

**Locations:** `docs/specs/analysis-v1.md:11`, `docs/specs/analysis-v1.md:23`; `backend/src/pa/decisions.yaml:24`. Supplemental implementation observations: `backend/src/pa/signals/ecg.py:36`, `backend/src/pa/signals/ecg.py:52`, `backend/src/pa/signals/ecg.py:75`, `backend/src/pa/signals/ecg.py:87`.

The specification says to reject noisy ECG and use morphology/regularity to choose polarity, but it does not define a signal-quality admission rule, prominence threshold, morphology criterion, polarity score/tie behavior, or local-median neighborhood. Minimum peak distance and plausible RR ranges are not sufficient evidence of cardiac beats. The specification also leaves counter-discontinuity treatment optional at line 11 and never defines how ECG intervals crossing a jump become invalid. Timing across such a jump is unverified.

The practical failure is reproducible without participant data: pure Gaussian noise, 30 seconds at 500 Hz using NumPy generator seeds 0, 1 and 2, was accepted for both HR and RMSSD. Seed 0 yielded **167.1309 bpm and 60.8470 ms**, with no rejection reasons. The current implementation also uses a global RR median despite the specified local rule, accepts total interval count rather than the required consecutive run, and has no counter input. These are corroborating observations of an unfinished implementation, not an assertion that T009 is complete.

The duration contract needs clarification independently of that code: a 30-second source file need not contain 30 seconds of usable intervals. Twenty consecutive intervals can cover much less than 30 seconds. Neither source duration nor the total number of accepted intervals defines the amount of valid adjacent-difference evidence used for RMSSD. Keeping a fixed minimum of twenty intervals during the 10-second sensitivity requires an average RR interval no longer than 0.5 seconds to fit those intervals within the segment; that interaction must be intentional and reported.

**Required correction:** freeze the detector/quality rules and parameters, explicitly reject intervals spanning acquisition discontinuities and prevent filtering across unverified gaps, define the local outlier window, and define valid runs/adjacent pairs and their duration. State whether RMSSD uses one qualifying contiguous segment or a justified aggregation of within-segment differences, with minimum usable coverage and failure reasons. Specify the 10/20/30-second scenarios completely. Retain raw RR/beat-quality evidence; label automated accepted intervals as an operational approximation to NN rather than established normal beats. Verify noise-only, clipped, dropout/gap and fragmented-run cases as well as known beat timing before using real outputs.

[SciPy `find_peaks`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.find_peaks.html) detects local maxima using requested properties; it does not establish their physiological identity. The cited [Munoz et al. study](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0138921) used resting finger-pressure interval recordings, visual artifact preprocessing and high-quality selected segments. The cited [Baek et al. study](https://pubmed.ncbi.nlm.nih.gov/25807067/) supports a 30-second RMSSD result in its own study, not an arbitrary 30-second file containing noise or sparse accepted beats. The specification correctly disclaims direct validation of this moving wrist-electrode protocol; the implementation contract must preserve that distinction.

### M3 — Finish the model-selection contract before model comparisons

**Locations:** `docs/specs/analysis-v1.md:29`, `docs/specs/analysis-v1.md:35`; `backend/src/pa/decisions.yaml:40`; requirement `fab/changes/261008-ymhz-research-platform-rebuild/plan.md:42`.

The broad leakage protections are correct: separate room and participant holdouts, training-only transforms, and no outer-fold winner selection. However, “small bounded RandomForest,” “where enough groups remain,” and “improve grouped MAE consistently” do not define a reproducible selection procedure. The settings contain candidate names, a seed and a minimum group count, but no candidate configurations/grids, scoring aggregation, tie rule, low-group fallback, or final artifact-selection procedure. The immediately preceding target-construction paragraph does not spell out population weighting/calibration or the inner-fold refitting sequence. These choices affect both the constructed target and which model is retained, so leaving them to implementation after this purported method gate defeats R7's pre-result parameter contract.

**Required correction:** record the bounded candidate settings, grouping and minimum eligibility for inner evaluation, per-axis/group scoring and aggregation, deterministic ties/baseline preference, and the unavailable or fixed-setting path when tuning is unsupported. Specify the exact population component transform and its degeneracy handling. Explicitly refit target and feature transforms on every inner-training partition, rather than constructing targets once on the entire outer-training set before inner validation. Define final full-data fitting/selection separately from untouched outer evaluation; outer performance may describe weakness without becoming an undeclared winner-selection step. Add the corresponding inner- and outer-held-out mutation checks to the downstream verification contract. No real model fit is required to resolve this specification finding.

This request applies the cited [training-only transformation guidance](https://scikit-learn.org/stable/common_pitfalls.html) and [nested evaluation guidance](https://scikit-learn.org/stable/auto_examples/model_selection/plot_nested_cross_validation_iris.html). It does not claim that leakage has already occurred or require a model to outperform a baseline.

## Should-fix findings

1. **Correct the line-frequency explanation.** `docs/specs/analysis-v1.md:19` says the 45 Hz low pass “excludes line frequency.” A Butterworth response attenuates rather than eliminates 50 Hz. A synthetic frequency-response calculation for `butter(4, [1,45], fs=500, btype="bandpass", output="sos")` gives forward/backward attenuation of **10.9693 dB at 50 Hz**, not exclusion. Describe the roll-off accurately and state how residual line contamination is inspected; this does not require adding a notch blindly. Clarify that the configured SciPy prototype order yields an eighth-order band-pass before forward/backward application. [SciPy Butterworth documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.butter.html).
2. **Verify the manifest as well as the inventory.** `backend/src/pa/io/manifest.py:29` reads only `migration-inventory.json`; it never checks `data/MANIFEST.sha256`. Deleting or changing the SHA manifest alone therefore leaves `pa verify-data` able to report success. The audit nevertheless hashes that file as provenance at `backend/src/pa/io/audit.py:83`. This review independently checked current consistency and found no mismatch. Make the reproducible verifier enforce that consistency and test an absent/mismatched manifest, with explicit rules for preserved source versus migrated destination paths.
3. **Give audit decisions one source of truth.** `backend/src/pa/io/audit.py:20`, `backend/src/pa/io/audit.py:36`, `backend/src/pa/io/audit.py:84` and `backend/src/pa/io/audit.py:99` separately hardcode rate candidates, discrepancy threshold, primary rate text and the third scenario's position. They currently match `decisions.yaml:3`, so the present audit is correct. A future decision amendment could silently leave audit summaries on the old settings. Read the shared settings, or explicitly version the audit settings and check agreement; select the primary scenario by rate rather than list position.

No nice-to-have findings are recorded.

## Verified evidence and acceptable decisions

The following commands ran in `backend/` during this review:

```text
uv run --frozen pytest -q tests/test_audit.py tests/test_ingestion.py tests/test_manifest.py tests/test_config.py
......                                                                   [100%]
6 passed in 0.21s

uv run --frozen pa verify-data
Source inventory verified
```

Independent read-only checks used CSV/NumPy parsing and SHA-256 calculations, rather than trusting report counts:

| Check | Observed result |
| --- | --- |
| Source preservation | All 315 manifest entries matched the inventory and current source bytes: 160 recordings, 7 metadata CSVs, 30 renders, 116 legacy images and 2 thesis PDFs. |
| Copied assets | All 148 migration destinations exist and match their original hashes. Source directories contain no additional uninventoried source files in these categories. |
| Committed originals | All 285 inventoried files tracked in legacy commit `41d6ba507965d5159a679e65962fb3d02963a551` match its Git blob contents. The 30 originally untracked renders match the preservation manifest and destination copies; Git cannot independently attest their earlier state. |
| Audit provenance | SHA manifest digest matches `audit.json`: `2119a2245bc71b0266343e28f9873f39f7753fc549eebd5ce954e47e2ef4392f`. |
| Anchored metadata | 50/50/60 trials, 10 distinct participant IDs, 30 room IDs, no duplicate experiment/participant/room keys; 10 populated spatial rows per experiment. |
| Blank records | Exactly 4 blank Experiment 3 biometric rows and 14 blank spatial rows; no extra trials inferred. |
| Ratings | All 270 stored comfort/valence/arousal values compared numerically equal after ingestion. Experiment 1 comfort remains separate; structural omissions remain `None`. |
| Sample ratios | Experiment medians: 500.0, 500.0, 499.5166667 samples per logged second. Every file's sample count, discontinuity indices and candidate-rate durations/flags match the audit. |
| Integrity and timing caveats | 38 Experiment 1 counter-flagged files; none in Experiments 2/3. Six files exceed 10% duration disagreement at conditional 500 Hz. The shortest is 7,961 samples, or 15.922 conditional seconds. |
| Chronology | Experiment 1: 3 ascending/2 descending sequences. Experiment 2: 5 distinct sequences. Experiment 3: 3 ascending/3 descending. Filenames establish chronology, not stimulus event times or randomization quality. |

The acquisition, ratings and spatial-provenance documents reflect the authoritative intake: Barcelona, owner-reported NPG Lite/Chords/Quest 3, approximate right/left forehead and wrist channels, unverified reference/ground and units, no recorded baseline, post-exposure ratings, repeated identities, differing elicitation and unmatched simulation/render conditions. No new confirmation, identity, questionnaire response or exposure calibration was inferred.

The manufacturer references were checked. [Chords-Web](https://docs.upsidedownlabs.tech/software/chords/chords-web/index.html) documents CSV recording and modality/notch filtering; [NPG Lite ESP-IDF firmware](https://github.com/upsidedownlabs/NPG-Lite-IDF-Firmware) documents three channels at 250 Hz; [NPG Lite Cardio](https://docs.upsidedownlabs.tech/software/applications/npg-lite-cardio/index.html) documents 500 Hz for that application. They support retaining uncertainty, not identifying these files' acquisition settings. The conditional 500 Hz primary and 250/256/512 sensitivity are acceptable as explicitly labelled scenarios.

The referenced [Smith et al. asymmetry primer](https://pubmed.ncbi.nlm.nih.gov/27865882/) is correctly identified and relevant to reference, artifact and interpretation caveats. The chosen right-minus-left log-alpha convention is explicit, with no established emotional-valence claim. The corrected two-second Hann/50%-overlap Welch settings fit inside four-second epochs and are consistent with [SciPy's Welch primitive](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.welch.html); synthetic recovery remains an implementation prerequisite. PubMed's direct page rendering was restricted for some requests, so citation identity/abstracts were checked through indexed PubMed records and the Munoz full article through its publisher.

Keeping raw components, signed ratings, constructed coordinates and full/partial modality cohorts distinct is appropriate. The alpha grid and descriptive within-person calibration are explicitly hypotheses. The ban on global descriptive targets in held-out evaluation is correct. Descriptive summaries without automatic trial-iid intervals or p-values appropriately acknowledge crossed participant/room dependence; no additional inferential machinery is required merely to make the report appear complete. Neuro-Score's fixed-diameter normalization and user-selected target are coherent mathematical conventions, not validated health or design-quality measures.

## Scope, snapshots and exit condition

The review loaded AGENTS.md, the standard Fab project context, intake/plan, preservation/audit artifacts, protocol documents, specification/decisions, ingestion/audit/manifest code and requested tests. In-progress signal code was read and exercised only with synthetic adversarial inputs to check consequences of the proposed methods. No participant-level physiological features, fused targets, model comparisons, public exports or final-site results were produced or approved. Real visual signal review, downstream recovery/leakage tests, statistical products, model usefulness and deployment remain outside this checkpoint.

Reviewed snapshot hashes:

```text
analysis-v1.md  2fba8ff54b4396051cd24b9bd9bd4b59fdd421877e3bfd992e0a0df09daed78a
decisions.yaml  5a2f75ab7cf3db5e57cae673bb5043cfbd9a4b2ec03d1143952476b1b5779739
signals/ecg.py  46ff4e9ff18cd07ef21bb5df0e3e373e85470b2a326f2331c5f47df754ba0789
signals/eeg.py  e635a70a76087a09be9c28c34011e0b25f69596f2b32aa11c5e47764aef2d9bc
signals/qc.py   bb691685b72c5b3a4074321abb60d74472537886fd7a16c38f944a7b7fdd5788
```

Record amendments for M1–M3 in the specification, machine-readable settings and append-only decision history; resolve the synthetic QC failures before real signal use; then obtain and record a checkpoint re-review. The coordinator owns the verdict record and any subsequent transition. Downstream scientific results remain gated by this fail verdict.
