# Research Atlas analysis catalogue

This crosswalk retains the full catalogue from the original October revision guide under the approved v1.2 methods. EEG/ECG lead the research; self-report is compared; fused coordinates remain visible; the Studio predicts **only fusion**; and the landing explains the thesis without results cards or a featured findings chart. The source-computed products are exported as `artifacts/results/analysis/{ID}.json` with a validated `index.json`; each has a question, takeaway or explicit unavailable reason, method, caveats, source/spec hash, counts and units. A product is staged for publication only after the corresponding checkpoint disposition. E1 comfort is never a valence point; E2/E3 report charts remain separate. No guide F1–F10 estimate is an acceptance target.

| ID | Research question or product | Route / computed export |
| --- | --- | --- |
| S1 | Who saw which room, and where are EEG/ECG measurements eligible? | `/study` · exposure × room matrix |
| S2 | Which records can enter each analysis? | `/study` · branching eligibility by modality/experiment, never a falsely nested funnel |
| S3 | What do thirty rooms look like and how do their attributes vary? | `/study` · original-render gallery and display-scaled parallel-coordinate profiles; original values/units retained |
| S4 | Which spatial attributes move together across independent rooms? | `/rooms` · room-level correlation matrix, n rooms |
| S5 | Who took part? | `/study` · per-person age/gender/sleep dots, scope labeled |
| R1 | How do person, room and residual shares compare for ratings? | `/rooms` · E2/E3 axis-specific variation, E1 comfort separate |
| R2 | Which rated rooms have higher/lower reported valence or arousal? | `/rooms` · ranked room means with valid uncertainty or unavailable interval |
| R3 | Where do reported rooms sit on the affect plane? | `/rooms` · report-only positions/density, E2/E3 distinction |
| R4 | Do raters agree on room profiles? | `/rooms` · pairwise person agreement and ten unique balanced rater partitions per E2/E3 axis |
| R5 | How do participants use the scales? | `/rooms` · individual mean and range |
| R6 | How do supplied E2 lighting attributes relate to ratings? | `/rooms` · room-level scatter and valid paired day/night contrasts |
| R7 | How do E3 space types compare? | `/rooms` · individual dots with room/person counts |
| R8 | Does E1 comfort vary with form? | `/rooms` · separate comfort/volume/height chart |
| R9 | Do participant characteristics relate to reports? | `/rooms` · per-person sleep/ratings dots with n people |
| B1 | Which EEG/ECG traces are usable and why? | `/body` · delegated review eligibility by experiment and component; trial traces remain in source bundle |
| B2 | What EEG spectrum/band pattern remains after QC? | `/body` · per-experiment/channel median first-accepted-epoch spectrum and reviewed all-epoch band powers |
| B3 | What cardiac features are available? | `/body` · HR, eligible RMSSD and R-peak trace examples |
| B4 | Does cortical arousal agree with reported arousal? | `/body` · alpha suppression, engagement, composite and within-person relationships |
| B5 | Does cortical arousal agree with HR? | `/body` · experiment-separated candidate comparisons |
| B6 | Does forehead alpha asymmetry relate to reported valence? | `/body` · FAA distribution and exploratory association |
| B7 | Where do body and report diverge? | `/body` · measured-pair disagreement map/table, no privacy-masking claim |
| B8 | How do physiology, report and fusion densities/coordinates differ? | `/body` · same complete-fusion trials in all three panels, E2/E3 separate, with observed positions and centroid vectors |
| P1 | Does a known room's relative rating profile transfer to a held-out person? | `/prediction` · model/baseline error by person; centered-rating limit |
| P2 | Are observed scores unusual under declared room-label/attribute nulls? | `/prediction` · permutation distributions and observed markers |
| P3 | Can spatial attributes predict a held-out room? | `/prediction` · distinct self-report comparator and fused target, held-out-room folds and all 455 prespecified unique room-subset fits |
| P4 | Which features matter inside an experimental fitted model? | `/prediction` · importance next to baseline/error limits |
| P5 | How are model targets, features, folds and baselines constructed? | `/prediction` · training diagram and model status |
| Methods | What method/provenance limits the above? | `/methods` · timebase, thresholds, CP-B decisions, sensitivity, data/model cards, implemented thesis prototypes |

The `/explore` route supplies filtered trial/room/person tables and available signals for every analysis's “see the data” link. The `/studio` route has one fused model and two flows: forward room evaluation against an emotional target and constrained generation toward a separate requested **numerical** Neuro-Score. Neither flow is a research catalogue result. The `/` landing and eight-page route structure follow the intake.

## Current export encodings

These are the generated v1.2 product contracts in `artifacts/results/analysis/index.json`. Row counts describe chart records, not independent people or trials; each product carries its own eligible denominators, units and caveats. The frontend uses the exported encodings and data values without recalculating research statistics.

