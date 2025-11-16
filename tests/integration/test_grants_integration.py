"""Integration tests for grant endpoints

Pytest Markers:
    @pytest.mark.integration: Marks tests as integration tests that may hit external APIs
    @pytest.mark.vcr(): Enables VCR recording/playback for HTTP interactions
    @pytest.mark.live: Forces tests to use live API (skip cassettes) - not used by default
    @pytest.mark.cached: Forces tests to only run with cached responses - not used by default
    @pytest.mark.slow: Marks tests that are slow to execute - not used by default

Usage:
    # Run all integration tests (uses cassettes if available)
    pytest tests/integration/

    # Run only grant integration tests
    pytest tests/integration/test_grants_integration.py

    # Run with live API (requires TANGO_API_KEY environment variable)
    TANGO_USE_LIVE_API=true TANGO_API_KEY=xxx pytest tests/integration/

    # Refresh cassettes (re-record all interactions)
    TANGO_REFRESH_CASSETTES=true TANGO_API_KEY=xxx pytest tests/integration/
"""

from datetime import datetime

import pytest

from tango import ShapeConfig
from tests.integration.conftest import handle_api_exceptions
from tests.integration.validation import (
    validate_no_parsing_errors,
    validate_pagination,
)


def validate_grant_fields(grant, minimal: bool = True) -> None:
    """Validate grant object has required fields and correct types

    Args:
        grant: A Grant object to validate
        minimal: If True, only validate minimal fields. If False, validate comprehensive fields.

    Raises:
        AssertionError: If validation fails
    """
    # Required fields - Grant uses 'grant_id' not 'key'
    is_dict = isinstance(grant, dict)
    grant_id = grant.get("grant_id") if is_dict else getattr(grant, "grant_id", None)
    assert grant_id is not None, "Grant 'grant_id' must not be None"
    assert isinstance(grant_id, int), f"Grant 'grant_id' must be int, got {type(grant_id)}"

    opportunity_number = (
        grant.get("opportunity_number") if is_dict else getattr(grant, "opportunity_number", None)
    )
    assert opportunity_number is not None, "Grant 'opportunity_number' must not be None"
    assert isinstance(opportunity_number, str), (
        f"Grant 'opportunity_number' must be str, got {type(opportunity_number)}"
    )

    title = grant.get("title") if is_dict else getattr(grant, "title", None)
    assert title is not None, "Grant 'title' must not be None"
    assert isinstance(title, str), f"Grant 'title' must be str, got {type(title)}"

    # Optional fields that may be present
    if not minimal:
        # Check status if present
        status = grant.get("status") if is_dict else getattr(grant, "status", None)
        if status is not None:
            assert isinstance(status, dict), f"Grant 'status' must be dict, got {type(status)}"

        # Check agency_code if present
        agency_code = grant.get("agency_code") if is_dict else getattr(grant, "agency_code", None)
        if agency_code is not None:
            assert isinstance(agency_code, str), (
                f"Grant 'agency_code' must be str, got {type(agency_code)}"
            )

        # Check last_updated if present
        last_updated = (
            grant.get("last_updated") if is_dict else getattr(grant, "last_updated", None)
        )
        if last_updated is not None:
            assert isinstance(last_updated, (str, datetime)), (
                f"Grant 'last_updated' must be str or datetime, got {type(last_updated)}"
            )

        # Check cfda_numbers if present (list of dicts)
        cfda_numbers = (
            grant.get("cfda_numbers") if is_dict else getattr(grant, "cfda_numbers", None)
        )
        if cfda_numbers is not None:
            assert isinstance(cfda_numbers, list), (
                f"Grant 'cfda_numbers' must be list, got {type(cfda_numbers)}"
            )


@pytest.mark.vcr()
@pytest.mark.integration
class TestGrantsIntegration:
    """Integration tests for grant endpoints using production data"""

    @handle_api_exceptions("grants")
    @pytest.mark.parametrize(
        "shape_name,shape_value",
        [
            ("default", None),
            ("minimal", ShapeConfig.GRANTS_MINIMAL),
            (
                "detailed",
                "grant_id,opportunity_number,title,status(*),agency_code,description,last_updated,cfda_numbers(number,title),applicant_types(*),funding_categories(*)",
            ),
            ("custom", "grant_id,title,opportunity_number"),
        ],
    )
    def test_list_grants_with_shapes(self, tango_client, shape_name, shape_value):
        """Test listing grants with different shapes

        Validates:
        - Grants endpoint exists and returns data
        - Paginated response structure
        - Grant parsing with various shapes
        - Required fields are present regardless of shape
        """
        kwargs = {"limit": 5}
        if shape_value is not None:
            kwargs["shape"] = shape_value

        response = tango_client.list_grants(**kwargs)

        # Validate response structure
        validate_pagination(response)

        # If we have results, validate them
        if response.results:
            grant = response.results[0]
            validate_grant_fields(grant, minimal=(shape_name in ("default", "minimal")))
            validate_no_parsing_errors(grant)

            # Verify required fields are present
            is_dict = isinstance(grant, dict)
            grant_id = grant.get("grant_id") if is_dict else getattr(grant, "grant_id", None)
            title = grant.get("title") if is_dict else getattr(grant, "title", None)
            assert grant_id is not None, "Grant grant_id should be present"
            assert title is not None, "Grant title should be present"

    @handle_api_exceptions("grants")
    def test_grant_field_types(self, tango_client):
        """
        Test that grant fields have correct types

        Validates:
        - Field types match expected types
        - Nested objects are properly structured
        """
        response = tango_client.list_grants(limit=1)

        if not response.results:
            pytest.skip("No grants available for testing")

        grant = response.results[0]
        is_dict = isinstance(grant, dict)

        # Required fields
        grant_id = grant.get("grant_id") if is_dict else getattr(grant, "grant_id", None)
        assert isinstance(grant_id, int), f"grant_id should be int, got {type(grant_id)}"

        opportunity_number = (
            grant.get("opportunity_number")
            if is_dict
            else getattr(grant, "opportunity_number", None)
        )
        assert isinstance(opportunity_number, str), (
            f"opportunity_number should be str, got {type(opportunity_number)}"
        )

        title = grant.get("title") if is_dict else getattr(grant, "title", None)
        assert isinstance(title, str), f"title should be str, got {type(title)}"

    @handle_api_exceptions("grants")
    def test_grant_pagination(self, tango_client):
        """Test grant pagination

        Validates:
        - Pagination works correctly
        - Multiple pages can be retrieved
        - Page metadata is correct
        """
        # Get first page
        page1 = tango_client.list_grants(limit=5, page=1)
        validate_pagination(page1)

        # Get second page
        page2 = tango_client.list_grants(limit=5, page=2)
        validate_pagination(page2)

        # Verify pages have different results
        if page1.results and page2.results:
            is_dict1 = isinstance(page1.results[0], dict)
            is_dict2 = isinstance(page2.results[0], dict)
            grant1_id = (
                page1.results[0].get("grant_id")
                if is_dict1
                else getattr(page1.results[0], "grant_id", None)
            )
            grant2_id = (
                page2.results[0].get("grant_id")
                if is_dict2
                else getattr(page2.results[0], "grant_id", None)
            )
            assert grant1_id != grant2_id, "Different pages should have different results"

