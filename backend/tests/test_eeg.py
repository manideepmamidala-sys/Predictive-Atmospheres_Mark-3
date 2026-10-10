from copy import deepcopy

import numpy as np
import pytest

from pa.signals import eeg as eeg_module
from pa.signals.common import decisions
from pa.signals.eeg import experiment_amplitude_references, process_eeg


def test_known_alpha_asymmetry_and_beta_power():
    fs = 500
    t = np.arange(fs * 20) / fs
    right = 2 * np.sin(2 * np.pi * 10 * t) + 0.5 * np.sin(2 * np.pi * 20 * t)
    left = np.sin(2 * np.pi * 10 * t) + 0.5 * np.sin(2 * np.pi * 20 * t)
    result = process_eeg(right, left, np.arange(len(t)) % 256, fs)
    assert result.valid and result.accepted_epochs == 5
    assert result.forehead_log_alpha_asymmetry == pytest.approx(np.log(4), abs=0.12)
    assert result.beta_right > 0 and result.beta_left > 0
    assert result.theta_right > 0 and result.theta_left > 0
    assert result.high_frequency_right > 0 and result.high_frequency_left > 0
    assert result.alpha_suppression == pytest.approx(
        -np.log((result.alpha_right + result.alpha_left) / 2), abs=0.02)
    assert result.engagement == pytest.approx(np.log(
        ((result.beta_right + result.beta_left) / 2) /
        ((result.alpha_right + result.alpha_left) / 2 +
         (result.theta_right + result.theta_left) / 2)), abs=0.02)
    assert result.muscle_activity is not None
    assert result.ocular_activity is None
    assert result.ocular_activity_reason == "unavailable_detector_not_validated"
    assert result.arousal_channel_scope == "bilateral"


def test_faa_uses_median_of_paired_epoch_log_ratios():
    fs = 500
    epoch_t = np.arange(fs * 4) / fs
    wave = (np.sin(2 * np.pi * 10 * epoch_t) +
            0.3 * np.sin(2 * np.pi * 20 * epoch_t))
    right_amplitudes = np.array([1, 2, 3, 4, 5])
    left_amplitudes = np.array([2, 3, 4, 5, 1])
    right = np.concatenate([amplitude * wave for amplitude in right_amplitudes])
    left = np.concatenate([amplitude * wave for amplitude in left_amplitudes])
    result = process_eeg(right, left, np.arange(len(right)) % 256, fs)
    expected = float(np.median(2 * np.log(right_amplitudes / left_amplitudes)))
    assert result.valid and result.accepted_epochs == 5
    assert expected == pytest.approx(-0.5753641449)
    assert result.forehead_log_alpha_asymmetry == pytest.approx(expected, abs=0.02)
    assert np.log(result.alpha_right) - np.log(result.alpha_left) == pytest.approx(0, abs=0.02)
    unit_alpha = result.alpha_right / 9
    epoch_mean_alpha = unit_alpha * (right_amplitudes**2 + left_amplitudes**2) / 2
    assert result.alpha_suppression == pytest.approx(
        float(np.median(-np.log(epoch_mean_alpha))), abs=0.02)


def test_flat_short_and_discontinuous_eeg_are_invalid():
    fs = 500
    flat = np.zeros(fs * 20)
    assert not process_eeg(flat, flat, np.arange(len(flat)) % 256, fs).valid
    short = np.sin(2 * np.pi * 10 * np.arange(fs * 4) / fs)
    assert not process_eeg(short, short, np.arange(len(short)) % 256, fs).valid
    signal = np.sin(2 * np.pi * 10 * np.arange(fs * 12) / fs)
    counter = np.arange(len(signal)) % 256
    counter[fs * 4:] = (counter[fs * 4:] + 2) % 256
    result = process_eeg(signal, signal, counter, fs)
    assert not result.valid and any("counter_discontinuity" in item["reasons"]
                                    for item in result.rejected_epochs)


