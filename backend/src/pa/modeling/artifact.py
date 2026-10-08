"""Trusted local fitted pipeline persistence and compatibility checks."""

from __future__ import annotations

import hashlib
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
import scipy
import sklearn

from pa.config import MODEL, ROOT, SCHEMA_VERSION
from pa.features.builder import FEATURE_ORDER


class ArtifactUnavailable(RuntimeError):
    """Missing, invalid or incompatible trusted local model artifact."""


@dataclass(frozen=True)
class LoadedArtifact:
    pipeline: Any
    metadata: dict


def source_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def code_tree_hash() -> str:
    digest = hashlib.sha256()
    for path in sorted((ROOT / "backend/src/pa").rglob("*.py")):
        digest.update(str(path.relative_to(ROOT)).encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


def current_code_revision() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                       text=True, stderr=subprocess.DEVNULL).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unavailable"


def source_snapshot_status() -> str:
    try:
        status = subprocess.check_output(
            ["git", "status", "--porcelain", "--", "backend/src/pa", "backend/pyproject.toml",
             "backend/uv.lock", "docs/specs/analysis-v1.md", "data/MANIFEST.sha256"],
            cwd=ROOT, text=True, stderr=subprocess.DEVNULL)
        return "uncommitted_changes" if status.strip() else "clean_committed_tree"
    except (OSError, subprocess.CalledProcessError):
        return "git_status_unavailable"


def build_metadata(*, model_status: str, training_scope: dict, metrics: dict,
                   limitations: list[str]) -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_version": "1.0.0",
        "model_status": model_status,
        "feature_order": list(FEATURE_ORDER),
        "sklearn_version": sklearn.__version__,
        "numpy_version": np.__version__,
        "pandas_version": pd.__version__,
        "scipy_version": scipy.__version__,
        "uv_lock_sha256": source_hash(ROOT / "backend/uv.lock"),
        "pyproject_sha256": source_hash(ROOT / "backend/pyproject.toml"),
        "decisions_sha256": source_hash(ROOT / "backend/src/pa/decisions.yaml"),
        "code_tree_sha256": code_tree_hash(),
        "dataset_manifest_sha256": source_hash(ROOT / "data/MANIFEST.sha256"),
        "analysis_spec_sha256": source_hash(ROOT / "docs/specs/analysis-v1.md"),
        "base_git_revision": current_code_revision(),
        "source_snapshot_status": source_snapshot_status(),
        "training_scope": training_scope,
        "metrics": metrics,
        "limitations": limitations,
    }


def save_artifact(pipeline: Any, metadata: dict, directory: Path = MODEL) -> None:
    if not hasattr(pipeline, "predict"):
        raise ValueError("model artifact has no predict method")
    if metadata.get("feature_order") != list(FEATURE_ORDER):
        raise ValueError("feature schema mismatch before save")
    directory.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, directory / "model.joblib")
    saved = {**metadata, "model_sha256": source_hash(directory / "model.joblib")}
    (directory / "metadata.json").write_text(json.dumps(saved, indent=2, allow_nan=False) + "\n")


def load_artifact(directory: Path = MODEL) -> LoadedArtifact:
    metadata_path = directory / "metadata.json"
    model_path = directory / "model.joblib"
    if not metadata_path.is_file() or not model_path.is_file():
        raise ArtifactUnavailable("model artifact or metadata is missing")
    try:
        metadata = json.loads(metadata_path.read_text())
    except (OSError, ValueError) as exc:
        raise ArtifactUnavailable("model metadata is unreadable") from exc
    checks = {
        "schema_version": SCHEMA_VERSION,
        "feature_order": list(FEATURE_ORDER),
        "sklearn_version": sklearn.__version__,
        "numpy_version": np.__version__,
        "pandas_version": pd.__version__,
        "scipy_version": scipy.__version__,
        "uv_lock_sha256": source_hash(ROOT / "backend/uv.lock"),
        "pyproject_sha256": source_hash(ROOT / "backend/pyproject.toml"),
        "decisions_sha256": source_hash(ROOT / "backend/src/pa/decisions.yaml"),
        "code_tree_sha256": code_tree_hash(),
        "dataset_manifest_sha256": source_hash(ROOT / "data/MANIFEST.sha256"),
        "analysis_spec_sha256": source_hash(ROOT / "docs/specs/analysis-v1.md"),
        "model_sha256": source_hash(model_path),
    }
    differences = [field for field, expected in checks.items() if metadata.get(field) != expected]
    if differences:
        raise ArtifactUnavailable("incompatible model metadata: " + ", ".join(differences))
    try:
        pipeline = joblib.load(model_path)
    except (OSError, ValueError, EOFError) as exc:
        raise ArtifactUnavailable("model artifact cannot be loaded") from exc
    if not hasattr(pipeline, "predict"):
        raise ArtifactUnavailable("model artifact has no predict method")
    return LoadedArtifact(pipeline, metadata)
