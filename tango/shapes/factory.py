"""Model factory for creating typed instances from API responses

This module provides the ModelFactory class which creates instances of dynamically
generated types from API response data. It handles field parsing, nested object
creation, and validation.

Examples:
    >>> from tango.models import Contract
    >>> from tango.shapes import ShapeParser, TypeGenerator, ModelFactory
    >>>
    >>> parser = ShapeParser()
    >>> generator = TypeGenerator()
    >>> factory = ModelFactory(generator, parser_registry)
    >>>
    >>> shape_spec = parser.parse("key,piid,recipient(display_name)")
    >>> dynamic_type = generator.generate_type(shape_spec, Contract)
    >>>
    >>> response_data = {"key": "123", "piid": "ABC", "recipient": {"display_name": "Acme Corp"}}
    >>> instance = factory.create_instance(response_data, shape_spec, Contract, dynamic_type)
"""

import logging
from collections.abc import Callable
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from tango.exceptions import ModelInstantiationError
from tango.shapes.generator import TypeGenerator
from tango.shapes.models import FieldSpec, ShapeSpec
from tango.shapes.schema import SchemaRegistry

logger = logging.getLogger(__name__)


class ShapedModel(dict):
    """Wrapper class for shaped model instances with enhanced repr

    This class wraps dictionary instances returned from dynamic model generation
    to provide a better __repr__ that shows the type name and fields.

    Attributes:
        _type_name: Name of the dynamically generated type
        _shape_spec: Shape specification used to create this instance
    """

    def __init__(self, data: dict[str, Any], type_name: str, shape_spec: ShapeSpec | None = None):
        """Initialize a shaped model instance

        Args:
            data: Dictionary data for the instance
            type_name: Name of the dynamically generated type
            shape_spec: Optional shape specification
        """
        super().__init__(data)
        self._type_name = type_name
        self._shape_spec = shape_spec

    def __getattr__(self, name: str) -> Any:
        """Get attribute with helpful error messages for missing fields

        Args:
            name: Attribute name

        Returns:
            Attribute value

        Raises:
            AttributeError: If attribute doesn't exist, with helpful suggestions
        """
        # Avoid recursion for internal attributes
        if name.startswith("_"):
            raise AttributeError(f"'{self._type_name}' object has no attribute '{name}'")

        # Try to get from dictionary
        try:
            return self[name]
        except KeyError:
            # Generate helpful error message
            available_fields = list(self.keys())
            error_msg = f"Field '{name}' not found in {self._type_name}."

            # Suggest similar field names
            suggestions = self._find_similar_fields(name, available_fields)
            if suggestions:
                error_msg += f" Did you mean: {', '.join(repr(s) for s in suggestions)}?"

            # Show available fields
            if available_fields:
                if len(available_fields) <= 10:
                    error_msg += (
                        f" Available fields: {', '.join(repr(f) for f in available_fields)}"
                    )
                else:
                    shown = available_fields[:10]
                    error_msg += f" Available fields: {', '.join(repr(f) for f in shown)}, ... ({len(available_fields) - 10} more)"

            # Provide hint about shape
            error_msg += "\n\nThis field may not be included in your shape specification."
            error_msg += "\nTo include this field, add it to your shape parameter."

            raise AttributeError(error_msg) from None

    def _find_similar_fields(
        self, target: str, available: list[str], max_suggestions: int = 3
    ) -> list[str]:
        """Find similar field names using simple string similarity

        Args:
            target: Target field name
            available: List of available field names
            max_suggestions: Maximum number of suggestions to return

        Returns:
            List of similar field names
        """
        if not available:
            return []

        # Calculate similarity scores using Levenshtein-like distance
        scores = []
        for field in available:
            # Simple similarity: count matching characters in order
            score = self._similarity_score(target.lower(), field.lower())
            scores.append((score, field))

        # Sort by score (higher is better) and return top matches
        scores.sort(reverse=True, key=lambda x: x[0])

        # Only return suggestions with reasonable similarity
        suggestions = [field for score, field in scores[:max_suggestions] if score > 0.3]
        return suggestions

    def _similarity_score(self, s1: str, s2: str) -> float:
        """Calculate simple similarity score between two strings

        Args:
            s1: First string
            s2: Second string

        Returns:
            Similarity score between 0 and 1
        """
        if not s1 or not s2:
            return 0.0

        # Check for substring match
        if s1 in s2 or s2 in s1:
            return 0.8

        # Check for common prefix
        common_prefix = 0
        for c1, c2 in zip(s1, s2, strict=False):
            if c1 == c2:
                common_prefix += 1
            else:
                break

        if common_prefix > 0:
            return common_prefix / max(len(s1), len(s2))

        # Count common characters
        common_chars = sum(1 for c in s1 if c in s2)
        return common_chars / max(len(s1), len(s2))

    def __repr__(self) -> str:
        """Return a readable representation of the shaped model

        Returns:
            String representation showing type name and fields
        """
        # Limit the number of fields shown in repr
        max_fields = 5
        fields = list(self.keys())

        if len(fields) <= max_fields:
            fields_str = ", ".join(f"{k}={repr(self[k])}" for k in fields)
        else:
            shown_fields = fields[:max_fields]
            fields_str = ", ".join(f"{k}={repr(self[k])}" for k in shown_fields)
            fields_str += f", ... ({len(fields) - max_fields} more fields)"

        return f"{self._type_name}({fields_str})"

    def __str__(self) -> str:
        """Return a string representation of the shaped model

        Returns:
            String representation showing all fields
        """
        fields_str = ", ".join(f"{k}={repr(self[k])}" for k in self.keys())
        return f"{self._type_name}({fields_str})"

    def get_type_name(self) -> str:
        """Get the type name of this shaped model

        Returns:
            Type name string
        """
        return self._type_name

    def get_shape_spec(self) -> ShapeSpec | None:
        """Get the shape specification used to create this instance

        Returns:
            ShapeSpec object or None if not available
        """
        return self._shape_spec


