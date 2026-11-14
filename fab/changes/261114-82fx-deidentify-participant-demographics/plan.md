# Plan: De-identify participant demographics

**Change**: 261114-82fx-deidentify-participant-demographics
**Intake**: `intake.md`

## Requirements

### Data: Public source metadata

#### R1: Per-person demographics are withheld from the public tree
The repository SHALL NOT contain any file that maps a participant code to age, gender, occupation or sleep hours. `data/metadata/Subject Data.csv` SHALL be removed. The `Sleep Hours` column SHALL be removed from `data/metadata/experiment_03_biometric data.csv`, leaving every other byte of each retained field unchanged (same row order, same other values, same trailing empty column).

- **GIVEN** the checked-out tree outside `fab/` and git history
- **WHEN** searching for per-code age/gender/occupation/sleep values
- **THEN** no file pairs a `Subj_*` code with any of those attributes
- **AND** `experiment_03_biometric data.csv` still parses with identical Subject_ID, Room_ID, duration, filename, valence and arousal values for all 60 trials

#### R2: Withheld originals keep checksum provenance
Each withheld original SHALL be recorded in `data/withheld-sources.json` with `path`, original `sha256`, `size_bytes`, `reason` and `custody`. The recorded values are:
- `data/metadata/Subject Data.csv`: sha256 `98d2e507028f24dda1b5d0a6c91f24ba80035f28730665acd04513e22120c85e`, 293 bytes;
- `data/metadata/experiment_03_biometric data.csv` (original with the sleep column): sha256 `0012d8d3a57c7152b7de6bc8fe2ee30f9afd34a0bc3e4c2cc2ef06cdbec42d9c`, 3592 bytes.

- **GIVEN** an auditor with the owner's private originals
- **WHEN** they hash the originals
- **THEN** the hashes match `data/withheld-sources.json`

#### R3: Aggregate cohort summary is published
`data/metadata/participant_summary.csv` SHALL hold exactly one aggregate row:
`scope=all, participants=10, age_min=25, age_max=28, age_mean=26.0, female=5, male=5, occupation=Architect, e3_sleep_trials=60, e3_sleep_hours_mean=6.75, e3_sleep_hours_min=3.0, e3_sleep_hours_max=8.5`.
These values are derived from the withheld originals before removal.

- **GIVEN** the published summary
- **WHEN** the loader reads it
- **THEN** it returns those values with validation (counts non-negative, female+male ≤ participants, min ≤ mean ≤ max)

#### R4: Source manifests stay verifiable
`data/source-inventory.json` and `data/MANIFEST.sha256` SHALL be regenerated with `scripts/build_source_manifest.py`, and `--check` SHALL pass.

- **GIVEN** the modified metadata directory
- **WHEN** `python3 scripts/build_source_manifest.py --check` runs
- **THEN** it exits 0

### Backend: Pipeline and exports

#### R5: Loader exposes only aggregates
`pa.io.metadata` SHALL provide `load_participant_summary()`, returning a validated aggregate record, and SHALL no longer provide `load_demographics()`. `Trial` SHALL no longer carry `sleep_hours`.

- **GIVEN** a malformed summary (missing column, negative count, or min > max)
- **WHEN** `load_participant_summary()` runs
- **THEN** it raises `ValueError`

#### R6: People export carries no per-person demographics or sleep
`PersonRecord` SHALL NOT have `age`, `gender` or `sleep_hours`. `PersonExperimentRecord` SHALL NOT have `sleep_hours`, `sleep_min_hours`, `sleep_max_hours` or `sleep_observations`. `PeopleExport` and `ResearchBundle` SHALL carry a `cohort: CohortSummary` holding the R3 values.

- **GIVEN** a pipeline run
- **WHEN** `artifacts/results/people.json` and `bundle.json` are written
- **THEN** no person entry contains age, gender or sleep keys
- **AND** `cohort` equals the R3 aggregate