def test_sustained_clipping_and_isolated_spike_are_rejected_before_filtering():
    fs = 500
    t = np.arange(fs * 30) / fs
    counter = np.arange(len(t)) % 256
    clipped = np.clip(100 * np.sin(2 * np.pi * 10 * t), -1, 1)
    clipped_result = process_eeg(clipped, clipped, counter, fs)
    assert not clipped_result.valid
    assert all("repeated_extrema_possible_clipping" in epoch["reasons"]
               for epoch in clipped_result.rejected_epochs)
    healthy = np.sin(2 * np.pi * 10 * t)
    spiked = healthy.copy()
    spiked[fs * 8 + 100] = 100
    result = process_eeg(spiked, healthy, counter, fs)
    assert result.valid and any("extreme_peak_to_peak" in epoch["reasons"]
                                for epoch in result.rejected_epochs)


def test_dead_channel_preserves_eligible_single_channel_without_faa():
    fs = 500
    t = np.arange(fs * 20) / fs
    healthy = np.sin(2 * np.pi * 10 * t) + 0.4 * np.sin(2 * np.pi * 20 * t)
    result = process_eeg(np.zeros_like(healthy), healthy, np.arange(len(t)) % 256, fs)
    assert not result.valid
    assert result.forehead_log_alpha_asymmetry is None
    assert result.arousal_channel_scope == "single_left"
    assert result.channel_qc["left"]["eligible"]
    assert result.channel_qc["right"]["accepted_epochs"] == 0
    assert result.alpha_right is None and result.alpha_left > 0
    assert all("flat_channel" in item["reasons"]
               for item in result.channel_qc["right"]["rejected_epochs"])
    assert result.alpha_suppression is not None and result.engagement is not None


def test_disjoint_eligible_channels_keep_independent_cortical_candidates():
    fs = 500
    epoch_t = np.arange(fs * 4) / fs
    wave = (np.sin(2 * np.pi * 10 * epoch_t) +
            0.3 * np.sin(2 * np.pi * 20 * epoch_t))
    right = np.concatenate([wave, 2 * wave, 3 * wave, *([np.zeros_like(wave)] * 3)])
    left = np.concatenate([*([np.zeros_like(wave)] * 3), 4 * wave, 5 * wave, 6 * wave])
    result = process_eeg(right, left, np.arange(len(right)) % 256, fs)
    assert not result.valid and result.accepted_epochs == 0
    assert result.channel_qc["right"]["eligible"] and result.channel_qc["left"]["eligible"]
    assert result.forehead_log_alpha_asymmetry is None
    assert result.arousal_channel_scope == "independent_right_left"
    assert result.trial_qc["candidate_epoch_contributors"] == {
        "both": 0, "right_only": 3, "left_only": 3}
    assert result.alpha_suppression is not None
    assert result.engagement is not None
    assert result.muscle_activity is not None


def test_gain_and_imbalance_are_review_flags_without_automatic_exclusion():
    fs = 500
    t = np.arange(fs * 20) / fs
    nominal = np.sin(2 * np.pi * 10 * t) + 0.3 * np.sin(2 * np.pi * 20 * t)
    reference = float(np.std(nominal[:fs * 4]))
    nominal_result = process_eeg(nominal, nominal, np.arange(len(t)) % 256, fs)
    dead_result = process_eeg(np.zeros_like(nominal), nominal, np.arange(len(t)) % 256, fs)
    pooled = experiment_amplitude_references([nominal_result, dead_result])
    assert pooled["right"] == pytest.approx(reference)
    result = process_eeg(11 * nominal, nominal, np.arange(len(t)) % 256, fs,
                         amplitude_reference_raw_std=pooled)
    assert result.valid
    assert result.trial_qc["channel_imbalance_ratio"] == pytest.approx(11)
    assert "channel_imbalance" in result.trial_qc["review_flags"]
    assert "absolute_amplitude_anomaly" in result.channel_qc["right"]["review_flags"]
    assert "absolute_amplitude_anomaly" not in result.channel_qc["left"]["review_flags"]
    assert result.channel_qc["right"]["amplitude_upper_threshold"] == pytest.approx(10 * reference)


