"""Integration tests for protest endpoints

Pytest Markers:
    @pytest.mark.integration: Marks tests as integration tests that may hit external APIs
    @pytest.mark.vcr(): Enables VCR recording/playback for HTTP interactions
    @pytest.mark.live: Forces tests to use live API (skip cassettes) - not used by default
    @pytest.mark.cached: Forces tests to only run with cached responses - not used by default
    @pytest.mark.slow: Marks tests that are slow to execute - not used by default

Usage:
    # Run all integration tests (uses cassettes if available)
    pytest tests/integration/

    # Run only protest integration tests
    pytest tests/integration/test_protests_integration.py

    # Run with live API (requires TANGO_API_KEY environment variable)
    TANGO_USE_LIVE_API=true TANGO_API_KEY=xxx pytest tests/integration/

    # Refresh cassettes (re-record all interactions)
    TANGO_REFRESH_CASSETTES=true TANGO_API_KEY=xxx pytest tests/integration/

API reference: https://tango.makegov.com/docs/api-reference/protests.md
"""

from datetime import datetime

import pytest

from tango import ShapeConfig
from tests.integration.conftest import handle_api_exceptions
from tests.integration.validation import (
    validate_no_parsing_errors,
    validate_pagination,
)


def validate_protest_fields(protest, minimal: bool = True) -> None:
    """Validate protest object has required fields and correct types

    Args:
        protest: A Protest object to validate
        minimal: If True, only validate minimal fields. If False, validate comprehensive fields.

    Raises:
        AssertionError: If validation fails
    """
    is_dict = isinstance(protest, dict)
    case_id = protest.get("case_id") if is_dict else getattr(protest, "case_id", None)
    assert case_id is not None, "Protest 'case_id' must not be None"
    assert isinstance(case_id, str), f"Protest 'case_id' must be string, got {type(case_id)}"

    # Optional fields - type check when present
    case_number = protest.get("case_number") if is_dict else getattr(protest, "case_number", None)
    if case_number is not None:
        assert isinstance(case_number, str), (
            f"Protest 'case_number' must be string, got {type(case_number)}"
        )

    title = protest.get("title") if is_dict else getattr(protest, "title", None)
    if title is not None:
        assert isinstance(title, str), f"Protest 'title' must be string, got {type(title)}"

    outcome = protest.get("outcome") if is_dict else getattr(protest, "outcome", None)
    if outcome is not None:
        assert isinstance(outcome, str), f"Protest 'outcome' must be string, got {type(outcome)}"

    source_system = (
        protest.get("source_system") if is_dict else getattr(protest, "source_system", None)
    )
    if source_system is not None:
        assert isinstance(source_system, str), (
            f"Protest 'source_system' must be string, got {type(source_system)}"
        )

    filed_date = protest.get("filed_date") if is_dict else getattr(protest, "filed_date", None)
    if filed_date is not None:
        assert isinstance(filed_date, datetime), (
            f"Protest 'filed_date' must be datetime, got {type(filed_date)}"
        )

    decision_date = (
        protest.get("decision_date") if is_dict else getattr(protest, "decision_date", None)
    )
    if decision_date is not None:
        assert isinstance(decision_date, datetime), (
            f"Protest 'decision_date' must be datetime, got {type(decision_date)}"
        )

    posted_date = protest.get("posted_date") if is_dict else getattr(protest, "posted_date", None)
    if posted_date is not None:
        assert isinstance(posted_date, datetime), (
            f"Protest 'posted_date' must be datetime, got {type(posted_date)}"
        )

    dockets = protest.get("dockets") if is_dict else getattr(protest, "dockets", None)
    if dockets is not None:
        assert isinstance(dockets, list), f"Protest 'dockets' must be list, got {type(dockets)}"


@pytest.mark.vcr()
@pytest.mark.integration
class TestProtestsIntegration:
    """Integration tests for protest endpoints using production data"""

    @handle_api_exceptions("protests")
    @pytest.mark.parametrize(
        "shape_name,shape_value",
        [
            ("default", None),
            ("minimal", ShapeConfig.PROTESTS_MINIMAL),
            (
                "with_dockets",
                "case_id,case_number,title,outcome,filed_date,dockets(docket_number,filed_date,outcome)",
            ),
            ("custom", "case_id,title,source_system,outcome"),
        ],
    )
    def test_list_protests_with_shapes(self, tango_client, shape_name, shape_value):
        """Test listing protests with different shapes

        Validates:
        - Protests endpoint exists and returns data
        - Paginated response structure
        - Protest parsing with various shapes
        - Required field case_id is present regardless of shape
        """
        kwargs: dict = {"limit": 5}
        if shape_value is not None:
            kwargs["shape"] = shape_value

        response = tango_client.list_protests(**kwargs)

        validate_pagination(response)

        if response.results:
            protest = response.results[0]
            validate_protest_fields(protest, minimal=(shape_name in ("default", "minimal")))
            validate_no_parsing_errors(protest)

            is_dict = isinstance(protest, dict)
            case_id = protest.get("case_id") if is_dict else getattr(protest, "case_id", None)
            assert case_id is not None, "Protest case_id should be present"

    @handle_api_exceptions("protests")
    def test_list_protests_with_filter(self, tango_client):
        """Test listing protests with source_system filter (e.g. gao)"""
        response = tango_client.list_protests(limit=5, source_system="gao")

        validate_pagination(response)

        if response.results:
            for protest in response.results:
                validate_protest_fields(protest, minimal=True)
                validate_no_parsing_errors(protest)
                source_system = (
                    protest.get("source_system")
                    if isinstance(protest, dict)
                    else getattr(protest, "source_system", None)
                )
                if source_system is not None:
                    assert source_system.lower() == "gao", (
                        f"Expected source_system gao, got {source_system}"
                    )

    @handle_api_exceptions("protests")
    def test_protest_pagination(self, tango_client):
        """Test protest pagination

        Validates:
        - Pagination works correctly
        - Multiple pages can be retrieved
        """
        page1 = tango_client.list_protests(limit=5, page=1)
        validate_pagination(page1)

        page2 = tango_client.list_protests(limit=5, page=2)
        validate_pagination(page2)

        if page1.results and page2.results:
            is_dict1 = isinstance(page1.results[0], dict)
            is_dict2 = isinstance(page2.results[0], dict)
            case_id1 = (
                page1.results[0].get("case_id")
                if is_dict1
                else getattr(page1.results[0], "case_id", None)
            )
            case_id2 = (
                page2.results[0].get("case_id")
                if is_dict2
                else getattr(page2.results[0], "case_id", None)
            )
            assert case_id1 != case_id2, "Different pages should have different results"

    @handle_api_exceptions("protests")
    def test_get_protest_by_case_id(self, tango_client):
        """Test get_protest detail by case_id (UUID from list response)"""
        response = tango_client.list_protests(limit=1)
        validate_pagination(response)

        if not response.results:
            pytest.skip("No protests returned from list to fetch by case_id")

        protest = response.results[0]
        is_dict = isinstance(protest, dict)
        case_id = protest.get("case_id") if is_dict else getattr(protest, "case_id", None)
        assert case_id is not None

        detail = tango_client.get_protest(case_id)
        validate_protest_fields(detail, minimal=False)
        validate_no_parsing_errors(detail)

        detail_case_id = detail.get("case_id") if isinstance(detail, dict) else detail.case_id
        assert detail_case_id == case_id, "Detail case_id should match requested case_id"
