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
        if eeg_signal.size == 0:
            raise ValueError("eeg_signal must not be empty.")
        _ = fs  # preserved for legacy signature compatibility

        optimized_room = self._services.optimization_service.optimize_for_target(
            target_score=target_score,
            n_samples=self._services.config.optimization.monte_carlo_samples,
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
