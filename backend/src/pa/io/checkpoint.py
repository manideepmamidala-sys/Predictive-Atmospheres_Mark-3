"""Version-aware scientific result gates and approved-method provenance."""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path

from pa.config import ROOT
from pa.signals.common import decisions


def require_science_checkpoint(
    path: Path = ROOT / "docs/reports/analysis-checkpoint.md", *, stage: str = "dependent"
) -> None:
    """Allow approved QC, but hold v1.2 dependent products until signed CP-B."""
    settings = decisions()
    if not settings["version"].startswith("1.2."):
        if not path.exists() or "**Coordinator verdict:** PASS" not in path.read_text():
            raise RuntimeError("scientific processing held until recorded independent checkpoint PASS")
        return

    spec = ROOT / settings["approved_spec_path"]
    approved_hash = settings["approved_spec_sha256"]
    if not spec.exists() or hashlib.sha256(spec.read_bytes()).hexdigest() != approved_hash:
        raise RuntimeError("v1.2 approved specification hash mismatch")
    approval = ROOT / settings["approval_record"]
    if not approval.exists() or approved_hash not in approval.read_text() or \
            "**Status: OWNER APPROVED" not in approval.read_text():
        raise RuntimeError("v1.2 CP-Spec approval record missing or mismatched")
    if stage == "qc":
        return
    if stage != "dependent":
        raise ValueError(f"unknown science checkpoint stage: {stage}")
    load_reviewed_qc()


def load_reviewed_qc() -> dict:
    """Reconcile exact reviewed decisions and source evidence before dependent use."""
    from pa.results.disposition import (
        ECG_REVIEW,
        EEG_REVIEW,
        QUEUE,
        SIGNALS,
        TIMEBASE,
        integrate_decisions,
    )

    settings = decisions()
    cp_b = ROOT / settings["qc_review_checkpoint"]
    if not cp_b.exists() or \
            "**Delegated QC verdict:** APPROVED_FOR_REANALYSIS_WITH_EXCLUSIONS" not in cp_b.read_text():
        raise RuntimeError("v1.2 dependent science held until delegated CP-B disposition")
    if not all(path.exists() for path in (QUEUE, SIGNALS, TIMEBASE, EEG_REVIEW, ECG_REVIEW)):
        raise RuntimeError("v1.2 CP-B source or reviewer evidence missing")
    review = json.loads(QUEUE.read_text())
    entries = review.get("entries", [])
    approved_hash = settings["approved_spec_sha256"]
    if (review.get("approved_spec_sha256") != approved_hash or
            review.get("delegated_verdict") != "approved_for_reanalysis_with_exclusions" or
            review.get("owner_verdict") != "delegated_no_personal_review" or
            review.get("eligibility_integrated") is not True or len(entries) != 346 or
            review.get("reviewer_file_sha256") != {
                "eeg": hashlib.sha256(EEG_REVIEW.read_bytes()).hexdigest(),
                "ecg": hashlib.sha256(ECG_REVIEW.read_bytes()).hexdigest()}):
        raise RuntimeError("v1.2 CP-B disposition provenance missing or mismatched")
    before_entries = deepcopy(entries)
    before_trials = deepcopy(review["trials"])
    try:
        expected = integrate_decisions(deepcopy(review), json.loads(SIGNALS.read_text()),
                                       json.loads(TIMEBASE.read_text()),
                                       json.loads(EEG_REVIEW.read_text()),
                                       json.loads(ECG_REVIEW.read_text()),
                                       reviewed_at=review["reviewed_at_utc"])
    except (KeyError, TypeError, ValueError) as exc:
        raise RuntimeError(f"v1.2 CP-B source/decision reconciliation failed: {exc}") from exc
    if expected["entries"] != before_entries or expected["trials"] != before_trials:
        raise RuntimeError("v1.2 CP-B integrated eligibility differs from reviewed decisions")
    return review
