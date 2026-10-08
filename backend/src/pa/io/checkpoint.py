"""Apply-stage scientific result gate; coordinator records the independent verdict."""

from __future__ import annotations

from pathlib import Path

from pa.config import ROOT


def require_science_checkpoint(path: Path = ROOT / "docs/reports/analysis-checkpoint.md") -> None:
    if not path.exists() or "**Coordinator verdict:** PASS" not in path.read_text():
        raise RuntimeError("scientific processing held until recorded independent checkpoint PASS")
