"""
Prediction Service
Core prediction logic for room features -> emotional response.

Supports both:
  - Full-feature mode (20+ spatial features via predict_full)
  - Legacy 3-dim mode (length, width, height via predict)

NO STREAMLIT DEPENDENCIES - can be used from any interface.

Usage:
    from src.services import PredictionService

    service = PredictionService()
    result = service.predict(length=10.0, width=8.0, height=3.5)
    # or
    result = service.predict_full({'Length (meter)': 10.0, 'Width (meter)': 8.0, ...})
"""
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any, Tuple
import numpy as np

from src.config import get_config, Config


@dataclass
class PredictionResult:
    """Result of a spatial prediction."""
    valence: float
    arousal: float
    neuro_score: float = 0.0
    atmosphere: str = "Neutral"
    emotion_weights: Dict[str, float] = field(default_factory=dict)
    categories: Optional[np.ndarray] = None  # For CognitiveMapMLP

    def __post_init__(self):
        """Compute derived fields."""
        self.neuro_score = (self.valence + 1.0) / 2.0
        self._compute_atmosphere()

    def _compute_atmosphere(self) -> None:
        """Determine atmosphere classification from valence."""
        config = get_config()
        if self.valence > config.emotion.positive_threshold:
            self.atmosphere = "POSITIVE / WELCOMING"
        elif self.valence > config.emotion.negative_threshold:
            self.atmosphere = "NEUTRAL"
        else:
            self.atmosphere = "NEGATIVE / STRESSFUL"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'valence': float(self.valence),
            'arousal': float(self.arousal),
            'neuro_score': float(self.neuro_score),
            'atmosphere': self.atmosphere,
            'emotion_weights': self.emotion_weights
        }


