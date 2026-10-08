# Hydrate handoff — implemented state on 2026-10-08

The existing `docs/memory/website_architecture.md` describes the retired Streamlit/root-`src` system and is not authoritative for this implementation. During Fab hydrate, replace it with indexed architecture, research and operations memory based on the implemented code and these records. Do not carry over the old PyTorch/Streamlit/fixed-target/confirmed-rate assumptions.

| Memory topic | Implemented evidence to distill |
|---|---|
| Architecture | `backend/src/pa/` CLI, `api/app.py`, `features/schema.py`, `modeling/artifact.py`; `frontend/src/App.tsx`, `src/lib/research.ts`, `src/api/client.ts`; [phase 7](phase-7.md), [phase 8](phase-8.md), [interaction map](interaction-map.md). Seven static research routes; predict/optimize alone require API. |
| Research | [analysis specification](../specs/analysis-v1.md), [checkpoint](analysis-checkpoint.md), [decisions](../../DECISIONS.md), [data card](../data_card.md), [model card](../model_card.md), [phases 1–6](phase-1.md). Conditional unconfirmed rate, operational QC with visual limitations, distinct fusion/model cohorts, weak held-out-room result. |
| Operations | [operations guide](../operations.md), [reproduction](reproduction.md), [release readiness](../release-readiness.md), `Makefile`, `.github/workflows/ci.yml`, `render.yaml`, `frontend/vercel.json`. Frozen local build validated; external deployment, DOI, license scopes and named biometric publication remain separate. |

The independent T007 reviewer was a fresh Codex `gpt-6-astra`/`xhigh` worker, with initial FAIL and fresh PASS findings retained in the checkpoint reports; the coordinator recorded the gate verdict. The Fab coordinator still owns the separate final independent full review, hydrate verdict and any PR/release steps. No review that has not run should be inferred from this handoff.
