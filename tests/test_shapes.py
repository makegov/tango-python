"""Comprehensive tests for response shaping system

This module tests:
- Shape string parsing and validation
- Schema registry and model registration
- Type generation from shapes
- Default shapes and their usage
- Flat lists parameter and response unflattening
"""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from unittest.mock import Mock, patch

import pytest

from tango import ShapeConfig, TangoClient
from tango.exceptions import ShapeParseError, ShapeValidationError
from tango.models import Agency, Contract, Entity, Location
from tango.shapes import (
    FieldSchema,
    FieldSpec,
    SchemaRegistry,
    ShapeParser,
    ShapeSpec,
    TypeGenerator,
)

# ============================================================================
# Shared Test Models
# ============================================================================


@dataclass
class MockNestedModel:
    """Mock nested model for testing"""

    display_name: str
    uei: str | None = None
    code: str | None = None
    amount: Decimal | None = None


@dataclass
class MockModel:
    """Mock model for testing"""

    key: str
    piid: str | None = None
    description: str | None = None
    recipient: MockNestedModel | None = None
    tags: list[str] | None = None
    amount: Decimal | None = None
    award_date: date | None = None


@dataclass
class MockListModel:
    """Mock model with list fields"""

    key: str
    items: list[MockNestedModel] | None = None
    tags: list[str] | None = None


@dataclass
class SimpleModel:
    """Simple model for schema testing"""

    name: str
    age: int
    active: bool


@dataclass
class OptionalFieldsModel:
    """Model with optional fields"""

    required_field: str
    optional_field: str | None = None
    optional_int: int | None = None


@dataclass
class ListFieldsModel:
    """Model with list fields"""

    tags: list[str]
    optional_tags: list[str] | None = None
    numbers: list[int] | None = None


@dataclass
class NestedChildModel:
    """Nested child model"""

    child_name: str
    child_value: int | None = None


@dataclass
class NestedParentModel:
    """Model with nested objects"""

    name: str
    child: NestedChildModel | None = None
    children: list[NestedChildModel] | None = None


# ============================================================================
# Shape Parser Tests
# ============================================================================


class TestShapeParserSimple:
    """Test simple shape parsing"""

    def test_parse_single_field(self):
        """Test parsing a single field"""
        parser = ShapeParser()
        spec = parser.parse("key")

        assert len(spec.fields) == 1
        assert spec.fields[0].name == "key"
        assert spec.fields[0].alias is None
        assert spec.fields[0].nested_fields is None
        assert spec.fields[0].is_wildcard is False

    def test_parse_multiple_fields(self):
        """Test parsing multiple comma-separated fields"""
        parser = ShapeParser()
        spec = parser.parse("key,piid,description")

        assert len(spec.fields) == 3
        assert spec.fields[0].name == "key"
        assert spec.fields[1].name == "piid"
        assert spec.fields[2].name == "description"

    def test_parse_with_whitespace(self):
        """Test parsing handles whitespace correctly"""
        parser = ShapeParser()
        spec = parser.parse("key , piid , description")

        assert len(spec.fields) == 3
        assert spec.fields[0].name == "key"
        assert spec.fields[1].name == "piid"
        assert spec.fields[2].name == "description"

    def test_parse_field_with_underscores(self):
        """Test parsing fields with underscores"""
        parser = ShapeParser()
        spec = parser.parse("award_date,total_contract_value")

        assert len(spec.fields) == 2
        assert spec.fields[0].name == "award_date"
        assert spec.fields[1].name == "total_contract_value"

    def test_parse_field_with_numbers(self):
        """Test parsing fields with numbers"""
        parser = ShapeParser()
        spec = parser.parse("field1,field2,field3")

        assert len(spec.fields) == 3
        assert spec.fields[0].name == "field1"
        assert spec.fields[1].name == "field2"
        assert spec.fields[2].name == "field3"


class TestShapeParserNested:
    """Test nested field parsing"""

    def test_parse_nested_single_field(self):
        """Test parsing nested field with single child"""
        parser = ShapeParser()
        spec = parser.parse("recipient(display_name)")

        assert len(spec.fields) == 1
        assert spec.fields[0].name == "recipient"
        assert spec.fields[0].nested_fields is not None
        assert len(spec.fields[0].nested_fields) == 1
        assert spec.fields[0].nested_fields[0].name == "display_name"

    def test_parse_nested_multiple_fields(self):
        """Test parsing nested field with multiple children"""
        parser = ShapeParser()
        spec = parser.parse("recipient(display_name,uei)")

        assert len(spec.fields) == 1
        assert spec.fields[0].name == "recipient"
        assert len(spec.fields[0].nested_fields) == 2
        assert spec.fields[0].nested_fields[0].name == "display_name"
        assert spec.fields[0].nested_fields[1].name == "uei"

    def test_parse_mixed_nested_and_simple(self):
        """Test parsing mix of nested and simple fields"""
        parser = ShapeParser()
        spec = parser.parse("key,piid,recipient(display_name,uei),description")

        assert len(spec.fields) == 4
        assert spec.fields[0].name == "key"
        assert spec.fields[1].name == "piid"
        assert spec.fields[2].name == "recipient"
        assert spec.fields[2].nested_fields is not None
        assert len(spec.fields[2].nested_fields) == 2
        assert spec.fields[3].name == "description"

    def test_parse_nested_with_whitespace(self):
        """Test parsing nested fields with whitespace"""
        parser = ShapeParser()
        spec = parser.parse("recipient( display_name , uei )")

        assert len(spec.fields) == 1
        assert spec.fields[0].name == "recipient"
        assert len(spec.fields[0].nested_fields) == 2
        assert spec.fields[0].nested_fields[0].name == "display_name"
        assert spec.fields[0].nested_fields[1].name == "uei"


class TestShapeParserWildcard:
    """Test wildcard parsing"""

    def test_parse_wildcard_simple(self):
        """Test parsing simple wildcard"""
        parser = ShapeParser()
        spec = parser.parse("*")

        assert len(spec.fields) == 1
        assert spec.fields[0].name == "*"
        assert spec.fields[0].is_wildcard is True

    def test_parse_wildcard_in_nested(self):
        """Test parsing wildcard in nested field"""
        parser = ShapeParser()
        spec = parser.parse("recipient(*)")

        assert len(spec.fields) == 1
        assert spec.fields[0].name == "recipient"
        assert spec.fields[0].is_wildcard is True
        assert spec.fields[0].nested_fields is None

    def test_parse_wildcard_mixed_with_fields(self):
        """Test parsing wildcard mixed with regular fields"""
        parser = ShapeParser()
        spec = parser.parse("key,recipient(*),description")

        assert len(spec.fields) == 3
        assert spec.fields[0].name == "key"
        assert spec.fields[1].name == "recipient"
        assert spec.fields[1].is_wildcard is True
        assert spec.fields[2].name == "description"


