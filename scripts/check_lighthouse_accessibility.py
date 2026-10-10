"""Measure the eight atlas routes with pinned Lighthouse and retain JSON evidence.

Start the built site with ``cd frontend && corepack pnpm preview --port 4175``.
Set CHROME_PATH to a local Chromium binary; install host libraries as needed.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import tempfile
from pathlib import Path
from urllib.parse import urljoin

ROUTES = {
    "landing": "/",
    "study": "/study",
    "rooms": "/rooms",
    "body": "/body",
    "prediction": "/prediction",
    "studio": "/studio",
    "explore": "/explore",
    "methods": "/methods",
}
LIGHTHOUSE_VERSION = "13.5.0"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:4175/")
    parser.add_argument("--output-dir", type=Path, default=Path(
        "docs/reports/revision-2026-10/lighthouse"))
    parser.add_argument("--minimum", type=int, default=95)
    args = parser.parse_args()
    if not os.environ.get("CHROME_PATH"):
        parser.error("CHROME_PATH must name the Chromium binary used for Lighthouse")
    args.output_dir = args.output_dir.resolve()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    scores = []
    with tempfile.TemporaryDirectory(prefix="pa-lighthouse-") as working_directory:
        for name, route in ROUTES.items():
            output = args.output_dir / f"{name}.json"
            url = urljoin(args.base_url.rstrip("/") + "/", route.lstrip("/"))
            subprocess.run([
                "npm", "exec", "--yes", f"--package=lighthouse@{LIGHTHOUSE_VERSION}",
                "--", "lighthouse", url, "--only-categories=accessibility",
                "--output=json", f"--output-path={output}",
                "--chrome-flags=--headless --no-sandbox --disable-dev-shm-usage", "--quiet",
            ], cwd=working_directory, check=True)
            result = json.loads(output.read_text())
            accessibility = result["categories"]["accessibility"]
            score = accessibility["score"] * 100
            failed = [item["id"] for item in accessibility["auditRefs"]
                      if item.get("weight", 0) > 0 and
                      result["audits"][item["id"]].get("score") not in (None, 1)]
            scores.append({"route": route, "score": score, "fetch_time": result["fetchTime"],
                           "lighthouse_version": result["lighthouseVersion"],
                           "failed_audits": failed, "report": output.name})
            print(f"{route}: accessibility {score:.2f}, failed audits {failed}", flush=True)
    (args.output_dir / "scores.json").write_text(json.dumps({
        "minimum": args.minimum, "base_url": args.base_url, "routes": scores,
    }, indent=2) + "\n")
    below = [item for item in scores if item["score"] < args.minimum]
    if below:
        raise SystemExit(f"{len(below)} route(s) below Lighthouse accessibility {args.minimum}")


if __name__ == "__main__":
    main()
