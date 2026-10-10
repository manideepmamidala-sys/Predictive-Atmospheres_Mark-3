# Source inventory and preservation check — 2026-10-10

This is the current-tree cleanup precondition. It records read-only source inspection and byte checks, not new signal processing or model evaluation. The original 2026-10-08 [migration inventory](../migration-inventory.json) remains a historical path map. `data/source-inventory.json` and `data/MANIFEST.sha256` now identify retained canonical source paths. `python3 scripts/build_source_manifest.py --check` verifies their bytes without reading private PC paths.

| Evidence | Count | Retained canonical path | Verified original/copy relationship |
| --- | ---: | --- | --- |
| Raw `Counter,Channel1,Channel2,Channel3` CSVs | 160 | `data/raw/` | All 160 match historical SHA-256; 296,535,120 source bytes. |
| Source metadata CSVs | 7 | `data/metadata/` | All 7 match historical SHA-256; 12,414 bytes. |
| Original Lumion room JPEGs | 30 | `data/renders/raw/` | All 30 match `rooms/` and historical SHA-256; 150,805,079 source bytes. |
| Historical site images | 116 | `docs/history/legacy-site-assets/` | All 116 match `frontend/assets/IMAGES/` and historical SHA-256; 67,811,155 source bytes. Some illustrations are third-party material; preservation is not a new license grant. |

The verified canonical source inventory contains **313 files**. Browser WebP renders in `frontend/public/rooms/` are separate derivatives, not interchangeable with originals. Historical `rooms/` and `frontend/assets/IMAGES/` copies are byte-identical duplicates and eligible for current-tree removal. Raw recordings, metadata and canonical render/history assets are not cleanup targets.

## Thesis and package documents

| Document | SHA-256 | Bytes | Windows-original check and action |
| --- | --- | ---: | --- |
| 48-page presentation `PredictiveAtmospheres_ManideepMamidala.pdf` | `821bff1820eac354d6496e9845a542a3783f15cc2b084c36aa0d1c8d679ae43a` | 13,561,838 | Root and `docs/thesis/` copies equal the Windows `Machine Learning/Predictive Atmospheres_Mark 3/` copy. Remove project copies after source context capture. |
| 104-page booklet `ManideepMamidala_ThesisBooklet.pdf` | `d633e20132cacab155af28e6b0d93ee345d9a2e487d8cdf6b6aa12d9a56297ac` | 25,566,729 | Root and `docs/thesis/` copies equal the Windows Mark-3 copy. The InDesign package includes a near-identical 25,566,717-byte PDF with a **different** SHA; it remains under Windows ownership. Remove project copies after source context capture. |
| Booklet InDesign package ZIP | `044169a5ea2639c25b751a5efaf30cecb17d6007e428d05d2617b682a7ac3e40` | 73,702,232 | Untracked project ZIP equals Windows `Booklet/ManideepMamidala_ThesisBooklet Folder.zip`; 93 entries include 79 linked graphic files, 8 font files, IDML, INDD and PDF. Remove project copy after reading. |
| `ManideepMamidala_TextoftheThesis.docx` | `bd205b8fe18129a2c5543a8481b2701babdf377477e99c726a112f7e28be4411` | 31,855 | Its text was inspected, but an exact Windows original was **not found** in the thesis tree; retain the untracked project file until original preservation is verified. Do not add it to the public site or active manifest. |

The Windows thesis tree was inspected read-only. Relevant folders include Presentation, Booklet, Experiment Design, Findings, Machine Learning, Rhino Integration and Illustrations. The `Machine Learning/Predictive Atmospheres_Mark 3.zip` source package contains the earlier Streamlit studio and optimization service. The `Rhino Integration` folder contains `trial_5 final term 3 plugin.gh` and `trial_6 nanobanana.gh`. [Maintained thesis context](../../research/thesis-source-context.md) records the architectural question, experiment diagrams, formula and prototype distinctions with page references. Windows files were neither edited nor selected as build dependencies.

The separately authorized researcher portrait `/mnt/d/RUNNING FILES/Portfolio 2.0/IMG_2644.png` exists (2268 × 4032 RGBA, 5,170,317 bytes, SHA-256 `d81a4475ef87720089a5a7949453b711cd846798a8edcfb15696c792e42392bb`). Its original remains outside the project; a derived website copy belongs to the later visual workstream and is not part of source cleanup.

## Cleanup boundaries

The previous `EXECUTION_PLAN.md` describes the completed seven-page rebuild and duplicates its retained Fab plan and current research records. `PROJECT_REPORT.md` describes the retired Streamlit architecture and unverified historical method defaults. Their source meaning has been captured in the current protocol/specification, thesis context and active intake/plan. Retire these standalone root narratives without moving them into another public archive. Retain the active change's `intake.md`, `plan.md`, Fab machinery, `DECISIONS.md`, `docs/specs/analysis-v1.md`, data/model cards, current operational documentation, previous Fab provenance and meaningful research reports. The October review PDF remains a current analytical source pending a verified external original; it is not part of automatic deletion.

No Git history rewrite is planned or authorized. Deleted project paths remain recoverable from repository history where tracked; that history still contains their bytes and is not reduced by current-tree cleanup. The retained file sizes and proposed storage handling are in [CP-A](CP-A.md).
