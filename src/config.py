"""
Configuration Module
Centralized configuration for all system parameters.

Usage:
    from src.config import Config, get_config
    config = get_config()
    print(config.eeg.sample_rate)
"""
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
import json
import os


@dataclass
class EEGConfig:
    """EEG signal processing configuration."""
    sample_rate: int = 256
    filter_order: int = 4
    low_cutoff: float = 0.5
    high_cutoff: float = 50.0
    target_length: int = 500
    channels: int = 3

    # Preprocessing
    baseline_window_sec: float = 2.0
    zscore_epsilon: float = 1e-6

    # Frequency bands (Hz)
    delta_range: tuple = (0.5, 4)
    theta_range: tuple = (4, 8)
    alpha_range: tuple = (8, 13)
    beta_range: tuple = (13, 30)
    gamma_range: tuple = (30, 100)


@dataclass
class ModelConfig:
    """Neural network model configuration."""
    # SpatialMLP (legacy)
    spatial_hidden_sizes: List[int] = field(default_factory=lambda: [16, 32])
    spatial_output_dim: int = 2

    # SpatialFFNN (new — for extended spatial features)
    ffnn_hidden_sizes: List[int] = field(default_factory=lambda: [64, 128, 64, 32])
    ffnn_dropout_rates: List[float] = field(default_factory=lambda: [0.3, 0.2, 0.1])
    ffnn_use_batch_norm: bool = True
    ffnn_use_residual: bool = True

    # CognitiveMapMLP
    cognitive_shared_sizes: List[int] = field(default_factory=lambda: [32, 64])
    cognitive_num_categories: int = 13

    # MultiScaleEEGCNN
    eeg_in_channels: int = 3
    eeg_temporal_len: int = 500
    eeg_num_t_filters: int = 8
    eeg_ratios: List[float] = field(default_factory=lambda: [0.5, 0.25, 0.125, 0.0625, 0.03125])
    eeg_dropout: float = 0.3

    # Default model type for training
    default_model_type: str = 'PyTorch FFNN'


@dataclass
class SpatialFeatureConfig:
    """
    Spatial feature definitions with strict independent/derived separation.

    Independent features are raw inputs from experiments or user.
    Derived features are computed by the backend from independent features.
    Categorical features are one-hot encoded before model input.

    Each independent feature has: (min_value, max_value, default_value, unit, category).
    """
    Length_m: Dict[str, Any] = field(default_factory=lambda: {'min': 2.0, 'max': 50.0, 'default': 10.0, 'unit': 'm', 'category': 'geometry'})
    Width_m: Dict[str, Any] = field(default_factory=lambda: {'min': 2.0, 'max': 50.0, 'default': 8.0, 'unit': 'm', 'category': 'geometry'})
    Height_m: Dict[str, Any] = field(default_factory=lambda: {'min': 2.0, 'max': 10.0, 'default': 3.5, 'unit': 'm', 'category': 'geometry'})
    Num_Doors: Dict[str, Any] = field(default_factory=lambda: {'min': 0.0, 'max': 10.0, 'default': 1.0, 'unit': '', 'category': 'openings'})
    Door_Area_m2: Dict[str, Any] = field(default_factory=lambda: {'min': 0.0, 'max': 30.0, 'default': 1.8, 'unit': 'm²', 'category': 'openings'})
    Num_Windows: Dict[str, Any] = field(default_factory=lambda: {'min': 0.0, 'max': 30.0, 'default': 2.0, 'unit': '', 'category': 'openings'})
    Window_Area_m2: Dict[str, Any] = field(default_factory=lambda: {'min': 0.0, 'max': 250.0, 'default': 5.0, 'unit': 'm²', 'category': 'openings'})
    Daylight_Factor_pct: Dict[str, Any] = field(default_factory=lambda: {'min': 0.0, 'max': 20.0, 'default': 2.0, 'unit': '%', 'category': 'daylight'})
    Illuminance_lux: Dict[str, Any] = field(default_factory=lambda: {'min': 0.0, 'max': 2000.0, 'default': 300.0, 'unit': 'lux', 'category': 'daylight'})
    CCT_K: Dict[str, Any] = field(default_factory=lambda: {'min': 2000.0, 'max': 10000.0, 'default': 4000.0, 'unit': 'K', 'category': 'daylight'})
    Walkable_Floor_Area_m2: Dict[str, Any] = field(default_factory=lambda: {'min': 0.0, 'max': 500.0, 'default': 60.0, 'unit': 'm²', 'category': 'geometry'})

    # Condition categorical (one-hot encoded)
    condition_features: List[str] = field(default_factory=lambda: ['Day_or_Night'])

    # Space type categorical (one-hot encoded)
    categorical_features: List[str] = field(default_factory=lambda: ['Type_of_Space'])

    # Valid categories for Type of Space
    space_types: List[str] = field(default_factory=lambda: [
        'Bedroom', 'Living Room', 'Workplace', 'Classroom', 'Cafeteria',
    ])

    def get_independent_feature_names(self) -> List[str]:
        """Return ordered list of independent numeric feature names."""
        return sorted([
            'Length_m', 'Width_m', 'Height_m', 'Num_Doors', 'Door_Area_m2', 
            'Num_Windows', 'Window_Area_m2', 'Daylight_Factor_pct', 
            'Illuminance_lux', 'CCT_K', 'Walkable_Floor_Area_m2'
        ])


