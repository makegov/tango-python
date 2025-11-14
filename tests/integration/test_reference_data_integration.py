"""Integration tests for reference data endpoints (business types)

Pytest Markers:
    @pytest.mark.integration: Marks tests as integration tests that may hit external APIs
    @pytest.mark.vcr(): Enables VCR recording/playback for HTTP interactions
    @pytest.mark.live: Forces tests to use live API (skip cassettes) - not used by default
    @pytest.mark.cached: Forces tests to only run with cached responses - not used by default
    @pytest.mark.slow: Marks tests that are slow to execute - not used by default

Usage:
    # Run all integration tests (uses cassettes if available)
    pytest tests/integration/

    # Run only reference data integration tests
    pytest tests/integration/test_reference_data_integration.py

    # Run with live API (requires TANGO_API_KEY environment variable)
    TANGO_USE_LIVE_API=true TANGO_API_KEY=xxx pytest tests/integration/

    # Refresh cassettes (re-record all interactions)
    TANGO_REFRESH_CASSETTES=true TANGO_API_KEY=xxx pytest tests/integration/
"""

import pytest

from tests.integration.validation import (
    validate_pagination,
)


@pytest.mark.vcr()
@pytest.mark.integration
class TestBusinessTypesIntegration:
    """Integration tests for business types endpoints using production data"""

    def test_list_business_types(self, tango_client):
        """Test listing business types

        Validates:
        - Paginated response structure
        - Business type parsing
        - Required fields are present
        """
        response = tango_client.list_business_types(limit=5)

        # Validate response structure
        validate_pagination(response)
        assert response.count >= 0, "Expected non-negative count"

        # If we have results, validate them
        if response.results:
            assert len(response.results) > 0, "Expected results in the response"

            # Validate first business type
            business_type = response.results[0]

            # Verify required fields are present
            assert business_type.code is not None, "Business type 'code' should be present"
            assert business_type.name is not None, "Business type 'name' should be present"
            assert isinstance(business_type.code, str), (
                f"Business type 'code' should be string, got {type(business_type.code)}"
            )
            assert isinstance(business_type.name, str), (
                f"Business type 'name' should be string, got {type(business_type.name)}"
            )

    def test_business_type_field_type_validation(self, tango_client):
        """Test that business type field types are correctly parsed

        Validates:
        - String fields are strings
        - All required fields are present
        - Optional fields have correct types when present
        """
        response = tango_client.list_business_types(limit=10)

        # If we have results, validate field types
        if response.results:
            for business_type in response.results:
                # Required fields
                assert isinstance(business_type.code, str), (
                    f"'code' should be string, got {type(business_type.code)}"
                )
                assert isinstance(business_type.name, str), (
                    f"'name' should be string, got {type(business_type.name)}"
                )

                # Optional string fields
                if business_type.description is not None:
                    assert isinstance(business_type.description, str), (
                        f"'description' should be string, got {type(business_type.description)}"
                    )

                if business_type.business_type_code is not None:
                    assert isinstance(business_type.business_type_code, str), (
                        f"'business_type_code' should be string, got {type(business_type.business_type_code)}"
                    )

    def test_business_type_parsing_consistency(self, tango_client):
        """Test that business type parsing is consistent across multiple results

        Validates:
        - All business types in a list parse successfully
        - No parsing errors across different business types
        - Consistent field types across all results
        """
        response = tango_client.list_business_types(limit=25)

        # If we have results, validate all parse successfully
        if response.results:
            for business_type in response.results:
                assert business_type.code is not None, "Each business type should have a code"
                assert business_type.name is not None, "Each business type should have a name"
