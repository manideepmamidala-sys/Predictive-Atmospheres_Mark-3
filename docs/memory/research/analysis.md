---
type: memory
description: "Conditional EEG/ECG QC, descriptive affect cohorts, grouped model evaluation, scoring and reported limitations."
---
# Analysis and Model Evidence

**Domain**: research

## Overview

The [analysis specification](../../specs/analysis-v1.md) governs conditional signal processing, constructed affect, grouped evaluation and failure status. The [protocol](/research/protocol.md) records source uncertainty. The [data card](../../data_card.md), [model card](../../model_card.md) and phase reports record actual counts and results.

## Requirements

### Conditional signals and descriptive affect

The primary rate scenario is 500 Hz, with 250, 256 and 512 Hz sensitivities because the source has no confirmed sampling setting. EEG is filtered in accepted four-second epochs after raw-sample QC; accepted features remain subject to persistent ocular, motion and muscle contamination. ECG processing splits at counter discontinuities and rejected blocks; heart rate and RMSSD require qualifying contiguous runs. Invalid measures retain explicit reasons and do not receive neutral or nominal substitutes. At the primary scenario, EEG features are operationally available on 160 trials, heart rate on 71 and strict 30-second RMSSD on 18.

Descriptive objective coordinates combine eligible forehead EEG and wrist ECG components after within-person calibration. Experiment 2 contributes four complete-fusion trials from one person; Experiment 3 contributes ten from one person. The fourteen complete descriptive positions therefore represent two people. Partial-modality records and objective-only or subjective-only states stay distinct. The generated atlas reports alpha sensitivity, objective versus subjective disagreement and participant summaries with available-record denominators; Experiment 1 comfort is never an affect axis.

### Prediction, support and status

The model cohort comprises fourteen Experiment 3 full-component trials from three people and ten rooms. Population target calibration is fitted inside each training partition, separately from descriptive within-person transforms. Room and participant Leave-One-Group-Out analyses answer different holdout questions, with inner grouped selection or a specified baseline fallback. Held-out-room equal-axis MAE is 0.4304 versus 0.4099 for the median baseline; status is `not_better_than_baseline`. The subject holdout has only three eligible people. No calibrated interval, individual response guarantee or causal design claim follows from these results.

Neuro-Score is bounded distance from the predicted signed point to a user-selected target. The optimizer searches physically valid independent inputs within studied support and can return no candidates. The [platform](/architecture/platform.md) documents input, support and artifact contracts.

## Design Decisions

### Separate descriptive and prediction cohorts

**Decision**: Use within-person calibration for descriptive views and fold-fitted population calibration for held-out prediction targets.
**Why**: A held-out person's outcome distribution is unavailable at inference, and the complete descriptive and modeling cohorts differ.
**Rejected**: Pooling partial records or fitting targets on all outcomes before evaluation, which would obscure eligibility or leak held-out information.
*Introduced by*: 261008-ymhz-research-platform-rebuild

### Count-aware studied support

**Decision**: Check opening counts along with the other observed numerical room inputs and categorical combinations.
**Why**: Door and window counts are model inputs and affect whether a proposed room resembles observed rooms.
**Rejected**: A support label that ignores counts while the fitted model consumes them.
*Introduced by*: 261008-ymhz-research-platform-rebuild
