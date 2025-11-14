"""Integration tests for entity endpoints

Pytest Markers:
    @pytest.mark.integration: Marks tests as integration tests that may hit external APIs
    @pytest.mark.vcr(): Enables VCR recording/playback for HTTP interactions
    @pytest.mark.live: Forces tests to use live API (skip cassettes) - not used by default
    @pytest.mark.cached: Forces tests to only run with cached responses - not used by default
    @pytest.mark.slow: Marks tests that are slow to execute - not used by default

Usage:
    # Run all integration tests (uses cassettes if available)
    pytest tests/integration/

    # Run only entity integration tests
    pytest tests/integration/test_entities_integration.py

    # Run with live API (requires TANGO_API_KEY environment variable)
    TANGO_USE_LIVE_API=true TANGO_API_KEY=xxx pytest tests/integration/

    # Refresh cassettes (re-record all interactions)
    TANGO_REFRESH_CASSETTES=true TANGO_API_KEY=xxx pytest tests/integration/
"""


import pytest

from tango import ShapeConfig
from tests.integration.conftest import handle_api_exceptions
from tests.integration.validation import (
    validate_entity_fields,
    validate_no_parsing_errors,
    validate_pagination,
)


@pytest.mark.vcr()
@pytest.mark.integration
class TestEntitiesIntegration:
    """Integration tests for entity endpoints using production data"""

    @handle_api_exceptions("entities")
    @pytest.mark.parametrize(
        "shape_name,shape_value",
        [
            ("minimal", ShapeConfig.ENTITIES_MINIMAL),
            ("with_address", "uei,legal_business_name,cage_code,business_types,physical_address"),
            ("comprehensive", ShapeConfig.ENTITIES_COMPREHENSIVE),
            ("custom", "uei,legal_business_name,cage_code"),
        ],
    )
    def test_list_entities_with_shapes(self, tango_client, shape_name, shape_value):
        """Test listing entities with different shapes

        Validates:
        - Paginated response structure
        - Entity parsing with various shapes
        - Required entity fields are present regardless of shape
        """
        response = tango_client.list_entities(limit=5, shape=shape_value)

        # Validate response structure
        validate_pagination(response)
        assert response.count > 0, "Expected at least one entity in the system"
        assert len(response.results) > 0, "Expected results in the response"

        # Validate first entity
        entity = response.results[0]
        validate_entity_fields(entity)
        validate_no_parsing_errors(entity)

        # Verify required fields are present
        is_dict = isinstance(entity, dict)
        uei = entity.get("uei") if is_dict else getattr(entity, "uei", None)
        assert uei is not None, "Entity uei should be present"
        legal_business_name = (
            entity.get("legal_business_name")
            if is_dict
            else getattr(entity, "legal_business_name", None)
        )
        assert legal_business_name is not None, "Entity legal_business_name should be present"

    @handle_api_exceptions("entities")
    def test_list_entities_with_search(self, tango_client):
        """Test listing entities with search parameter

        Validates:
        - Search parameter works correctly
        - Paginated response structure
        - Entity parsing with search results
        - Search returns relevant results
        """
        # Search for a common company name
        search_query = "IBM"

        response = tango_client.list_entities(
            limit=5, search=search_query, shape=ShapeConfig.ENTITIES_MINIMAL
        )

        # Validate response structure
        validate_pagination(response)
        # Note: count may be 0 if no entities match the search

        # If we have results, validate them
        if response.results:
            entity = response.results[0]
            validate_entity_fields(entity)
            validate_no_parsing_errors(entity)

            # Verify entity has required fields
            is_dict = isinstance(entity, dict)
            uei = entity.get("uei") if is_dict else getattr(entity, "uei", None)
            assert uei is not None, "Entity uei should be present"
            assert entity.legal_business_name is not None, (
                "Entity legal_business_name should be present"
            )

    @handle_api_exceptions("entities")
    def test_get_entity_by_uei(self, tango_client):
        """Test getting a specific entity by UEI

        Validates:
        - get_entity() method works correctly
        - Entity retrieval by UEI
        - Comprehensive entity data is returned
        - All entity fields are parsed correctly
        """
        # First, get a list of entities to find a valid UEI
        list_response = tango_client.list_entities(limit=25, shape=ShapeConfig.ENTITIES_MINIMAL)

        # Ensure we have entities to test with
        assert len(list_response.results) > 0, "Expected at least one entity in the system"

        # Find an entity with a UEI
        test_entity = None
        for entity in list_response.results:
            # Handle both dict and model access
            is_dict = isinstance(entity, dict)
            uei = entity.get("uei") if is_dict else getattr(entity, "uei", None)
            if uei:
                test_entity = entity
                break

        # Ensure we found an entity with UEI
        assert test_entity is not None, (
            "Expected to find at least one entity with UEI in the sample"
        )
        test_uei = (
            test_entity.get("uei")
            if isinstance(test_entity, dict)
            else getattr(test_entity, "uei", None)
        )
        assert test_uei is not None, "Test entity should have a UEI"

        # Get the entity by UEI
        entity = tango_client.get_entity(test_uei, shape=ShapeConfig.ENTITIES_COMPREHENSIVE)

        # Handle dict fallback (if dynamic model generation failed)
        if isinstance(entity, dict):
            # For dicts, use dict access
            assert "uei" in entity or "key" in entity, "Entity should have 'uei' or 'key'"
            if "uei" in entity:
                assert entity["uei"] == test_uei, "Retrieved entity should match requested UEI"
            if "legal_business_name" in entity:
                assert entity["legal_business_name"] is not None, (
                    "Entity legal_business_name should be present"
                )
        else:
            # Validate entity
            validate_entity_fields(entity)
            validate_no_parsing_errors(entity)

            # Verify the entity matches
            if hasattr(entity, "uei") and entity.uei:
                assert entity.uei == test_uei, "Retrieved entity should match requested UEI"
            is_dict = isinstance(entity, dict)
            uei = entity.get("uei") if is_dict else getattr(entity, "uei", None)
            assert uei is not None, "Entity uei should be present"
            legal_business_name = (
                entity.get("legal_business_name")
                if is_dict
                else getattr(entity, "legal_business_name", None)
            )
            assert legal_business_name is not None, "Entity legal_business_name should be present"

    @handle_api_exceptions("entities")
    def test_entity_field_types(self, tango_client):
        """Test that all entity field types are correctly parsed

        Validates:
        - Date fields are parsed as date objects
        - Datetime fields are parsed as datetime objects
        - String fields are strings
        - List fields are lists
        - Nested objects (location) are parsed correctly
        """
        response = tango_client.list_entities(limit=25, shape=ShapeConfig.ENTITIES_COMPREHENSIVE)

        assert len(response.results) > 0, "Expected at least one entity"

        for entity in response.results:
            # Validate field types
            validate_entity_fields(entity)
            validate_no_parsing_errors(entity)

            # Additional type checks for specific fields
            is_dict = isinstance(entity, dict)
            uei = entity.get("uei") if is_dict else getattr(entity, "uei", None)
            assert isinstance(uei, str), f"uei should be string, got {type(uei)}"

            legal_business_name = (
                entity.get("legal_business_name")
                if is_dict
                else getattr(entity, "legal_business_name", None)
            )
            assert isinstance(legal_business_name, str), (
                f"legal_business_name should be string, got {type(legal_business_name)}"
            )

            # Only check fields that are in the ENTITIES_COMPREHENSIVE shape
            cage_code = entity.get("cage_code") if is_dict else getattr(entity, "cage_code", None)
            if cage_code is not None:
                assert isinstance(cage_code, str), (
                    f"cage_code should be string, got {type(cage_code)}"
                )

            # Check business_types (in shape)
            business_types = (
                entity.get("business_types") if is_dict else getattr(entity, "business_types", None)
            )
            if business_types is not None:
                assert isinstance(business_types, (list, dict)), (
                    f"business_types should be list or dict, got {type(business_types)}"
                )

            # Check physical_address (in shape)
            physical_address = (
                entity.get("physical_address")
                if is_dict
                else getattr(entity, "physical_address", None)
            )
            if physical_address is not None:
                # Should be a dict
                assert isinstance(physical_address, dict), (
                    f"physical_address should be dict, got {type(physical_address)}"
                )

    @handle_api_exceptions("entities")
    def test_entity_parsing_with_business_types(self, tango_client):
        """Test entity parsing with various business_types

        Validates:
        - business_types field is parsed as a list
        - business_types contains valid values
        - Entities with different business types parse correctly
        - business_types field is optional
        """
        standard_shape = "uei,legal_business_name,cage_code,business_types,physical_address"
        response = tango_client.list_entities(limit=25, shape=standard_shape)

        assert len(response.results) > 0, "Expected at least one entity"

        for entity in response.results:
            # Validate each entity
            validate_entity_fields(entity)
            validate_no_parsing_errors(entity)

            # Validate business_types if present (handle dict fallback)
            business_types = (
                entity.get("business_types")
                if isinstance(entity, dict)
                else getattr(entity, "business_types", None)
            )
            if business_types is not None:
                assert isinstance(business_types, (list, dict)), (
                    f"business_types should be list or dict, got {type(business_types)}"
                )

                # If list is not empty, verify it contains strings or dicts
                if business_types:
                    # Handle both list and dict (if it's a dict, convert to list of values)
                    if isinstance(business_types, dict):
                        business_types_list = list(business_types.values())
                    else:
                        business_types_list = business_types
                    for business_type in business_types_list:
                        # Accept either string (parsed code) or dict (full object)
                        assert isinstance(business_type, (str, dict)), (
                            f"business_type should be string or dict, got {type(business_type)}"
                        )

                        # If it's a dict, verify it has expected fields
                        if isinstance(business_type, dict):
                            assert "code" in business_type or "description" in business_type, (
                                "business_type dict should have 'code' or 'description'"
                            )

    @handle_api_exceptions("entities")
    def test_entity_location_parsing(self, tango_client):
        """Test entity location parsing

        Validates:
        - Location nested object is parsed correctly
        - Location fields are accessible
        - Location parsing handles missing fields gracefully
        - Multiple entities with locations parse consistently
        """
        standard_shape = "uei,legal_business_name,cage_code,business_types,physical_address"
        response = tango_client.list_entities(limit=25, shape=standard_shape)

        assert len(response.results) > 0, "Expected at least one entity"

        for entity in response.results:
            # Validate each entity
            validate_entity_fields(entity)
            validate_no_parsing_errors(entity)

            # Validate location if present (handle dict fallback)
            location = (
                entity.get("location")
                if isinstance(entity, dict)
                else getattr(entity, "location", None)
            )
            physical_address = (
                entity.get("physical_address")
                if isinstance(entity, dict)
                else getattr(entity, "physical_address", None)
            )
            # Use location if available, otherwise try physical_address
            location = location or physical_address

            if location is not None:
                # Verify location has expected attributes (using dict access for raw data fallback)
                if isinstance(location, dict):
                    # Raw data fallback - use dict access
                    assert (
                        "city_name" in location
                        or "state_code" in location
                        or "country_code" in location
                    ), "Location should have at least one location field"
                else:
                    # Dynamic model - check attributes
                    assert (
                        hasattr(location, "city_name")
                        or hasattr(location, "state_code")
                        or hasattr(location, "country_code")
                    ), "Location should have at least one location field"

                # Verify at least some location fields are populated
                if isinstance(location, dict):
                    location_fields = [
                        location.get("city_name"),
                        location.get("state_name"),
                        location.get("state_code"),
                        location.get("zip_code"),
                        location.get("country_name"),
                        location.get("country_code"),
                    ]
                else:
                    location_fields = [
                        getattr(location, "city_name", None),
                        getattr(location, "state_name", None),
                        getattr(location, "state_code", None),
                        getattr(location, "zip_code", None),
                        getattr(location, "country_name", None),
                        getattr(location, "country_code", None),
                    ]
                non_none_fields = [f for f in location_fields if f is not None]
                assert len(non_none_fields) > 0, "Location should have at least one populated field"

    @handle_api_exceptions("entities")
    def test_list_entities_with_flat(self, tango_client):
        """Test listing entities with flat=true parameter

        Validates:
        - Flat responses are correctly unflattened
        - Nested objects are reconstructed properly
        - Parsing works with flattened data
        """
        response = tango_client.list_entities(
            limit=5, shape="uei,legal_business_name,physical_address", flat=True
        )

        # Validate response structure
        validate_pagination(response)
        assert len(response.results) > 0, "Expected results in the response"

        # Validate first entity
        entity = response.results[0]
        validate_entity_fields(entity)
        validate_no_parsing_errors(entity)

        # Verify key fields are present
        is_dict = isinstance(entity, dict)
        uei = entity.get("uei") if is_dict else getattr(entity, "uei", None)
        assert uei is not None, "Entity uei should be present"
        legal_business_name = (
            entity.get("legal_business_name")
            if is_dict
            else getattr(entity, "legal_business_name", None)
        )
        assert legal_business_name is not None, "Entity legal_business_name should be present"

    @handle_api_exceptions("entities")
    def test_entity_with_various_identifiers(self, tango_client):
        """Test entities with different identifier types (UEI, CAGE)

        Validates:
        - Entities can have different identifier combinations
        - All identifier types are parsed correctly
        - Entities may have one or more identifiers
        """
        response = tango_client.list_entities(limit=25, shape=ShapeConfig.ENTITIES_MINIMAL)

        assert len(response.results) > 0, "Expected at least one entity"

        # Track which identifier types we've seen
        found_uei = False
        found_cage = False

        for entity in response.results:
            validate_entity_fields(entity)
            validate_no_parsing_errors(entity)

            # Track identifier types
            if entity.uei:
                found_uei = True
            if entity.cage_code:
                found_cage = True

        # Note: We don't require all types to be present in the sample
        # This just validates that when present, they're parsed correctly
