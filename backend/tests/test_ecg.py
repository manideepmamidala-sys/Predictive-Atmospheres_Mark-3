import json

import numpy as np
import pytest

from pa.signals.ecg import ecg_review_examples, process_ecg


def synthetic_ecg(beat_times, duration=36, sample_rate=500):
    t = np.arange(duration * sample_rate) / sample_rate
    raw = 0.005 * np.sin(2 * np.pi * 3 * t)
    for beat in beat_times:
        raw += np.exp(-0.5 * ((t - beat) / 0.012) ** 2)
    return raw


def test_known_rr_and_rmssd_units():
    beat_times = [1.0]
    for index in range(36):
        beat_times.append(beat_times[-1] + (0.8 if index % 2 == 0 else 0.9))
    result = process_ecg(synthetic_ecg(beat_times), 500, np.arange(500 * 36) % 256)
    assert result.valid_hr and result.valid_rmssd
    assert result.heart_rate_bpm == pytest.approx(60 / 0.85, rel=0.08)
    assert result.rmssd_ms == pytest.approx(100, abs=15)
    inverted = process_ecg(-synthetic_ecg(beat_times), 500, np.arange(500 * 36) % 256)
    assert inverted.valid_rmssd and inverted.rmssd_ms == pytest.approx(100, abs=15)


def test_flat_and_short_ecg_do_not_return_nominal_values():
    result = process_ecg(np.zeros(500 * 40), 500, np.arange(500 * 40) % 256)
    assert result.heart_rate_bpm is None and result.rmssd_ms is None
    result = process_ecg(synthetic_ecg([1, 2, 3, 4, 5, 6], duration=10), 500, np.arange(500 * 10) % 256)
    assert result.rmssd_ms is None and not result.valid_rmssd


def test_noise_only_and_clipped_ecg_have_no_plausible_output():
    fs = 500
    counter = np.arange(fs * 36) % 256
    for seed in (0, 1, 2):
        result = process_ecg(np.random.default_rng(seed).normal(size=len(counter)), fs, counter)
        assert not result.valid_hr and not result.valid_rmssd
        assert result.heart_rate_bpm is None and result.rmssd_ms is None
        assert "no_qrs_quality" in result.reasons
    t = np.arange(len(counter)) / fs
    clipped = np.clip(100 * np.sin(2 * np.pi * 10 * t), -1, 1)
    result = process_ecg(clipped, fs, counter)
    assert not result.valid_rmssd and "repeated_extrema_possible_clipping" in result.reasons


def test_gap_and_dropout_break_usable_interval_coverage():
    fs = 500
    beats = np.arange(1.0, 35.0, 0.8)
    signal = synthetic_ecg(beats)
    counter = np.arange(len(signal)) % 256
    broken = counter.copy()
    broken[18 * fs:] = (broken[18 * fs:] + 2) % 256
    result = process_ecg(signal, fs, broken)
    assert not result.valid_rmssd and result.rmssd_ms is None
    assert any(item["reason"] == "counter_discontinuity" for item in result.excluded_segments)
    assert result.rmssd_scenarios["sensitivity_10s"]["valid"]
    dropout = signal.copy()
    dropout[18 * fs:19 * fs] = 0
    result = process_ecg(dropout, fs, counter)
    assert not result.valid_rmssd and result.rmssd_ms is None
    assert any(item["reason"] == "flat_dropout" for item in result.excluded_segments)


def test_usable_coverage_not_source_length_controls_rmssd():
    fs = 500
    beats = [1.0]
    for index in range(35):
        beats.append(beats[-1] + (0.8 if index % 2 == 0 else 0.9))
    result = process_ecg(synthetic_ecg(beats), fs, np.arange(fs * 36) % 256)
    assert result.sample_duration_s == 36
    assert not result.valid_rmssd
    assert result.rmssd_scenarios["sensitivity_20s"]["valid"]
    assert result.rmssd_scenarios["sensitivity_10s"]["valid"]


