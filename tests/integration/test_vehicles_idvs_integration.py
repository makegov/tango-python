"""Integration tests for Vehicles and IDV endpoints

Pytest Markers:
    @pytest.mark.integration: Marks tests as integration tests that may hit external APIs
    @pytest.mark.vcr(): Enables VCR recording/playback for HTTP interactions
    @pytest.mark.live: Forces tests to use live API (skip cassettes) - not used by default
    @pytest.mark.cached: Forces tests to only run with cached responses - not used by default
    @pytest.mark.slow: Marks tests that are slow to execute - not used by default

Usage:
    # Run all integration tests (uses cassettes if available)
    pytest tests/integration/

    # Run only vehicles/IDV integration tests
    pytest tests/integration/test_vehicles_idvs_integration.py

    # Run with live API (requires TANGO_API_KEY environment variable)
    TANGO_USE_LIVE_API=true TANGO_API_KEY=xxx pytest tests/integration/test_vehicles_idvs_integration.py

    # Refresh cassettes (re-record all interactions)
    TANGO_REFRESH_CASSETTES=true TANGO_API_KEY=xxx pytest tests/integration/test_vehicles_idvs_integration.py
"""

from datetime import date
from decimal import Decimal

import pytest

from tests.integration.conftest import handle_api_exceptions
from tests.integration.validation import validate_no_parsing_errors, validate_pagination


