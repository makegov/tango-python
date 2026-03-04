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
            page2 = production_client.list_contracts(
                cursor=page1.cursor, limit=2, shape=ShapeConfig.CONTRACTS_MINIMAL
            )

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

    @handle_rate_limit
    @handle_auth_error
    def test_list_idvs_basic(self, production_client):
        """Test basic IDV listing

        Validates:
        - Basic IDV listing works
        - Response parsing is correct
        - Pagination structure is valid
        """
        response = production_client.list_idvs(limit=5)

        # Validate response structure
        validate_pagination(response)
        # IDVs may be empty, so we just validate structure
        assert response.count >= 0, "Count should be non-negative"

        if len(response.results) > 0:
            idv = response.results[0]
            validate_no_parsing_errors(idv)
            # Verify required fields are present
            assert idv.get("key") is not None, "IDV key should be present"

    @handle_rate_limit
    @handle_auth_error
    def test_get_idv(self, production_client):
        """Test getting a specific IDV

        Validates:
        - Single IDV retrieval works
        - IDV parsing is correct
        """
        # First, get an IDV key from listing
        list_response = production_client.list_idvs(limit=1)
        if not list_response.results:
            pytest.skip("No IDVs available to test get_idv")

        idv_key = (
            list_response.results[0].get("key")
            if isinstance(list_response.results[0], dict)
            else list_response.results[0].key
        )
        assert idv_key is not None, "IDV key should be present"

        idv = production_client.get_idv(idv_key)

        validate_no_parsing_errors(idv)
        assert idv.get("key") is not None, "IDV key should be present"
        assert idv.get("key") == idv_key if isinstance(idv, dict) else idv.key == idv_key, (
            "Returned IDV should match requested key"
        )

    @handle_rate_limit
    @handle_auth_error
    def test_list_vehicles_basic(self, production_client):
        """Test basic vehicle listing

        Validates:
        - Basic vehicle listing works
        - Response parsing is correct
        - Pagination structure is valid
        """
        response = production_client.list_vehicles(limit=5)

        # Validate response structure
        validate_pagination(response)
        # Vehicles may be empty, so we just validate structure
        assert response.count >= 0, "Count should be non-negative"

        if len(response.results) > 0:
            vehicle = response.results[0]
            validate_no_parsing_errors(vehicle)
            # Verify required fields are present
            assert vehicle.get("uuid") is not None or hasattr(vehicle, "uuid"), (
                "Vehicle uuid should be present"
            )

    @handle_rate_limit
    @handle_auth_error
    def test_get_vehicle(self, production_client):
        """Test getting a specific vehicle

        Validates:
        - Single vehicle retrieval works
        - Vehicle parsing is correct
        """
        # First, get a vehicle UUID from listing
        list_response = production_client.list_vehicles(limit=1)
        if not list_response.results:
            pytest.skip("No vehicles available to test get_vehicle")

        vehicle_uuid = (
            list_response.results[0].get("uuid")
            if isinstance(list_response.results[0], dict)
            else list_response.results[0].uuid
        )
        assert vehicle_uuid is not None, "Vehicle UUID should be present"

        vehicle = production_client.get_vehicle(vehicle_uuid)

        validate_no_parsing_errors(vehicle)
        assert vehicle.get("uuid") is not None or hasattr(vehicle, "uuid"), (
            "Vehicle uuid should be present"
        )

    # ============================================================================
    # OTA Endpoints
    # ============================================================================

    @handle_rate_limit
    @handle_auth_error
    def test_list_otas_basic(self, production_client):
        """Test basic OTA listing

        Validates:
        - Basic OTA listing works
        - Response parsing is correct
        - Pagination structure is valid
        """
        response = production_client.list_otas(limit=5)

        # Validate response structure
        validate_pagination(response)
        # OTAs may be empty, so we just validate structure
        assert response.count >= 0, "Count should be non-negative"

        if len(response.results) > 0:
            ota = response.results[0]
            validate_no_parsing_errors(ota)
            # Verify required fields are present
            assert ota.get("key") is not None, "OTA key should be present"

    @handle_rate_limit
    @handle_auth_error
    def test_get_ota(self, production_client):
        """Test getting a specific OTA

        Validates:
        - Single OTA retrieval works
        - OTA parsing is correct
        """
        # First, get an OTA key from listing
        list_response = production_client.list_otas(limit=1)
        if not list_response.results:
            pytest.skip("No OTAs available to test get_ota")

        ota_key = (
            list_response.results[0].get("key")
            if isinstance(list_response.results[0], dict)
            else list_response.results[0].key
        )
        assert ota_key is not None, "OTA key should be present"

        ota = production_client.get_ota(ota_key)

        validate_no_parsing_errors(ota)
        assert ota.get("key") is not None, "OTA key should be present"

    # ============================================================================
    # OTIDV Endpoints
    # ============================================================================

    @handle_rate_limit
    @handle_auth_error
    def test_list_otidvs_basic(self, production_client):
        """Test basic OTIDV listing

        Validates:
        - Basic OTIDV listing works
        - Response parsing is correct
        - Pagination structure is valid
        """
        response = production_client.list_otidvs(limit=5)

        # Validate response structure
        validate_pagination(response)
        # OTIDVs may be empty, so we just validate structure
        assert response.count >= 0, "Count should be non-negative"

        if len(response.results) > 0:
            otidv = response.results[0]
            validate_no_parsing_errors(otidv)
            # Verify required fields are present
            assert otidv.get("key") is not None, "OTIDV key should be present"

    @handle_rate_limit
    @handle_auth_error
    def test_get_otidv(self, production_client):
        """Test getting a specific OTIDV

        Validates:
        - Single OTIDV retrieval works
        - OTIDV parsing is correct
        """
        # First, get an OTIDV key from listing
        list_response = production_client.list_otidvs(limit=1)
        if not list_response.results:
            pytest.skip("No OTIDVs available to test get_otidv")

        otidv_key = (
            list_response.results[0].get("key")
            if isinstance(list_response.results[0], dict)
            else list_response.results[0].key
        )
        assert otidv_key is not None, "OTIDV key should be present"

        otidv = production_client.get_otidv(otidv_key)

        validate_no_parsing_errors(otidv)
        assert otidv.get("key") is not None, "OTIDV key should be present"

    # ============================================================================
    # Organization Endpoints
    # ============================================================================

    @handle_rate_limit
    @handle_auth_error
    def test_list_organizations(self, production_client):
        """Test organization listing

        Validates:
        - Organization listing works
        - Response parsing is correct
        - Pagination structure is valid
        """
        response = production_client.list_organizations(limit=5)

        validate_pagination(response)
        assert response.count >= 0, "Count should be non-negative"

        if len(response.results) > 0:
            org = response.results[0]
            validate_no_parsing_errors(org)
            # Organizations should have fh_key or key
            has_key = org.get("fh_key") is not None or org.get("key") is not None
            assert has_key, "Organization should have fh_key or key"

    @handle_rate_limit
    @handle_auth_error
    def test_get_organization(self, production_client):
        """Test getting a specific organization

        Validates:
        - Single organization retrieval works
        - Organization parsing is correct
        """
        # First, get an organization fh_key from listing
        list_response = production_client.list_organizations(limit=1)
        if not list_response.results:
            pytest.skip("No organizations available to test get_organization")

        org = list_response.results[0]
        fh_key = org.get("fh_key") if isinstance(org, dict) else getattr(org, "fh_key", None)
        if fh_key is None:
            pytest.skip("First organization has no fh_key")

        result = production_client.get_organization(fh_key)

        validate_no_parsing_errors(result)

    # ============================================================================
    # Office Endpoints
    # ============================================================================

    @handle_rate_limit
    @handle_auth_error
    def test_list_offices(self, production_client):
        """Test office listing

        Validates:
        - Office listing works
        - Response parsing is correct
        - Pagination structure is valid
        """
        response = production_client.list_offices(limit=5)

        validate_pagination(response)
        assert response.count >= 0, "Count should be non-negative"

        if len(response.results) > 0:
            office = response.results[0]
            # Offices are returned as raw dicts
            assert isinstance(office, dict), "Office should be a dict"

    @handle_rate_limit
    @handle_auth_error
    def test_get_office(self, production_client):
        """Test getting a specific office

        Validates:
        - Single office retrieval works
        - Office data is returned
        """
        # First, get an office code from listing
        list_response = production_client.list_offices(limit=1)
        if not list_response.results:
            pytest.skip("No offices available to test get_office")

        office = list_response.results[0]
        # API returns 'office_code', not 'code'
        code = (
            office.get("office_code")
            if isinstance(office, dict)
            else getattr(office, "office_code", None)
        )
        if code is None:
            pytest.skip("First office has no office_code")

        result = production_client.get_office(code)

        assert isinstance(result, dict), "Office should be a dict"
        assert result.get("office_code") is not None, "Office code should be present"

    # ============================================================================
    # Subaward Endpoints
    # ============================================================================

    @handle_rate_limit
    @handle_auth_error
    def test_list_subawards(self, production_client):
        """Test subaward listing

        Validates:
        - Subaward listing works
        - Response parsing is correct
        - Pagination structure is valid
        """
        response = production_client.list_subawards(limit=5)

        validate_pagination(response)
        assert response.count >= 0, "Count should be non-negative"

        if len(response.results) > 0:
            subaward = response.results[0]
            validate_no_parsing_errors(subaward)
            # Subawards should have id or award_key
            has_id = subaward.get("id") is not None or subaward.get("award_key") is not None
            assert has_id, "Subaward should have id or award_key"

    # ============================================================================
    # NAICS Endpoints
    # ============================================================================

    @handle_rate_limit
    @handle_auth_error
    def test_list_naics(self, production_client):
        """Test NAICS code listing

        Validates:
        - NAICS listing works
        - Response parsing is correct
        - Pagination structure is valid
        """
        response = production_client.list_naics(limit=5)

        validate_pagination(response)
        assert response.count >= 0, "Count should be non-negative"

        if len(response.results) > 0:
            naics = response.results[0]
            # NAICS codes are returned as raw dicts
            assert isinstance(naics, dict), "NAICS should be a dict"
            # Should have code field
            assert naics.get("code") is not None, "NAICS code should be present"

    # ============================================================================
    # Assistance Endpoints
    # ============================================================================

    # ============================================================================
    # Forecast Endpoints
    # ============================================================================

    @handle_rate_limit
    @handle_auth_error
    def test_list_forecasts(self, production_client):
        """Test forecast listing

        Validates:
        - Forecast listing works
        - Response parsing is correct
        - Pagination structure is valid
        """
        response = production_client.list_forecasts(limit=5)

        validate_pagination(response)
        assert response.count >= 0, "Count should be non-negative"

        if len(response.results) > 0:
            forecast = response.results[0]
            validate_no_parsing_errors(forecast)

    # ============================================================================
    # Notice Endpoints
    # ============================================================================

    @handle_rate_limit
    @handle_auth_error
    def test_list_notices(self, production_client):
        """Test notice listing

        Validates:
        - Notice listing works
        - Response parsing is correct
        - Pagination structure is valid
        """
        response = production_client.list_notices(limit=5)

        validate_pagination(response)
        assert response.count >= 0, "Count should be non-negative"

        if len(response.results) > 0:
            notice = response.results[0]
            validate_no_parsing_errors(notice)

    # ============================================================================
    # Grant Endpoints
    # ============================================================================

    @handle_rate_limit
    @handle_auth_error
    def test_list_grants(self, production_client):
        """Test grant listing

        Validates:
        - Grant listing works
        - Response parsing is correct
        - Pagination structure is valid
        """
        response = production_client.list_grants(limit=5)

        validate_pagination(response)
        assert response.count >= 0, "Count should be non-negative"

        if len(response.results) > 0:
            grant = response.results[0]
            validate_no_parsing_errors(grant)

    # ============================================================================
    # Webhook Endpoints
    # ============================================================================

    @handle_rate_limit
    @handle_auth_error
    def test_list_webhook_event_types(self, production_client):
        """Test webhook event types listing

        Validates:
        - Webhook event types endpoint works
        - Response structure is valid
        """
        response = production_client.list_webhook_event_types()

        # Response should have event_types list
        assert hasattr(response, "event_types"), "Response should have event_types"
        assert isinstance(response.event_types, list), "event_types should be a list"

        # Response should have subject_types list
        assert hasattr(response, "subject_types"), "Response should have subject_types"
        assert isinstance(response.subject_types, list), "subject_types should be a list"

    @handle_rate_limit
    @handle_auth_error
    def test_list_webhook_endpoints(self, production_client):
        """Test webhook endpoints listing

        Validates:
        - Webhook endpoints listing works
        - Response parsing is correct
        """
        response = production_client.list_webhook_endpoints(limit=5)

        validate_pagination(response)
        assert response.count >= 0, "Count should be non-negative"

    @handle_rate_limit
    @handle_auth_error
    def test_list_webhook_subscriptions(self, production_client):
        """Test webhook subscriptions listing

        Validates:
        - Webhook subscriptions listing works
        - Response parsing is correct
        """
        response = production_client.list_webhook_subscriptions()

        validate_pagination(response)
        assert response.count >= 0, "Count should be non-negative"
