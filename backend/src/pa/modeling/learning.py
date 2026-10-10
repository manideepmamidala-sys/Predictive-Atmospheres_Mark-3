"""Execute the fixed unique-subset room learning curve as a durable artifact."""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

from pa.config import RESULTS, ROOT
from pa.io.checkpoint import require_science_checkpoint
from pa.io.metadata import load_rooms
from pa.modeling.evaluate import room_learning_curve
from pa.modeling.train import build_cohort

FINAL = RESULTS / "model_learning_curve.json"


def write_learning_curve() -> dict:
    require_science_checkpoint()
    source_path = RESULTS / "affect_detail.json"
    source = json.loads(source_path.read_text())
    cohort = build_cohort(source, load_rooms())
    started = time.monotonic()
    result = room_learning_curve(cohort.X, cohort.raw, cohort.reports, cohort.room_groups)
    observed = sum(len(point["subsets"]) for point in result["points"])
    expected = 455 if len(set(cohort.room_groups)) == 10 else None
    if expected is not None and observed != expected:
        raise ValueError(f"learning curve generated {observed}, expected {expected} unique subsets")
    output = {"schema_version": "1.0.0", "method_version": source["method_version"],
              "approved_spec_sha256": source["approved_spec_sha256"],
              "cohort_ids": list(cohort.ids),
              "source_fingerprint": {
                  "affect_detail_sha256": hashlib.sha256(source_path.read_bytes()).hexdigest(),
                  "approved_spec_sha256": source["approved_spec_sha256"],
                  "decisions_sha256": hashlib.sha256((ROOT / "backend/src/pa/decisions.yaml").read_bytes()).hexdigest(),
              }, "elapsed_wall_seconds": time.monotonic()-started, **result}
    FINAL.parent.mkdir(parents=True, exist_ok=True)
    temp = Path(str(FINAL) + ".tmp")
    temp.write_text(json.dumps(output, indent=2, allow_nan=False) + "\n")
    temp.replace(FINAL)
    print(f"Learning curve complete: {observed} unique subsets in {output['elapsed_wall_seconds']:.1f}s.",
          flush=True)
    return output


if __name__ == "__main__":
    write_learning_curve()