@dataclass
class TrainingConfig:
    """Training hyperparameters."""
    epochs: int = 300
    learning_rate: float = 0.005
    lr_scheduler_factor: float = 0.5
    lr_scheduler_patience: int = 25
    convergence_threshold: float = 0.001
    convergence_window: int = 20
    default_feature_mode: str = 'full'

    # scikit-learn alternatives
    sklearn_hidden_layers: tuple = (64, 32)
    sklearn_max_iter: int = 500
    sklearn_random_state: int = 42

    def __post_init__(self):
        if self.epochs < 1:
            raise ValueError("training.epochs must be >= 1")
        if not (0 < self.learning_rate <= 1.0):
            raise ValueError("training.learning_rate must be in (0, 1]")
        if self.lr_scheduler_patience < 1:
            raise ValueError("training.lr_scheduler_patience must be >= 1")


@dataclass
class RoomConfig:
    """Room design parameters — core geometry ranges."""
    min_length: float = 2.0
    max_length: float = 50.0
    min_width: float = 2.0
    max_width: float = 50.0
    min_height: float = 2.0
    max_height: float = 10.0

    # Default dimensions
    default_length: float = 10.0
    default_width: float = 8.0
    default_height: float = 3.5

    def __post_init__(self):
        if not (self.min_length < self.max_length):
            raise ValueError("room.min_length must be < room.max_length")
        if not (self.min_width < self.max_width):
            raise ValueError("room.min_width must be < room.max_width")
        if not (self.min_height < self.max_height):
            raise ValueError("room.min_height must be < room.max_height")


@dataclass
class OptimizationConfig:
    """Room optimization parameters."""
    monte_carlo_samples: int = 2000
    target_score_default: float = 0.8

    def __post_init__(self):
        if self.monte_carlo_samples < 10:
            raise ValueError("optimization.monte_carlo_samples must be >= 10")
        if not (0.0 <= self.target_score_default <= 1.0):
            raise ValueError("optimization.target_score_default must be in [0, 1]")


@dataclass
class EmotionConfig:
    """Emotion centroids for MDS space mapping."""
    # Reference centroids in V-A space
    centroids: Dict[str, List[float]] = field(default_factory=lambda: {
        'Anger': [-0.7, 0.7],
        'Anxiety': [-0.4, 0.6],
        'Fear': [-0.6, 0.8],
        'Surprise': [0.3, 0.8],
        'Guilt': [-0.5, 0.3],
        'Disgust': [-0.6, 0.4],
        'Sad': [-0.7, -0.4],
        'Regard': [0.3, 0.2],
        'Satisfaction': [0.7, -0.3],
        'WarmHeartedness': [0.6, -0.2],
        'Happiness': [0.8, 0.5],
        'Pride': [0.7, 0.6],
        'Love': [0.8, 0.3]
    })

    # Distance decay for emotion weighting
    distance_decay: float = 8.0

    # Atmosphere classification thresholds
    positive_threshold: float = 0.3
    negative_threshold: float = -0.3


@dataclass
class FusionConfig:
    """Multimodal affective fusion parameters.

    Controls the weighted combination of objective (EEG/ECG-derived) and
    subjective (self-reported) affective scores into a single ground-truth target.

    Target_Valence = alpha × FAA  + (1 - alpha) × Subjective_Valence
    Target_Arousal = alpha × RMSSD + (1 - alpha) × Subjective_Arousal
    """
    # Weight for objective biometric signal (higher = trust EEG/ECG more)
    alpha: float = 0.6

    def __post_init__(self):
        if not (0.0 <= self.alpha <= 1.0):
            raise ValueError("fusion.alpha must be in [0.0, 1.0]")


