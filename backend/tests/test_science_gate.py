import pytest

from pa.io.checkpoint import require_science_checkpoint


def test_real_science_gate_requires_recorded_coordinator_pass(tmp_path, monkeypatch):
    from pa.io import checkpoint as gate

    monkeypatch.setattr(gate, "decisions", lambda: {"version": "1.1.0"})
    checkpoint = tmp_path / "checkpoint.md"
    with pytest.raises(RuntimeError, match="checkpoint PASS"):
        require_science_checkpoint(checkpoint)
    checkpoint.write_text("**Coordinator verdict:** FAIL")
    with pytest.raises(RuntimeError, match="checkpoint PASS"):
        require_science_checkpoint(checkpoint)
    checkpoint.write_text("**Coordinator verdict:** PASS")
    require_science_checkpoint(checkpoint)


def test_v12_qc_requires_exact_approved_source_and_dependent_work_requires_cp_b(
    tmp_path, monkeypatch
):
    import hashlib

    from pa.io import checkpoint as gate

    draft = tmp_path / "approved.md"
    draft.write_text("approved exact source")
    digest = hashlib.sha256(draft.read_bytes()).hexdigest()
    approval = tmp_path / "CP-Spec.md"
    approval.write_text(f"**Status: OWNER APPROVED**\n{digest}\n")
    settings = {
        "version": "1.2.0", "approved_spec_path": "approved.md",
        "approved_spec_sha256": digest, "approval_record": "CP-Spec.md",
        "qc_review_checkpoint": "CP-B.md",
    }
    monkeypatch.setattr(gate, "ROOT", tmp_path)
    monkeypatch.setattr(gate, "decisions", lambda: settings)
    gate.require_science_checkpoint(stage="qc")
    with pytest.raises(RuntimeError, match="delegated CP-B disposition"):
        gate.require_science_checkpoint()
    (tmp_path / "CP-B.md").write_text("**Owner verdict:** APPROVED\n")
    with pytest.raises(RuntimeError, match="delegated CP-B disposition"):
        gate.require_science_checkpoint()
    (tmp_path / "CP-B.md").write_text(
        "**Delegated QC verdict:** APPROVED_FOR_REANALYSIS_WITH_EXCLUSIONS\n")
    with pytest.raises(RuntimeError, match="provenance missing or mismatched"):
        gate.require_science_checkpoint()
    draft.write_text("changed after approval")
    with pytest.raises(RuntimeError, match="hash mismatch"):
        gate.require_science_checkpoint(stage="qc")


def test_integrated_cp_b_rejects_tampered_disposition(tmp_path, monkeypatch):
    import json

    from pa.io import checkpoint as gate
    from pa.results import disposition

    gate.require_science_checkpoint()
    queue = tmp_path / "qc_review.json"
    data = json.loads(disposition.QUEUE.read_text())
    data["entries"][0]["decision"]["status"] = "reject"
    queue.write_text(json.dumps(data))
    monkeypatch.setattr(disposition, "QUEUE", queue)
    with pytest.raises(RuntimeError, match="differs from reviewed decisions"):
        gate.require_science_checkpoint()


def test_qc_review_regeneration_preserves_exact_integrated_decisions(tmp_path):
    from pa.results.disposition import QUEUE, SIGNALS, TIMEBASE
    from pa.results.review import write_qc_review

    queue = tmp_path / "qc_review.json"
    signals = tmp_path / "signals_detail.json"
    timebase = tmp_path / "timebase.json"
    queue.write_bytes(QUEUE.read_bytes())
    signals.write_bytes(SIGNALS.read_bytes())
    timebase.write_bytes(TIMEBASE.read_bytes())
    original = queue.read_bytes()
    result = write_qc_review(signals_path=signals, timebase_path=timebase,
                             queue_path=queue, panel_dir=tmp_path / "panels",
                             report_path=tmp_path / "CP-B.md")
    assert result["eligibility_integrated"] is True
    assert queue.read_bytes() == original
    signals.write_bytes(signals.read_bytes() + b"\n")
    with pytest.raises(RuntimeError, match="source/method changed"):
        write_qc_review(signals_path=signals, timebase_path=timebase,
                        queue_path=queue, panel_dir=tmp_path / "panels",
                        report_path=tmp_path / "CP-B.md")
    assert queue.read_bytes() == original


def test_conditional_trial_processing_preserves_missing_ecg_and_rate_scenarios():
    import numpy as np

    from pa.io.metadata import Trial
    from pa.io.recordings import Recording
    from pa.signals.run import process_trial

    sample_rate = 500
    t = np.arange(sample_rate * 12) / sample_rate
    eeg = np.sin(2 * np.pi * 10 * t)
    trial = Trial(1, "P1", "R1", "synthetic.csv", 12, 0.2, None, None, None,
                  "synthetic_test_fixture")
    recording = Recording(np.arange(len(t)) % 256, eeg, eeg, np.zeros(len(t)))
    result = process_trial(trial, recording)
    assert result["eeg"]["valid"]
    assert result["ecg"]["heart_rate_bpm"] is None
    assert result["ecg"]["rmssd_ms"] is None
    assert {entry["rate_hz"] for entry in result["rate_scenarios"]} == {250, 256, 500, 512}
    assert len(result["eeg_trace"]["raw"]) == sample_rate * 4
    onset_ecg = result["sensitivity"]["ecg_first_5_s_excluded"]
    assert onset_ecg["source_offset_samples"] == sample_rate * 5
    assert onset_ecg["ecg"]["sample_duration_s"] == 7
    assert onset_ecg["ecg"]["heart_rate_bpm"] is None
