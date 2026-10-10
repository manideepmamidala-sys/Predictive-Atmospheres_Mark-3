# CP-E2 — independent site and accessibility review

**Disposition: APPROVED under delegated AI review.** The corrected static frontend and populated live Studio pass this checkpoint. The reviewer verified all 80 final screenshot hashes and dimensions, inspected the final route and live-state captures, and read all eight actual Lighthouse reports: accessibility is 100 on every route, above the required 95. No unresolved must-fix presentation findings remain. The approved scientific scope remains baseline-only and experimental, as recorded in CP-C; this is not a human inspection or deployment claim.

**Review date:** 2026-10-10 UTC. **Reviewer:** fresh Codex agent `/root/visual_checkpoint_review`. The parent explicitly dispatched `model: gpt-6-astra`, `reasoning_effort: xhigh`, `fork_turns: none`; the tool accepted those arguments. This verifies the recorded dispatch settings. Runtime model introspection is not exposed by the agent-status tool.

**Authorization:** the user's instruction `$fab-ff approve all the future checkpoint automatically and continue the work` delegates this checkpoint to evidence-based agent review. It does not claim that the owner inspected the site, copy, captures or measurements. Scope follows the active [intake](../../../fab/changes/261010-tadj-research-atlas-design-studio/intake.md), [plan](../../../fab/changes/261010-tadj-research-atlas-design-studio/plan.md), approved [CP-E1 copy](CP-E1.md) and the qualified [CP-C baseline-only publication decision](CP-C.md).

## Evidence inspected

The reviewer independently loaded all eight routes using the real staged research exports at **1440 × 900** and **390 × 844**, in **light and dark themes**: 32 route/viewport/theme cases. All 32 viewport images were viewed through contact sheets. Full-page layouts and focused native-size chart crops were also inspected; long-page overview captures were supplemented by chart-level review rather than treated as proof that every small label was readable.

The independent DOM audit found zero page errors, zero document-width overflow, the expected catalogue figure counts in all 32 cases, no broken loaded images, no public PDF/CV/portfolio links, no clipped main-chart text and no unlabelled overflowing chart containers after correction. Intentional table, navigation and dense-chart scrolling is contained within the page. All 68 distinct internal links collected from the default routes addressed the implemented route family; the interaction checks below exercised representative destination and anchor behavior.

| Route | Catalogue figures | Visual scope |
| --- | ---: | --- |
| `/` | 0 | Concept and hypothesis, experiment story, source renders, researcher portrait and authorized contact links |
| `/study` | 4 | Protocol narrative, S1 exposure map, S2 branching eligibility, S3 room profiles and S5 participant characteristics |
| `/rooms` | 10 | Source-room gallery and selected detail; S4 and R1–R9, including affect densities and observed function ratings |
| `/body` | 8 | Physiology-led component explanation, signed affect plane, B1–B8, spectra, cardiac values and component/fusion densities |
| `/prediction` | 5 | Baseline-only status, P1–P5, separate null controls, fused learning curve and explicit unavailable importance |
| `/studio` | 0 | Fused-only input/target/actions, unavailable-service state and distinct requested numerical score |
| `/explore` | 0 | URL filters, trial/room/person views, contained data tables and related-analysis return link |
| `/methods` | 1 | Source/current-method distinction, historical implemented prototypes, glossary and versioned method table |

The review inspected question, takeaway, axis descriptions and units, legend, contributing trial/person/room counts, method, caveat and accessible table treatment. The 28-product catalogue contains 27 available products and the explicit P4 unavailable result for the constant fitted model. Table-only rows remain available without being added to incompatible plotted scales. This checkpoint checks presentation against the approved scientific decision; it does not reproduce every statistical estimate.

## Findings and corrections

| Finding from actual render | Corrected behavior and verification |
| --- | --- |
| Mobile S1, S3, S4, R2 and related categorical plots had overlapping or clipped ticks; long axis titles were cut off. | Dense charts retain readable category spacing inside labelled keyboard-scrollable regions. Complete axis descriptions and units wrap outside the SVG. Corrected light/dark mobile and desktop crops were inspected; the 32-case main-chart text-bounds audit passed. |
| P5 long stage names were unreadable as categorical bar ticks, including after the first margin fix. | An ordered five-stage count/unit flow preserves all exported stages and the source table, explicitly distinguishing trial and room counts. Its mobile layout and both themes were inspected. |
| S3's ten-room legend overflowed even where the three-attribute plot fitted; S4's negative legend endpoint was clipped. | Legend-only overflow now has the same labelled keyboard-scroll region and visible hint. Continuous ramps have enough left space for their endpoint ticks. Focused crops were re-inspected. |
| P3's legend included comparator/fold rows that were not plotted training-size curves, implying a shared error scale. | The graph now shows only its two actual fused-coordinate learning-curve series and labels constructed fused-coordinate MAE. Self-report comparators retain their separate units in the complete table and explanatory note. |
| B5's takeaway described the narrower correlation cohort as though it were the complete plotted paired cohort. | The final staged product explicitly reports E3's 33 plotted raw-HR pairs from five people versus 31 calibrated-HR correlation pairs from four people. The method and caveat explain calibrated, sufficiently variable within-person correlation eligibility; usable raw-HR pairs remain visible. The reviewer checked the staged product and rendered text. |
| Live generation exposed dimensions and scores but omitted the complete generated parameter sets and candidate fused coordinates required by the intake. | Every candidate has an accessible disclosure containing all 13 canonical inputs with units and both fused coordinates. All 65 displayed input values across five candidates were independently matched to the real API response; all ten coordinate fields were present. All four viewport/theme detail views were inspected. |
| Successful generation expanded `.studio-output` to 438 pixels in a 390-pixel viewport, although empty and forward-result states fitted. | Corrected table/grid containment keeps the populated page at 390 pixels, with a 358-pixel output column and an internal table scroller. Both themes at both required viewports passed independent width and expanded-detail checks. |
| Initial Lighthouse measurements flagged prohibited ARIA attributes emitted inside Observable Plot SVG groups. | Generated SVGs are decorative while the question, method, caption and complete data table remain accessible. The independent reviewer verified that P3's complete 24-row table opens after the change. All eight final Lighthouse reports score 100 for accessibility with zero failed weighted audits. |

