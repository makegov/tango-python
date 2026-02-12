#!/usr/bin/env python3
"""
Validate tango-python against a canonical filter/shape manifest.

Runs two conformance checks:
1. Filter conformance: SDK list/get methods expose the filter params from the manifest.
2. Shape conformance: Every ShapeConfig constant parses and validates against the
   SDK schema for its model (so default shapes only reference allowed fields).
"""

from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path
from typing import Any, Type

REPO_ROOT = Path(__file__).resolve().parents[1]
CLIENT_PATH = REPO_ROOT / "tango" / "client.py"


def get_shape_config_entries() -> list[tuple[str, str, Type[Any]]]:
    """Return (shape_name, shape_string, model_class) for every ShapeConfig constant."""
    from tango.models import (
        Contract,
        Entity,
        Forecast,
        Grant,
        IDV,
        Notice,
        OTA,
        Organization,
        Opportunity,
        OTIDV,
        ShapeConfig,
        Subaward,
        Vehicle,
    )

    # ShapeConfig constant name -> (shape string, model class for validation)
    entries: list[tuple[str, str, Type[Any]]] = []
    configs = [
        ("CONTRACTS_MINIMAL", ShapeConfig.CONTRACTS_MINIMAL, Contract),
        ("ENTITIES_MINIMAL", ShapeConfig.ENTITIES_MINIMAL, Entity),
        ("ENTITIES_COMPREHENSIVE", ShapeConfig.ENTITIES_COMPREHENSIVE, Entity),
        ("FORECASTS_MINIMAL", ShapeConfig.FORECASTS_MINIMAL, Forecast),
        ("OPPORTUNITIES_MINIMAL", ShapeConfig.OPPORTUNITIES_MINIMAL, Opportunity),
        ("NOTICES_MINIMAL", ShapeConfig.NOTICES_MINIMAL, Notice),
        ("GRANTS_MINIMAL", ShapeConfig.GRANTS_MINIMAL, Grant),
        ("IDVS_MINIMAL", ShapeConfig.IDVS_MINIMAL, IDV),
        ("IDVS_COMPREHENSIVE", ShapeConfig.IDVS_COMPREHENSIVE, IDV),
        ("VEHICLES_MINIMAL", ShapeConfig.VEHICLES_MINIMAL, Vehicle),
        ("VEHICLES_COMPREHENSIVE", ShapeConfig.VEHICLES_COMPREHENSIVE, Vehicle),
        ("VEHICLE_AWARDEES_MINIMAL", ShapeConfig.VEHICLE_AWARDEES_MINIMAL, IDV),
        ("ORGANIZATIONS_MINIMAL", ShapeConfig.ORGANIZATIONS_MINIMAL, Organization),
        ("OTAS_MINIMAL", ShapeConfig.OTAS_MINIMAL, OTA),
        ("OTIDVS_MINIMAL", ShapeConfig.OTIDVS_MINIMAL, OTIDV),
        ("SUBAWARDS_MINIMAL", ShapeConfig.SUBAWARDS_MINIMAL, Subaward),
    ]
    for name, shape_str, model_cls in configs:
        entries.append((name, shape_str, model_cls))
    return entries


def run_shape_check() -> tuple[list[str], list[str]]:
    """Validate all ShapeConfig constants against SDK schemas. Returns (errors, warnings)."""
    from tango.exceptions import ShapeParseError, ShapeValidationError
    from tango.shapes.parser import ShapeParser

    errors: list[str] = []
    warnings: list[str] = []
    parser = ShapeParser(cache_enabled=True)

    for shape_name, shape_string, model_class in get_shape_config_entries():
        try:
            shape_spec = parser.parse(shape_string)
            parser.validate(shape_spec, model_class)
        except ShapeParseError as e:
            errors.append(f"shapes: `ShapeConfig.{shape_name}` parse error: {e}")
        except ShapeValidationError as e:
            errors.append(f"shapes: `ShapeConfig.{shape_name}` invalid: {e}")

    return errors, warnings


