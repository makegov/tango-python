"""The reverse shape-coverage gate must not go blind on a null shape tree.

Tango published `"shape": null` for entities, opportunities, notices, protests,
and itdashboard because its contract generator crashed on tier-aware viewsets
(makegov/tango#2944). This gate skipped any resource with a falsy shape, so it
reported full coverage while the SDK's Entity and Protest schemas drifted 13
fields behind the API — fields the SDK then rejected client-side, before ever
issuing a request.

The skip is now conditional: at schema_version >= 2 a contract declares
`shape_supported`, so a null tree on a shaping resource is a hard finding. Older
contracts omit the key, where `None` really is ambiguous and skipping is the
only safe read.
"""

import importlib.util
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]


def _load_gate():
    spec = importlib.util.spec_from_file_location(
        "check_shape_coverage", REPO_ROOT / "scripts" / "check_shape_coverage.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def gate():
    return _load_gate()


def _contract(runtime: dict) -> dict:
    return {"resources": {"widgets": {"runtime": runtime}}}


def test_null_shape_on_shaping_resource_is_a_finding(gate):
    findings = gate.collect_gaps(
        _contract({"shape": None, "shape_supported": True, "shape_error": "AttributeError: boom"}),
        registry=None,
        models=None,
    )

    assert len(findings) == 1
    assert findings[0]["kind"] == "contract_missing_shape"
    assert findings[0]["resource"] == "widgets"
    assert "AttributeError" in findings[0]["name"]


def test_finding_survives_without_a_recorded_error(gate):
    findings = gate.collect_gaps(
        _contract({"shape": None, "shape_supported": True}), registry=None, models=None
    )

    assert [f["kind"] for f in findings] == ["contract_missing_shape"]
    assert findings[0]["name"] == "no shape tree published"


def test_non_shaping_resource_is_not_a_finding(gate):
    """news/events genuinely have no shaping — a null tree there is correct."""
    findings = gate.collect_gaps(
        _contract({"shape": None, "shape_supported": False}), registry=None, models=None
    )

    assert findings == []


def test_older_contract_without_the_key_still_skips(gate):
    """Pre-schema_version-2 contracts omit shape_supported; null stays ambiguous."""
    findings = gate.collect_gaps(_contract({"shape": None}), registry=None, models=None)

    assert findings == []


def test_finding_key_is_stable_for_baselining(gate):
    finding = {
        "kind": "contract_missing_shape",
        "resource": "widgets",
        "path": "(root)",
        "name": "no shape tree published",
    }

    assert (
        gate.finding_key(finding) == "contract_missing_shape|widgets|(root)|no shape tree published"
    )


def test_vendored_contract_publishes_shape_for_every_shaping_resource(gate):
    """End-to-end: the real vendored contract must have no blind spots left."""
    import json

    contract = json.loads(
        (REPO_ROOT / "contracts" / "filter_shape_contract.json").read_text(encoding="utf-8")
    )

    blind = [
        name
        for name, resource in contract["resources"].items()
        if (resource.get("runtime") or {}).get("shape_supported")
        and not (resource.get("runtime") or {}).get("shape")
    ]

    assert blind == [], f"vendored contract has shape blind spots: {blind}"
