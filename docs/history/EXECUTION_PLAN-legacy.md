# Predictive Atmospheres — Rebuild Execution Plan (v1)

This document is the single source of truth for rebuilding Predictive Atmospheres into a research-grade, reproducible project with a redesigned research website. It is written to be executed phase by phase by a coding agent (Codex or Claude Code in a Linux terminal) and reviewed by agents and by the project owner.

Owner: Manideep Mamidala
Branch: `rebuild/v1` (created from `main`; `main` is tagged `v0.2.0-legacy` before any change)
Primary goal: research first (defensible, reproducible, honestly reported), then a portfolio-quality research website.

---

## Contents

1. How to use this plan
2. Locked decisions from the planning discussion
3. Files the owner must provide before or during execution
4. Target repository layout
5. Agent rules (contents for `AGENTS.md` and `CLAUDE.md`)
6. Record keeping and documentation system
7. Dependencies and skills
8. Phases 0–9 (task cards)
9. Website: information architecture and design system
10. Risk register
11. Definition of done

---

## 1. How to use this plan

Work strictly one phase at a time. Each phase card has a goal, inputs, tasks, outputs, acceptance checks, and a list of "stop and ask" points. A phase is complete only when every acceptance check passes and its phase report is written.

The workflow for each phase:

1. Create a branch `phase/<n>-<short-name>` from `rebuild/v1`.
2. Start a fresh agent session. Paste the "Prompt to give the agent" block from the phase card.
3. The agent works, runs the acceptance commands, and writes `docs/reports/phase-<n>.md`.
4. Start a second, separate agent session as the reviewer. Paste the "Review prompt" from section 6.4. The reviewer must not edit code; it only reports.
5. Fix anything the reviewer raises, then merge into `rebuild/v1` and add the `CHANGELOG.md` entry.
6. Any "stop and ask" item is answered by the owner and recorded in `DECISIONS.md` before work continues.

Phases 0 → 7 are strictly sequential. Phase 8 (website) may start its design-system and landing-page layout work after Phase 7 freezes the API contract, using fixture data; the data-driven pages are wired only after Phases 3–5 are merged. Phase 9 is last.

---

## 2. Locked decisions from the planning discussion

These are recorded verbatim in `DECISIONS.md` during Phase 0. Agents may read them but must never change them; only the owner can, by adding a new numbered decision that supersedes an old one.

| ID | Decision |
|---|---|
| D-001 | Recording hardware: Upside Down Labs NPG Lite (Beast pack), recorded via Chords. Sampling rate is verified from the data in Phase 1 (evidence so far: ~500 Hz, not 256 Hz). The 0–255 `Counter` column is a packet counter, not a time base. |
| D-002 | Channel map: Channel1 = right forehead (Fp2), Channel2 = left forehead (Fp1), reference/ground on the earlobe behind the ear, Channel3 = ECG from the wrists (limb lead I). All documentation and the website call the EEG measure "prefrontal alpha asymmetry (Fp2–Fp1)", never F3/F4. |
| D-003 | Protocol: VR headset; participants stood in place and rotated to view each room; 10 rooms per experiment. After each room the headset was removed, the participant sat, closed their eyes, gave their rating, then moved to the next room. An eyes-closed rest and a neutral room preceded the trials. |
| D-004 | Self-report: Experiment 1 recorded a single comfort score (kept as its own variable `comfort`, never mapped to valence). Experiment 2 recorded valence and arousal ratings. Experiment 3 recorded a choice (pleasant/unpleasant; calm/excited) plus a 0–1 intensity; the stored value is signed (unpleasant and calm are negative). Experiments 2 and 3 are treated as signed scales in [−1, 1], with an explicit equivalence check before pooling. |
| D-005 | Fusion is kept as the core idea. Both signals are put on comparable scales before fusion; α is reported with a sensitivity analysis; trials without self-report use α = 1 and are flagged. |
| D-006 | Neuro-Score is the closeness of a predicted (valence, arousal) point to a target point defined per space type. Experiments 1 and 2 rooms have no space type and use the general "calm and positive" target. Target coordinates are proposed in Phase 3 and signed off by the owner. |
| D-007 | Results are reported openly as a pilot study, whatever they are. If no model beats the baseline, the website says so plainly and the simulator shows uncertainty rather than confident predictions. |
| D-008 | Participants are identified only by subject ID (e.g. `Subj_A`). Consent covers public release of recordings and demographics. No names appear anywhere: code, data, images, renders, PDFs, website. |
| D-009 | Frontend: React + Vite + TypeScript, desktop-first but responsive. System Architecture page is dropped. All other page content is kept, regrouped as in section 9. Model Training becomes a read-only Model Report. |
| D-010 | Audience: researchers. The landing page explains the whole project scientifically: question, experiments, protocol, methods, analysis, findings, limitations. |
| D-011 | Hosting: free tiers (Vercel for the site, Render for the API), optional custom domain. |
| D-012 | PyTorch is removed. With ~160 trials, neural networks are not justified; scikit-learn and statsmodels cover all modelling. |
| D-013 | Licences: MIT for code, CC BY 4.0 for data, renders and documentation (owner had no preference; this is the common research default). |
| D-014 | Work happens on branch `rebuild/v1`; legacy `main` is tagged `v0.2.0-legacy` and left untouched. |

---

## 3. Files the owner must provide

The agent has the code, the metadata CSVs, the raw recordings and the thesis PDFs. It does not have the items below. Without them, the affected parts are either blocked or must use a documented fallback.

