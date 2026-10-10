"""Expose the unchanged research API to Vercel's Python runtime."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend" / "src"))

from pa.api.app import app  # noqa: E402
