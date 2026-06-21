from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from src.services.container import ServiceContainer
from src.services.optimization_service import OptimizationResult
from src.services.prediction_service import PredictionResult


@dataclass
class OrchestrationResult:
    optimized_room: OptimizationResult
    optimized_prediction: PredictionResult


class NeuroArchitectureOrchestrator:
    """Compatibility orchestrator for the existing service-oriented architecture."""

    def __init__(self, services: ServiceContainer):
        self._services = services

    def analyze_and_optimize(
        self,
        eeg_signal: np.ndarray,
        fs: int = 256,
        target_score: float = 0.6,
    ) -> OrchestrationResult:
        """Run end-to-end optimization while preserving legacy method signature."""
        if eeg_signal.size == 0:
            raise ValueError("eeg_signal must not be empty.")
        if fs <= 0:
            raise ValueError("fs must be a positive integer.")
        signal_array = np.asarray(eeg_signal, dtype=np.float64)
        if signal_array.ndim != 2:
            raise ValueError("eeg_signal must be a 2D array of channels x samples.")
        if signal_array.shape[0] > signal_array.shape[1]:
            signal_array = signal_array.T
        if signal_array.shape[0] < 3:
            raise ValueError("eeg_signal must include at least 3 channels (2 EEG + 1 ECG).")

        # Preserve legacy behavior by processing incoming neuro-signals before optimization.
        self._services.neural_processing_service.process_multimodal(
            eeg_channels=signal_array[:2],
            ecg_channel=signal_array[2],
            fs=fs,
        )
        monte_carlo_samples = getattr(
            getattr(self._services.config, "optimization", object()),
            "monte_carlo_samples",
            2000,
        )
        if not isinstance(monte_carlo_samples, int) or monte_carlo_samples < 10:
            raise ValueError("services.config.optimization.monte_carlo_samples must be an int >= 10.")

        optimized_room = self._services.optimization_service.optimize_for_target(
            target_score=target_score,
            n_samples=monte_carlo_samples,
        )
        optimized_prediction = self._services.prediction_service.predict(
            optimized_room.length,
            optimized_room.width,
            optimized_room.height,
        )
        return OrchestrationResult(
            optimized_room=optimized_room,
            optimized_prediction=optimized_prediction,
        )
