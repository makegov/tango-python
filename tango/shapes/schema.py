"""Schema registry for model validation

This module provides schema extraction and validation for Tango models.
It allows the shape parser to validate that requested fields exist in the model schema.

This module now includes explicit schema definitions for all resource types to support
the dynamic-only model approach. These schemas define field types, nested models, and
list indicators independently of the dataclass definitions.
"""

from dataclasses import dataclass
from typing import Any, get_args, get_origin, get_type_hints

from tango.exceptions import ShapeValidationError


@dataclass
class FieldSchema:
    """Schema information for a model field

    Attributes:
        name: Field name
        type: Field type (e.g., str, int, Decimal)
        is_optional: Whether the field is Optional (can be None)
        is_list: Whether the field is a list type
        nested_model: For nested objects, the model class

    Examples:
        Simple field: FieldSchema(name="key", type=str, is_optional=False, is_list=False)
        Optional field: FieldSchema(name="piid", type=str, is_optional=True, is_list=False)
        List field: FieldSchema(name="tags", type=str, is_optional=False, is_list=True)
        Nested: FieldSchema(name="recipient", type=Agency, is_optional=True, is_list=False, nested_model=Agency)
    """

    name: str
    type: type
    is_optional: bool
    is_list: bool
    nested_model: type | None = None

    def __repr__(self) -> str:
        """String representation for debugging"""
        type_str = self.type.__name__ if hasattr(self.type, "__name__") else str(self.type)

        if self.is_list:
            type_str = f"list[{type_str}]"
        if self.is_optional:
            type_str = f"{type_str} | None"

        return f"FieldSchema(name='{self.name}', type={type_str})"


