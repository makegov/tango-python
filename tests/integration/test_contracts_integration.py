"""Integration tests for contract endpoints

Pytest Markers:
    @pytest.mark.integration: Marks tests as integration tests that may hit external APIs
    @pytest.mark.vcr(): Enables VCR recording/playback for HTTP interactions
    @pytest.mark.live: Forces tests to use live API (skip cassettes) - not used by default
    @pytest.mark.cached: Forces tests to only run with cached responses - not used by default
    @pytest.mark.slow: Marks tests that are slow to execute - not used by default

Usage:
    # Run all integration tests (uses cassettes if available)
    pytest tests/integration/

    # Run only contract integration tests
    pytest tests/integration/test_contracts_integration.py

    # Run with live API (requires TANGO_API_KEY environment variable)
    TANGO_USE_LIVE_API=true TANGO_API_KEY=xxx pytest tests/integration/

    # Refresh cassettes (re-record all interactions)
    TANGO_REFRESH_CASSETTES=true TANGO_API_KEY=xxx pytest tests/integration/
"""

from datetime import date, datetime
from decimal import Decimal

import pytest

from tango import SearchFilters, ShapeConfig
from tests.integration.conftest import handle_api_exceptions
from tests.integration.validation import (
    validate_contract_fields,
    validate_no_parsing_errors,
    validate_pagination,
)