def test_coverage_and_examples_keep_filterable_and_valid_rr_seconds_distinct():
    fs = 500
    raw = synthetic_ecg(np.arange(1.0, 35.0, 0.8))
    result = process_ecg(raw, fs, np.arange(len(raw)) % 256)
    coverage = result.coverage
    assert coverage["source_seconds"] == 36
    assert coverage["filterable_seconds"] == 36
    assert 0 < coverage["valid_rr_seconds"] <= coverage["filterable_seconds"]
    assert coverage["longest_valid_run"]["covered_seconds"] >= 30
    assert coverage["heart_rate_run"]["valid_intervals"] >= 5
    assert result.eligibility["heart_rate"]["automated_eligible"]
    assert result.eligibility["rmssd_30s"]["automated_eligible"]
    assert result.eligibility["human_review"] == "pending_cp_b"
    examples = ecg_review_examples(raw, result)
    accepted = next(item for item in examples if item["kind"] == "accepted_run")
    assert accepted["sample_rate_hz"] == fs
    assert accepted["start_s"] == pytest.approx(accepted["start_sample"] / fs)
    assert len(accepted["raw"]) == len(accepted["filtered"]) == fs * 4
    assert accepted["raw_spectrum"]["frequency_hz"] == \
        accepted["filtered_spectrum"]["frequency_hz"]
    assert accepted["amplitude_unit"] == "unverified raw amplitude"


def test_gap_coverage_and_review_example_never_filter_across_discontinuity():
    fs = 500
    raw = synthetic_ecg(np.arange(1.0, 35.0, 0.8))
    counter = np.arange(len(raw)) % 256
    counter[18 * fs:] = (counter[18 * fs:] + 2) % 256
    result = process_ecg(raw, fs, counter)
    coverage = result.coverage
    assert coverage["filterable_seconds"] == 36
    assert coverage["valid_rr_seconds"] > coverage["longest_valid_run"]["covered_seconds"]
    assert coverage["longest_valid_run"]["covered_seconds"] < 30
    assert coverage["rmssd_30s_run"] is None
    assert not result.eligibility["rmssd_30s"]["automated_eligible"]
    assert result.rmssd_scenarios["sensitivity_10s"]["valid"]
    examples = ecg_review_examples(raw, result)
    gap = next(item for item in examples if item["reason"] == "counter_discontinuity")
    assert gap["filtered"] is None and gap["filtered_spectrum"] is None
    assert gap["raw_spectrum"] is None


def test_rejected_channel_has_explicit_coverage_and_raw_review_evidence():
    fs = 500
    raw = np.zeros(fs * 8)
    result = process_ecg(raw, fs, np.arange(len(raw)) % 256)
    assert result.coverage["filterable_seconds"] == 0
    assert result.coverage["valid_rr_seconds"] == 0
    assert result.eligibility["heart_rate"]["automated_eligible"] is False
    assert result.eligibility["rmssd_30s"]["automated_eligible"] is False
    examples = ecg_review_examples(raw, result)
    assert examples and all(item["filtered"] is None for item in examples)
    assert any(item["reason"] == "flat_dropout" for item in examples)


def test_nonfinite_channel_keeps_serializable_raw_review_evidence():
    fs = 500
    raw = synthetic_ecg(np.arange(1.0, 7.0, 0.8), duration=8)
    raw[3 * fs] = np.nan
    result = process_ecg(raw, fs, np.arange(len(raw)) % 256)
    assert not result.valid_hr and result.heart_rate_bpm is None
    examples = ecg_review_examples(raw, result)
    assert examples[0]["reason"] == "nonfinite_samples"
    assert None in examples[0]["raw"]
    assert examples[0]["raw_spectrum"] is None
    json.dumps(examples, allow_nan=False)


def test_every_ecg_example_spanning_counter_gap_suppresses_raw_spectrum():
    fs = 500
    raw = synthetic_ecg(np.arange(1.0, 11.0, 0.8), duration=12)
    counter = np.arange(len(raw)) % 256
    counter[5 * fs:] = (counter[5 * fs:] + 2) % 256
    counter[6 * fs:] = (counter[6 * fs:] + 2) % 256
    result = process_ecg(raw, fs, counter)
    gaps = [round(item["start_s"] * fs) for item in result.excluded_segments
            if item["reason"] == "counter_discontinuity"]
    examples = ecg_review_examples(raw, result)
    assert gaps == [5 * fs, 6 * fs]
    assert any(item["reason"] != "counter_discontinuity" and
               any(item["start_sample"] < gap < item["stop_sample"] for gap in gaps)
               for item in examples)
    assert all(item["raw_spectrum"] is None
               for item in examples
               if any(item["start_sample"] < gap < item["stop_sample"] for gap in gaps))
