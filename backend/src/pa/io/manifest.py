"""Verify inventoried originals and byte-identical migrations without rewriting hashes."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from pa.config import ROOT

INVENTORY = ROOT / "data/source-inventory.json"
SHA_MANIFEST = ROOT / "data/MANIFEST.sha256"


@dataclass(frozen=True)
class Discrepancy:
    path: str
    reason: str


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_sources(inventory_path: Path = INVENTORY,
                   manifest_path: Path = SHA_MANIFEST) -> list[Discrepancy]:
    inventory = json.loads(inventory_path.read_text())
    errors: list[Discrepancy] = []
    expected = {entry.get("path", entry.get("source")): entry["sha256"]
                for entry in inventory["entries"]}
    if not manifest_path.is_file():
        errors.append(Discrepancy(str(manifest_path), "SHA manifest missing"))
    else:
        observed: dict[str, str] = {}
        for line in manifest_path.read_text().splitlines():
            digest, separator, path = line.partition("  ")
            if not separator or not path or path in observed:
                errors.append(Discrepancy(str(manifest_path), "malformed or duplicate SHA entry"))
                continue
            observed[path] = digest
        if observed != expected:
            errors.append(Discrepancy(str(manifest_path), "SHA manifest disagrees with inventory"))
    for entry in inventory["entries"]:
        entry_path = entry.get("path", entry.get("source"))
        source = ROOT / entry_path
        destination = ROOT / entry["destination"] if entry.get("destination") else None
        paths = [source]
        if destination is not None:
            paths.append(destination)
        found = [path for path in paths if path.is_file()]
        if not found:
            errors.append(Discrepancy(entry_path, "missing source and migration destination"))
            continue
        for path in found:
            relative = path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else path.as_posix()
            if path.stat().st_size != entry["size_bytes"]:
                errors.append(Discrepancy(relative, "size mismatch"))
            elif sha256(path) != entry["sha256"]:
                errors.append(Discrepancy(relative, "sha256 mismatch"))
    return errors