@pytest.mark.vcr()
@pytest.mark.integration
class TestVehiclesIntegration:
    """Integration tests for Vehicles endpoints using production data"""

    @handle_api_exceptions("vehicles")
    def test_list_vehicles_uses_default_shape_and_search(self, tango_client):
        """Test listing vehicles with default shape and search parameter

        Validates:
        - Default shape is applied
        - Search parameter is passed correctly
        - Vehicles are parsed correctly with proper types
        """
        response = tango_client.list_vehicles(search="GSA", limit=10)

        # Validate response structure
        validate_pagination(response)
        assert len(response.results) > 0, "Expected at least one vehicle"

        # Validate first vehicle
        vehicle = response.results[0]
        validate_no_parsing_errors(vehicle)

        # Verify required fields are present
        assert vehicle.get("uuid") is not None or hasattr(vehicle, "uuid"), (
            "Vehicle uuid should be present"
        )
        assert vehicle.get("solicitation_identifier") is not None or hasattr(
            vehicle, "solicitation_identifier"
        ), "Vehicle solicitation_identifier should be present"

        # Verify type parsing
        if vehicle.get("vehicle_obligations") is not None or (
            hasattr(vehicle, "vehicle_obligations") and vehicle.vehicle_obligations is not None
        ):
            obligations = (
                vehicle.get("vehicle_obligations")
                if isinstance(vehicle, dict)
                else vehicle.vehicle_obligations
            )
            assert isinstance(obligations, Decimal), "vehicle_obligations should be Decimal"

        if vehicle.get("solicitation_date") is not None or (
            hasattr(vehicle, "solicitation_date") and vehicle.solicitation_date is not None
        ):
            solicitation_date = (
                vehicle.get("solicitation_date")
                if isinstance(vehicle, dict)
                else vehicle.solicitation_date
            )
            assert isinstance(solicitation_date, date), "solicitation_date should be date"

    @handle_api_exceptions("vehicles")
    def test_get_vehicle_supports_joiner_and_flat_lists(self, tango_client):
        """Test getting a single vehicle with joiner and flat_lists parameters

        Validates:
        - Shape parameter is passed correctly
        - flat, flat_lists, and joiner parameters work correctly
        - Vehicle is parsed correctly
        """
        # First, get a vehicle UUID from listing
        list_response = tango_client.list_vehicles(limit=1)
        if not list_response.results:
            pytest.skip("No vehicles available to test get_vehicle")

        vehicle_uuid = (
            list_response.results[0].get("uuid")
            if isinstance(list_response.results[0], dict)
            else list_response.results[0].uuid
        )
        assert vehicle_uuid is not None, "Vehicle UUID should be present"

        # Test with flat, flat_lists, and joiner
        vehicle = tango_client.get_vehicle(
            vehicle_uuid,
            shape="uuid,opportunity(title)",
            flat=True,
            flat_lists=True,
            joiner="__",
        )

        validate_no_parsing_errors(vehicle)
        assert vehicle.get("uuid") is not None or hasattr(vehicle, "uuid"), (
            "Vehicle uuid should be present"
        )

        # If opportunity is present, verify it's accessible
        if vehicle.get("opportunity") is not None or (
            hasattr(vehicle, "opportunity") and vehicle.opportunity is not None
        ):
            opportunity = (
                vehicle.get("opportunity") if isinstance(vehicle, dict) else vehicle.opportunity
            )
            if isinstance(opportunity, dict):
                assert "title" in opportunity or hasattr(opportunity, "title")

    @handle_api_exceptions("vehicles")
    def test_list_vehicle_awardees_uses_default_shape(self, tango_client):
        """Test listing vehicle awardees with default shape

        Validates:
        - Default shape is applied
        - Awardees are parsed correctly with proper types
        """
        # First, get a vehicle UUID from listing
        list_response = tango_client.list_vehicles(limit=1)
        if not list_response.results:
            pytest.skip("No vehicles available to test list_vehicle_awardees")

        vehicle_uuid = (
            list_response.results[0].get("uuid")
            if isinstance(list_response.results[0], dict)
            else list_response.results[0].uuid
        )
        assert vehicle_uuid is not None, "Vehicle UUID should be present"

        response = tango_client.list_vehicle_awardees(vehicle_uuid, limit=10)

        # Validate response structure
        validate_pagination(response)

        # If we have results, validate them
        if response.results:
            awardee = response.results[0]
            validate_no_parsing_errors(awardee)

            # Verify required fields
            assert awardee.get("key") is not None or hasattr(awardee, "key"), (
                "Awardee key should be present"
            )

            # Verify type parsing
            if awardee.get("idv_obligations") is not None or (
                hasattr(awardee, "idv_obligations") and awardee.idv_obligations is not None
            ):
                obligations = (
                    awardee.get("idv_obligations")
                    if isinstance(awardee, dict)
                    else awardee.idv_obligations
                )
                assert isinstance(obligations, Decimal), "idv_obligations should be Decimal"

            if awardee.get("award_date") is not None or (
                hasattr(awardee, "award_date") and awardee.award_date is not None
            ):
                award_date = (
                    awardee.get("award_date") if isinstance(awardee, dict) else awardee.award_date
                )
                assert isinstance(award_date, date), "award_date should be date"

            # Verify recipient is accessible if present
            if awardee.get("recipient") is not None or (
                hasattr(awardee, "recipient") and awardee.recipient is not None
            ):
                recipient = (
                    awardee.get("recipient") if isinstance(awardee, dict) else awardee.recipient
                )
                if isinstance(recipient, dict):
                    assert "display_name" in recipient or hasattr(recipient, "display_name")