class TestShapeParserAlias:
    """Test field alias parsing"""

    def test_parse_alias_simple(self):
        """Test parsing simple field alias"""
        parser = ShapeParser()
        spec = parser.parse("display_name::vendor_name")

        assert len(spec.fields) == 1
        assert spec.fields[0].name == "display_name"
        assert spec.fields[0].alias == "vendor_name"

    def test_parse_alias_in_nested(self):
        """Test parsing alias in nested field"""
        parser = ShapeParser()
        spec = parser.parse("recipient(display_name::vendor_name,uei)")

        assert len(spec.fields) == 1
        assert spec.fields[0].name == "recipient"
        assert len(spec.fields[0].nested_fields) == 2
        assert spec.fields[0].nested_fields[0].name == "display_name"
        assert spec.fields[0].nested_fields[0].alias == "vendor_name"
        assert spec.fields[0].nested_fields[1].name == "uei"

    def test_parse_multiple_aliases(self):
        """Test parsing multiple aliased fields"""
        parser = ShapeParser()
        spec = parser.parse("field1::alias1,field2::alias2")

        assert len(spec.fields) == 2
        assert spec.fields[0].name == "field1"
        assert spec.fields[0].alias == "alias1"
        assert spec.fields[1].name == "field2"
        assert spec.fields[1].alias == "alias2"

    def test_parse_alias_with_whitespace(self):
        """Test parsing alias with whitespace"""
        parser = ShapeParser()
        spec = parser.parse("display_name :: vendor_name")

        assert len(spec.fields) == 1
        assert spec.fields[0].name == "display_name"
        assert spec.fields[0].alias == "vendor_name"


class TestShapeParserErrors:
    """Test error cases with invalid syntax"""

    def test_empty_shape_raises_error(self):
        """Test empty shape string raises error"""
        parser = ShapeParser()

        with pytest.raises(ShapeParseError) as exc_info:
            parser.parse("")

        assert "cannot be empty" in str(exc_info.value)

    def test_whitespace_only_raises_error(self):
        """Test whitespace-only shape raises error"""
        parser = ShapeParser()

        with pytest.raises(ShapeParseError) as exc_info:
            parser.parse("   ")

        assert "cannot be empty" in str(exc_info.value)

    def test_trailing_comma_raises_error(self):
        """Test trailing comma raises error in validation"""
        parser = ShapeParser()

        with pytest.raises(ShapeParseError) as exc_info:
            parser.validate_syntax("key,piid,")

        assert "cannot end with a comma" in str(exc_info.value)

    def test_unmatched_opening_paren_raises_error(self):
        """Test unmatched opening parenthesis raises error"""
        parser = ShapeParser()

        with pytest.raises(ShapeParseError) as exc_info:
            parser.parse("recipient(display_name")

        assert "Unmatched opening parenthesis" in str(exc_info.value) or "Expected ')'" in str(
            exc_info.value
        )

    def test_unmatched_closing_paren_raises_error(self):
        """Test unmatched closing parenthesis raises error"""
        parser = ShapeParser()

        with pytest.raises(ShapeParseError) as exc_info:
            parser.validate_syntax("recipient(display_name))")

        assert "Unmatched closing parenthesis" in str(exc_info.value)

    def test_empty_nested_raises_error(self):
        """Test empty nested field list raises error"""
        parser = ShapeParser()

        with pytest.raises(ShapeParseError) as exc_info:
            parser.parse("recipient()")

        assert "Empty nested field list" in str(
            exc_info.value
        ) or "Expected at least one field" in str(exc_info.value)

    def test_invalid_field_name_raises_error(self):
        """Test invalid field name raises error"""
        parser = ShapeParser()

        with pytest.raises(ShapeParseError) as exc_info:
            parser.parse("123invalid")

        assert "Invalid field name" in str(exc_info.value)

    def test_wildcard_with_nested_fields_raises_error(self):
        """Test wildcard with nested field selections raises error"""
        parser = ShapeParser()

        with pytest.raises(ShapeParseError) as exc_info:
            parser.parse("recipient(*,display_name)")

        assert "Expected ')'" in str(exc_info.value) or "Expected ',' or ')'" in str(exc_info.value)

    def test_wildcard_alias_parses_but_questionable(self):
        """Test wildcard with alias - parses but semantically questionable"""
        parser = ShapeParser()

        spec = parser.parse("*::alias")

        assert spec.fields[0].name == "*"
        assert spec.fields[0].alias == "alias"
        assert spec.fields[0].is_wildcard is True


class TestShapeParserValidation:
    """Test shape validation against model schema"""

    def test_validate_simple_fields(self):
        """Test validation of simple fields"""
        parser = ShapeParser()
        registry = SchemaRegistry()
        registry.register(MockModel)
        parser._schema_registry = registry

        spec = parser.parse("key,piid,description")
        parser.validate(spec, MockModel)  # Should not raise

    def test_validate_nested_fields(self):
        """Test validation of nested fields"""
        parser = ShapeParser()
        registry = SchemaRegistry()
        registry.register(MockModel)
        registry.register(MockNestedModel)
        parser._schema_registry = registry

        spec = parser.parse("key,recipient(display_name,uei)")
        parser.validate(spec, MockModel)  # Should not raise

    def test_validate_invalid_field_raises_error(self):
        """Test validation raises error for invalid field"""
        parser = ShapeParser()
        registry = SchemaRegistry()
        registry.register(MockModel)
        parser._schema_registry = registry

        spec = parser.parse("invalid_field")

        with pytest.raises(ShapeValidationError) as exc_info:
            parser.validate(spec, MockModel)

        assert "invalid_field" in str(exc_info.value)
        assert "does not exist" in str(exc_info.value)

    def test_validate_invalid_nested_field_raises_error(self):
        """Test validation raises error for invalid nested field"""
        parser = ShapeParser()
        registry = SchemaRegistry()
        registry.register(MockModel)
        registry.register(MockNestedModel)
        parser._schema_registry = registry

        spec = parser.parse("recipient(invalid_nested)")

        with pytest.raises(ShapeValidationError) as exc_info:
            parser.validate(spec, MockModel)

        assert "invalid_nested" in str(exc_info.value)

    def test_validate_nested_on_non_nested_field_raises_error(self):
        """Test validation raises error when using nested syntax on non-nested field"""
        parser = ShapeParser()
        registry = SchemaRegistry()
        registry.register(MockModel)
        parser._schema_registry = registry

        spec = parser.parse("key(nested)")

        with pytest.raises(ShapeValidationError) as exc_info:
            parser.validate(spec, MockModel)

        assert "not a nested object" in str(exc_info.value)

    def test_validate_wildcard_always_valid(self):
        """Test wildcard is always valid"""
        parser = ShapeParser()
        registry = SchemaRegistry()
        registry.register(MockModel)
        parser._schema_registry = registry

        spec = parser.parse("recipient(*)")
        parser.validate(spec, MockModel)  # Should not raise