## Independent interaction checks

Nine checks passed against real static exports in a 390 × 844 Chromium viewport with reduced motion enabled:

1. API-offline readiness is visible before submission and disables both model actions.
2. The emotional target supports arrow keys, Shift fine steps and Home reset, updating the numeric coordinates.
3. Wheel scrolling leaves the focused room dimension unchanged.
4. Experiment filtering and room selection display and focus the selected `Rm_025` detail.
5. Its Explorer link preserves the room filter and displays the six associated source trials.
6. Returning from Explorer to the lazy-loaded S3 chart focuses it below the sticky header.
7. A dense chart region can be focused and scrolled using the keyboard.
8. An unknown route displays the dedicated 404 page.
9. The legacy signals route preserves experiment and signal-view intent.

The landing remains a concept-led explanation without results cards or a findings plot. Its portrait/research statement and email, LinkedIn and IAAC links match the authorized scope. Body-derived, reported and fused positions are differentiated; E1 comfort remains separate. The Methods page identifies Grasshopper and AI rendering as historical implemented proofs of concept. The Prediction page and unavailable P4 importance preserve the CP-C finding that the selected fitted model is constant. None of this presentation establishes learned spatial predictive utility or individual emotion accuracy.

A real API run using E3 preset `Rm_025`, target `(0, 0)` and requested score `65` returned fused valence `0.1993364768`, arousal `−0.0741607067` and normalized proximity `0.9248045535`, displayed as `92.5 / 100`. Five candidates all achieved `92.48045535`, each `27.48045535` from the request, and preserved locked dimensions `7.33 × 3.99 × 2.59 m`. The baseline-only notice, schematic/source-render distinction and absence of a promised exact match were visible. The corrected candidate disclosures and populated mobile layout were subsequently verified against real API values, not fixtures.

## Final measurements and capture identity

The final [screenshot manifest](../../screenshots/manifest.json) contains **80 PNGs / 41,470,419 image bytes**: 32 viewport captures and 32 full-page captures covering all eight routes in both required sizes and themes, plus eight viewport and eight full-page captures of populated live Studio prediction and generation. The reviewer independently checked every image's SHA-256, byte count and PNG dimensions, with no mismatches, missing combinations or unlisted PNGs. All final route viewport captures, all 32 route full-page captures and all 16 live Studio captures were visually inspected through contact-sheet overviews. Final mobile candidate output also received native-size crop inspection in both themes. The detailed earlier browser, chart and interaction checks supplement these overviews.

The frozen manifest SHA-256 is `0869190c50e3efdd013e8c617edc46f49899ed36187a618f8c79d126f421ccff`. Its canonical analysis-index, B5 and model-metadata hashes were independently matched to the named files. The separately recorded staged index has different serialized whitespace but identical parsed JSON; its recorded hash also matches. The corrected B5 product is identical in the canonical and staged locations. The release live captures use an E3 preset and unrestricted generated dimensions; they supplement the reviewer's separate locked-dimension API scenario documented above.

The [Lighthouse score summary](lighthouse/scores.json), SHA-256 `f60c1df299ef9c6245b11be71e3e1c6597c2551564c3365587f7365f082569d8`, matches the eight underlying reports. These are actual Lighthouse **13.5.0** measurements on the built preview at `http://127.0.0.1:4175/`, fetched between **13:14:34 and 13:16:16 UTC on 2026-10-10**. Lighthouse used its mobile form factor with **412 × 823** emulation and device scale factor **1.75**; these settings are distinct from the two visual-review viewports. All reports have zero failed weighted accessibility audits and no runtime error. Five reports carry a CPU-speed warning relevant to performance scoring; this checkpoint makes no performance-score claim.

| Route | Accessibility | Actual report |
| --- | ---: | --- |
| `/` | 100 | [Landing](lighthouse/landing.json) |
| `/study` | 100 | [Study](lighthouse/study.json) |
| `/rooms` | 100 | [Rooms](lighthouse/rooms.json) |
| `/body` | 100 | [Body](lighthouse/body.json) |
| `/prediction` | 100 | [Prediction](lighthouse/prediction.json) |
| `/studio` | 100 | [Studio](lighthouse/studio.json) |
| `/explore` | 100 | [Explorer](lighthouse/explore.json) |
| `/methods` | 100 | [Methods](lighthouse/methods.json) |

The built-preview Studio audit covers its unavailable-API state because that server has no API proxy. Successful real prediction and generation are covered separately by the proxied live captures and independent API/browser checks above. Accessibility scores do not replace those live-state checks or imply exhaustive assistive-technology coverage.

## Review boundary

This is an independent AI review of the local Chromium rendering, responsive behavior, content boundaries and recorded accessibility evidence. It is not a human inspection claim, an exhaustive assistive-technology evaluation, a cross-browser certification, a clean scientific reproduction or an external deployment authorization. Full-page captures of long tables and charts were reviewed as layout overviews with focused inspection of the relevant charts and interactions; the report does not claim pixel-by-pixel inspection of every data-table row.
