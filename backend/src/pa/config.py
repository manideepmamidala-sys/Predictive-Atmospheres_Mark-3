"""Repository paths resolved independently of the launch directory."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "data"
ARTIFACTS = ROOT / "artifacts"
RESULTS = ARTIFACTS / "results"
MODEL = ARTIFACTS / "model"
SCHEMA_VERSION = "1.0.0"