| ID | Route | Status | Chart encoding | Rows |
| --- | --- | --- | --- | ---: |
| S1 | `/study` | available | `heatmap`: `room_id` → `participant_id`; series `exposed` | 160 |
| S2 | `/study` | available | `bar`: `branch` → `trials`; facet `experiment` | 21 |
| S3 | `/study` | available | `line`: `attribute` → `normalized_value`; series `room_id`; facet `experiment` | 240 |
| S4 | `/rooms` | available | `heatmap`: `attribute_x` → `attribute_y`; series `spearman_rho`; facet `experiment` | 209 |
| S5 | `/study` | available | `scatter`: `age` → `trial_count`; series `experiment` | 16 |
| R1 | `/rooms` | available | `bar`: `axis` → `room_share`; series `experiment` | 4 |
| R2 | `/rooms` | available | `bar`: `room_id` → `mean_rating`; series `axis`; facet `experiment` | 40 |
| R3 | `/rooms` | available | `heatmap`: `valence` → `arousal`; series `density`; facet `experiment` | 994 |
| R4 | `/rooms` | available | `bar`: `partition` → `spearman_rho`; series `axis`; facet `experiment` | 90 |
| R5 | `/rooms` | available | `scatter`: `participant_id` → `mean_rating`; series `axis`; facet `experiment` | 22 |
| R6 | `/rooms` | available | `scatter`: `illuminance` → `rating`; series `axis`; facet `experiment` | 230 |
| R7 | `/rooms` | available | `scatter`: `space_type` → `mean_rating`; series `kind`; facet `axis` | 130 |
| R8 | `/rooms` | available | `scatter`: `floor_area` → `comfort`; series `participant_id` | 50 |
| R9 | `/rooms` | available | `scatter`: `mean_sleep_hours` → `mean_rating`; series `axis`; facet `experiment` | 22 |
| B1 | `/body` | available | `bar`: `branch` → `eligible_trials`; series `experiment` | 18 |
| B2 | `/body` | available | `line`: `frequency_hz` → `median_psd`; series `channel`; facet `experiment` | 1614 |
| B3 | `/body` | available | `scatter`: `heart_rate_bpm` → `rmssd_ms`; series `experiment` | 466 |
| B4 | `/body` | available | `scatter`: `candidate_value` → `report_arousal`; series `candidate`; facet `experiment` | 276 |
| B5 | `/body` | available | `scatter`: `eeg_arousal` → `heart_rate_bpm`; series `participant_id`; facet `experiment` | 52 |
| B6 | `/body` | available | `scatter`: `faa` → `subjective_valence`; series `participant_id`; facet `experiment` | 78 |
| B7 | `/body` | available | `scatter`: `reported_axis` → `physiology_axis`; series `axis`; facet `experiment` | 176 |
| B8 | `/body` | available | `heatmap`: `valence` → `arousal`; series `density`; facet `component` | 2772 |
| P1 | `/prediction` | available | `bar`: `participant_id` → `mae`; series `axis`; facet `experiment` | 22 |
| P2 | `/prediction` | available | `bar`: `bin_center` → `draw_count`; facet `control` | 180 |
| P3 | `/prediction` | available | `line`: `training_room_count` → `mean_mae`; series `candidate` | 24 |
| P4 | `/prediction` | unavailable | `bar`: `feature` → `importance` | 0 |
| P5 | `/prediction` | available | `bar`: `stage` → `count` | 5 |
| Methods | `/methods` | available | `table`: `experiment` → `source_trials` | 3 |

P4 is unavailable because the selected final model is constant; the product supplies an explicit reason and no importance values. P2 contains nine controls with 1,000 draws each, binned into twenty exported bars per control. R7 contains 120 individual E3 rating-axis dots and ten function means; B8 includes density-grid and observed/vector records distinguished by `kind`. The descriptive control ranges are not population p-values.

## Legacy visual crosswalk

The original presentation/booklet and its linked InDesign graphics are sources of ideas and layout only; redraw from approved versioned exports. The Windows booklet ZIP's 79 `Links/` files include the following concepts.

| Legacy chart idea | Current placement and correction |
| --- | --- |
| Objective, subjective and fused density fields and target vectors | R3 and B8; show all three, matched axes and contributing cohorts. Fusion is retained rather than appendix-only. |
| Age, gender and sleep violins | S5/R9 per-person dots; five/six/ten people do not justify smoothed group densities. |
| Average ECG spectrum | B3 HR, valid HRV and R-peak examples; ECG spectrum may appear as methodological trace, not primary outcome. |
| EEG spectrum and band balance | B2 with review-approved QC and units. |
| Heart rate versus HRV | B3 only where both valid, with independent counts. |
| Stress distribution / beta-alpha by experiment | B4 separate EEG candidates and composite, exploratory and experiment-specific. |
| Day versus night and illuminance extremes | R6 paired self-report contrasts and labeled room-level scatter; do not copy old effect numbers. |
| Feature correlation matrix | S4 room-attribute correlations; attribute/rating relationships belong to R6/R7. |
| High-variance spatial triggers | B7 descriptive body/report disagreement; no proof of privacy masking. |
| Nonlinear feature importance | P4 beside P3 baseline and fold uncertainty. |
| Room-profile parallel coordinates | S3 with thirty original rooms and experiment labels. |

The prior guide's F1–F10 rate, QC, correlation, variance and model estimates were exploratory planner observations, not inherited measurements. Current products calculate results from the reviewed ledger; null/unavailable outcomes remain visible with reasons. The accepted intake supersedes the guide's self-report-primary, no-fusion and nearest-room-only Studio suggestions. The active Fab plan and approved CP-Spec source fix the method contract.
