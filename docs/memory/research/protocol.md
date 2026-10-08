---
type: memory
description: "Observed pilot source inventory, investigator-reported acquisition and ratings, and unresolved measurement provenance."
---
# Protocol and Source Provenance

**Domain**: research

## Overview

The pilot contains 160 room-viewing recordings across three experiments, ten distinct subject IDs and thirty room IDs. Original recordings, seven metadata CSVs, thirty room renders, historical images and thesis PDFs are inventoried and SHA-256 checked. The [data card](../../data_card.md) and [protocol records](../../protocol/acquisition.md) distinguish files from investigator report.

## Requirements

### Acquisition and exposure

The investigator reports Barcelona collection with an Upside Down Labs NPG Lite through Chords, approximate bilateral forehead electrodes and a wrist ECG channel. Participants stood and turned while viewing non-interactive 360-degree Lumion rooms in a Meta Quest 3 gallery. Files contain `Counter,Channel1,Channel2,Channel3`, without timestamps or physical units. The modulo-256 counter is an integrity field; it does not prove a hardware sample rate. Reference/ground wiring, exact sensor placement, firmware, original event timing and physical units remain unverified. Analysis uses a conditional 500 Hz scenario with rate sensitivity, not a confirmed acquisition setting.

### Rating and spatial fields

Experiment 1 records comfort in signed form and has no valence/arousal rating. Experiments 2 and 3 contain signed valence/arousal values from different investigator-reported response procedures; original forms and conversion sheets are unavailable, so measurement equivalence is unresolved. Experiment 3 supplies sleep observations on its sixty trial rows. Age and gender map to all ten source IDs; participant names are not mapped to recordings. Missing fields stay missing.

Grasshopper/Ladybug/Honeybee derived supplied spatial and lighting values, but the calculations were not matched to headset exposure. Door and window areas are totals, not per-opening areas. Room renders map by filename stem; the display-eye convention is inferred. See [rating](../../protocol/ratings.md) and [spatial](../../protocol/spatial-provenance.md) provenance.

## Design Decisions

### Provenance-separated measurements

**Decision**: Preserve original values and mark owner report, observed fields, conditional analysis assumptions and derived products separately.
**Why**: The available source does not verify hardware settings, questionnaire wording or visual exposure conditions.
**Rejected**: Treating thesis prose, counter increments or supplied simulation fields as independent measurement proof.
*Introduced by*: 261008-ymhz-research-platform-rebuild
