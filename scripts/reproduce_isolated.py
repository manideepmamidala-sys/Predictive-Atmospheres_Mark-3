"""Build a temporary source-only Git snapshot, clone it, and run the full workflow.

This never commits or modifies the project repository. The temporary snapshot
contains the intended current source bytes, including presently uncommitted
implementation, so its commit is not confused with the project's old HEAD.
The approved CP-B review ledger is reconstructed from the documented delegated
AI decisions. No model, result or reviewed ledger is copied into the clone.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCLUDES = (
    "/.git/", "/artifacts/", "/.fab-status.yaml", "**/.venv/", "**/node_modules/",
    "**/dist/", "**/__pycache__/", "**/.pytest_cache/", "**/.ruff_cache/",
    "**/playwright-report/", "**/test-results/", "/frontend/public/research/",
    "*.pyc", "*.tsbuildinfo", "*.Zone.Identifier",
)
REVIEW_LEDGER = Path("artifacts/results/qc_review.json")
SOURCE_DIRS = ("backend/src", "backend/tests", "frontend/src", "frontend/tests",
               "frontend/scripts", "frontend/public/images", "scripts")
SOURCE_FILES = ("Makefile", "backend/pyproject.toml", "backend/uv.lock",
                "frontend/package.json", "frontend/pnpm-lock.yaml",
                "frontend/vite.config.ts", "frontend/playwright.config.ts",
                "frontend/index.html", "frontend/vercel.json", "render.yaml",
                "data/MANIFEST.sha256", "data/source-inventory.json",
                "docs/specs/analysis-v1.2-draft.md",
                "docs/reports/revision-2026-10/CP-Spec.md",
                "docs/reports/revision-2026-10/CP-B.md",
                "docs/reports/revision-2026-10/cp-b-eeg-decisions.json",
                "docs/reports/revision-2026-10/cp-b-ecg-decisions.json")


def source_hashes(root: Path) -> dict[str, str]:
    """Track the exact code and approved review inputs throughout a long rebuild."""
    paths = [root / name for name in SOURCE_FILES]
    for directory in SOURCE_DIRS:
        paths.extend(path for path in (root / directory).rglob("*") if path.is_file() and
                     "__pycache__" not in path.parts and not path.name.endswith(
                         (".pyc", ".tsbuildinfo", ".check.d.ts")))
    return {path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(set(paths))}


def source_digest(hashes: dict[str, str]) -> str:
    return hashlib.sha256(json.dumps(hashes, sort_keys=True).encode()).hexdigest()


def run(command: list[str], *, cwd: Path | None = None,
        output: object | None = None, timeout: int = 300) -> subprocess.CompletedProcess:
    return subprocess.run(command, cwd=cwd, check=True, text=True, stdout=output,
                          stderr=subprocess.STDOUT if output else None, timeout=timeout)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workdir", type=Path,
                        help="Keep the isolated snapshot, clone and command log here")
    parser.add_argument("--timeout", type=int, default=14400,
                        help="Maximum seconds for the full make workflow (default: 14400)")
    args = parser.parse_args()
    work = args.workdir.resolve() if args.workdir else Path(tempfile.mkdtemp(prefix="pa-repro-"))
    work.mkdir(parents=True, exist_ok=True)
    source = work / "source-snapshot"
    clone = work / "clean-clone"
    log = work / "make-all.log"
    source.mkdir(exist_ok=False)
    print(f"Temporary isolated workspace: {work}", flush=True)
    run(["rsync", "-a", *(f"--exclude={item}" for item in EXCLUDES),
         f"{ROOT}/", f"{source}/"], timeout=300)
    run(["git", "init", "-q"], cwd=source)
    run(["git", "add", "-A"], cwd=source, timeout=300)
    with log.open("w") as handle:
        run(["git", "-c", "user.name=Local reproduction", "-c",
             "user.email=local-reproduction@example.invalid", "commit", "-qm",
             "Temporary source snapshot for isolated reproduction"], cwd=source,
            output=handle, timeout=300)
    snapshot = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=source,
                                       text=True).strip()
    print(f"Temporary source snapshot commit: {snapshot}", flush=True)
    run(["git", "clone", "--quiet", "--no-hardlinks", str(source), str(clone)], timeout=300)
    status = subprocess.check_output(["git", "status", "--porcelain"], cwd=clone,
                                     text=True).strip()
    if status:
        raise RuntimeError(f"new clone was not clean: {status}")
    snapshot_hashes = source_hashes(source)
    current_hashes = source_hashes(ROOT)
    if snapshot_hashes != current_hashes:
        raise RuntimeError("source inputs changed while the temporary snapshot was copied")
    source_record = {"snapshot_commit": snapshot, "source_sha256": source_digest(snapshot_hashes),
                     "paths": snapshot_hashes}
    (work / "source-inputs.json").write_text(json.dumps(source_record, indent=2) + "\n")
    print(f"Source inputs: {len(snapshot_hashes)} files, sha256={source_record['source_sha256']}",
          flush=True)
    ledger = ROOT / REVIEW_LEDGER
    if not ledger.is_file():
        raise FileNotFoundError(f"Approved CP-B review ledger missing: {ledger}")
    digest = hashlib.sha256(ledger.read_bytes()).hexdigest()
    print(f"Fresh clone clean; reconstructing delegated CP-B review sha256={digest}", flush=True)
    try:
        with log.open("a") as handle:
            run(["make", "setup"], cwd=clone, output=handle, timeout=1800)
            run(["uv", "run", "--frozen", "python", "../scripts/rebuild_review_ledger.py",
                 "--expected-sha256", digest], cwd=clone / "backend", output=handle,
                timeout=3600)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        print(f"CP-B source reconstruction failed; inspect {log}", flush=True)
        raise
    print("Approved CP-B decisions reconstructed byte-for-byte; running `make all` "
          "without model or downstream result caches", flush=True)
    started = time.monotonic()
    try:
        with log.open("a") as handle:
            run(["make", "all"], cwd=clone, output=handle, timeout=args.timeout)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        print(f"Reproduction failed; inspect {log}", flush=True)
        raise
    elapsed = time.monotonic() - started
    print(f"`make all` passed in {elapsed:.1f} seconds", flush=True)
    current_hashes = source_hashes(ROOT)
    if snapshot_hashes != current_hashes:
        changed = sorted(name for name in snapshot_hashes.keys() | current_hashes.keys()
                         if snapshot_hashes.get(name) != current_hashes.get(name))
        raise RuntimeError(f"source inputs changed during isolated rebuild: {changed[:20]}")
    run([sys.executable, str(ROOT / "scripts/compare_reproduction.py"), str(ROOT),
         str(clone)], timeout=300)
    print(f"Verified clone: {clone}", flush=True)
    print(f"Full command log: {log}", flush=True)


if __name__ == "__main__":
    main()
