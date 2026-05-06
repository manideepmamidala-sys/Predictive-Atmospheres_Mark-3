"""
Service Container
Centralized dependency injection for model-backed services.
"""
from __future__ import annotations

from typing import Optional, Any, List

from src.config import Config, get_config
from src.models.architectures import SpatialMLP
from src.services.prediction_service import PredictionService
from src.services.optimization_service import OptimizationService
from src.services.neural_processing_service import NeuralProcessingService
from src.services.space_capability_service import SpaceCapabilityService


class ServiceContainer:
    """Lazily-instantiated service container for app/runtime integrations."""

    def __init__(self, config: Optional[Config] = None, model: Optional[Any] = None):
        self.config = config or get_config()
        self._model: Optional[Any] = model
        self._feature_names: List[str] = []
        self._scaler: Optional[Any] = None
        self._prediction_service: Optional[PredictionService] = None
        self._optimization_service: Optional[OptimizationService] = None
        self._neural_processing_service: Optional[NeuralProcessingService] = None
        self._space_capability_service: Optional[SpaceCapabilityService] = None

    @property
    def model(self) -> Any:
        """Get or create the active spatial model."""
        if self._model is None:
            self._model = SpatialMLP()
        return self._model

    def set_model(self, model: Any) -> None:
        """Update active model and refresh dependent services."""
        self._model = model
        if self._prediction_service is not None:
            self._prediction_service.set_model(model)
        if self._optimization_service is not None:
            self._optimization_service.set_model(model)

    def set_feature_config(self, feature_names: List[str], scaler: Any = None) -> None:
        """Update feature config across all applicable services."""
        self._feature_names = feature_names
        self._scaler = scaler
        if self._prediction_service is not None:
            self._prediction_service.set_feature_config(feature_names, scaler)
        if self._optimization_service is not None:
            self._optimization_service.set_feature_config(feature_names, scaler)

    @property
    def prediction_service(self) -> PredictionService:
        if self._prediction_service is None:
            self._prediction_service = PredictionService(
                model=self.model, config=self.config,
                feature_names=self._feature_names, scaler=self._scaler
            )
        return self._prediction_service

    @property
    def optimization_service(self) -> OptimizationService:
        if self._optimization_service is None:
            self._optimization_service = OptimizationService(
                model=self.model, config=self.config,
                feature_names=self._feature_names, scaler=self._scaler
            )
        return self._optimization_service

    @property
    def neural_processing_service(self) -> NeuralProcessingService:
        if self._neural_processing_service is None:
            self._neural_processing_service = NeuralProcessingService(config=self.config)
        return self._neural_processing_service

    @property
    def space_capability_service(self) -> SpaceCapabilityService:
        if self._space_capability_service is None:
            self._space_capability_service = SpaceCapabilityService()
        return self._space_capability_service

    def reset(self) -> None:
        """Reset model and service instances."""
        self._model = None
        self._feature_names = []
        self._scaler = None
        self._prediction_service = None
        self._optimization_service = None
        self._neural_processing_service = None
        self._space_capability_service = None
