# Preparation validation — 2026-10-10

This validates only the authorized preparation slice (plan T001–T012). The v1.2 methods remain a draft at CP-Spec. No new v1.2 signal, affect, validity or model analysis was executed, and CP-A did not authorize an LFS migration.

## Preservation and cleanup

- The [machine inventory](source-inventory.json) records original sizes, roles, SHA-256 values and removal dispositions. All 313 retained canonical source hashes match their pre-cleanup counterparts: 160 recordings, 7 metadata files, 30 room renders and 116 historical images. `python3 scripts/build_source_manifest.py --check` and `make verify-data` passed after the source-path migration.
- Both root thesis PDFs and their `docs/thesis/` copies were byte-identical to the checked Windows Mark-3 originals. The removed InDesign ZIP matched its Windows Booklet original. The removed room renders and frontend historical images matched canonical retained copies file by file. The Windows source folders and originals were read only.
- The thesis DOCX had no verified matching Windows original and remains in `docs/thesis/`. The current project-review PDF also remains. See [cleanup](cleanup.md) for exact removals and retained-source paths. No unique raw signal, metadata, render, asset evidence, active Fab record or Git history was removed.
- A relative Markdown-link scan across the maintained README and 56 project documents found no unresolved local links after retiring the old paths. The ignored, retained DOCX is not used by routine builds.

## Unchanged-method reproduction

`make pipeline` ran the **already approved v1 methods** after the path changes. It passed with 160 audited and processed recordings, 10 representative signal-review panels, 160 affect rows, 14 eligible model trials, seven research exports and generated OpenAPI. The model remained `not_better_than_baseline`. Comparison of 15 generated result JSON/model-metadata products against `HEAD` found only source-manifest/code-tree provenance values and product digests attributable to them; numerical and scientific-result fields did not change. `artifacts/model/model.joblib` remained byte-identical. The pre-existing user edit in `artifacts/model/metadata.json` was preserved; pipeline provenance now truthfully reports an uncommitted working tree. These derived provenance changes are expected before a commit and are not v1.2 results.

CI now snapshots the committed derived products, regenerates them and compares substantive content/model bytes. The comparison excludes volatile checkout revision/status from scientific identity while retaining those values in artifact metadata and compatibility checks. Targeted artifact/export tests passed (27 tests in the repair worker's run), and the repaired comparator passed a self-comparison. Since source paths intentionally changed on this branch, comparing its generated outputs directly with the prior committed revision is expected to show provenance differences until a new reviewed snapshot is committed.

## Build and browser checks

- `make lint test site`: Ruff, API-schema and TypeScript checks passed; backend tests passed **83/83** with one deprecation warning. Its first Playwright invocation failed **25/25 at Chromium launch** because this host lacked `libnspr4`, `libnss3` and `libasound2`; it did not report application assertions. The live fitted-service test was intentionally skipped.
- The missing Debian runtime libraries were downloaded and extracted only under `/tmp/pa-browser-libs`, with `LD_LIBRARY_PATH` set for the test process. No system package or app code was changed for this environment issue. `ldd` then showed no missing Chromium libraries. A direct frontend rerun passed **25 Playwright tests**, with the same one intentional live-service skip.
- `make site` passed the production Vite build, and `make verify-data` passed both the 313-source canonical manifest check and backend `pa verify-data`. The Playwright capture had rewritten a tracked screenshot; that test-only byte change was restored after verification.

No owner checkpoint is inferred from these checks. CP-A awaits a storage choice, CP-Spec awaits explicit approval of the exact draft hash, and later manual QC, result, landing-copy and final-visual checkpoints remain open.
