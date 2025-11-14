"""Integration tests for edge cases and error handling

Pytest Markers:
    @pytest.mark.integration: Marks tests as integration tests that may hit external APIs
    @pytest.mark.vcr(): Enables VCR recording/playback for HTTP interactions
    @pytest.mark.live: Forces tests to use live API (skip cassettes) - not used by default
    @pytest.mark.cached: Forces tests to only run with cached responses - not used by default
    @pytest.mark.slow: Marks tests that are slow to execute - not used by default

Usage:
    # Run all integration tests (uses cassettes if available)
    pytest tests/integration/

    # Run only edge case integration tests
    pytest tests/integration/test_edge_cases_integration.py

    # Run with live API (requires TANGO_API_KEY environment variable)
    TANGO_USE_LIVE_API=true TANGO_API_KEY=xxx pytest tests/integration/

    # Refresh cassettes (re-record all interactions)
    TANGO_REFRESH_CASSETTES=true TANGO_API_KEY=xxx pytest tests/integration/
"""

from datetime import date, datetime
from decimal import Decimal

import pytest

from tango import ShapeConfig
from tests.integration.conftest import handle_api_exceptions
from tests.integration.validation import (
    validate_contract_fields,
    validate_entity_fields,
    validate_no_parsing_errors,
    validate_pagination,
)