#### R7: S5 and R9 products are aggregate-safe
- **S5** SHALL keep one row per participant code × experiment with `trial_count`, `room_count` and `complete_fusion_count`, and SHALL NOT include age or gender; its x axis is `experiment`.
- **R9** SHALL contain no `participant_id`, age, gender or per-person sleep. It SHALL be an experiment × axis aggregate (`experiment`, `axis`, `participants`, `rating_trials`, `mean_rating`), drawn as a bar chart. E3 rows carry the cohort sleep aggregate (`sleep_trials`, `sleep_hours_mean/min/max`); E2 rows set these to null with an explanatory caveat.

- **GIVEN** the catalogue build
- **WHEN** `analysis/S5.json` and `analysis/R9.json` are written
- **THEN** neither contains age, gender or a per-person sleep value
- **AND** both validate against `CatalogueProduct`

#### R8: Signal-review provenance remains valid
Regeneration SHALL NOT alter the raw-signal artifacts the CP-B ledger pins (`signals_detail.json`, `timebase.json`). The CP-B integration hash checks SHALL keep passing. Hashes SHALL NOT be hand-edited.

- **GIVEN** `make pipeline` after the data change
- **WHEN** the CP-B disposition is integrated
- **THEN** no "source hashes changed" error occurs, and `signals_detail.json`/`timebase.json` are byte-identical to before

### Frontend: Explore page

#### R9: Website shows only aggregate demographics
`frontend/src/lib/research.ts` SHALL drop per-person `age`, `gender` and sleep fields and accept the bundle `cohort`. `frontend/src/pages/Explore.tsx` SHALL remove the Age, Reported gender and Sleep (h) columns, and SHALL render one aggregate cohort sentence built from `cohort`.

- **GIVEN** the people view on Explore
- **WHEN** it renders
- **THEN** the table shows Participant, Trials and Complete fusion only
- **AND** a sentence states "10 participants, all architects, aged 25–28 (mean 26.0); 5 women, 5 men. Experiment 3 sleep (60 trials): mean 6.75 h, range 3.0–8.5 h." from data

### Docs

#### R10: Documentation states the privacy approach
`docs/data_card.md` and `docs/research/analysis-catalogue.md` SHALL describe aggregate-only demographics, the withheld originals and the reason, and the new S5/R9 content.

- **GIVEN** a reader of the data card
- **WHEN** they look for participant characteristics
- **THEN** they find the aggregate and the withholding rationale, not per-person values

### Non-Goals
- Rewriting git history to purge old values: owner decision, out of scope.
- Redeploying the Vercel website: a separate, owner-approved step after merge.
- Changing signal processing, QC, affect, model selection or any scientific result.

### Design Decisions

#### Withhold, don't delete, source evidence
**Decision**: Remove identifying originals from the public tree, but record their sha256 and size in `data/withheld-sources.json`; the owner keeps the originals privately.
**Why**: Constitution I requires source evidence to be checksum-verified, and constitution V forbids silently publishing participant identities. Withholding with a checksum satisfies both.
**Rejected**: Overwriting the files in place with aggregates (loses provenance); keeping the originals public (privacy risk).
*Introduced by*: 261114-82fx-deidentify-participant-demographics

#### Cohort-level, not per-experiment, demographics
**Decision**: Publish one cohort row only.
**Why**: Per-experiment cells of 5–6 people add re-identification risk, and the paper reports the cohort only.
**Rejected**: Per-experiment age ranges and gender counts.
*Introduced by*: 261114-82fx-deidentify-participant-demographics

## Tasks

### Phase 1: Setup

- [x] T001 Add `data/metadata/participant_summary.csv` with the R3 row, and `data/withheld-sources.json` with the R2 entries <!-- R2 -->
- [x] T002 Remove `data/metadata/Subject Data.csv`; strip the `Sleep Hours` field (7th of 8 comma-separated fields) from every line of `data/metadata/experiment_03_biometric data.csv`, preserving all other fields byte-for-byte; verify the retained values are unchanged <!-- R1 -->

### Phase 2: Core Implementation

