# Independent implementation review — T013–T018

**Date:** 2026-10-10 UTC. **Reviewer route:** Codex `gpt-6-astra`, `xhigh`, independently dispatched from the implementation worker.

**Verdict:** No unresolved must-fix findings in this checkpoint slice. The generated package is ready for **owner CP-B review**, with all owner decisions still pending. This is not a formal Fab review-stage verdict, whole-apply pass, physiological validity certification, or permission to run dependent analysis. T019 and subsequent tasks remain outside this verdict.

The review covered approval provenance, conditional timebase, EEG candidates and per-channel missingness, cardiac coverage, review evidence, and the pending checkpoint boundary. It used AGENTS.md, project config/constitution/context/code-quality/code-review, plan Requirements and T013–T018, the retained v1.1 details, and the exact approved v1.2 source. Implementation files were reviewed without edits; this report is the reviewer's only authored artifact. No Acceptance items or stage transitions were performed.

## Findings and resolution

| Priority | Finding identified during review | Verified resolution |
| --- | --- | --- |
| Must-fix | FAA initially logged median powers instead of taking the median of each epoch's log-power difference. A five-epoch amplitude permutation returned 0 instead of −0.575364. | `backend/src/pa/signals/eeg.py:340` computes the per-epoch expression before aggregation; variable-epoch regression passes. |
| Must-fix | Two independently eligible channels with insufficient paired overlap lost all cortical candidates. | `backend/src/pa/signals/eeg.py:287` retains candidates under explicit `independent_right_left` scope and contributor counts; FAA remains unavailable. The disjoint-channel regression passes. |
| Must-fix | Initial panels omitted rejected EEG spectra and flagged ECG windows/spectra; overview decimation could hide a transient. | `backend/src/pa/results/review.py:295` and `:338` provide full-resolution, source-indexed accepted and flagged detail windows, raw/eligible-filtered spectra, and ECG candidate peaks. Gap spectra remain unavailable. Generated examples were visually inspected. |
| Must-fix | Generic epoch-rejection labels hid specific severe EEG reasons from the owner queue. | `backend/src/pa/results/review.py:154` retains actual reasons and rejected-epoch records. Severe entries link the corresponding detailed channel panel; imbalance entries link both channels. |
| Must-fix | ECG windows labelled short/dropout could contain a counter gap while retaining a raw PSD. | `backend/src/pa/signals/ecg.py:373` checks gap overlap independently of the example label. The two-gap regression passes; no generated ECG example crossing a known gap retains a PSD. |
| Must-fix | Five-second onset sensitivity initially covered EEG only. | `backend/src/pa/signals/run.py:58` adds an independently processed ECG sensitivity with cropped raw/counter arrays and source-offset provenance. All 160 exported rows have the 2,500-sample offset, correct conditional duration and fresh coverage. |
| Should-fix | New EEG thresholds and bands initially duplicated versioned settings as literals. | Defaults now read the versioned settings (`eeg.py:97` and associated band/threshold calculations). Explicit sensitivity overrides remain inspectable. |

The approved phrase “robust raw per-epoch standard deviations” does not specify a within-epoch MAD estimator. Ordinary epoch standard deviations followed by the explicitly required median of paired ratios is a defensible reading. CP-B now states that calculation precisely; the review did not introduce an unapproved MAD-based replacement.

## Verification evidence

- `uv run --project backend pytest backend/tests/test_eeg.py backend/tests/test_ecg.py backend/tests/test_audit.py backend/tests/test_science_gate.py -q` — **27 passed** after the scientific fixes. The final gate hardening was then checked with `backend/tests/test_science_gate.py` — **3 passed**.
- Independently recomputed all four epoch-median expressions (FAA, alpha suppression, engagement, muscle) directly from source samples for one trial in each experiment; each matched exported values to `1e-12` tolerance.
- Timebase contains 160 unique trials and all four conditional rates (250/256/500/512 Hz), six duration-mismatch flags and 38 counter-flagged recordings. Mismatches are flags, not automatic exclusions.
- Final queue contains **346 pending entries across 152 flagged trials**, with **160 unique ledger rows** (E1 50, E2 50, E3 60) and **330 linked panels**. All 487 Markdown links resolve. Queue entry identities, flags, evidence and pending decisions match derivation from the final signal/timebase products.
- Every owner status is `pending`; reason, reviewer and review time remain null. `owner_verdict` is `pending` and `eligibility_integrated` is false. No human decisions were fabricated.
- Representatives include automated accepted and rejected records in every experiment. All 20 imbalance entries link both channel panels. The maximum mismatch is linked: E3:Subj_M:Rm_021, 73.4633% at conditional 500 Hz.
- Visual inspection included E1:Subj_A:Rm_001 EEG/ECG gap examples; E1:Subj_B:Rm_010 accepted ECG and candidate peaks; E2:Subj_M:Rm_017 right-channel severe transient; E2:Subj_F:Rm_020 left-channel imbalance evidence; both E3:Subj_H:Rm_021 channels; and the maximum-mismatch overview. These inspections assessed evidence usability, not owner signal dispositions.
- Approved QC runs are permitted. Dependent processing raises the pending CP-B error. The historical fitted model fails current method/code/spec compatibility rather than being served as v1.2; retained affect/model outputs identify v1.1.

## Reviewed artifact identity and boundary

| Artifact | SHA-256 |
| --- | --- |
| Approved source `docs/specs/analysis-v1.2-draft.md` | `51c01ef6ccdf2f4318ac786d1bb39afeb1aa2bcf3bc93039479a4ed2454603ac` |
| `artifacts/results/signals_detail.json` | `ec1001ac3bc53c15d3afd3b565756666b2b418670057ce8ba8011036d999c4b1` |
| `artifacts/results/timebase.json` | `07927368f68553d069ced78235d5131693fec0f2a74fd3df98bfc88660ccc604` |
| `artifacts/results/qc_review.json` | `0c2dd17cba43a7eb6eb597dab4383b78ca055a6a5ddd2806a082d6c918195066` |

The queue and [CP-B report](CP-B.md) identify the matching final signal/timebase hashes. Automated bilateral EEG eligibility (160), HR eligibility (71) and primary RMSSD eligibility (18) are screening outcomes only. They do not establish cortical origin, verified normal beats or complete physiology. No blanket Subj_F/Subj_H exclusion was introduced. T019 must record and integrate actual owner dispositions before dependent interpretation; this review does not supply those decisions.
