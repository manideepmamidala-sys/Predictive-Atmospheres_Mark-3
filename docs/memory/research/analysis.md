---
type: memory
description: "Approved v1.2 conditional signal analysis, reviewed component eligibility, constructed affect, complete catalogue and baseline-only grouped model evidence."
---
# Analysis and Model Evidence

**Domain**: research

## Overview

The [approved v1.2 specification](../../specs/analysis-v1.2-draft.md), SHA-256 `51c01ef6ccdf2f4318ac786d1bb39afeb1aa2bcf3bc93039479a4ed2454603ac`, governs the current conditional signal, constructed affect, comparison and model methods. It is a retrospective plan approved before dependent v1.2 reanalysis, not prospective preregistration. The [protocol](/research/protocol.md) records source uncertainty; the [data card](../../data_card.md), [model card](../../model_card.md), [CP-C receipt](../../reports/revision-2026-10/CP-C.md) and versioned result products record actual cohorts and limits. The v1.1 specification remains a historical contract for its historical products.

## Requirements

### Conditional signals and reviewed eligibility

The primary processing scenario is 500 Hz, with 250, 256 and 512 Hz sensitivity scenarios because the hardware sampling setting is unconfirmed. Counter continuity, logged durations and sample counts are separate evidence. EEG QC records channel, epoch and trial reasons; accepted forehead features still admit residual ocular, motion and muscle contamination. ECG processing honors counter discontinuities and contiguous-run gates. Heart rate and 30-second RMSSD have independent validity; invalid or uncertain values retain reasons rather than neutral replacements.

The delegated [CP-B ledger](../../reports/revision-2026-10/CP-B.md) records reviewed accept/reject/uncertain decisions and exclusions with evidence and agent provenance. It does not claim personal owner inspection. Across 160 trials, reviewed timebase is eligible in 154, bilateral EEG in 128, heart rate in 66 and RMSSD in 17. E1/E2/E3 bilateral EEG counts are 50/37/41, heart-rate counts 13/20/33 and RMSSD counts 0/4/13. Public exports keep automated and reviewed status and reasons separate for timebase, right EEG, left EEG, bilateral EEG, heart rate and RMSSD. Thirty-three trials have at least one review downgrade; 49 retain eligible heart rate without eligible RMSSD.

### Components, fusion and descriptive comparisons

Physiology-derived and self-reported coordinates remain separate; fusion is a constructed hypothesis, not measured emotion. Eligible raw FAA supplies physiology-derived valence. Alpha suppression and engagement contribute equally to EEG arousal; EEG arousal and eligible heart rate contribute equally to physiology-derived arousal. Physiology-derived and signed self-report coordinates receive equal 0.5 weights in complete fusion. Descriptive calibration uses within-person median/MAD only where at least three distinct eligible trials give positive scale. Missing components remain missing; partial-modality, partial-axis-overlap, objective-only and self-report-only records are not labelled complete.

Experiment 2 has 19 complete-fusion trials and Experiment 3 has 21, from five distinct people combined. E2 also has 18 partial-modality, one partial-axis-overlap and 12 self-report-only records; E3 has 20, 14 and five respectively. Experiment 1 has 50 objective-only records and comfort as a distinct construct. E2/E3 rating procedures differ, so their results are analysed separately before qualified comparison. The prespecified validity matrix reports eligible counts and unavailable reasons for EEG/report, EEG/heart-rate, heart-rate/report, blink/muscle and FAA/valence questions. Repeated people and rooms limit independent inference; a trial count is not a population sample size.

### Grouped prediction and controls

The fitted Studio cohort has 23 raw full-component E3 trials across four people and ten rooms. Population target calibration, feature preprocessing and estimator selection fit within each training partition, including grouped inner folds. Room and person holdouts answer different questions. Equal-axis, equal-held-out-room MAE is 0.34964, versus 0.34606 for the median baseline and 0.34044 for the mean baseline. Equal-held-out-person MAE is 0.35118, equal to the median fallback with too few remaining person groups for inner selection. The full-data selection is `dummy_mean`, so the fitted artifact is `baseline_only` and its output does not respond to room attributes.

The prespecified learning curve evaluates all 455 unique training-room subsets at k=4–9; its median baseline is lower at every k. The spatial negative control performs 1,000 whole-training-room attribute shuffles with full refitting; the observed room MAE lies within its descriptive shuffled distribution. These overlapping comparisons are not independent population replications or a calibrated significance test. Self-report-only room comparisons use different targets and are research-only; they are not alternative Studio fits. No personal accuracy, learned spatial gain, causal design effect, calibrated interval or validated emotion measurement follows. The [platform](/architecture/platform.md) records the deployed score and search contract.

### Research catalogue

`artifacts/results/analysis/` holds 28 validated products: S1–S5, R1–R9, B1–B8, P1–P5 and Methods. Twenty-seven are available; P4 explicitly reports unavailability for feature importance under a constant selected model. Product envelopes include question, method, sample counts, units, caveats, status and source/method provenance. Methods exposes 22 approved settings, ten already-computed fusion-weight sensitivity summaries, CP-B review evidence and eight pinned references. The browser renders these products without recomputing statistical results.

## Design Decisions

### Separate descriptive and prediction calibrations

**Decision**: Use within-person calibration for descriptive views and training-fold population calibration for deployable E3 targets.
**Why**: A held-out person's outcome distribution is unavailable at inference, and descriptive and modeling cohorts differ.
**Rejected**: Pooling partial records or fitting target calibration on held-out outcomes.
*Introduced by*: 261008-ymhz-research-platform-rebuild

### Count-aware studied support

**Decision**: Check opening counts with other observed numeric room inputs and categorical combinations.
**Why**: Door and window counts are model inputs and part of the observed support boundary.
**Rejected**: A support label that ignores counts while the estimator consumes them.
*Introduced by*: 261008-ymhz-research-platform-rebuild

### Complete reviewed fusion cohort

**Decision**: Require reviewed raw FAA, alpha suppression, engagement, heart rate and observed report for complete fusion and E3 modeling; retain partial components for descriptive analyses.
**Why**: Separate eligibility lets each observed component contribute where valid without imputing a missing emotional axis.
**Rejected**: Treating a partial or uncertain record as complete to enlarge the model cohort.
*Introduced by*: 261010-tadj-research-atlas-design-studio

### Publish baseline and unavailable evidence

**Decision**: Keep the selected constant model, grouped baselines, full controls and unavailable P4 visible beside Studio.
**Why**: A functioning prediction interface does not establish that room attributes explain the constructed target.
**Rejected**: Suppressing weak comparisons or presenting feature importance for a constant estimator.
*Introduced by*: 261010-tadj-research-atlas-design-studio