class SchemaRegistry:
    """Registry of model schemas for validation and type inference

    This class maintains a registry of all known model schemas, allowing
    the shape parser to validate that requested fields exist in the model.

    Attributes:
        _schemas: Dictionary mapping model classes to their field schemas

    Examples:
        >>> from tango.models import Contract
        >>> registry = SchemaRegistry()
        >>> registry.register(Contract)
        >>> schema = registry.get_schema(Contract)
        >>> 'key' in schema
        True
    """

    def __init__(self, auto_register_builtin: bool = True, use_explicit_schemas: bool = True):
        """Initialize the schema registry

        Args:
            auto_register_builtin: If True, automatically register all built-in Tango models
            use_explicit_schemas: If True, use explicit schema definitions instead of dataclass introspection
        """
        self._schemas: dict[type | str, dict[str, FieldSchema]] = {}
        self._auto_register_builtin = auto_register_builtin
        self._use_explicit_schemas = use_explicit_schemas
        self._builtin_registered = False
        self._explicit_schemas_registered = False

        # Lazy initialization - only register builtin models when first needed
        # This improves startup performance

    def _register_explicit_schemas(self) -> None:
        """Register explicit schema definitions

        This method registers all explicit schema definitions from the
        explicit_schemas module. These schemas are comprehensive and
        independent of the dataclass definitions.
        """
        try:
            from tango.shapes.explicit_schemas import EXPLICIT_SCHEMAS

            for model_name, schema in EXPLICIT_SCHEMAS.items():
                self._schemas[model_name] = schema

            self._explicit_schemas_registered = True
        except ImportError:
            # Explicit schemas module not available, fall back to dataclass introspection
            pass

    def _register_builtin_models(self) -> None:
        """Register all built-in Tango model schemas

        This method registers all the standard model schemas that come with the Tango SDK,
        including Contract, Agency, Location, Entity, Grant, etc.

        Since the SDK now uses dynamic-only models, this always uses the explicit schema
        definitions from tango.shapes.explicit_schemas rather than introspecting dataclasses.
        """
        # Always use explicit schemas (dataclass models have been removed)
        if not self._explicit_schemas_registered:
            self._register_explicit_schemas()
            self._builtin_registered = True

    def register(self, model_class: type) -> None:
        """Register a model class schema

        Extracts field information from the model's type hints and stores
        it in the registry for validation.

        Args:
            model_class: Model class to register (e.g., Contract, Agency)

        Examples:
            >>> from tango.models import Contract
            >>> registry = SchemaRegistry()
            >>> registry.register(Contract)
        """
        if model_class in self._schemas:
            return  # Already registered

        schema: dict[str, FieldSchema] = {}

        try:
            type_hints = get_type_hints(model_class)
        except Exception:
            # If we can't get type hints, register empty schema
            self._schemas[model_class] = schema
            return

        for field_name, field_type in type_hints.items():
            field_schema = self._analyze_field_type(field_name, field_type)
            schema[field_name] = field_schema

        self._schemas[model_class] = schema

    def _analyze_field_type(self, field_name: str, field_type: Any) -> FieldSchema:
        """Analyze a field type to extract schema information

        Args:
            field_name: Name of the field
            field_type: Type annotation for the field

        Returns:
            FieldSchema object with extracted information
        """
        origin = get_origin(field_type)
        args = get_args(field_type)

        is_optional = False
        is_list = False
        nested_model = None
        base_type = field_type

        # Check for Union types (including Optional which is Union[T, None])
        if origin is type(None) or (hasattr(origin, "__name__") and origin.__name__ == "UnionType"):
            # This is a union type (e.g., str | None)
            if args:
                # Filter out NoneType
                non_none_args = [arg for arg in args if arg is not type(None)]
                if len(non_none_args) == 1:
                    is_optional = True
                    base_type = non_none_args[0]
                    origin = get_origin(base_type)
                    args = get_args(base_type)

        # Check for list types
        if origin is list:
            is_list = True
            if args:
                base_type = args[0]
                # Check if list element is optional
                elem_origin = get_origin(base_type)
                elem_args = get_args(base_type)
                if elem_origin is type(None) or (
                    hasattr(elem_origin, "__name__") and elem_origin.__name__ == "UnionType"
                ):
                    if elem_args:
                        non_none_args = [arg for arg in elem_args if arg is not type(None)]
                        if len(non_none_args) == 1:
                            base_type = non_none_args[0]

        # Check if base_type is a class (potential nested model)
        if isinstance(base_type, type) and hasattr(base_type, "__dataclass_fields__"):
            nested_model = base_type

        return FieldSchema(
            name=field_name,
            type=base_type,
            is_optional=is_optional,
            is_list=is_list,
            nested_model=nested_model,
        )

    def get_schema(self, model_class: type | str) -> dict[str, FieldSchema]:
        """Get schema for a model class or model name

        Args:
            model_class: Model class or model name string to get schema for

        Returns:
            Dictionary mapping field names to FieldSchema objects

        Examples:
            >>> from tango.models import Contract
            >>> registry = SchemaRegistry()
            >>> registry.register(Contract)
            >>> schema = registry.get_schema(Contract)
            >>> schema['key'].type
            <class 'str'>

            >>> # Can also use string names
            >>> schema = registry.get_schema("Contract")
            >>> schema['key'].type
            <class 'str'>
        """
        # Lazy register builtin models on first access
        if self._auto_register_builtin and not self._builtin_registered:
            self._register_builtin_models()
            self._builtin_registered = True

        # Handle string model names
        if isinstance(model_class, str):
            # Check if we have an explicit schema for this name
            if model_class in self._schemas:
                return self._schemas[model_class]

            # Try to find by class name
            for key, schema in self._schemas.items():
                if isinstance(key, type) and key.__name__ == model_class:
                    return schema

            # Not found, return empty schema
            return {}

        # Handle class types
        if model_class not in self._schemas:
            # Check if we have an explicit schema by class name
            class_name = (
                model_class.__name__ if hasattr(model_class, "__name__") else str(model_class)
            )
            if class_name in self._schemas:
                return self._schemas[class_name]

            # Try to register the class
            self.register(model_class)

        return self._schemas.get(model_class, {})

    def validate_field(self, model_class: type | str, field_name: str) -> FieldSchema:
        """Validate that a field exists in the model schema

        Args:
            model_class: Model class or model name string to validate against
            field_name: Field name to validate

        Returns:
            FieldSchema for the validated field

        Raises:
            ShapeValidationError: If field doesn't exist in the model

        Examples:
            >>> from tango.models import Contract
            >>> registry = SchemaRegistry()
            >>> registry.register(Contract)
            >>> field = registry.validate_field(Contract, 'key')
            >>> field.name
            'key'

            >>> registry.validate_field(Contract, 'invalid_field')
            Traceback (most recent call last):
                ...
            ShapeValidationError: Field 'invalid_field' does not exist in Contract
        """
        schema = self.get_schema(model_class)

        if field_name not in schema:
            # Get model name for error message
            if isinstance(model_class, str):
                model_name = model_class
            else:
                model_name = (
                    model_class.__name__ if hasattr(model_class, "__name__") else str(model_class)
                )

            available_fields = sorted(schema.keys())

            # Try to suggest similar field names
            suggestions = self._find_similar_fields(field_name, available_fields)
            suggestion_text = ""
            if suggestions:
                suggestion_text = f" Did you mean: {', '.join(suggestions)}?"

            raise ShapeValidationError(
                f"Field '{field_name}' does not exist in {model_name}.{suggestion_text}", shape=None
            )

        return schema[field_name]

    def _find_similar_fields(
        self, field_name: str, available_fields: list[str], max_suggestions: int = 3
    ) -> list[str]:
        """Find similar field names for suggestions

        Uses simple string similarity to suggest corrections for typos.

        Args:
            field_name: The invalid field name
            available_fields: List of valid field names
            max_suggestions: Maximum number of suggestions to return

        Returns:
            List of suggested field names
        """
        suggestions = []
        field_lower = field_name.lower()

        # Look for fields that start with the same prefix
        for available in available_fields:
            if available.lower().startswith(field_lower[:3]) and len(field_lower) >= 3:
                suggestions.append(available)

        # Look for fields that contain the search term
        if not suggestions:
            for available in available_fields:
                if field_lower in available.lower() or available.lower() in field_lower:
                    suggestions.append(available)

        return suggestions[:max_suggestions]

    def is_registered(self, model_class: type | str) -> bool:
        """Check if a model class or model name is registered

        Args:
            model_class: Model class or model name string to check

        Returns:
            True if the model is registered, False otherwise
        """
        # Lazy register builtin models on first access
        if self._auto_register_builtin and not self._builtin_registered:
            self._register_builtin_models()
            self._builtin_registered = True

        # Handle string model names
        if isinstance(model_class, str):
            if model_class in self._schemas:
                return True
            # Check if any registered class has this name
            for key in self._schemas.keys():
                if isinstance(key, type) and key.__name__ == model_class:
                    return True
            return False

        # Handle class types
        if model_class in self._schemas:
            return True

        # Check if we have an explicit schema by class name
        class_name = model_class.__name__ if hasattr(model_class, "__name__") else str(model_class)
        return class_name in self._schemas

    def clear(self) -> None:
        """Clear all registered schemas

        This can be useful for testing or when models are dynamically updated.
        """
        self._schemas.clear()
