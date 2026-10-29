import importlib.util
import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def refresh():
    spec = importlib.util.spec_from_file_location(
        "refresh_contract", REPO_ROOT / "scripts" / "refresh_contract.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _upstream() -> dict:
    return {
        "meta": {
            "api_version": "9.9.9",
            "schema_version": 2,
            "description": "d",
            "generated_from": "x.py",
        },
        "policy": {"anything": []},
        "unmapped_resources": {"no_docs_page": ["widgets"]},
        "resources": {
            "widgets": {
                "resource_key": "widgets",
                "prefix": "widgets",
                "basename": "widget",
                "docs_file": "widgets.md",
                "docs_params": ["q"],
                "runtime": {
                    "filter_params": ["q"],
                    "filter_params_detail": {"q": {"filter_class": "SomeFilter", "type": "string"}},
                    "pagination": {"class": "SomePaginator", "max_page_size": 100},
                    "shape": {"name": None},
                },
            }
        },
    }


def test_project_public_drops_server_internals(refresh):
    projected = refresh.project_public(_upstream())

    assert set(projected) == {"meta", "resources"}
    assert projected["meta"] == {"api_version": "9.9.9", "schema_version": 2, "description": "d"}
    assert projected["resources"]["widgets"] == {
        "resource_key": "widgets",
        "prefix": "widgets",
        "basename": "widget",
        "runtime": {
            "filter_params": ["q"],
            "filter_params_detail": {"q": {"type": "string"}},
            "pagination": {"max_page_size": 100},
            "shape": {"name": None},
        },
    }


def test_project_public_leaves_input_untouched(refresh):
    upstream = _upstream()
    refresh.project_public(upstream)

    assert upstream == _upstream()


def test_vendored_contract_is_already_projected(refresh):
    text = (REPO_ROOT / "contracts" / "filter_shape_contract.json").read_text(encoding="utf-8")

    assert refresh.render(json.loads(text)) == text
