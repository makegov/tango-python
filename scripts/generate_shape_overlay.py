#!/usr/bin/env python3
"""Generate tango/shapes/generated_overlay.py — the reverse shape-coverage overlay.

check_shape_coverage.py detects fields/expands Tango's shape trees expose that the
hand-curated tango/shapes/explicit_schemas.py does not capture. This generates the
schema additions that close every such gap, and SchemaRegistry merges the result
over the base so the SDK's typed shape API accepts everything the API returns.

Inputs (both vendored — regenerates with no network/API key):
  contracts/filter_shape_contract.json   Tango's shape trees (names + nesting).
  contracts/observed_shape_types.json    per-path types/list-ness sampled from the
                                          live API by scripts/probe_shape_types.py.

Reads the curated base directly from explicit_schemas.EXPLICIT_SCHEMAS — never
through SchemaRegistry, which auto-merges this overlay (that would feed the
generator its own output).

Type resolution per field: live-API observation -> structural equivalence
(vehicles.awardees mirror idvs, .orders mirror contracts) -> name heuristic.
{code,description} expands point at the shared "CodeDescription" schema; freeform
("*") expands stay plain dicts. Identical nested shapes are interned to one schema.

Run: uv run python scripts/generate_shape_overlay.py            # writes the module
     uv run python scripts/generate_shape_overlay.py --report   # print gaps, write nothing
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACT = REPO_ROOT / "contracts" / "filter_shape_contract.json"
OBSERVED = REPO_ROOT / "contracts" / "observed_shape_types.json"
OUT = REPO_ROOT / "tango" / "shapes" / "generated_overlay.py"

sys.path.insert(0, str(REPO_ROOT))

import json  # noqa: E402

sys.path.insert(0, str(REPO_ROOT / "scripts"))
from check_shape_coverage import RESOURCE_TO_MODEL  # noqa: E402

from tango.shapes.explicit_schemas import EXPLICIT_SCHEMAS  # noqa: E402

contract = json.loads(CONTRACT.read_text())
observed = json.loads(OBSERVED.read_text())

DATE_NAMES = {"start_date", "end_date", "award_date"}


def base_schema(ref):
    if ref is None:
        return None
    name = ref if isinstance(ref, str) else getattr(ref, "__name__", str(ref))
    return EXPLICIT_SCHEMAS.get(name) or None


def heuristic(name: str) -> tuple[str, bool]:
    n = name.lower()
    if n.endswith("_date") or n in DATE_NAMES:
        return "date", False
    if n.endswith(("_datetime", "_at", "_timestamp")) or n in {"created", "modified"}:
        return "datetime", False
    if n.endswith(("_amount", "_value", "_price", "_obligations", "_ceiling", "_cost", "_fee")):
        return "Decimal", False
    if n.startswith(("is_", "has_")):
        return "bool", False
    if n.endswith(("_count", "_rank")) or n.startswith("number_of_"):
        return "int", False
    return "str", False


def observed_paths(res: str) -> dict:
    return observed.get(res, {}).get("paths", {})


def equiv_lookup(res: str, path: str, name: str):
    full = f"{path}.{name}" if path and path != "(root)" else name
    if res == "vehicles":
        if full.startswith("awardees.orders."):
            return observed_paths("contracts").get(full[len("awardees.orders.") :])
        if full.startswith("awardees."):
            return observed_paths("idvs").get(full[len("awardees.") :])
    return None


def resolve_scalar(res: str, path: str, name: str) -> tuple[str, bool]:
    full = f"{path}.{name}" if path and path != "(root)" else name
    d = observed_paths(res).get(full)
    if d and d.get("kind") == "scalar" and d.get("type"):
        return d["type"], bool(d.get("is_list"))
    e = equiv_lookup(res, path, name)
    if e and e.get("kind") == "scalar" and e.get("type"):
        return e["type"], bool(e.get("is_list"))
    return heuristic(name)


def is_code_object(node: dict, res: str, path: str, name: str) -> bool:
    if set(node.get("fields", []) or []) == {"code", "description"} and not (
        node.get("expands") or {}
    ):
        return True
    full = f"{path}.{name}" if path and path != "(root)" else name
    d = observed_paths(res).get(full) or equiv_lookup(res, path, name)
    return bool(d and d.get("kind") == "code_object")


def node_is_list(res: str, path: str, name: str) -> bool:
    full = f"{path}.{name}" if path and path != "(root)" else name
    d = observed_paths(res).get(full) or equiv_lookup(res, path, name)
    return bool(d and d.get("is_list"))


def is_wildcard(node: dict) -> bool:
    return "*" in (node.get("fields", []) or [])


nested_schemas: dict[str, dict] = {}
_by_signature: dict[tuple, str] = {}


def _sig(schema: dict) -> tuple:
    return tuple(sorted((k, (v["type"], v["is_list"], v.get("nested"))) for k, v in schema.items()))


def _title(name: str) -> str:
    return "".join(w.title() for w in name.split("_"))


def intern_nested(preferred: str, schema: dict) -> str:
    sig = _sig(schema)
    if sig in _by_signature:
        return _by_signature[sig]
    name, i = preferred, 2
    while name in nested_schemas:
        name, i = f"{preferred}{i}", i + 1
    nested_schemas[name] = schema
    _by_signature[sig] = name
    return name


def entry(t: str, is_optional: bool, is_list: bool, nested: str | None = None) -> dict:
    return {"type": t, "is_optional": is_optional, "is_list": is_list, "nested": nested}


def build_nested(res: str, path: str, name: str, node: dict) -> str:
    npath = f"{path}.{name}" if path and path != "(root)" else name
    schema: dict[str, dict] = {}
    for f in node.get("fields", []) or []:
        if f == "*":
            continue
        t, lst = resolve_scalar(res, npath, f)
        schema[f] = entry(t, True, lst)
    for cname, cnode in (node.get("expands") or {}).items():
        schema[cname] = expand_entry(res, npath, cname, cnode)
    return intern_nested(_title(name), schema)


def expand_entry(res: str, path: str, ename: str, enode: dict) -> dict:
    if is_wildcard(enode):
        return entry("dict", True, node_is_list(res, path, ename))
    if is_code_object(enode, res, path, ename):
        return entry("dict", True, node_is_list(res, path, ename), nested="CodeDescription")
    return entry(
        "dict", True, node_is_list(res, path, ename), nested=build_nested(res, path, ename, enode)
    )


overlay: dict[str, dict[str, dict]] = {}
report_rows: list[str] = []


def walk(res: str, path: str, node: dict, schema, container: str) -> None:
    if schema is None:
        return
    fields = node.get("fields", []) or []
    if "*" not in fields:
        for f in fields:
            if f != "*" and f not in schema:
                t, lst = resolve_scalar(res, path, f)
                overlay.setdefault(container, {})[f] = entry(t, True, lst)
                report_rows.append(f"{res}:{path or '(root)'}.{f}  ->  {t}{'[]' if lst else ''}")
    for ename, enode in (node.get("expands") or {}).items():
        fs = schema.get(ename)
        child_path = f"{path}.{ename}" if path and path != "(root)" else ename
        nested_name = getattr(fs, "nested_model", None) if fs is not None else None
        child_schema = base_schema(nested_name) if nested_name else None
        if fs is None or child_schema is None:
            if is_wildcard(enode) and fs is not None:
                continue
            overlay.setdefault(container, {})[ename] = expand_entry(res, path, ename, enode)
            report_rows.append(f"{res}:{path or '(root)'}.{ename}  ->  expand")
        else:
            walk(res, child_path, enode, child_schema, container=nested_name)


for rkey, r in contract["resources"].items():
    shape = (r.get("runtime") or {}).get("shape")
    if not shape:
        continue
    model_name = RESOURCE_TO_MODEL.get(rkey)
    schema = base_schema(model_name)
    if schema is None:
        s: dict[str, dict] = {}
        for f in shape.get("fields", []) or []:
            if f == "*":
                continue
            t, lst = resolve_scalar(rkey, "", f)
            s[f] = entry(t, True, lst)
        for cname, cnode in (shape.get("expands") or {}).items():
            s[cname] = expand_entry(rkey, "", cname, cnode)
        if model_name:
            overlay[model_name] = {**overlay.get(model_name, {}), **s}
        continue
    walk(rkey, "", shape, schema, container=model_name)


def render_field(name: str, e: dict) -> str:
    args = [
        f'name="{name}"',
        f"type={e['type']}",
        f"is_optional={e['is_optional']}",
        f"is_list={e['is_list']}",
    ]
    if e.get("nested"):
        args.append(f'nested_model="{e["nested"]}"')
    return f'"{name}": FieldSchema({", ".join(args)}),'


def emit() -> str:
    lines = [
        '"""GENERATED by scripts/generate_shape_overlay.py — do not edit by hand.',
        "",
        "Reverse shape-coverage overlay: the fields and expands Tango's shape trees",
        "expose that the hand-curated explicit_schemas.py did not capture. SchemaRegistry",
        "merges this over the base schemas so the SDK's typed shape API accepts everything",
        "the API returns. Regenerate after refreshing the vendored contract or observations.",
        '"""',
        "from __future__ import annotations",
        "",
        "from datetime import date, datetime  # noqa: F401",
        "from decimal import Decimal  # noqa: F401",
        "",
        "from tango.shapes.schema import FieldSchema",
        "",
    ]
    var = {ref: re.sub(r"(?<!^)(?=[A-Z])", "_", ref).upper() + "_SCHEMA" for ref in nested_schemas}
    for ref in sorted(nested_schemas):
        lines.append(f"{var[ref]}: dict[str, FieldSchema] = {{")
        for n in sorted(nested_schemas[ref]):
            lines.append("    " + render_field(n, nested_schemas[ref][n]))
        lines += ["}", ""]
    lines.append("GENERATED_NESTED: dict[str, dict[str, FieldSchema]] = {")
    for ref in sorted(nested_schemas):
        lines.append(f'    "{ref}": {var[ref]},')
    lines += ["}", ""]
    lines.append("# container model-name -> additional field schemas (merged over base)")
    lines.append("GENERATED_OVERLAY: dict[str, dict[str, FieldSchema]] = {")
    for model in sorted(overlay):
        lines.append(f'    "{model}": {{')
        for n in sorted(overlay[model]):
            lines.append("        " + render_field(n, overlay[model][n]))
        lines.append("    },")
    lines += ["}", ""]
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate the reverse shape-coverage overlay.")
    ap.add_argument(
        "--report", action="store_true", help="Print the gaps that would be closed; write nothing."
    )
    args = ap.parse_args()

    n_fields = sum(len(v) for v in overlay.values())
    if args.report:
        for row in sorted(report_rows):
            print(row)
        print(
            f"\n{n_fields} additions across {len(overlay)} containers, {len(nested_schemas)} nested schemas."
        )
        return 0

    OUT.write_text(emit())
    # Keep the emitted module ruff-clean so CI's format gate stays green on regen.
    subprocess.run(["uv", "run", "ruff", "format", str(OUT)], cwd=REPO_ROOT, capture_output=True)
    subprocess.run(
        ["uv", "run", "ruff", "check", "--fix", str(OUT)], cwd=REPO_ROOT, capture_output=True
    )
    print(
        f"wrote {OUT.relative_to(REPO_ROOT)}: {n_fields} fields across {len(overlay)} containers, {len(nested_schemas)} nested schemas."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
