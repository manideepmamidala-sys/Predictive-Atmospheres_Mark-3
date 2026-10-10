"""Resumable full-refit spatial negative controls on fixed E3 room folds."""

from __future__ import annotations

import hashlib
import json
import os
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import UTC, datetime
from pathlib import Path

from pa.config import RESULTS, ROOT
from pa.io.checkpoint import require_science_checkpoint
from pa.io.metadata import load_rooms
from pa.modeling.evaluate import evaluate_outer, spatial_permutation_draw
from pa.modeling.train import Cohort, build_cohort

SEED = 2718
DRAWS = 1000
CHECKPOINT = RESULTS / "model_null_checkpoint.json"
FINAL = RESULTS / "model_null.json"
_WORKER_COHORT: Cohort | None = None


def _source_fingerprint() -> dict[str, str]:
    paths = [
        "docs/specs/analysis-v1.2-draft.md",
        "backend/src/pa/decisions.yaml",
        "backend/src/pa/features/builder.py",
        "backend/src/pa/modeling/targets.py",
        "backend/src/pa/modeling/splits.py",
        "backend/src/pa/modeling/evaluate.py",
        "backend/src/pa/modeling/nulls.py",
        "artifacts/results/affect_detail.json",
        "artifacts/results/qc_review.json",
        "data/MANIFEST.sha256",
    ]
    return {path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest() for path in paths}


def _write_atomic(path: Path, product: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(product, indent=2, allow_nan=False) + "\n")
    temp.replace(path)


def _init_worker(cohort: Cohort) -> None:
    global _WORKER_COHORT
    _WORKER_COHORT = cohort


def _run_draw(draw: int) -> dict:
    assert _WORKER_COHORT is not None
    c = _WORKER_COHORT
    return spatial_permutation_draw(c.X, c.raw, c.reports, c.room_groups,
                                    draw=draw, seed=SEED)


def _validate_existing(product: dict, fingerprint: dict[str, str]) -> None:
    if product.get("source_fingerprint") != fingerprint or \
            product.get("seed") != SEED or product.get("requested_draws") != DRAWS:
        raise RuntimeError("spatial null checkpoint source/settings mismatch; preserve for audit")
    results = product.get("draws", {})
    if not isinstance(results, dict) or any(int(key) < 0 or int(key) >= DRAWS or
                                            value.get("draw") != int(key) or
                                            value.get("seed") != SEED
                                            for key, value in results.items()):
        raise RuntimeError("spatial null checkpoint has invalid draw identities")


def run_full_spatial_null(*, workers: int | None = None) -> dict:
    require_science_checkpoint()
    fingerprint = _source_fingerprint()
    if FINAL.exists():
        final = json.loads(FINAL.read_text())
        _validate_existing(final, fingerprint)
        if len(final["draws"]) == DRAWS and final.get("status") == "complete":
            print("Spatial null: verified exact complete artifact; no refits needed.", flush=True)
            return final
    cohort = build_cohort(json.loads((RESULTS / "affect_detail.json").read_text()), load_rooms())
    if CHECKPOINT.exists():
        product = json.loads(CHECKPOINT.read_text())
        _validate_existing(product, fingerprint)
    else:
        observed_folds = evaluate_outer(cohort.X, cohort.raw, cohort.reports, cohort.room_groups)
        scores = [fold["mean_mae"] for fold in observed_folds if fold["status"] == "evaluated"]
        product = {"schema_version": "1.0.0", "method_version": "1.2.0",
                   "status": "in_progress", "seed": SEED, "requested_draws": DRAWS,
                   "source_fingerprint": fingerprint,
                   "cohort": {"rows": len(cohort.ids), "rooms": len(set(cohort.room_groups)),
                              "participants": len(set(cohort.subject_groups)),
                              "trial_ids": list(cohort.ids)},
                   "observed": {"folds": observed_folds,
                                "mean_mae": sum(scores) / len(scores) if len(scores) == len(observed_folds)
                                and scores else None},
                   "draws": {}, "started_at_utc": datetime.now(UTC).isoformat(),
                   "elapsed_wall_seconds": 0.0,
                   "interpretation": "descriptive training-room-attribute permutation; no calibrated population p-value"}
        _write_atomic(CHECKPOINT, product)
    missing = [draw for draw in range(DRAWS) if str(draw) not in product["draws"]]
    worker_count = workers or min(8, max(1, (os.cpu_count() or 2) - 2))
    print(f"Spatial null: {len(product['draws'])}/{DRAWS} complete; "
          f"running {len(missing)} exact full-refit draws with {worker_count} workers.", flush=True)
    started = time.monotonic()
    with ProcessPoolExecutor(max_workers=worker_count, initializer=_init_worker,
                             initargs=(cohort,)) as executor:
        futures = {executor.submit(_run_draw, draw): draw for draw in missing}
        for future in as_completed(futures):
            draw = futures[future]
            product["draws"][str(draw)] = future.result()
            completed = len(product["draws"])
            if completed % 10 == 0 or completed == DRAWS:
                product["updated_at_utc"] = datetime.now(UTC).isoformat()
                product["elapsed_wall_seconds"] += time.monotonic() - started
                started = time.monotonic()
                _write_atomic(CHECKPOINT, product)
                print(f"Spatial null: {completed}/{DRAWS} draws complete; "
                      f"elapsed {product['elapsed_wall_seconds']:.1f}s.", flush=True)
    if len(product["draws"]) != DRAWS:
        raise RuntimeError("spatial null terminated before all prescribed draws")
    ordered = [product["draws"][str(draw)] for draw in range(DRAWS)]
    if any(item["status"] != "evaluated" for item in ordered):
        product["status"] = "unavailable_some_draws"
        product["unavailable_draws"] = [item["draw"] for item in ordered
                                         if item["status"] != "evaluated"]
    else:
        product["status"] = "complete"
        product["null_mean_mae"] = [item["mean_mae"] for item in ordered]
    product["completed_at_utc"] = datetime.now(UTC).isoformat()
    _write_atomic(FINAL, product)
    return product


if __name__ == "__main__":
    run_full_spatial_null()
