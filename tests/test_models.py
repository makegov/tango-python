"""Tests for data models and model factory

This module tests:
- Basic data models (PaginatedResponse)
- ModelFactory for creating dynamic model instances
"""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

import pytest

from tango.exceptions import ModelInstantiationError
from tango.models import PaginatedResponse
from tango.shapes import (
    ModelFactory,
    ShapeParser,
    TypeGenerator,
    create_default_parser_registry,
)

# ============================================================================
# Test Models
# ============================================================================


@dataclass
class MockLocation:
    """Mock location model for testing"""

    city: str | None = None
    state: str | None = None
    zip_code: str | None = None


@dataclass
class MockRecipient:
    """Mock recipient model for testing"""

    display_name: str
    uei: str | None = None
    location: MockLocation | None = None


@dataclass
class MockContract:
    """Mock contract model for testing"""

    key: str
    piid: str | None = None
    description: str | None = None
    award_date: date | None = None
    award_amount: Decimal | None = None
    recipient: MockRecipient | None = None
    tags: list[str] | None = None


# ============================================================================
# Basic Model Tests
# ============================================================================


class TestPaginatedResponse:
    """Test PaginatedResponse model"""

    def test_paginated_response(self):
        """Test PaginatedResponse model"""
        response = PaginatedResponse(
            count=100,
            next="https://api.example.com/page2",
            previous=None,
            results=["item1", "item2"],
        )

        assert response.count == 100
        assert len(response.results) == 2
        assert response.next is not None
        assert response.previous is None


# ============================================================================
# ModelFactory Tests
# ============================================================================


class TestModelFactorySimple:
    """Test simple instance creation"""

    def test_create_instance_simple_fields(self):
        """Test creating instance with simple fields"""
        parser = ShapeParser()
        generator = TypeGenerator()
        parsers = create_default_parser_registry()
        factory = ModelFactory(generator, parsers)

        shape_spec = parser.parse("key,piid,description")
        dynamic_type = generator.generate_type(shape_spec, MockContract)

        data = {"key": "CONTRACT-123", "piid": "ABC123", "description": "Test contract"}

        instance = factory.create_instance(data, shape_spec, MockContract, dynamic_type)

        assert instance["key"] == "CONTRACT-123"
        assert instance["piid"] == "ABC123"
        assert instance["description"] == "Test contract"

    def test_create_instance_missing_fields(self):
        """Test creating instance with missing fields sets them to None"""
        parser = ShapeParser()
        generator = TypeGenerator()
        parsers = create_default_parser_registry()
        factory = ModelFactory(generator, parsers)

        shape_spec = parser.parse("key,piid,description")
        dynamic_type = generator.generate_type(shape_spec, MockContract)

        data = {"key": "CONTRACT-123", "piid": "ABC123"}

        instance = factory.create_instance(data, shape_spec, MockContract, dynamic_type)

        assert instance["key"] == "CONTRACT-123"
        assert instance["piid"] == "ABC123"
        assert instance["description"] is None

    def test_create_instance_with_alias(self):
        """Test creating instance with field alias"""
        parser = ShapeParser()
        generator = TypeGenerator()
        parsers = create_default_parser_registry()
        factory = ModelFactory(generator, parsers)

        shape_spec = parser.parse("key,piid::contract_id")
        dynamic_type = generator.generate_type(shape_spec, MockContract)

        data = {"key": "CONTRACT-123", "piid": "ABC123"}

        instance = factory.create_instance(data, shape_spec, MockContract, dynamic_type)

        assert instance["key"] == "CONTRACT-123"
        assert instance["contract_id"] == "ABC123"  # Aliased field


