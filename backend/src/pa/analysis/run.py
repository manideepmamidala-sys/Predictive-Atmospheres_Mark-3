"""Execute prespecified research analyses from reviewed source products."""

from __future__ import annotations

import json
from pathlib import Path

from pa.analysis.ratings import crossed_additive, rater_partitions
from pa.analysis.transfer import evaluate_relative_transfer
from pa.config import RESULTS
from pa.io.checkpoint import require_science_checkpoint


def rating_rows(affect_detail: dict, experiment: int, axis: str) -> list[dict]:
    if experiment not in (1, 2, 3) or axis not in ("valence", "arousal", "comfort"):
        raise ValueError("unsupported experiment or rating axis")
    if (experiment == 1) != (axis == "comfort"):
        raise ValueError("E1 comfort and E2/E3 affect must remain separate")
    rows = []
    for trial in affect_detail["trials"]:
        if trial["experiment"] != experiment:
            continue
        value = trial["comfort"] if axis == "comfort" else trial["subjective"][axis]
        if value is not None:
            rows.append({"trial_id": trial["id"], "participant_id": trial["participant_id"],
                         "room_id": trial["room_id"], "value": value})
    return rows


def rating_research(affect_detail: dict) -> dict:
    analyses = []
    for experiment, axes in ((1, ("comfort",)), (2, ("valence", "arousal")),
                             (3, ("valence", "arousal"))):
        for axis in axes:
            rows = rating_rows(affect_detail, experiment, axis)
            analyses.append({"experiment": experiment, "axis": axis,
                             "source_rows": rows, "crossed_additive": crossed_additive(rows),
                             "rater_partitions": rater_partitions(rows) if experiment > 1 else
                             {"status": "unavailable_not_prespecified_for_E1"},
                             "known_room_relative_transfer": evaluate_relative_transfer(rows)
                             if experiment > 1 else
                             {"status": "unavailable_not_prespecified_for_E1"}})
    return {"schema_version": "1.0.0", "method_version": affect_detail["method_version"],
            "approved_spec_sha256": affect_detail["approved_spec_sha256"],
            "analyses": analyses, "pooling": "none_across_experiments",
            "null_interpretation": "Descriptive negative controls on the observed pilot; not population p-values."}


def write_rating_research(affect_path: Path = RESULTS / "affect_detail.json",
                          destination: Path = RESULTS / "rating_research.json") -> dict:
    require_science_checkpoint()
    result = rating_research(json.loads(affect_path.read_text()))
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    return result
