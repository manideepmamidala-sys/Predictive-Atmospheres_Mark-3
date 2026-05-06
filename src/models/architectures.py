"""
Neural Network Architectures
Aligned with: arxiv.org/html/2506.16448v1 (Section 3.3.2 & 3.3.3)

SpatialMLP:
  - Room dimensions (L, W, H) → Valence, Arousal prediction
  - ReLU hidden layers, Tanh output (maps to [-1, 1])

SpatialFFNN:
  - Extended spatial features (20+ parameters) → Valence, Arousal prediction
  - BatchNorm + Dropout + Residual connections for regularization
  - Tanh output maps to [-1, 1] for V/A space
"""
import torch
import torch.nn as nn


class SpatialMLP(nn.Module):
    """
    MLP for predicting emotional response from room dimensions.
    Input: 3 features (Length, Width, Height)
    Output: 2 values (Valence, Arousal) in range [-1, 1]

    Architecture follows standard ANN principles from paper §2.4.1:
      - Input layer → Hidden layers with ReLU → Output with Tanh
    """

    def __init__(self, input_dim: int = 3) -> None:
        super(SpatialMLP, self).__init__()
        self.fc1 = nn.Linear(input_dim, 16)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(16, 32)
        self.fc3 = nn.Linear(32, 2)  # Valence, Arousal
        self.tanh = nn.Tanh()        # Maps to [-1, 1] for MDS space

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.relu(self.fc1(x))
        x = self.relu(self.fc2(x))
        x = self.tanh(self.fc3(x))
        return x


class SpatialFFNN(nn.Module):
    """
    Feed-Forward Neural Network for predicting emotional response from
    extended architectural spatial features (20+ parameters).

    Designed for Experiment 02 data which includes geometry, openings,
    daylight metrics, and environmental conditions.

    Architecture:
      - Input → 64 → BatchNorm → ReLU → Dropout(0.3)
      - 64 → 128 → BatchNorm → ReLU → Dropout(0.2)
      - 128 → 64 → BatchNorm → ReLU → Dropout(0.1)   [+ residual from layer 1]
      - 64 → 32 → ReLU → 2 → Tanh

    Features:
      - Batch normalization for training stability across heterogeneous feature ranges
      - Dropout for regularization (critical with limited dataset ~90 rows)
      - Residual connection from layer 1 to layer 3 for gradient flow
      - Tanh output maps to [-1, 1] Valence/Arousal space
    """

    def __init__(self, input_dim: int = 20) -> None:
        super(SpatialFFNN, self).__init__()
        self.input_dim = input_dim

        # Layer 1: input → 64
        self.layer1 = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Dropout(p=0.3),
        )

        # Layer 2: 64 → 128
        self.layer2 = nn.Sequential(
            nn.Linear(64, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Dropout(p=0.2),
        )

        # Layer 3: 128 → 64 (receives residual from layer 1)
        self.layer3_main = nn.Sequential(
            nn.Linear(128, 64),
            nn.BatchNorm1d(64),
        )
        self.layer3_act = nn.Sequential(
            nn.ReLU(),
            nn.Dropout(p=0.1),
        )

        # Output head: 64 → 32 → 2
        self.output_head = nn.Sequential(
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 2),
            nn.Tanh(),  # Maps to [-1, 1] for V/A space
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass.
        Args:
            x: (Batch, input_dim) — spatial feature vector
        Returns:
            (Batch, 2) — [Valence, Arousal] in [-1, 1]
        """
        # Layer 1
        h1 = self.layer1(x)           # (B, 64)

        # Layer 2
        h2 = self.layer2(h1)          # (B, 128)

        # Layer 3 with residual connection from Layer 1
        h3 = self.layer3_main(h2)     # (B, 64)
        h3 = h3 + h1                  # Residual connection
        h3 = self.layer3_act(h3)      # (B, 64)

        # Output
        out = self.output_head(h3)    # (B, 2)
        return out
