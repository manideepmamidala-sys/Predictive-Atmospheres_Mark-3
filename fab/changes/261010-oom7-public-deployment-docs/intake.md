# Intake: Public deployment documentation and website access

**Change**: 261010-oom7-public-deployment-docs
**Created**: 2026-10-10

## Origin

> "$fab-discuss lets do the small updates about the recent deployments and changes, like updating the readme etc to access the webpage, any questions?"

The user then invoked `$fab-new` after discussion recommended a prominent live-site link, an eight-page guide, recent feature summaries, current deployment information, synchronized project memory and a GitHub About website link. This intake carries that already-discussed scope; there are no new product or scientific decisions to resolve.

The prior atlas change `261010-tadj-research-atlas-design-studio` has completed all Fab stages. Its deployment follow-up published both the frontend and FastAPI Studio API at https://predictive-atmospheres.vercel.app. The dated evidence is `docs/reports/revision-2026-10/deployment.md`; operations and release-readiness documents already reflect publication. This change closes the remaining README and memory gaps rather than repeating deployment preparation.

## Why

The README has no prominent live website link, still says independent whole-change review is pending, and incorrectly describes hosting as undeployed Vercel/Render candidates. Operations memory similarly says no production deployment exists. A visitor to GitHub therefore cannot easily find the public research atlas and receives outdated status information.

Update the entry-point documentation and affected memory around the verified deployment. Keep the README useful to thesis jury members and academic researchers first, with reproducibility instructions and evidence accessible below. Link to the existing detailed deployment report instead of copying its full operational history. This is a multi-file documentation correction with memory impact, not a single-spot micro edit.

## What Changes

### README access and orientation

Put a descriptive, prominent link near the top of `README.md`:

`[Open the live website](https://predictive-atmospheres.vercel.app)`

Lead with a short explanation of the architectural research and linked human/spatial metrics. Separate visiting the hosted site from running the research locally: visitors need no account or local installation. Include a compact page guide using these exact existing routes and names:

| Route | Name | Purpose |
|---|---|---|
| `/` | Predictive Atmospheres | Concept, research question, hypothesis and researcher context |
| `/study` | The Study | Study structure and experiments |
| `/rooms` | Rooms & Experience | Spatial attributes, experiences and comparisons |
| `/body` | Body & Experience | Physiology and self-report evidence |
| `/prediction` | Prediction & Findings | Evaluation and model limitations |
| `/studio` | Design Studio | Fused prediction, Neuro-Score and closest-score room generation |
| `/explore` | Data Explorer | Research records, filters and QC evidence |
| `/methods` | Methods & Research Context | Methods, interpretation and research context |

Link each page to the public production origin. Preserve useful local setup, data/model cards, approved scientific specification and reproduction links. Remove stale claims that review remains pending or no deployment exists, without implying a PR was merged or every possible operational measure was benchmarked.

### Recent changes and accurate use boundary

Briefly summarize the eight-route research atlas, component comparisons on research pages, fused-only Design Studio prediction, a separate requested numerical Neuro-Score for closest-score generation, and visible contact email `manideepmamidala2@gmail.com`. Generation seeks a close requested score; it is not a minimum-score solver or a guaranteed optimum. Retain schematic-room/reference-image distinctions where relevant.

Keep an explicit, concise experimental baseline-only qualification: the selected fitted model predicts a constant fused valence/arousal position and has no demonstrated spatial predictive gain. Neuro-Score measures distance to a visitor-selected emotional target, not a probability of well-being. Do not imply separate physiology/self-report Studio predictors, calibrated individual predictions or validated design advice. Keep detailed evidence below the introduction, linked to existing cards and reports.

### Deployment documentation and memory consistency

Use the existing dated deployment report as evidence. It records production source `69e223fa0f42457c51cec0a6cad8e89c8f9d1d53`, deployed through manual CLI prebuilt upload to project `predictive-atmospheres` under `manideep-personal`, on Hobby. The public alias needs no Vercel login; protected unique/preview addresses are not the reader-facing link. The project has no GitHub automatic deployment connection. The later documentation commit `6c502c87a2bd48b842f3c604f266df20dc3c2556` records verification and is not itself the deployed application revision.

