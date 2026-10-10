# CP-E2 — independent site and accessibility review

**Original disposition: APPROVED under delegated AI review.** The corrected static frontend and populated live Studio pass this checkpoint. The reviewer verified all 80 final screenshot hashes and dimensions, inspected the final route and live-state captures, and read all eight actual Lighthouse reports: accessibility is 100 on every route, above the required 95. No unresolved must-fix presentation findings remain. The approved scientific scope remains baseline-only and experimental, as recorded in CP-C; this is not a human inspection or deployment claim.

**Original review date:** 2026-10-10 UTC. **Reviewer:** fresh Codex agent `/root/visual_checkpoint_review`. The parent explicitly dispatched `model: gpt-6-astra`, `reasoning_effort: xhigh`, `fork_turns: none`; the tool accepted those arguments. This verifies the recorded dispatch settings. Runtime model introspection is not exposed by the agent-status tool.

**Current rework disposition: APPROVED under delegated AI review**, recorded 2026-10-10T16:17:06Z by fresh Codex reviewer `/root/checkpoint_refresh`, native `gpt-6-astra`/`xhigh`. The [dated rework receipt](#rework-receipt--2026-10-10t161706z) verifies the corrected Explorer/Methods presentation, current capture identity and all eight new accessibility measurements. Earlier measurements below remain historical.

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

## Original final measurements and capture identity

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

## Rework receipt — 2026-10-10T16:17:06Z

**Disposition: APPROVED under the user's existing automatic-checkpoint delegation.** Fresh independent AI reviewer `/root/checkpoint_refresh` used native Codex `gpt-6-astra` with `xhigh` reasoning. Parent dispatch specified that route, and this reviewer independently resolved `fab agent review -o yaml` to provider `codex`, model `gpt-6-astra`, effort `xhigh`, with an empty model alias and no dispatch override. Agent-status tools do not expose runtime model introspection. This checkpoint concerns the first formal-review rework's public presentation and evidence; it is neither the forthcoming fresh formal whole-change review nor personal owner inspection.

### Corrected presentation and independent checks

The reviewer loaded all eight current routes from the real staged exports in Chromium at 1440 × 900 and 390 × 844, in light and dark themes with reduced motion: **32 route cases passed**. The expected catalogue counts remained 0/4/10/8/5/0/0/1 in route order; no browser page error, document-width overflow or broken loaded image was observed. Methods displayed all 22 approved settings and ten existing experiment/weight sensitivity rows. The numerical evidence and scientific limits remain those of the scoped [CP-C rework receipt](CP-C.md#rework-receipt--2026-10-10t160842z).

Both actual Explorer review examples were exercised in both themes and viewports, for **eight focused cases**. `E2:Subj_E:Rm_018` visibly carries the uncertain timebase reason and withholds the affected physiology. `E1:Subj_B:Rm_010` shows **HR eligible: Yes**, **RMSSD eligible: No**, and **81.08 bpm**. Each disclosure opens and closes with keyboard Space and exposes all six component groups with automated and reviewed status/reasons. At mobile width, expanded detail text occupies 288 pixels inside the 358-pixel table scroller while document width remains 390 pixels. The retained reasons explain the difference between conditional ECG acceptance and timebase withholding without changing eligibility decisions. Focused native-size mobile crops in both themes were visually inspected; long source reasons wrap within the disclosure.

Methods renders the conditional sampling assumption, numerical QC/mapping/model settings, actual delegated reviewer identities/counts, existing sensitivity values and canonical references. The eight source links are pinned to commit `63a325d7f0446ccfbfeaee2516e94568a3f23772`. Independent HTTP retrieval of each corresponding raw repository source returned 200: settings, ledger, approved spec, decisions, CP-B and both cards matched local bytes at the 16:17:06Z disposition. The CP-C link intentionally resolves to that named historical snapshot and therefore predates this receipt; it supplies the governing baseline-only review, not a claim to contain later receipt hashes. No missing source link or invented owner review was found.

A separate check against the **built preview at `http://127.0.0.1:4176/`** confirmed all 22 settings, ten sensitivity rows, the Methods-to-Explorer link, 160 trial records and the uncertain timebase example. The built Studio could reach the ready baseline-only API during this check. A controlled network-abort scenario then displayed offline/unavailable readiness and disabled both actions. The accessibility run covers the unsubmitted Studio route; populated prediction/generation remain covered separately by the fresh real-API capture set. The original receipt's unavailable-preview description is historical and is not asserted as the current preview's state.

### Refreshed capture identity

The current [screenshot manifest](../../screenshots/manifest.json), captured at **2026-10-10T16:10:41.222959+00:00**, contains **80 PNGs / 46,891,133 image bytes**: 64 route images and 16 populated live Studio images. Every PNG's SHA-256, byte count and dimensions were independently checked, along with exact route/theme/viewport/state coverage and absence of unlisted PNGs. The manifest SHA-256 is **`95083d450de1ea2a3645922984ed5faca68d6147e0089eed38076b12b3e39a7b`**.

All 32 current route viewport captures and the eight populated Studio full-page captures were visually inspected through overview sheets, supplemented by focused Methods/QC screenshots and native mobile crops. Overview inspection is not pixel-by-pixel validation of every long table or expanded source-reason row. The independent DOM checks above cover the full route matrix, while the earlier detailed interaction review remains dated evidence for unchanged behavior.

Manifest source identities independently match their files:

| Evidence | SHA-256 |
| --- | --- |
| Canonical analysis index | `b98514efe855d7d1fb914bb1c59bf1e7efa28dbeb267164d9194cddfce1d1911` |
| Current B5 product | `741781eecc2dbd2c4fa047a853e3b1b39dfdf538f191028ab2293397ee95a459` |
| Model metadata | `7320414317c7799f3f382e5a1e88e77ffa9a28d5047b7297be8cac482dd95331` |
| Staged analysis index | `560af2e73f0bd4db731ed63ae8bcfbd3e2d9763b68d614bc9779370623060ffd` |

The staged index is parsed-equal to the canonical index despite serialized whitespace differences; current B5 is byte-identical in canonical and staged locations. Its new byte hash reflects generation-time provenance, while its scientific content is unchanged under the CP-C digest rule.

### Current measured accessibility

The [score summary](lighthouse/scores.json) SHA-256 is **`49eedacb301fd66eb53e69952e3321968fd0e8cdf9bd00e0869439c3d163c878`**. All eight underlying **Lighthouse 13.5.0** reports were independently read and matched to the summary, requested built-preview URLs and fetch times. Every route scored **100**, above the required **95**, with zero failed weighted accessibility audits and no runtime error. The reports used mobile emulation **412 × 823**, scale factor **1.75**. Explorer alone has a CPU-speed warning relevant to performance; no performance claim is made.

| Route | Accessibility | Fetch time (UTC, 2026-10-10) | Actual report SHA-256 |
| --- | ---: | --- | --- |
| `/` | 100 | 16:12:24.924Z | `3230093dc4904889a2bcc741349c2a77bdc524903f670416aa0fd1bab3f16b0d` |
| `/study` | 100 | 16:12:39.742Z | `589d3a4dee4b2f1298c859d7103fcaddac070480083d4c97082faaf40d115f98` |
| `/rooms` | 100 | 16:12:54.093Z | `42cc1b4f57f897a1348c79c147673397e9eb75ba5175af855584e22fb55c4cc4` |
| `/body` | 100 | 16:13:09.052Z | `292bef12409d8be642769590808759789dab99c39940f8d9b2cfe2a1b042a7e9` |
| `/prediction` | 100 | 16:13:25.076Z | `c038b36ed19a5be8d690f1559b2781dec1c41bdd5c86cf2439a42745505a3ff0` |
| `/studio` | 100 | 16:13:39.318Z | `090c4c7a8af504d6e5a715ed59128e9bf2bf0631ac63f8d42e7b24909b26dcae` |
| `/explore` | 100 | 16:13:53.110Z | `abbd8e7c5c3e59363429bf56d68eee3baa8786c723b7211f7676346861859e6f` |
| `/methods` | 100 | 16:14:10.977Z | `5d4b43a58c30008fd255050cb76615a2cd74672272647848958eb0b030d37edb` |

The frontend worker's actual capture command passed both tests, including populated real-API Studio states; the pinned Lighthouse command completed with exit 0 on port 4176. Independent reviewer scratch evidence is `/tmp/tadj-cpe2-dom-check.mjs`, `/tmp/tadj-cpe2-built-check.mjs`, `/tmp/tadj-cpe2-images.py` and `/tmp/tadj-cpe2-rework-review/`; these are temporary review aids, not maintained application entry points.

**Boundary:** no unresolved must-fix finding remains in this refreshed visual checkpoint. Baseline-only/experimental interpretation is retained. This is local Chromium evidence, not exhaustive assistive-technology or cross-browser certification, deployment authorization, a new scientific rerun or formal whole-change approval. The reviewer edits checkpoint receipts and, under the parent's explicit follow-up authorization, marks only T052 complete; final-source validation and the different fresh formal reviewer remain separate.

**Subsequent documentation-only identity note — 2026-10-10T16:17:53Z:** the model/data cards gained the explanatory paragraphs independently verified in [CP-C's card supplement](CP-C.md#card-only-supplement--2026-10-10t161753z). The website continues to link the explicit historical snapshot, which retains the same governing methods/results/limitations. No frontend source, rendered export, capture or Lighthouse report changed; the visual disposition and its recorded hashes remain valid.