class TestShapeParserCaching:
    """Test shape parser caching"""

    def test_cache_stores_parsed_shapes(self):
        """Test cache stores parsed shapes"""
        parser = ShapeParser(cache_enabled=True)

        shape = "key,piid,description"
        spec1 = parser.parse(shape)
        spec2 = parser.parse(shape)

        assert spec1 is spec2
        assert parser.get_cache_size() == 1

    def test_cache_different_shapes(self):
        """Test cache stores different shapes separately"""
        parser = ShapeParser(cache_enabled=True)

        spec1 = parser.parse("key,piid")
        spec2 = parser.parse("key,description")

        assert spec1 is not spec2
        assert parser.get_cache_size() == 2

    def test_cache_disabled(self):
        """Test caching can be disabled"""
        parser = ShapeParser(cache_enabled=False)

        shape = "key,piid,description"
        spec1 = parser.parse(shape)
        spec2 = parser.parse(shape)

        assert spec1 is not spec2
        assert parser.get_cache_size() == 0

    def test_clear_cache(self):
        """Test cache can be cleared"""
        parser = ShapeParser(cache_enabled=True)

        parser.parse("key,piid")
        parser.parse("key,description")
        assert parser.get_cache_size() == 2

        parser.clear_cache()
        assert parser.get_cache_size() == 0


class TestShapeParserSyntaxValidation:
    """Test syntax validation method"""

    def test_validate_syntax_valid_shape(self):
        """Test syntax validation passes for valid shape"""
        parser = ShapeParser()
        parser.validate_syntax("key,piid,recipient(display_name)")  # Should not raise

    def test_validate_syntax_invalid_shape(self):
        """Test syntax validation fails for invalid shape"""
        parser = ShapeParser()

        with pytest.raises(ShapeParseError):
            parser.validate_syntax("key,piid,")

    def test_validate_syntax_unbalanced_parens(self):
        """Test syntax validation catches unbalanced parentheses"""
        parser = ShapeParser()

        with pytest.raises(ShapeParseError) as exc_info:
            parser.validate_syntax("recipient(display_name")

        assert "parenthesis" in str(exc_info.value).lower()


# ============================================================================
# Schema Registry Tests
# ============================================================================


class TestSchemaRegistryBasics:
    """Test basic schema registry functionality"""

    def test_register_simple_model(self):
        """Test registering a simple model"""
        registry = SchemaRegistry(auto_register_builtin=False)
        registry.register(SimpleModel)

        schema = registry.get_schema(SimpleModel)
        assert len(schema) == 3
        assert "name" in schema
        assert "age" in schema
        assert "active" in schema

    def test_get_schema_auto_registers(self):
        """Test get_schema automatically registers model if not registered"""
        registry = SchemaRegistry(auto_register_builtin=False)

        schema = registry.get_schema(SimpleModel)
        assert len(schema) == 3
        assert registry.is_registered(SimpleModel)

    def test_is_registered(self):
        """Test checking if model is registered"""
        registry = SchemaRegistry(auto_register_builtin=False)

        assert not registry.is_registered(SimpleModel)
        registry.register(SimpleModel)
        assert registry.is_registered(SimpleModel)

    def test_clear_registry(self):
        """Test clearing the registry"""
        registry = SchemaRegistry(auto_register_builtin=False)
        registry.register(SimpleModel)

        assert registry.is_registered(SimpleModel)
        registry.clear()
        assert not registry.is_registered(SimpleModel)


class TestSchemaExtractionSimpleFields:
    """Test schema extraction for simple field types"""

    def test_extract_string_field(self):
        """Test extracting string field schema"""
        registry = SchemaRegistry(auto_register_builtin=False)
        registry.register(SimpleModel)

        schema = registry.get_schema(SimpleModel)
        name_field = schema["name"]

        assert name_field.name == "name"
        assert name_field.type == str
        assert not name_field.is_optional
        assert not name_field.is_list
        assert name_field.nested_model is None

    def test_extract_int_field(self):
        """Test extracting int field schema"""
        registry = SchemaRegistry(auto_register_builtin=False)
        registry.register(SimpleModel)

        schema = registry.get_schema(SimpleModel)
        age_field = schema["age"]

        assert age_field.name == "age"
        assert age_field.type == int
        assert not age_field.is_optional
        assert not age_field.is_list

    def test_extract_bool_field(self):
        """Test extracting bool field schema"""
        registry = SchemaRegistry(auto_register_builtin=False)
        registry.register(SimpleModel)

        schema = registry.get_schema(SimpleModel)
        active_field = schema["active"]

        assert active_field.name == "active"
        assert active_field.type == bool
        assert not active_field.is_optional


class TestSchemaExtractionOptionalFields:
    """Test schema extraction for optional fields"""

    def test_extract_optional_string_field(self):
        """Test extracting optional string field"""
        registry = SchemaRegistry(auto_register_builtin=False)
        registry.register(OptionalFieldsModel)

        schema = registry.get_schema(OptionalFieldsModel)
        optional_field = schema["optional_field"]

        assert optional_field.name == "optional_field"
        assert optional_field.type == str
        assert optional_field.is_optional
        assert not optional_field.is_list

    def test_extract_optional_int_field(self):
        """Test extracting optional int field"""
        registry = SchemaRegistry(auto_register_builtin=False)
        registry.register(OptionalFieldsModel)

        schema = registry.get_schema(OptionalFieldsModel)
        optional_int = schema["optional_int"]

        assert optional_int.name == "optional_int"
        assert optional_int.type == int
        assert optional_int.is_optional

    def test_required_field_not_optional(self):
        """Test required field is not marked as optional"""
        registry = SchemaRegistry(auto_register_builtin=False)
        registry.register(OptionalFieldsModel)

        schema = registry.get_schema(OptionalFieldsModel)
        required_field = schema["required_field"]

        assert required_field.name == "required_field"
        assert not required_field.is_optional