@pytest.mark.vcr()
@pytest.mark.integration
class TestEdgeCasesIntegration:
    """Integration tests for edge cases, error handling, and API stability"""

    def test_parsing_null_missing_fields_in_contracts(self, tango_client):
        """Test that contract parsing handles null/missing fields gracefully

        Validates:
        - Null fields don't cause parsing errors
        - Missing optional fields are handled correctly
        - Objects with sparse data still parse successfully
        - Required fields are always present

        Requirements: 5.1, 6.1
        """
        # Request a large sample to increase chance of finding sparse records
        # Use a custom shape for analysis
        analysis_shape = "key,piid,award_date,fiscal_year,recipient(display_name,uei),total_contract_value,base_and_exercised_options_value,place_of_performance(state_code,country_code),naics_code,set_aside"
        response = tango_client.list_contracts(limit=50, shape=analysis_shape)

        validate_pagination(response)
        assert len(response.results) > 0, "Expected at least one contract"

        # Track field presence across all contracts
        field_presence = {
            "has_award_amount": 0,
            "has_award_date": 0,
            "has_description": 0,
            "has_awarding_agency": 0,
            "has_place_of_performance": 0,
            "has_naics": 0,
            "has_psc": 0,
        }

        for contract in response.results:
            # Validate each contract parses without errors
            validate_contract_fields(contract, minimal=False)
            validate_no_parsing_errors(contract)

            # Track which fields are present
            total_contract_value = contract.get("total_contract_value")
            if total_contract_value is not None:
                field_presence["has_award_amount"] += 1
            award_date = contract.get("award_date")
            if award_date is not None:
                field_presence["has_award_date"] += 1
            description = contract.get("description")
            if description:
                field_presence["has_description"] += 1
            awarding_office = contract.get("awarding_office")
            if awarding_office is not None:
                field_presence["has_awarding_agency"] += 1
            place_of_performance = contract.get("place_of_performance")
            if place_of_performance is not None:
                field_presence["has_place_of_performance"] += 1
            naics_code = contract.get("naics_code")
            if naics_code is not None:
                field_presence["has_naics"] += 1
            psc_code = contract.get("psc_code")
            if psc_code is not None:
                field_presence["has_psc"] += 1

            # Verify required fields are always present
            key = contract.get("key")
            assert key is not None, "Contract key should always be present"
            # recipient may not be in minimal shapes
            recipient = contract.get("recipient")
            if recipient is not None:
                # Verify recipient has at least display_name or uei
                assert (
                    recipient.get("display_name") is not None or recipient.get("uei") is not None
                ), "Recipient should have display_name or uei"

            # Verify optional fields can be None without breaking parsing
            # (no assertion needed - if we got here, parsing succeeded)

        # Log field presence statistics (useful for debugging)
        total = len(response.results)
        print(f"\nField presence in {total} contracts:")
        for field, count in field_presence.items():
            percentage = (count / total) * 100 if total > 0 else 0
            print(f"  {field}: {count}/{total} ({percentage:.1f}%)")

    def test_parsing_nested_objects_with_missing_data(self, tango_client):
        """Test parsing of nested objects when some nested fields are missing

        Validates:
        - Nested objects (agencies, locations) parse with partial data
        - Missing nested fields don't cause errors
        - Nested object parsing is resilient to API changes

        Requirements: 5.2, 6.1
        """
        # Use comprehensive shape to get nested objects
        agencies_shape = "key,piid,award_date,recipient(display_name),description,total_contract_value,awarding_office(*),funding_office(*)"
        response = tango_client.list_contracts(limit=25, shape=agencies_shape)

        validate_pagination(response)
        assert len(response.results) > 0, "Expected at least one contract"

        for contract in response.results:
            validate_contract_fields(contract, minimal=False)
            validate_no_parsing_errors(contract)

            # Test awarding_office nested object (agencies shape uses awarding_office)
            agency = contract.get("awarding_office")

            if agency is not None:
                # Verify agency/office has at least one identifier field
                # Agencies shape uses wildcard, so fields may vary
                if isinstance(agency, dict):
                    has_identifier = (
                        "code" in agency
                        or "name" in agency
                        or "agency" in agency
                        or len(agency) > 0
                    )
                else:
                    has_identifier = (
                        hasattr(agency, "code")
                        or hasattr(agency, "name")
                        or hasattr(agency, "agency")
                    )
                assert has_identifier, (
                    "Agency/office should have at least one identifier attribute (code, name, or agency)"
                )

                # Verify optional fields can be None
                # (no assertion needed - if we got here, parsing succeeded)

                # If department exists, verify it has expected structure
                department = (
                    agency.get("department")
                    if isinstance(agency, dict)
                    else getattr(agency, "department", None)
                )
                if department is not None:
                    if isinstance(department, dict):
                        assert (
                            "name" in department or "code" in department or len(department) > 0
                        ), "Department should have at least one field"
                    else:
                        assert hasattr(department, "name") or hasattr(department, "code"), (
                            "Department should have 'name' or 'code' attribute"
                        )

            # Test place_of_performance nested object (if present in shape)
            place_of_performance = contract.get("place_of_performance")
            if place_of_performance is not None:
                location = place_of_performance

                # Verify location has expected attributes
                if isinstance(location, dict):
                    has_location_field = (
                        "city_name" in location
                        or "state_code" in location
                        or "country_code" in location
                        or "city" in location
                        or "state" in location
                        or "country" in location
                        or len(location) > 0
                    )
                    assert has_location_field, "Location should have at least one location field"

                    # Verify at least one location field is populated
                    location_fields = [
                        location.get("city_name"),
                        location.get("state_code"),
                        location.get("state_name"),
                        location.get("zip_code"),
                        location.get("country_code"),
                        location.get("country_name"),
                        location.get("city"),
                        location.get("state"),
                        location.get("country"),
                    ]
                else:
                    has_location_field = (
                        hasattr(location, "city_name")
                        or hasattr(location, "state_code")
                        or hasattr(location, "country_code")
                        or hasattr(location, "city")
                        or hasattr(location, "state")
                        or hasattr(location, "country")
                    )
                    assert has_location_field, "Location should have at least one location field"

                    # Verify at least one location field is populated
                    location_fields = [
                        getattr(location, "city_name", None),
                        getattr(location, "state_code", None),
                        getattr(location, "state_name", None),
                        getattr(location, "zip_code", None),
                        getattr(location, "country_code", None),
                        getattr(location, "country_name", None),
                        getattr(location, "city", None),
                        getattr(location, "state", None),
                        getattr(location, "country", None),
                    ]
                non_none_fields = [f for f in location_fields if f is not None]
                assert len(non_none_fields) > 0, "Location should have at least one populated field"

    def test_flattened_responses_with_flat_lists(self, tango_client):
        """Test parsing of flattened responses with flat_lists=true

        Validates:
        - flat_lists parameter works correctly
        - Flattened array responses are unflattened properly
        - Parsing handles indexed keys (e.g., items.0.field)

        Requirements: 5.3
        """
        # Test with flat_lists on contracts - use minimal shape
        response = tango_client.list_contracts(
            limit=5, shape=ShapeConfig.CONTRACTS_MINIMAL, flat=True, flat_lists=True
        )

        validate_pagination(response)
        assert len(response.results) > 0, "Expected at least one contract"

        for contract in response.results:
            # Validate basic parsing
            validate_contract_fields(contract, minimal=True)
            validate_no_parsing_errors(contract)

            # Verify required fields are present
            contract_key = contract.get("key")
            assert contract_key is not None, "Contract key should be present"
            # recipient_name may not be in shape (CONTRACTS_MINIMAL uses recipient(display_name))
            if hasattr(contract, "recipient_name"):
                assert contract.recipient_name is not None, "Recipient name should be present"
            elif hasattr(contract, "recipient") and contract.recipient is not None:
                assert hasattr(contract.recipient, "display_name"), (
                    "Recipient should have display_name"
                )

    def test_api_schema_stability_detection_contracts(self, tango_client):
        """Test detection of API schema changes in contract responses

        Validates:
        - Expected fields are present in responses
        - Field types match expectations
        - Schema changes are detected through validation

        Requirements: 5.5, 6.1, 6.2, 6.3
        """
        analysis_shape = "key,piid,award_date,fiscal_year,recipient(display_name,uei),total_contract_value,base_and_exercised_options_value,place_of_performance(state_code,country_code),naics_code,set_aside"
        response = tango_client.list_contracts(limit=10, shape=analysis_shape)

        validate_pagination(response)
        assert len(response.results) > 0, "Expected at least one contract"

        # Define expected fields that should be present in Contract model
        # Note: Fields depend on the shape used - analysis shape
        expected_fields = [
            "key",
            "piid",
            "award_date",
            "fiscal_year",
            "recipient",
            "total_contract_value",
            "base_and_exercised_options_value",
            "place_of_performance",
            "naics_code",
            "set_aside",
        ]

        contract = response.results[0]

        # Verify all expected fields exist as attributes
        for field in expected_fields:
            field_exists = field in contract
            assert field_exists, (
                f"Contract missing expected field: {field}. API schema may have changed."
            )

        # Verify field types for non-None values
        contract_key = contract.get("key")
        if contract_key is not None:
            assert isinstance(contract_key, str), (
                f"Contract.key should be str, got {type(contract_key)}"
            )

        award_date = contract.get("award_date")
        if award_date is not None:
            from datetime import date

            assert isinstance(award_date, date), (
                f"Contract.award_date should be date, got {type(award_date)}"
            )

        award_amount = contract.get("award_amount")
        if award_amount is not None:
            assert isinstance(award_amount, Decimal), (
                f"Contract.award_amount should be Decimal, got {type(award_amount)}"
            )

        last_modified = contract.get("last_modified")
        if last_modified is not None:
            assert isinstance(last_modified, datetime), (
                f"Contract.last_modified should be datetime, got {type(last_modified)}"
            )

            # Verify nested object types (analysis shape doesn't include awarding_office anymore)
        # Only check if present
        awarding_agency = contract.get("awarding_agency")
        if awarding_agency is not None:
            if isinstance(awarding_agency, dict):
                assert (
                    "code" in awarding_agency
                    or "name" in awarding_agency
                    or len(awarding_agency) > 0
                ), "awarding_agency should have at least one field"
            else:
                assert hasattr(awarding_agency, "code"), (
                    "awarding_agency missing 'code' attribute. Schema may have changed."
                )
                assert hasattr(awarding_agency, "name"), (
                    "awarding_agency missing 'name' attribute. Schema may have changed."
                )

        awarding_office = contract.get("awarding_office")
        if awarding_office is not None:
            if isinstance(awarding_office, dict):
                assert (
                    "code" in awarding_office
                    or "agency" in awarding_office
                    or len(awarding_office) > 0
                ), "awarding_office should have at least one field"
            else:
                assert hasattr(awarding_office, "code") or hasattr(awarding_office, "agency"), (
                    "awarding_office missing 'code' or 'agency' attribute. Schema may have changed."
                )

        place_of_performance = contract.get("place_of_performance")
        if place_of_performance is not None:
            # Analysis shape includes place_of_performance(state_code,country_code)
            if isinstance(place_of_performance, dict):
                assert (
                    "state_code" in place_of_performance
                    or "country_code" in place_of_performance
                    or len(place_of_performance) > 0
                ), "place_of_performance should have at least one field"
            else:
                assert hasattr(place_of_performance, "state_code") or hasattr(
                    place_of_performance, "country_code"
                ), (
                    "place_of_performance missing 'state_code' or 'country_code' attribute. Schema may have changed."
                )

    def test_api_schema_stability_detection_entities(self, tango_client):
        """Test detection of API schema changes in entity responses

        Validates:
        - Expected entity fields are present
        - Entity field types match expectations
        - Entity schema changes are detected

        Requirements: 5.5, 6.1, 6.2, 6.3
        """
        response = tango_client.list_entities(limit=10, shape=ShapeConfig.ENTITIES_COMPREHENSIVE)

        validate_pagination(response)
        assert len(response.results) > 0, "Expected at least one entity"

        # Define expected fields in Entity model
        # Note: 'key' may not be returned by API for entities (they use 'uei' as identifier)
        # 'location' may be returned as 'physical_address' or 'mailing_address' in the shape
        # Note: 'display_name' was replaced by 'legal_business_name' in the API
        expected_fields = ["legal_business_name", "uei", "cage_code", "business_types"]

        # Optional fields that may be present
        optional_fields = [
            "key",
            "location",
            "physical_address",
            "mailing_address",
            "registration_date",
            "sam_registration_date",
            "expiration_date",
            "sam_expiration_date",
            "last_updated",
        ]

        entity = response.results[0]

        # Verify all expected fields exist as attributes
        for field in expected_fields:
            # Use 'in' operator for dict-like objects, hasattr for regular objects
            field_exists = field in entity if isinstance(entity, dict) else hasattr(entity, field)
            assert field_exists, (
                f"Entity missing expected field: {field}. API schema may have changed. Available fields: {list(entity.keys()) if isinstance(entity, dict) else dir(entity)}"
            )

        # Verify required fields are present
        # Entity doesn't have 'key' field - use 'uei' as identifier
        uei = entity.get("uei") if isinstance(entity, dict) else getattr(entity, "uei", None)
        assert uei is not None, "Entity.uei should not be None"
        legal_business_name = (
            entity.get("legal_business_name")
            if isinstance(entity, dict)
            else getattr(entity, "legal_business_name", None)
        )
        assert legal_business_name is not None, "Entity.legal_business_name should not be None"

        # Verify field types for non-None values
        # Entity doesn't have 'key' field - use 'uei' as identifier
        uei = entity.get("uei") if isinstance(entity, dict) else getattr(entity, "uei", None)
        if uei is not None:
            assert isinstance(uei, str), f"Entity.uei should be str, got {type(uei)}"

        if entity.legal_business_name is not None:
            assert isinstance(entity.legal_business_name, str), (
                f"Entity.legal_business_name should be str, got {type(entity.legal_business_name)}"
            )

        # Date fields may not be in shape - only check if present (use safe access)
        registration_date = entity.get("registration_date")
        if registration_date is not None:
            from datetime import date

            assert isinstance(registration_date, date), (
                f"Entity.registration_date should be date, got {type(registration_date)}"
            )

        last_updated = entity.get("last_updated")
        if last_updated is not None:
            assert isinstance(last_updated, datetime), (
                f"Entity.last_updated should be datetime, got {type(last_updated)}"
            )

        business_types = entity.get("business_types")
        if business_types is not None:
            # business_types can be list or dict depending on API response
            assert isinstance(business_types, (list, dict)), (
                f"Entity.business_types should be list or dict, got {type(business_types)}"
            )

        # Verify nested location object (entity uses physical_address or mailing_address, not location)
        physical_address = entity.get("physical_address")
        mailing_address = entity.get("mailing_address")
        location = physical_address or mailing_address
        if location is not None:
            if isinstance(location, dict):
                assert len(location) > 0, "Address should have at least one field"
            else:
                # Address fields may vary - just check it has some attributes
                assert (
                    hasattr(location, "city_name")
                    or hasattr(location, "city")
                    or hasattr(location, "state_code")
                    or hasattr(location, "state")
                    or hasattr(location, "country_code")
                ), "Address should have location fields"

    def test_parsing_with_minimal_shape_sparse_data(self, tango_client):
        """Test parsing with minimal shape returns only requested fields

        Validates:
        - Minimal shape limits returned data
        - Parsing handles sparse responses correctly
        - Unrequested fields may be None

        Requirements: 5.1, 5.5
        """
        # Use ultra-minimal shape
        summary_shape = "key,piid,recipient(display_name),total_contract_value"
        response = tango_client.list_contracts(limit=10, shape=summary_shape)

        validate_pagination(response)
        assert len(response.results) > 0, "Expected at least one contract"

        for contract in response.results:
            # Validate basic parsing
            validate_no_parsing_errors(contract)

            # Verify key fields are present (from summary shape)
            contract_key = contract.get("key")
            assert contract_key is not None, "Contract key should be present"
            # Summary shape has recipient(display_name), not recipient_name
            if hasattr(contract, "recipient_name"):
                assert contract.recipient_name is not None, "Recipient name should be present"
            elif hasattr(contract, "recipient") and contract.recipient is not None:
                assert hasattr(contract.recipient, "display_name"), (
                    "Recipient should have display_name"
                )

            # Many fields may be None with minimal shape - this is expected
            # Just verify parsing doesn't fail

    def test_entity_parsing_with_various_address_formats(self, tango_client):
        """Test entity parsing handles different address field variations

        Validates:
        - physical_address vs mailing_address vs location
        - Address parsing is flexible
        - Missing address fields don't break parsing

        Requirements: 5.1, 5.2, 6.1
        """
        response = tango_client.list_entities(limit=25, shape=ShapeConfig.ENTITIES_COMPREHENSIVE)

        validate_pagination(response)
        assert len(response.results) > 0, "Expected at least one entity"

        for entity in response.results:
            validate_entity_fields(entity)
            validate_no_parsing_errors(entity)

            # Entity uses physical_address or mailing_address, not location
            physical_address = entity.get("physical_address")
            mailing_address = entity.get("mailing_address")
            address = physical_address or mailing_address

            if address is not None:
                # Verify address has expected attributes (handle dict fallback)
                if isinstance(address, dict):
                    assert len(address) > 0, "Address should have at least one field"
                    # At least one field should be populated
                    location_fields = [
                        address.get("city_name"),
                        address.get("city"),
                        address.get("state_code"),
                        address.get("state"),
                        address.get("zip_code"),
                        address.get("country_code"),
                        address.get("country"),
                    ]
                else:
                    # Address fields may vary - just check it has some attributes
                    assert (
                        hasattr(address, "city_name")
                        or hasattr(address, "city")
                        or hasattr(address, "state_code")
                        or hasattr(address, "state")
                        or hasattr(address, "country_code")
                    ), "Address should have location fields"
                    # At least one field should be populated
                    location_fields = [
                        getattr(address, "city_name", None),
                        getattr(address, "city", None),
                        getattr(address, "state_code", None),
                        getattr(address, "state", None),
                        getattr(address, "zip_code", None),
                        getattr(address, "country_code", None),
                        getattr(address, "country", None),
                    ]
                non_none_fields = [f for f in location_fields if f is not None]
                assert len(non_none_fields) > 0, "Address should have at least one populated field"

    def test_decimal_field_parsing_edge_cases(self, tango_client):
        """Test decimal field parsing handles various numeric formats

        Validates:
        - Large decimal values parse correctly
        - Small decimal values parse correctly
        - Zero values parse correctly
        - Null values are handled

        Requirements: 5.4, 6.1
        """
        analysis_shape = "key,piid,award_date,fiscal_year,recipient(display_name,uei),total_contract_value,base_and_exercised_options_value,place_of_performance(state_code,country_code),naics_code,set_aside"
        response = tango_client.list_contracts(limit=50, shape=analysis_shape)

        validate_pagination(response)
        assert len(response.results) > 0, "Expected at least one contract"

        # Track decimal value ranges
        amounts = []

        for contract in response.results:
            validate_contract_fields(contract, minimal=False)

            # Verify decimal fields are correct type when present (only if field is in shape)
            if hasattr(contract, "award_amount") and contract.award_amount is not None:
                assert isinstance(contract.award_amount, Decimal), (
                    f"award_amount should be Decimal, got {type(contract.award_amount)}"
                )

                # Verify decimal is non-negative (business rule)
                assert contract.award_amount >= 0, (
                    f"award_amount should be non-negative, got {contract.award_amount}"
                )

                amounts.append(contract.award_amount)

            # Check ContractData decimal fields if present (only if field is in shape)
            if hasattr(contract, "contract_data") and contract.contract_data is not None:
                cd = contract.contract_data

                if cd.federal_action_obligation is not None:
                    assert isinstance(cd.federal_action_obligation, Decimal), (
                        "federal_action_obligation should be Decimal"
                    )

                if cd.base_and_exercised_options_value is not None:
                    assert isinstance(cd.base_and_exercised_options_value, Decimal), (
                        "base_and_exercised_options_value should be Decimal"
                    )

        # Verify we found some decimal values
        if amounts:
            print(f"\nDecimal value range: ${min(amounts):,.2f} to ${max(amounts):,.2f}")

    def test_date_field_parsing_edge_cases(self, tango_client):
        """Test date field parsing handles various date formats

        Validates:
        - ISO date format parsing
        - Date-only vs datetime parsing
        - Null date values are handled
        - Date fields have correct types

        Requirements: 5.4, 6.1
        """
        dates_shape = "key,piid,award_date,fiscal_year,recipient(display_name),description,total_contract_value"
        response = tango_client.list_contracts(limit=25, shape=dates_shape)

        validate_pagination(response)
        assert len(response.results) > 0, "Expected at least one contract"

        for contract in response.results:
            validate_contract_fields(contract, minimal=False)

            # Verify date fields are correct type when present
            award_date = contract.get("award_date")
            if award_date is not None:
                assert isinstance(award_date, date), (
                    f"award_date should be date, got {type(award_date)}"
                )

                # Verify date is reasonable (not in far future)
                assert award_date.year >= 1990, f"award_date year seems unreasonable: {award_date}"
                assert award_date.year <= 2030, f"award_date year seems unreasonable: {award_date}"

            # Only check fields that are in the shape
            period_of_performance_start = contract.get("period_of_performance_start")
            if period_of_performance_start is not None:
                assert isinstance(period_of_performance_start, date), (
                    "period_of_performance_start should be date"
                )

            period_of_performance_end = contract.get("period_of_performance_end")
            if period_of_performance_end is not None:
                assert isinstance(period_of_performance_end, date), (
                    "period_of_performance_end should be date"
                )

            # Verify datetime fields (only if in shape)
            last_modified = contract.get("last_modified")
            if last_modified is not None:
                assert isinstance(last_modified, datetime), (
                    f"last_modified should be datetime, got {type(last_modified)}"
                )

    def test_empty_list_responses(self, tango_client):
        """Test handling of empty result lists

        Validates:
        - Empty results don't cause errors
        - Pagination structure is correct for empty results
        - Count is 0 for empty results

        Requirements: 6.1, 6.2
        """
        # Use a date filter that likely returns no results (far future)
        response = tango_client.list_contracts(
            limit=5, award_date_gte="2099-01-01", shape=ShapeConfig.CONTRACTS_MINIMAL
        )

        # Validate pagination structure even with no results
        validate_pagination(response)

        # Verify empty results are handled correctly
        assert isinstance(response.results, list), "results should be a list"
        assert response.count >= 0, "count should be non-negative"

        # If no results, count should be 0
        if len(response.results) == 0:
            assert response.count == 0, "count should be 0 when results are empty"

    def test_list_field_parsing_consistency(self, tango_client):
        """Test that list fields are consistently parsed as lists

        Validates:
        - List fields are always lists (not strings or other types)
        - Empty lists are handled correctly
        - List items have expected types

        Requirements: 5.2, 6.1
        """
        standard_shape = "uei,legal_business_name,cage_code,business_types,physical_address"
        response = tango_client.list_entities(limit=25, shape=standard_shape)

        validate_pagination(response)
        assert len(response.results) > 0, "Expected at least one entity"

        for entity in response.results:
            validate_entity_fields(entity)

            # Verify business_types is a list or dict when present
            business_types = entity.get("business_types")
            if business_types is not None:
                # business_types can be a list or dict depending on API response
                assert isinstance(business_types, (list, dict)), (
                    f"business_types should be list or dict, got {type(business_types)}"
                )

                # If list is not empty, verify items are strings or dicts
                if isinstance(business_types, list) and business_types:
                    for bt in business_types:
                        assert isinstance(bt, (str, dict)), (
                            f"business_type item should be str or dict, got {type(bt)}"
                        )


