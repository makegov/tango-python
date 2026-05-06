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

import warnings
from datetime import date
from decimal import Decimal

import pytest

from tests.integration.conftest import handle_api_exceptions
from tests.integration.validation import validate_no_parsing_errors, validate_pagination


def _field(obj, name):
    """Read a field by name from a dict-or-attr-style shaped instance."""
    if isinstance(obj, dict):
        return obj.get(name)
    return getattr(obj, name, None)


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

        # Post-cutover (May 2026) lakehouse fields. All optional — only verify type when present.
        is_synth = _field(vehicle, "is_synthetic_solicitation")
        if is_synth is not None:
            assert isinstance(is_synth, bool), "is_synthetic_solicitation should be bool"

        idv_count = _field(vehicle, "idv_count")
        if idv_count is not None:
            assert isinstance(idv_count, int), "idv_count should be int"

        total_obligated = _field(vehicle, "total_obligated")
        if total_obligated is not None:
            assert isinstance(total_obligated, Decimal), "total_obligated should be Decimal"

        latest_award_date = _field(vehicle, "latest_award_date")
        if latest_award_date is not None:
            assert isinstance(latest_award_date, date), "latest_award_date should be date"

        organization = _field(vehicle, "organization")
        if organization is not None:
            assert isinstance(organization, dict), "organization should be a dict"
            allowed = {
                "organization_id",
                "office_code",
                "office_name",
                "agency_code",
                "agency_name",
                "department_code",
                "department_name",
            }
            assert set(organization).issubset(allowed), (
                f"organization keys outside allowed set: {set(organization) - allowed}"
            )

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

        # Test with flat, flat_lists, and joiner. Uses the post-cutover `organization`
        # leaf field (the prior `opportunity(...)` expansion is now deprecated).
        vehicle = tango_client.get_vehicle(
            vehicle_uuid,
            shape="uuid,organization",
            flat=True,
            flat_lists=True,
            joiner="__",
        )

        validate_no_parsing_errors(vehicle)
        assert vehicle.get("uuid") is not None or hasattr(vehicle, "uuid"), (
            "Vehicle uuid should be present"
        )

        # When flattened with joiner="__", organization fields surface as
        # `organization__office_code` / `organization__office_name`. Assert no
        # dotted keys leaked through (organization may be null on this UUID, in
        # which case flattening produces no organization-prefixed keys at all).
        keys = list(vehicle) if isinstance(vehicle, dict) else []
        org_keys = [k for k in keys if k.startswith("organization")]
        assert all("." not in k for k in org_keys), (
            f"flattened keys should use joiner='__', not '.': {org_keys}"
        )

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

    @handle_api_exceptions("vehicles")
    def test_list_vehicles_with_ordering(self, tango_client):
        """`ordering=-vehicle_obligations` returns vehicles sorted descending."""
        response = tango_client.list_vehicles(
            limit=10,
            ordering="-vehicle_obligations",
            shape="uuid,vehicle_obligations",
        )
        validate_pagination(response)

        obligations = [
            v for v in (_field(r, "vehicle_obligations") for r in response.results) if v is not None
        ]
        if len(obligations) >= 2:
            assert obligations == sorted(obligations, reverse=True), (
                f"Expected descending sort by vehicle_obligations, got {obligations}"
            )

    @handle_api_exceptions("vehicles")
    def test_get_vehicle_with_metrics_expansion(self, tango_client):
        """`metrics(*)` expansion returns the 12 lakehouse metric fields with correct types."""
        list_response = tango_client.list_vehicles(limit=1)
        if not list_response.results:
            pytest.skip("No vehicles available to test metrics expansion")
        vehicle_uuid = _field(list_response.results[0], "uuid")
        assert vehicle_uuid, "Vehicle UUID should be present"

        vehicle = tango_client.get_vehicle(vehicle_uuid, shape="uuid,metrics(*)")
        validate_no_parsing_errors(vehicle)

        metrics = _field(vehicle, "metrics")
        if metrics is None:
            pytest.skip("Vehicle has no metrics row yet (lakehouse sync may be pending)")

        assert isinstance(metrics, dict), "metrics expansion should be a dict"
        # Float-typed metrics
        for fname in (
            "avg_offers_received",
            "award_concentration_hhi",
            "order_concentration_hhi",
            "competed_rate",
            "avg_order_value",
            "max_order_value",
            "top_recipient_share",
            "recent_obligations_24mo",
            "obligation_to_ceiling_ratio",
        ):
            value = metrics.get(fname)
            if value is not None:
                assert isinstance(value, float), f"{fname} should be float"
        # Int-typed metrics
        for fname in ("using_agency_count", "recent_orders_24mo", "days_since_last_order"):
            value = metrics.get(fname)
            if value is not None:
                assert isinstance(value, int), f"{fname} should be int"

    @handle_api_exceptions("vehicles")
    def test_list_vehicle_orders_uses_default_shape(self, tango_client):
        """`/api/vehicles/{uuid}/orders/` returns task orders with the default shape applied."""
        list_response = tango_client.list_vehicles(limit=1)
        if not list_response.results:
            pytest.skip("No vehicles available to test list_vehicle_orders")
        vehicle_uuid = _field(list_response.results[0], "uuid")
        assert vehicle_uuid, "Vehicle UUID should be present"

        response = tango_client.list_vehicle_orders(vehicle_uuid, limit=10)
        validate_pagination(response)

        if response.results:
            order = response.results[0]
            validate_no_parsing_errors(order)
            assert _field(order, "key") is not None, "Order key should be present"

            award_date = _field(order, "award_date")
            if award_date is not None:
                assert isinstance(award_date, date), "award_date should be date"

            obligated = _field(order, "obligated")
            if obligated is not None:
                assert isinstance(obligated, Decimal), "obligated should be Decimal"

    def test_deprecated_shape_field_warns(self, tango_client):
        """Explicitly requesting a deprecated shape field emits a DeprecationWarning."""
        # Pure unit-style assertion on the helper — no HTTP call needed, so no
        # cassette / @vcr / @handle_api_exceptions decoration. Cheap to run.
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            tango_client._warn_deprecated_vehicle_shape(
                "uuid,solicitation_identifier,agency_details(*)"
            )
        deprecations = [w for w in caught if issubclass(w.category, DeprecationWarning)]
        assert deprecations, "Expected a DeprecationWarning for `agency_details`"
        message = str(deprecations[0].message)
        assert "agency_details" in message

        # Sanity check: the default shape (no deprecated tokens) does NOT warn.
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            tango_client._warn_deprecated_vehicle_shape("uuid,solicitation_identifier,metrics(*)")
        assert not [w for w in caught if issubclass(w.category, DeprecationWarning)], (
            "Non-deprecated shape should not emit DeprecationWarning"
        )


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