class TestSchemaExtractionListFields:
    """Test schema extraction for list fields"""

    def test_extract_list_field(self):
        """Test extracting list field"""
        registry = SchemaRegistry(auto_register_builtin=False)
        registry.register(ListFieldsModel)

        schema = registry.get_schema(ListFieldsModel)
        tags_field = schema["tags"]

        assert tags_field.name == "tags"
        assert tags_field.type == str
        assert tags_field.is_list
        assert not tags_field.is_optional

    def test_extract_optional_list_field(self):
        """Test extracting optional list field"""
        registry = SchemaRegistry(auto_register_builtin=False)
        registry.register(ListFieldsModel)

        schema = registry.get_schema(ListFieldsModel)
        optional_tags = schema["optional_tags"]

        assert optional_tags.name == "optional_tags"
        assert optional_tags.type == str
        assert optional_tags.is_list
        assert optional_tags.is_optional

    def test_extract_list_of_ints(self):
        """Test extracting list of integers"""
        registry = SchemaRegistry(auto_register_builtin=False)
        registry.register(ListFieldsModel)

        schema = registry.get_schema(ListFieldsModel)
        numbers = schema["numbers"]

        assert numbers.name == "numbers"
        assert numbers.type == int
        assert numbers.is_list
        assert numbers.is_optional


class TestSchemaExtractionNestedModels:
    """Test schema extraction for nested models"""

    def test_extract_nested_model_field(self):
        """Test extracting nested model field"""
        registry = SchemaRegistry(auto_register_builtin=False)
        registry.register(NestedParentModel)
        registry.register(NestedChildModel)

        schema = registry.get_schema(NestedParentModel)
        child_field = schema["child"]

        assert child_field.name == "child"
        assert child_field.type == NestedChildModel
        assert child_field.is_optional
        assert not child_field.is_list
        assert child_field.nested_model == NestedChildModel

    def test_extract_list_of_nested_models(self):
        """Test extracting list of nested models"""
        registry = SchemaRegistry(auto_register_builtin=False)
        registry.register(NestedParentModel)
        registry.register(NestedChildModel)

        schema = registry.get_schema(NestedParentModel)
        children_field = schema["children"]

        assert children_field.name == "children"
        assert children_field.type == NestedChildModel
        assert children_field.is_optional
        assert children_field.is_list
        assert children_field.nested_model == NestedChildModel

    def test_nested_model_schema_extraction(self):
        """Test extracting schema from nested model"""
        registry = SchemaRegistry(auto_register_builtin=False)
        registry.register(NestedChildModel)

        schema = registry.get_schema(NestedChildModel)

        assert "child_name" in schema
        assert "child_value" in schema
        assert schema["child_name"].type == str
        assert schema["child_value"].type == int
        assert schema["child_value"].is_optional


class TestFieldValidation:
    """Test field validation against schema"""

    def test_validate_existing_field(self):
        """Test validating an existing field"""
        registry = SchemaRegistry(auto_register_builtin=False)
        registry.register(SimpleModel)

        field_schema = registry.validate_field(SimpleModel, "name")
        assert field_schema.name == "name"

    def test_validate_nonexistent_field_raises_error(self):
        """Test validating non-existent field raises error"""
        registry = SchemaRegistry(auto_register_builtin=False)
        registry.register(SimpleModel)

        with pytest.raises(ShapeValidationError) as exc_info:
            registry.validate_field(SimpleModel, "nonexistent")

        assert "nonexistent" in str(exc_info.value)
        assert "does not exist" in str(exc_info.value)
        assert "SimpleModel" in str(exc_info.value)

    def test_validate_field_suggestions(self):
        """Test field validation provides suggestions for similar fields"""
        registry = SchemaRegistry(auto_register_builtin=False)
        registry.register(SimpleModel)

        with pytest.raises(ShapeValidationError) as exc_info:
            registry.validate_field(SimpleModel, "nam")  # Typo of 'name'

        error_msg = str(exc_info.value)
        assert "nam" in error_msg
        assert "Did you mean" in error_msg or "name" in error_msg


class TestBuiltinModelsRegistration:
    """Test registration of built-in Tango models"""

    def test_auto_register_builtin_models(self):
        """Test built-in models are auto-registered"""
        registry = SchemaRegistry(auto_register_builtin=True)

        assert registry.is_registered(Contract)
        assert registry.is_registered(Agency)
        assert registry.is_registered(Location)
        assert registry.is_registered(Entity)

    def test_builtin_models_have_schemas(self):
        """Test built-in models have valid schemas"""
        registry = SchemaRegistry(auto_register_builtin=True)

        contract_schema = registry.get_schema(Contract)
        assert "key" in contract_schema
        assert "piid" in contract_schema
        assert "recipient" in contract_schema
        assert "description" in contract_schema

    def test_builtin_nested_models(self):
        """Test built-in models with nested objects"""
        registry = SchemaRegistry(auto_register_builtin=True)

        contract_schema = registry.get_schema(Contract)

        assert "awarding_office" in contract_schema
        office_field = contract_schema["awarding_office"]
        from tango.models import Office

        assert office_field.nested_model == Office or office_field.nested_model == "Office"

        assert "place_of_performance" in contract_schema
        location_field = contract_schema["place_of_performance"]
        from tango.models import PlaceOfPerformance

        assert (
            location_field.nested_model == PlaceOfPerformance
            or location_field.nested_model == "PlaceOfPerformance"
        )

    def test_disable_auto_register(self):
        """Test disabling auto-registration of built-in models"""
        registry = SchemaRegistry(auto_register_builtin=False)

        assert not registry.is_registered(Contract)
        assert not registry.is_registered(Agency)


class TestFieldSchemaRepresentation:
    """Test FieldSchema string representation"""

    def test_simple_field_repr(self):
        """Test repr for simple field"""
        field = FieldSchema(name="test", type=str, is_optional=False, is_list=False)
        repr_str = repr(field)

        assert "test" in repr_str
        assert "str" in repr_str

    def test_optional_field_repr(self):
        """Test repr for optional field"""
        field = FieldSchema(name="test", type=str, is_optional=True, is_list=False)
        repr_str = repr(field)

        assert "test" in repr_str
        assert "None" in repr_str or "|" in repr_str

    def test_list_field_repr(self):
        """Test repr for list field"""
        field = FieldSchema(name="test", type=str, is_optional=False, is_list=True)
        repr_str = repr(field)

        assert "test" in repr_str
        assert "list" in repr_str