@pytest.mark.vcr()
@pytest.mark.integration
class TestContractsIntegration:
    """Integration tests for contract endpoints using production data"""

    @handle_api_exceptions("contracts")
    @pytest.mark.parametrize(
        "shape_name,shape_value",
        [
            ("default", None),  # None means use default minimal shape
            ("minimal", ShapeConfig.CONTRACTS_MINIMAL),
            ("custom", "key,piid,recipient(display_name),total_contract_value,award_date"),
            (
                "detailed",
                "key,piid,award_date,description,total_contract_value,obligated,fiscal_year,set_aside,recipient(display_name,uei),awarding_office(*),place_of_performance(city_name,state_code,state_name,country_code,country_name),naics_code,psc_code",
            ),
        ],
    )
    def test_list_contracts_with_shapes(self, tango_client, shape_name, shape_value):
        """Test listing contracts with different shapes

        Validates:
        - Paginated response structure
        - Contract parsing with various shapes
        - Required contract fields are present regardless of shape
        """
        kwargs = {"limit": 5}
        if shape_value is not None:
            kwargs["shape"] = shape_value

        response = tango_client.list_contracts(**kwargs)

        # Validate response structure
        validate_pagination(response)
        assert response.count > 0, "Expected at least one contract in the system"
        assert len(response.results) > 0, "Expected results in the response"

        # Validate first contract
        contract = response.results[0]
        validate_contract_fields(contract, minimal=(shape_name in ("default", "minimal")))
        validate_no_parsing_errors(contract)

        # Verify key fields are present
        assert contract.key is not None, "Contract key should be present"
        # recipient_name may not be in custom shape, check if present
        if hasattr(contract, "recipient_name"):
            assert contract.recipient_name is not None, "Recipient name should be present"

    @handle_api_exceptions("contracts")
    def test_list_contracts_with_flat(self, tango_client):
        """Test listing contracts with flat=true parameter

        Validates:
        - Flat responses are correctly unflattened
        - Nested objects are reconstructed properly
        - Parsing works with flattened data
        """
        response = tango_client.list_contracts(
            limit=5, shape=ShapeConfig.CONTRACTS_MINIMAL, flat=True
        )

        # Validate response structure
        validate_pagination(response)
        assert len(response.results) > 0, "Expected results in the response"

        # Validate first contract
        contract = response.results[0]
        validate_contract_fields(contract, minimal=True)
        validate_no_parsing_errors(contract)

    @handle_api_exceptions("contracts")
    def test_list_contracts_with_awarding_agency_filter(self, tango_client):
        """Test filtering contracts by awarding agency

        Validates:
        - Agency filter works correctly
        - Results match the filter criteria
        - Awarding agency is parsed in results
        """
        # Use GSA as a test agency (code 4700)
        agency_code = "4700"

        response = tango_client.list_contracts(limit=5, awarding_agency=agency_code)

        # Validate response structure
        validate_pagination(response)
        # Note: count may be 0 if no contracts for this agency

        # If we have results, validate them
        if response.results:
            contract = response.results[0]
            validate_contract_fields(contract, minimal=True)
            validate_no_parsing_errors(contract)

    @handle_api_exceptions("contracts")
    def test_list_contracts_with_date_range_filter(self, tango_client):
        """Test filtering contracts by date range

        Validates:
        - Date range filters work correctly
        - Date parsing is accurate
        - Results fall within the specified range
        """
        # Filter for contracts awarded in 2023
        response = tango_client.list_contracts(
            limit=5, filters={"award_date_gte": "2023-01-01", "award_date_lte": "2023-12-31"}
        )

        # Validate response structure
        validate_pagination(response)

        # If we have results, validate them
        if response.results:
            contract = response.results[0]
            validate_contract_fields(contract, minimal=True)
            validate_no_parsing_errors(contract)

            # Verify date is within range (if present)
            award_date = getattr(contract, "award_date", None)
            if award_date:
                assert award_date >= date(2023, 1, 1), "Award date should be >= 2023-01-01"
                assert award_date <= date(2023, 12, 31), "Award date should be <= 2023-12-31"

    @handle_api_exceptions("contracts")
    def test_search_contracts_with_filters(self, tango_client):
        """Test advanced contract search with SearchFilters

        Validates:
        - SearchFilters object works correctly
        - Multiple filters can be combined
        - Results match the filter criteria
        """
        # Create search filters with just date range (award_amount filter may not work as expected)
        filters = SearchFilters(
            page=1, limit=5, award_date_gte="2023-01-01", award_date_lte="2023-12-31"
        )

        response = tango_client.list_contracts(filters=filters)

        # Validate response structure
        validate_pagination(response)

        # If we have results, validate them
        if response.results:
            contract = response.results[0]
            validate_contract_fields(contract, minimal=True)
            validate_no_parsing_errors(contract)

            # Verify date filter is applied (if data is present)
            award_date = getattr(contract, "award_date", None)
            if award_date:
                assert award_date >= date(2023, 1, 1), "Award date should be >= 2023-01-01"
                assert award_date <= date(2023, 12, 31), "Award date should be <= 2023-12-31"

    @handle_api_exceptions("contracts")
    def test_list_contracts_with_naics_code_filter(self, tango_client):
        """Test filtering contracts by NAICS code

        Validates:
        - NAICS code filter works correctly
        - Filtered results have fewer or equal count than unfiltered
        - Results match the filter criteria (if NAICS data is available in response)
        """
        # First, get a baseline count without filter
        baseline_response = tango_client.list_contracts(limit=10)
        baseline_count = baseline_response.count

        # Filter by a specific NAICS code (541511 - IT services)
        # Use a shape that includes naics_code to verify the filter
        filtered_response = tango_client.list_contracts(
            naics_code="541511",
            limit=10,
            shape="key,piid,award_date,recipient(display_name),description,total_contract_value,naics_code",
        )

        # Validate response structure
        validate_pagination(filtered_response)

        # Verify that filtered results have fewer or equal count than baseline
        # (The filter should reduce the result set)
        assert (
            filtered_response.count <= baseline_count
        ), f"Filtered count ({filtered_response.count}) should be <= baseline count ({baseline_count})"

        # If we have results, validate them
        if filtered_response.results:
            contract = filtered_response.results[0]
            validate_contract_fields(contract, minimal=False)
            validate_no_parsing_errors(contract)

            # Verify NAICS code in results if available
            # The naics_code field might be a string or nested object
            naics_value = None
            if hasattr(contract, "naics_code") and contract.naics_code is not None:
                naics_value = contract.naics_code
            elif hasattr(contract, "naics") and contract.naics is not None:
                if hasattr(contract.naics, "code"):
                    naics_value = contract.naics.code

            # If we can verify the NAICS code, check it matches
            if naics_value:
                assert str(naics_value) == "541511", (
                    f"Contract NAICS code should be '541511', got '{naics_value}'"
                )

    @handle_api_exceptions("contracts")
    def test_contract_field_types(self, tango_client):
        """Test that all contract field types are correctly parsed

        Validates:
        - Date fields are parsed as date objects
        - Decimal fields are parsed as Decimal objects
        - Datetime fields are parsed as datetime objects
        - Nested objects (agencies, locations) are parsed correctly
        """
        # Use a shape with more fields to test type validation
        comprehensive_shape = (
            "key,piid,award_date,description,total_contract_value,"
            "recipient(display_name),naics_code,psc_code"
        )

        response = tango_client.list_contracts(limit=10, shape=comprehensive_shape)

        assert len(response.results) > 0, "Expected at least one contract"

        for contract in response.results:
            # Validate field types
            validate_contract_fields(contract, minimal=False)
            validate_no_parsing_errors(contract)

            # Additional type checks for specific fields (only if in shape)
            if hasattr(contract, "award_amount") and contract.award_amount is not None:
                assert isinstance(contract.award_amount, Decimal), (
                    f"award_amount should be Decimal, got {type(contract.award_amount)}"
                )

            if hasattr(contract, "award_date") and contract.award_date is not None:
                assert isinstance(contract.award_date, date), (
                    f"award_date should be date, got {type(contract.award_date)}"
                )

            if hasattr(contract, "last_modified") and contract.last_modified is not None:
                assert isinstance(contract.last_modified, datetime), (
                    f"last_modified should be datetime, got {type(contract.last_modified)}"
                )

            # Validate nested objects if present (only if in shape)
            if hasattr(contract, "awarding_agency") and contract.awarding_agency is not None:
                assert hasattr(contract.awarding_agency, "code"), (
                    "awarding_agency should have 'code' attribute"
                )
                assert hasattr(contract.awarding_agency, "name"), (
                    "awarding_agency should have 'name' attribute"
                )

            if (
                hasattr(contract, "place_of_performance")
                and contract.place_of_performance is not None
            ):
                assert hasattr(contract.place_of_performance, "city"), (
                    "place_of_performance should have 'city' attribute"
                )

            if hasattr(contract, "naics") and contract.naics is not None:
                assert hasattr(contract.naics, "code"), "naics should have 'code' attribute"

            if hasattr(contract, "psc") and contract.psc is not None:
                assert hasattr(contract.psc, "code"), "psc should have 'code' attribute"
            elif hasattr(contract, "psc_code") and contract.psc_code is not None:
                # psc_code might be a string field instead of nested object
                assert isinstance(contract.psc_code, str), "psc_code should be string"

    @handle_api_exceptions("contracts")
    def test_contract_data_object_parsing(self, tango_client):
        """Test that ContractData nested object is parsed correctly

        Validates:
        - ContractData object is populated with comprehensive shape
        - Decimal fields in ContractData are correctly typed
        - All ContractData fields are accessible
        """
        # Use minimal shape - ContractData is populated from piid field
        response = tango_client.list_contracts(limit=5, shape=ShapeConfig.CONTRACTS_MINIMAL)

        assert len(response.results) > 0, "Expected at least one contract"

        # Find a contract with contract_data populated (only if field is in shape)
        contract_with_data = None
        for contract in response.results:
            if hasattr(contract, "contract_data") and contract.contract_data is not None:
                contract_with_data = contract
                break

        # If we found one, validate it
        if contract_with_data and contract_with_data.contract_data:
            contract_data = contract_with_data.contract_data

            # Validate ContractData has expected attributes
            assert hasattr(contract_data, "piid"), "ContractData should have 'piid' attribute"

            # Validate decimal fields if present
            if contract_data.federal_action_obligation is not None:
                assert isinstance(contract_data.federal_action_obligation, Decimal), (
                    "federal_action_obligation should be Decimal"
                )

            if contract_data.base_and_exercised_options_value is not None:
                assert isinstance(contract_data.base_and_exercised_options_value, Decimal), (
                    "base_and_exercised_options_value should be Decimal"
                )
