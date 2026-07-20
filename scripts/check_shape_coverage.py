#!/usr/bin/env python3
"""Reverse shape-coverage gate: Tango's shape trees -> SDK schemas.

The existing conformance check (check_filter_shape_conformance.py) validates one
direction only: that the SDK's ShapeConfig constants reference *allowed* fields.
It never checks the reverse — that the SDK actually *captures* every field and
expand Tango exposes. That reverse gap is where the SDK silently under-serves
users: a field Tango returns that the SDK schema lacks can't be requested through
the typed shape API at all.

This walks each resource's real shape tree from the vendored contract
(contracts/filter_shape_contract.json — Tango's own generated truth) against the
SDK's schema for that model (tango/shapes/schema.py + explicit_schemas.py) and
reports what Tango exposes that the SDK does not capture, in three kinds:

    missing_field    Tango exposes a leaf field; SDK schema has no such key.
    missing_expand   Tango exposes a whole nested expand; SDK schema lacks it.
    expand_flat      Tango models an expand as a nested object ({code,description}
                     code-objects, etc.); SDK carries it as a scalar with no
                     nested schema, so its sub-fields are unreachable.
    unmapped_resource  A resource has a contract shape tree but no SDK schema.

Fully local: no network, no API key, no Tango checkout — it reads the vendored
contract, so it runs on forks and in tokenless CI (the public-repo-safe pattern).

Baseline: contracts/shape_coverage_baseline.json records the CURRENTLY-KNOWN
gaps. The gate fails only on findings NOT in the baseline — so it stops NEW drift
immediately while the known backlog is burned down separately. Refresh with
--update-baseline after intentionally changing coverage.

Exit codes: 0 = no new gaps, 1 = new gaps beyond the baseline, 2 = setup error.
Run: uv run python scripts/check_shape_coverage.py [--update-baseline] [--json]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = REPO_ROOT / "contracts" / "filter_shape_contract.json"
BASELINE_PATH = REPO_ROOT / "contracts" / "shape_coverage_baseline.json"

# Contract resource key -> SDK model class name (resolved from tango.models).
# A resource that maps to no importable model is reported as unmapped_resource.
RESOURCE_TO_MODEL: dict[str, str] = {
    "contracts": "Contract",
    "idvs": "IDV",
    "vehicles": "Vehicle",
    "otas": "OTA",
    "otidvs": "OTIDV",
    "subawards": "Subaward",
    "organizations": "Organization",
    "opportunities": "Opportunity",
    "notices": "Notice",
    "forecasts": "Forecast",
    "grants": "Grant",
    "entities": "Entity",
    "agencies": "Agency",
    "naics": "Naics",
    "gsa_elibrary_contracts": "GsaElibraryContract",
    "itdashboard": "ITDashboardInvestment",
    # Nested routes are keyed with a slash in the contract ("budget/accounts").
    # The pre-slash key is kept so an older vendored contract still maps.
    "budget/accounts": "BudgetAccount",
    "budget_accounts": "BudgetAccount",
    "protests": "Protest",
    "offices": "Office",
    "assistance_listings": "AssistanceListing",
    "business_types": "BusinessType",
    "departments": "Department",
    "psc": "PSC",
    "dibbs/rfqs": "DibbsRfq",
    "dibbs/rfps": "DibbsRfp",
    "dibbs/awards": "DibbsAward",
    "exclusions": "Exclusion",
    "sbir/topics": "SbirTopic",
    "sbir/solicitations": "SbirSolicitation",
    "mas_sins": "MasSin",
    "events": "Event",
    "news": "News",
}


def _load_registry_and_models() -> tuple[Any, Any]:
    sys.path.insert(0, str(REPO_ROOT))
    import tango.models as models
    from tango.shapes.schema import SchemaRegistry

    return SchemaRegistry(), models


def _sdk_schema(registry: Any, model_ref: Any) -> dict[str, Any] | None:
    """Return the SDK field-name -> FieldSchema map for a model class/name, or None."""
    if model_ref is None:
        return None
    try:
        schema = registry.get_schema(model_ref)
    except Exception:
        return None
    return schema or None


def collect_gaps(contract: dict[str, Any], registry: Any, models: Any) -> list[dict[str, Any]]:
    """Walk every resource's contract shape tree against the SDK schema.

    Returns a flat list of finding dicts, each a stable, JSON-serializable record
    keyed for baseline diffing.
    """
    findings: list[dict[str, Any]] = []

    def walk(resource: str, path: str, node: dict[str, Any], schema: dict[str, Any] | None) -> None:
        # A node the SDK can't resolve to a schema — its whole subtree is uncheckable.
        if schema is None:
            findings.append(
                {"kind": "unresolved_node", "resource": resource, "path": path or "(root)"}
            )
            return
        fields = node.get("fields", []) or []
        # A wildcard node ("*") permits any key, so leaf coverage is vacuously satisfied.
        wildcard = "*" in fields
        if not wildcard:
            for f in fields:
                if f == "*":
                    continue
                if f not in schema:
                    findings.append(
                        {
                            "kind": "missing_field",
                            "resource": resource,
                            "path": path or "(root)",
                            "name": f,
                        }
                    )
        for ename, enode in (node.get("expands") or {}).items():
            fs = schema.get(ename)
            child_path = f"{path}.{ename}" if path else ename
            # A wildcard expand ("*") is freeform (any key permitted) — the SDK
            # carrying it as a plain dict is full coverage, not a flattened gap.
            if fs is not None and "*" in (enode.get("fields") or []):
                continue
            if fs is None:
                sub = len(enode.get("fields", []) or []) + len(enode.get("expands") or {})
                findings.append(
                    {
                        "kind": "missing_expand",
                        "resource": resource,
                        "path": path or "(root)",
                        "name": ename,
                        "sub_nodes": sub,
                    }
                )
                continue
            nested = getattr(fs, "nested_model", None)
            child_schema = _sdk_schema(registry, nested) if nested else None
            if child_schema is None:
                # SDK has the key but as a scalar (no nested schema) — Tango models
                # it as an object, so its sub-fields are unreachable through shapes.
                findings.append(
                    {
                        "kind": "expand_flat",
                        "resource": resource,
                        "path": path or "(root)",
                        "name": ename,
                    }
                )
                continue
            walk(resource, child_path, enode, child_schema)

    for rkey, r in contract.get("resources", {}).items():
        runtime = r.get("runtime") or {}
        shape = runtime.get("shape")
        if not shape:
            # A null tree used to be an unconditional skip, which made this gate
            # blind to exactly the resources it most needed to check. Tango
            # published null for entities/opportunities/notices/protests/
            # itdashboard because its generator crashed on tier-aware viewsets
            # (makegov/tango#2944), and this gate reported full coverage while
            # the SDK's Entity and Protest schemas drifted 13 fields behind.
            #
            # Contracts at schema_version >= 2 declare shape_supported, so a
            # null tree on a shaping resource is now a hard finding. Older
            # contracts omit the key; there `None` is genuinely ambiguous and
            # skipping stays the only safe read.
            if runtime.get("shape_supported"):
                findings.append(
                    {
                        "kind": "contract_missing_shape",
                        "resource": rkey,
                        "path": "(root)",
                        "name": runtime.get("shape_error") or "no shape tree published",
                    }
                )
            continue
        model_name = RESOURCE_TO_MODEL.get(rkey)
        model = getattr(models, model_name, None) if model_name else None
        schema = _sdk_schema(registry, model if model is not None else model_name)
        if schema is None:
            findings.append(
                {
                    "kind": "unmapped_resource",
                    "resource": rkey,
                    "path": "(root)",
                    "name": model_name,
                }
            )
            continue
        walk(rkey, "", shape, schema)

    return findings


def finding_key(f: dict[str, Any]) -> str:
    """Stable identity for baseline diffing — ignores volatile counts like sub_nodes."""
    return "|".join([f["kind"], f["resource"], f.get("path", ""), str(f.get("name", ""))])


def load_baseline() -> set[str]:
    if not BASELINE_PATH.exists():
        return set()
    data = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    return set(data.get("known_gaps", []))


def write_baseline(findings: list[dict[str, Any]]) -> None:
    keys = sorted(finding_key(f) for f in findings)
    BASELINE_PATH.parent.mkdir(parents=True, exist_ok=True)
    BASELINE_PATH.write_text(
        json.dumps(
            {
                "description": (
                    "Known reverse shape-coverage gaps (Tango exposes, SDK schema lacks), "
                    "accepted as a tracked backlog. check_shape_coverage.py fails only on "
                    "gaps NOT listed here. Burn down and regenerate with --update-baseline."
                ),
                "count": len(keys),
                "known_gaps": keys,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def _print_grouped(title: str, findings: list[dict[str, Any]]) -> None:
    if not findings:
        return
    print(f"\n{title} ({len(findings)}):")
    by_res: dict[str, list[dict[str, Any]]] = {}
    for f in findings:
        by_res.setdefault(f["resource"], []).append(f)
    for res in sorted(by_res):
        rows = by_res[res]
        print(f"  {res} ({len(rows)}):")
        for f in sorted(rows, key=lambda x: (x.get("path", ""), str(x.get("name", "")))):
            loc = f.get("path", "")
            name = f.get("name", "")
            extra = f"  (+{f['sub_nodes']} sub-nodes)" if f.get("sub_nodes") else ""
            print(f"      {loc} -> {name}{extra}" if name else f"      {loc}")


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Reverse shape-coverage gate (contract -> SDK schemas)."
    )
    ap.add_argument(
        "--update-baseline",
        action="store_true",
        help="Rewrite the baseline to the current gaps and exit 0.",
    )
    ap.add_argument(
        "--json", action="store_true", help="Emit findings as JSON instead of the grouped report."
    )
    args = ap.parse_args()

    if not CONTRACT_PATH.exists():
        print(f"error: vendored contract not found at {CONTRACT_PATH}", file=sys.stderr)
        return 2

    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    try:
        registry, models = _load_registry_and_models()
    except Exception as exc:  # pragma: no cover - import/setup failure
        print(f"error: could not import SDK schema registry: {exc}", file=sys.stderr)
        return 2

    findings = collect_gaps(contract, registry, models)

    if args.update_baseline:
        write_baseline(findings)
        print(f"Wrote {BASELINE_PATH.relative_to(REPO_ROOT)} with {len(findings)} known gaps.")
        return 0

    baseline = load_baseline()
    new = [f for f in findings if finding_key(f) not in baseline]
    fixed = baseline - {finding_key(f) for f in findings}

    if args.json:
        print(
            json.dumps(
                {
                    "new": new,
                    "total": len(findings),
                    "baseline": len(baseline),
                    "fixed": sorted(fixed),
                },
                indent=2,
            )
        )
        return 1 if new else 0

    print(
        f"Shape coverage: {len(findings)} total gaps, {len(baseline)} baselined, {len(new)} NEW, {len(fixed)} fixed since baseline."
    )
    if fixed:
        print(
            f"\n{len(fixed)} baselined gap(s) now fixed — run --update-baseline to shrink the baseline:"
        )
        for k in sorted(fixed):
            print(f"      {k}")
    if not new:
        print("\nNo new shape-coverage drift. ✓")
        return 0

    contract_gaps = [f for f in new if f["kind"] == "contract_missing_shape"]
    if contract_gaps:
        print(
            "\n*** CONTRACT DEFECT — these resources support shaping but publish no shape tree ***"
        )
        _print_grouped("RESOURCES WITH NO SHAPE TREE", contract_gaps)
        print(
            "\n  This is an upstream problem, not an SDK one: the vendored contract understates\n"
            "  the API, so coverage cannot be checked for these resources at all. Refresh the\n"
            "  contract (scripts/refresh_contract.py); if it persists, the generator is failing\n"
            "  to extract them — see makegov/tango contracts/README.md."
        )

    print("\n*** NEW shape-coverage drift (Tango exposes these; the SDK schema does not) ***")
    _print_grouped("MISSING FIELDS", [f for f in new if f["kind"] == "missing_field"])
    _print_grouped("MISSING EXPANDS", [f for f in new if f["kind"] == "missing_expand"])
    _print_grouped(
        "EXPANDS FLATTENED (no nested schema)", [f for f in new if f["kind"] == "expand_flat"]
    )
    _print_grouped("UNRESOLVED NODES", [f for f in new if f["kind"] == "unresolved_node"])
    _print_grouped("UNMAPPED RESOURCES", [f for f in new if f["kind"] == "unmapped_resource"])
    print(
        "\nFix the SDK schema (or regenerate from the contract), or if intentional, run --update-baseline."
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
