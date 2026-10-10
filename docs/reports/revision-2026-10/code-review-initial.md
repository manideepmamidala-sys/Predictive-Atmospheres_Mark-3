# Independent review — tadj

Reviewed 2026-10-10 in full mode: plan conformance and holistic diff, including the enabled parsimony pass. **Verdict: FAIL — four must-fix findings.** All 54 implementation tasks are complete; **54/57 acceptance items are met, three are unmet, none are N/A**. Passing execution checks do not cover the public evidence gaps below.

The fresh native Codex reviewer used **gpt-6-astra / xhigh**; `fab agent review -o yaml` confirmed the configured provider/model/effort, with no alias or dispatch override. No nested review agent was used. Reviewed HEAD: `63a325d7f0446ccfbfeaee2516e94568a3f23772`; recorded base: `main`; merge-base with `origin/main`: `8a9c4df630c34388d8c6ff4f2ee57950443d62ec`. The 805-path diff contains extensive generated JSON and binary assets; review policy excludes line-by-line generated/binary review. Canonical code, changed tests/docs, product contracts and cited artifact provenance were inspected. The unrelated earlier change history and untracked project-review PDF were excluded.

## Must-fix findings

### M1 — Preserve reviewed reasons and independent cardiac eligibility through the Explorer

**References:** `backend/src/pa/results/build.py:101–123`, `frontend/src/lib/research.ts:10`, `frontend/src/pages/Explore.tsx:37`. **Acceptance:** A-050, with R7/R14 interface implications.

The exporter applies reviewed eligibility to measurements but builds `reasons`, `eeg_reasons` and `ecg_reasons` solely from automated signal reasons. The public result therefore cannot explain measurements withheld by delegated review. The frontend schema also drops exported `ecg_hr_valid`, `ecg_rmssd_valid` and `reviewed_eligibility`; its single “ECG eligible” column renders the conjunction of HR and RMSSD validity.

Real-data reproduction in the browser:

- `E2:Subj_E:Rm_018` shows both modalities ineligible and reports only `insufficient_contiguous_coverage_for_rmssd`. Its actual reviewed timebase decision is **uncertain**: 26,000 samples imply 52 seconds at the conditional 500 Hz, versus 58 logged seconds, a 10.34% mismatch without acquisition timestamp/event evidence. That decision withholds all physiology; neither the exported EEG reasons nor the table explains it.
- `E1:Subj_B:Rm_010` shows **ECG eligible: No** beside **HR: 81.08 bpm** and unavailable RMSSD. HR is independently eligible; RMSSD is not. There are **49** HR-valid/RMSSD-invalid trials represented by this misleading combined status.
- **33** trials lose an automated-eligible EEG or HR modality after review without carrying the corresponding reviewed reason in the public trial reasons.

Carry component-specific automated and reviewed status/reason provenance from the approved ledger through exports, validation and the Explorer. Show HR and RMSSD eligibility separately and explain timebase/review withholding. Preserve the existing numerical decisions. Add regressions using the two actual examples above; verify the resulting table at mobile width.

### M2 — Remove the unused integrated-review report writer

**Reference:** `backend/src/pa/results/disposition.py:152–200`. **Parsimony category:** `zero-call-sites` → must-fix under `_review/SKILL.md`.

New `write_integrated_review()` has no tracked caller, CLI entry point or documented invocation. Its `_report()` helper exists only for this unused path. The active reconstruction script calls `integrate_decisions()` directly. Remove the unused writer, exclusive report helper and resulting unused imports/constants, or establish a genuinely required supported entry point. Do not introduce a dummy caller merely to satisfy review. Preserve the active integration/reconstruction behavior and verify provenance after changing source bytes.

### M3 — Complete the accepted Methods evidence contract

**References:** `frontend/src/pages/Methods.tsx:15–20`, `backend/src/pa/results/build.py:298–323`. **Acceptance:** A-014. **Requirement sources:** intake §6 and `docs/research/analysis-catalogue.md:34`.

