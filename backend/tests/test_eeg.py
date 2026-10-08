import numpy as np
import pytest

from pa.signals.eeg import process_eeg


def test_known_alpha_asymmetry_and_beta_power():
    fs = 500
    t = np.arange(fs * 20) / fs
    right = 2 * np.sin(2 * np.pi * 10 * t) + 0.5 * np.sin(2 * np.pi * 20 * t)
    left = np.sin(2 * np.pi * 10 * t) + 0.5 * np.sin(2 * np.pi * 20 * t)
    result = process_eeg(right, left, np.arange(len(t)) % 256, fs)
    assert result.valid and result.accepted_epochs == 5
    assert result.forehead_log_alpha_asymmetry == pytest.approx(np.log(4), abs=0.12)
    assert result.beta_right > 0 and result.beta_left > 0


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
