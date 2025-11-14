"""Response validation utilities for integration tests"""

from datetime import date, datetime
from decimal import Decimal
from typing import Any


def validate_pagination(response: Any) -> None:
    """Validate paginated response structure

    Args:
        response: A PaginatedResponse object to validate

    Raises:
        AssertionError: If validation fails
    """
    assert hasattr(response, "count"), "Response missing 'count' attribute"
    assert hasattr(response, "results"), "Response missing 'results' attribute"
    assert isinstance(response.results, list), "Response 'results' must be a list"
    assert response.count >= 0, "Response 'count' must be non-negative"
    assert isinstance(response.count, int), "Response 'count' must be an integer"


def validate_contract_fields(contract: Any, minimal: bool = True) -> None:
    """Validate contract object has required fields and correct types

    Args:
        contract: A Contract object to validate
        minimal: If True, only validate minimal fields. If False, validate comprehensive fields.

    Raises:
        AssertionError: If validation fails
    """
    # Always present fields - contracts use 'key' field from API
    key = contract.get("key")
    assert key is not None, "Contract 'key' must not be None"
    # recipient_name may not be in minimal shapes, check if present
    if hasattr(contract, "recipient_name"):
        assert contract.recipient_name is not None, "Contract 'recipient_name' must not be None"

    # Type validation for optional fields (only check if field exists in shape)
    if hasattr(contract, "award_amount") and contract.award_amount is not None:
        assert isinstance(contract.award_amount, Decimal), (
            f"Contract 'award_amount' must be Decimal, got {type(contract.award_amount)}"
        )

    if hasattr(contract, "award_date") and contract.award_date is not None:
        assert isinstance(contract.award_date, date), (
            f"Contract 'award_date' must be date, got {type(contract.award_date)}"
        )

    if (
        hasattr(contract, "period_of_performance_start")
        and contract.period_of_performance_start is not None
    ):
        assert isinstance(contract.period_of_performance_start, date), (
            f"Contract 'period_of_performance_start' must be date, got {type(contract.period_of_performance_start)}"
        )

    if (
        hasattr(contract, "period_of_performance_end")
        and contract.period_of_performance_end is not None
    ):
        assert isinstance(contract.period_of_performance_end, date), (
            f"Contract 'period_of_performance_end' must be date, got {type(contract.period_of_performance_end)}"
        )

    if hasattr(contract, "last_modified") and contract.last_modified is not None:
        assert isinstance(contract.last_modified, datetime), (
            f"Contract 'last_modified' must be datetime, got {type(contract.last_modified)}"
        )

    # Comprehensive fields validation
    if not minimal:
        # When requesting comprehensive data, contract_data should be present
        # Note: This may be None if the API doesn't return it, so we check if it exists
        if hasattr(contract, "contract_data"):
            # If contract_data exists and is not None, validate it has some fields
            if contract.contract_data is not None:
                assert hasattr(contract.contract_data, "piid"), (
                    "ContractData must have 'piid' attribute"
                )


def validate_entity_fields(entity: Any) -> None:
    """Validate entity object has required fields and correct types

    Args:
        entity: An Entity object to validate (may be dict if model generation failed)

    Raises:
        AssertionError: If validation fails
    """
    # Handle dict fallback (if dynamic model generation failed)
    if isinstance(entity, dict):
        # For dicts, check if key exists
        if "key" in entity:
            assert entity["key"] is not None, "Entity 'key' must not be None"
        # legal_business_name may not be in all shapes, check if present
        if "legal_business_name" in entity:
            assert entity["legal_business_name"] is not None, (
                "Entity 'legal_business_name' must not be None"
            )
        return

    # Required fields
    # Entity doesn't have 'key' field - use 'uei' as identifier
    is_dict = isinstance(entity, dict)
    uei = entity.get("uei") if is_dict else getattr(entity, "uei", None)
    assert uei is not None, "Entity 'uei' must not be None"
    # legal_business_name may not be in all shapes, check if present
    if hasattr(entity, "legal_business_name"):
        assert entity.legal_business_name is not None, (
            "Entity 'legal_business_name' must not be None"
        )

    # Type validation for optional fields (only if present in shape)
    if hasattr(entity, "registration_date") and entity.registration_date is not None:
        assert isinstance(entity.registration_date, date), (
            f"Entity 'registration_date' must be date, got {type(entity.registration_date)}"
        )

    if hasattr(entity, "expiration_date") and entity.expiration_date is not None:
        assert isinstance(entity.expiration_date, date), (
            f"Entity 'expiration_date' must be date, got {type(entity.expiration_date)}"
        )

    if hasattr(entity, "last_updated") and entity.last_updated is not None:
        assert isinstance(entity.last_updated, datetime), (
            f"Entity 'last_updated' must be datetime, got {type(entity.last_updated)}"
        )

    if hasattr(entity, "business_types") and entity.business_types is not None:
        assert isinstance(entity.business_types, list), (
            f"Entity 'business_types' must be list, got {type(entity.business_types)}"
        )


def validate_agency_fields(agency: Any) -> None:
    """Validate agency object has required fields and correct types

    Args:
        agency: An Agency object to validate

    Raises:
        AssertionError: If validation fails
    """
    # Required fields
    assert agency.code is not None, "Agency 'code' must not be None"
    assert agency.name is not None, "Agency 'name' must not be None"

    # Type validation for required fields
    assert isinstance(agency.code, str), f"Agency 'code' must be string, got {type(agency.code)}"
    assert isinstance(agency.name, str), f"Agency 'name' must be string, got {type(agency.name)}"

    # Type validation for optional fields
    if agency.abbreviation is not None:
        assert isinstance(agency.abbreviation, str), (
            f"Agency 'abbreviation' must be string, got {type(agency.abbreviation)}"
        )

    if agency.department is not None:
        assert hasattr(agency.department, "name"), "Agency 'department' must have 'name' attribute"
        assert hasattr(agency.department, "code"), "Agency 'department' must have 'code' attribute"


def validate_no_parsing_errors(obj: Any) -> None:
    """Ensure object was parsed successfully and doesn't have all None values

    This is a heuristic check to detect parsing failures. If an object has
    all or nearly all None values, it likely indicates a parsing error.

    Args:
        obj: Any dataclass object to validate

    Raises:
        AssertionError: If the object appears to have failed parsing
    """
    # Get all attributes and their values
    # ShapedModel objects are dict-like (subclass of dict), so use dict() constructor
    # Regular dataclass objects need vars() or __dict__
    if isinstance(obj, dict):
        obj_vars = obj
    else:
        obj_vars = vars(obj) if hasattr(obj, "__dict__") else dict(obj)

    # Count non-None values
    non_none_count = sum(1 for v in obj_vars.values() if v is not None)
    total_count = len(obj_vars)

    # At least a few fields should parse successfully
    # We use a threshold of 2 to be lenient (e.g., key and name fields)
    # But for ShapedModel dict-like objects, we need to check the actual dict
    assert non_none_count >= 2, (
        f"Object appears to have parsing errors: only {non_none_count}/{total_count} "
        f"fields are non-None. Object: {obj}"
    )
