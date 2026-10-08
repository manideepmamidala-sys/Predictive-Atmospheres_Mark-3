# Phase 3 — constructed affect and descriptive analysis

Date: 2026-10-08. `pa affect` and `pa analyze` used the gated 160-trial signal evidence and original investigator-supplied ratings. Reproducible products are `artifacts/results/affect_detail.json` and `artifacts/results/affect_analysis.json`. Original comfort, valence and arousal are retained without reinterpretation or physiological replacement. Experiment 1 has comfort only and contributes **no self-reported valence/arousal**. The objective coordinates are explicit hypotheses made from conditionally sampled, operationally screened channels, not observed emotion or clinical measures.

| Experiment | Original valence/arousal pairs | Complete descriptive fusion | Partial-modality fusion | Objective-only | Participants contributing complete fusion |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1 | 0 | 0 | 0 | 50 | 0 |
| 2 | 50 | 4 | 46 | 0 | 1 |
| 3 | 60 | 10 | 50 | 0 | 1 |

Only four Experiment 2 and ten Experiment 3 records retain all four **within-person descriptive** components after the declared three-valid-trial and nonzero-scale rule. The Experiment 3 source signal ledger has 14 raw full EEG/HR/RMSSD component trials across three participants; four lose full descriptive status because their participants have too few RMSSD trials to calibrate that component within person. This descriptive normalization is **never** supplied to the held-out model; its target transform is separately fitted on training partitions. Partial-modality coordinates are exported with exact component availability and a distinct cohort name. They are not pooled into the complete-fusion mean or model target. Experiment 1 comfort stays independent of valence/arousal.

Primary α=0.5 complete-fusion descriptive means are (valence −0.382, arousal 0.037) for four Experiment 2 records and (0.190, 0.036) for ten Experiment 3 records. Each mean describes **one participant's observed rooms**, not a participant-population response. The predeclared α grid changes the same eligible records' mean coordinates as follows; this is assumption sensitivity, not uncertainty calibration:

| α objective weight | Exp 2 mean valence / arousal (n=4) | Exp 3 mean valence / arousal (n=10) |
| ---: | ---: | ---: |
| 0 | 0.000 / 0.200 | 0.260 / 0.010 |
| 0.25 | −0.191 / 0.119 | 0.225 / 0.023 |
| 0.5 | −0.382 / 0.037 | 0.190 / 0.036 |
| 0.75 | −0.573 / −0.044 | 0.155 / 0.050 |
| 1 | −0.764 / −0.126 | 0.120 / 0.063 |

`affect_detail.json` retains each trial's original signed reports, raw and normalized components, objective and fused axes, cohort, α scenarios, and objective-minus-subjective disagreement where both axes exist. Disagreement summaries are **stratified by experiment and complete/partial cohort**, with explicit available-pair counts. The absolute complete-fusion objective/report difference averages 0.764 valence and 0.354 arousal for Experiment 2's four records, and 0.890 valence and 0.734 arousal for Experiment 3's ten records. These are distances on constructed signed coordinates; they do not validate or invalidate self-report or physiology.

At the room-summary level, supplied illuminance versus original valence has descriptive Pearson r=0.620 across ten Experiment 2 rooms (five participants) and r=0.081 across ten Experiment 3 rooms (six participants). The corresponding **complete-fusion** room correlations use only one participant: r=−0.843 over four Experiment 2 rooms and r=−0.387 over ten Experiment 3 rooms. They cannot support between-person generalization. Room attributes are simulation metadata, not verified headset exposure; protocols and elicitation differ, so cross-experiment equality is not assumed. All these associations are descriptive, with no causal language or significance claim.

Participant and room are crossed/repeated, and there are too few independent participants for a justified default interval method. `affect_analysis.json` therefore records `interval_status: unavailable_no_validated_crossed_group_interval_method`, null intervals and null p-values. Group tables show trial, participant, room, experiment and per-measure valid counts. An unavailable inferential interval is intentional; no trial-independent confidence interval, singular mixed-model replacement, or default neutral response was emitted.