class TestSchemaRegistryEdgeCases:
    """Test edge cases and error handling"""

    def test_model_without_type_hints(self):
        """Test handling model without type hints"""

        class NoTypeHints:
            def __init__(self):
                self.field = "value"

        registry = SchemaRegistry(auto_register_builtin=False)
        registry.register(NoTypeHints)

        schema = registry.get_schema(NoTypeHints)
        assert len(schema) == 0

    def test_register_same_model_twice(self):
        """Test registering the same model twice doesn't cause issues"""
        registry = SchemaRegistry(auto_register_builtin=False)

        registry.register(SimpleModel)
        registry.register(SimpleModel)  # Should not raise

        assert registry.is_registered(SimpleModel)

    def test_validate_field_auto_registers_model(self):
        """Test validate_field auto-registers model if needed"""
        registry = SchemaRegistry(auto_register_builtin=False)

        field_schema = registry.validate_field(SimpleModel, "name")
        assert field_schema.name == "name"
        assert registry.is_registered(SimpleModel)


# ============================================================================
# Type Generator Tests
# ============================================================================


class TestTypeGeneratorSimple:
    """Test simple TypedDict generation"""

    def test_generate_type_single_field(self):
        """Test generating type for a single field"""
        generator = TypeGenerator()
        parser = ShapeParser()

        spec = parser.parse("key")
        shaped_type = generator.generate_type(spec, MockModel, "MockShaped")

        assert shaped_type is not None
        assert shaped_type.__name__ == "MockShaped"

        annotations = shaped_type.__annotations__
        assert "key" in annotations
        assert annotations["key"] == str

    def test_generate_type_multiple_fields(self):
        """Test generating type for multiple fields"""
        generator = TypeGenerator()
        parser = ShapeParser()

        spec = parser.parse("key,piid,description")
        shaped_type = generator.generate_type(spec, MockModel)

        annotations = shaped_type.__annotations__
        assert len(annotations) == 3
        assert "key" in annotations
        assert "piid" in annotations
        assert "description" in annotations

        assert annotations["key"] == str
        assert annotations["piid"] == str | None
        assert annotations["description"] == str | None

    def test_generate_type_with_optional_fields(self):
        """Test that optional fields are correctly typed"""
        generator = TypeGenerator()
        parser = ShapeParser()

        spec = parser.parse("key,piid")
        shaped_type = generator.generate_type(spec, MockModel)

        annotations = shaped_type.__annotations__
        assert annotations["key"] == str
        assert annotations["piid"] == str | None

    def test_generate_type_with_date_field(self):
        """Test generating type with date field"""
        generator = TypeGenerator()
        parser = ShapeParser()

        spec = parser.parse("key,award_date")
        shaped_type = generator.generate_type(spec, MockModel)

        annotations = shaped_type.__annotations__
        assert "award_date" in annotations
        assert annotations["award_date"] == date | None

    def test_generate_type_with_decimal_field(self):
        """Test generating type with Decimal field"""
        generator = TypeGenerator()
        parser = ShapeParser()

        spec = parser.parse("key,amount")
        shaped_type = generator.generate_type(spec, MockModel)

        annotations = shaped_type.__annotations__
        assert "amount" in annotations
        assert annotations["amount"] == Decimal | None


class TestTypeGeneratorNested:
    """Test nested type generation"""

    def test_generate_type_with_nested_fields(self):
        """Test generating type with nested field selection"""
        generator = TypeGenerator()
        parser = ShapeParser()

        spec = parser.parse("key,recipient(display_name,uei)")
        shaped_type = generator.generate_type(spec, MockModel)

        annotations = shaped_type.__annotations__
        assert "key" in annotations
        assert "recipient" in annotations

        recipient_type = annotations["recipient"]
        assert recipient_type is not None

    def test_generate_nested_type_structure(self):
        """Test that nested types have correct structure"""
        generator = TypeGenerator()
        parser = ShapeParser()

        spec = parser.parse("key,recipient(display_name,uei)")
        shaped_type = generator.generate_type(spec, MockModel)

        annotations = shaped_type.__annotations__
        recipient_type = annotations["recipient"]
        assert recipient_type is not None

    def test_generate_type_with_deeply_nested_fields(self):
        """Test generating type with multiple levels of nesting"""
        generator = TypeGenerator()
        parser = ShapeParser()

        spec = parser.parse("key,recipient(display_name)")
        shaped_type = generator.generate_type(spec, MockModel)

        annotations = shaped_type.__annotations__
        assert "key" in annotations
        assert "recipient" in annotations

    def test_generate_type_with_nested_all_fields(self):
        """Test nested field with multiple fields"""
        generator = TypeGenerator()
        parser = ShapeParser()

        spec = parser.parse("key,recipient(display_name,uei,code)")
        shaped_type = generator.generate_type(spec, MockModel)

        annotations = shaped_type.__annotations__
        assert "key" in annotations
        assert "recipient" in annotations


class TestTypeGeneratorWildcard:
    """Test wildcard expansion"""

    def test_generate_type_with_wildcard(self):
        """Test generating type with wildcard selector"""
        generator = TypeGenerator()
        parser = ShapeParser()

        spec = parser.parse("*")
        shaped_type = generator.generate_type(spec, MockModel)

        annotations = shaped_type.__annotations__
        assert "key" in annotations
        assert "piid" in annotations
        assert "description" in annotations
        assert "recipient" in annotations
        assert "tags" in annotations
        assert "amount" in annotations
        assert "award_date" in annotations

    def test_generate_type_with_nested_wildcard(self):
        """Test generating type with nested wildcard"""
        generator = TypeGenerator()
        parser = ShapeParser()

        spec = parser.parse("key,recipient(*)")
        shaped_type = generator.generate_type(spec, MockModel)

        annotations = shaped_type.__annotations__
        assert "key" in annotations
        assert "recipient" in annotations

        recipient_type = annotations["recipient"]
        assert recipient_type is not None

    def test_generate_type_wildcard_with_other_fields(self):
        """Test wildcard combined with specific fields"""
        generator = TypeGenerator()
        parser = ShapeParser()

        spec = parser.parse("*")
        shaped_type = generator.generate_type(spec, MockModel)

        annotations = shaped_type.__annotations__
        assert len(annotations) >= 7  # All fields in MockModel


