"""
Optimization Service
Room optimization for target emotional response.

Supports both full-feature and legacy 3-dim optimization.

NO STREAMLIT DEPENDENCIES - can be used from any interface.

Usage:
    from src.services import OptimizationService

    service = OptimizationService(model=my_model)
    result = service.optimize_for_target(target_valence=0.8)
    print(result.length, result.width, result.height)
"""
from dataclasses import dataclass, field
from typing import Optional, Tuple, List, Dict, Any
import numpy as np
import logging
from scipy.optimize import differential_evolution

from src.config import get_config, Config
from src.services.prediction_service import PredictionService

logger = logging.getLogger(__name__)


@dataclass
class OptimizationResult:
    """Result of room optimization."""
    length: float
    width: float
    height: float
    predicted_valence: float
    predicted_arousal: float
    target_achieved: float  # How close to target
    samples_evaluated: int
    full_features: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'length': float(self.length),
            'width': float(self.width),
            'height': float(self.height),
            'predicted_valence': float(self.predicted_valence),
            'predicted_arousal': float(self.predicted_arousal),
            'target_achieved': float(self.target_achieved),
            'samples_evaluated': self.samples_evaluated,
            'full_features': self.full_features,
        }


class OptimizationService:
    """
    Room optimization service.

    Uses differential evolution to find room configurations that achieve
    a target emotional response.

    Example:
        service = OptimizationService(model=my_model)
        result = service.optimize_for_target(0.8)  # Target neuro-score
    """

    def __init__(self, model: Any = None, config: Optional[Config] = None,
                 feature_names: Optional[List[str]] = None, scaler: Any = None):
        """
        Initialize optimization service.

        Args:
            model: Trained model
            config: Configuration instance
            feature_names: Ordered feature names for full-feature mode
            scaler: StandardScaler used during training
        """
        self._prediction_service = PredictionService(
            model=model, config=config, feature_names=feature_names, scaler=scaler,
        )
        self._config = config or get_config()
        self._feature_names = feature_names or []
        self._scaler = scaler

    def set_model(self, model: Any) -> None:
        """Set or update the trained model."""
        self._prediction_service.set_model(model)

    def set_feature_config(self, feature_names: List[str], scaler: Any = None) -> None:
        """Update feature names and scaler for full-feature optimization."""
        self._feature_names = feature_names
        self._scaler = scaler
        self._prediction_service.set_feature_config(feature_names, scaler)

    def optimize_for_target(
        self,
        target_score: float,
        n_samples: Optional[int] = None,
        constraints: Optional[dict] = None,
        method: str = 'differential_evolution'
    ) -> OptimizationResult:
        """
        Find room dimensions that achieve target neuro-score.

        Uses differential evolution (default) within dimension constraints.
        """
        if not 0.0 <= target_score <= 1.0:
            raise ValueError(f"target_score must be in [0, 1], got {target_score}")

        if n_samples is None:
            n_samples = self._config.optimization.monte_carlo_samples

        # Get dimension ranges
        room_config = self._config.room
        constraints = constraints or {}

        l_range = constraints.get('length', (room_config.min_length, room_config.max_length))
        w_range = constraints.get('width', (room_config.min_width, room_config.max_width))
        h_range = constraints.get('height', (room_config.min_height, room_config.max_height))

        bounds = [l_range, w_range, h_range]

        target_valence = target_score * 1.99 - 0.99

        def objective(dims: np.ndarray) -> float:
            pred = self._prediction_service.predict(float(dims[0]), float(dims[1]), float(dims[2]))
            return abs(pred.valence - target_valence)

        if method == 'differential_evolution':
            try:
                result = differential_evolution(
                    objective,
                    bounds=bounds,
                    seed=42,
                    maxiter=35,
                    popsize=10,
                    polish=True,
                    tol=1e-6,
                )

                best_dims = result.x
                best_pred = self._prediction_service.predict(
                    float(best_dims[0]),
                    float(best_dims[1]),
                    float(best_dims[2])
                )
                best_diff = abs(best_pred.valence - target_valence)
                evaluated = int(result.nfev)

                return OptimizationResult(
                    length=float(best_dims[0]),
                    width=float(best_dims[1]),
                    height=float(best_dims[2]),
                    predicted_valence=best_pred.valence,
                    predicted_arousal=best_pred.arousal,
                    target_achieved=max(0.0, 1.0 - best_diff),
                    samples_evaluated=evaluated
                )
            except Exception as e:
                logger.warning(f"Differential evolution failed: {e}. Falling back to monte_carlo.")
                method = 'monte_carlo'

        if method != 'monte_carlo':
            raise ValueError(f"Unknown optimization method: {method}")

        l_rand = np.random.uniform(l_range[0], l_range[1], n_samples)
        w_rand = np.random.uniform(w_range[0], w_range[1], n_samples)
        h_rand = np.random.uniform(h_range[0], h_range[1], n_samples)
        candidates = np.stack([l_rand, w_rand, h_rand], axis=1)

        best_idx = None
        best_diff = float('inf')

        for i in range(len(candidates)):
            pred = self._prediction_service.predict(
                float(candidates[i, 0]), float(candidates[i, 1]), float(candidates[i, 2])
            )
            diff = abs(pred.valence - target_valence)
            if diff < best_diff:
                best_diff = diff
                best_idx = i

        if best_idx is None:
            raise ValueError("Optimization failed - no valid candidates")

        best_room = candidates[best_idx]
        best_pred = self._prediction_service.predict(
            float(best_room[0]), float(best_room[1]), float(best_room[2])
        )
        return OptimizationResult(
            length=float(best_room[0]),
            width=float(best_room[1]),
            height=float(best_room[2]),
            predicted_valence=best_pred.valence,
            predicted_arousal=best_pred.arousal,
            target_achieved=max(0.0, 1.0 - best_diff),
            samples_evaluated=n_samples
        )

    def optimize_full(
        self,
        target_score: float,
        fixed_features: Optional[Dict[str, float]] = None,
    ) -> OptimizationResult:
        """
        Full-feature optimization — searches across all spatial parameters.

        Args:
            target_score: Target neuro-score (0.0 to 1.0)
            fixed_features: Features to hold constant during optimization

        Returns:
            OptimizationResult with optimized features
        """
        if not self._feature_names:
            return self.optimize_for_target(target_score)

        spatial_config = self._config.spatial_features
        fixed = fixed_features or {}
        target_valence = target_score * 1.99 - 0.99

        # Build bounds for optimizable features
        opt_features = []
        opt_bounds = []
        for name in self._feature_names:
            if name in fixed:
                continue
            if name.startswith('Day_or_Night_') or name.startswith('Day or Night_'):
                opt_features.append(name)
                opt_bounds.append((0.0, 1.0))
            elif hasattr(spatial_config, name):
                feat = getattr(spatial_config, name)
                if isinstance(feat, dict) and 'min' in feat and 'max' in feat:
                    opt_features.append(name)
                    opt_bounds.append((feat['min'], feat['max']))
            else:
                opt_features.append(name)
                opt_bounds.append((0.0, 1.0))

        def objective(values: np.ndarray) -> float:
            features = dict(fixed)
            for i, fname in enumerate(opt_features):
                features[fname] = float(values[i])
            pred = self._prediction_service.predict_full(features)
            return abs(pred.valence - target_valence)

        try:
            result = differential_evolution(
                objective,
                bounds=opt_bounds,
                seed=42,
                maxiter=50,
                popsize=15,
                polish=True,
                tol=1e-6,
            )

            best_values = result.x
            best_features = dict(fixed)
            for i, fname in enumerate(opt_features):
                best_features[fname] = float(best_values[i])

            best_pred = self._prediction_service.predict_full(best_features)

            return OptimizationResult(
                length=best_features.get('Length_m', 10.0),
                width=best_features.get('Width_m', 8.0),
                height=best_features.get('Height_m', 3.5),
                predicted_valence=best_pred.valence,
                predicted_arousal=best_pred.arousal,
                target_achieved=max(0.0, 1.0 - abs(best_pred.valence - target_valence)),
                samples_evaluated=int(result.nfev),
                full_features=best_features,
            )
        except Exception as e:
            logger.warning(f"Full-feature optimization failed: {e}. Falling back to 3-dim optimization.")
            return self.optimize_for_target(target_score)

    def optimize_for_valence_arousal(
        self,
        target_valence: float,
        target_arousal: float,
        n_samples: Optional[int] = None,
        constraints: Optional[dict] = None
    ) -> OptimizationResult:
        """
        Find room dimensions that achieve target valence and arousal.
        """
        if n_samples is None:
            n_samples = self._config.optimization.monte_carlo_samples

        room_config = self._config.room
        constraints = constraints or {}

        l_range = constraints.get('length', (room_config.min_length, room_config.max_length))
        w_range = constraints.get('width', (room_config.min_width, room_config.max_width))
        h_range = constraints.get('height', (room_config.min_height, room_config.max_height))

        l_rand = np.random.uniform(l_range[0], l_range[1], n_samples)
        w_rand = np.random.uniform(w_range[0], w_range[1], n_samples)
        h_rand = np.random.uniform(h_range[0], h_range[1], n_samples)

        best_idx = None
        best_dist = float('inf')

        for i in range(n_samples):
            pred = self._prediction_service.predict(
                float(l_rand[i]), float(w_rand[i]), float(h_rand[i])
            )
            dist = np.sqrt(
                (pred.valence - target_valence)**2 +
                (pred.arousal - target_arousal)**2
            )
            if dist < best_dist:
                best_dist = dist
                best_idx = i

        if best_idx is None:
            raise ValueError("Optimization failed - no valid candidates")

        best_pred = self._prediction_service.predict(
            float(l_rand[best_idx]), float(w_rand[best_idx]), float(h_rand[best_idx])
        )

        return OptimizationResult(
            length=float(l_rand[best_idx]),
            width=float(w_rand[best_idx]),
            height=float(h_rand[best_idx]),
            predicted_valence=best_pred.valence,
            predicted_arousal=best_pred.arousal,
            target_achieved=1.0 - best_dist / 2.0,
            samples_evaluated=n_samples
        )

    def gradient_optimize(
        self,
        target_score: float,
        initial_dims: Tuple[float, float, float],
        learning_rate: float = 0.1,
        max_iterations: int = 100,
        tolerance: float = 0.01
    ) -> OptimizationResult:
        """
        Gradient-based optimization for PyTorch models.
        Only works with PyTorch models that support backpropagation.
        """
        import torch
        from src.models.adapters import PyTorchAdapter

        model_adapter = self._prediction_service._model
        if model_adapter is None:
            raise ValueError("Model not set")

        if isinstance(model_adapter, PyTorchAdapter):
            model = model_adapter.get_torch_model()
        elif hasattr(model_adapter, 'parameters'):
            model = model_adapter
        else:
            logger.warning("gradient_optimize is deprecated for non-PyTorch models. Using fallback or rejecting.")
            raise ValueError("gradient_optimize requires a PyTorchAdapter.")

        target_valence = target_score * 1.99 - 0.99

        dims = torch.tensor([initial_dims], dtype=torch.float32, requires_grad=True)
        optimizer = torch.optim.Adam([dims], lr=learning_rate)

        for iteration in range(max_iterations):
            optimizer.zero_grad()

            output = model(dims)
            if isinstance(output, dict):
                pred_valence = output['affective_space'][0, 0]
            else:
                pred_valence = output[0, 0]

            loss = (pred_valence - target_valence) ** 2
            loss.backward()
            optimizer.step()

            with torch.no_grad():
                room_config = self._config.room
                dims.data[0, 0].clamp_(room_config.min_length, room_config.max_length)
                dims.data[0, 1].clamp_(room_config.min_width, room_config.max_width)
                dims.data[0, 2].clamp_(room_config.min_height, room_config.max_height)

            if loss.item() < tolerance:
                break

        with torch.no_grad():
            final_output = model(dims)
            if isinstance(final_output, dict):
                final_va = final_output['affective_space'].numpy()[0]
            else:
                final_va = final_output.numpy()[0]

        return OptimizationResult(
            length=float(dims[0, 0].item()),
            width=float(dims[0, 1].item()),
            height=float(dims[0, 2].item()),
            predicted_valence=float(final_va[0]),
            predicted_arousal=float(final_va[1]),
            target_achieved=1.0 - np.sqrt((final_va[0] - target_valence)**2),
            samples_evaluated=iteration + 1
        )