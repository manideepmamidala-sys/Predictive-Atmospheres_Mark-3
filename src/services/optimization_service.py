"""
Optimization Service
Room optimization for target emotional response.

Supports Vectorized Monte Carlo Search for target Neuro-Score.

NO STREAMLIT DEPENDENCIES - can be used from any interface.
"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
import numpy as np
import pandas as pd
import logging
import random

from src.config import get_config, Config
from src.services.prediction_service import PredictionService, calculate_neuro_score

logger = logging.getLogger(__name__)


@dataclass
class OptimizationResult:
    """Result of room optimization."""
    length: float
    width: float
    height: float
    predicted_valence: float
    predicted_arousal: float
    neuro_score: float
    target_achieved: float  # How close to target
    samples_evaluated: int
    full_features: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            'length': float(self.length),
            'width': float(self.width),
            'height': float(self.height),
            'predicted_valence': float(self.predicted_valence),
            'predicted_arousal': float(self.predicted_arousal),
            'neuro_score': float(self.neuro_score),
            'target_achieved': float(self.target_achieved),
            'samples_evaluated': self.samples_evaluated,
            'full_features': self.full_features,
        }


class OptimizationService:
    """
    Room optimization service.
    Uses Vectorized Monte Carlo Search to find room configurations that achieve
    a target Neuro-Score.
    """

    def __init__(self, model: Any = None, config: Optional[Config] = None,
                 feature_names: Optional[List[str]] = None, scaler: Any = None):
        self._prediction_service = PredictionService(
            model=model, config=config, feature_names=feature_names, scaler=scaler,
        )
        self._config = config or get_config()
        self._feature_names = feature_names or []
        self._scaler = scaler
        
        # Step A: Define the strict min and max realistic bounds for all 25 spatial features
        self._default_bounds = {
            'Length_m': (2.0, 20.0),
            'Width_m': (2.0, 20.0),
            'Height_m': (3.0, 5.0),
            'Num_Doors': (0.0, 5.0),
            'Door_Area_m2': (0.0, 10.0),
            'Num_Windows': (0.0, 10.0),
            'Window_Area_m2': (0.0, 50.0),
            'Daylight_Factor_pct': (0.0, 10.0),
            'Illuminance_lux': (50.0, 1000.0),
            'CCT_K': (2700.0, 6500.0),
            'Walkable_Floor_Area_m2': (10.0, 500.0),
            'Day_or_Night_Day': (0.0, 1.0),
            'Day_or_Night_Night': (0.0, 1.0),
            'Type_of_Space_Bedroom': (0.0, 1.0),
            'Type_of_Space_Living Room': (0.0, 1.0),
            'Type_of_Space_Workplace': (0.0, 1.0),
            'Type_of_Space_Classroom': (0.0, 1.0),
            'Type_of_Space_Cafeteria': (0.0, 1.0),
            'Length_to_Width_Ratio': (0.1, 10.0),
            'Floor_Area_m2': (4.0, 400.0),
            'Wall_Area_m2': (10.0, 1000.0),
            'Volume_m3': (8.0, 2000.0),
            'Door_to_Wall_Ratio': (0.01, 0.5),
            'Window_to_Wall_Ratio': (0.0, 0.9),
            'Walkable_to_Floor_Ratio': (0.1, 1.0)
        }

    def set_model(self, model: Any) -> None:
        self._prediction_service.set_model(model)

    def set_feature_config(self, feature_names: List[str], scaler: Any = None) -> None:
        self._feature_names = feature_names
        self._scaler = scaler
        self._prediction_service.set_feature_config(feature_names, scaler)

    def optimize_for_target(
        self,
        target_score: float,
        n_samples: int = 5000,
        fixed_features: Optional[Dict[str, float]] = None,
    ) -> OptimizationResult:
        """
        Vectorized Monte Carlo Search for target Neuro-Score.
        """
        if not 0.0 <= target_score <= 1.0:
            raise ValueError(f"target_score must be in [0, 1], got {target_score}")
            
        fixed = fixed_features or {}
        feature_names = self._feature_names
        if not feature_names:
            # Fallback to legacy 3-feature if needed, but the prompt implies full features are used.
            feature_names = ['Length_m', 'Width_m', 'Height_m']
            
        spatial_config = self._config.spatial_features
        bounds_list = []
        for name in feature_names:
            if hasattr(spatial_config, name):
                feat = getattr(spatial_config, name)
                if isinstance(feat, dict) and 'min' in feat and 'max' in feat:
                    bounds_list.append((feat['min'], feat['max']))
                else:
                    bounds_list.append(self._default_bounds.get(name, (0.0, 1.0)))
            else:
                bounds_list.append(self._default_bounds.get(name, (0.0, 1.0)))
                
        # Step B: Generate a massive random sample
        samples_matrix = np.zeros((n_samples, len(feature_names)), dtype=np.float32)
        for i, name in enumerate(feature_names):
            if name in fixed:
                samples_matrix[:, i] = fixed[name]
            else:
                min_val, max_val = bounds_list[i]
                
                if name.startswith('Num_'):
                    # Discrete / Integer features
                    samples_matrix[:, i] = np.random.randint(int(min_val), int(max_val) + 1, size=n_samples)
                elif name.startswith('Day_or_Night_') or name.startswith('Type_of_Space_'):
                    # Binary / Categorical features
                    samples_matrix[:, i] = np.random.choice([0.0, 1.0], size=n_samples)
                else:
                    # Continuous features
                    if name == 'Height_m':
                        samples_matrix[:, i] = np.round(np.random.uniform(3.0, max_val, n_samples), 2)
                    else:
                        samples_matrix[:, i] = np.round(np.random.uniform(min_val, max_val, n_samples), 2)                
        batch_df = pd.DataFrame(samples_matrix, columns=feature_names)
        
        # Step C: Run batch inference
        if self._scaler is not None:
            scaled_batch_array = self._scaler.transform(batch_df.values)
        else:
            scaled_batch_array = batch_df.to_numpy()
            
        # Bypass UI formatting and predict directly using the raw model
        # Scikit-Learn multi-output regression returns a NumPy array of shape (N_samples, 2)
        model_adapter = self._prediction_service._model
        if hasattr(model_adapter, 'model'):
            raw_model = model_adapter.model
        else:
            raw_model = model_adapter
            
        try:
            if hasattr(raw_model, 'predict'):
                raw_batch_predictions = raw_model.predict(scaled_batch_array)
            else:
                # Fallback for PyTorch models that don't have .predict()
                import torch
                with torch.no_grad():
                    t_samples = torch.tensor(scaled_batch_array, dtype=torch.float32)
                    out = raw_model(t_samples)
                    if isinstance(out, dict):
                        out = out['affective_space']
                    raw_batch_predictions = out.cpu().numpy()
        except ValueError as ve:
            # If the raw model itself raises unpacking error, it might be due to a weird pipeline step.
            # We catch and re-raise with more context.
            raise ValueError(f"Model prediction failed: {ve}") from ve

        # Slice the columns explicitly: Column 0 is Valence, Column 1 is Arousal
        valences = raw_batch_predictions[:, 0]
        arousals = raw_batch_predictions[:, 1]
            
        # Step D: Batch Score
        batch_neuro_scores = calculate_neuro_score(valences, arousals)
        
        # Step E: Calculate Error
        errors = np.abs(batch_neuro_scores - target_score)
        
        # Step F: Diversity Selection
        top_indices = np.argsort(errors)[:50]
        chosen_idx = random.choice(top_indices)
        
        # Step G: Return the feature vector
        chosen_vector = samples_matrix[chosen_idx]
        chosen_valence = float(valences[chosen_idx])
        chosen_arousal = float(arousals[chosen_idx])
        chosen_ns = float(batch_neuro_scores[chosen_idx])
        
        full_features = {name: float(chosen_vector[i]) for i, name in enumerate(feature_names)}
        
        # Map back to exact UI param names for frontend syncing
        ui_mappings = {
            'Num_Doors': 'num_doors',
            'Door_Area_m2': 'door_area',
            'Num_Windows': 'num_windows',
            'Window_Area_m2': 'window_area',
            'Daylight_Factor_pct': 'daylight_factor',
            'Illuminance_lux': 'illuminance',
            'CCT_K': 'cct',
            'Walkable_Floor_Area_m2': 'walkable_floor'
        }
        for model_key, ui_key in ui_mappings.items():
            if model_key in full_features:
                full_features[ui_key] = full_features[model_key]
        
        return OptimizationResult(
            length=full_features.get('Length_m', 0.0),
            width=full_features.get('Width_m', 0.0),
            height=full_features.get('Height_m', 0.0),
            predicted_valence=chosen_valence,
            predicted_arousal=chosen_arousal,
            neuro_score=chosen_ns,
            target_achieved=max(0.0, 1.0 - float(errors[chosen_idx])),
            samples_evaluated=n_samples,
            full_features=full_features,
        )

    def optimize_full(
        self,
        target_score: float,
        fixed_features: Optional[Dict[str, float]] = None,
    ) -> OptimizationResult:
        """Alias for optimize_for_target to maintain compatibility."""
        return self.optimize_for_target(target_score=target_score, fixed_features=fixed_features)