class PredictionService:
    """
    Core prediction service for spatial-emotional mapping.

    This service is completely decoupled from any UI framework.
    It can be used from Streamlit, Rhino, or any other interface.

    Example:
        service = PredictionService(model=my_trained_model)
        result = service.predict(10.0, 8.0, 3.5)
    """

    def __init__(
        self,
        model: Any = None,
        config: Optional[Config] = None,
        feature_names: Optional[List[str]] = None,
        scaler: Any = None,
    ):
        """
        Initialize prediction service.

        Args:
            model: Trained model (PyTorch or scikit-learn)
            config: Configuration instance
            feature_names: Ordered feature names the model was trained on
            scaler: StandardScaler used during training
        """
        self._model = None
        self._config = config or get_config()
        self._emotion_centroids = self._config.emotion.centroids
        self._feature_names = feature_names or []
        self._scaler = scaler
        
        if model is not None:
            self.set_model(model)

    def set_model(self, model: Any) -> None:
        """Set or update the trained model, automatically wrapping it in an adapter if needed."""
        if model is not None and not hasattr(model, 'predict'):
            model_type = type(model).__module__ if hasattr(type(model), '__module__') else ""
            from src.models.adapters import PyTorchAdapter, SKLearnAdapter
            if 'torch' in model_type or 'src.models' in model_type:
                model = PyTorchAdapter(model)
            elif 'sklearn' in model_type:
                model = SKLearnAdapter(model)
            else:
                try:
                    model = PyTorchAdapter(model)
                except Exception as e:
                    raise ValueError(f"Unknown model type {model_type} that cannot be auto-wrapped. Error: {e}")
        self._model = model

    def set_feature_config(
        self,
        feature_names: List[str],
        scaler: Any = None,
    ) -> None:
        """Update the feature order and scaler for full-feature predictions."""
        self._feature_names = feature_names
        self._scaler = scaler

    def predict(self, length: float, width: float, height: float) -> PredictionResult:
        """
        Predict emotional response from room dimensions (legacy 3-dim mode).

        When feature_names has extended features, this builds a full vector
        with defaults for missing features.

        Args:
            length: Room length in meters
            width: Room width in meters
            height: Room height in meters

        Returns:
            PredictionResult with valence, arousal, and derived metrics
        """
        if self._model is None:
            raise ValueError("Model not set. Call set_model() first.")

        if self._feature_names and len(self._feature_names) > 3:
            # Build a full feature vector with defaults
            features_dict = self._build_features_from_geometry(length, width, height)
            return self.predict_full(features_dict)

        # Legacy 3-feature path
        input_data = np.array([[length, width, height]], dtype=np.float32)
        if self._scaler is not None:
            input_data = self._scaler.transform(input_data)

        valence, arousal = self._run_model_prediction(input_data)
        emotion_weights = self._compute_emotion_weights(valence, arousal)

        return PredictionResult(
            valence=float(valence),
            arousal=float(arousal),
            emotion_weights=emotion_weights
        )

    def predict_full(self, features_dict: Dict[str, float]) -> PredictionResult:
        """
        Predict emotional response from a full feature vector.

        Args:
            features_dict: Dictionary of feature_name -> value

        Returns:
            PredictionResult with valence, arousal, and derived metrics
        """
        if self._model is None:
            raise ValueError("Model not set. Call set_model() first.")

        if not self._feature_names:
            raise ValueError("Feature names not set. Call set_feature_config() first.")

        # Build ordered input vector
        input_values = []
        for name in self._feature_names:
            if name in features_dict:
                input_values.append(float(features_dict[name]))
            else:
                # Use 0.0 as fallback (scaler will handle centering)
                input_values.append(0.0)

        input_data = np.array([input_values], dtype=np.float32)
        if self._scaler is not None:
            input_data = self._scaler.transform(input_data)

        valence, arousal = self._run_model_prediction(input_data)
        emotion_weights = self._compute_emotion_weights(valence, arousal)

        return PredictionResult(
            valence=float(valence),
            arousal=float(arousal),
            emotion_weights=emotion_weights
        )

    def _build_features_from_geometry(
        self, length: float, width: float, height: float
    ) -> Dict[str, float]:
        """Compute a full feature dict from basic geometry using defaults for unknowns.

        Computes all independent features. Derived features are removed.
        """
        config = self._config.spatial_features

        features: Dict[str, float] = {}

        # Set defaults for all independent features directly from flattened config
        for name in config.get_independent_feature_names():
            feat_def = getattr(config, name)
            features[name] = feat_def['default']

        # Override core geometry with actual values
        features['Length_m'] = length
        features['Width_m'] = width
        features['Height_m'] = height

        # Handle categorical one-hot features
        for name in self._feature_names:
            if name.startswith('Day_or_Night_'):
                features[name] = 1.0 if name == 'Day_or_Night_Day' else 0.0
            elif name.startswith('Type_of_Space_'):
                features[name] = 1.0 if name == 'Type_of_Space_Living Room' else 0.0

        return features

    def predict_batch(self, dimensions: np.ndarray) -> List[PredictionResult]:
        """
        Predict emotional responses for multiple rooms.

        Args:
            dimensions: Array of shape (N, D) with features

        Returns:
            List of PredictionResult objects
        """
        if self._model is None:
            raise ValueError("Model not set. Call set_model() first.")

        if self._scaler is not None:
            dimensions = self._scaler.transform(dimensions)

        predictions = self._run_model_prediction(dimensions, batch=True)
        results = []

        for i in range(len(predictions)):
            valence, arousal = predictions[i]
            emotion_weights = self._compute_emotion_weights(valence, arousal)
            results.append(PredictionResult(
                valence=float(valence),
                arousal=float(arousal),
                emotion_weights=emotion_weights
            ))

        return results

    def _run_model_prediction(self, input_data: np.ndarray, batch: bool = False) -> Tuple:
        """
        Run model prediction, delegating to the BaseModelAdapter.
        """
        if self._model is None:
            raise ValueError("Model is not set.")
        return self._model.predict(input_data, batch=batch)

    def _compute_emotion_weights(self, valence: float, arousal: float) -> Dict[str, float]:
        """
        Compute emotion weights based on distance to centroids.
        Uses exponential decay based on distance in V-A space.
        """
        weights = {}
        decay = self._config.emotion.distance_decay

        for emotion, coords in self._emotion_centroids.items():
            dist = np.sqrt((valence - coords[0])**2 + (arousal - coords[1])**2)
            weights[emotion] = np.exp(-dist * decay)

        # Normalize to sum to 1
        total = sum(weights.values())
        if total > 0:
            weights = {k: v / total for k, v in weights.items()}

        return weights

    def get_reference_centroids(self) -> Dict[str, List[float]]:
        """Get the emotion reference centroids."""
        return self._emotion_centroids.copy()