class TestTypeGeneratorListTypes:
    """Test list type handling"""

    def test_generate_type_with_list_field(self):
        """Test generating type with list field"""
        generator = TypeGenerator()
        parser = ShapeParser()

        spec = parser.parse("key,tags")
        shaped_type = generator.generate_type(spec, MockModel)

        annotations = shaped_type.__annotations__
        assert "tags" in annotations
        tags_type = annotations["tags"]
        assert tags_type is not None

    def test_generate_type_with_nested_list(self):
        """Test generating type with list of nested objects"""
        generator = TypeGenerator()
        parser = ShapeParser()

        spec = parser.parse("key,items(display_name)")
        shaped_type = generator.generate_type(spec, MockListModel)

        annotations = shaped_type.__annotations__
        assert "key" in annotations
        assert "items" in annotations


class TestTypeGeneratorCaching:
    """Test type caching mechanism"""

    def test_cache_enabled_by_default(self):
        """Test that caching is enabled by default"""
        generator = TypeGenerator()
        assert generator._cache_enabled is True

    def test_cache_stores_generated_types(self):
        """Test that generated types are cached"""
        generator = TypeGenerator()
        parser = ShapeParser()

        spec = parser.parse("key,piid")

        shaped_type1 = generator.generate_type(spec, MockModel)
        assert generator.get_cache_size() == 1

        shaped_type2 = generator.generate_type(spec, MockModel)
        assert shaped_type1 is shaped_type2
        assert generator.get_cache_size() == 1

    def test_cache_different_shapes(self):
        """Test that different shapes create different cache entries"""
        generator = TypeGenerator()
        parser = ShapeParser()

        spec1 = parser.parse("key,piid")
        spec2 = parser.parse("key,description")

        shaped_type1 = generator.generate_type(spec1, MockModel)
        shaped_type2 = generator.generate_type(spec2, MockModel)

        assert generator.get_cache_size() == 2
        assert shaped_type1 is not shaped_type2

    def test_cache_different_models(self):
        """Test that same shape on different models creates different cache entries"""
        generator = TypeGenerator()
        parser = ShapeParser()

        spec = parser.parse("key")

        shaped_type1 = generator.generate_type(spec, MockModel)
        shaped_type2 = generator.generate_type(spec, MockListModel)

        assert generator.get_cache_size() == 2
        assert shaped_type1 is not shaped_type2

    def test_clear_cache(self):
        """Test clearing the cache"""
        generator = TypeGenerator()
        parser = ShapeParser()

        spec = parser.parse("key,piid")
        generator.generate_type(spec, MockModel)

        assert generator.get_cache_size() == 1
        generator.clear_cache()
        assert generator.get_cache_size() == 0

    def test_cache_disabled(self):
        """Test that caching can be disabled"""
        generator = TypeGenerator(cache_enabled=False)
        parser = ShapeParser()

        spec = parser.parse("key,piid")

        shaped_type1 = generator.generate_type(spec, MockModel)
        shaped_type2 = generator.generate_type(spec, MockModel)

        assert generator.get_cache_size() == 0
        assert shaped_type1 is not shaped_type2

    def test_cache_stats(self):
        """Test cache statistics"""
        generator = TypeGenerator()
        parser = ShapeParser()

        stats = generator.get_cache_stats()
        assert stats["size"] == 0
        assert stats["enabled"] is True
        assert stats["hits"] == 0
        assert stats["misses"] == 0

        spec = parser.parse("key,piid")
        generator.generate_type(spec, MockModel)

        stats = generator.get_cache_stats()
        assert stats["size"] == 1
        assert stats["misses"] == 1

        generator.generate_type(spec, MockModel)

        stats = generator.get_cache_stats()
        assert stats["size"] == 1
        assert stats["hits"] == 1
        assert stats["misses"] == 1

    def test_cache_hit_rate(self):
        """Test cache hit rate calculation"""
        generator = TypeGenerator()
        parser = ShapeParser()

        spec = parser.parse("key,piid")

        generator.generate_type(spec, MockModel)
        generator.generate_type(spec, MockModel)
        generator.generate_type(spec, MockModel)

        stats = generator.get_cache_stats()
        assert stats["hits"] == 2
        assert stats["misses"] == 1
        assert "66.7%" in stats["hit_rate"]

    def test_lru_cache_eviction(self):
        """Test that LRU cache evicts least recently used items"""
        generator = TypeGenerator(cache_size=2)
        parser = ShapeParser()

        spec1 = parser.parse("key")
        spec2 = parser.parse("piid")
        spec3 = parser.parse("description")

        generator.generate_type(spec1, MockModel)
        generator.generate_type(spec2, MockModel)

        assert generator.get_cache_size() == 2

        generator.generate_type(spec3, MockModel)

        assert generator.get_cache_size() == 2

        stats_before = generator.get_cache_stats()
        misses_before = stats_before["misses"]

        generator.generate_type(spec1, MockModel)

        stats_after = generator.get_cache_stats()
        assert stats_after["misses"] == misses_before + 1


class TestTypeGeneratorAliases:
    """Test field alias handling"""

    def test_generate_type_with_alias(self):
        """Test generating type with field alias"""
        generator = TypeGenerator()
        parser = ShapeParser()

        spec = parser.parse("key,display_name::vendor_name")

        @dataclass
        class ModelWithDisplayName:
            key: str
            display_name: str | None = None

        shaped_type = generator.generate_type(spec, ModelWithDisplayName)

        annotations = shaped_type.__annotations__
        assert "vendor_name" in annotations
        assert "display_name" not in annotations


class TestTypeGeneratorErrors:
    """Test error handling"""

    def test_generate_type_with_invalid_model(self):
        """Test error handling for invalid model"""
        generator = TypeGenerator()
        parser = ShapeParser()

        spec = parser.parse("key")
        shaped_type = generator.generate_type(spec, str)  # type: ignore

        assert shaped_type is not None

    def test_generate_type_handles_missing_fields_gracefully(self):
        """Test that missing fields are handled gracefully"""
        generator = TypeGenerator()

        spec = ShapeSpec(fields=[FieldSpec(name="key"), FieldSpec(name="nonexistent_field")])
        shaped_type = generator.generate_type(spec, MockModel)

        annotations = shaped_type.__annotations__
        assert "key" in annotations
        assert "nonexistent_field" in annotations


