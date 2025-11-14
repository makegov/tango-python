"""Integration tests for opportunity endpoints

Pytest Markers:
    @pytest.mark.integration: Marks tests as integration tests that may hit external APIs
    @pytest.mark.vcr(): Enables VCR recording/playback for HTTP interactions
    @pytest.mark.live: Forces tests to use live API (skip cassettes) - not used by default
    @pytest.mark.cached: Forces tests to only run with cached responses - not used by default
    @pytest.mark.slow: Marks tests that are slow to execute - not used by default

Usage:
    # Run all integration tests (uses cassettes if available)
    pytest tests/integration/

    # Run only opportunity integration tests
    pytest tests/integration/test_opportunities_integration.py

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


def validate_opportunity_fields(opportunity, minimal: bool = True) -> None:
    """Validate opportunity object has required fields and correct types

    Args:
        opportunity: An Opportunity object to validate
        minimal: If True, only validate minimal fields. If False, validate comprehensive fields.

    Raises:
        AssertionError: If validation fails
    """
    # Required fields - key may not be present in all shapes
    # Check for key if it exists (some shapes use opportunity_id instead)
    try:
        key_value = opportunity.key
        if key_value is not None:
            assert isinstance(key_value, str), (
                f"Opportunity 'key' must be string, got {type(key_value)}"
            )
    except AttributeError:
        # key field not in shape - this is acceptable (shapes may use opportunity_id instead)
        pass

    assert opportunity.title is not None, "Opportunity 'title' must not be None"
    assert opportunity.solicitation_number is not None, (
        "Opportunity 'solicitation_number' must not be None"
    )

    # Type validation for required fields
    assert isinstance(opportunity.title, str), (
        f"Opportunity 'title' must be string, got {type(opportunity.title)}"
    )
    assert isinstance(opportunity.solicitation_number, str), (
        f"Opportunity 'solicitation_number' must be string, got {type(opportunity.solicitation_number)}"
    )

    # Type validation for optional datetime fields
    # These fields may not be present in minimal shapes
    try:
        if opportunity.posted_date is not None:
            assert isinstance(opportunity.posted_date, datetime), (
                f"Opportunity 'posted_date' must be datetime, got {type(opportunity.posted_date)}"
            )
    except AttributeError:
        pass  # posted_date not in shape

    try:
        if opportunity.response_deadline is not None:
            assert isinstance(opportunity.response_deadline, datetime), (
                f"Opportunity 'response_deadline' must be datetime, got {type(opportunity.response_deadline)}"
            )
    except AttributeError:
        pass  # response_deadline not in shape

    try:
        if opportunity.archive_date is not None:
            assert isinstance(opportunity.archive_date, datetime), (
                f"Opportunity 'archive_date' must be datetime, got {type(opportunity.archive_date)}"
            )
    except AttributeError:
        pass  # archive_date not in shape

    # Type validation for notice_type
    try:
        if opportunity.notice_type is not None:
            assert isinstance(opportunity.notice_type, str), (
                f"Opportunity 'notice_type' must be string, got {type(opportunity.notice_type)}"
            )
    except AttributeError:
        pass  # notice_type not in shape

    # Type validation for nested objects
    # Shaped responses are dict-like, so use dict access
    try:
        agency = opportunity.get("agency")
        if agency is not None:
            # Shaped responses are dict-like
            assert isinstance(agency, dict), "Agency should be dict-like"
            assert "code" in agency or "name" in agency, (
                "Opportunity 'agency' must have 'code' or 'name' key"
            )
    except (AttributeError, KeyError):
        pass  # agency not in shape

    try:
        place_of_perf = opportunity.get("place_of_performance")
        if place_of_perf is not None:
            # Shaped responses are dict-like
            assert isinstance(place_of_perf, dict), "place_of_performance should be dict-like"
            # Check for any location-related keys
            location_keys = ["city", "state", "country", "state_code", "country_code", "zip_code"]
            assert any(key in place_of_perf for key in location_keys), (
                f"Opportunity 'place_of_performance' must have at least one location key: {location_keys}"
            )
    except (AttributeError, KeyError):
        pass  # place_of_performance not in shape


@pytest.mark.vcr()
@pytest.mark.integration
class TestOpportunitiesIntegration:
    """Integration tests for opportunity endpoints using production data"""

    @handle_api_exceptions("opportunities")
    @pytest.mark.parametrize(
        "shape_name,shape_value",
        [
            ("default", None),
            ("minimal", ShapeConfig.OPPORTUNITIES_MINIMAL),
            (
                "detailed",
                "opportunity_id,title,description,solicitation_number,response_deadline,first_notice_date,last_notice_date,active,naics_code,psc_code,set_aside,sam_url,office(*),place_of_performance(*)",
            ),
            ("custom", "opportunity_id,title,solicitation_number"),
        ],
    )
    def test_list_opportunities_with_shapes(self, tango_client, shape_name, shape_value):
        """Test listing opportunities with different shapes

        Validates:
        - Opportunities endpoint exists and returns data
        - Paginated response structure
        - Opportunity parsing with various shapes
        - Required fields are present regardless of shape
        """
        kwargs = {"limit": 5}
        if shape_value is not None:
            kwargs["shape"] = shape_value

        response = tango_client.list_opportunities(**kwargs)

        # Validate response structure
        validate_pagination(response)

        # If we have results, validate them
        if response.results:
            opportunity = response.results[0]
            validate_opportunity_fields(opportunity, minimal=(shape_name in ("default", "minimal")))
            validate_no_parsing_errors(opportunity)

            # Verify required fields are present
            # Note: key may not be present in minimal shapes
            try:
                if opportunity.key is not None:
                    assert isinstance(opportunity.key, str), (
                        "Opportunity key should be string if present"
                    )
            except AttributeError:
                pass  # key not in shape - acceptable for minimal shapes
            assert opportunity.title is not None, "Opportunity title should be present"
            assert opportunity.solicitation_number is not None, (
                "Solicitation number should be present"
            )

    @handle_api_exceptions("opportunities")
    def test_opportunity_field_types(self, tango_client):
        """Test that all opportunity field types are correctly parsed

        Validates:
        - Datetime fields are parsed as datetime objects
        - String fields are strings
        - Nested objects (agency, place_of_performance) are parsed correctly
        - Dict fields (links, contact_info, award) are dicts when present
        """
        response = tango_client.list_opportunities(limit=10)

        # Validate response structure
        validate_pagination(response)

        # If we have results, validate them
        if response.results:
            for opportunity in response.results:
                # Validate field types
                validate_opportunity_fields(opportunity, minimal=True)
                validate_no_parsing_errors(opportunity)

                # Additional type checks for specific fields
                # Note: key may not be present in minimal shapes
                try:
                    if opportunity.key is not None:
                        assert isinstance(opportunity.key, str), (
                            f"key should be string, got {type(opportunity.key)}"
                        )
                except AttributeError:
                    pass  # key not in shape - acceptable for minimal shapes

                assert isinstance(opportunity.title, str), (
                    f"title should be string, got {type(opportunity.title)}"
                )

                assert isinstance(opportunity.solicitation_number, str), (
                    f"solicitation_number should be string, got {type(opportunity.solicitation_number)}"
                )

                try:
                    if opportunity.description is not None:
                        assert isinstance(opportunity.description, str), (
                            f"description should be string, got {type(opportunity.description)}"
                        )
                except AttributeError:
                    pass  # description not in shape

                try:
                    if opportunity.notice_type is not None:
                        assert isinstance(opportunity.notice_type, str), (
                            f"notice_type should be string, got {type(opportunity.notice_type)}"
                        )
                except AttributeError:
                    pass  # notice_type not in shape

                try:
                    if opportunity.posted_date is not None:
                        assert isinstance(opportunity.posted_date, datetime), (
                            f"posted_date should be datetime, got {type(opportunity.posted_date)}"
                        )
                except AttributeError:
                    pass  # posted_date not in shape

                try:
                    if opportunity.response_deadline is not None:
                        assert isinstance(opportunity.response_deadline, datetime), (
                            f"response_deadline should be datetime, got {type(opportunity.response_deadline)}"
                        )
                except AttributeError:
                    pass  # response_deadline not in shape

                try:
                    if opportunity.archive_date is not None:
                        assert isinstance(opportunity.archive_date, datetime), (
                            f"archive_date should be datetime, got {type(opportunity.archive_date)}"
                        )
                except AttributeError:
                    pass  # archive_date not in shape

                # Validate nested agency object if present
                try:
                    if opportunity.agency is not None:
                        assert hasattr(opportunity.agency, "code"), (
                            "agency should have 'code' attribute"
                        )
                        assert hasattr(opportunity.agency, "name"), (
                            "agency should have 'name' attribute"
                        )
                except AttributeError:
                    pass  # agency not in shape

                # Validate nested place_of_performance object if present
                try:
                    if opportunity.place_of_performance is not None:
                        assert hasattr(opportunity.place_of_performance, "city"), (
                            "place_of_performance should have 'city' attribute"
                        )
                except AttributeError:
                    pass  # place_of_performance not in shape

                # Validate dict fields if present
                try:
                    if opportunity.links is not None:
                        assert isinstance(opportunity.links, dict), (
                            f"links should be dict, got {type(opportunity.links)}"
                        )
                except AttributeError:
                    pass  # links not in shape

                try:
                    if opportunity.contact_info is not None:
                        assert isinstance(opportunity.contact_info, dict), (
                            f"contact_info should be dict, got {type(opportunity.contact_info)}"
                        )
                except AttributeError:
                    pass  # contact_info not in shape

                try:
                    if opportunity.award is not None:
                        assert isinstance(opportunity.award, dict), (
                            f"award should be dict, got {type(opportunity.award)}"
                        )
                except AttributeError:
                    pass  # award not in shape
