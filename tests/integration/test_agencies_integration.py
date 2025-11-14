"""Integration tests for agency endpoints

Pytest Markers:
    @pytest.mark.integration: Marks tests as integration tests that may hit external APIs
    @pytest.mark.vcr(): Enables VCR recording/playback for HTTP interactions
    @pytest.mark.live: Forces tests to use live API (skip cassettes) - not used by default
    @pytest.mark.cached: Forces tests to only run with cached responses - not used by default
    @pytest.mark.slow: Marks tests that are slow to execute - not used by default

Usage:
    # Run all integration tests (uses cassettes if available)
    pytest tests/integration/

    # Run only agency integration tests
    pytest tests/integration/test_agencies_integration.py

    # Run with live API (requires TANGO_API_KEY environment variable)
    TANGO_USE_LIVE_API=true TANGO_API_KEY=xxx pytest tests/integration/

    # Refresh cassettes (re-record all interactions)
    TANGO_REFRESH_CASSETTES=true TANGO_API_KEY=xxx pytest tests/integration/
"""

import pytest

from tests.integration.validation import (
    validate_agency_fields,
    validate_no_parsing_errors,
    validate_pagination,
)


@pytest.mark.vcr()
@pytest.mark.integration
class TestAgenciesIntegration:
    """Integration tests for agency endpoints using production data"""

    def test_list_agencies(self, tango_client):
        """Test listing agencies with production data

        Validates:
        - Paginated response structure
        - Agency parsing from real API responses
        - Required agency fields are present
        """
        response = tango_client.list_agencies(limit=10)

        # Validate response structure
        validate_pagination(response)
        assert response.count > 0, "Expected at least one agency in the system"
        assert len(response.results) > 0, "Expected results in the response"

        agency = response.results[0]
        validate_agency_fields(agency)
        validate_no_parsing_errors(agency)

    def test_get_agency(self, tango_client):
        """Test getting a specific agency by code

        Validates:
        - Single agency retrieval
        - Agency parsing with full details
        - All agency fields are correctly typed
        """
        # Use a well-known agency code (GSA - General Services Administration)
        agency_code = "4700"

        agency = tango_client.get_agency(agency_code)

        # Validate agency fields and parsing
        validate_agency_fields(agency)
        validate_no_parsing_errors(agency)

        assert agency.abbreviation == "GSA", (
            f"Expected agency abbreviation GSA, got {agency.abbreviation}"
        )
        # Verify we got the correct agency
        assert agency.code == agency_code, f"Expected agency code {agency_code}, got {agency.code}"
