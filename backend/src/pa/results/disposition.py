"""Integrate delegated CP-B judgments without promoting invalid source measurements."""

from __future__ import annotations

import hashlib
from collections import Counter
from pathlib import Path

from pa.config import ROOT
from pa.results.review import _review_entries
from pa.signals.common import decisions

QUEUE = ROOT / "artifacts/results/qc_review.json"
SIGNALS = ROOT / "artifacts/results/signals_detail.json"
TIMEBASE = ROOT / "artifacts/results/timebase.json"
EEG_REVIEW = ROOT / "docs/reports/revision-2026-10/cp-b-eeg-decisions.json"
ECG_REVIEW = ROOT / "docs/reports/revision-2026-10/cp-b-ecg-decisions.json"
REPORT = ROOT / "docs/reports/revision-2026-10/CP-B.md"
AUTHORIZATION = (
    "$fab-ff with your CP-B decidions; "
    "$fab-ff approve all the future checkpoint automatically and continue the work"
)
VALID = {"accept", "reject", "uncertain"}


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _index(items: list[dict], key: str, label: str) -> dict[str, dict]:
    indexed = {item[key]: item for item in items}
    if len(indexed) != len(items):
        raise ValueError(f"duplicate {label} identity")
    return indexed


def _check_decision(item: dict, *, label: str) -> None:
    if item.get("status") not in VALID or not isinstance(item.get("reason"), str) or not item["reason"].strip():
        raise ValueError(f"incomplete {label} disposition")
    if not item.get("evidence"):
        raise ValueError(f"missing {label} evidence")


