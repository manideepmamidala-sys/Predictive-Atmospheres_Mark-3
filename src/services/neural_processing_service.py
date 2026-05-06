"""
Neural Processing Service
Core EEG/ECG signal processing without UI dependencies.

This service wraps the preprocessing and emotion engine logic,
making it accessible from any interface (Streamlit, Rhino, CLI, API).

Usage:
    from src.services import NeuralProcessingService

    service = NeuralProcessingService()
    result = service.process_eeg(eeg_signal, fs=256)
    print(result.valence, result.arousal)
"""
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Tuple, Any
import numpy as np

from src.config import get_config, Config
from src.data.preprocessing import (
    preprocess_eeg_signal,
    analyze_eeg_bands,
    analyze_ecg,
    butter_bandpass_filter
)
from src.data.emotion_engine import process_emotion_engine


@dataclass
class EEGProcessingResult:
    """Result of EEG signal processing."""
    valence: float
    arousal: float
    band_powers: Dict[str, float]
    emotion_distribution: Dict[str, float]
    trajectory: Dict[str, List[float]]  # V/A over time

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'valence': float(self.valence),
            'arousal': float(self.arousal),
            'band_powers': self.band_powers,
            'emotion_distribution': self.emotion_distribution,
            'trajectory': self.trajectory
        }


@dataclass
class ECGProcessingResult:
    """Result of ECG signal processing."""
    bpm: float
    hrv: float
    peak_count: int
    quality: str  # 'good', 'moderate', 'poor'

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'bpm': float(self.bpm),
            'hrv': float(self.hrv),
            'peak_count': self.peak_count,
            'quality': self.quality
        }


@dataclass
class MultiModalResult:
    """Combined EEG + ECG processing result."""
    eeg: EEGProcessingResult
    ecg: Optional[ECGProcessingResult] = None
    combined_valence: float = 0.0
    combined_arousal: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'eeg': self.eeg.to_dict(),
            'ecg': self.ecg.to_dict() if self.ecg else None,
            'combined_valence': float(self.combined_valence),
            'combined_arousal': float(self.combined_arousal)
        }


