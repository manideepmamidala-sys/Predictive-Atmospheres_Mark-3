# Independent review — tadj, iteration 2

Reviewed 2026-10-10 in **full mode**, including plan conformance, holistic diff and the enabled parsimony pass. **Verdict: PASS.** All **54/54 tasks** are complete and **57/57 acceptance items** are met; none are unmet or N/A. There are **zero must-fix, zero should-fix and zero nice-to-have findings** remaining. The initial failed review is preserved in [code-review-initial.md](code-review-initial.md).

## Reviewer and scope

This is a fresh independent reviewer, not the implementation author or initial reviewer. Native Codex dispatch was explicitly **gpt-6-astra / xhigh**; `fab agent review -o yaml` confirmed that provider/model/effort configuration, with no alias or dispatch override. No nested review was dispatched.

Recorded base: `main`; independently resolved merge-base with `origin/main`: `8a9c4df630c34388d8c6ff4f2ee57950443d62ec`. Published HEAD remains `63a325d7f0446ccfbfeaee2516e94568a3f23772`. The review covers both the committed base-to-HEAD change and **base-to-current-working-tree**, including uncommitted corrections and task-related untracked reports. Reviewing only published HEAD would assess the superseded implementation. The unrelated earlier change's `.history.jsonl` and `docs/reports/project-review-2026-10.pdf` were excluded.

The review read the intake, plan, project review/quality policy, constitution/context, affected memory, approved method and checkpoint evidence, canonical scientific/model/export/API source, frontend routes/contracts, changed tests, reproducibility scripts and documentation. Generated JSON and binary assets were assessed through contracts, selected content, hashes and reproduction evidence rather than line-by-line review, as project policy requires.

## Previous findings closed

- **M1 — Reviewed QC and separate cardiac eligibility:** Exports preserve six component records with automated and reviewed statuses, exact decision reasons and review provenance. Backend and frontend validation enforce the eligibility contract. Explorer presents HR and RMSSD separately and exposes component reasons. Actual `E2:Subj_E:Rm_018` retains the uncertain timebase reason and resulting withholding; actual `E1:Subj_B:Rm_010` retains eligible HR (81.08108108108108 bpm) alongside unavailable RMSSD. The 49 HR-valid/RMSSD-invalid trials and 33 review downgrades are accounted for. Regression tests and refreshed mobile evidence cover these cases.
- **M2 — Unused writer:** The unused `write_integrated_review` and its exclusive report helper are removed. The active `integrate_decisions` reconstruction path remains tested. The retained `REPORT` constant has a real reconstruction-script caller. The parsimony pass found no remaining newly introduced zero-call implementation or duplicate canonical calculation requiring correction.
- **M3 — Methods contract:** The validated Methods product and page expose 22 approved numerical settings, 10 existing fusion-weight sensitivity summaries, CP-B decision counts/reviewer provenance and eight canonical pinned references. They report existing approved computations rather than introducing new science or browser-side statistics. The historical CP-C snapshot and pinned reference scope are explained in the receipt.
- **M4 — Readability:** Studio and Explorer use ordinary multiline JSX with inspectable controls, branches, tables and accessibility attributes. Methods is likewise readable; no unnecessary abstraction framework was added.
- **S1/S2 — Documentation:** Thesis-context implementation snapshots are explicitly historical and link current v1.2 behavior. The specification index reports delegated CP-B approval with exclusions, without claiming personal owner inspection or editing the approved specification.

## Independently executed checks

| Check | Result |
| --- | --- |
| `cd backend && uv run --frozen pytest -q` | **123 passed**, 56.40 s; one upstream Starlette/httpx deprecation warning. |
| Focused Playwright: `site`, `simulator`, `real-exports`, `chart-encoding`, `theme`, one worker with the documented native-library path | **23 tests passed**; final Playwright run record is `passed` with no failed tests. Covers route/offline behavior, real exports and QC/Methods contracts, score/locks/ranges, chart encoding and themes. Capture-writing suites were excluded from this independent run. |
| `python3 scripts/build_source_manifest.py --check` | **313 retained originals verified**: 160 recordings, seven metadata files, 30 renders and 116 legacy assets. |
| `python3 scripts/compare_reproduction.py /home/manideep/.cache/pa-rework-delta-8go52o66/final-source-clone .` | **53 JSON products**, model metadata and model bytes match at `1e-8`, using the documented narrowly scoped normalizations. |
| Current visual manifest | **80/80 PNGs** match recorded SHA-256, byte size and dimensions; filename coverage is exact. |
| Stored Lighthouse evidence | All **eight underlying Lighthouse 13.5.0 reports** have no runtime error and **100 accessibility**; score-summary hash verified. |

The visual check initially found one overwritten capture: the later main `make lint test site` run included the capture-writing suite and rewrote `explore-light-mobile.png` after the approved manifest was frozen. The exact approved copy was found in the final-source clone and restored by the coordinator after verifying its source hash. This reviewer then rechecked all 80 images successfully. The restored image is `0d15ffde04b20a21b9df520d3b483029315fca2ba7670a640e976a9a0cef42ec`; the unchanged manifest is `95083d450de1ea2a3645922984ed5faca68d6147e0089eed38076b12b3e39a7b`. No source or numerical artifact changed in that restoration. This is resolved evidence drift, not an outstanding finding.

The current Lighthouse summary is `49eedacb301fd66eb53e69952e3321968fd0e8cdf9bd00e0869439c3d163c878`. Selected actual Methods and QC mobile images were inspected. The independent refreshed [CP-E2 receipt](CP-E2.md) additionally records 32 DOM cases with no overflow/errors, eight real-QC mobile checks and eight Methods references returning HTTP 200. Those broader checks and checkpoint dispositions are delegated agent evidence, not a claim of owner personal inspection.