@dataclass
class CacheConfig:
    """Caching configuration."""
    data_cache_ttl: int = 3600  # 1 hour
    resource_cache_ttl: int = 86400  # 24 hours
    mds_cache_maxsize: int = 128


@dataclass
class PathsConfig:
    """File system paths."""
    base_dir: str = ""
    data_dir: str = ""
    cache_dir: str = ""
    output_dir: str = ""

    def __post_init__(self):
        if not self.base_dir:
            self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if not self.data_dir:
            self.data_dir = os.path.join(self.base_dir, 'data')
        if not self.cache_dir:
            self.cache_dir = os.path.join(self.data_dir, 'processed')
        if not self.output_dir:
            self.output_dir = os.path.join(self.base_dir, 'output')


@dataclass
class Config:
    """Main configuration container."""
    eeg: EEGConfig = field(default_factory=EEGConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    training: TrainingConfig = field(default_factory=TrainingConfig)
    room: RoomConfig = field(default_factory=RoomConfig)
    optimization: OptimizationConfig = field(default_factory=OptimizationConfig)
    emotion: EmotionConfig = field(default_factory=EmotionConfig)
    fusion: FusionConfig = field(default_factory=FusionConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    paths: PathsConfig = field(default_factory=PathsConfig)
    spatial_features: SpatialFeatureConfig = field(default_factory=SpatialFeatureConfig)

    # Feature flags
    use_pytorch: bool = True  # Set False to use scikit-learn alternatives
    debug_mode: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        from dataclasses import asdict
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Config':
        """Create config from dictionary."""
        return cls(
            eeg=EEGConfig(**data.get('eeg', {})),
            model=ModelConfig(**data.get('model', {})),
            training=TrainingConfig(**data.get('training', {})),
            room=RoomConfig(**data.get('room', {})),
            optimization=OptimizationConfig(**data.get('optimization', {})),
            emotion=EmotionConfig(**data.get('emotion', {})),
            fusion=FusionConfig(**data.get('fusion', {})),
            cache=CacheConfig(**data.get('cache', {})),
            paths=PathsConfig(**data.get('paths', {})),
            use_pytorch=data.get('use_pytorch', True),
            debug_mode=data.get('debug_mode', False)
        )

    def save(self, filepath: str) -> None:
        """Save config to JSON file."""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, filepath: str) -> 'Config':
        """Load config from JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)


# Singleton instance
_config_instance: Optional[Config] = None


def get_config(reload: bool = False) -> Config:
    """
    Get the global configuration instance.

    Args:
        reload: Force reload from environment/config file

    Returns:
        Config instance
    """
    global _config_instance
    if _config_instance is None or reload:
        _config_instance = Config()

        # Check for config file
        config_file = os.environ.get('PREDICTIVE_ATMOSPHERES_CONFIG', '')
        if config_file and os.path.exists(config_file):
            _config_instance = Config.load(config_file)

        # Check environment variable for PyTorch toggle
        use_pytorch = os.environ.get('PREDICTIVE_ATMOSPHERES_USE_PYTORCH', 'true')
        _config_instance.use_pytorch = use_pytorch.lower() == 'true'

        # Optional environment overrides for key hyperparameters
        env_lr = os.environ.get('PREDICTIVE_ATMOSPHERES_LEARNING_RATE')
        if env_lr:
            _config_instance.training.learning_rate = float(env_lr)

        env_epochs = os.environ.get('PREDICTIVE_ATMOSPHERES_EPOCHS')
        if env_epochs:
            _config_instance.training.epochs = int(env_epochs)

        env_mc_samples = os.environ.get('PREDICTIVE_ATMOSPHERES_MONTE_CARLO_SAMPLES')
        if env_mc_samples:
            _config_instance.optimization.monte_carlo_samples = int(env_mc_samples)

        # Re-run dataclass validations after env overrides
        _config_instance.training.__post_init__()
        _config_instance.optimization.__post_init__()
        _config_instance.room.__post_init__()
        _config_instance.fusion.__post_init__()

    return _config_instance


def reset_config() -> None:
    """Reset the global config instance (mainly for testing)."""
    global _config_instance
    _config_instance = None