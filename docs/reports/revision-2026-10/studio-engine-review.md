# Studio engine interim independent review

Date: 2026-10-10. Reviewer: fresh Codex worker, explicitly dispatched as `gpt-6-astra` with `xhigh` reasoning. Scope: T027–T030 and their shared inference/artifact boundaries. This is an interim implementation-slice review, not whole-change acceptance or a Fab review-stage transition. No implementation, acceptance checkbox, or workflow state was changed.

**Verdict: rework required before T030 completion.** Two must-fix findings and two should-fix findings follow. The score formula, distinct emotional/numeric targets, closest-score objective, lock preservation, physical rejection, seeded search, and constant-model behavior are otherwise sound in the checks performed.

## Must-fix

### E-01 — Restore the approved support-distance definition

Location: `backend/src/pa/features/support.py:51–56`; calibration at `:42–44`. Requirement: R11/R13, retained `docs/specs/analysis-v1.md:55`, and approved PD-007.

The implementation restricts nearest-neighbor distance to rooms sharing both categories, but calibrates its threshold using numeric nearest neighbors across all complete rooms. The retained specification instead defines the nearest numeric complete-room distance and checks observed categorical combinations separately. PD-007 does not replace that definition. The change alters both support labels and search admissibility without an approved metric change.

Reproduction using real E3 metadata: take the numeric inputs of `Rm_023` and the observed `Day`/`Classroom` category combination. Its approved numeric-nearest distance is zero. The new implementation reports `sparse`, nearest room `Rm_028`, distance `1.4377285667037265`, threshold `1.4062989577434732`. In a probe crossing each of the ten room input rows with each of the ten observed category rows, 26 of 100 combinations changed from the retained metric's supported result.

Restore the nearest numeric room for the distance calculation, keep the categorical-combination check separate, and preserve deterministic room-ID ties and explicit numeric-only provenance for unseen categories. Add a regression where the nearest numeric room and the category-sharing room differ. The coordinator agreed with restoration during this review; no scientific amendment is needed.

### E-02 — Complete real fitted-artifact parity without assuming the previous model outcome

Location: `backend/tests/test_real_parity.py:55`, with generation assertions at `:44–48`.

The real-artifact test hardcodes `model_status == "not_better_than_baseline"`. The current E3 artifact selects `dummy_mean`, reports `baseline_only`, and contains 23 trials, ten rooms, and four participants. Once its source metadata is rebuilt for the final implementation, the hardcoded status assertion will fail for this valid prespecified outcome.

Check response status against the loaded artifact and generated model evidence. Extend the same real-artifact verification to generation through direct, CLI and API calls with the same requested score, target, seed and constraints; the current real test only checks that API generation returns two candidates. Confirm identical coordinates/scores across distinct room inputs when the selected estimator is a constant baseline. Do not require artificial room-dependent variation.

T030 is already unchecked, appropriately. Synthetic tests do not substitute for this final fitted-artifact check. Source hash mismatch during concurrent research implementation is expected and is not reported here as an engine regression; rebuild and rerun the actual compatibility path before checking T030.

## Should-fix

### E-03 — Make bounded-search exhaustion wording accurate

Location: `backend/src/pa/optimize/search.py:165–167`.

After finite random sampling, the reason says no supported candidate *satisfies* the constraints. The loop establishes only that none was found within the budget. Use wording such as “No physically valid, supported candidate was found within this search budget under the supplied locks and ranges.” Keep provable category/range contradictions as their more specific early reasons. This preserves the approved closest-found limitation without changing search behavior.

### E-04 — Close small but meaningful test blind spots

Locations: `backend/tests/test_prediction_parity.py:83–88`, `backend/tests/test_optimize.py:102–107`, `backend/tests/test_scoring.py:30–34`.

The generation parity assertion uses `zip` without requiring equal nonzero candidate counts; an empty or truncated CLI/API list can evade comparison. Assert equal lengths and compare the complete ordered payload, including raw/projected coordinates, normalized score, requested score, and support identity. The named support-distance tie test gives every candidate distance zero, so it verifies only the final identity tie. Include equal-score candidates with different support distances. Persist requested-score endpoint checks (0 and 100), all-fields-locked deduplication, and a near-boundary clipping check alongside the E-01 regression. These should remain small scientific-contract tests, not duplicate the implementation.

## Verification performed

Read `AGENTS.md`, Fab project config/constitution/context/code-quality/code-review, intake, R11–R13/R18 and task/acceptance references, active-spec approval amendment, and approved v1.2 PD-006/PD-007. Inspected schema/builder/support/scoring, search, API request/response/error handling, Studio CLI commands, fitted inference, artifact loading, and training feature-frame reuse. Generated OpenAPI/TypeScript outputs were not treated as hand-authored implementation.

Command:

```text
uv run --project backend pytest backend/tests/test_features.py backend/tests/test_scoring.py backend/tests/test_optimize.py backend/tests/test_api.py backend/tests/test_prediction_parity.py -q
24 passed, 1 warning in 5.76s
```

The warning is the existing Starlette `httpx` TestClient deprecation.

Additional read-only numerical probes used a declared synthetic constant fitted-model stand-in and actual E3 support. They produced:

- Opposite corners: displayed score `0`; equal corners: `100`.
- Just inside the opposite corner (`-1 + 1e-12` on both axes, target `(1,1)`): approximately `5.00044e-11`; just inside the target: `99.99999999995`; raw coordinates just outside the target project to score `100`.
- All thirteen independent fields locked: `ok`, one evaluated/distinct candidate despite budget 40.
- Door-count range `[1.1, 1.9]`: explicit `empty`, zero predictions.
- Contradictory locked space type and requested category: explicit `empty`, zero predictions; locks were not relaxed.
- Requested scores 0 and 100: valid candidates with the same constant prediction and correct requested/achieved/difference semantics; no fabricated model variation.
- E-01's actual-room support discrepancy, with distances reported above.

The existing 64.5-versus-95 test passes, preserves a separate emotional target, and verifies that 64.5 is preferred for request 65. Existing API tests also pass for missing/malformed artifacts, nonfinite fitted outputs, invalid room inputs, invalid locks/ranges, and readiness versus liveness.

## Remaining boundary

This report does not approve research interpretation, CP-C publication, frontend readiness/interaction, or whole-change acceptance. Recheck the two must-fix items and final artifact parity after the research and engine sources settle; no unrelated long-running negative-control job is required merely to finish this scoped review.