## Reproduction and scientific assessment

The [validation record](validation.md), actual logs, terminal exit codes and refreshed [CP-C review](science-checkpoint-c-review.md) distinguish two runs correctly:

1. **Original fresh source-only reproduction:** `/tmp/pa-final-repro-run-1y3bl3n6`, source snapshot `a4f4850f77e6f6d5eb3d1d0634e0a602f89650f9`, 150-input digest `936cd86add14e0406dc563d97a5d536a41b5d33b036b5008f3bb4b245d2dcc93`. It reconstructed the approved review ledger byte-for-byte, passed the matching dependency guard before draw zero, ran **1,000 fresh full-refit null draws** and **455 unique learning subsets**, and completed `make all` in 7,672 seconds with exit code zero and reproduction parity. This is the original source snapshot, not the post-rework snapshot.
2. **Final-source targeted replay:** `/home/manideep/.cache/pa-rework-delta-8go52o66/final-source-clone`, source snapshot `e9381e0326ebce2a97c7f67561a4cb3c7882b3fd`, 150-input digest `f6a5420fe9f5dad42684d3dcdd82100359ce6a919a7d5d47089e03ad4a0c4ed5`. This reused artifacts from the original clean run, refreshed model provenance/POC/export, passed lint/site and 123 backend tests, and finished in 194.9 seconds with exit code zero and 53-product/model parity. **It is not another fresh null run.** Inspection of the corrections supports reuse because the approved numerical method, scientific inputs and numerical results are unchanged.

The approved specification remains byte-frozen at `51c01ef6ccdf2f4318ac786d1bb39afeb1aa2bcf3bc93039479a4ed2454603ac`. Fitted model bytes remain `17bfa472c30a9bb24034dd3800c85cd1fa9db36fec8c4a6cba2b8070b6b3544d`. Its honest disposition is **baseline-only**: `dummy_mean`, 23 E3 trials, four people, ten rooms, constant fused point `[0.19933647676353913, -0.07416070665631107]`. No learned spatial improvement is established or claimed. Grouped inner/outer evaluation keeps preprocessing and target calibration within training folds; the recorded spatial null refits the full procedure. E1 comfort remains separate from valence, and complete/partial component denominators are explicit.

The catalogue exposes all 28 products, including 27 available products and honest unavailable P4. One validated fitted-artifact contract serves direct, CLI, API and search inference. Neuro-Score uses the approved clipped target-distance formula with explicit 0–1 API versus 0–100 display conversion. Generation minimizes absolute requested-score error while respecting locks/ranges; it does not reinterpret the requested score as a maximization objective. Direct/CLI/API/search parity and failure paths are tested.

Main post-rework validation additionally records 123 backend tests, 32 browser tests with two expected live-disabled skips, lint and site build; both separately enabled live tests passed. Hosted CI passed for the earlier published HEAD only. CI for a future corrected push and deployment are not claimed by this review.

## Acceptance disposition

Every acceptance item was reassessed against implementation and evidence, rather than inferred from checked task boxes. The plan retains all 57 checked items.

| Items | Disposition and basis |
| --- | --- |
| A-001–A-004 | Met: traceable thesis/prototype context, verified cleanup/original preservation, CP-A owner choice, canonical manifest and artifact compatibility/drift checks. |
| A-005–A-008 | Met: approved specification/gates, explicit uncertain timebases, approved component eligibility, independent contiguous cardiac processing and all-source affect accounting. |
| A-009–A-014 | Met: declared available/unavailable analyses, honest grouped/model comparisons, shared inference/score/constraint contracts and complete Methods evidence. |
| A-015–A-020 | Met: eight routes/redirects, static/offline reading, approved concept-led landing, chart/accessibility contracts, both Studio actions, delegated visual checkpoints and accurate release/hydrate handoff. |
| A-021–A-026 | Met: scientific approval boundaries, E1 separation, held-out isolation, closest-score behavior, preserved locks and independent S2 denominators. |
| A-027–A-029 | Met: verified obsolete-copy removal, protected originals, no retired personal-document downloads/invented biography and useful legacy redirects. |
| A-030–A-035 | Met: meaningful signal/review edge cases, grouped isolation/mutation checks, inference parity/readiness, score boundary and constrained-search tests. |
| A-036–A-037 | Met: recorded complete browser matrix, fresh focused regression coverage, exact current visual manifest and eight measured accessibility scores. |
| A-038–A-042 | Met: safe cleanup exclusions, explicit partial/unavailable components, tiny/undefined analysis handling, API readiness and malformed/stale export rejection. |
| A-043–A-047 | Met: package/schema/error conventions, utility reuse, normally formatted complex pages, approved pattern changes and focused component composition. |
| A-048–A-050 | Met: source/constructed/predicted distinctions, serialized fold-contained transformations and exact unavailability/review reasons surviving the public boundary. |
| A-051–A-055 | Met: explicit orchestration steps, shared canonical features/scoring/manifest utilities, setting provenance and no invented replacement physiology or confidence. |
| A-056–A-057 | Met: authorized public/display scope, validated constraints and trusted artifact readiness without request-time training. |

Affected architecture/research/operations memory still describes the prior v1.1/seven-route implementation. This remains a **warning and the declared post-review hydrate handoff**, not a blocker or a claim that hydrate is complete. Existing-code deletion opportunities were reassessed and recorded in the plan's single Deletion Candidates section; this review does not remove them.

Review mutations are limited to this report, the plan's acceptance/deletion-candidate record and the required terminal `fab status refresh tadj`. The initial report is preserved at SHA-256 `ddf0151d97453677750bad87893159090ebb18faf672c931d8cb995008c8c02d`. No implementation correction, stage transition, commit, push, PR mutation or deployment was performed by this reviewer.
