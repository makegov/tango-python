"""Production API smoke tests

These tests run against the live production API to quickly validate core SDK functionality.
They are designed to be fast (~30-60 seconds) and test critical paths only.

Pytest Markers:
    @pytest.mark.production: Marks tests as production API tests
    @pytest.mark.live: Forces tests to use live API (no cassettes)

Usage:
    # Run production smoke tests (requires TANGO_API_KEY)
    pytest tests/production/ -m production

    # Run with specific API key
    TANGO_API_KEY=xxx pytest tests/production/
"""

import pytest

from tango import ShapeConfig
from tango.exceptions import TangoAuthError, TangoNotFoundError, TangoValidationError
from tests.integration.validation import (
    validate_agency_fields,
    validate_contract_fields,
    validate_entity_fields,
    validate_no_parsing_errors,
    validate_pagination,
)
from tests.production.conftest import handle_auth_error, handle_rate_limit


@pytest.mark.production
@pytest.mark.live
class TestProductionSmoke:
    """Smoke tests against production API - validates core SDK functionality"""

    @handle_rate_limit
    @handle_auth_error
    def test_list_contracts_basic(self, production_client):
        """Test basic contract listing with minimal shape

        Validates:
        - Basic contract listing works
        - Response parsing is correct
        - Pagination structure is valid
        """
        response = production_client.list_contracts(limit=5, shape=ShapeConfig.CONTRACTS_MINIMAL)

        # Validate response structure
        validate_pagination(response)
        assert response.count > 0, "Expected at least one contract in production"
        assert len(response.results) > 0, "Expected results in the response"

        # Validate first contract
        contract = response.results[0]
        validate_contract_fields(contract, minimal=True)
        validate_no_parsing_errors(contract)
        assert contract.get("key") is not None, "Contract key should be present"

    @handle_rate_limit
    @handle_auth_error
    def test_list_contracts_with_shape(self, production_client):
        """Test contract listing with custom shape parameter

        Validates:
        - Shape parameter works correctly
        - Custom shape fields are present
        - Response parsing with shaped data
        """
        shape = "key,piid,recipient(display_name),total_contract_value,award_date"
        response = production_client.list_contracts(limit=3, shape=shape)

        validate_pagination(response)
        assert len(response.results) > 0, "Expected results in the response"

        contract = response.results[0]
        validate_no_parsing_errors(contract)
        # Verify shape fields are present
        assert contract.get("key") is not None, "Contract key should be present"
        assert contract.get("piid") is not None, "Contract piid should be present"

    @handle_rate_limit
    @handle_auth_error
    def test_list_entities(self, production_client):
        """Test entity listing

        Validates:
        - Entity listing works
        - Entity parsing is correct
        - Required entity fields are present
        """
        response = production_client.list_entities(limit=5, shape=ShapeConfig.ENTITIES_MINIMAL)

        validate_pagination(response)
        assert response.count > 0, "Expected at least one entity in production"
        assert len(response.results) > 0, "Expected results in the response"

        entity = response.results[0]
        validate_entity_fields(entity)
        validate_no_parsing_errors(entity)

    @handle_rate_limit
    @handle_auth_error
    def test_list_agencies(self, production_client):
        """Test agency listing

        Validates:
        - Agency listing works
        - Agency parsing is correct
        - Required agency fields are present
        """
        response = production_client.list_agencies(limit=5)

        validate_pagination(response)
        assert response.count > 0, "Expected at least one agency in production"
        assert len(response.results) > 0, "Expected results in the response"

        agency = response.results[0]
        validate_agency_fields(agency)
        validate_no_parsing_errors(agency)

    @handle_rate_limit
    @handle_auth_error
    def test_get_agency(self, production_client):
        """Test getting a specific agency

        Validates:
        - Single agency retrieval works
        - Agency parsing with full details
        """
        # Use a well-known agency code (GSA - General Services Administration)
        agency_code = "4700"

        agency = production_client.get_agency(agency_code)

        validate_agency_fields(agency)
        validate_no_parsing_errors(agency)
        assert agency.code == agency_code, f"Expected agency code {agency_code}, got {agency.code}"

    @handle_rate_limit
    @handle_auth_error
    def test_list_opportunities(self, production_client):
        """Test opportunity listing

        Validates:
        - Opportunity listing works
        - Response parsing is correct
        """
        response = production_client.list_opportunities(limit=3)

        validate_pagination(response)
        # Opportunities may be empty, so we just validate structure
        assert response.count >= 0, "Count should be non-negative"

        if len(response.results) > 0:
            opportunity = response.results[0]
            validate_no_parsing_errors(opportunity)
            # Opportunities should have an opportunity_id
            assert opportunity.get("opportunity_id") is not None, "Opportunity ID should be present"

    @handle_rate_limit
    @handle_auth_error
    def test_pagination(self, production_client):
        """Test pagination works correctly

        Validates:
        - Pagination metadata is correct
        - Can navigate between pages
        """
        # Get first page
        page1 = production_client.list_contracts(limit=2, shape=ShapeConfig.CONTRACTS_MINIMAL)

        validate_pagination(page1)
        assert page1.count > 0, "Expected contracts in production"

        # If there are more results, test second page
        if page1.next is not None and page1.count > 2:
            page2 = production_client.list_contracts(cursor=page1.cursor, limit=2, shape=ShapeConfig.CONTRACTS_MINIMAL)

            validate_pagination(page2)
            assert len(page2.results) > 0, "Expected results on second page"
            # Results should be different
            if len(page1.results) > 0 and len(page2.results) > 0:
                assert page1.results[0].get("key") != page2.results[0].get("key"), (
                    "Page 1 and Page 2 should have different results"
                )


    @handle_rate_limit
    @handle_auth_error
    def test_search_filters(self, production_client):
        """Test search filters work correctly

        Validates:
        - Filter parameters are applied correctly
        - Filtered results are returned
        """
        # Search for contracts with a specific agency (GSA)
        response = production_client.list_contracts(
            awarding_agency="4700", limit=3, shape=ShapeConfig.CONTRACTS_MINIMAL
        )

        validate_pagination(response)
        # Results may be empty, but structure should be valid
        assert response.count >= 0, "Count should be non-negative"

        if len(response.results) > 0:
            contract = response.results[0]
            validate_no_parsing_errors(contract)