| # | What | Where to put it | Needed by | If missing |
|---|---|---|---|---|
| F-1 | Room renders, one or more images per room, any common format, at the highest resolution available | `data/renders/raw/` | Phase 8 | Rooms page and simulator show generated 3D massing only |
| F-2 | A mapping file `data/renders/renders.csv` with columns `room_id, file, view_label` (e.g. `Rm_021, rm021_a.png, entrance view`) | `data/renders/` | Phase 8 | Agent cannot pair images with rooms |
| F-3 | Eyes-closed rest and neutral-room recordings, if they were recorded as separate files. Check your Chords export folders. Include how they are named and which trial they precede | `data/raw/baseline/experiment_0X/` | Phase 2 | Per-subject normalisation uses each person's own trial distribution (documented fallback, weaker) |
| F-4 | The Chords/NPG Lite settings used (screenshot of the app or the sampling-rate setting), and the firmware/app version if known | `docs/protocol/hardware.md` | Phase 1 | Rate is inferred from data and marked "inferred" |
| F-5 | Exact wording of the questions and instructions given to participants in each experiment, and the scale used for Experiment 1's comfort score | `docs/protocol/questionnaires.md` | Phases 3, 8 | Methods text uses the thesis PDF wording, marked for verification |
| F-6 | VR setup: headset model, software used to present rooms (Unity, Unreal, Enscape, etc.), how long each room was shown, whether room order was randomised per participant | `docs/protocol/vr_setup.md` | Phases 3, 8 | Order effects cannot be analysed; methods text incomplete |
| F-7 | How spatial and lighting values were obtained: which software computed daylight factor, illuminance and CCT (e.g. Ladybug, ClimateStudio, DIALux), and under what sky/time conditions | `docs/protocol/spatial_measurement.md` | Phase 8 | Methods page states values were computed in simulation without detail |
| F-8 | Ethics/consent statement wording, and the institution (IAAC) and advisors as they should be credited | `docs/protocol/ethics_and_credits.md` | Phase 8 | Website omits the ethics section |
| F-9 | Custom domain name, if any, and access to its DNS settings | tell the agent at Phase 9 | Phase 9 | Site lives on the default Vercel URL |

A short template for each `docs/protocol/*.md` file is created in Phase 0 so you only have to fill in blanks.

Two data inconsistencies were found during review and must be explained by the owner in Phase 1 (the agent will produce the exact rows):

- Experiment 3's spatial sheet lists 24 rooms, but you ran 10 rooms per experiment and only 30 unique rooms appear across all trials.
- Experiment 3's biometric sheet lists 64 trials, but only 60 survived the merge. Which rows are retakes, pilots or errors?

---

## 4. Target repository layout

```
Predictive-Atmospheres_Mark-3/   (branch rebuild/v1)
├── AGENTS.md                 agent rules (Codex reads this)
├── CLAUDE.md                 one line: "Follow AGENTS.md" (Claude Code reads this)
├── DECISIONS.md              numbered, append-only decisions (D-001 …)
├── CHANGELOG.md              Keep a Changelog format, one entry per merged phase
├── README.md                 truthful overview, quick start, links to docs
├── CITATION.cff              how to cite the project
├── LICENSE                   MIT (code)
├── LICENSE-DATA              CC BY 4.0 (data, renders, docs)
├── Makefile                  the only entry points: make setup / data / pipeline / test / site / all
├── backend/
│   ├── pyproject.toml        managed by uv, Python 3.11 pinned
│   ├── uv.lock
│   ├── src/pa/
│   │   ├── config.py         paths and settings only; science constants live in decisions.yaml
│   │   ├── decisions.yaml    machine-readable copy of locked numeric decisions (fs, bands, α, targets)
│   │   ├── io/               loading metadata and raw recordings, schema validation (pandera)
│   │   ├── signals/          EEG and ECG cleaning, artifact rejection, features, QC
│   │   ├── affect/           self-report harmonisation, objective mapping, fusion, perception gap
│   │   ├── scoring/          the single Neuro-Score implementation
│   │   ├── features/         spatial schema (pydantic) and the single build_features()
│   │   ├── modeling/         baselines, models, grouped CV, mixed effects, uncertainty, model card
│   │   ├── optimize/         constrained room search
│   │   ├── results/          exporters that write JSON consumed by the website
│   │   ├── api/              FastAPI app (v1 routes)
│   │   └── cli.py            `pa` command (typer): audit, signals, targets, dataset, train, export, serve
│   └── tests/                unit, synthetic-signal, parity, contract and API tests
├── frontend/
│   ├── package.json          pnpm, Node 22 LTS pinned in .nvmrc
│   ├── src/
│   │   ├── api/              generated OpenAPI types + typed client
│   │   ├── content/          MDX chapters for the landing page and methods text
│   │   ├── design/           tokens.css, typography, figure primitives
│   │   ├── figures/          circumplex, signal traces, room charts, model report charts
│   │   ├── pages/            the seven pages (section 9)
│   │   └── lib/              results loader, number formatting, Stat component
│   ├── public/rooms/         optimised render images (generated, not hand-edited)
│   └── tests/                vitest unit tests, playwright e2e + accessibility + screenshots
├── data/
│   ├── metadata/             small CSVs (kept in git)
│   ├── raw/                  recordings (NOT in git going forward; fetched or placed locally)
│   ├── renders/              raw renders + renders.csv (raw images not in git; optimised copies are)
│   ├── processed/            generated; never committed except tiny fixtures
│   └── MANIFEST.sha256       checksums of every raw file, committed
├── artifacts/                generated model, metrics, results JSON (committed only at release tags)
├── docs/
│   ├── methods.md            full scientific methods (source for the website)
│   ├── data_card.md          what the data is, how collected, caveats
│   ├── model_card.md         generated in Phase 5
│   ├── protocol/             owner-provided protocol notes (F-4 … F-8)
│   ├── reports/              phase-0.md … phase-9.md, data_audit.md, signal_qc.md
│   ├── history/              legacy audits and notes moved out of the root
│   └── thesis/               thesis PDFs (Git LFS)
└── .github/workflows/        ci.yml (lint, types, tests, OpenAPI drift, site build), deploy notes
```

Removed on the branch (history keeps them): `frontend_streamlit_archive/`, the Streamlit `frontend/`, duplicated `frontend/preprocessing.py` and `frontend/config.py`, `predictive_atmospheres.egg-info/`, `pytest.log`, `test_output.txt`, `data/processed/*.cache`, `cached_data.pt`, `.agents/`, `fab/`, `.envrc`, `website publishing.md`, `Dockerfile` (Streamlit), the root `api.py`, `run_pipeline.py`, `requirements.txt`. The two audit documents move to `docs/history/`.

