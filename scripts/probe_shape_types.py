#!/usr/bin/env python3
"""Sample the live Tango API to derive ground-truth shape types.

The vendored contract gives shape field NAMES + nesting but no types or list-ness.
This samples real records per resource — requesting the full shape from the
contract tree — and observes the actual JSON to derive, per dotted shape path:
py_type (str/int/Decimal/date/datetime/bool), is_list, is_optional, and whether a
node is a {code,description} code-object or a nested object.

Writes contracts/observed_shape_types.json, the vendored input to
scripts/generate_shape_overlay.py. Maintainer-run (needs TANGO_API_KEY, like
scripts/refresh_contract.py); regenerating the overlay itself needs no key.

Requests split per top-level expand (short URLs, isolates 400s) and prune
unknown-field paths on 400 then retry.

Run: TANGO_API_KEY=... uv run python scripts/probe_shape_types.py
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path

import httpx

REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACT = REPO_ROOT / "contracts" / "filter_shape_contract.json"
OUT = REPO_ROOT / "contracts" / "observed_shape_types.json"
SAMPLE = 40

try:
    from dotenv import load_dotenv

    load_dotenv(REPO_ROOT / ".env")
except ImportError:
    pass

KEY = os.getenv("TANGO_API_KEY")
BASE = os.getenv("TANGO_BASE_URL", "https://tango.makegov.com")
if not KEY:
    print("error: TANGO_API_KEY not set", file=sys.stderr)
    raise SystemExit(2)
H = {"X-API-KEY": KEY}

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
DT_RE = re.compile(r"^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}")
INT_RE = re.compile(r"^-?\d+$")
DEC_RE = re.compile(r"^-?\d+\.\d+$")


def build_shape(node: dict) -> str:
    parts = [f for f in (node.get("fields") or []) if f != "*"]
    for name, child in (node.get("expands") or {}).items():
        sub = build_shape(child)
        parts.append(f"{name}({sub})" if sub else name)
    return ",".join(parts)


def scalar_kind(v):
    if isinstance(v, bool):
        return "bool"
    if isinstance(v, int):
        return "int"
    if isinstance(v, float):
        return "Decimal"
    if isinstance(v, str):
        if DATE_RE.match(v):
            return "date"
        if DT_RE.match(v):
            return "datetime"
        if DEC_RE.match(v):
            return "Decimal"
        if INT_RE.match(v) and len(v) <= 9:
            return "int"
        return "str"
    return None


def observe(value, node, path, obs):
    rec = obs.setdefault(path, {"kinds": set(), "list": False, "nonnull": False, "dictkeys": set()})
    if value is None:
        return
    rec["nonnull"] = True
    if isinstance(value, list):
        rec["list"] = True
        for item in value:
            observe(item, node, path, obs)
        return
    if isinstance(value, dict):
        rec["dictkeys"].update(value.keys())
        expands = (node or {}).get("expands") or {}
        for k, v in value.items():
            observe(v, expands.get(k, {}), f"{path}.{k}" if path else k, obs)
        return
    k = scalar_kind(value)
    if k:
        rec["kinds"].add(k)


def fetch(res_path, shape, prune_rounds=4):
    params = {"shape": shape, "limit": SAMPLE}
    for _ in range(prune_rounds):
        r = httpx.get(f"{BASE}/api/{res_path}/", headers=H, params=params, timeout=60)
        if r.status_code == 200:
            d = r.json()
            return d.get("results", d if isinstance(d, list) else [])
        if r.status_code == 400:
            try:
                issues = r.json().get("issues", [])
            except Exception:
                return []
            bad = {i.get("path") for i in issues if i.get("path")}
            if not bad:
                return []
            for b in bad:
                leaf = b.split(".")[-1]
                shape = re.sub(rf"(?<![\w]){re.escape(leaf)}(\([^)]*\))?", "", shape)
            params["shape"] = re.sub(r",{2,}", ",", shape).strip(",")
            continue
        return []
    return []


def derive(rec):
    if rec["dictkeys"] == {"code", "description"}:
        return {"kind": "code_object"}
    if rec["dictkeys"]:
        return {"kind": "object", "is_list": rec["list"], "is_optional": not rec["nonnull"]}
    for t in ["bool", "datetime", "date", "Decimal", "int", "str"]:
        if t in rec["kinds"]:
            return {"kind": "scalar", "type": t, "is_list": rec["list"], "is_optional": True}
    return {"kind": "scalar", "type": "str", "is_list": rec["list"], "is_optional": True}


def main() -> int:
    contract = json.loads(CONTRACT.read_text())
    out = {}
    for res, r in contract["resources"].items():
        shape_tree = (r.get("runtime") or {}).get("shape")
        if not shape_tree:
            continue
        obs: dict = {}
        root_fields = [f for f in (shape_tree.get("fields") or []) if f != "*"]
        chunks = [{"fields": root_fields, "expands": {}}] if root_fields else []
        for name, child in (shape_tree.get("expands") or {}).items():
            chunks.append({"fields": root_fields[:1], "expands": {name: child}})
        got = 0
        for ch in chunks:
            shape = build_shape(ch)
            if not shape:
                continue
            recs = fetch(res, shape)
            got += len(recs)
            for rec in recs:
                observe(rec, shape_tree, "", obs)
            time.sleep(0.15)
        out[res] = {"records_seen": got, "paths": {p: derive(v) for p, v in obs.items() if p}}
        print(f"{res:22} records={got:4} paths={len(out[res]['paths'])}", file=sys.stderr)
    OUT.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(f"\nwrote {OUT.relative_to(REPO_ROOT)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