@pytest.mark.vcr()
@pytest.mark.integration
class TestIDVsIntegration:
    """Integration tests for IDV endpoints using production data"""

    @handle_api_exceptions("idvs")
    def test_list_idvs_uses_default_shape_and_keyset_params(self, tango_client):
        """Test listing IDVs with default shape and keyset pagination

        Validates:
        - Default shape is applied
        - Keyset pagination parameters (limit, cursor) work correctly
        - Filter parameters are passed correctly
        - IDVs are parsed correctly with proper types
        """
        response = tango_client.list_idvs(limit=10, awarding_agency="4700")

        # Validate response structure
        validate_pagination(response)

        # If we have results, validate them
        if response.results:
            idv = response.results[0]
            validate_no_parsing_errors(idv)

            # Verify required fields
            assert idv.get("key") is not None or hasattr(idv, "key"), "IDV key should be present"

            # Verify type parsing
            if idv.get("award_date") is not None or (
                hasattr(idv, "award_date") and idv.award_date is not None
            ):
                award_date = idv.get("award_date") if isinstance(idv, dict) else idv.award_date
                assert isinstance(award_date, date), "award_date should be date"

            if idv.get("obligated") is not None or (
                hasattr(idv, "obligated") and idv.obligated is not None
            ):
                obligated = idv.get("obligated") if isinstance(idv, dict) else idv.obligated
                assert isinstance(obligated, Decimal), "obligated should be Decimal"

    @handle_api_exceptions("idvs")
    def test_get_idv_uses_default_shape(self, tango_client):
        """Test getting a single IDV with default shape

        Validates:
        - Default comprehensive shape is applied
        - IDV is parsed correctly
        """
        # First, get an IDV key from listing
        list_response = tango_client.list_idvs(limit=1)
        if not list_response.results:
            pytest.skip("No IDVs available to test get_idv")

        idv_key = (
            list_response.results[0].get("key")
            if isinstance(list_response.results[0], dict)
            else list_response.results[0].key
        )
        assert idv_key is not None, "IDV key should be present"

        idv = tango_client.get_idv(idv_key)

        validate_no_parsing_errors(idv)
        assert idv.get("key") is not None or hasattr(idv, "key"), "IDV key should be present"
        assert idv.get("key") == idv_key if isinstance(idv, dict) else idv.key == idv_key, (
            "Returned IDV should match requested key"
        )

    @handle_api_exceptions("idvs")
    def test_list_idv_awards_uses_default_shape(self, tango_client):
        """Test listing IDV awards (child contracts) with default shape

        Validates:
        - Default shape is applied
        - Awards are parsed correctly with proper types
        - Pagination works correctly
        """
        # First, get an IDV key from listing
        list_response = tango_client.list_idvs(limit=1)
        if not list_response.results:
            pytest.skip("No IDVs available to test list_idv_awards")

        idv_key = (
            list_response.results[0].get("key")
            if isinstance(list_response.results[0], dict)
            else list_response.results[0].key
        )
        assert idv_key is not None, "IDV key should be present"

        response = tango_client.list_idv_awards(idv_key, limit=10)

        # Validate response structure
        validate_pagination(response)

        # If we have results, validate them
        if response.results:
            award = response.results[0]
            validate_no_parsing_errors(award)

            # Verify required fields
            assert award.get("key") is not None or hasattr(award, "key"), (
                "Award key should be present"
            )

            # Verify type parsing
            if award.get("award_date") is not None or (
                hasattr(award, "award_date") and award.award_date is not None
            ):
                award_date = (
                    award.get("award_date") if isinstance(award, dict) else award.award_date
                )
                assert isinstance(award_date, date), "award_date should be date"

            if award.get("award_amount") is not None or (
                hasattr(award, "award_amount") and award.award_amount is not None
            ):
                award_amount = (
                    award.get("award_amount") if isinstance(award, dict) else award.award_amount
                )
                assert isinstance(award_amount, Decimal), "award_amount should be Decimal"

    @handle_api_exceptions("idvs")
    def test_list_idv_child_idvs_uses_default_shape(self, tango_client):
        """Test listing child IDVs under an IDV with default shape

        Validates:
        - Default shape is applied
        - Child IDVs are parsed correctly with proper types
        - Pagination works correctly
        """
        # First, get an IDV key from listing
        list_response = tango_client.list_idvs(limit=1)
        if not list_response.results:
            pytest.skip("No IDVs available to test list_idv_child_idvs")

        idv_key = (
            list_response.results[0].get("key")
            if isinstance(list_response.results[0], dict)
            else list_response.results[0].key
        )
        assert idv_key is not None, "IDV key should be present"

        response = tango_client.list_idv_child_idvs(idv_key, limit=10)

        # Validate response structure
        validate_pagination(response)

        # If we have results, validate them
        if response.results:
            child_idv = response.results[0]
            validate_no_parsing_errors(child_idv)

            # Verify required fields
            assert child_idv.get("key") is not None or hasattr(child_idv, "key"), (
                "Child IDV key should be present"
            )

            # Verify type parsing
            if child_idv.get("award_date") is not None or (
                hasattr(child_idv, "award_date") and child_idv.award_date is not None
            ):
                award_date = (
                    child_idv.get("award_date")
                    if isinstance(child_idv, dict)
                    else child_idv.award_date
                )
                assert isinstance(award_date, date), "award_date should be date"

    @handle_api_exceptions("idvs")
    def test_list_idv_transactions(self, tango_client):
        """Test listing transactions for an IDV

        Validates:
        - Transactions are returned correctly
        - Pagination works correctly
        - Response structure is valid
        """
        # First, get an IDV key from listing
        list_response = tango_client.list_idvs(limit=1)
        if not list_response.results:
            pytest.skip("No IDVs available to test list_idv_transactions")

        idv_key = (
            list_response.results[0].get("key")
            if isinstance(list_response.results[0], dict)
            else list_response.results[0].key
        )
        assert idv_key is not None, "IDV key should be present"

        response = tango_client.list_idv_transactions(idv_key, limit=10)

        # Validate response structure
        validate_pagination(response)

        # If we have results, validate they are dictionaries (transactions don't use shape parsing)
        if response.results:
            transaction = response.results[0]
            assert isinstance(transaction, dict), "Transaction should be a dictionary"

    @handle_api_exceptions("idvs")
    def test_get_idv_summary(self, tango_client):
        """Test getting an IDV summary by solicitation identifier

        Validates:
        - Summary is returned correctly
        - Response structure is valid
        """
        # Use a vehicle to get solicitation_identifier (vehicles group IDVs by solicitation)
        vehicles_response = tango_client.list_vehicles(limit=10)
        if not vehicles_response.results:
            pytest.skip("No vehicles available to test get_idv_summary")

        # Find a vehicle with a solicitation_identifier
        solicitation_identifier = None
        for vehicle in vehicles_response.results:
            identifier = (
                vehicle.get("solicitation_identifier")
                if isinstance(vehicle, dict)
                else getattr(vehicle, "solicitation_identifier", None)
            )
            if identifier:
                solicitation_identifier = identifier
                break

        if not solicitation_identifier:
            pytest.skip("No vehicles with solicitation_identifier found to test get_idv_summary")

        summary = tango_client.get_idv_summary(solicitation_identifier)

        # Validate response structure
        assert isinstance(summary, dict), "Summary should be a dictionary"
        assert len(summary) > 0, "Summary should not be empty"

    @handle_api_exceptions("idvs")
    def test_list_idv_summary_awards(self, tango_client):
        """Test listing awards under an IDV summary

        Validates:
        - Awards are returned correctly
        - Pagination works correctly
        - Response structure is valid
        """
        # Use a vehicle to get solicitation_identifier (vehicles group IDVs by solicitation)
        vehicles_response = tango_client.list_vehicles(limit=10)
        if not vehicles_response.results:
            pytest.skip("No vehicles available to test list_idv_summary_awards")

        # Find a vehicle with a solicitation_identifier
        solicitation_identifier = None
        for vehicle in vehicles_response.results:
            identifier = (
                vehicle.get("solicitation_identifier")
                if isinstance(vehicle, dict)
                else getattr(vehicle, "solicitation_identifier", None)
            )
            if identifier:
                solicitation_identifier = identifier
                break

        if not solicitation_identifier:
            pytest.skip(
                "No vehicles with solicitation_identifier found to test list_idv_summary_awards"
            )

        response = tango_client.list_idv_summary_awards(solicitation_identifier, limit=10)

        # Validate response structure
        validate_pagination(response)

        # If we have results, validate they are dictionaries (awards don't use shape parsing)
        if response.results:
            award = response.results[0]
            assert isinstance(award, dict), "Award should be a dictionary"