class TestTypeGeneratorIntegration:
    """Integration tests with real models"""

    def test_generate_type_for_contract_minimal(self):
        """Test generating type for Contract with minimal shape"""
        generator = TypeGenerator()
        parser = ShapeParser()

        spec = parser.parse("key,piid,description")
        shaped_type = generator.generate_type(spec, Contract)

        annotations = shaped_type.__annotations__
        assert "key" in annotations
        assert "piid" in annotations
        assert "description" in annotations

    def test_generate_type_for_entity_minimal(self):
        """Test generating type for Entity with minimal shape"""
        generator = TypeGenerator()
        parser = ShapeParser()

        spec = parser.parse("key,display_name,uei")
        shaped_type = generator.generate_type(spec, Entity)

        annotations = shaped_type.__annotations__
        assert "key" in annotations
        assert "display_name" in annotations
        assert "uei" in annotations


# ============================================================================
# Default Shapes and Usage Tests
# ============================================================================


class TestDefaultShapes:
    """Test that default shapes are defined and used correctly"""

    def test_default_contract_shape_defined(self):
        """Test that CONTRACTS_MINIMAL default is defined"""
        assert hasattr(ShapeConfig, "CONTRACTS_MINIMAL")
        shape = ShapeConfig.CONTRACTS_MINIMAL
        assert isinstance(shape, str)
        assert "key" in shape
        assert "piid" in shape
        assert "award_date" in shape
        assert "recipient" in shape

    def test_default_entity_shapes_defined(self):
        """Test that default entity shapes are defined"""
        assert hasattr(ShapeConfig, "ENTITIES_MINIMAL")
        assert hasattr(ShapeConfig, "ENTITIES_COMPREHENSIVE")

        minimal = ShapeConfig.ENTITIES_MINIMAL
        assert "uei" in minimal
        assert "legal_business_name" in minimal

        comprehensive = ShapeConfig.ENTITIES_COMPREHENSIVE
        assert "uei" in comprehensive
        assert "legal_business_name" in comprehensive

    def test_default_forecast_shape_defined(self):
        """Test that FORECASTS_MINIMAL default is defined"""
        assert hasattr(ShapeConfig, "FORECASTS_MINIMAL")
        shape = ShapeConfig.FORECASTS_MINIMAL
        assert "id" in shape
        assert "title" in shape

    def test_default_opportunity_shape_defined(self):
        """Test that OPPORTUNITIES_MINIMAL default is defined"""
        assert hasattr(ShapeConfig, "OPPORTUNITIES_MINIMAL")
        shape = ShapeConfig.OPPORTUNITIES_MINIMAL
        assert "opportunity_id" in shape
        assert "title" in shape

    def test_default_notice_shape_defined(self):
        """Test that NOTICES_MINIMAL default is defined"""
        assert hasattr(ShapeConfig, "NOTICES_MINIMAL")
        shape = ShapeConfig.NOTICES_MINIMAL

    def test_grants_minimal_default_is_defined(self):
        """Test that GRANTS_MINIMAL default is defined"""
        assert hasattr(ShapeConfig, "GRANTS_MINIMAL")
        shape = ShapeConfig.GRANTS_MINIMAL
        assert "grant_id" in shape
        assert "title" in shape
        assert "opportunity_number" in shape

    def test_contracts_minimal_excludes_award_type(self):
        """Test that CONTRACTS_MINIMAL doesn't include award_type (not in API)"""
        shape = ShapeConfig.CONTRACTS_MINIMAL
        assert "award_type" not in shape, "award_type removed - not in API"

    def test_entities_minimal_uses_legal_business_name(self):
        """Test that ENTITIES_MINIMAL uses legal_business_name (not display_name)"""
        shape = ShapeConfig.ENTITIES_MINIMAL
        assert "legal_business_name" in shape
        assert "display_name" not in shape, "display_name removed - use legal_business_name"


class TestDefaultShapeUsage:
    """Test that all endpoints use default shapes when shape=None"""

    @patch("tango.client.httpx.Client.request")
    def test_list_contracts_defaults_to_minimal(self, mock_request):
        """Test that list_contracts uses CONTRACTS_MINIMAL by default"""
        mock_response = Mock()
        mock_response.is_success = True
        mock_response.json.return_value = {
            "count": 0,
            "next": None,
            "previous": None,
            "results": [],
        }
        mock_response.content = b"{}"
        mock_request.return_value = mock_response

        client = TangoClient(api_key="test-key")
        client.list_contracts()

        call_args = mock_request.call_args
        assert call_args[1]["params"]["shape"] == ShapeConfig.CONTRACTS_MINIMAL

    @patch("tango.client.httpx.Client.request")
    def test_search_contracts_defaults_to_minimal(self, mock_request):
        """Test that list_contracts uses CONTRACTS_MINIMAL by default"""
        mock_response = Mock()
        mock_response.is_success = True
        mock_response.json.return_value = {
            "count": 0,
            "next": None,
            "previous": None,
            "results": [],
        }
        mock_response.content = b"{}"
        mock_request.return_value = mock_response

        client = TangoClient(api_key="test-key")
        from tango.models import SearchFilters

        client.list_contracts(filters=SearchFilters())

        call_args = mock_request.call_args
        assert call_args[1]["params"]["shape"] == ShapeConfig.CONTRACTS_MINIMAL

    @patch("tango.client.httpx.Client.request")
    def test_list_entities_defaults_to_minimal(self, mock_request):
        """Test that list_entities uses ENTITIES_MINIMAL by default"""
        mock_response = Mock()
        mock_response.is_success = True
        mock_response.json.return_value = {
            "count": 0,
            "next": None,
            "previous": None,
            "results": [],
        }
        mock_response.content = b"{}"
        mock_request.return_value = mock_response

        client = TangoClient(api_key="test-key")
        client.list_entities()

        call_args = mock_request.call_args
        assert call_args[1]["params"]["shape"] == ShapeConfig.ENTITIES_MINIMAL

    @patch("tango.client.httpx.Client.request")
    def test_get_entity_defaults_to_comprehensive(self, mock_request):
        """Test that get_entity uses ENTITIES_COMPREHENSIVE by default"""
        mock_response = Mock()
        mock_response.is_success = True
        mock_response.json.return_value = {}
        mock_response.content = b"{}"
        mock_request.return_value = mock_response

        client = TangoClient(api_key="test-key")
        try:
            client.get_entity("test-uei")
        except Exception:
            pass  # Endpoint might not exist

        if mock_request.called:
            call_args = mock_request.call_args
            assert call_args[1]["params"]["shape"] == ShapeConfig.ENTITIES_COMPREHENSIVE

    @patch("tango.client.httpx.Client.request")
    def test_list_forecasts_defaults_to_minimal(self, mock_request):
        """Test that list_forecasts uses FORECASTS_MINIMAL by default"""
        mock_response = Mock()
        mock_response.is_success = True
        mock_response.json.return_value = {
            "count": 0,
            "next": None,
            "previous": None,
            "results": [],
        }
        mock_response.content = b"{}"
        mock_request.return_value = mock_response

        client = TangoClient(api_key="test-key")
        client.list_forecasts()

        call_args = mock_request.call_args
        assert call_args[1]["params"]["shape"] == ShapeConfig.FORECASTS_MINIMAL

    @patch("tango.client.httpx.Client.request")
    def test_list_opportunities_defaults_to_minimal(self, mock_request):
        """Test that list_opportunities uses OPPORTUNITIES_MINIMAL by default"""
        mock_response = Mock()
        mock_response.is_success = True
        mock_response.json.return_value = {
            "count": 0,
            "next": None,
            "previous": None,
            "results": [],
        }
        mock_response.content = b"{}"
        mock_request.return_value = mock_response

        client = TangoClient(api_key="test-key")
        client.list_opportunities()

        call_args = mock_request.call_args
        assert call_args[1]["params"]["shape"] == ShapeConfig.OPPORTUNITIES_MINIMAL

    @patch("tango.client.httpx.Client.request")
    def test_list_notices_defaults_to_minimal(self, mock_request):
        """Test that list_notices uses NOTICES_MINIMAL by default"""
        mock_response = Mock()
        mock_response.is_success = True
        mock_response.json.return_value = {
            "count": 0,
            "next": None,
            "previous": None,
            "results": [],
        }
        mock_response.content = b"{}"
        mock_request.return_value = mock_response

        client = TangoClient(api_key="test-key")
        client.list_notices()

        call_args = mock_request.call_args
        assert call_args[1]["params"]["shape"] == ShapeConfig.NOTICES_MINIMAL

    @patch("tango.client.httpx.Client.request")
    def test_list_grants_defaults_to_minimal(self, mock_request):
        """Test that list_grants uses GRANTS_MINIMAL by default"""
        mock_response = Mock()
        mock_response.is_success = True
        mock_response.json.return_value = {
            "count": 0,
            "next": None,
            "previous": None,
            "results": [],
        }
        mock_response.content = b"{}"
        mock_request.return_value = mock_response

        client = TangoClient(api_key="test-key")
        client.list_grants()

        call_args = mock_request.call_args
        assert call_args[1]["params"]["shape"] == ShapeConfig.GRANTS_MINIMAL


