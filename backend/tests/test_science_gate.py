import pytest

from pa.io.checkpoint import require_science_checkpoint


def test_real_science_gate_requires_recorded_coordinator_pass(tmp_path):
    checkpoint = tmp_path / "checkpoint.md"
    with pytest.raises(RuntimeError, match="checkpoint PASS"):
        require_science_checkpoint(checkpoint)
    checkpoint.write_text("**Coordinator verdict:** FAIL")
    with pytest.raises(RuntimeError, match="checkpoint PASS"):
        require_science_checkpoint(checkpoint)
    checkpoint.write_text("**Coordinator verdict:** PASS")
    require_science_checkpoint(checkpoint)


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