Describe the active root `vercel.json` services configuration: Vite static research pages and same-origin `/v1/*` FastAPI, with direct-page SPA routing. Distinguish canonical Python 3.11 research reproduction from isolated Python 3.12 Vercel deployment. Larger-function support is enabled using `VERCEL_SUPPORT_LARGE_FUNCTIONS=1`; do not promise unlimited free usage. Keep the older `render.yaml` and `frontend/vercel.json` configurations identified as fallback/history where they are mentioned, not the current active split.

The report documents all eight direct routes, mobile width checks, email visibility, prediction/generation and 20 independent unauthenticated HTTP checks with scoped API parity. Do not inflate this into deployed memory, sustained latency, quota or exhaustive performance verification. Keep private PDFs/CV/booklet/portfolio files, credentials and local environments excluded; do not add personal download links. Existing public contact/project details are already authorized.

Update affected memory to current behavior and its rationale, preserving historical research evidence and source provenance. Refresh `fab/project/context.md` only as needed to state current hosting and point to the approved v1.2 specification instead of the superseded general v1 pointer. Regenerate affected documentation indexes through `fab docs-index`; do not manually edit generated index rows. Avoid editing the approved specification, model, source data or scientific code.

### GitHub website discoverability

The repository `manideepmamidala-sys/Predictive-Atmospheres_Mark-3` currently has an empty About homepage field. During implementation, set that website field to `https://predictive-atmospheres.vercel.app`, as a reversible discoverability update consistent with the discussion. Preserve the repository description, topics, visibility and default branch. Verify the resulting field. If it has changed since intake, inspect it before overwriting a different nonempty value. Do not post messages, merge a PR, purchase a domain or redeploy the application for this documentation task.

## Affected Memory

- `operations/reproducibility`: (modify) Replace candidate-only hosting statements with verified single-project deployment, runtime profiles, manual publication, provenance and measured/unmeasured checks.
- `architecture/website`: (modify) Record the public origin, same-origin service routing, direct-page access and visible authorized email links while retaining the existing static/live and experimental-model contracts.

## Impact

Expected edits are `README.md`, the two affected memory files, their generated indexes and a small `fab/project/context.md` correction if warranted. Existing `docs/operations.md`, `docs/release-readiness.md` and the deployment report are primary references; amend them only if a concrete inconsistency is found. The GitHub About homepage is the only intended external setting change. No application behavior, schema, dependencies, data, model, API or deployment configuration changes are needed.

Validate Markdown/internal links, route names, referenced files and public website links, check the GitHub homepage value, search scoped current-state documentation for stale hosting/review claims and run `git diff --check`. Documentation changes do not justify rerunning the hours-long scientific pipeline, regenerating artifacts or overwriting approved screenshots. Preserve historical reports as dated evidence rather than rewriting all old candidate references.

The new branch inherits the current deployed-feature branch HEAD; it does not merge that branch into main. Follow Fab's default-base recording procedure and account for this ancestry when later preparing a PR, avoiding a misleading docs-only claim for an inherited full-feature diff. Existing dirty files must remain untouched and unstaged: `fab/changes/261008-ymhz-research-platform-rebuild/.history.jsonl`, `fab/changes/261010-tadj-research-atlas-design-studio/.history.jsonl` (discussion telemetry), and untracked `docs/reports/project-review-2026-10.pdf`. Do not stash or delete them.

## Open Questions

None required. The immediate prior discussion supplies the scope and the verified deployment report supplies the concrete facts. GitHub homepage discoverability is a recorded, reversible assumption; it does not authorize unrelated account or repository changes.

## Assumptions

| # | Grade | Decision | Rationale | Scores |
|---|-------|----------|-----------|--------|
| 1 | Certain | Use the preceding discussion as the description; lead README with the public URL and eight-page guide. | The user invoked fab-new immediately after discussing exactly these updates. | S:98 R:98 A:95 D:98 |
| 2 | Certain | Correct deployment/runtime memory while retaining experimental baseline-only claims and dated evidence. | Verified deployment report and existing scientific contract determine the facts. | S:95 R:95 A:98 D:98 |
| 3 | Certain | Keep implementation to documentation and discoverability; use targeted link/content checks. | User requested small updates; no runtime or scientific behavior change is needed. | S:95 R:98 A:95 D:95 |
| 4 | Confident | Set the empty GitHub About website field to the live production URL during implementation. | Recommended in discussion and directly serves webpage access; user advanced the proposed scope, but did not separately name the setting. | S:65 R:90 A:80 D:75 |

4 assumptions (3 certain, 1 confident, 0 tentative, 0 unresolved).
