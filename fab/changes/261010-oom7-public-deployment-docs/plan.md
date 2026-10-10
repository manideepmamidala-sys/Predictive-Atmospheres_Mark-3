# Plan: Public deployment documentation and website access

**Change**: 261010-oom7-public-deployment-docs
**Intake**: `intake.md`

## Requirements

### Documentation: Website access

#### R1: Visitor-first README
README SHALL lead with the live website link and a concise research introduction, offer all eight named page links from intake, and retain reproducibility/evidence references below. It SHALL describe recent atlas, fused Studio, closest-score generation and visible email features while preserving the baseline-only, constant-prediction and target-distance qualifications.

- **GIVEN** a GitHub visitor, **WHEN** reading the README, **THEN** they can open the public site without local installation and understand its experimental use boundary.

#### R2: Current deployment facts and memory
README, affected memory and project context SHALL reflect the verified single Vercel project, public alias, same-origin API, manual deployment and Python 3.11 research versus 3.12 hosting. They SHALL link existing evidence and remove stale pending-review/undeployed claims. Approved specifications, artifacts and dated historical reports SHALL remain unchanged. Indexes SHALL be generated, not manually edited.

- **GIVEN** the completed deployment report, **WHEN** reading current documentation, **THEN** deployed facts and unmeasured runtime properties are distinguished and older hosting configurations are identified as fallback.

#### R3: Repository homepage
The GitHub About homepage SHALL be `https://predictive-atmospheres.vercel.app`; unrelated metadata SHALL remain unchanged. A newly nonempty differing value SHALL be inspected before any overwrite.

- **GIVEN** the empty homepage field, **WHEN** updating website discovery, **THEN** the live URL appears in About with description, topics, visibility and default branch preserved.

#### R4: Focused verification and preservation
Validate local documentation links, the eight public page links, homepage metadata and whitespace. Preserve the three unrelated dirty files captured in `/home/manideep/.cache/oom7-protected.json`. No model/data/application changes, scientific rerun, screenshot regeneration, redeployment or merge SHALL occur in this change. The draft PR SHALL identify inherited deployment commits not yet in main rather than present its complete diff as docs-only.

- **GIVEN** inherited deployment commits and unrelated dirty files, **WHEN** preparing the PR, **THEN** existing files are preserved, the PR scope is explicit and validation targets changed documentation.

## Tasks

### Phase 1: Documentation

- [x] T001 Rewrite README access, route guide, recent features and status using verified evidence. <!-- R1 -->
- [x] T002 Update `docs/memory/operations/reproducibility.md`, `docs/memory/architecture/website.md` and `fab/project/context.md` for current deployment; generate affected indexes. <!-- R2 -->

### Phase 2: Discoverability and verification

- [x] T003 Inspect and update GitHub About homepage only; record before/after metadata. <!-- R3 -->
- [x] T004 Validate changed documentation links, eight public routes, metadata preservation, scoped diff and protected-file hashes; record results in this change's `validation.md`. <!-- R4 -->

## Acceptance

### Functional Completeness

- [ ] A-001 R1: README has prominent live link, eight correct page names/URLs, recent features and visible contact email.
- [ ] A-002 R1: Local reproduction and scientific evidence links remain available, with fused-only baseline/constant/Neuro-Score qualifications.
- [ ] A-003 R2: README, memory and project context consistently describe active hosting, runtime split and measured limits; approved specification is unchanged.
- [ ] A-004 R2: Generated indexes match memory descriptions; dated evidence remains intact.
- [ ] A-005 R3: Homepage is the live origin and unrelated GitHub metadata is unchanged.

### Scenario Coverage

- [ ] A-006 R4: Local references and eight live routes pass targeted checks, with results recorded.
- [ ] A-007 R4: Protected hashes remain unchanged, no new runtime/scientific edits exist relative to inherited HEAD, and PR ancestry is described accurately.

### Code Quality

- [ ] A-008: Plain, readable prose follows existing Markdown and memory conventions.
- [ ] A-009: Existing deployment report is reused rather than unnecessarily duplicated.
- [ ] A-010: Source evidence, derived features and predictions remain distinguishable; no placeholder research claims are introduced.
- [ ] A-011: Documentation changes do not duplicate runtime contracts or add unused utilities/tests.

## Notes

Four tasks select the light lane: apply and hydrate inline, fresh independent review dispatched. Current session model is retained for inline work as required by the light-lane contract; an already-running main session cannot be switched by instructions. Independent review uses the AGENTS.md GPT-6 Astra/xhigh profile.

Starting HEAD is `6c502c87a2bd48b842f3c604f266df20dc3c2556`. PR #5 merged at `71523db3dd04027125a6c077a92fa7353307f537`; the three subsequent deployment commits remain outside main. The new PR targets main and includes those previously reviewed deployment changes plus this documentation update. No automatic merge or publication is part of this run.

## Assumptions

| # | Grade | Decision | Rationale | Scores |
|---|-------|----------|-----------|--------|
| 1 | Certain | Target main and explicitly describe inherited deployment changes in the PR. | Recorded base is main; GitHub confirms PR #5 merged while three deployment commits remain unmerged. | S:95 R:90 A:95 D:95 |
| 2 | Certain | Use link/content/metadata checks without scientific reruns. | Only current documentation and the homepage field are changing. | S:95 R:98 A:98 D:98 |

2 assumptions (2 certain, 0 confident, 0 tentative).
