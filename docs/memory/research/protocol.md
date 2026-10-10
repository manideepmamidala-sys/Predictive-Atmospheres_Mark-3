---
type: memory
description: "Observed pilot sources, investigator-reported acquisition and ratings, historical thesis claims, conditional timebase and delegated signal-review provenance."
---
# Protocol and Source Provenance

**Domain**: research

## Overview

The pilot has 160 room-viewing recordings across three experiments, ten distinct source subject IDs and thirty room IDs. The retained canonical source set contains 160 recordings, seven metadata CSVs, thirty Lumion renders and 116 historical site assets, all checksum-addressed in `data/MANIFEST.sha256`. Source files, investigator report, historical thesis statements, analysis assumptions and derived products carry distinct authority. The [data card](../../data_card.md), [acquisition record](../../protocol/acquisition.md) and [thesis context](../../research/thesis-source-context.md) detail that provenance.

## Requirements

### Acquisition and exposure

The investigator reports Barcelona collection with an Upside Down Labs NPG Lite through Chords, approximate right and left forehead electrodes and wrist ECG. Participants stood and turned while viewing non-interactive 360-degree Lumion rooms in a Meta Quest 3 gallery. Recording began at eye opening in the headset and stopped before headset removal; the seated, closed-eye ratings came afterwards. Exposures were intended to be around one minute, but sampled and logged lengths vary. The investigator reports randomized presentation order without a supplied randomization algorithm or event log.

Source CSVs contain `Counter,Channel1,Channel2,Channel3` without timestamps or physical units. The modulo-256 counter is an integrity field, not a verified sample clock. Electrode reference/ground wiring, exact placement, firmware, original event timing, hardware rate, signal units and ECG normal-to-normal status remain unverified. Analysis therefore uses a conditional 500 Hz primary scenario with 250, 256 and 512 Hz sensitivities. [Approved method settings](../../specs/analysis-v1.2-draft.md) govern timebase and quality decisions; neither counter increments nor thesis prose establish acquisition settings.

### Ratings and supplied room fields

Experiment 1 records signed comfort and has no valence/arousal rating. Experiments 2 and 3 have signed valence/arousal values but use different investigator-reported response procedures; original forms and conversion sheets are unavailable, so measurement equivalence is unresolved. Experiment 3 supplies sleep observations on its sixty trial rows. Age and gender map to the ten source IDs; participant names are not mapped to recordings. Missing values stay missing. See [rating provenance](../../protocol/ratings.md).

Grasshopper/Ladybug/Honeybee supplied spatial and lighting values, but those calculations were not calibrated to headset exposure. Door and window areas are totals, not per-opening areas. Room renders map by filename stem; top-eye extraction from stacked stereo images is an inferred presentation convention. See [spatial provenance](../../protocol/spatial-provenance.md).

### Thesis and reviewed signal evidence

The 48-page presentation, 104-page booklet, DOCX text, booklet assets and Windows prototype sources were inspected for the architectural question, original formulas, experiment diagrams and demonstrations. The thesis's five-minute seated baseline, exact exposure timing, 250 Hz acquisition and questionnaire batteries are historical claims without corresponding verification in the source files; no rest/neutral baseline or extra questionnaire responses were supplied. The Rhino/Grasshopper and AI-rendering examples are historical demonstrations, not running integrations in the atlas. [Thesis source context](../../research/thesis-source-context.md) retains page and file references.

Approved CP-B AI reviewers inspected flagged raw traces and spectra and recorded accept/reject/uncertain dispositions, reviewer identities, reasons and exclusions in the [decision record](../../reports/revision-2026-10/CP-B.md) and `artifacts/results/qc_review.json`. This is delegated review evidence, not personal owner inspection or proof that accepted signals are artifact-free. Reviewed timebase is eligible in 154 of 160 trials, bilateral EEG in 128, heart rate in 66 and RMSSD in 17. Public trial exports preserve six separate automated and reviewed component records. An uncertain timebase decision withholds `E2:Subj_E:Rm_018`; `E1:Subj_B:Rm_010` retains eligible heart rate while RMSSD is unavailable. The [analysis memory](/research/analysis.md) records cohort consequences.

## Design Decisions

### Provenance-separated measurements

**Decision**: Preserve original values and mark observed fields, owner report, historical thesis claims, conditional assumptions and derived products separately.
**Why**: Available sources do not independently verify hardware settings, questionnaire wording or visual exposure conditions.
**Rejected**: Treating thesis prose, counter increments or supplied simulation fields as independent measurement proof.
*Introduced by*: 261008-ymhz-research-platform-rebuild

### Delegated review with explicit uncertainty

**Decision**: Apply recorded CP-B agent dispositions to each flagged channel/trial component and retain uncertain or rejected signals as unavailable.
**Why**: Inspectable evidence can guide eligibility while preserving who reviewed it and what remains unresolved.
**Rejected**: Promoting a flag without a supported disposition or calling delegated AI review personal owner signoff.
*Introduced by*: 261010-tadj-research-atlas-design-studio
