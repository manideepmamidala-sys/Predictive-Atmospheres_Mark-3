# Intake: De-identify participant demographics

**Change**: 261114-82fx-deidentify-participant-demographics
**Created**: 2026-11-14

## Origin

> De-identify participant demographics in the public repository and website. Replace per-person age, gender, occupation (data/metadata/Subject Data.csv) and per-trial/per-person sleep hours (Sleep Hours column in data/metadata/experiment_03_biometric data.csv) with aggregate-only records; stop the backend pipeline, generated results and the frontend Explore page from exposing per-person demographics or sleep; update tests, data manifests and docs; regenerate artifacts and verify CI reproducibility. Do NOT rewrite git history. Commit locally; ask before pushing.

Conversational. This arose while the owner was preparing the research paper *How people experience virtual rooms* (kept outside this repository). The paper reports demographics only in aggregate: 10 architects, aged 25–28, 5 women and 5 men. The paper links this public repository as its data and code source. The owner chose:
- (a) **Full fix on a branch**, not a data-files-only edit and not "do nothing".
- (b) **No git-history rewrite**: current files only; old values remain in history.

AGENTS.md routes implementation to Codex `gpt-6-sol`. That routing is unavailable in this Claude session, so the limitation is reported and the work is done in-session.

## Why

1. **Problem.** The 10 participants are the owner's classmates and acquaintances. Public files map each participant code to identifying attributes:
   - `data/metadata/Subject Data.csv` maps codes (Subj_A…Subj_M) to age, gender and occupation.
   - `artifacts/results/people.json`, `bundle.json` and the analysis products S5/R9 republish age, gender and per-person sleep hours.
   - The public website Explore page renders a per-person table with Age, Reported gender and Sleep (h).

   Within a known cohort of 10, age plus gender per code can re-identify individuals. Those codes link to biometric recordings and ratings.
2. **Consequence if not fixed.** Participants gave verbal consent to the use of *anonymised* data in publications. They cannot be re-contacted for written consent. Keeping identifying per-person attributes public contradicts the consent basis stated in the paper, and Zenodo's requirement that human-subject data be anonymised. Constitution V also says participant identities SHALL not be silently published.
3. **Why this approach.** Aggregates keep the descriptive value (cohort composition, E3 sleep range) without per-person linkage.
   - Rewriting history was rejected by the owner (force-push risk).
   - A data-only edit was rejected because it would break the pipeline/CI and leave the website exposing old artifacts.
   - Constitution I (preserve source evidence) is honoured by **withholding**, not deleting. The originals stay with the owner privately, and their SHA-256 and size are recorded in the repository as withheld sources.

## What Changes

### 1. Source data (`data/`)
- **Remove** `data/metadata/Subject Data.csv` from the repository tree.
- **Add** `data/metadata/participant_summary.csv`, a single aggregate row derived from the withheld originals:
  ```csv
  scope,participants,age_min,age_max,age_mean,female,male,occupation,e3_sleep_trials,e3_sleep_hours_mean,e3_sleep_hours_min,e3_sleep_hours_max
  all,10,25,28,26.0,5,5,Architect (10),60,<mean>,<min>,<max>
  ```
  Sleep aggregates are computed from the 60 E3 trial rows of the original `Sleep Hours` column, before removal.
- **Modify** `data/metadata/experiment_03_biometric data.csv`: drop the `Sleep Hours` column and any trailing empty column. All other bytes and values are unchanged; row order and other columns are preserved exactly.
- **Add** `data/withheld-sources.json`. For each withheld original, record path, original sha256, size_bytes, reason ("participant privacy: per-person demographics/sleep") and custody ("retained privately by the study owner; not redistributed"). Covers `Subject Data.csv` and the original `experiment_03_biometric data.csv`.
- **Regenerate** `data/source-inventory.json` and `data/MANIFEST.sha256` via `python3 scripts/build_source_manifest.py`. `--check` must pass.

### 2. Backend pipeline (`backend/src/pa/`)
- `io/metadata.py`:
  - Replace `load_demographics()` (per-ID map) with `load_participant_summary()`, which returns the single aggregate record and validates its fields.
  - Remove `sleep_hours` from the per-trial metadata record, and stop reading `Sleep Hours`.
- `analysis/study.py` **S5**: keep one row per participant code × experiment with `trial_count`, `room_count` and `complete_fusion_count`, but **remove `age` and `gender`**. Axis becomes `x="experiment"`; the method, caveats and units text are updated.
- `analysis/rooms.py` **R9**: remove per-person rows. R9 becomes an aggregate cohort/experiment product with no `participant_id`, no age/gender and no per-person sleep: per experiment, participant count, rating-trial count, mean rating per axis, plus E3 sleep aggregate (n, mean, min, max) from `participant_summary.csv`. The question/takeaway/caveats are reworded to state that the study reports demographics and sleep in aggregate only. If the product framework cannot express this cleanly, R9 may be retired with its catalogue entries updated (Tentative; decide at plan).
- `results/schemas.py` / `results/build.py`:
  - Remove `age`, `gender` and `sleep_hours` from `PersonRecord`, and the four sleep fields from `PersonExperimentRecord`.
  - Add a cohort-level aggregate record to the people export (or the bundle) carrying the `participant_summary.csv` values.
- Any API/OpenAPI schema mirroring these models is regenerated (`artifacts/results/openapi.json`).

