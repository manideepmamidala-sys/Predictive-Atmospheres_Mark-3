# Predictive Atmospheres — research platform rebuild roadmap

This roadmap implements the [Fab change](fab/changes/261008-ymhz-research-platform-rebuild/plan.md) on branch `261008-ymhz-research-platform-rebuild`. Its plan's requirements and tasks govern execution. The prior manual phase instructions are retained as historical context at [docs/history/EXECUTION_PLAN-legacy.md](docs/history/EXECUTION_PLAN-legacy.md); their locked methodological and release assertions are superseded by the intake and current evidence. The committed legacy snapshot is Git commit `41d6ba507965d5159a679e65962fb3d02963a551`. This is a reference to the original committed tree, distinct from the uncommitted files inventoried in `docs/reports/migration-inventory.json`. No existing tag or branch is moved.

The primary question is how bilateral forehead recordings, wrist ECG, and self-reported ratings describe experience of rendered architectural spaces. Affective fusion is a constructed hypothesis to examine with component disagreement and sensitivity. Predicting responses to room attributes and optimizing toward a user's chosen valence/arousal target are experimental demonstrations. They do not establish a validated emotion detector or a causal effect of geometry or lighting.

## Evidence and decision order

1. Inventory and checksum all original recordings, metadata, room renders, legacy images and thesis documents before moving or removing paths. Keep originals and record identical destinations.
2. Audit file integrity, sampling-rate evidence, counters, actual versus logged duration, chronology, and structural missingness. A count/duration ratio near 500 Hz is evidence for a *candidate* rate, not confirmation of the hardware setting. Counter jumps are acquisition flags, not measured lost packets or timestamps.
3. Write a versioned analysis specification from primary physiological and statistical methods, with declared assumptions, eligibility, uncertainty and failure handling. Have a fresh independent reviewer check the audit and specification before real processing or model comparisons. Record amendments before affected reruns.
4. Process valid recorded samples without padding or invented baselines. Keep failed EEG/ECG measurements missing with reason codes. Maintain objective components, subjective reports and fused coordinates separately. Experiment 1 comfort is its own construct.
5. Validate room inputs and derive features in one backend builder. Train and evaluate only with declared group splits and training-fold preprocessing. Save the complete pipeline and state uncertainty and baseline comparisons honestly. Score candidate rooms against a **user-selected** target.
6. Export versioned research results and expose a small versioned API for live simulation. Build the seven-page research site against generated data, with Light/Dark/System themes and static research access when the API sleeps.
7. Reproduce from original evidence in a clean checkout, test contracts and accessibility, record independent review, hydrate memory and prepare a local deployment/release handoff. The Fab coordinator owns stage transitions and PR activity.

Scientific choices remain revisable through documented decision amendments. An unavailable physiological measure or weak predictive model is reported with its eligibility and evidence; neither is silently replaced with a plausible default.

## Phase milestones

| Phase | Deliverable | Gate to the next phase |
| --- | --- | --- |
| 0 — Preservation and governance | Reconciled instructions, source manifest, verified asset copies, replacement package, exact historical-change cleanup | Recorded legacy commit and worktree inventory; verified source checksums |
| 1 — Acquisition audit | File-level audit, rate scenarios, trial chronology, duration and counter flags | Audit checks and independent audit/specification checkpoint |
| 2 — Signals | Validated EEG/ECG features, validity ledger, representative traces | Synthetic feature recovery and corruption/short-recording tests |
| 3 — Affect and analysis | Original self-report, component/fused cohorts, alpha sensitivity, dependent-sample summaries | Distinct constructs/missingness; qualified statistical claims |
| 4 — Spatial data | Unified input schema, derived features and physical versus studied support | No contradictory or fabricated independent features |
| 5 — Modeling | Room/participant grouped baselines and candidates, complete model artifact | Leakage tests, fold evidence and reload parity or justified unavailable status |
| 6 — Optimizer | Seeded, bounded search toward selected affect target | Valid distinct candidates within supported search or truthful empty result |
| 7 — API and exports | Versioned static results and `/v1` health/meta/predict/optimize contracts | Generated schema/client and API parity/drift checks |
| 8 — Website | The study, Rooms, Signals, Affect, People, Room simulator, Model report | Both themes, mobile/desktop, keyboard and reduced-motion review with screenshots |
| 9 — Reproduction and handoff | Clean-checkout run, reports, documentation, local deployment configuration | Independent review, hydrate and explicit external release prerequisites |

Phase numbers are evidence milestones, not independent manual branches. Some implementation can proceed in parallel once its prerequisites are met; the order and dependencies are in the Fab plan. No phase report claims a command, source or result that was not observed.

## Source provenance and known limitations

The owner reports NPG Lite acquisition through Chords in Barcelona, with Channel1 near right Fp2, Channel2 near left Fp1 and Channel3 wrist ECG across experiments. Exact electrode placement, reference/ground wiring, signal units, sample setting, firmware and app version remain unverified. Participants stood and turned in Meta Quest 3 while viewing non-interactive 360 renders. Recording began on opening eyes in the headset and ended before removal; ratings followed while seated with eyes closed. Exposures varied. No neutral-room or eyes-closed rest baseline recordings were collected. Repeated subject IDs refer to the same people. The owner reports random room order; the randomization mechanism and event timestamps were not retained.

The stored rating CSVs already contain the investigator's signed conversions. Experiment 1's transformed comfort is not valence. Experiments 2 and 3 elicited valence/arousal differently, so equal numeric ranges alone do not establish measurement equivalence. Original forms and conversion sheet are unavailable. The spatial values came from Grasshopper with Ladybug/Honeybee and do not establish calibrated stimulus exposure in the headset. Renders were samples, not matched simulation/extraction conditions. Do not invent sky, date/time or other settings.

The pilot has 160 referenced recordings, 10 subject IDs and 30 rooms. Four fully empty Experiment 3 biometric rows and fourteen fully empty spatial rows do not imply missing trials or extra rooms. Document the actual acquisition discrepancies and missing fields in the audit. All participants remain identified by IDs. No unverified name-to-recording mapping, institutional endorsement, ethics approval, questionnaire results or causal claims are published.

## Release boundary

Local completion includes a working site and API, reproducible results or documented unavailable states, review and deployment-ready configuration. Production deployment, public visibility changes, licensing grants, DOI registration and named-recording publication require separate decisions/evidence. MIT code and CC BY 4.0 data/assets are historical proposals, not current licences. Keep third-party terms intact. Vercel and Render are free-tier candidates whose current limits must be checked when deploying.
