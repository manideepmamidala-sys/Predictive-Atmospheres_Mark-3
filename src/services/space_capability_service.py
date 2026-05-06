"""
SpaCE Capability Service
Predict SR/CK/EI capability signals from architectural parameters.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict
import pickle

import numpy as np


@dataclass
class CapabilityResult:
    spatial_reasoning: float
    commonsense_knowledge: float
    environment_interaction: float

    def as_dict(self) -> Dict[str, float]:
        return {
            "Spatial Reasoning": float(self.spatial_reasoning),
            "Commonsense Knowledge": float(self.commonsense_knowledge),
            "Environment Interaction": float(self.environment_interaction),
        }


class SpaceCapabilityService:
    """Loads additive SpaCE capability model and runs inference."""

    def __init__(self, model_path: str | None = None):
        root = Path(__file__).resolve().parents[2]
        self.model_path = Path(model_path) if model_path else root / "artifacts" / "models" / "space_eval_capability_model.pkl"
        self._model: Any = None

    def has_model(self) -> bool:
        return self.model_path.exists()

    def _ensure_loaded(self) -> None:
        if self._model is None:
            if not self.model_path.exists():
                raise FileNotFoundError(
                    f"SpaCE capability model not found at {self.model_path}. "
                    "Run: python -m src.cli space-eval-integrate"
                )
            with self.model_path.open("rb") as f:
                self._model = pickle.load(f)

    @staticmethod
    def _feature_vector(length: float, width: float, height: float) -> np.ndarray:
        area = length * width
        volume = area * height
        aspect_ratio = max(length, width) / max(min(length, width), 1e-6)

        # Optional feature slots default to zero for interactive UI prediction.
        vector = np.array([
            length,
            width,
            height,
            area,
            volume,
            aspect_ratio,
            0.0,  # window_count
            0.0,  # window_area
            0.0,  # natural_light
            0.0,  # artificial_light
            0.0,  # walkable_ratio
        ], dtype=np.float32)
        return vector.reshape(1, -1)

    def predict(self, length: float, width: float, height: float) -> CapabilityResult:
        self._ensure_loaded()
        x = self._feature_vector(length, width, height)
        pred = np.asarray(self._model.predict(x), dtype=np.float32).reshape(-1)
        pred = np.clip(pred, 0.0, 1.0)

        return CapabilityResult(
            spatial_reasoning=float(pred[0]),
            commonsense_knowledge=float(pred[1]),
            environment_interaction=float(pred[2]),
        )
