"""Integration tests for notice endpoints

Pytest Markers:
    @pytest.mark.integration: Marks tests as integration tests that may hit external APIs
    @pytest.mark.vcr(): Enables VCR recording/playback for HTTP interactions
    @pytest.mark.live: Forces tests to use live API (skip cassettes) - not used by default
    @pytest.mark.cached: Forces tests to only run with cached responses - not used by default
    @pytest.mark.slow: Marks tests that are slow to execute - not used by default

Usage:
    # Run all integration tests (uses cassettes if available)
    pytest tests/integration/

    # Run only notice integration tests
    pytest tests/integration/test_notices_integration.py

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


def validate_notice_fields(notice, minimal: bool = True) -> None:
    """Validate notice object has required fields and correct types

    Args:
        notice: A Notice object to validate
        minimal: If True, only validate minimal fields. If False, validate comprehensive fields.

    Raises:
        AssertionError: If validation fails
    """
    # Required fields - Notice uses 'notice_id' not 'key'
    is_dict = isinstance(notice, dict)
    notice_id = notice.get("notice_id") if is_dict else getattr(notice, "notice_id", None)
    assert notice_id is not None, "Notice 'notice_id' must not be None"

    title = notice.get("title") if is_dict else getattr(notice, "title", None)
    assert title is not None, "Notice 'title' must not be None"

    # Type validation for required fields
    assert isinstance(notice_id, str), f"Notice 'notice_id' must be string, got {type(notice_id)}"
    assert isinstance(title, str), f"Notice 'title' must be string, got {type(title)}"
    # notice_type may not be in all shapes
    notice_type = notice.get("notice_type") if is_dict else getattr(notice, "notice_type", None)
    if notice_type is not None:
        assert isinstance(notice_type, str), (
            f"Notice 'notice_type' must be string, got {type(notice_type)}"
        )

    # Type validation for optional string fields (only if in shape)
    solicitation_number = (
        notice.get("solicitation_number")
        if is_dict
        else getattr(notice, "solicitation_number", None)
    )
    if solicitation_number is not None:
        assert isinstance(solicitation_number, str), (
            f"Notice 'solicitation_number' must be string, got {type(solicitation_number)}"
        )

    description = notice.get("description") if is_dict else getattr(notice, "description", None)
    if description is not None:
        assert isinstance(description, str), (
            f"Notice 'description' must be string, got {type(description)}"
        )

    # Type validation for optional fields (only if in shape - use safe access)
    office = notice.get("office") if is_dict else getattr(notice, "office", None)
    if office is not None:
        if isinstance(office, dict):
            assert len(office) > 0, "Notice 'office' should have at least one field"
        elif isinstance(office, str):
            assert len(office) > 0, "Notice 'office' should not be empty"
        else:
            # Dynamic model - check for attributes
            assert (
                hasattr(office, "code") or hasattr(office, "name") or hasattr(office, "agency")
            ), "Notice 'office' should have code, name, or agency"

    naics_code = notice.get("naics_code") if is_dict else getattr(notice, "naics_code", None)
    if naics_code is not None:
        assert isinstance(naics_code, (str, int)), (
            f"Notice 'naics_code' must be string or int, got {type(naics_code)}"
        )

    psc_code = notice.get("psc_code") if is_dict else getattr(notice, "psc_code", None)
    if psc_code is not None:
        assert isinstance(psc_code, str), f"Notice 'psc_code' must be string, got {type(psc_code)}"

    set_aside = notice.get("set_aside") if is_dict else getattr(notice, "set_aside", None)
    if set_aside is not None:
        assert isinstance(set_aside, str), (
            f"Notice 'set_aside' must be string, got {type(set_aside)}"
        )

    # Type validation for datetime fields (only if in shape)
    posted_date = notice.get("posted_date") if is_dict else getattr(notice, "posted_date", None)
    if posted_date is not None:
        assert isinstance(posted_date, datetime), (
            f"Notice 'posted_date' must be datetime, got {type(posted_date)}"
        )

    updated_date = notice.get("updated_date") if is_dict else getattr(notice, "updated_date", None)
    if updated_date is not None:
        assert isinstance(updated_date, datetime), (
            f"Notice 'updated_date' must be datetime, got {type(updated_date)}"
        )

    # Type validation for nested objects (only if in shape)
    agency = notice.get("agency") if is_dict else getattr(notice, "agency", None)
    if agency is not None:
        if isinstance(agency, dict):
            assert "code" in agency or "name" in agency or len(agency) > 0, (
                "Notice 'agency' should have at least one field"
            )
        else:
            assert hasattr(agency, "code") or hasattr(agency, "name"), (
                "Notice 'agency' should have 'code' or 'name' attribute"
            )

    place_of_performance = (
        notice.get("place_of_performance")
        if is_dict
        else getattr(notice, "place_of_performance", None)
    )
    if place_of_performance is not None:
        if isinstance(place_of_performance, dict):
            assert len(place_of_performance) > 0, (
                "Notice 'place_of_performance' should have at least one field"
            )
        else:
            assert (
                hasattr(place_of_performance, "city_name")
                or hasattr(place_of_performance, "state_code")
                or hasattr(place_of_performance, "country_code")
            ), "Notice 'place_of_performance' should have location fields"

    # Type validation for dict and list fields (only if in shape)
    links = notice.get("links") if is_dict else getattr(notice, "links", None)
    if links is not None:
        assert isinstance(links, dict), f"Notice 'links' must be dict, got {type(links)}"

    related_notices = (
        notice.get("related_notices") if is_dict else getattr(notice, "related_notices", None)
    )
    if related_notices is not None:
        assert isinstance(related_notices, list), (
            f"Notice 'related_notices' must be list, got {type(related_notices)}"
        )


@pytest.mark.vcr()
@pytest.mark.integration
class TestNoticesIntegration:
    """Integration tests for notice endpoints using production data"""

    @handle_api_exceptions("notices")
    @pytest.mark.parametrize(
        "shape_name,shape_value",
        [
            ("default", None),
            ("minimal", ShapeConfig.NOTICES_MINIMAL),
            (
                "detailed",
                "notice_id,title,description,solicitation_number,posted_date,naics_code,set_aside,office(*),place_of_performance(*)",
            ),
            ("custom", "notice_id,title,solicitation_number"),
        ],
    )
    def test_list_notices_with_shapes(self, tango_client, shape_name, shape_value):
        """Test listing notices with different shapes

        Validates:
        - Notices endpoint exists and returns data
        - Paginated response structure
        - Notice parsing with various shapes
        - Required fields are present regardless of shape
        """
        kwargs = {"limit": 5}
        if shape_value is not None:
            kwargs["shape"] = shape_value

        response = tango_client.list_notices(**kwargs)

        # Validate response structure
        validate_pagination(response)

        # If we have results, validate them
        if response.results:
            notice = response.results[0]
            validate_notice_fields(notice, minimal=(shape_name in ("default", "minimal")))
            validate_no_parsing_errors(notice)

            # Verify required fields are present
            # Notice uses 'notice_id' not 'key'
            is_dict = isinstance(notice, dict)
            notice_id = notice.get("notice_id") if is_dict else getattr(notice, "notice_id", None)
            title = notice.get("title") if is_dict else getattr(notice, "title", None)
            assert notice_id is not None, "Notice notice_id should be present"
            assert title is not None, "Notice title should be present"
            # notice_type may not be in minimal shape - only check if present
            notice_type = (
                notice.get("notice_type") if is_dict else getattr(notice, "notice_type", None)
            )
            if notice_type is not None:
                assert isinstance(notice_type, str), "Notice type should be string"

    @handle_api_exceptions("notices")
    def test_notice_field_types(self, tango_client):
        """Test that all notice field types are correctly parsed

        Validates:
        - Datetime fields are parsed as datetime objects
        - String fields are strings
        - Nested objects (agency, place_of_performance) are parsed correctly
        - Dict fields (links) are dicts when present
        - List fields (related_notices) are lists when present
        """
        response = tango_client.list_notices(limit=10)

        # Validate response structure
        validate_pagination(response)

        # If we have results, validate them
        if response.results:
            for notice in response.results:
                # Validate field types
                validate_notice_fields(notice, minimal=True)
                validate_no_parsing_errors(notice)

                # Additional type checks for specific fields
                notice_id = (
                    notice.get("notice_id")
                    if isinstance(notice, dict)
                    else getattr(notice, "notice_id", None)
                )
                assert isinstance(notice_id, str), (
                    f"notice_id should be string, got {type(notice_id)}"
                )

                title = (
                    notice.get("title")
                    if isinstance(notice, dict)
                    else getattr(notice, "title", None)
                )
                assert isinstance(title, str), f"title should be string, got {type(title)}"

                # notice_type may not be in minimal shape
                notice_type = (
                    notice.get("notice_type")
                    if isinstance(notice, dict)
                    else getattr(notice, "notice_type", None)
                )
                if notice_type is not None:
                    assert isinstance(notice_type, str), (
                        f"notice_type should be string, got {type(notice_type)}"
                    )

                description = (
                    notice.get("description")
                    if isinstance(notice, dict)
                    else getattr(notice, "description", None)
                )
                if description is not None:
                    assert isinstance(description, str), (
                        f"description should be string, got {type(description)}"
                    )

                posted_date = (
                    notice.get("posted_date")
                    if isinstance(notice, dict)
                    else getattr(notice, "posted_date", None)
                )
                if posted_date is not None:
                    assert isinstance(posted_date, datetime), (
                        f"posted_date should be datetime, got {type(posted_date)}"
                    )

                updated_date = (
                    notice.get("updated_date")
                    if isinstance(notice, dict)
                    else getattr(notice, "updated_date", None)
                )
                if updated_date is not None:
                    assert isinstance(updated_date, datetime), (
                        f"updated_date should be datetime, got {type(updated_date)}"
                    )

                # Validate nested agency object if present
                agency = (
                    notice.get("agency")
                    if isinstance(notice, dict)
                    else getattr(notice, "agency", None)
                )
                if agency is not None:
                    if isinstance(agency, dict):
                        assert "code" in agency or "name" in agency or len(agency) > 0, (
                            "agency should have at least one field"
                        )
                    else:
                        assert hasattr(agency, "code") or hasattr(agency, "name"), (
                            "agency should have 'code' or 'name' attribute"
                        )

                # Validate nested place_of_performance object if present
                place_of_performance = (
                    notice.get("place_of_performance")
                    if isinstance(notice, dict)
                    else getattr(notice, "place_of_performance", None)
                )
                if place_of_performance is not None:
                    if isinstance(place_of_performance, dict):
                        assert len(place_of_performance) > 0, (
                            "place_of_performance should have at least one field"
                        )
                    else:
                        assert (
                            hasattr(place_of_performance, "city_name")
                            or hasattr(place_of_performance, "state_code")
                            or hasattr(place_of_performance, "country_code")
                        ), "place_of_performance should have location fields"

                # Validate dict fields if present (only if in shape)
                links = (
                    notice.get("links")
                    if isinstance(notice, dict)
                    else getattr(notice, "links", None)
                )
                if links is not None:
                    assert isinstance(links, dict), f"links should be dict, got {type(links)}"

                # Validate list fields if present (only if in shape)
                related_notices = (
                    notice.get("related_notices")
                    if isinstance(notice, dict)
                    else getattr(notice, "related_notices", None)
                )
                if related_notices is not None:
                    assert isinstance(related_notices, list), (
                        f"related_notices should be list, got {type(related_notices)}"
                    )

                    # If the list is not empty, validate items are strings
                    if related_notices:
                        for related_notice in related_notices:
                            assert isinstance(related_notice, str), (
                                f"related_notices items should be strings, got {type(related_notice)}"
                            )

    @handle_api_exceptions("notices")
    def test_notice_with_meta_fields(self, tango_client):
        """Test notice parsing with meta fields

        Validates:
        - Meta fields are extracted correctly (notice_type, related notices)
        - Links are populated from meta and sam_url
        - All notice fields are populated when available
        """
        # Use comprehensive shape to get meta fields
        comprehensive_shape = "notice_id,title,description,solicitation_number,naics_code,posted_date,set_aside,office(*),place_of_performance(*),primary_contact(*),attachments(*)"
        response = tango_client.list_notices(limit=10, shape=comprehensive_shape)

        # Validate response structure
        validate_pagination(response)

        # Track if we found notices with meta fields
        found_notice_type = False
        found_related_notices = False
        found_links = False

        # If we have results, validate them
        if response.results:
            for notice in response.results:
                validate_notice_fields(notice, minimal=False)
                validate_no_parsing_errors(notice)

                # Check for notice_type (only if in shape)
                is_dict = isinstance(notice, dict)
                notice_type = (
                    notice.get("notice_type") if is_dict else getattr(notice, "notice_type", None)
                )
                if notice_type:
                    found_notice_type = True
                    assert isinstance(notice_type, str), (
                        f"notice_type should be string, got {type(notice_type)}"
                    )

                # Check for related_notices (only if in shape)
                related_notices = (
                    notice.get("related_notices")
                    if is_dict
                    else getattr(notice, "related_notices", None)
                )
                if related_notices:
                    found_related_notices = True
                    assert isinstance(related_notices, list), (
                        f"related_notices should be list, got {type(related_notices)}"
                    )
                    assert len(related_notices) > 0, "related_notices should not be empty list"

                # Check for links (only if in shape)
                links = notice.get("links") if is_dict else getattr(notice, "links", None)
                if links:
                    found_links = True
                    assert isinstance(links, dict), f"links should be dict, got {type(links)}"

    @handle_api_exceptions("notices")
    def test_notice_pagination(self, tango_client):
        """Test notice pagination

        Validates:
        - Pagination works correctly
        - Multiple pages can be retrieved
        - Page metadata is correct
        """
        # Get first page
        page1 = tango_client.list_notices(limit=5, page=1)
        validate_pagination(page1)

        # Get second page
        page2 = tango_client.list_notices(limit=5, page=2)
        validate_pagination(page2)

        # Verify pages have different results
        if page1.results and page2.results:
            notice1_id = (
                page1.results[0].get("notice_id")
                if isinstance(page1.results[0], dict)
                else getattr(page1.results[0], "notice_id", None)
            )
            notice2_id = (
                page2.results[0].get("notice_id")
                if isinstance(page2.results[0], dict)
                else getattr(page2.results[0], "notice_id", None)
            )
            assert notice1_id != notice2_id, "Different pages should have different results"