class NeuralProcessingService:
    """
    Core neural signal processing service.

    Handles EEG preprocessing, emotion analysis, and ECG metrics
    without any UI dependencies.

    Example:
        service = NeuralProcessingService()
        result = service.process_eeg(eeg_array, fs=256)
    """

    def __init__(self, config: Optional[Config] = None):
        """
        Initialize neural processing service.

        Args:
            config: Configuration instance
        """
        self._config = config or get_config()

    def process_emotion_signals(
        self,
        signal_right: np.ndarray,
        signal_left: np.ndarray,
        signal_ecg: np.ndarray,
        fs: Optional[int] = None
    ) -> EEGProcessingResult:
        """
        Process dual EEG channels and ECG for emotion mapping.

        Args:
            signal_right: 1D numpy array of Right EEG samples
            signal_left: 1D numpy array of Left EEG samples
            signal_ecg: 1D numpy array of ECG samples
            fs: Sampling frequency (default from config)

        Returns:
            EEGProcessingResult with valence, arousal, and band powers
        """
        if fs is None:
            fs = self._config.eeg.sample_rate

        # Run emotion engine
        result = process_emotion_engine(signal_right, signal_left, signal_ecg, fs=fs)

        # Extract final valence/arousal from trajectory
        trajectory = result['MDS']
        valence = np.mean(trajectory['Valence_X']) if trajectory['Valence_X'] else 0.0
        arousal = np.mean(trajectory['Arousal_Y']) if trajectory['Arousal_Y'] else 0.0

        # Flatten band powers and emotion distribution
        band_powers = {k: v[0] if isinstance(v, list) else v
                       for k, v in result['Bands'].items()}
        emotion_dist = {k: v[0] if isinstance(v, list) else v
                        for k, v in result['Emotion_Distribution'].items()}

        return EEGProcessingResult(
            valence=float(valence),
            arousal=float(arousal),
            band_powers=band_powers,
            emotion_distribution=emotion_dist,
            trajectory=trajectory
        )

    def process_eeg_multichannel(
        self,
        signals: np.ndarray,
        signal_ecg: np.ndarray,
        fs: Optional[int] = None
    ) -> EEGProcessingResult:
        """
        Process multiple EEG channels and ECG for emotion mapping.
        Assumes signals[0] is Right Frontal, signals[1] is Left Frontal.

        Args:
            signals: 2D array (channels x time) or (time x channels)
            signal_ecg: 1D ECG array
            fs: Sampling frequency

        Returns:
            EEGProcessingResult
        """
        if fs is None:
            fs = self._config.eeg.sample_rate

        # Handle shape
        if signals.shape[0] > signals.shape[1]:
            # Assume (time, channels)
            signals = signals.T

        if signals.shape[0] < 2:
            raise ValueError("process_eeg_multichannel requires at least 2 channels (Right, Left)")

        return self.process_emotion_signals(signals[0], signals[1], signal_ecg, fs=fs)

    def process_ecg(
        self,
        signal_data: np.ndarray,
        fs: Optional[int] = None
    ) -> ECGProcessingResult:
        """
        Process ECG signal for heart rate and HRV.

        Args:
            signal_data: 1D numpy array of ECG samples
            fs: Sampling frequency

        Returns:
            ECGProcessingResult with BPM, HRV, and quality
        """
        if fs is None:
            fs = self._config.eeg.sample_rate

        metrics, peaks, _ = analyze_ecg(signal_data, fs=fs)

        # Determine quality
        peak_count = len(peaks)
        if peak_count >= 5:
            quality = 'good'
        elif peak_count >= 2:
            quality = 'moderate'
        else:
            quality = 'poor'

        return ECGProcessingResult(
            bpm=float(metrics['BPM']),
            hrv=float(metrics['HRV']),
            peak_count=peak_count,
            quality=quality
        )

    def process_multimodal(
        self,
        eeg_channels: np.ndarray,
        ecg_channel: Optional[np.ndarray] = None,
        fs: Optional[int] = None
    ) -> MultiModalResult:
        """
        Process EEG and optional ECG together.

        Combines results for a comprehensive physiological assessment.

        Args:
            eeg_channels: 2D array of EEG signals
            ecg_channel: Optional 1D ECG array
            fs: Sampling frequency

        Returns:
            MultiModalResult with combined analysis
        """
        if fs is None:
            fs = self._config.eeg.sample_rate

        if ecg_channel is None:
            raise ValueError("process_multimodal requires ecg_channel to calculate arousal")

        # Process emotion signals
        eeg_result = self.process_eeg_multichannel(eeg_channels, ecg_channel, fs=fs)

        avg_valence = eeg_result.valence
        avg_arousal = eeg_result.arousal

        # Get ECG specifics (bpm, hrv)
        ecg_result_obj = self.process_ecg(ecg_channel, fs=fs)

        return MultiModalResult(
            eeg=eeg_result,
            ecg=ecg_result_obj,
            combined_valence=float(avg_valence),
            combined_arousal=float(avg_arousal)
        )

    def prepare_for_model(
        self,
        eeg_data: np.ndarray,
        target_length: Optional[int] = None,
        fs: Optional[int] = None
    ) -> np.ndarray:
        """
        Prepare EEG data for model input.

        Applies preprocessing and formats for model consumption.

        Args:
            eeg_data: 2D array (channels x time) or (time x channels)
            target_length: Target sequence length
            fs: Sampling frequency

        Returns:
            Processed array ready for model input
        """
        if fs is None:
            fs = self._config.eeg.sample_rate
        if target_length is None:
            target_length = self._config.eeg.target_length

        # Handle shape - ensure (channels, time)
        if eeg_data.shape[0] > eeg_data.shape[1]:
            eeg_data = eeg_data.T

        n_channels, n_samples = eeg_data.shape

        # Preprocess each channel
        processed = []
        for ch in range(n_channels):
            clean = preprocess_eeg_signal(eeg_data[ch], fs=fs)
            processed.append(clean)

        processed = np.array(processed)

        # Pad or truncate to target length
        if n_samples > target_length:
            processed = processed[:, :target_length]
        elif n_samples < target_length:
            padding = np.zeros((n_channels, target_length - n_samples))
            processed = np.concatenate([processed, padding], axis=1)

        return processed