- [x] T003 `backend/src/pa/io/metadata.py`: replace `load_demographics` with `load_participant_summary`, add a `ParticipantSummary` model with validation, and drop `Trial.sleep_hours` <!-- R5 -->
- [x] T004 `backend/src/pa/results/schemas.py`: add `CohortSummary`; remove person demographic and sleep fields; add `cohort` to `PeopleExport` and `ResearchBundle`. `backend/src/pa/results/export.py`: pass `cohort` into the bundle <!-- R6 -->
- [x] T005 `backend/src/pa/results/build.py`: wire `load_participant_summary`; build people without demographics or sleep; include `cohort`; replace `demographics` parameters through `build_products`/`build_catalogue_products` <!-- R6 -->
- [x] T006 `backend/src/pa/analysis/study.py`: S5 without age/gender, `x="experiment"`, updated method and caveats <!-- R7 -->
- [x] T007 `backend/src/pa/analysis/rooms.py`: R9 as an experiment × axis aggregate bar product with cohort sleep on E3 rows; update the module docstring <!-- R7 -->
- [x] T008 `frontend/src/lib/research.ts`: update the zod schemas (remove per-person fields; add the optional `cohort` object). `frontend/src/pages/Explore.tsx`: remove the three columns and add the aggregate sentence <!-- R9 -->

### Phase 3: Integration & Edge Cases

- [x] T009 Update the tests: `backend/tests/test_exports.py` (replace demographic tests with summary loader tests, including invalid-row cases and the people/bundle cohort assertions); `backend/tests/test_ingestion.py` (no `sleep_hours`); `frontend/tests/fixtures.ts`; add assertions that S5/R9 contain no age, gender or per-person sleep <!-- R5 -->
- [x] T010 Regenerate the manifests with `python3 scripts/build_source_manifest.py`, then `--check` <!-- R4 -->
- [x] T011 Run `make pipeline` in the pinned environment. Confirm `signals_detail.json`/`timebase.json` are byte-identical and CP-B integration passes. Confirm the regenerated `artifacts/` contain no per-code age/gender/sleep <!-- R8 -->
- [x] T012 Run `make lint test site` (and `scripts/compare_reproduction.py` against the regenerated artifacts if feasible) <!-- R6 -->

### Phase 4: Polish

- [x] T013 Update `docs/data_card.md` and `docs/research/analysis-catalogue.md` (S5/R9 rows; the age/gender/sleep violins rationale) <!-- R10 -->

## Execution Order

- T001 and T002 come before T010, because the manifest must reflect the final data.
- T003–T007 come before T009 and T011.
- T011 regenerates the artifacts that T012's tests and site build read.

## Acceptance

### Functional Completeness

- [x] A-001 R1: `Subject Data.csv` is absent; the E3 CSV has no `Sleep Hours` header; all 60 E3 trials keep identical non-sleep values
- [x] A-002 R2: `data/withheld-sources.json` lists both originals with the exact sha256/size from R2
- [x] A-003 R3: `participant_summary.csv` contains exactly the R3 row
- [x] A-004 R4: `build_source_manifest.py --check` passes
- [x] A-005 R5: `load_participant_summary` exists and validates; `load_demographics` and `Trial.sleep_hours` are gone
- [x] A-006 R6: `people.json` and `bundle.json` have no age, gender or sleep keys on persons; `cohort` matches R3
- [x] A-007 R7: S5/R9 rows contain no age, gender or per-person sleep; R9 has no `participant_id`
- [x] A-008 R9: the Explore people table has three columns and renders the aggregate sentence from `cohort`
- [x] A-009 R10: the data card and catalogue describe aggregate-only demographics and the withheld originals

### Behavioral Correctness

- [x] A-010 R8: `signals_detail.json` and `timebase.json` are byte-identical to the pre-change versions; the pipeline completes without a CP-B hash error

### Removal Verification

- [x] A-011 R1: a repository grep (excluding `fab/` and `.git`) finds no per-code age, gender or sleep values in data, artifacts, frontend sources/fixtures or docs

