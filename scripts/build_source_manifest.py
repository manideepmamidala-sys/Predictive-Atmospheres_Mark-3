"""Inventory supplied evidence before migration; never rewrite it during verification."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def digest(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            sha.update(chunk)
    return sha.hexdigest()


def main() -> None:
    groups = (
        ("recording", ROOT / "data/raw", None),
        ("metadata", ROOT / "data/metadata", None),
        ("room_render", ROOT / "rooms", ROOT / "data/renders/raw"),
        ("legacy_site_asset", ROOT / "frontend/assets/IMAGES", ROOT / "docs/history/legacy-site-assets"),
    )
    entries = []
    for role, source, destination in groups:
        for file in sorted(path for path in source.rglob("*") if path.is_file()):
            relative = file.relative_to(source)
            entries.append({
                "role": role,
                "source": file.relative_to(ROOT).as_posix(),
                "destination": (destination / relative).relative_to(ROOT).as_posix() if destination else None,
                "size_bytes": file.stat().st_size,
                "sha256": digest(file),
            })
    for name in ("ManideepMamidala_ThesisBooklet.pdf", "PredictiveAtmospheres_ManideepMamidala.pdf"):
        file = ROOT / name
        entries.append({
            "role": "thesis_pdf",
            "source": name,
            "destination": f"docs/thesis/{name}",
            "size_bytes": file.stat().st_size,
            "sha256": digest(file),
        })
    status = subprocess.check_output(["git", "status", "--porcelain=v1"], cwd=ROOT, text=True).splitlines()
    user_files = ("AGENTS.md", "EXECUTION_PLAN.md", "EXECUTION_PLAN.md:Zone.Identifier", "PROJECT_REPORT.md", "fab/.fab-version", "fab/.kit-migration-version", "fab/project/config.yaml")
    report = {
        "schema_version": "1.0.0",
        "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "branch": subprocess.check_output(["git", "branch", "--show-current"], cwd=ROOT, text=True).strip(),
        "initial_worktree_status": status,
        "existing_user_files": {name: digest(ROOT / name) for name in user_files if (ROOT / name).is_file()},
        "entries": entries,
    }
    report_path = ROOT / "docs/reports/migration-inventory.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2) + "\n")
    manifest_path = ROOT / "data/MANIFEST.sha256"
    manifest_path.write_text("".join(f"{entry['sha256']}  {entry['source']}\n" for entry in entries))
    print(f"Inventoried {len(entries)} source files by role: " + ", ".join(f"{role}={sum(e['role'] == role for e in entries)}" for role in sorted({e['role'] for e in entries})))


if __name__ == "__main__":
    main()