The accepted Methods route includes timebase, QC thresholds, CP-B decisions, sensitivity analyses, specification/decisions and data/model-card context. The page currently supplies broad prose, a glossary, historical prototypes and an experiment-count table. Its Methods product has three experiment rows, not the promised numerical settings, decision evidence or sensitivities. There are no useful specification/decision/card references. Existing computed sensitivity data remain in the research bundle, while the former `Sensitivity` component is no longer mounted.

Expose the approved numerical method/timebase/QC/mapping settings, reviewed decision provenance, existing computed sensitivity evidence and canonical versioned spec/data/model-card references. Keep the account concise and readable. This requires presentation/export wiring of approved evidence, not new scientific choices or browser-side research calculations. Add meaningful assertions for the promised content and verify both themes/viewports.

### M4 — Format complex page components to meet the explicit readability acceptance

**References:** `frontend/src/pages/Studio.tsx:170–178`, `frontend/src/pages/Explore.tsx:32–40`. **Acceptance:** A-045.

Complex forms, controls, conditional output and trial tables occupy individual multi-kilobyte JSX lines. For example, Studio's entire candidate/prediction output is on line 176 and the Explorer's three table variants share line 37. This makes branch nesting, accessibility attributes and eligibility presentation unnecessarily difficult to inspect or maintain. It does not meet the plan's explicit “formatted components over clever compression” criterion.

Apply ordinary multiline JSX formatting to the changed page components, keeping related branches/controls legible. Extract meaningful sections only where that improves clarity; do not add an abstraction framework or redesign behavior. Existing type and focused browser checks should remain green.

## Should-fix findings

- **S1 — Label stale implementation snapshots as historical.** `docs/research/thesis-source-context.md:19–29` calls pre-v1.2 physiology mapping, the 0.4304/0.4099 model comparison and highest-score/no-lock optimization the current implementation. Preserve the thesis citations and historical comparisons, but date/label those implementation snapshots and link the approved v1.2 method, current baseline-only card and closest-score contract.
- **S2 — Correct the specification index's checkpoint status.** `docs/specs/index.md:8` says CP-B human QC decisions remain pending. The actual checkpoint is delegated and approved with exclusions. Update the index to reference that disposition without claiming owner personal inspection or editing the byte-frozen approved specification.

No additional nice-to-have findings or applicable inline review suppressions were identified.

## Verification and scientific assessment

Independently executed during review:

| Check | Result |
| --- | --- |
| `cd backend && uv run --frozen pytest -q` | **122 passed**, 42.08 s; one upstream Starlette/httpx deprecation warning. |
| Focused Playwright: `site`, `simulator`, `real-exports`, `chart-encoding`, `theme`, one worker with the documented native-library path | **20 passed**, 1.2 min; all eight routes, both viewports/themes, offline states, score/locks/ranges, keyboard/wheel behavior and real catalogue/chart contracts. |
| `python3 scripts/build_source_manifest.py --check` | **313 retained originals verified**. |
| `python3 scripts/compare_reproduction.py /tmp/pa-final-repro-run-1y3bl3n6/reproduction/clean-clone .` | **53 JSON products**, nested catalogue, model metadata and model bytes matched at the documented `1e-8` tolerance and narrowly declared normalizations. |
| Stored final visual evidence | **80 PNG hashes/dimensions verified**; eight underlying Lighthouse reports and score summary agree on **100 accessibility** for every route. |
| Real-data Explorer inspection | Reproduced M1's timebase-withheld and HR-only cases in a 390×844 browser. |

The final [validation record](validation.md), actual isolated logs and exit code were inspected rather than repeating the hours-long pipeline. The clean source-only snapshot `a4f4850f77e6f6d5eb3d1d0634e0a602f89650f9` retained the 150-input digest `936cd86add14e0406dc563d97a5d536a41b5d33b036b5008f3bb4b245d2dcc93`, reconstructed CP-B byte-for-byte, created the matching null guard before draw zero, completed **1,000 fresh full-refit draws** and **455 unique learning subsets**, and passed `make all` in 7,672 seconds. That evidence includes lint/type checks, 122 backend tests, 29 browser tests with two expected live-disabled skips, and strict site build. The separate final live-API run passed both enabled tests. These are local results; hosted CI completion and deployment are not claimed.