### 3. Frontend (`frontend/src/`)
- `lib/research.ts` zod schemas: drop the per-person `age`, `gender` and sleep fields; add the cohort aggregate.
- `pages/Explore.tsx`: remove the Age, Reported gender and Sleep (h) columns from the per-person table. Show one aggregate sentence or table instead, e.g. "10 participants, all architects, aged 25–28 (mean 26.0); 5 women, 5 men. E3 sleep (60 trials): mean …, range …–… h."
- Update `frontend/tests/fixtures.ts` and any tests or labels referencing these fields.

### 4. Generated artifacts and verification
- Run `make pipeline` (or the CI-equivalent pinned environment) to regenerate `artifacts/results/*`. The CP-B review ledger hash checks (`signals_detail.json`, `timebase.json`) must remain valid. These files do not embed the manifest hash, and raw recordings are unchanged, so they should regenerate byte-identically. If not, stop and report; do not hand-edit hashes.
- Run `make lint test site`, `python3 scripts/build_source_manifest.py --check`, and the reproduction comparison used by CI (`scripts/compare_reproduction.py`), if runnable locally.
- Grep check: no committed file outside `fab/` and git history contains per-code age/gender/sleep. In particular, check `artifacts/`, `frontend/dist` (if tracked) and `docs/`.

### 5. Documentation
- `docs/data_card.md`: describe aggregate-only demographics, withheld originals and the reason.
- `docs/research/analysis-catalogue.md`: update the S5/R9 descriptions; remove the per-person sleep dots wording.
- Memory files (hydrate) per Affected Memory.

### 6. Git and deployment
- Branch `261114-82fx-deidentify-participant-demographics`, based on `origin/main`. The local HEAD `a3c527c` has a tree identical to `origin/main` `aa6f7b7`.
- Commit locally. **Ask the owner before pushing or opening a PR.** Redeploying the Vercel site is a separate, owner-approved step after merge.
- **No history rewrite** (owner decision).

## Affected Memory

- `research/protocol`: (modify) participant demographics now aggregate-only; per-person originals withheld with recorded hashes; E3 sleep column removed from the public CSV.
- `research/analysis`: (modify) S5 without age/gender; R9 aggregate-only (or retired).
- `architecture/platform`: (modify) metadata loader/aggregate contract; people export schema without per-person demographics/sleep.
- `architecture/website`: (modify) Explore page shows aggregate cohort description, not a per-person demographic table.

## Impact

- **Data:** two metadata files; new `participant_summary.csv` and `withheld-sources.json`; regenerated manifest and inventory.
- **Backend:** `io/metadata.py`, `analysis/study.py`, `analysis/rooms.py`, `results/build.py`, `results/schemas.py`; tests `backend/tests/test_exports.py`, `test_ingestion.py` and others asserting demographics.
- **Artifacts:** `artifacts/results/{people,bundle,openapi,manifest,study,…}.json`, `analysis/S5.json` and `R9.json`, plus anything that hashes `data/MANIFEST.sha256` (audit, model artifact metadata, catalogue).
- **Frontend:** `lib/research.ts`, `pages/Explore.tsx`, `tests/fixtures.ts`.
- **Docs:** data card, analysis catalogue, memory.
- **Risk:** the model artifact records a dataset manifest hash, and its trusted loader checks hashes, so it must be regenerated consistently by the pipeline, not patched.

## Open Questions

- Can the analysis-product framework (`product()`) express an aggregate-only R9 without a scatter of per-person points, or should R9 be retired?
- Does the trusted model artifact loader require retraining when only `data/MANIFEST.sha256` changes, and is the retrained output byte-identical under the pinned CI kernels?

## Assumptions

| # | Grade | Decision | Rationale | Scores |
|---|-------|----------|-----------|--------|
| 1 | Certain | Full fix on a branch: data, backend, artifacts, frontend, tests, docs | Owner chose "Full fix on a branch (Recommended)" | S:95 R:90 A:95 D:95 |
| 2 | Certain | No git-history rewrite; current files only | Owner chose "No, current files only" | S:95 R:95 A:95 D:95 |
| 3 | Certain | Commit locally; ask before push/PR/redeploy | Owner instruction pattern; outward-facing actions need confirmation | S:90 R:90 A:90 D:90 |
| 4 | Confident | Withhold originals (record sha256/size in `data/withheld-sources.json`) instead of silently deleting | Constitution I requires preserving and checksumming source evidence; the originals also exist in the owner's thesis archive | S:75 R:70 A:80 D:75 |
| 5 | Confident | Aggregate demographics published as one cohort row (no per-experiment age breakdown) | Per-experiment cells of 5–6 people add re-identification risk for little value; the paper uses cohort-level values | S:70 R:75 A:75 D:70 |
| 6 | Confident | Drop the `Sleep Hours` column from the public E3 CSV; publish only an E3 sleep aggregate | Owner's request named per-trial/per-person sleep; aggregate keeps descriptive value | S:80 R:70 A:80 D:75 |
| 7 | Confident | S5 keeps per-code trial/room/fusion counts without age/gender | Counts per code are not identifying and support the existing participation view | S:70 R:80 A:75 D:70 |
| 8 | Tentative | R9 becomes an aggregate product (fallback: retire R9 and update catalogue/UI IDs) | Depends on product-framework constraints; decided at plan | S:55 R:70 A:60 D:55 |
| 9 | Confident | CP-B ledger hashes stay valid because `signals_detail`/`timebase` do not embed the manifest hash | Verified by inspecting artifact headers in-session; raw recordings unchanged | S:70 R:60 A:70 D:65 |
| 10 | Certain | Implementation in this Claude session despite AGENTS.md Codex routing; limitation reported | Codex dispatch is unavailable here; AGENTS.md requires reporting instead of silent substitution | S:90 R:80 A:85 D:85 |

10 assumptions (4 certain, 5 confident, 1 tentative, 0 unresolved).
