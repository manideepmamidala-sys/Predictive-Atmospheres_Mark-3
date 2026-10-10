"""Content guard for effective model inputs before spatial-null cache reuse."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from pa.config import RESULTS, ROOT
from pa.io.metadata import load_rooms
from pa.modeling.evaluate import evaluate_outer
from pa.modeling.nulls import CHECKPOINT, FINAL, _source_fingerprint
from pa.modeling.train import build_cohort

GUARD = RESULTS / "model_null_input.json"
DEPENDENCIES = (
    "backend/src/pa/modeling/train.py",
    "backend/src/pa/modeling/predict.py",
    "backend/src/pa/features/builder.py",
    "backend/src/pa/features/schema.py",
    "backend/src/pa/io/metadata.py",
    "backend/pyproject.toml",
    "backend/uv.lock",
)


def _digest(payload: object) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"),
                                     allow_nan=False).encode()).hexdigest()


def current_input_guard() -> dict:
    source = json.loads((RESULTS / "affect_detail.json").read_text())
    cohort = build_cohort(source, load_rooms())
    content = {"trial_ids": list(cohort.ids),
               "features": json.loads(cohort.X.to_json(orient="split", double_precision=15)),
               "raw_components": json.loads(cohort.raw.to_json(orient="split", double_precision=15)),
               "reports": cohort.reports.tolist(),
               "room_groups": cohort.room_groups.tolist(),
               "subject_groups": cohort.subject_groups.tolist()}
    return {"schema_version": "1.0.0", "effective_cohort_sha256": _digest(content),
            "cohort_trials": len(cohort.ids), "room_groups": len(set(cohort.room_groups)),
            "participant_groups": len(set(cohort.subject_groups)),
            "source_fingerprint": _source_fingerprint(),
            "dependency_sha256": {path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
                                  for path in DEPENDENCIES}}


def verify_or_create_null_guard(destination: Path = GUARD) -> dict:
    """Reject changed effective inputs/dependencies before any cached draw is consumed."""
    current = current_input_guard()
    if destination.exists():
        previous = json.loads(destination.read_text())
        if previous != current:
            raise RuntimeError("model null effective input/dependency guard changed; do not reuse cached draws")
        return current
    prior_path = FINAL if FINAL.exists() else CHECKPOINT
    if prior_path.exists():
        prior = json.loads(prior_path.read_text())
        if prior.get("source_fingerprint") != current["source_fingerprint"]:
            raise RuntimeError("existing null output source fingerprint changed before guard backfill")
        source = json.loads((RESULTS / "affect_detail.json").read_text())
        cohort = build_cohort(source, load_rooms())
        if prior.get("cohort", {}).get("trial_ids") != list(cohort.ids):
            raise RuntimeError("existing null output trial identities differ from effective cohort")
        expected = json.loads(json.dumps(evaluate_outer(cohort.X, cohort.raw, cohort.reports,
                                                        cohort.room_groups), allow_nan=False))
        if prior.get("observed", {}).get("folds") != expected:
            raise RuntimeError("existing null observed folds differ from rebuilt effective cohort")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(current, indent=2, allow_nan=False) + "\n")
    return current