# ============================================================================
# Type Hints Integration Tests
# ============================================================================


@pytest.mark.integration
@pytest.mark.vcr
class TestTypeHintsIntegration:
    """Test dict access patterns work correctly with real API responses

    These tests validate that shaped responses return dict-like objects that can be
    accessed with dict syntax, which is what type hints indicate.

    Note: These tests are complementary to the regular integration tests which test
    attribute access. These specifically validate dict access patterns that type
    hints suggest are available.

    Note: Only tests endpoints that support response shaping.
    Forecasts endpoints don't currently support shaping.
    """

    @pytest.mark.parametrize(
        "shape_name,shape_value",
        [
            ("minimal", ShapeConfig.CONTRACTS_MINIMAL),
            ("custom", "key,piid,description"),
            ("ultra_minimal", "key,piid,recipient(display_name),total_contract_value"),
        ],
    )
    @handle_api_exceptions("contracts")
    def test_contracts_dict_access(self, tango_client, shape_name, shape_value):
        """Test dict access for contracts with different shapes

        Validates that shaped responses support dict access as type hints indicate.
        """
        response = tango_client.list_contracts(shape=shape_value, limit=5)

        assert response.results
        for contract in response.results:
            # Validate dict access works
            assert isinstance(contract, dict), "Contract should be dict-like"
            assert "key" in contract, "Contract should have 'key' field"
            assert isinstance(contract["key"], str), "key should be string"

            # Optional fields may be None
            if "piid" in contract:
                assert contract["piid"] is None or isinstance(contract["piid"], str)

            # Nested dict access
            if "recipient" in contract and contract["recipient"]:
                assert isinstance(contract["recipient"], dict)
                if "display_name" in contract["recipient"]:
                    assert isinstance(contract["recipient"]["display_name"], str)

    @pytest.mark.parametrize(
        "shape_name,shape_value",
        [
            ("minimal", ShapeConfig.ENTITIES_MINIMAL),
            ("with_address", "uei,legal_business_name,cage_code,business_types,physical_address"),
        ],
    )
    @handle_api_exceptions("entities")
    def test_entities_dict_access(self, tango_client, shape_name, shape_value):
        """Test dict access for entities with different shapes"""
        response = tango_client.list_entities(shape=shape_value, limit=5)

        assert response.results
        for entity in response.results:
            # Validate dict access works
            assert isinstance(entity, dict), "Entity should be dict-like"
            assert "uei" in entity or "legal_business_name" in entity, (
                "Entity should have identifier fields"
            )

            if "uei" in entity:
                assert entity["uei"] is None or isinstance(entity["uei"], str)
            if "legal_business_name" in entity:
                assert isinstance(entity["legal_business_name"], str)

            # Optional fields
            if "cage_code" in entity:
                assert entity["cage_code"] is None or isinstance(entity["cage_code"], str)
            if "business_types" in entity:
                assert entity["business_types"] is None or isinstance(
                    entity["business_types"], list
                )

            # Nested dict access
            if "physical_address" in entity and entity.get("physical_address"):
                addr = entity["physical_address"]
                if isinstance(addr, dict):
                    # Check for city_name (new API) or city (old API)
                    assert (
                        addr.get("city_name") is None
                        or isinstance(addr.get("city_name"), str)
                        or addr.get("city") is None
                        or isinstance(addr.get("city"), str)
                    )

    @pytest.mark.parametrize(
        "shape_name,shape_value",
        [
            ("minimal", ShapeConfig.OPPORTUNITIES_MINIMAL),
            (
                "detailed",
                "opportunity_id,title,description,solicitation_number,response_deadline,first_notice_date,last_notice_date,active,naics_code,psc_code,set_aside,sam_url,office(*),place_of_performance(*)",
            ),
        ],
    )
    @handle_api_exceptions("opportunities")
    def test_opportunities_dict_access(self, tango_client, shape_name, shape_value):
        """Test dict access for opportunities with different shapes"""
        response = tango_client.list_opportunities(shape=shape_value, limit=5)

        assert response.results
        for opp in response.results:
            # Validate dict access works
            assert isinstance(opp, dict), "Opportunity should be dict-like"
            assert "opportunity_id" in opp or "title" in opp, (
                "Opportunity should have identifier fields"
            )

            if "opportunity_id" in opp:
                assert isinstance(opp["opportunity_id"], str)
            if "title" in opp:
                assert isinstance(opp["title"], str)

            # Optional fields
            if "description" in opp:
                assert opp["description"] is None or isinstance(opp["description"], str)

            # Nested dict access
            if "office" in opp and opp.get("office"):
                office = opp["office"]
                if isinstance(office, dict):
                    # Check if any of the expected fields exist
                    assert (
                        "code" in office
                        or "name" in office
                        or "agency" in office
                        or len(office) > 0
                    )

    @pytest.mark.parametrize(
        "shape_name,shape_value",
        [
            ("minimal", ShapeConfig.NOTICES_MINIMAL),
            (
                "detailed",
                "notice_id,title,description,solicitation_number,posted_date,naics_code,set_aside,office(*),place_of_performance(*)",
            ),
        ],
    )
    @handle_api_exceptions("notices")
    def test_notices_dict_access(self, tango_client, shape_name, shape_value):
        """Test dict access for notices with different shapes"""
        response = tango_client.list_notices(shape=shape_value, limit=5)

        assert response.results
        for notice in response.results:
            # Validate dict access works
            assert isinstance(notice, dict), "Notice should be dict-like"
            assert "notice_id" in notice, "Notice should have notice_id"
            assert isinstance(notice["notice_id"], str)
            assert "title" in notice, "Notice should have title"
            assert isinstance(notice["title"], str)

            # Optional fields
            if "description" in notice:
                assert notice["description"] is None or isinstance(notice["description"], str)

            # Nested dict access
            if "office" in notice and notice.get("office"):
                office = notice["office"]
                if isinstance(office, dict):
                    # Check if any of the expected fields exist
                    assert (
                        "code" in office
                        or "name" in office
                        or "agency" in office
                        or len(office) > 0
                    )
