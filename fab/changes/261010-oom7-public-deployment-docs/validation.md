# Documentation validation — 2026-10-10

- 43 local Markdown references across README, project context, affected memory and the regenerated operations index resolve. Bundle-relative memory links resolve under docs/memory.
- Eight public route URLs returned HTTP 200 without redirects: /, /study, /rooms, /body, /prediction, /studio, /explore, /methods.
- GitHub About homepage changed from empty to https://predictive-atmospheres.vercel.app. Description, topics, visibility and default branch match the before snapshot.
- All three unrelated dirty-file SHA-256 values match the pre-change snapshot.
- `git diff --check` passes. The new edits affect documentation and current change artifacts only; source/models/specification/deployment config are unchanged relative to starting HEAD 6c502c87a2bd48b842f3c604f266df20dc3c2556.
- Generated operations index refreshed with `fab docs-index docs/memory`; no generated rows were hand-edited.
- Existing deployment verification remains dated evidence in docs/reports/revision-2026-10/deployment.md; no scientific reruns, screenshot replacements or redeployment were performed.

## PR ancestry

PR #5 is merged into main. Three deployment follow-up commits remain outside main and are inherited by this branch: da0f785, 69e223f, 6c502c8. The draft PR must describe both those already-published deployment changes and the new documentation updates. Repository homepage metadata is already live; branch documentation reaches the default-branch README only after merge.