class TestModelFactoryFieldParsing:
    """Test field parsing with various types"""

    def test_parse_date_field(self):
        """Test parsing date fields"""
        parser = ShapeParser()
        generator = TypeGenerator()
        parsers = create_default_parser_registry()
        factory = ModelFactory(generator, parsers)

        shape_spec = parser.parse("key,award_date")
        dynamic_type = generator.generate_type(shape_spec, MockContract)

        data = {"key": "CONTRACT-123", "award_date": "2024-01-15"}

        instance = factory.create_instance(data, shape_spec, MockContract, dynamic_type)

        assert instance["key"] == "CONTRACT-123"
        assert instance["award_date"] == date(2024, 1, 15)

    def test_parse_decimal_field(self):
        """Test parsing Decimal fields"""
        parser = ShapeParser()
        generator = TypeGenerator()
        parsers = create_default_parser_registry()
        factory = ModelFactory(generator, parsers)

        shape_spec = parser.parse("key,award_amount")
        dynamic_type = generator.generate_type(shape_spec, MockContract)

        data = {"key": "CONTRACT-123", "award_amount": "1234567.89"}

        instance = factory.create_instance(data, shape_spec, MockContract, dynamic_type)

        assert instance["key"] == "CONTRACT-123"
        assert instance["award_amount"] == Decimal("1234567.89")

    def test_parse_null_values(self):
        """Test parsing null/None values"""
        parser = ShapeParser()
        generator = TypeGenerator()
        parsers = create_default_parser_registry()
        factory = ModelFactory(generator, parsers)

        shape_spec = parser.parse("key,award_date,award_amount")
        dynamic_type = generator.generate_type(shape_spec, MockContract)

        data = {"key": "CONTRACT-123", "award_date": None, "award_amount": None}

        instance = factory.create_instance(data, shape_spec, MockContract, dynamic_type)

        assert instance["key"] == "CONTRACT-123"
        assert instance["award_date"] is None
        assert instance["award_amount"] is None


class TestModelFactoryNestedObjects:
    """Test nested object creation"""

    def test_create_nested_instance(self):
        """Test creating instance with nested object"""
        parser = ShapeParser()
        generator = TypeGenerator()
        parsers = create_default_parser_registry()
        factory = ModelFactory(generator, parsers)

        shape_spec = parser.parse("key,recipient(display_name,uei)")
        dynamic_type = generator.generate_type(shape_spec, MockContract)

        data = {
            "key": "CONTRACT-123",
            "recipient": {"display_name": "Acme Corp", "uei": "UEI123456"},
        }

        instance = factory.create_instance(data, shape_spec, MockContract, dynamic_type)

        assert instance["key"] == "CONTRACT-123"
        assert instance["recipient"]["display_name"] == "Acme Corp"
        assert instance["recipient"]["uei"] == "UEI123456"

    def test_create_deeply_nested_instance(self):
        """Test creating instance with deeply nested objects"""
        parser = ShapeParser()
        generator = TypeGenerator()
        parsers = create_default_parser_registry()
        factory = ModelFactory(generator, parsers)

        shape_spec = parser.parse("key,recipient(display_name,location(city,state))")
        dynamic_type = generator.generate_type(shape_spec, MockContract)

        data = {
            "key": "CONTRACT-123",
            "recipient": {
                "display_name": "Acme Corp",
                "location": {"city": "New York", "state": "NY"},
            },
        }

        instance = factory.create_instance(data, shape_spec, MockContract, dynamic_type)

        assert instance["key"] == "CONTRACT-123"
        assert instance["recipient"]["display_name"] == "Acme Corp"
        assert instance["recipient"]["location"]["city"] == "New York"
        assert instance["recipient"]["location"]["state"] == "NY"

    def test_create_nested_instance_missing_data(self):
        """Test creating nested instance with missing nested data"""
        parser = ShapeParser()
        generator = TypeGenerator()
        parsers = create_default_parser_registry()
        factory = ModelFactory(generator, parsers)

        shape_spec = parser.parse("key,recipient(display_name,uei)")
        dynamic_type = generator.generate_type(shape_spec, MockContract)

        data = {"key": "CONTRACT-123", "recipient": None}

        instance = factory.create_instance(data, shape_spec, MockContract, dynamic_type)

        assert instance["key"] == "CONTRACT-123"
        assert instance["recipient"] is None


class TestModelFactoryWildcards:
    """Test wildcard handling"""

    def test_wildcard_top_level(self):
        """Test wildcard at top level includes all fields"""
        parser = ShapeParser()
        generator = TypeGenerator()
        parsers = create_default_parser_registry()
        factory = ModelFactory(generator, parsers)

        shape_spec = parser.parse("*")
        dynamic_type = generator.generate_type(shape_spec, MockContract)

        data = {
            "key": "CONTRACT-123",
            "piid": "ABC123",
            "description": "Test contract",
            "award_date": "2024-01-15",
        }

        instance = factory.create_instance(data, shape_spec, MockContract, dynamic_type)

        assert instance["key"] == "CONTRACT-123"
        assert instance["piid"] == "ABC123"
        assert instance["description"] == "Test contract"
        assert instance["award_date"] == date(2024, 1, 15)

    def test_wildcard_nested(self):
        """Test wildcard in nested object"""
        parser = ShapeParser()
        generator = TypeGenerator()
        parsers = create_default_parser_registry()
        factory = ModelFactory(generator, parsers)

        shape_spec = parser.parse("key,recipient(*)")
        dynamic_type = generator.generate_type(shape_spec, MockContract)

        data = {
            "key": "CONTRACT-123",
            "recipient": {"display_name": "Acme Corp", "uei": "UEI123456"},
        }

        instance = factory.create_instance(data, shape_spec, MockContract, dynamic_type)

        assert instance["key"] == "CONTRACT-123"
        assert instance["recipient"]["display_name"] == "Acme Corp"
        assert instance["recipient"]["uei"] == "UEI123456"


