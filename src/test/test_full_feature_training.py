import pandas as pd
import torch

from src.models.architectures import SpatialMLP
from src.models.train import Trainer


def test_spatial_mlp_accepts_dynamic_input_dim():
    model = SpatialMLP(input_dim=7)
    out = model(torch.randn(4, 7))
    assert out.shape == (4, 2)


def test_full_feature_builder_and_targets():
    trainer = Trainer(model_type='Random Forest', feature_mode='full')

    df = pd.DataFrame(
        {
            'Subject_ID': ['S1', 'S2', 'S3'],
            'Room_ID': ['R1', 'R2', 'R3'],
            'EEG_Filename': ['a.csv', 'b.csv', 'c.csv'],
            'Valence Score by Subject': [0.6, 0.0, 0.2],
            'Arousal Score by Subject': [-0.4, 0.2, 0.4],
            'Length (meter)': [8.0, 10.0, 12.0],
            'Width (meter)': [4.0, 5.0, 6.0],
            'Height (meter)': [3.0, 3.2, 3.4],
            'Illuminance (lux)': [150, 500, 900],
            'Day or Night': ['Night', 'Day', 'Day'],
            '__experiment': ['experiment_02', 'experiment_02', 'experiment_01'],
        }
    )

    y = trainer._extract_targets(df)
    assert y.shape == (3, 2)

    x_df, feature_names = trainer._build_features(df.loc[y.index])

    assert 'Length (meter)' in feature_names
    assert 'Width (meter)' in feature_names
    assert 'Height (meter)' in feature_names
    assert any(name.startswith('Day or Night_') for name in feature_names)
    assert x_df.isna().sum().sum() == 0
