"""
Experiment Registry
===================
Config-driven loader for multi-experiment data.

Each experiment is defined by:
    - A biometric metadata CSV in data/metadata/experiment_XX_biometric data.csv
    - A spatial metadata CSV in data/metadata/experiment_XX_spatial data.csv
  - Raw signal files in data/raw/experiment_XX/

Adding a new experiment:
  1. Create data/raw/experiment_03/ and place your CSV recordings there
  2. Create data/metadata/experiment_03_spatial data.csv with columns:
      Room_ID, Length (meter), Width (meter), Height (meter)
      Plus any additional spatial columns you want.
  3. Create data/metadata/experiment_03_biometric data.csv with columns:
      Subject_ID, Room_ID, Time spent by the subject in the room (seconds), EEG_Filename
      Plus labels (`Score by Subject_(0-10)` or `Valence/Arousal Score by Subject (0-10)`).
    4. The loader auto-discovers experiments from data/metadata/.

Usage:
        from src.data.experiment_registry import discover_experiments
    experiments = discover_experiments()
"""
import os
import glob
import logging
from dataclasses import dataclass, field
from typing import List, Optional

import pandas as pd

from src.config import get_config

logger = logging.getLogger(__name__)


@dataclass
class ExperimentInfo:
    """Metadata about a discovered experiment."""
    name: str                          # e.g. "experiment_01"
    biometric_csv: str                 # absolute path to biometric CSV
    spatial_csv: str                   # absolute path to spatial CSV
    raw_dir: str                       # absolute path to raw signal folder
    num_rows: int = 0                  # rows in biometric CSV (discovered lazily)
    spatial_columns: List[str] = field(default_factory=list)  # detected spatial columns

    @property
    def has_data(self) -> bool:
        return (
            self.num_rows > 0
            and os.path.isdir(self.raw_dir)
            and os.path.exists(self.biometric_csv)
            and os.path.exists(self.spatial_csv)
        )


# Required columns that must appear in every biometric CSV
_REQUIRED_BIOMETRIC_COLUMNS = {'Room_ID', 'EEG_Filename', 'Subject_ID'}


def discover_experiments(data_dir: Optional[str] = None) -> List[ExperimentInfo]:
    """
    Auto-discover experiments from paired split metadata files:
      - experiment_*_biometric data.csv
      - experiment_*_spatial data.csv

    Returns a list of ExperimentInfo objects sorted by name.
    """
    config = get_config()
    data_dir = data_dir or config.paths.data_dir
    metadata_dir = os.path.join(data_dir, 'metadata')

    biometric_pattern = os.path.join(metadata_dir, 'experiment_*_biometric data.csv')
    biometric_files = sorted(glob.glob(biometric_pattern))

    experiments: List[ExperimentInfo] = []
    for biometric_path in biometric_files:
        basename = os.path.basename(biometric_path)
        # e.g. "experiment_01_biometric data.csv" → "experiment_01"
        exp_name = basename.replace('_biometric data.csv', '')
        spatial_path = os.path.join(metadata_dir, f'{exp_name}_spatial data.csv')

        if not os.path.exists(spatial_path):
            logger.warning(f"Skipping {exp_name}: missing spatial file {spatial_path}")
            continue

        raw_dir = os.path.join(data_dir, 'raw', exp_name)

        info = ExperimentInfo(
            name=exp_name,
            biometric_csv=biometric_path,
            spatial_csv=spatial_path,
            raw_dir=raw_dir,
        )

        # Probe CSVs
        try:
            bio_df = pd.read_csv(biometric_path, nrows=0)  # headers only
            spatial_df = pd.read_csv(spatial_path, nrows=0)  # headers only

            missing = _REQUIRED_BIOMETRIC_COLUMNS - set(bio_df.columns)
            if missing:
                logger.warning(f"Biometric CSV for {exp_name} missing required columns: {sorted(missing)}")

            info.num_rows = sum(1 for _ in open(biometric_path, encoding='utf-8')) - 1
            if info.num_rows < 0:
                info.num_rows = 0

            # Detect spatial columns from spatial metadata file
            reserved_spatial = {
                'Room_ID',
                'Type of Space',
                'Emotion felt by Subject',
                'Questions asked to the Subject',
            }
            info.spatial_columns = [c for c in spatial_df.columns if c not in reserved_spatial]
        except Exception as e:
            logger.warning(f"Could not probe metadata for {exp_name}: {e}")

        experiments.append(info)

    logger.info(f"Discovered {len(experiments)} experiment(s): {[e.name for e in experiments]}")
    return experiments


def get_spatial_columns(experiments: Optional[List[ExperimentInfo]] = None) -> List[str]:
    """
    Return the union of spatial columns across all experiments.
    Falls back to the default 3 columns if none discovered.
    """
    if experiments is None:
        experiments = discover_experiments()

    all_cols: set = set()
    for exp in experiments:
        all_cols.update(exp.spatial_columns)

    if not all_cols:
        return ['Length (meter)', 'Width (meter)', 'Height (meter)']
    return sorted(all_cols)