### Scenario Coverage

- [x] A-012 R5: tests cover the valid summary and invalid summaries (negative count, min > max, missing column)

### Edge Cases & Error Handling

- [x] A-013 R7: R9 E2 rows carry null sleep fields with an explanatory caveat, not zeros

### Code Quality

- [x] A-014 Pattern consistency: new code follows the naming and structural patterns of surrounding code
- [x] A-015 No unnecessary duplication: existing utilities (`_rows`, `_number`, `product`, `counts`) are reused
- [x] A-016 Unavailable values are explicit: sleep is null with a reason, not a default

### Security

- [x] A-017 R1: no participant-identifying attribute remains linkable to a participant code in any published file

## Notes

- Check items as you review: `- [x]`
- All acceptance items must pass before `/fab-continue` (hydrate)
- If an item is not applicable, mark checked and prefix with **N/A**: `- [x] A-NNN **N/A**: {reason}`
- The owner approved implementing in this Claude session (Opus 5.5) instead of the configured Codex `gpt-6-sol` apply profile, which this harness cannot dispatch.

## Deletion Candidates

- `docs/history/legacy-site-assets/FINDINGS/Demographic Insights/*.png` (6 files) — legacy per-trial age/gender/sleep violin plots now contradict the aggregate-only policy (data card, analysis-catalogue violins row); owner decision whether to withhold them like the CSV originals (they are inventoried `legacy_site_asset` sources).
- `backend/src/pa/results/build.py` `build_products(... participant_summary=None)` fallback to `load_participant_summary()` — the only production caller always passes the summary; the implicit file read in a pure builder could be dropped by making the parameter required.

## Assumptions

| # | Grade | Decision | Rationale | Scores |
|---|-------|----------|-----------|--------|
| 1 | Confident | R9 kept as an experiment × axis aggregate bar product rather than retired | The `product()` framework supports the `bar` type and extra row fields; keeping the ID avoids catalogue/route churn | S:65 R:75 A:75 D:65 |
| 2 | Confident | Cohort summary added to `PeopleExport` and `ResearchBundle` as `cohort` | The frontend reads the bundle; the people export is the natural home | S:70 R:75 A:75 D:70 |
| 3 | Certain | Sleep aggregates: n=60, mean 6.75, min 3.0, max 8.5 h | Computed in-session from the original CSV before removal | S:90 R:85 A:90 D:90 |
| 4 | Confident | Trailing empty column of the E3 CSV kept | Minimises the byte diff; the loader ignores empty headers | S:70 R:85 A:75 D:70 |
| 5 | Certain | Implemented by Claude in-session with owner approval (routing override) | The owner chose "Claude does it here" | S:95 R:85 A:90 D:90 |

5 assumptions (2 certain, 3 confident, 0 tentative).

## Apply Log

- **Pipeline:** the first `make pipeline` stopped at the spatial-null cache guard, as designed. `data/MANIFEST.sha256` and `io/metadata.py` are fingerprinted, while the effective cohort hash was unchanged. The old null outputs were backed up, removed and fully regenerated (1,000 seeded draws, ~64 min). Draws, observed folds and `null_mean_mae` are identical to the previous artifact; only timestamps and the fingerprint differ.
- **CP-B pinned artifacts:** `signals_detail.json`, `timebase.json` and `qc_review.json` are byte-identical before and after (sha256 checked).
- **Semantic artifact diff** (volatile hash/time keys ignored): substantive changes only in `analysis/S5.json`, `analysis/R9.json`, `people.json` and `bundle.json`. The model binary is unchanged; `artifacts/model/metadata.json` differs only in `base_git_revision` and the manifest hash.
- **Checks:** `make lint test site` passed except one Playwright assertion that depended on the removed gender column. That test was updated and its spec passes 3/3. A privacy sweep of artifacts, data, frontend and docs found no participant code paired with age, gender, occupation or sleep.
- **Housekeeping:** screenshots re-captured by the Playwright run were restored, and the intermediate `model_null_checkpoint.json` was removed.
