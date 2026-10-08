# Audit and analysis specification checkpoint

Date: 2026-10-08. The source manifest, `artifacts/results/audit.json`, `docs/reports/phase-1.md`, `docs/specs/analysis-v1.md`, `backend/src/pa/decisions.yaml` and `DECISIONS.md` are ready for an independent review of acquisition evidence, conditional rate selection, scientific assumptions, missingness, failure handling and fold separation.

At checkpoint creation, `uv run --frozen pytest -q tests/test_audit.py tests/test_ingestion.py tests/test_manifest.py tests/test_config.py` returned `6 passed in 0.21s`; `uv run --frozen pa audit` returned `Audited 160 recordings`; `uv run --frozen pa verify-data` returned `Source inventory verified`. These checks verify source reading and audit mechanics, not physiological interpretation.

**Review dispatch:** fresh native Codex `gpt-6-astra`, `xhigh` worker completed on 2026-10-08.
**Review findings:** [Independent report](audit-spec-review.md) confirms preservation, ingestion and audit counts, but identifies three must-fix specification gaps: sustained EEG saturation, ECG quality/gap/usable-duration rules, and reproducible nested model selection. It also requests accurate filter wording, manifest consistency checks and shared audit settings.
**Initial coordinator verdict:** FAIL, adopting all three must-fix findings. The author amended the specification and decision history and added adverse synthetic regression checks before re-review.

**Re-review:** a fresh native Codex `gpt-6-astra`, `xhigh` worker reviewed specification v1.1.0 and recorded [PASS with no remaining methodology blockers](audit-spec-rereview.md). The reviewer reproduced 40 tests and additional independent clipping, noise, gap, timing and leakage probes. The report records the reviewed hashes and operational limits.

**Coordinator verdict:** PASS

The coordinator adopts the re-review verdict on 2026-10-08 and releases conditional real-data signal processing under the reviewed specification. Before real model comparisons, T014 must fix nonfinite component handling and global-minimum tie selection and complete both baseline reports and retained evaluation evidence. This checkpoint does not complete those tasks or replace final Fab review. Required visual signal review, sensitivities, cohort exclusions and unavailable outcomes remain downstream obligations. Any subsequent method change requires a dated decision amendment and affected rerun.
