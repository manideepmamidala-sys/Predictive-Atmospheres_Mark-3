# Phase 0 — Preservation and governance

Date: 2026-10-08. Branch: `261008-ymhz-research-platform-rebuild`. Implementation dispatch: Codex `gpt-6-sol`, `high`. Fab stage transitions and final independent review belong to the coordinator.

The committed legacy snapshot is `41d6ba507965d5159a679e65962fb3d02963a551` (Git `HEAD` before implementation). The original worktree also held modified Fab version/config files and untracked AGENTS.md, EXECUTION_PLAN.md, PROJECT_REPORT.md and `rooms/`. Their pre-edit status and file hashes are recorded in `docs/reports/migration-inventory.json`; this commit reference alone does not contain those uncommitted bytes. The previous execution plan is preserved as `docs/history/EXECUTION_PLAN-legacy.md`.

The inventory covers 315 source files: 160 raw recordings, 7 metadata CSVs, 30 room renders, 116 legacy website images, and 2 thesis PDFs. `data/MANIFEST.sha256` records hashes of original paths. The 30 renders were copied to `data/renders/raw/`, 116 site images to `docs/history/legacy-site-assets/`, and both thesis PDFs to `docs/thesis/`; all 148 destination hashes matched the source manifest immediately after copying. Original paths remain present at this checkpoint.

Only these historical Fab change directories were removed: `260915-a2td-website-delivery`, `260915-bc1i-update-repo-docs-fix`, `260915-vwf1-migrate-react-frontend`, and `261008-rvq3-decouple-streamlit-fastapi`. Each contained intake/plan/status records, and the first three also contained history files. The obsolete UTF-16 `.active` pointer named the deleted `bc1i` record and was removed. The current `ymhz` change, archive sentinel, Fab tools and `.agents/` are retained.

`EXECUTION_PLAN.md` now points to the Fab plan and lists phases 0–9 as evidence milestones. The constitution and project context reflect the replacement architecture, descriptive fusion, user-selected target and dual-theme site. `fab/project/config.yaml` routes the backend/frontend source and test paths while preserving the exact AGENTS.md Codex model/effort profiles and native dispatch.

Checks observed: the inventory script printed `recording=160, metadata=7, room_render=30, legacy_site_asset=116, thesis_pdf=2`; copied-destination verification printed `verified copied destinations: 148 mismatches: []`; `fab preflight 261008-ymhz-research-platform-rebuild` reported apply active with 30 tasks. Source manifest verification and frozen setup are completed in later phase evidence.

At this preservation checkpoint, responsibility-mapped legacy **runtime** retirement was still pending; [phase 4](phase-4.md) now records its exact file inventory and replacement. Original `rooms/` and legacy image assets remain intentionally preserved as source evidence. The historical roadmap contains incorrect protocol/release assumptions and is archived as historical material, not active instructions.