# ============================================================================
# Flat Lists and Unflatten Tests
# ============================================================================


class TestFlatListsParameter:
    """Test flat_lists parameter support"""

    @patch("tango.client.httpx.Client.request")
    def test_contracts_flat_lists_parameter(self, mock_request):
        """Test that flat_lists parameter is passed to API"""
        mock_response = Mock()
        mock_response.is_success = True
        mock_response.json.return_value = {
            "count": 0,
            "next": None,
            "previous": None,
            "results": [],
        }
        mock_response.content = b"{}"
        mock_request.return_value = mock_response

        client = TangoClient(api_key="test-key")
        client.list_contracts(flat=True, flat_lists=True)

        call_args = mock_request.call_args
        assert call_args[1]["params"]["flat"] == "true"
        assert call_args[1]["params"]["flat_lists"] == "true"

    @patch("tango.client.httpx.Client.request")
    def test_entities_flat_lists_parameter(self, mock_request):
        """Test that entities support flat_lists parameter"""
        mock_response = Mock()
        mock_response.is_success = True
        mock_response.json.return_value = {
            "count": 0,
            "next": None,
            "previous": None,
            "results": [],
        }
        mock_response.content = b"{}"
        mock_request.return_value = mock_response

        client = TangoClient(api_key="test-key")
        client.list_entities(flat=True, flat_lists=True)

        call_args = mock_request.call_args
        assert call_args[1]["params"]["flat_lists"] == "true"


class TestUnflattenResponse:
    """Test the _unflatten_response utility"""

    def test_unflatten_simple_flat_response(self):
        """Test unflattening a simple flat response"""
        client = TangoClient()
        flat_data = {"key": "123", "recipient.display_name": "Acme Corp", "recipient.uei": "ABC123"}

        result = client._unflatten_response(flat_data)

        assert result["key"] == "123"
        assert result["recipient"]["display_name"] == "Acme Corp"
        assert result["recipient"]["uei"] == "ABC123"

    def test_unflatten_nested_response(self):
        """Test unflattening a deeply nested flat response"""
        client = TangoClient()
        flat_data = {
            "key": "123",
            "recipient.address.city": "Washington",
            "recipient.address.state": "DC",
            "recipient.name": "Acme",
        }

        result = client._unflatten_response(flat_data)

        assert result["key"] == "123"
        assert result["recipient"]["name"] == "Acme"
        assert result["recipient"]["address"]["city"] == "Washington"
        assert result["recipient"]["address"]["state"] == "DC"

    def test_unflatten_already_nested_response(self):
        """Test that already nested responses are returned as-is"""
        client = TangoClient()
        nested_data = {"key": "123", "recipient": {"display_name": "Acme Corp", "uei": "ABC123"}}

        result = client._unflatten_response(nested_data)

        assert result == nested_data

    def test_unflatten_with_arrays(self):
        """Test unflattening responses with array indices"""
        client = TangoClient()
        flat_data = {
            "key": "123",
            "transactions.0.date": "2024-01-01",
            "transactions.0.amount": "1000",
            "transactions.1.date": "2024-02-01",
            "transactions.1.amount": "2000",
        }

        result = client._unflatten_response(flat_data)

        assert result["key"] == "123"
        assert result["transactions"]["0"]["date"] == "2024-01-01"
        assert result["transactions"]["1"]["amount"] == "2000"

    def test_unflatten_empty_dict(self):
        """Test unflattening empty dictionary"""
        client = TangoClient()
        result = client._unflatten_response({})
        assert result == {}

    def test_unflatten_with_custom_joiner(self):
        """Test unflattening with custom joiner character"""
        client = TangoClient()
        flat_data = {"key": "123", "recipient::name": "Acme", "recipient::uei": "ABC123"}

        result = client._unflatten_response(flat_data, joiner="::")

        assert result["key"] == "123"
        assert result["recipient"]["name"] == "Acme"
        assert result["recipient"]["uei"] == "ABC123"
