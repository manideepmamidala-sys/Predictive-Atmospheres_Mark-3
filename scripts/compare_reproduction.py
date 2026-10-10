"""Compare reference and regenerated research artifacts across Git snapshots."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

ABS_TOL = 1e-8
REL_TOL = 1e-8
# These describe the checkout that performed the run, not the scientific result.
VOLATILE_REVISION_FIELDS = ("base_git_revision", "source_snapshot_status")
CATALOGUE_DIR = Path("artifacts/results/analysis")
NULL_RESULT = Path("artifacts/results/model_null.json")
NULL_CHECKPOINT = Path("artifacts/results/model_null_checkpoint.json")
LEARNING_CURVE_RESULT = Path("artifacts/results/model_learning_curve.json")
CATALOGUE_INDEX = CATALOGUE_DIR / "index.json"
NULL_INPUT = Path("artifacts/results/model_null_input.json")
REVIEW_LEDGER = Path("artifacts/results/qc_review.json")
NULL_TIMING_FIELDS = ("started_at_utc", "updated_at_utc", "completed_at_utc",
                      "elapsed_wall_seconds")


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


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def result_paths(root: Path) -> set[Path]:
    return {path.relative_to(root) for path in (root / "artifacts/results").rglob("*.json")
            if path.relative_to(root) != NULL_CHECKPOINT}


def full_spatial_null(product: object) -> bool:
    if not isinstance(product, dict) or product.get("status") != "complete" or \
            product.get("requested_draws") != 1000:
        return False
    draws = product.get("draws")
    values = product.get("null_mean_mae")
    if not isinstance(draws, dict) or set(draws) != {str(i) for i in range(1000)} or \
            not isinstance(values, list) or len(values) != 1000:
        return False
    return all(isinstance(draws[str(i)], dict) and draws[str(i)].get("draw") == i and
               draws[str(i)].get("status") == "evaluated" for i in range(1000))


def full_learning_curve(product: object) -> bool:
    expected = {4: 100, 5: 100, 6: 100, 7: 100, 8: 45, 9: 10}
    if not isinstance(product, dict) or not isinstance(product.get("points"), list) or \
            len(product["points"]) != len(expected):
        return False
    seen: set[int] = set()
    for point in product["points"]:
        if not isinstance(point, dict):
            return False
        count = point.get("training_room_count")
        subsets = point.get("subsets")
        if not isinstance(count, int) or count in seen or count not in expected or \
                not isinstance(subsets, list) or \
                len(subsets) != expected[count]:
            return False
        seen.add(count)
        room_sets = [tuple(sorted(item["training_rooms"]))
                     for item in subsets if isinstance(item, dict) and
                     isinstance(item.get("training_rooms"), list) and
                     len(item["training_rooms"]) == count and
                     all(isinstance(room, str) for room in item["training_rooms"])]
        if len(room_sets) != len(subsets) or len(set(room_sets)) != len(subsets):
            return False
    return seen == set(expected)


def normalized_product(path: Path, product: object) -> object:
    """Remove only known checkout/time provenance, never statistical content."""
    if path.parent == CATALOGUE_DIR and path.name != "index.json":
        if not isinstance(product, dict) or not isinstance(product.get("provenance"), dict):
            return product
        product["provenance"].pop("generated_at_utc", None)
    if path == NULL_RESULT and isinstance(product, dict):
        for key in NULL_TIMING_FIELDS:
            product.pop(key, None)
    if path == LEARNING_CURVE_RESULT and isinstance(product, dict):
        product.pop("elapsed_wall_seconds", None)
    return product


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reference", type=Path)
    parser.add_argument("reproduction", type=Path)
    args = parser.parse_args()
    source_names = result_paths(args.reference)
    reproduced_names = result_paths(args.reproduction)
    if not source_names or source_names != reproduced_names:
        missing = sorted(str(path) for path in source_names - reproduced_names)
        extra = sorted(str(path) for path in reproduced_names - source_names)
        raise SystemExit(f"Result JSON product sets are empty or differ; missing={missing}, extra={extra}")
    reference_metadata = json.loads((args.reference / "artifacts/model/metadata.json").read_text())
    reproduced_metadata = json.loads((args.reproduction / "artifacts/model/metadata.json").read_text())
    is_v12 = bool(reference_metadata.get("approved_spec_sha256"))
    differences: list[str] = []
    for name in sorted(source_names):
        left = normalized_product(name, json.loads((args.reference / name).read_text()))
        right = normalized_product(name, json.loads((args.reproduction / name).read_text()))
        for label, product in (("reference", left), ("reproduction", right)):
            if not is_v12:
                continue
            if name == NULL_RESULT and not full_spatial_null(product):
                differences.append(f"{label}: spatial null lacks the 1000 prescribed draws")
            if name == LEARNING_CURVE_RESULT and not full_learning_curve(product):
                differences.append(f"{label}: learning curve lacks the 455 room subsets")
            if name == CATALOGUE_INDEX and (not isinstance(product, dict) or
                                            not isinstance(product.get("products"), list) or
                                            len(product["products"]) != 28):
                differences.append(f"{label}: analysis catalogue lacks 28 cards")
            if name == REVIEW_LEDGER and (not isinstance(product, dict) or
                                          product.get("eligibility_integrated") is not True):
                differences.append(f"{label}: CP-B review ledger is not integrated")
        compare(left, right, str(name), differences)
    for item in (reference_metadata, reproduced_metadata):
        for key in VOLATILE_REVISION_FIELDS:
            item.pop(key, None)
    if is_v12:
        required = {NULL_RESULT, NULL_INPUT, LEARNING_CURVE_RESULT,
                    CATALOGUE_INDEX, REVIEW_LEDGER}
        for name in sorted(required - source_names):
            differences.append(f"v1.2 reference product missing: {name}")
    compare(reference_metadata, reproduced_metadata, "model metadata", differences)
    for root, metadata, label in ((args.reference, reference_metadata, "reference"),
                                  (args.reproduction, reproduced_metadata, "reproduction")):
        model_path = root / "artifacts/model/model.joblib"
        if not model_path.is_file():
            differences.append(f"{label}: model.joblib is missing")
        elif metadata.get("model_sha256") != sha256(model_path):
            differences.append(f"{label}: model_sha256 does not match model.joblib")
    if differences:
        print("\n".join(differences[:30]))
        raise SystemExit(f"{len(differences)} artifact differences found "
                         f"(numeric abs/rel tolerance {ABS_TOL})")
    print(f"Matched {len(source_names)} JSON products (including nested catalogue), model metadata and model bytes "
          f"at abs/rel tolerance {ABS_TOL}")


if __name__ == "__main__":
    main()
