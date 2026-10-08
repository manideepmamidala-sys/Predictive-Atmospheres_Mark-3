"""Compare two regenerated source snapshots without assuming matching Git commits."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

ABS_TOL = 1e-8
REL_TOL = 1e-8


def compare(left: object, right: object, path: str, differences: list[str]) -> None:
    if type(left) is not type(right):
        differences.append(f"{path}: type {type(left).__name__} != {type(right).__name__}")
    elif isinstance(left, dict):
        if left.keys() != right.keys():
            differences.append(f"{path}: keys differ")
        for key in left.keys() & right.keys():
            compare(left[key], right[key], f"{path}.{key}", differences)
    elif isinstance(left, list):
        if len(left) != len(right):
            differences.append(f"{path}: lengths {len(left)} != {len(right)}")
        for index, (left_item, right_item) in enumerate(zip(left, right)):
            compare(left_item, right_item, f"{path}[{index}]", differences)
    elif isinstance(left, float):
        if not (math.isfinite(left) and math.isfinite(right) and
                math.isclose(left, right, abs_tol=ABS_TOL, rel_tol=REL_TOL)):
            differences.append(f"{path}: {left} != {right}")
    elif left != right:
        differences.append(f"{path}: values differ")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reference", type=Path)
    parser.add_argument("reproduction", type=Path)
    args = parser.parse_args()
    source_names = sorted(path.name for path in (args.reference / "artifacts/results").glob("*.json"))
    reproduced_names = sorted(path.name for path in (args.reproduction / "artifacts/results").glob("*.json"))
    if source_names != reproduced_names:
        raise SystemExit("Result JSON product sets differ")
    differences: list[str] = []
    for name in source_names:
        left = json.loads((args.reference / "artifacts/results" / name).read_text())
        right = json.loads((args.reproduction / "artifacts/results" / name).read_text())
        compare(left, right, name, differences)
    reference_metadata = json.loads((args.reference / "artifacts/model/metadata.json").read_text())
    reproduced_metadata = json.loads((args.reproduction / "artifacts/model/metadata.json").read_text())
    for item in (reference_metadata, reproduced_metadata):
        for key in ("base_git_revision", "source_snapshot_status", "model_sha256"):
            item.pop(key, None)
    compare(reference_metadata, reproduced_metadata, "model metadata", differences)
    if differences:
        print("\n".join(differences[:30]))
        raise SystemExit(f"{len(differences)} differences exceed abs/rel tolerance {ABS_TOL}")
    print(f"Matched {len(source_names)} JSON products and model metadata at abs/rel tolerance {ABS_TOL}")


if __name__ == "__main__":
    main()
