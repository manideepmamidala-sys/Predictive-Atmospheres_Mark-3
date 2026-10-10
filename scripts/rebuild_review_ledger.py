"""Rebuild the integrated CP-B ledger from raw evidence and approved AI decisions.

Run after ``make setup`` when ``artifacts/results/qc_review.json`` is absent.
This deliberately does not invent an owner signature or review time.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess

from pa.config import ROOT
from pa.io.checkpoint import load_reviewed_qc
from pa.results.disposition import (
    ECG_REVIEW,
    EEG_REVIEW,
    QUEUE,
    REPORT,
    SIGNALS,
    TIMEBASE,
    integrate_decisions,
)

# The reviewed CP-B JSON placed pending-queue provenance after the evidence
# arrays. The current pending-queue writer inserts those fields earlier. Keep
# the approved ledger's original serialization order for an exact byte/hash
# reconstruction; this does not alter any decision or value.
REVIEWED_KEY_ORDER = (
    "schema_version", "method_version", "approved_spec_sha256", "owner_verdict",
    "summary", "examples", "worst_duration_mismatch", "trials", "entries",
    "signals_sha256", "timebase_sha256", "eligibility_integrated",
    "generated_date_utc", "delegated_verdict", "authorization_quote",
    "reviewers", "reviewer_file_sha256", "reviewed_at_utc",
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expected-sha256", help="Expected byte digest of reviewed ledger")
    args = parser.parse_args()
    if QUEUE.exists():
        raise SystemExit(f"Remove the existing generated ledger before source-only rebuild: {QUEUE}")
    report_bytes = REPORT.read_bytes()
    report = report_bytes.decode()
    if "**Delegated QC verdict:** APPROVED_FOR_REANALYSIS_WITH_EXCLUSIONS" not in report:
        raise SystemExit("Approved delegated CP-B report is missing")
    match = re.search(r"^\*\*Reviewed:\*\* (\S+) by ", report, flags=re.MULTILINE)
    if not match:
        raise SystemExit("Approved CP-B report lacks a recorded review timestamp")
    reviewed_at = match.group(1)
    try:
        subprocess.run(["make", "qc-review"], cwd=ROOT, check=True)
        pending = json.loads(QUEUE.read_text())
        if pending.get("eligibility_integrated"):
            raise SystemExit("Expected a pending queue before integrating CP-B decisions")
        # The queue's wall-clock creation date is provenance, not a new review.
        # Recover the reviewed record's date so a later rebuild has identical bytes.
        pending["generated_date_utc"] = reviewed_at[:10]
        eeg = json.loads(EEG_REVIEW.read_text())
        ecg = json.loads(ECG_REVIEW.read_text())
        product = integrate_decisions(pending, json.loads(SIGNALS.read_text()),
                                      json.loads(TIMEBASE.read_text()), eeg, ecg,
                                      reviewed_at=reviewed_at)
        if set(product) != set(REVIEWED_KEY_ORDER):
            raise SystemExit("Reconstructed CP-B ledger has unexpected top-level fields")
        ordered = {key: product[key] for key in REVIEWED_KEY_ORDER}
        QUEUE.write_text(json.dumps(ordered, indent=2, allow_nan=False) + "\n")
    finally:
        REPORT.write_bytes(report_bytes)
    load_reviewed_qc()
    digest = hashlib.sha256(QUEUE.read_bytes()).hexdigest()
    if args.expected_sha256 and digest != args.expected_sha256:
        raise SystemExit(f"Reconstructed CP-B ledger hash differs: {digest} != {args.expected_sha256}")
    print(f"Reconstructed approved CP-B review ledger sha256={digest}")


if __name__ == "__main__":
    main()
