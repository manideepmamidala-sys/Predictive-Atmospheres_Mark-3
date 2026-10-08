"""Write validated, source-traceable browser products and one deployment bundle."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from pydantic import BaseModel

from pa.config import RESULTS, ROOT, SCHEMA_VERSION
from pa.results.schemas import (
    AffectExport,
    ModelExport,
    PeopleExport,
    ResearchBundle,
    RoomsExport,
    SignalsExport,
    StudyExport,
)

PRODUCT_TYPES = {
    "study": StudyExport, "rooms": RoomsExport, "signals": SignalsExport,
    "affect": AffectExport, "people": PeopleExport, "model": ModelExport,
}


def write_json(path: Path, product: BaseModel) -> str:
    encoded = json.dumps(product.model_dump(mode="json", exclude_none=False),
                         indent=2, allow_nan=False) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(encoded)
    return hashlib.sha256(encoded.encode()).hexdigest()


def write_products(products: dict[str, BaseModel], destination: Path = RESULTS) -> dict:
    if set(products) != set(PRODUCT_TYPES):
        raise ValueError("all six research product families are required")
    verified = {name: PRODUCT_TYPES[name].model_validate(product.model_dump(mode="json"))
                for name, product in products.items()}
    hashes = {name: write_json(destination / f"{name}.json", product)
              for name, product in verified.items()}
    bundle = ResearchBundle(
        provenance=verified["study"].provenance,
        study=verified["study"].study, rooms=verified["rooms"].rooms,
        trials=[trial.model_copy(update={"eeg": None, "ecg": None})
                for trial in verified["signals"].trials],
        sensitivity=verified["affect"].sensitivity,
        people=verified["people"].people, model=verified["model"].model,
    )
    hashes["bundle"] = write_json(destination / "bundle.json", bundle)
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "products": {name: {"file": f"{name}.json", "sha256": digest}
                     for name, digest in hashes.items()},
        "source_manifest_sha256": hashlib.sha256((ROOT / "data/MANIFEST.sha256").read_bytes()).hexdigest(),
        "analysis_spec_sha256": hashlib.sha256((ROOT / "docs/specs/analysis-v1.md").read_bytes()).hexdigest(),
    }
    write_json(destination / "manifest.json", ManifestModel.model_validate(manifest))
    return manifest


class ManifestModel(BaseModel):
    schema_version: str
    products: dict[str, dict[str, str]]
    source_manifest_sha256: str
    analysis_spec_sha256: str
