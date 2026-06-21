from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np


_DEFAULT_MDS_COORDS: Dict[str, List[float]] = {
    "amusing": [0.7, 0.2],
    "angry": [-0.7, 0.7],
    "anxious": [-0.5, 0.8],
    "awful": [-0.8, 0.5],
    "boring": [-0.4, -0.6],
    "calm": [0.7, -0.7],
    "disgusting": [-0.7, 0.3],
    "exciting": [0.8, 0.8],
    "happy": [0.9, 0.4],
    "interesting": [0.4, 0.3],
    "pleasant": [0.8, -0.1],
    "sad": [-0.7, -0.4],
    "scary": [-0.6, 0.7],
}


class CognitiveBridge:
    """Legacy bridge for mapping emotion-probability vectors to MDS trajectories."""

    def __init__(self, mds_path: Optional[str] = None):
        coords = _DEFAULT_MDS_COORDS if mds_path is None else self._load_coords(Path(mds_path))
        self._validate_coords(coords)
        self.mds_coords: Dict[str, List[float]] = coords
        self.categories: List[str] = list(coords.keys())

    @staticmethod
    def _load_coords(path: Path) -> Dict[str, List[float]]:
        raw = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            raise ValueError("MDS coordinates file must contain a JSON object.")
        return {str(k): list(v) for k, v in raw.items()}

    @staticmethod
    def _validate_coords(coords: Dict[str, List[float]]) -> None:
        for category, pair in coords.items():
            arr = np.asarray(pair, dtype=np.float64)
            if arr.shape != (2,) or not np.all(np.isfinite(arr)):
                raise ValueError(f"Invalid 2D coordinates for '{category}'.")
            if np.any(arr < -1.0) or np.any(arr > 1.0):
                raise ValueError(f"Coordinates for '{category}' are out of bounds [-1, 1].")

    def eeg_to_trajectory(self, probabilities: np.ndarray) -> np.ndarray:
        probs = np.asarray(probabilities, dtype=np.float64)
        if probs.ndim == 1:
            probs = probs.reshape(1, -1)
        if probs.ndim != 2:
            raise ValueError("probabilities must be a 1D or 2D array.")
        if probs.shape[1] != len(self.categories):
            raise ValueError(
                f"Expected {len(self.categories)} categories, got {probs.shape[1]}."
            )

        coords = np.asarray([self.mds_coords[name] for name in self.categories], dtype=np.float64)
        row_sums = probs.sum(axis=1, keepdims=True)
        safe_sums = np.where(row_sums == 0.0, 1.0, row_sums)
        normalized = probs / safe_sums
        return normalized @ coords
