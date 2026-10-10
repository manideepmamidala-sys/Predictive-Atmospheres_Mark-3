"""Build or check the path-stable inventory of retained original evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GROUPS = (
    ("recording", "data/raw"),
    ("metadata", "data/metadata"),
    ("room_render", "data/renders/raw"),
    ("legacy_site_asset", "docs/history/legacy-site-assets"),
)
INVENTORY = ROOT / "data/source-inventory.json"
MANIFEST = ROOT / "data/MANIFEST.sha256"


def digest(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            sha.update(chunk)
    return sha.hexdigest()


def build() -> tuple[str, str, list[dict]]:
    entries = []
    for role, directory in GROUPS:
        source = ROOT / directory
        for path in sorted(p for p in source.rglob("*") if p.is_file()):
            entries.append({"role": role, "path": path.relative_to(ROOT).as_posix(),
                            "size_bytes": path.stat().st_size, "sha256": digest(path)})
    inventory = json.dumps({"schema_version": "2.0.0", "entries": entries}, indent=2) + "\n"
    manifest = "".join(f"{entry['sha256']}  {entry['path']}\n" for entry in entries)
    return inventory, manifest, entries


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="compare retained sources with checked-in records")
    args = parser.parse_args()
    inventory, manifest, entries = build()
    if args.check:
        if not INVENTORY.is_file() or INVENTORY.read_text() != inventory:
            raise SystemExit("data/source-inventory.json differs from retained source bytes")
        if not MANIFEST.is_file() or MANIFEST.read_text() != manifest:
            raise SystemExit("data/MANIFEST.sha256 differs from retained source bytes")
    else:
        INVENTORY.write_text(inventory)
        MANIFEST.write_text(manifest)
    print(f"Verified {len(entries)} retained sources: " + ", ".join(
        f"{role}={sum(entry['role'] == role for entry in entries)}" for role, _ in GROUPS))


if __name__ == "__main__":
    main()