def parse_client_methods() -> dict[str, dict[str, Any]]:
    tree = ast.parse(CLIENT_PATH.read_text(encoding="utf-8"), filename=str(CLIENT_PATH))
    methods: dict[str, dict[str, Any]] = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue
        if not node.name.startswith(("list_", "get_")):
            continue
        args = [arg.arg for arg in node.args.args if arg.arg != "self"]
        has_kwargs = node.args.kwarg is not None
        mapping: dict[str, str] = {}
        for child in ast.walk(node):
            if isinstance(child, ast.Assign):
                if len(child.targets) != 1 or not isinstance(child.targets[0], ast.Name):
                    continue
                if child.targets[0].id != "api_param_mapping":
                    continue
                if isinstance(child.value, ast.Dict):
                    for key, value in zip(child.value.keys, child.value.values):
                        if isinstance(key, ast.Constant) and isinstance(value, ast.Constant):
                            mapping[str(key.value)] = str(value.value)
        methods[node.name] = {
            "args": set(args),
            "has_kwargs": has_kwargs,
            "mapped_api_params": set(mapping.values()),
        }
    return methods


def run_check(manifest_path: Path) -> tuple[list[str], list[str]]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    resources = manifest.get("resources", {})
    methods = parse_client_methods()

    errors: list[str] = []
    warnings: list[str] = []

    for resource_name, payload in resources.items():
        candidates = payload.get("sdk_method_candidates", []) or []
        sdk_method = next((name for name in candidates if name in methods), None)
        if not sdk_method:
            if payload.get("runtime", {}).get("filter_params"):
                warnings.append(
                    f"{resource_name}: no matching SDK method found among candidates: {', '.join(candidates) if candidates else '(none)'}"
                )
            continue

        runtime_filters = set(payload.get("runtime", {}).get("filter_params", []))
        method_info = methods[sdk_method]
        exposed = set(method_info["args"]) | set(method_info["mapped_api_params"])

        if method_info["has_kwargs"]:
            missing_named = sorted(runtime_filters - exposed)
            if missing_named:
                warnings.append(
                    f"{resource_name}: `{sdk_method}` relies on **kwargs for filters: {', '.join(missing_named)}"
                )
            continue

        missing = sorted(runtime_filters - exposed)
        if missing:
            errors.append(
                f"{resource_name}: `{sdk_method}` missing runtime filters: {', '.join(missing)}"
            )

    return errors, warnings


def get_missing_endpoints(manifest_path: Path) -> list[dict[str, Any]]:
    """Return a list of resources that have no matching SDK method (for implementation checklist)."""
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    resources = manifest.get("resources", {})
    methods = parse_client_methods()
    missing: list[dict[str, Any]] = []
    for resource_name, payload in resources.items():
        candidates = payload.get("sdk_method_candidates", []) or []
        sdk_method = next((name for name in candidates if name in methods), None)
        if not sdk_method:
            runtime = payload.get("runtime", {}) or {}
            missing.append({
                "resource": resource_name,
                "sdk_method_candidates": candidates,
                "filter_params": runtime.get("filter_params", []),
                "pagination_class": (runtime.get("pagination") or {}).get("class", ""),
            })
    return missing


def main() -> int:
    parser = argparse.ArgumentParser(description="Check SDK conformance to canonical manifest")
    parser.add_argument(
        "--manifest",
        required=True,
        help="Path to filter_shape_contract.json generated by tango",
    )
    parser.add_argument(
        "--list-missing",
        action="store_true",
        help="Output machine-readable list of missing endpoints (resources with no SDK method) only",
    )
    args = parser.parse_args()

    manifest_path = Path(args.manifest).resolve()
    if not manifest_path.exists():
        print(f"Manifest not found: {manifest_path}")
        return 2

    if args.list_missing:
        missing = get_missing_endpoints(manifest_path)
        print(json.dumps({"missing_endpoints": missing}, indent=2))
        return 0

    errors, warnings = run_check(manifest_path)

    # Shape conformance: every ShapeConfig constant must validate against its model schema
    shape_errors, shape_warnings = run_shape_check()
    errors = list(errors) + shape_errors
    warnings = list(warnings) + shape_warnings

    # Treat "no matching SDK method" warnings as errors so CI enforces endpoint coverage
    missing_method_warnings = [w for w in warnings if "no matching SDK method found" in w]
    if missing_method_warnings:
        errors = list(errors) + missing_method_warnings

    report = {
        "manifest": str(manifest_path),
        "errors": errors,
        "warnings": warnings,
    }
    print(json.dumps(report, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