Inspection supports the current scientific limits: the fitted `dummy_mean` is **baseline-only**, with constant fused point `[0.19933647676353913, -0.07416070665631107]` on 23 E3 trials, four people and ten rooms. It demonstrates no learned spatial gain. Evaluation uses grouped, fold-contained transformations; the null refits the full pipeline. The 28 catalogue products include 27 available results and honest unavailable P4. Target coordinates and requested numeric Neuro-Score are separate; scoring is clipped target proximity, and generation ranks absolute requested-score difference while preserving constraints. No replacement science is requested by this review.

## Acceptance disposition

The plan checkboxes are the individual disposition record. All items below were assessed, not inferred solely from completed task checkboxes.

| Items | Result and evidence |
| --- | --- |
| A-001–A-004 | Met: retained source context, cleanup hash/original evidence, CP-A owner choice, canonical manifest and compatibility/drift checks. S1 identifies stale snapshot wording, not missing source traceability. |
| A-005–A-008 | Met: approved specification hash/gates, explicit timebase uncertainty, approved component eligibility and independent contiguous cardiac processing, all-source accounting and separate affect components. M1 concerns downstream public reason/status presentation. |
| A-009–A-013 | Met: prespecified validity products/unavailable cases, honest grouped comparisons and baseline model card, CP-C and shared inference contract, exact score semantics and constraint-respecting nearest-score search. |
| **A-014** | **Unmet: M3.** The presence of a schema-valid Methods ID does not fulfill its promised content. |
| A-015–A-020 | Met: eight routes/redirects/offline behavior, authorized concept-led landing, accessible chart contracts, complete Studio actions, delegated checkpoint/visual evidence and honest release-readiness/hydrate handoff. |
| A-021–A-026 | Met: approval gates, E1 separation, held-out isolation, nearest-score example, locked inputs and independent S2 denominators. |
| A-027–A-029 | Met: verified removals/protected originals, no personal-document downloads/invented biography, old routes deliberately redirected. |
| A-030–A-035 | Met: synthetic signal edge cases, review gates/contiguous cardiac tests, held-out mutation tests, direct/CLI/API/search parity, scoring boundaries and search constraints/ties/fixed seeds. |
| A-036–A-037 | Met: full recorded browser matrix, fresh focused coverage, eight actual Lighthouse measurements and delegated CP-E2 evidence. |
| A-038–A-042 | Met: safe cleanup exclusions, unavailable/partial components, tiny/undefined analysis handling, API readiness failures and malformed/stale export rejection. |
| A-043–A-044 | Met: package/schema/error conventions and existing shared utilities; M2 is unused new code rather than duplicate implementations. |
| **A-045** | **Unmet: M4.** Complex page JSX remains compressed. |
| A-046–A-049 | Met: approved pattern changes, component composition, source/constructed/predicted distinctions and serialized fold-contained transforms. |
| **A-050** | **Unmet: M1.** Reviewed unavailability reasons do not survive the complete public boundary. |
| A-051–A-055 | Met: longer scientific orchestration functions follow explicit pipeline steps; feature/scoring/manifest utilities are shared; settings have decision provenance; no nominal replacement physiology or fabricated model confidence. Long JSX readability is separately blocked under A-045. |
| A-056–A-057 | Met: authorized public scope/display codes, validated constraints and trusted artifact readiness boundary; no request-time training. |

Existing architecture/research/operations memory still describes the earlier implementation. This is a **warning and the declared post-review hydrate handoff**, not a new blocker or a claim that hydrate is complete. The two discovered existing-code deletion candidates are recorded immediately after Notes in the plan. No code, scientific source, generated evidence, stage transitions, commits or deployment were changed by the review.
