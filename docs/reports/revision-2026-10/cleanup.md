# Verified current-tree cleanup — 2026-10-10

The [source inventory](source-inventory.md) and its [machine record](source-inventory.json) were written before deletion. The source-render and legacy-image groups were compared file by file against the prior SHA-256 inventory at both their old and retained paths. The two root and two `docs/thesis/` PDFs, and the untracked InDesign ZIP, were checked against exact Windows originals immediately before removal. The Windows originals were read only and never altered. No raw CSV, metadata CSV, unique render, linked historical image, active Fab file, decision record, research report or Git history was removed.

| Removed project path | Reason / retained source |
| --- | --- |
| `rooms/` (30 files) | Identical originals retained at `data/renders/raw/`. |
| `frontend/assets/IMAGES/` (116 files) | Identical historical image evidence retained at `docs/history/legacy-site-assets/`; frontend runtime does not import the old tree. |
| Two root thesis PDFs and two `docs/thesis/` PDF copies | Exact Windows `Machine Learning/Predictive Atmospheres_Mark 3/` originals; page-referenced findings/prototype knowledge retained in `docs/research/thesis-source-context.md`. Hashes retained in `source-inventory.json`. |
| Untracked `docs/thesis/ManideepMamidala_ThesisBooklet Folder.zip` | Exact Windows Booklet package original; linked chart concepts mapped in `docs/research/analysis-catalogue.md`. ZIP hash and content count retained. |
| `EXECUTION_PLAN.md`, `PROJECT_REPORT.md`, `current_state_analysis.md`, `deep_system_audit.md`, `website publishing.md`, `docs/history/EXECUTION_PLAN-legacy.md`, `MARK3_REVISION_PLAN.md` | Superseded standalone planning/retired-system narratives. Relevant study/studio context and complete chart catalogue are retained in maintained research docs; authorized work is in active Fab intake/plan. The tracked files remain recoverable in Git history; the untracked October guide is represented by the complete new intake, plan and catalogue rather than moved to another public archive. |

The seven removed narrative SHA-256 values, in table order, were `84041c7fff235954460ff99c5f2620330571771252a10e6402a11ba67ba32176`, `18ca0b240fbbfbca3b012114b95cdeb791ac4d0ca3bc4c3bdb48e71fbe47c299`, `b890506b0b3b564fb1e7df4a0114e37d5d955698cd36f191248153808e715fb1`, `014bd6086f4bb4cae5bf33941b47a7aace1b0cabc20b2580867a0dde9bc6bc6c`, `252017a03ac3efe04a470d3bbeedabeb1476a74f4af903cc64d435c4d591cac2`, `7b4330c738d647a61bb534892556f2dc5597655b826fd851bf029dfc67ebc3b9` and `adaa40abab7c4f131279157a76f443a2ef4b8f29c7c282b95e86a722f56ab3ff`.

The untracked `docs/thesis/ManideepMamidala_TextoftheThesis.docx` remains because no exact Windows original was found. The current `docs/reports/project-review-2026-10.pdf` also remains as an analysis source. Neither is added to the canonical source manifest or public site. These are explicit incomplete cleanup dispositions, not evidence that a private original was deleted.

The canonical manifest now contains 313 retained original files at current paths. The historical `docs/reports/migration-inventory.json` remains for the first migration's state and original hashes. Repointing source verification does not turn historical model results into new scientific results; existing approved-method regression and content/provenance comparisons are recorded separately.
