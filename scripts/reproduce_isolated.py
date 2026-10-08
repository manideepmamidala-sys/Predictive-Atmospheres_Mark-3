"""Build a temporary source-only Git snapshot, clone it, and run the full workflow.

This never commits or modifies the project repository. The temporary snapshot
contains the intended current source bytes, including presently uncommitted
implementation, so its commit is not confused with the project's old HEAD.
"""

from __future__ import annotations

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


def run(command: list[str], *, cwd: Path | None = None,
        output: object | None = None, timeout: int = 300) -> subprocess.CompletedProcess:
    return subprocess.run(command, cwd=cwd, check=True, text=True, stdout=output,
                          stderr=subprocess.STDOUT if output else None, timeout=timeout)


def main() -> None:
    work = Path(tempfile.mkdtemp(prefix="pa-repro-"))
    source = work / "source-snapshot"
    clone = work / "clean-clone"
    log = work / "make-all.log"
    source.mkdir()
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
    print("Fresh clone clean; running `make all` without model/results/processed caches", flush=True)
    started = time.monotonic()
    try:
        with log.open("a") as handle:
            run(["make", "all"], cwd=clone, output=handle, timeout=1800)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        print(f"Reproduction failed; inspect {log}", flush=True)
        raise
    elapsed = time.monotonic() - started
    print(f"`make all` passed in {elapsed:.1f} seconds", flush=True)
    run([sys.executable, str(ROOT / "scripts/compare_reproduction.py"), str(ROOT),
         str(clone)], timeout=300)
    print(f"Verified clone: {clone}", flush=True)
    print(f"Full command log: {log}", flush=True)


if __name__ == "__main__":
    main()