---

## 5. Agent rules (contents for `AGENTS.md`)

Copy this section into `AGENTS.md` in Phase 0. `CLAUDE.md` contains only: `Follow every rule in AGENTS.md.`

```markdown
# Rules for coding agents working on Predictive Atmospheres

## Scope
- Work only on the phase named in the prompt. Touch only the files that phase lists.
- Read EXECUTION_PLAN.md (your phase card), DECISIONS.md and the previous phase report before writing code.
- Do not start the next phase.

## Science is locked
- Never change DECISIONS.md or backend/src/pa/decisions.yaml. If a decision looks wrong,
  stop and write the concern under "Questions for the owner" in your phase report.
- Never hard-code a scientific constant (sampling rate, band edges, alpha, targets, thresholds)
  in code. Read it from decisions.yaml.
- Never replace a failed computation with a default value. Mark the trial as excluded,
  record the reason, and continue.

## Tests are the contract
- Never delete, skip, xfail or loosen a test to make it pass. If a test is wrong,
  explain why in the phase report and ask.
- Every new function that computes a number used in results gets a test.
- Run the phase's acceptance commands and paste their real output into the phase report.

## Honesty
- Never invent data, citations, participant details or results.
- Every number shown on the website must come from a generated results file, never typed by hand.
- If something cannot be done, say so in the report. Do not fake it with mocks outside tests.

## Privacy
- Participants are referred to only by subject ID. Never write a name anywhere.

## Records
- Use Conventional Commits (feat:, fix:, refactor:, docs:, test:, chore:).
- Write docs/reports/phase-<n>.md using the template in docs/reports/TEMPLATE.md.
- Add an "Unreleased" entry to CHANGELOG.md describing user-visible changes.

## Environment
- Backend: `cd backend && uv sync && uv run pytest`. Frontend: `cd frontend && pnpm install && pnpm test`.
- Use `make` targets where they exist. Do not install global packages.
```

---

## 6. Record keeping and documentation system

The owner asked for every change to be properly recorded and the repository to explain itself. Four mechanisms do this, each with one job.

### 6.1 `DECISIONS.md` — why things are the way they are

Append-only, numbered entries. Each entry has: ID, date, decision, reason, evidence (link to a report or figure), and "supersedes" if it replaces an earlier one. Every scientific choice in the code points back to a decision ID in a comment, for example `# D-001: sampling rate`.

### 6.2 `CHANGELOG.md` — what changed

