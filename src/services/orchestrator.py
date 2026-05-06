"""
Neuro Architecture Orchestrator
End-to-end coordination across neural processing, prediction, and optimization.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np

from src.services.container import ServiceContainer
from src.services.neural_processing_service import EEGProcessingResult
from src.services.optimization_service import OptimizationResult
from src.services.prediction_service import PredictionResult


@dataclass
class OrchestrationResult:
    eeg: EEGProcessingResult
    optimized_room: OptimizationResult
    optimized_prediction: PredictionResult


class NeuroArchitectureOrchestrator:
    """High-level workflow for EEG-informed room optimization."""

    def __init__(self, services: ServiceContainer):
        self.services = services

    def analyze_and_optimize(
        self,
        eeg_signal: np.ndarray,
        fs: int = 256,
        target_score: Optional[float] = None,
    ) -> OrchestrationResult:
        if eeg_signal.ndim == 1:
            signal_right = eeg_signal
            signal_left = eeg_signal
            signal_ecg = eeg_signal
        else:
            if eeg_signal.shape[0] > eeg_signal.shape[1]:
                eeg_signal = eeg_signal.T
            signal_right = eeg_signal[0]
            signal_left = eeg_signal[1] if eeg_signal.shape[0] > 1 else eeg_signal[0]
            signal_ecg = eeg_signal[2] if eeg_signal.shape[0] > 2 else eeg_signal[0]

        eeg_result = self.services.neural_processing_service.process_emotion_signals(signal_right, signal_left, signal_ecg, fs=fs)

        effective_target = target_score
        if effective_target is None:
            effective_target = float((eeg_result.valence + 1.0) / 2.0)

        optimization_result = self.services.optimization_service.optimize_for_target(
            target_score=effective_target,
            method='differential_evolution'
        )

        prediction_result = self.services.prediction_service.predict(
            optimization_result.length,
            optimization_result.width,
            optimization_result.height,
        )

        return OrchestrationResult(
            eeg=eeg_result,
            optimized_room=optimization_result,
            optimized_prediction=prediction_result,
        )
