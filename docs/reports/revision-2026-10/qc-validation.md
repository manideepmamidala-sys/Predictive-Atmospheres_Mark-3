# Approved v1.2 QC implementation validation — 2026-10-10

The owner approved the unchanged v1.2 source at CP-Spec, SHA-256 `51c01ef6ccdf2f4318ac786d1bb39afeb1aa2bcf3bc93039479a4ed2454603ac`, and chose ordinary Git at CP-A. Tasks T013–T018 are implemented. The [independent review](qc-implementation-review.md) found no unresolved must-fix in this checkpoint slice. This is preparation for the owner CP-B decision, not a physiology or model result verdict.

`make verify-data` passed the canonical manifest and backend source checks for all 313 retained originals. `cd backend && uv run --frozen pa audit` exported 160 conditional timebase rows: six >10% duration discrepancies and 38 counter-flagged files. A fresh `pa signals` run produced 160 approved-v1.2 trial records. Automated screening yielded bilateral EEG features on 160, HR on 71 and primary 30-second RMSSD on 18; these counts do not certify cortical or cardiac validity. Each row includes 250/256/500/512 Hz scenarios and a five-second ECG/EEG onset sensitivity. Experiment-specific raw amplitude references are exported. The signal file retains the exact approved hash.

`pa signal-review` produced [CP-B](CP-B.md), a queue of 346 pending trial/signal decisions across 152 flagged trials, and 330 raw/filtered trace and spectrum panels. The queue also has a 160-trial coverage ledger. All 487 relative links in CP-B and every queue panel path resolve. After adding ECG onset sensitivity, a canonical comparison confirmed that every primary QC field remained byte-equivalent to the data used to render the panels; the queue's final signal and timebase SHA-256 values match the current products. The worst logged-duration mismatch is E3:Subj_M:Rm_021 at 73.46% under conditional 500 Hz. All 346 decisions and the owner verdict remain pending; no F/H blanket exclusion was made.

`cd backend && uv run --frozen pytest -q` passed **97 tests** with one existing Starlette/httpx deprecation warning. `uv run --frozen ruff check src tests` and `git diff --check` passed. Direct `pa affect` exited 1 with `v1.2 dependent science held until owner CP-B approval`, the expected checkpoint behavior; the old v1.1 fitted model is incompatible with the approved v1.2 method and the API reports not ready. Existing v1.1 affect/model/site products were not regenerated or relabelled as v1.2.

| Approved evidence product | SHA-256 |
| --- | --- |
| `artifacts/results/timebase.json` | `07927368f68553d069ced78235d5131693fec0f2a74fd3df98bfc88660ccc604` |
| `artifacts/results/signals_detail.json` | `ec1001ac3bc53c15d3afd3b565756666b2b418670057ce8ba8011036d999c4b1` |
| `artifacts/results/qc_review.json` | `0c2dd17cba43a7eb6eb597dab4383b78ca055a6a5ddd2806a082d6c918195066` |

CP-B owner decisions and T019 eligibility integration must precede dependent affect, model, public export and whole-pipeline validation. The site/browser suite was already validated in [preparation validation](preparation-validation.md); no frontend source was changed in this slice.
