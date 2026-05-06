import json
import os
import torch
import numpy as np
from typing import Dict, Tuple, Union

class CognitiveBridge:
    """
    Translates prefrontal EEG signal features into the cognitive map framework
    proposed by Ma & Kragel (2026).
    """
    def __init__(self, mds_path: str = "data/paper_data/mds_coordinates/emotion_categories_13.json"):
        # The 13 emotion categories from the paper
        self.categories: list[str] = [
            'amusing', 'angry', 'anxious', 'awful', 'boring', 
            'calm', 'disgusting', 'exciting', 'happy', 'interesting',
            'pleasant', 'sad', 'scary'
        ]
        self.mds_coords = self._load_mds_coordinates(mds_path)
        self._validate_coordinates(self.mds_coords)
        
    def _load_mds_coordinates(self, mds_path: str) -> Dict[str, np.ndarray]:
        """Load the 2D affective-space coordinates for the 13 emotion categories."""
        if not os.path.exists(mds_path):
            print(f"Warning: {mds_path} not found. Using approximate MDS coordinates.")
            return self._get_approx_mds_coords()
            
        with open(mds_path, 'r') as f:
            data = json.load(f)

        # Supported formats:
        # 1) {"amusing": [x,y], ...}
        # 2) [ [x,y], ... ] with len == 13 in category order
        coords = {}
        for i, cat in enumerate(self.categories):
            if isinstance(data, list) and len(data) == 13:
                coords[cat] = np.array(data[i])
            elif isinstance(data, dict) and cat in data:
                coords[cat] = np.array(data[cat])

        if not coords:
            print(f"Warning: {mds_path} does not contain expected 13-category schema. Using approximate MDS coordinates.")
            return self._get_approx_mds_coords()

        return coords

    def _validate_coordinates(self, coords: Dict[str, np.ndarray]) -> None:
        """Validate MDS coordinates: complete category set, finite values, and bounds."""
        missing = [cat for cat in self.categories if cat not in coords]
        if missing:
            raise ValueError(f"Missing categories in MDS coordinates: {missing}")

        for category in self.categories:
            value = np.asarray(coords[category], dtype=np.float64)
            if value.shape != (2,):
                raise ValueError(f"Invalid coordinate shape for '{category}': {value.shape}, expected (2,)")
            if not np.all(np.isfinite(value)):
                raise ValueError(f"Non-finite coordinate for '{category}': {value}")
            if np.any(value < -1.0) or np.any(value > 1.0):
                raise ValueError(f"Coordinate out of bounds for '{category}': {value}, expected in [-1, 1]")
        
    def _get_approx_mds_coords(self) -> Dict[str, np.ndarray]:
        """
        Approximate MDS coordinates based on standard valence-arousal space.
        X-axis: Valence (negative to positive)
        Y-axis: Arousal (low to high)
        """
        return {
            'amusing': np.array([0.6, 0.4]),
            'angry': np.array([-0.7, 0.7]),
            'anxious': np.array([-0.5, 0.8]),
            'awful': np.array([-0.8, 0.5]),
            'boring': np.array([-0.4, -0.6]),
            'calm': np.array([0.7, -0.7]),
            'disgusting': np.array([-0.7, 0.3]),
            'exciting': np.array([0.8, 0.8]),
            'happy': np.array([0.9, 0.4]),
            'interesting': np.array([0.4, 0.3]),
            'pleasant': np.array([0.8, -0.1]),
            'sad': np.array([-0.7, -0.4]),
            'scary': np.array([-0.6, 0.7])
        }
        
    def eeg_to_trajectory(self, emotion_probs: Union[np.ndarray, torch.Tensor]) -> np.ndarray:
        """
        Paper Equation: trajectory(t) = sum(rating_c(t) * MDS_coord_c)
        
        Projects emotion category probabilities (from PLS or Neural Net)
        into a single 2D affective space coordinate [valence, arousal].
        
        Args:
            emotion_probs: Target probabilities for the 13 categories.
                           Can be a numpy array or torch Tensor (Batch x 13).
                           
        Returns:
            np.ndarray: [Batch x 2] array of [x, y] coordinates in MDS space.
        """
        if isinstance(emotion_probs, torch.Tensor):
            emotion_probs_arr = emotion_probs.detach().cpu().numpy()
        else:
            emotion_probs_arr = np.asarray(emotion_probs)
            
        # Ensure it's a 2D array (batch_size, num_categories)
        if emotion_probs_arr.ndim == 1:
            emotion_probs_arr = emotion_probs_arr.reshape(1, -1)

        if emotion_probs_arr.ndim != 2 or emotion_probs_arr.shape[1] != len(self.categories):
            raise ValueError(
                f"emotion_probs must have shape (N, {len(self.categories)}) or ({len(self.categories)},), "
                f"got {emotion_probs_arr.shape}"
            )
        
        # Get coordinates matrix (13 x 2)
        coord_matrix = np.array([self.mds_coords[cat] for cat in self.categories])
        
        # Matrix multiplication: (Batch x 13) @ (13 x 2) -> (Batch x 2)
        trajectories = np.dot(emotion_probs_arr, coord_matrix)
        return np.asarray(trajectories, dtype=np.float64)
        
    def map_to_grid(self, trajectory: Union[np.ndarray, list[float], tuple[float, float]], grid_size: int = 11) -> Tuple[int, int]:
        """
        Maps a continuous trajectory coordinate to the discrete 11x11 TEM grid.
        
        Args:
            trajectory: [x, y] coordinate in continuous affective space
            grid_size: Size of the grid (paper uses 11x11)
            
        Returns:
            Tuple[int, int]: (row, col) indices in the grid based on [x,y] position
        """
        # Assume trajectory coords are roughly in [-1, 1] range after normalization
        # We need to map [-1, 1] -> [0, grid_size-1]
        
        # Clip to ensure we stay in bounds
        x = np.clip(trajectory[0], -1.0, 1.0)
        y = np.clip(trajectory[1], -1.0, 1.0)
        
        # Map from [-1, 1] to [0, 1]
        x_norm = (x + 1.0) / 2.0
        y_norm = (y + 1.0) / 2.0
        
        # Map to discrete bins [0, 10]
        # In an image array, row is y-axis (inverted), col is x-axis
        # We'll stick to standard Cartesian coordinates where y goes UP
        col = int(round(x_norm * (grid_size - 1)))
        row = int(round(y_norm * (grid_size - 1)))
        
        # Ensure exact bounds
        col = max(0, min(grid_size - 1, col))
        row = max(0, min(grid_size - 1, row))
        
        return (row, col)

if __name__ == "__main__":
    # Test the bridge
    bridge = CognitiveBridge()
    import scipy.special
    dummy_probs = scipy.special.softmax(np.random.randn(1, 13), axis=1)
    
    trajectory = bridge.eeg_to_trajectory(dummy_probs)
    print(f"Input Probs: {dummy_probs}")
    print(f"Trajectory (2D): {trajectory}")
    
    grid_pos = bridge.map_to_grid(trajectory[0])
    print(f"Mapped to TEM grid cell: {grid_pos}")