[Keep a Changelog](https://keepachangelog.com) format with semantic versions. Each merged phase adds entries under Added / Changed / Removed / Fixed. The rebuild is released as `v1.0.0` at the end of Phase 9.

### 6.3 Phase reports — what was done and proven

`docs/reports/phase-<n>.md`, from this template (created in Phase 0 as `docs/reports/TEMPLATE.md`):

```markdown
# Phase <n> — <name>
Date, agent used, branch, commit range

## Goal (copied from the plan)
## What was done
## Files changed
## Acceptance checks (command → pasted output → PASS/FAIL)
## Numbers that changed (before → after, with explanation)
## Decisions needed / questions for the owner
## Known limitations carried forward
## Reviewer verdict (filled by the review session)
```

### 6.4 Review prompt (for the separate reviewer session)

```
You are reviewing Phase <n> of the Predictive Atmospheres rebuild. Do not edit any files.
Read EXECUTION_PLAN.md (Phase <n> card and section 5), DECISIONS.md, and docs/reports/phase-<n>.md.
Then:
1. Re-run every acceptance command yourself and compare with the report.
2. Check the diff (git diff rebuild/v1...HEAD) for: hard-coded constants, silenced or weakened tests,
   default values substituted for failures, invented content, names of participants, scope creep.
3. Check that every new numeric function has a test and every scientific choice cites a decision ID.
Write your findings as a list of BLOCKING and NON-BLOCKING issues, then a verdict: APPROVE or CHANGES REQUIRED.
Append it to the "Reviewer verdict" section of the phase report.
```

### 6.5 Docs that feed the website

`docs/methods.md`, `docs/data_card.md` and `docs/model_card.md` are the written source of truth. The website's long-form text in `frontend/src/content/*.mdx` is adapted from them, and every number in that text is rendered by a `<Stat id="..."/>` component that reads `artifacts/results/stats.json`. If the pipeline changes a number, the website changes with it, and a CI check fails if any `<Stat>` id is missing from the results file.

---

## 7. Dependencies and skills

### 7.1 Backend (Python 3.11, managed by `uv`)

| Package | Purpose |
|---|---|
| numpy, scipy, pandas, pyarrow | numerics, filtering, tables, parquet |
| mne | EEG filtering, notch, band power (Welch/multitaper), epoching |
| neurokit2 | ECG cleaning, R-peak detection, ectopic correction, HRV (RMSSD, HR) |
| scikit-learn | baselines, Ridge, random forest, gradient boosting, grouped CV, permutation importance |
| statsmodels | linear mixed-effects models, confidence intervals |
| mapie | conformal prediction intervals |
| optuna | constrained room search in the optimizer |
| pydantic (v2) | spatial input schema and API validation |
| pandera | schema checks on every table the pipeline produces |
| fastapi, uvicorn | API |
| typer | `pa` command-line interface |
| matplotlib | per-trial QC figures in reports (not used by the website) |
| skops (or joblib) | safe model serialisation |
| pyyaml | reading decisions.yaml |
| Dev: pytest, hypothesis, httpx, ruff, mypy, pre-commit | tests, property-based tests, API tests, lint, types |

Removed: torch, streamlit, plotly (backend), shap, requests.

### 7.2 Frontend (Node 22 LTS, `pnpm`)

| Package | Purpose |
|---|---|
| react, react-dom, typescript, vite | app and build |
| react-router | the seven pages |
| @tanstack/react-query | API calls with loading/error states (simulator only) |
| zod | runtime validation of results JSON |
| openapi-typescript, openapi-fetch | typed API client generated from the backend schema |
| @observablehq/plot, d3-scale, d3-shape | scientific charts with full styling control |
| three, @react-three/fiber, @react-three/drei | 3D room massing in the simulator (loaded only on that page) |
| @mdx-js/rollup, remark-math, rehype-katex, katex | long-form methods text with real equations |
| @fontsource/source-serif-4, @fontsource/public-sans | self-hosted fonts (see section 9.3) |
| CSS Modules + CSS custom properties | styling via design tokens; no CSS framework |
| Dev: vitest, @testing-library/react, playwright, @axe-core/playwright, eslint, prettier | unit, end-to-end, accessibility, screenshots, lint |

Image pipeline: `sharp` (via a small Node script) converts renders to responsive WebP/AVIF in `frontend/public/rooms/`.

### 7.3 Tooling and services

Git with Git LFS (thesis PDFs only), GitHub Actions, Docker (API image only), Render (API, free tier), Vercel (site, free tier), Zenodo (versioned DOI for data and code at release), optional custom domain.

### 7.4 Skills required, and who supplies them

| Skill | Used in | Supplied by |
|---|---|---|
| EEG signal processing (filtering, artifacts at forehead sites, band power, asymmetry) | Phase 2 | Agent, constrained by this plan and synthetic-signal tests |
| ECG and heart-rate variability | Phase 2 | Agent, via NeuroKit2 |
| Statistics for repeated measures (mixed models, grouped cross-validation, permutation tests, conformal intervals) | Phases 3, 5 | Agent, constrained by pre-registered analysis in DECISIONS.md |
| Software engineering (Python packaging, FastAPI, testing, CI) | Phases 0, 4, 6, 7, 9 | Agent |
| Front-end engineering (React, TypeScript, data visualisation, accessibility) | Phase 8 | Agent |
| Visual and information design | Phase 8 | This plan's design system; agent implements; owner approves screenshots |
| Scientific writing | Phases 8, 9 | Agent drafts from docs; owner verifies facts about the protocol |
| Domain knowledge of the experiments | all "stop and ask" points | Owner only |

What the owner needs to do personally: provide the files in section 3, answer "stop and ask" questions, approve the Neuro-Score targets, approve website screenshots, and check that the methods text describes the experiments correctly. Everything else is delegated.

---

## 8. Phases

Each card ends with a prompt to paste into a fresh agent session. Always paste the review prompt (6.4) into a second session afterwards.

### Phase 0 — Branch, cleanup and safety net

**Goal.** A clean, reproducible skeleton on `rebuild/v1` with rules, records and data integrity checks in place, and nothing scientific changed yet.

**Tasks.**
1. Tag `main` as `v0.2.0-legacy`. Create `rebuild/v1`.
2. Create `AGENTS.md` (section 5), `CLAUDE.md`, `DECISIONS.md` (D-001 … D-014 from section 2), `CHANGELOG.md`, `docs/reports/TEMPLATE.md`, and templates for `docs/protocol/hardware.md`, `questionnaires.md`, `vr_setup.md`, `spatial_measurement.md`, `ethics_and_credits.md` with headings and blanks for the owner.
3. Remove or move the files listed at the end of section 4. Move thesis PDFs to `docs/thesis/` under Git LFS.
4. Create `backend/` with `uv init`, Python 3.11 pinned, and move `src/` into `backend/src/pa/` (rename package to `pa`). Keep legacy modules temporarily in `backend/src/pa/legacy/` so nothing is lost; they are deleted in Phase 4 once replaced.
5. Stop tracking `data/raw/` going forward (add to `.gitignore`), write `data/MANIFEST.sha256` for every raw and metadata file, and add `pa verify-data` that checks the manifest.
6. Add `Makefile` targets: `setup`, `verify-data`, `test`, `lint`.
7. Add pre-commit with ruff and basic hygiene hooks. Replace CI with: ruff, mypy (strict on new modules), pytest.
8. Write data integrity tests: every `EEG_Filename` in the biometric sheets exists; every raw file has the columns `Counter, Channel1, Channel2, Channel3`; trial counts per experiment are reported (not asserted to a fixed number yet).

**Acceptance.**
- `make setup && make verify-data && make test && make lint` all pass on a fresh clone with data placed locally.
- `git ls-files | xargs du -ch | tail -1` shows the tracked size, recorded in the report, with no file over 10 MB outside LFS.
- No reference to Streamlit or torch remains outside `pa/legacy/`.

**Stop and ask.** Nothing scientific. Ask only if a file's purpose is unclear before deleting it.

**Prompt to give the agent.**
```
Execute Phase 0 of EXECUTION_PLAN.md exactly. Read sections 2, 4, 5 and 6 first.
Do not change any scientific logic. Write docs/reports/phase-0.md from the template with real command output.
```

---

### Phase 1 — Data audit and sampling-rate verification

**Goal.** A complete, evidence-backed description of the data, and a confirmed sampling rate, before any signal is processed.

**Tasks.**
1. `pa audit` writes `docs/reports/data_audit.md` and `data_audit.json` with:
   - per experiment: rooms, subjects, trials, trials missing files, duplicate (subject, room) pairs;
   - per raw file: sample count, `Counter` wrap count, logged time spent, implied rate = samples / time spent;
   - spectral evidence: for each file, power near 50 Hz and 100 Hz when read at 256 Hz vs 500 Hz (mains is 50 Hz in India; it must land on 50/100 Hz at the correct rate);
   - heart-rate plausibility: median heart rate from a quick NeuroKit2 pass at each candidate rate;
   - signal amplitude ranges per channel (to establish units);
   - the exact rows behind the two inconsistencies in section 3 (Experiment 3: 24 rooms listed vs 10 run; 64 trials vs 60 merged).
2. Produce a one-page summary figure set in `docs/reports/figures/phase-1/`.

**Acceptance.**
- `pa audit` runs end to end; the report states a recommended sampling rate with all three lines of evidence.
- Unit tests for the rate-inference function using synthetic signals sampled at known rates (250, 256, 500, 512 Hz) pass.

**Stop and ask.**
- Owner confirms the sampling rate (with F-4 if available). The confirmed value is written to D-015 and `decisions.yaml` by the owner or at their instruction.
- Owner explains each row flagged by the inconsistency checks: keep, drop, or retake. Recorded as D-016.
- Owner states whether baseline recordings exist (F-3). Recorded as D-017.

**Prompt to give the agent.**
```
Execute Phase 1 of EXECUTION_PLAN.md. Do not process signals beyond what the audit needs.
Do not choose the sampling rate yourself: recommend one with evidence and stop for the owner.
```

---

### Phase 2 — Signal processing rebuild

**Goal.** Valid, quality-controlled physiological features per trial, computed at the confirmed sampling rate, with every exclusion explained.

**Locked method (written to `decisions.yaml` at the start of the phase as D-018; agent implements, does not redesign).**
- Analysis window: from 10 s after room onset to the logged time spent in the room (not a fixed 60 s), to exclude the orienting response.
- EEG (Fp2, Fp1, earlobe reference): band-pass 1–40 Hz (zero-phase FIR via MNE), notch at 50 Hz and 100 Hz.
- Artifact handling at forehead sites (blinks, eye movements, head motion while standing and turning): split into 2 s epochs with 50% overlap; reject epochs whose peak-to-peak amplitude or low-frequency (<3 Hz) power exceeds a robust threshold (median + k × MAD per subject; k in decisions.yaml); reject flat or clipped epochs.
- Trial validity: at least 20 s of clean EEG; otherwise the EEG features are missing and the reason is recorded.
- EEG features from the median Welch spectrum across clean epochs: absolute alpha (8–13 Hz), theta (4–8 Hz), beta (13–30 Hz) per channel; prefrontal alpha asymmetry = ln(alpha Fp2) − ln(alpha Fp1); beta/alpha ratio.
- ECG (wrist, lead I): NeuroKit2 cleaning and R-peak detection with ectopic correction; heart rate and RMSSD. Trial validity: at least 30 accepted beats and at most 10% corrected beats; otherwise HRV features are missing with a reason.
- Baseline normalisation: if baseline recordings exist (D-017), each trial's features are expressed relative to the same participant's baseline (difference for log-power measures, log-ratio for HR and RMSSD). Otherwise each feature is z-scored within participant across their valid trials. The method used is recorded per trial.

**Tasks.**
1. Implement `pa.signals` modules and `pa signals` CLI writing `data/processed/signal_features.parquet`.
2. Write `docs/reports/signal_qc.md`: retained clean seconds per trial, exclusion table with reasons, heart-rate distribution, asymmetry distribution, before/after spectra for a sample of trials.
3. Save one QC figure per trial in `docs/reports/figures/signal_qc/` (raw vs cleaned trace, rejected epochs shaded, spectrum, R-peaks).

**Acceptance.**
- Synthetic tests pass: a signal with known right/left alpha ratio returns the expected asymmetry within 5%; an ECG simulated at a known heart rate (NeuroKit2 `ecg_simulate`) returns it within 2 bpm; injected blink artifacts are rejected; a 50 Hz sine is removed.
- A test fails if the sampling rate appears as a literal anywhere in `pa/signals`.
- At least 95% of included trials have a heart rate between 45 and 120 bpm (any outside are listed and explained).
- No trial has an imputed or default physiological value; excluded values are NaN with a reason code.

**Stop and ask.** Owner reviews `signal_qc.md` and a random sample of 10 QC figures before Phase 3. If more than 25% of trials are excluded, the owner decides whether to relax thresholds (recorded as a new decision with the reason).

**Prompt to give the agent.**
```
Execute Phase 2 of EXECUTION_PLAN.md. Implement the locked method exactly; read all constants from decisions.yaml.
Write the synthetic-signal tests first, then the implementation. Never substitute default values for failed trials.
```

---

### Phase 3 — Affective targets, fusion and Neuro-Score

**Goal.** Harmonised self-reports, objective affect on a comparable scale, a documented fusion, and one Neuro-Score implementation.

**Tasks.**
1. Self-report harmonisation (D-004): Experiments 2 and 3 to signed [−1, 1] valence and arousal; Experiment 1 to `comfort` only. Run an equivalence check between Experiments 2 and 3 (distributions, means, ranges) and report it; pooling is the default unless the owner decides otherwise.
2. Objective affect: objective valence from baseline-normalised prefrontal alpha asymmetry; objective arousal from a pre-specified composite (mean of standardised heart rate, inverted RMSSD and beta/alpha ratio, with weights in decisions.yaml). Map both to [−1, 1] with `tanh(z / c)` where `c` is in decisions.yaml, so they share the self-report scale.
3. Fusion (D-005): `fused = α × objective + (1 − α) × subjective`, α from decisions.yaml (starting value 0.6). Where self-report is missing, α = 1 and `fusion_source = objective_only`. Where objective is missing, the trial is excluded from fused targets (never filled with subjective alone without a flag).
4. Agreement analysis: correlation between objective and subjective with bootstrap confidence intervals, Bland–Altman plots, and per-trial perception gap (Euclidean distance).
5. α sensitivity: recompute every downstream summary for α in {0, 0.25, 0.5, 0.6, 0.75, 1} and store it for the Model Report.
6. Neuro-Score (D-006) in `pa/scoring/neuro_score.py`: `score = 1 − distance(point, target(space_type)) / max_distance`, clipped to [0, 1]. Proposed targets for owner sign-off (valence, arousal):

   | Space type | Proposed target | Reasoning |
   |---|---|---|
   | General (Experiments 1–2, no type) | (0.7, −0.5) | calm and positive, as designed |
   | Bedroom | (0.7, −0.6) | restorative, lowest arousal |
   | Living room | (0.7, −0.3) | relaxed and social |
   | Workplace | (0.6, 0.1) | positive, mildly alert |
   | Classroom | (0.6, 0.2) | positive, attentive |
   | Cafeteria | (0.6, 0.2) | positive, lively |

7. Write `data/processed/trials.parquet` (one row per trial, all targets and flags) validated by a pandera schema.

**Acceptance.**
- Tests: fusion arithmetic, α = 1 fallback flagged, Neuro-Score equals 1 at the target and decreases monotonically with distance (hypothesis property test), no stretch constants anywhere.
- `docs/reports/phase-3.md` includes the agreement statistics and α-sensitivity table.

**Stop and ask.** Owner signs off the Neuro-Score targets (D-019) and confirms pooling of Experiments 2 and 3 (D-020).

**Prompt to give the agent.**
```
Execute Phase 3 of EXECUTION_PLAN.md. Use the proposed Neuro-Score targets only as placeholders marked PROPOSED
until the owner signs off. Do not tune α or targets to improve any metric.
```

---

### Phase 4 — Spatial features and the single feature builder

**Goal.** One validated definition of room inputs, used identically by training, the API and the optimizer.

**Tasks.**
1. `pa/features/schema.py`: a pydantic `RoomInput` with the independent inputs only — length, width, height, number of doors, total door area, number of windows, total window area, daylight factor, illuminance, CCT, walkable floor area, day or night, space type (including `general`). Ranges come from the observed data widened by a documented margin, plus physical checks (walkable area ≤ floor area; door + window area < wall area).
2. `build_features(room) -> DataFrame` computes derived features (length-to-width, floor area, wall area, volume, door-to-wall, window-to-wall, walkable-to-floor) and fixed one-hot columns. Door and window areas are totals, never multiplied by counts. Volume is always derived.
3. Missing data policy: Experiment 1 has no openings or lighting data. These stay missing (never 0) with an indicator `has_lighting_data`; models must handle missing values natively or impute inside the pipeline.
4. Parity tests: derived ratios computed by `build_features` match the ratio columns already in the Experiment 2 and 3 spatial sheets (Door to Wall Ratio %, Window to Wall Ratio %, Walkable ratio %) within tolerance. This confirms the area-total interpretation from the data itself.
5. Delete `pa/legacy/` once nothing imports it.

**Acceptance.** Parity tests pass; a property test confirms that any valid `RoomInput` produces finite features; `pa dataset` writes `data/processed/model_table.parquet` with a schema version.

**Prompt to give the agent.**
```
Execute Phase 4 of EXECUTION_PLAN.md. There must be exactly one function that builds model features.
Write the parity tests against the spreadsheet ratio columns before implementing.
```

---

### Phase 5 — Modelling and honest evaluation

**Goal.** Know, with uncertainty, how much room design explains participants' responses, and ship one reproducible model with a model card.

**Pre-registered analysis (written as D-021 before any model is fitted; do not change after seeing results).**
- Explanatory analysis: linear mixed-effects models for fused valence and fused arousal with a random intercept per participant (and per room where it converges), and a small, pre-chosen set of standardised predictors: ceiling height, floor area, window-to-wall ratio, illuminance, CCT, day or night, space type. Report fixed effects with 95% confidence intervals and the share of variance attributable to participants and rooms.
- Predictive analysis: models = predict-the-mean baseline, Ridge, random forest, histogram gradient boosting. Validation = leave-one-room-out and leave-one-subject-out, with hyperparameters tuned only in an inner loop. Metrics = MAE and R² with bootstrap confidence intervals, plus a permutation test (shuffling targets within participant, 1000 permutations).
- Model selection rule: the simplest model whose leave-one-room-out MAE is within one standard error of the best; it ships only if it beats the baseline with permutation p < 0.05. Otherwise the shipped model is still the selected one, but `model_status = "not_better_than_baseline"` and the website shows this (D-007).
- Uncertainty: conformal prediction intervals (MAPIE) calibrated with grouped splits, reported at 80% coverage, with empirical coverage checked.
- Feature effects: grouped permutation importance and partial dependence for the shipped model.
- Repeat the headline metrics for every α in the Phase 3 sensitivity set.

**Tasks.** Implement `pa train` (deterministic seeds), write `artifacts/model/` containing the fitted pipeline, `feature_schema.json`, `metrics.json`, data hash and git commit, and generate `docs/model_card.md` from the metrics.

**Acceptance.**
- Running `pa train` twice gives identical metrics.
- `metrics.json` contains the baseline comparison, permutation p-values and interval coverage.
- A test confirms no preprocessing is fitted on validation folds (e.g. scaler inside the pipeline, checked by inspecting fold-wise fitted objects).

**Stop and ask.** Owner reads the model card before the website uses any result.

**Prompt to give the agent.**
```
Execute Phase 5 of EXECUTION_PLAN.md. Commit D-021 (the pre-registered analysis) before fitting anything.
Report results as they are; do not add models, features or tuning beyond the plan to improve them.
```

---

### Phase 6 — Optimizer rebuild

**Goal.** Suggest rooms that are physically valid, within the range of rooms actually studied, and honest about uncertainty.

**Tasks.**
1. Search only over independent inputs; the space type is fixed by the user; derived features always come from `build_features`.
2. Keep candidates inside the studied range: per-feature bounds from the data, plus a distance-to-training-data check (Mahalanobis on standardised inputs); candidates beyond the threshold are flagged `extrapolated`.
3. Use Optuna with a fixed seed to maximise Neuro-Score for the chosen space type; return the top 5 distinct candidates with predicted valence, arousal, intervals and Neuro-Score.
4. If `model_status` is not better than baseline, results are still returned but carry that status.

**Acceptance.** Property tests: every candidate passes `RoomInput` validation, has exactly one space type and one of day/night, and has derived features equal to `build_features` output; same seed gives the same candidates.

**Prompt to give the agent.**
```
Execute Phase 6 of EXECUTION_PLAN.md. Never sample derived features or one-hot columns directly.
```

---

### Phase 7 — API and results export

**Goal.** A small, validated, versioned API for the interactive parts, and static results files for everything else.

**Design.** Almost all website content is static research results, so it is exported as JSON at build time and shipped with the site. This keeps the site fast and working even when the free API is asleep. Only prediction and optimisation need the live API.

**Tasks.**
1. `pa export` writes `artifacts/results/`: `stats.json` (every number cited in text), `rooms.json`, `trials.json`, `signals/<trial_id>.json` (downsampled raw and cleaned traces, ≤ 2,000 points per channel, with rejected epochs), `affect.json`, `agreement.json`, `people.json` (by subject ID only), `model_report.json`, `alpha_sensitivity.json`. Each file is validated by a schema and versioned.
2. FastAPI `/v1/health`, `/v1/meta` (versions, model status, data hash), `/v1/predict` (body = `RoomInput`), `/v1/optimize`. Plain `def` handlers for CPU work. Errors return a structured message without stack traces. CORS origins from an environment variable. The app refuses to start if the model artifact is missing or its feature schema does not match `build_features`.
3. Export the OpenAPI schema to `frontend/src/api/openapi.json`; CI fails if it is out of date.
4. Dockerfile for the API on `python:3.11-slim` with `uv`; no torch; image size recorded in the report.

**Acceptance.** API tests with httpx for every route including invalid inputs; a parity test proving `/v1/predict` equals calling the model on `build_features` output; `pa export` output validates against its schemas.

**Prompt to give the agent.**
```
Execute Phase 7 of EXECUTION_PLAN.md. The API must import build_features from pa.features; never re-implement it.
```

---

### Phase 8 — Website redesign

**Goal.** A research website that explains the whole project scientifically, keeps every useful function of the old pages, and has a distinct visual identity drawn from the subject.

Work in this order, with an owner screenshot review after steps 2 and 6:

1. Scaffold `frontend/` (section 7.2), routing for the seven pages (section 9.1), generated API client, results loader with zod schemas, `<Stat>` component, image pipeline for renders (F-1, F-2).
2. Build the design system (section 9.3) as `src/design/tokens.css` and a small set of primitives: page frame, reading column, figure with caption and source note, table, data definition, footnote, equation (KaTeX), state messages. Produce a style sheet page at `/_styleguide` (excluded from navigation).
3. Build the signature circumplex figure (section 9.4) as a reusable component.
4. Write `content/*.mdx` from `docs/methods.md`, `docs/data_card.md` and `docs/model_card.md`; owner verifies protocol facts.
5. Build the pages in section 9.1 order.
6. Polish: responsiveness down to tablet and mobile, keyboard focus, reduced motion, colour contrast, loading/empty/error states, the "model is waking up" state for the free API.

**Acceptance.**
- `pnpm typecheck && pnpm lint && pnpm test && pnpm e2e` pass.
- Playwright + axe: no serious or critical accessibility violations on any page.
- Lighthouse (desktop) performance, accessibility and best practices ≥ 90 on every page.
- A CI check confirms every `<Stat id>` exists in `stats.json` and no digits representing results are hard-coded in MDX (lint rule).
- Screenshots of every page at 1440 px and 390 px committed to `docs/reports/figures/phase-8/` for owner approval.

**Prompt to give the agent.**
```
Execute Phase 8 of EXECUTION_PLAN.md, following section 9 exactly (structure, tokens, signature figure, content rules).
Stop after the design system and style guide page and after the polish step for owner screenshot review.
```

---

### Phase 9 — Documentation, deployment and release

**Tasks.**
1. Rewrite `README.md`: what the project is, the honest headline finding, how to reproduce (`make all`), repository map, links to methods, data card, model card, decisions and the live site.
2. Finalise `docs/methods.md`, `docs/data_card.md`, `CITATION.cff`, `LICENSE`, `LICENSE-DATA`.
3. Deploy the API to Render (Docker, health check `/v1/health`) and the site to Vercel (environment variable for the API URL, custom domain if F-9 provided). Document both in `docs/deployment.md`.
4. CI: lint, types, tests, OpenAPI drift, results-schema validation, site build, e2e on pull requests.
5. Release `v1.0.0`: changelog, git tag, GitHub release, Zenodo archive of code plus data (raw recordings, renders, metadata) with a DOI, added to the README and the website.

**Acceptance.** A fresh clone on a clean Linux machine reproduces the published metrics with `make all` (data fetched from the Zenodo record or placed locally, verified by the manifest); the live site and API pass a smoke test.

---

## 9. Website: information architecture and design system

### 9.1 Pages

The old tabs map onto seven pages. Every function of the old pages is kept (except System Architecture), with corrected data behind it.

| # | Page | Contents | Replaces |
|---|---|---|---|
| 1 | The study (landing) | Title and one-paragraph abstract; the research question; why it matters (indoor time, BIM, WELL); the signature circumplex figure; the three experiments (rooms, participants, trials, what was measured); protocol timeline (rest, VR room, rating); methods in brief with equations (filtering, asymmetry, HRV, fusion, Neuro-Score); headline findings with confidence intervals; limitations; data and code availability with DOI; credits, ethics, how to cite | Landing page |
| 2 | Rooms | Gallery of the 30 rooms with renders; per-room parameters; filter and sort by experiment, space type, lighting; room comparison; correlations between room parameters; day versus night; illuminance and CCT ranges; per-room average response on the circumplex | Spatial Insights, Environmental Impacts |
| 3 | Signals | Choose a trial: raw versus cleaned EEG and ECG traces with rejected epochs shaded; spectra and band powers; asymmetry; heart rate and RMSSD; baseline comparison; dataset-wide quality summary and exclusion table | Human Metrics |
| 4 | Affect | Objective, subjective and fused positions on the circumplex; agreement statistics and Bland–Altman; perception gap by room and person; α sensitivity slider (pre-computed values) | Emotion Landscape, Affective Fusion |
| 5 | People | Per-participant (subject ID) distributions; how much variance comes from people versus rooms; sleep hours, age and gender breakdowns where the data supports them, with sample sizes shown | Demographic Insights |
| 6 | Room simulator | Enter a room (all inputs, with validation messages); 3D massing view; predicted valence and arousal with intervals on the circumplex; Neuro-Score against the space-type target; nearest studied rooms with their renders; "suggest rooms" (optimizer) with extrapolation flags; model status banner when results are not better than baseline | Design Studio |
| 7 | Model report | Pre-registered analysis; mixed-effects estimates with intervals; cross-validated performance against the baseline; permutation test; interval coverage; feature effects; α sensitivity; known limitations; link to the model card | Model Training |

Navigation is a persistent side rail on desktop listing the seven pages in reading order, so the site reads like a paper you can interact with. On small screens it collapses to a top menu.

### 9.2 Content rules

- Plain, precise language for researchers. Sentence case everywhere. Active voice.
- Every figure has a caption stating what is plotted, the n, and the uncertainty shown, plus a source note pointing to the method section.
- Every number comes from `stats.json` via `<Stat>`. Effect sizes always carry intervals.
- Pilot status is stated on the landing page and the model report, never hidden.
- Error and empty states say what happened and what to do (for example, "The prediction service is starting up. This takes about 30 seconds on the free server.").

### 9.3 Design system

**Subject, audience, job.** The subject is how built space and light shape human affect, measured in the body. The audience is researchers. The site's job is to let a reader understand and scrutinise the study, then explore it.

**Concept: light as data.** Colour temperature is one of the study's own measured variables, so the palette is built from illuminant colours. Colour is never decoration: warm and cool hues are reserved for encoding lighting conditions, and the rest of the interface stays neutral so data colour carries meaning.

| Token | Hex | Role |
|---|---|---|
| `--ink` | `#1E2A30` | text and primary lines (blue-graphite, the colour of a drawing pen) |
| `--paper` | `#F7F8F6` | page background, a cool daylight white |
| `--graphite` | `#6A747A` | secondary text, axes, gridlines |
| `--lamp-2700k` | `#E39A4F` | warm illuminant end of the CCT scale |
| `--sky-6500k` | `#6F95C9` | cool illuminant end of the CCT scale |
| `--alert` | `#B04A3C` | validation errors and exclusion markers only |

Continuous CCT is drawn on a perceptually uniform interpolation between `--lamp-2700k` and `--sky-6500k` (OKLCH). Valence and arousal are encoded by position on the circumplex, not colour.

**Type.** Source Serif 4 for long-form text, captions and headings (it has optical sizes and reads well at length; body 19 px, line height 1.55, measure about 68 characters). Public Sans for interface, figure labels and tables, with tabular figures for numbers. No all-caps labels, no monospace labels, no single-word accent colouring in headlines.

**Layout.** Desktop: side rail (navigation) | reading column (text) | figure column, where the active figure stays in view while the related text scrolls past. Left-aligned text throughout. Figures may span both columns when they need width.

```
┌────────┬──────────────────────────┬───────────────────────────┐
│ rail   │ reading column (~68ch)   │ figure column (sticky)    │
│ Study  │ Heading                  │ ┌───────────────────────┐ │
│ Rooms  │ Paragraph … <Stat/> …    │ │  figure                │ │
│ Signals│ Equation (KaTeX)         │ │                        │ │
│ Affect │ Paragraph …              │ └───────────────────────┘ │
│ People │                          │ Caption, n, interval, source│
│ Sim.   │                          │                           │
│ Model  │                          │                           │
└────────┴──────────────────────────┴───────────────────────────┘
```

**Principles.** Spend boldness in one place: the circumplex. Keep everything else quiet and exact, like a well-set paper with architectural drawing restraint: thin ink lines, generous whitespace, figures given room. Borders and rules appear only where they separate information (table headers, figure frames). Radius is small and consistent on controls only.

**Review against generic defaults (done during planning).** The legacy notes specified a near-black background, white text and zero radius; that is a common template look and carries no meaning for this subject, so it was replaced. A cream background with terracotta accent was also avoided for the same reason. The broadsheet-column treatment was rejected in favour of a reading-column-plus-figure layout that suits a methods-heavy scientific text.

### 9.4 Signature figure: the atmosphere circumplex

A square valence–arousal plane with the circumplex emotion reference points labelled lightly. Each trial is a point coloured by its room's CCT. Space-type targets appear as small open markers.

On the landing page it plays the site's single orchestrated motion: points begin at their subjective positions, a faint trace shows their objective positions, and they settle into fused positions, illustrating the fusion idea in one movement. It runs once, can be replayed, and is replaced by the final state when the user prefers reduced motion.

The same component is reused on the Rooms, Affect, People and Simulator pages with different filters and highlighting, so the reader learns one figure and sees the study through it.

Hover or focus on a point shows subject ID, room (with render thumbnail), experiment and values; points are keyboard reachable and have an accessible table alternative.

---

## 10. Risk register

| Risk | Effect | Mitigation |
|---|---|---|
| Sampling rate cannot be confirmed | All physiological features uncertain | Three independent lines of evidence in Phase 1; owner sign-off; rate stored once in decisions.yaml |
| Forehead EEG heavily contaminated by eye and head movement | Many trials excluded | Epoch-level rejection, per-trial QC, owner decides thresholds with evidence; report exclusions openly |
| Baselines not recorded | Weaker normalisation | Documented within-participant fallback (D-017) |
| Small sample (10 people, 30 rooms) | Low statistical power | Pre-registered, few predictors; mixed models; intervals everywhere; pilot framing (D-007) |
| Agent silently changes science or weakens tests | Wrong results look right | Locked decisions, AGENTS.md rules, separate reviewer session, tests that check for literals and leakage |
| Website numbers drift from pipeline | Incorrect claims | `<Stat>` component, stats.json, CI check |
| Free API sleeps | Simulator slow on first use | Static results for all non-interactive pages; clear waking state |
| Raw data too large for git | Slow clones, LFS bandwidth limits | Raw data off git, manifest checksums, Zenodo DOI |
| Names leak in images or PDFs | Privacy breach | Phase 0 and Phase 9 scans of text and image metadata; owner check of renders and thesis pages used on the site |

---

## 11. Definition of done

- `make all` on a clean machine reproduces every published number.
- Every scientific choice is in `DECISIONS.md`, every change in `CHANGELOG.md`, every phase has an approved report.
- The model card states plainly whether room design predicts responses better than chance in this pilot.
- The website explains the full project on its landing page, every number on it comes from the pipeline, and all seven pages pass the accessibility and performance checks.
- Data, renders and code are archived with a DOI and correct licences, with participants identified only by subject ID.