def integrate_decisions(queue: dict, signals: dict, timebase: dict,
                        eeg: dict, ecg: dict, *, reviewed_at: str) -> dict:
    spec_hash = decisions()["approved_spec_sha256"]
    if queue.get("approved_spec_sha256") != spec_hash or \
            signals.get("approved_spec_sha256") != spec_hash or \
            timebase.get("approved_spec_sha256") != spec_hash:
        raise ValueError("approved source spec mismatch")
    if queue.get("signals_sha256") != _digest(SIGNALS) or \
            queue.get("timebase_sha256") != _digest(TIMEBASE):
        raise ValueError("review queue source hashes changed")
    source = _index(signals["trials"], "id", "signal trial")
    times = _index(timebase["trials"], "trial_id", "timebase trial")
    ledger = _index(queue["trials"], "trial_id", "queue trial")
    if len(source) != 160 or set(source) != set(times) or set(source) != set(ledger):
        raise ValueError("source and queue do not cover exactly 160 trials")
    expected_entries = _index([entry for row in source.values()
                               for entry in _review_entries(row, times[row["id"]])],
                              "id", "expected queue entry")
    queued_entries = _index(queue["entries"], "id", "queue entry")
    if len(queued_entries) != 346 or set(queued_entries) != set(expected_entries):
        raise ValueError("queue entry identities differ from fixed source QC")
    for entry_id, expected in expected_entries.items():
        queued = queued_entries[entry_id]
        if any(queued[field] != expected[field] for field in
               ("trial_id", "signal", "experiment", "participant_id", "room_id",
                "flags", "automated_eligible", "evidence")):
            raise ValueError(f"queue entry source evidence changed: {entry_id}")
    eeg_entries = _index(eeg["entries"], "id", "EEG review entry")
    ecg_entries = _index(ecg["entries"], "id", "ECG/timebase review entry")
    if set(eeg_entries) & set(ecg_entries) or set(eeg_entries) | set(ecg_entries) != set(queued_entries):
        raise ValueError("reviewers do not cover every queue entry exactly once")
    channels = _index(eeg["channels"], "id", "EEG channel")
    ecg_trials = _index(ecg["trials"], "trial_id", "ECG trial")
    expected_channels = {f"{trial}:{signal}" for trial in source
                         for signal in ("eeg_right", "eeg_left")}
    if set(channels) != expected_channels or set(ecg_trials) != set(source):
        raise ValueError("reviewer ledger lacks exact channel/trial coverage")
    for entry_id, entry in queued_entries.items():
        judgment = eeg_entries.get(entry_id) or ecg_entries.get(entry_id)
        if judgment["trial_id"] != entry["trial_id"] or judgment["signal"] != entry["signal"]:
            raise ValueError(f"review identity mismatch: {entry_id}")
        _check_decision(judgment, label=entry_id)
        entry["decision"] = {"status": judgment["status"], "reason": judgment["reason"],
                             "evidence": judgment["evidence"],
                             "reviewer": (eeg if entry["signal"].startswith("eeg") else ecg)["reviewer"]["id"],
                             "reviewed_at": reviewed_at}
    for trial_id, row in source.items():
        result = ledger[trial_id]
        if set(result["entry_ids"]) != {entry_id for entry_id, entry in queued_entries.items()
                                         if entry["trial_id"] == trial_id}:
            raise ValueError(f"trial queue entry references changed: {trial_id}")
        ecg_judgment = ecg_trials[trial_id]
        _check_decision(ecg_judgment, label=f"{trial_id}:ecg")
        time_judgment = ecg_judgment["timebase"]
        _check_decision(time_judgment, label=f"{trial_id}:timebase")
        channel_decisions = {}
        for name in ("right", "left"):
            key = f"{trial_id}:eeg_{name}"
            judgment = channels[key]
            _check_decision(judgment, label=key)
            if judgment["trial_id"] != trial_id or judgment["signal"] != f"eeg_{name}":
                raise ValueError(f"channel identity mismatch: {key}")
            if key in eeg_entries and eeg_entries[key]["status"] != judgment["status"]:
                raise ValueError(f"queued channel and ledger conflict: {key}")
            channel_decisions[name] = judgment["status"]
        if f"{trial_id}:ecg" in ecg_entries and \
                ecg_entries[f"{trial_id}:ecg"]["status"] != ecg_judgment["status"]:
            raise ValueError(f"queued ECG and ledger conflict: {trial_id}")
        if f"{trial_id}:timebase" in ecg_entries and \
                ecg_entries[f"{trial_id}:timebase"]["status"] != time_judgment["status"]:
            raise ValueError(f"queued timebase and ledger conflict: {trial_id}")
        eeg_trial = eeg_entries.get(f"{trial_id}:eeg_trial")
        trial_status = eeg_trial["status"] if eeg_trial else "accept"
        time_ok = time_judgment["status"] == "accept"
        right_ok = time_ok and channel_decisions["right"] == "accept" and \
            row["eeg"]["channel_qc"]["right"]["eligible"]
        left_ok = time_ok and channel_decisions["left"] == "accept" and \
            row["eeg"]["channel_qc"]["left"]["eligible"]
        hr_ok = time_ok and ecg_judgment["status"] == "accept" and row["ecg"]["valid_hr"]
        rmssd_ok = time_ok and ecg_judgment["status"] == "accept" and row["ecg"]["valid_rmssd"]
        result["reviewed_eligibility"] = {
            "timebase": time_ok, "eeg_right": bool(right_ok), "eeg_left": bool(left_ok),
            "eeg_bilateral": bool(row["eeg"]["valid"] and right_ok and left_ok and
                                  trial_status == "accept"),
            "ecg_hr": bool(hr_ok), "ecg_rmssd": bool(rmssd_ok),
        }
        result["reviewed_disposition"] = {
            "timebase": time_judgment["status"], "eeg_right": channel_decisions["right"],
            "eeg_left": channel_decisions["left"], "eeg_trial": trial_status,
            "ecg": ecg_judgment["status"],
        }
    queue["delegated_verdict"] = "approved_for_reanalysis_with_exclusions"
    queue["owner_verdict"] = "delegated_no_personal_review"
    queue["authorization_quote"] = AUTHORIZATION
    queue["reviewers"] = [eeg["reviewer"]["id"], ecg["reviewer"]["id"]]
    queue["reviewer_file_sha256"] = {"eeg": _digest(EEG_REVIEW), "ecg": _digest(ECG_REVIEW)}
    queue["eligibility_integrated"] = True
    queue["reviewed_at_utc"] = reviewed_at
    queue["summary"]["decision_counts"] = dict(Counter(
        entry["decision"]["status"] for entry in queue["entries"]))
    queue["summary"]["reviewed_eligibility_counts"] = dict(Counter(
        key for trial in queue["trials"]
        for key, value in trial["reviewed_eligibility"].items() if value))
    return queue