def build_parser_registry_from_client(client: Any) -> dict[str, Callable]:
    """Build a parser registry from TangoClient parser methods

    This function creates a dictionary mapping field type names to parser functions
    from a TangoClient instance. It registers all the standard parsers like
    _parse_date, _parse_decimal, _parse_location, etc.

    Args:
        client: TangoClient instance with parser methods

    Returns:
        Dictionary mapping type names to parser functions

    Examples:
        >>> from tango import TangoClient
        >>> client = TangoClient(api_key="test")
        >>> parsers = build_parser_registry_from_client(client)
        >>> parsers['date']
        <bound method TangoClient._parse_date of ...>
    """
    registry: dict[str, Callable] = {}

    # Register basic type parsers that still exist on the client
    if hasattr(client, "_parse_date"):
        registry["date"] = client._parse_date

    if hasattr(client, "_parse_datetime"):
        registry["datetime"] = client._parse_datetime

    if hasattr(client, "_parse_decimal"):
        registry["Decimal"] = client._parse_decimal

    return registry


def create_default_parser_registry() -> dict[str, Callable]:
    """Create a default parser registry without requiring a client instance

    This function creates a parser registry with standalone parser functions
    that don't depend on a TangoClient instance. Useful for testing or when
    you want to use the ModelFactory independently.

    Returns:
        Dictionary mapping type names to parser functions

    Examples:
        >>> parsers = create_default_parser_registry()
        >>> parsers['date']('2024-01-15')
        datetime.date(2024, 1, 15)
    """
    from tango.models import (
        Agency,
        Department,
        Location,
        NAICSCode,
        PSCCode,
        RecipientProfile,
    )

    def parse_date(date_string: str | None) -> date | None:
        """Parse date string to date object"""
        if not date_string:
            return None
        try:
            if "T" in date_string:
                return datetime.fromisoformat(date_string.replace("Z", "+00:00")).date()
            else:
                return datetime.strptime(date_string, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            return None

    def parse_datetime(datetime_string: str | None) -> datetime | None:
        """Parse datetime string to datetime object"""
        if not datetime_string:
            return None
        try:
            return datetime.fromisoformat(datetime_string.replace("Z", "+00:00"))
        except (ValueError, TypeError):
            return None

    def parse_decimal(value: Any) -> Decimal | None:
        """Parse numeric value to Decimal"""
        if value is None:
            return None
        try:
            return Decimal(str(value))
        except (ValueError, TypeError, Exception):
            return None

    def parse_location(location_data: dict[str, Any] | None) -> Location | None:
        """Parse location data"""
        if not location_data:
            return None
        return Location(
            address_line1=location_data.get("address_line1"),
            address_line2=location_data.get("address_line2"),
            city=location_data.get("city"),
            state=location_data.get("state"),
            state_code=location_data.get("state_code"),
            zip_code=location_data.get("zip_code") or location_data.get("zip"),
            zip4=location_data.get("zip4"),
            country=location_data.get("country"),
            country_code=location_data.get("country_code"),
            county=location_data.get("county"),
            congressional_district=location_data.get("congressional_district"),
            latitude=location_data.get("latitude"),
            longitude=location_data.get("longitude"),
        )

    def parse_agency(agency_data: dict[str, Any] | None) -> Agency | None:
        """Parse agency data"""
        if not agency_data:
            return None

        department = None
        if agency_data.get("department"):
            dept_data = agency_data["department"]
            department = Department(name=dept_data.get("name", ""), code=dept_data.get("code"))

        code = agency_data.get("code") or agency_data.get("office_code", "")
        name = agency_data.get("name") or agency_data.get("office_name", "")

        return Agency(
            code=code,
            name=name,
            abbreviation=agency_data.get("abbreviation"),
            department=department,
        )

    def parse_recipient_profile(recipient_data: dict[str, Any] | None) -> RecipientProfile | None:
        """Parse recipient profile data"""
        if not recipient_data:
            return None

        return RecipientProfile(
            uei=recipient_data.get("uei"),
            cage_code=recipient_data.get("cage_code"),
            parent_uei=recipient_data.get("parent_uei"),
            parent_name=recipient_data.get("parent_name"),
            business_types=recipient_data.get("business_types"),
            location=parse_location(recipient_data.get("location")),
        )

    def parse_naics_code(value: Any) -> Any:
        """Parse NAICS code"""
        if value is None:
            return None
        if isinstance(value, dict):
            return NAICSCode(
                code=value.get("code", ""),
                description=value.get("description"),
                year=value.get("year"),
            )
        elif isinstance(value, str):
            return NAICSCode(code=value)
        return value

    def parse_psc_code(value: Any) -> Any:
        """Parse PSC code"""
        if value is None:
            return None
        if isinstance(value, dict):
            return PSCCode(code=value.get("code", ""), description=value.get("description"))
        elif isinstance(value, str):
            return PSCCode(code=value)
        return value

    return {
        "date": parse_date,
        "datetime": parse_datetime,
        "Decimal": parse_decimal,
        "Location": parse_location,
        "Agency": parse_agency,
        "RecipientProfile": parse_recipient_profile,
        "NAICSCode": parse_naics_code,
        "PSCCode": parse_psc_code,
    }


class ModelFactory:
    """Factory for creating typed model instances from API response data

    This class takes API response data (dictionaries) and creates instances of
    dynamically generated types. It handles:
    - Field parsing using registered parser functions
    - Nested object creation
    - Missing field handling (sets to None)
    - Type validation and error reporting

    Attributes:
        type_generator: TypeGenerator instance for creating nested types
        parsers: Dictionary mapping field types to parser functions
        schema_registry: SchemaRegistry for field type information

    Examples:
        >>> factory = ModelFactory(type_generator, parsers)
        >>> instance = factory.create_instance(data, shape_spec, Contract, ContractShaped)
    """

    def __init__(
        self,
        type_generator: TypeGenerator,
        parsers: dict[str, Callable],
        schema_registry: SchemaRegistry | None = None,
    ):
        """Initialize the model factory

        Args:
            type_generator: TypeGenerator instance for creating nested types
            parsers: Dictionary mapping field type names to parser functions
            schema_registry: Optional schema registry for field type information
        """
        self.type_generator = type_generator
        self.parsers = parsers
        self.schema_registry = schema_registry or SchemaRegistry()

    def create_instance(
        self, data: dict[str, Any], shape_spec: ShapeSpec, base_model: type, dynamic_type: type
    ) -> Any:
        """Create a typed instance from response data

        This method takes raw API response data and creates an instance of the
        dynamically generated type. It handles field parsing, nested objects,
        and missing fields.

        Args:
            data: Raw API response data (dictionary)
            shape_spec: Shape specification describing the structure
            base_model: Base static model class (e.g., Contract, Agency)
            dynamic_type: Generated dynamic type to instantiate

        Returns:
            Instance of dynamic_type with parsed data

        Raises:
            ModelInstantiationError: If instance creation fails

        Examples:
            >>> data = {"key": "123", "piid": "ABC", "recipient": {"display_name": "Acme"}}
            >>> instance = factory.create_instance(data, shape_spec, Contract, ContractShaped)
            >>> instance["key"]
            '123'
        """
        if not isinstance(data, dict):
            raise ModelInstantiationError(f"Expected dictionary data, got {type(data).__name__}")

        # Ensure model is registered
        if not self.schema_registry.is_registered(base_model):
            self.schema_registry.register(base_model)

        # Get model schema
        model_schema = self.schema_registry.get_schema(base_model)

        # Build result dictionary
        result: dict[str, Any] = {}

        try:
            for field_spec in shape_spec.fields:
                # Determine the field name in the result (use alias if provided)
                result_field_name = field_spec.alias or field_spec.name

                # Handle wildcard - include all fields from data
                if field_spec.is_wildcard:
                    # Add all fields from data that exist in the model schema
                    for data_key, data_value in data.items():
                        if data_key in model_schema:
                            field_schema = model_schema[data_key]
                            parsed_value = self._parse_field(
                                data_key, data_value, field_schema.type, field_schema
                            )
                            result[data_key] = parsed_value
                    continue

                # Get the value from data (use original field name, not alias)
                value = data.get(field_spec.name)

                # Handle missing fields - set to None
                if value is None:
                    result[result_field_name] = None
                    continue

                # Get field schema
                if field_spec.name not in model_schema:
                    # Field doesn't exist in schema - this should have been caught by validation
                    # but we'll handle it gracefully
                    logger.warning(
                        f"Field '{field_spec.name}' not found in {base_model.__name__} schema, "
                        f"using raw value"
                    )
                    result[result_field_name] = value
                    continue

                field_schema = model_schema[field_spec.name]

                # Handle nested fields
                if field_spec.nested_fields:
                    if not field_schema.nested_model:
                        raise ModelInstantiationError(
                            f"Field '{field_spec.name}' is not a nested model but has nested field selections",
                            field_name=field_spec.name,
                        )

                    # Handle list of nested objects
                    if field_schema.is_list:
                        if not isinstance(value, list):
                            logger.warning(
                                f"Expected list for field '{field_spec.name}', got {type(value).__name__}, "
                                f"wrapping in list"
                            )
                            value = [value] if value is not None else []

                        # Create nested instances for each item
                        nested_instances = []
                        for item in value:
                            if isinstance(item, dict):
                                nested_instance = self._create_nested_instance(
                                    item, field_spec, field_schema.nested_model
                                )
                                nested_instances.append(nested_instance)
                            else:
                                nested_instances.append(item)

                        result[result_field_name] = nested_instances
                    else:
                        # Single nested object
                        if isinstance(value, dict):
                            nested_instance = self._create_nested_instance(
                                value, field_spec, field_schema.nested_model
                            )
                            result[result_field_name] = nested_instance
                        else:
                            # Value is not a dict - might be a primitive or None
                            result[result_field_name] = value

                elif field_spec.is_wildcard:
                    # Wildcard on nested field - use full model type
                    # This is handled at the top level, but we need to handle it here too
                    # for nested wildcards like recipient(*)
                    if field_schema.nested_model:
                        if field_schema.is_list:
                            if isinstance(value, list):
                                nested_instances = []
                                for item in value:
                                    if isinstance(item, dict):
                                        # Parse all fields from the nested model
                                        nested_instance = self._parse_nested_wildcard(
                                            item, field_schema.nested_model
                                        )
                                        nested_instances.append(nested_instance)
                                    else:
                                        nested_instances.append(item)
                                result[result_field_name] = nested_instances
                            else:
                                result[result_field_name] = value
                        else:
                            if isinstance(value, dict):
                                nested_instance = self._parse_nested_wildcard(
                                    value, field_schema.nested_model
                                )
                                result[result_field_name] = nested_instance
                            else:
                                result[result_field_name] = value
                    else:
                        # Not a nested model, just use the value
                        result[result_field_name] = value

                else:
                    # Simple field - parse using appropriate parser
                    parsed_value = self._parse_field(
                        field_spec.name, value, field_schema.type, field_schema
                    )
                    result[result_field_name] = parsed_value

            # Include automatic fields that are always returned by the API
            # even if not explicitly in the shape
            # Note: 'key' is ONLY valid for Contracts - all other models (Entities, Notices,
            #       Forecasts, Opportunities) do NOT support 'key' field
            automatic_fields = []
            # Only include 'key' for Contracts
            if base_model.__name__ == "Contract":
                automatic_fields.append("key")
            # For Entity models, include 'location' if present (may be alias for physical_address)
            if base_model.__name__ == "Entity":
                automatic_fields.append("location")

            # Get set of fields already processed from shape
            processed_fields = {
                field_spec.alias or field_spec.name for field_spec in shape_spec.fields
            }

            # Add automatic fields if present in data but not in shape
            for auto_field in automatic_fields:
                if auto_field in data and auto_field not in processed_fields:
                    # Check if field exists in model schema
                    if auto_field in model_schema:
                        field_schema = model_schema[auto_field]
                        parsed_value = self._parse_field(
                            auto_field, data[auto_field], field_schema.type, field_schema
                        )
                        result[auto_field] = parsed_value
                    else:
                        # Field not in schema, use raw value
                        result[auto_field] = data[auto_field]

            # Wrap result in ShapedModel for better repr
            type_name = (
                dynamic_type.__name__
                if hasattr(dynamic_type, "__name__")
                else f"{base_model.__name__}Shaped"
            )
            return ShapedModel(result, type_name, shape_spec)

        except ModelInstantiationError:
            raise
        except Exception as e:
            raise ModelInstantiationError(
                f"Failed to create instance of {base_model.__name__}: {e}"
            ) from e

    def _resolve_nested_model(self, nested_model: type | str) -> type:
        """Resolve a nested model reference to an actual model class

        Args:
            nested_model: Model class or string name of the model

        Returns:
            Resolved model class

        Raises:
            ModelInstantiationError: If model cannot be resolved
        """
        if isinstance(nested_model, str):
            # First check if it's in the schema registry (for schema-only models)
            schema = self.schema_registry.get_schema(nested_model)
            if schema:
                # Create a simple type to represent this schema-only model
                # We'll use a dynamically created type that the schema registry can work with
                class_name = nested_model
                model_type = type(class_name, (object,), {"__name__": class_name})
                # Register it with the schema registry if not already registered
                if not self.schema_registry.is_registered(model_type):
                    self.schema_registry._schemas[model_type] = schema
                return model_type

            # Try to import the model from tango.models
            try:
                from tango import models

                model_class = getattr(models, nested_model, None)
                if model_class is None:
                    raise ModelInstantiationError(
                        f"Could not resolve nested model '{nested_model}'"
                    )
                return model_class
            except ImportError as err:
                raise ModelInstantiationError(
                    f"Could not import models module to resolve '{nested_model}'"
                ) from err
        return nested_model

    def _create_nested_instance(
        self, data: dict[str, Any], field_spec: FieldSpec, nested_model: type | str
    ) -> Any:
        """Create instance for nested object

        Args:
            data: Nested object data
            field_spec: Field specification with nested_fields
            nested_model: Model class or string name for the nested object

        Returns:
            Instance of the nested type

        Raises:
            ModelInstantiationError: If nested instance creation fails
        """
        if not field_spec.nested_fields:
            raise ModelInstantiationError(
                f"Field '{field_spec.name}' has no nested field specifications"
            )

        # Resolve nested model if it's a string
        resolved_model = self._resolve_nested_model(nested_model)

        # Create shape spec for nested fields
        nested_shape = ShapeSpec(fields=field_spec.nested_fields)

        # Generate nested type
        nested_type_name = f"{resolved_model.__name__}Shaped"
        nested_type = self.type_generator.generate_type(
            nested_shape, resolved_model, nested_type_name
        )

        # Recursively create nested instance
        return self.create_instance(data, nested_shape, resolved_model, nested_type)

    def _parse_nested_wildcard(
        self, data: dict[str, Any], nested_model: type | str
    ) -> dict[str, Any]:
        """Parse nested object with wildcard (all fields)

        Args:
            data: Nested object data
            nested_model: Model class or string name for the nested object

        Returns:
            Dictionary with all parsed fields
        """
        # Resolve nested model if it's a string
        resolved_model = self._resolve_nested_model(nested_model)

        # Ensure model is registered
        if not self.schema_registry.is_registered(resolved_model):
            self.schema_registry.register(resolved_model)

        # Get model schema
        model_schema = self.schema_registry.get_schema(resolved_model)

        # Parse all fields
        result: dict[str, Any] = {}
        for field_name, value in data.items():
            if field_name in model_schema:
                field_schema = model_schema[field_name]
                parsed_value = self._parse_field(field_name, value, field_schema.type, field_schema)
                result[field_name] = parsed_value
            else:
                # Field not in schema, include as-is
                result[field_name] = value

        return result

    def _parse_field(self, field_name: str, value: Any, field_type: type, field_schema: Any) -> Any:
        """Parse a single field value using appropriate parser

        Args:
            field_name: Name of the field
            value: Raw value from API response
            field_type: Expected type of the field
            field_schema: FieldSchema object with metadata

        Returns:
            Parsed value

        Raises:
            ModelInstantiationError: If parsing fails in strict mode
        """
        # Handle None values
        if value is None:
            return None

        # Get type name for parser lookup
        type_name = field_type.__name__ if hasattr(field_type, "__name__") else str(field_type)

        # Check if we have a parser for this type
        if type_name in self.parsers:
            parser_func = self.parsers[type_name]
            try:
                return parser_func(value)
            except Exception as e:
                logger.warning(
                    f"Failed to parse field '{field_name}' with type {type_name}: {e}, "
                    f"using raw value"
                )
                return value

        # No specific parser - return value as-is
        # This handles basic types like str, int, bool, etc.
        return value

    def validate_data(
        self, data: dict[str, Any], shape_spec: ShapeSpec, base_model: type
    ) -> list[str]:
        """Validate that data matches the shape specification

        This method checks that:
        1. All required fields in the shape are present in the data
        2. Field values have compatible types
        3. Nested objects have the expected structure

        Args:
            data: API response data to validate
            shape_spec: Shape specification to validate against
            base_model: Base model class

        Returns:
            List of validation error messages (empty if valid)

        Examples:
            >>> errors = factory.validate_data(data, shape_spec, Contract)
            >>> if errors:
            ...     print("Validation errors:", errors)
        """
        errors: list[str] = []

        if not isinstance(data, dict):
            errors.append(f"Expected dictionary data, got {type(data).__name__}")
            return errors

        # Ensure model is registered
        if not self.schema_registry.is_registered(base_model):
            self.schema_registry.register(base_model)

        # Get model schema
        model_schema = self.schema_registry.get_schema(base_model)

        # Validate each field in the shape
        for field_spec in shape_spec.fields:
            # Skip wildcards - they're always valid
            if field_spec.is_wildcard:
                continue

            # Check if field exists in data
            if field_spec.name not in data:
                # Missing field - this is OK, we'll set it to None
                continue

            # Check if field exists in schema
            if field_spec.name not in model_schema:
                errors.append(
                    f"Field '{field_spec.name}' does not exist in {base_model.__name__} schema"
                )
                continue

            field_schema = model_schema[field_spec.name]
            value = data[field_spec.name]

            # Validate nested fields
            if field_spec.nested_fields:
                if not field_schema.nested_model:
                    errors.append(
                        f"Field '{field_spec.name}' is not a nested model but has nested field selections"
                    )
                    continue

                # Validate nested data
                if field_schema.is_list:
                    if not isinstance(value, list):
                        errors.append(
                            f"Field '{field_spec.name}' should be a list, got {type(value).__name__}"
                        )
                    else:
                        # Validate each item in the list
                        for i, item in enumerate(value):
                            if isinstance(item, dict):
                                nested_shape = ShapeSpec(fields=field_spec.nested_fields)
                                nested_errors = self.validate_data(
                                    item, nested_shape, field_schema.nested_model
                                )
                                for error in nested_errors:
                                    errors.append(f"{field_spec.name}[{i}]: {error}")
                else:
                    if isinstance(value, dict):
                        nested_shape = ShapeSpec(fields=field_spec.nested_fields)
                        nested_errors = self.validate_data(
                            value, nested_shape, field_schema.nested_model
                        )
                        for error in nested_errors:
                            errors.append(f"{field_spec.name}: {error}")
                    elif value is not None:
                        errors.append(
                            f"Field '{field_spec.name}' should be a dict, got {type(value).__name__}"
                        )

            # Validate list types
            elif field_schema.is_list and value is not None:
                if not isinstance(value, list):
                    errors.append(
                        f"Field '{field_spec.name}' should be a list, got {type(value).__name__}"
                    )

        return errors