class TestModelFactoryValidation:
    """Test validation functionality"""

    def test_validate_data_valid(self):
        """Test validation with valid data"""
        parser = ShapeParser()
        generator = TypeGenerator()
        parsers = create_default_parser_registry()
        factory = ModelFactory(generator, parsers)

        shape_spec = parser.parse("key,piid,description")

        data = {"key": "CONTRACT-123", "piid": "ABC123", "description": "Test contract"}

        errors = factory.validate_data(data, shape_spec, MockContract)

        assert len(errors) == 0

    def test_validate_data_missing_fields(self):
        """Test validation with missing fields (should be OK)"""
        parser = ShapeParser()
        generator = TypeGenerator()
        parsers = create_default_parser_registry()
        factory = ModelFactory(generator, parsers)

        shape_spec = parser.parse("key,piid,description")

        data = {"key": "CONTRACT-123"}

        errors = factory.validate_data(data, shape_spec, MockContract)

        # Missing fields are OK - they'll be set to None
        assert len(errors) == 0

    def test_validate_data_wrong_type(self):
        """Test validation with wrong data type"""
        parser = ShapeParser()
        generator = TypeGenerator()
        parsers = create_default_parser_registry()
        factory = ModelFactory(generator, parsers)

        shape_spec = parser.parse("key,tags")

        data = {
            "key": "CONTRACT-123",
            "tags": "not-a-list",  # Should be a list
        }

        errors = factory.validate_data(data, shape_spec, MockContract)

        assert len(errors) > 0
        assert "should be a list" in errors[0]

    def test_validation_mode_logs_warnings(self):
        """Test validation mode logs warnings for invalid fields"""
        parser = ShapeParser()
        generator = TypeGenerator()
        parsers = create_default_parser_registry()
        factory = ModelFactory(generator, parsers)

        shape_spec = parser.parse("key,invalid_field")
        dynamic_type = generator.generate_type(shape_spec, MockContract)

        data = {"key": "CONTRACT-123", "invalid_field": "value"}

        # Should not raise, just log warning
        instance = factory.create_instance(data, shape_spec, MockContract, dynamic_type)

        assert instance["key"] == "CONTRACT-123"
        assert instance["invalid_field"] == "value"


class TestModelFactoryErrorHandling:
    """Test error handling"""

    def test_invalid_data_type(self):
        """Test error when data is not a dictionary"""
        parser = ShapeParser()
        generator = TypeGenerator()
        parsers = create_default_parser_registry()
        factory = ModelFactory(generator, parsers)

        shape_spec = parser.parse("key")
        dynamic_type = generator.generate_type(shape_spec, MockContract)

        with pytest.raises(ModelInstantiationError) as exc_info:
            factory.create_instance("not-a-dict", shape_spec, MockContract, dynamic_type)

        assert "Expected dictionary" in str(exc_info.value)

    def test_parser_failure_logs_warning(self):
        """Test parser failure logs warning and uses raw value"""
        parser = ShapeParser()
        generator = TypeGenerator()

        parsers = create_default_parser_registry()

        def failing_parser(value):
            raise ValueError("Parse failed")

        parsers["date"] = failing_parser

        factory = ModelFactory(generator, parsers)

        shape_spec = parser.parse("key,award_date")
        dynamic_type = generator.generate_type(shape_spec, MockContract)

        data = {"key": "CONTRACT-123", "award_date": "2024-01-15"}

        # Should not raise, just log warning and use raw value
        instance = factory.create_instance(data, shape_spec, MockContract, dynamic_type)

        assert instance["key"] == "CONTRACT-123"
        assert instance["award_date"] == "2024-01-15"  # Raw value used