def test_review_defaults_follow_versioned_settings(monkeypatch):
    settings = deepcopy(decisions())
    settings["eeg"]["channel_std_ratio_range"] = [0.01, 100.0]
    settings["eeg"]["amplitude_experiment_median_ratio_range"] = [0.01, 20.0]
    settings["eeg"]["raw_line_power_ratio_max"] = 1e6
    settings["eeg"]["filtered_muscle_power_ratio_max"] = 1e6
    monkeypatch.setattr(eeg_module, "decisions", lambda: settings)
    fs = 500
    t = np.arange(fs * 20) / fs
    nominal = np.sin(2 * np.pi * 10 * t) + 0.3 * np.sin(2 * np.pi * 20 * t)
    reference = float(np.std(nominal[:fs * 4]))
    result = process_eeg(11 * nominal, nominal, np.arange(len(t)) % 256, fs,
                         amplitude_reference_raw_std={"right": reference, "left": reference})
    assert result.valid
    assert "channel_imbalance" not in result.trial_qc["review_flags"]
    assert "absolute_amplitude_anomaly" not in result.channel_qc["right"]["review_flags"]
    assert result.channel_qc["right"]["amplitude_upper_threshold"] == pytest.approx(20 * reference)
    assert result.channel_qc["right"]["line_noise_threshold"] == 1e6
    assert result.channel_qc["right"]["muscle_threshold"] == 1e6


def test_line_noise_and_muscle_flags_use_different_spectrum_stages():
    fs = 500
    t = np.arange(fs * 20) / fs
    counter = np.arange(len(t)) % 256
    base = np.sin(2 * np.pi * 10 * t) + 0.3 * np.sin(2 * np.pi * 20 * t)
    line = base + 5 * np.sin(2 * np.pi * 50 * t)
    line_result = process_eeg(line, line, counter, fs)
    assert line_result.valid
    assert "residual_line_noise" in line_result.channel_qc["right"]["review_flags"]
    assert line_result.channel_qc["right"]["line_noise_ratio"] > 0.20
    muscle = base + 5 * np.sin(2 * np.pi * 38 * t)
    muscle_result = process_eeg(muscle, muscle, counter, fs)
    assert muscle_result.valid
    assert "high_frequency_muscle_candidate" in muscle_result.channel_qc["left"]["review_flags"]
    assert muscle_result.channel_qc["left"]["muscle_ratio"] > 0.25
    assert muscle_result.muscle_activity > line_result.muscle_activity


def test_blink_like_transient_gap_and_nonfinite_sample_have_epoch_reasons():
    fs = 500
    t = np.arange(fs * 24) / fs
    base = np.sin(2 * np.pi * 10 * t) + 0.3 * np.sin(2 * np.pi * 20 * t)
    counter = np.arange(len(t)) % 256
    transient = base.copy()
    transient[fs * 5:fs * 5 + 200] += 20 * np.hanning(200)
    blink_result = process_eeg(transient, base, counter, fs)
    assert blink_result.valid
    assert any("extreme_peak_to_peak" in item["reasons"]
               for item in blink_result.channel_qc["right"]["rejected_epochs"])
    assert blink_result.ocular_activity is None
    assert blink_result.channel_qc["left"]["accepted_epochs"] == 6

    gap_counter = counter.copy()
    gap_counter[fs * 4:] = (gap_counter[fs * 4:] + 2) % 256
    gap_result = process_eeg(base, base, gap_counter, fs)
    assert gap_result.valid and gap_result.accepted_epochs == 5
    assert gap_result.trial_qc["counter_discontinuities"] == 1
    assert gap_result.rejected_epochs[0]["index"] == 1
    assert "counter_discontinuity" in gap_result.rejected_epochs[0]["reasons"]

    nonfinite = base.copy()
    nonfinite[fs * 9] = np.nan
    nonfinite_result = process_eeg(nonfinite, base, counter, fs)
    assert nonfinite_result.valid
    assert nonfinite_result.channel_qc["right"]["accepted_epochs"] == 5
    assert nonfinite_result.channel_qc["left"]["accepted_epochs"] == 6
    assert "nonfinite_samples" in nonfinite_result.rejected_epochs[0]["reasons"]
