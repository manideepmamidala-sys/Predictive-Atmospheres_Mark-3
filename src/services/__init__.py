"""
Services Module
Core business logic layer - NO UI dependencies.

This module contains all processing services that can be used by:
- Streamlit UI (src/ui/)
- Rhino Plugin (src/rhino/)
- API endpoints (future)
- CLI tools (future)

Usage:
    from src.services import PredictionService, OptimizationService
    from src.services import NeuralProcessingService
"""
from src.services.prediction_service import PredictionService
from src.services.optimization_service import OptimizationService
from src.services.neural_processing_service import NeuralProcessingService
from src.services.container import ServiceContainer

__all__ = [
    'PredictionService',
    'OptimizationService',
    'NeuralProcessingService',
    'ServiceContainer'
]