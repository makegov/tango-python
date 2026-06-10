#!/usr/bin/env python3
"""
Refresh the vendored API filter/shape contract.

The SDK conformance check (scripts/check_filter_shape_conformance.py) runs
against a vendored copy of the canonical contract at
contracts/filter_shape_contract.json. This script updates that copy from the
tango repo — a local sibling checkout when available, otherwise the GitHub API
(requires `gh` authenticated with access to makegov/tango).

Usage:
    uv run python scripts/refresh_contract.py                  # sibling, then gh fallback
    uv run python scripts/refresh_contract.py --source /path/to/filter_shape_contract.json
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
VENDORED_PATH = REPO_ROOT / "contracts" / "filter_shape_contract.json"
SIBLING_PATH = REPO_ROOT.parent / "tango" / "contracts" / "filter_shape_contract.json"
GH_CONTENTS_PATH = "/repos/makegov/tango/contents/contracts/filter_shape_contract.json"


def fetch_from_github() -> str:
    result = subprocess.run(
        [
            "gh",
            "api",
            "-H",
            "Accept: application/vnd.github.raw",
            GH_CONTENTS_PATH,
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


def main() -> int:
    parser = argparse.ArgumentParser(description="Refresh vendored API contract")
    parser.add_argument(
        "--source",
        help=(
            "Path to a filter_shape_contract.json to vendor. Defaults to the "
            f"sibling checkout ({SIBLING_PATH}), falling back to the GitHub API."
        ),
    )
    args = parser.parse_args()

    if args.source:
        source = Path(args.source)
        if not source.exists():
            print(f"Source not found: {source}", file=sys.stderr)
            return 2
        content = source.read_text(encoding="utf-8")
        origin = str(source)
    elif SIBLING_PATH.exists():
        content = SIBLING_PATH.read_text(encoding="utf-8")
        origin = str(SIBLING_PATH)
    else:
        try:
            content = fetch_from_github()
            origin = f"gh api {GH_CONTENTS_PATH}"
        except (OSError, subprocess.CalledProcessError) as exc:
            print(f"No sibling checkout and GitHub fetch failed: {exc}", file=sys.stderr)
            return 2

    manifest = json.loads(content)
    meta = manifest.get("meta", {})
    changed = not VENDORED_PATH.exists() or VENDORED_PATH.read_text(encoding="utf-8") != content
    VENDORED_PATH.parent.mkdir(parents=True, exist_ok=True)
    VENDORED_PATH.write_text(content, encoding="utf-8")

    print(
        json.dumps(
            {
                "vendored": str(VENDORED_PATH.relative_to(REPO_ROOT)),
                "source": origin,
                "schema_version": meta.get("schema_version", 1),
                "resources": len(manifest.get("resources", {})),
                "changed": changed,
            },
            indent=2,
        )
    )
    if changed:
        print(
            "Contract changed — run `uv run python scripts/check_filter_shape_conformance.py` "
            "and commit the updated contract with any SDK changes.",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
