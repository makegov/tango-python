"""Shape string parser for Tango SDK

This module provides parsing functionality for shape strings used in API requests.
Shape strings specify which fields to include in API responses.

Shape Syntax Grammar:
    shape       := field_list
    field_list  := field ("," field)*
    field       := field_name [alias] [nested]
    field_name  := identifier | "*"
    alias       := "::" identifier
    nested      := "(" field_list ")"
    identifier  := [a-zA-Z_][a-zA-Z0-9_]*

Examples:
    Simple fields: "key,piid,description"
    Nested fields: "recipient(display_name,uei)"
    Wildcards: "recipient(*)"
    Aliases: "display_name::vendor_name"
    Complex: "key,piid,recipient(display_name::vendor_name,uei),award_date"
"""

import re

from tango.exceptions import ShapeParseError, ShapeValidationError
from tango.shapes.models import FieldSpec, ShapeSpec
from tango.shapes.schema import SchemaRegistry


def _suggest_field_correction(invalid_field: str, valid_fields: list[str]) -> str | None:
    """Suggest a correction for an invalid field name

    Args:
        invalid_field: The invalid field name
        valid_fields: List of valid field names

    Returns:
        Suggested field name or None if no good match
    """
    if not valid_fields:
        return None

    invalid_lower = invalid_field.lower()

    # Check for exact case-insensitive match
    for field in valid_fields:
        if field.lower() == invalid_lower:
            return field

    # Check for substring match
    for field in valid_fields:
        if invalid_lower in field.lower() or field.lower() in invalid_lower:
            return field

    # Check for common prefix
    best_match = None
    best_score = 0

    for field in valid_fields:
        # Count common prefix length
        common_prefix = 0
        for c1, c2 in zip(invalid_lower, field.lower(), strict=False):
            if c1 == c2:
                common_prefix += 1
            else:
                break

        score = common_prefix / max(len(invalid_field), len(field))
        if score > best_score and score > 0.5:
            best_score = score
            best_match = field

    return best_match


class ShapeParser:
    """Parser for shape strings

    This class parses shape strings into structured ShapeSpec objects that can be
    used for type generation and validation.

    Attributes:
        _field_pattern: Compiled regex pattern for matching field names
        _parse_cache: Cache of parsed shape specifications

    Examples:
        >>> parser = ShapeParser()
        >>> spec = parser.parse("key,piid,recipient(display_name,uei)")
        >>> print(spec.fields[0].name)
        'key'
        >>> print(spec.fields[2].nested_fields[0].name)
        'display_name'
    """

    # Regex pattern for valid field names (Python identifier rules) - compiled once for performance
    _FIELD_NAME_PATTERN = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")

    # Pre-compiled regex for faster field name extraction
    _FIELD_EXTRACT_PATTERN = re.compile(r"[a-zA-Z_][a-zA-Z0-9_]*")

    def __init__(self, cache_enabled: bool = True, schema_registry: SchemaRegistry | None = None):
        """Initialize the shape parser

        Args:
            cache_enabled: Whether to cache parsed shape specifications
            schema_registry: Optional schema registry for field validation
        """
        self._cache_enabled = cache_enabled
        self._parse_cache: dict[str, ShapeSpec] = {}
        # Lazy initialization of schema registry for performance
        self._schema_registry = schema_registry
        self._schema_registry_initialized = schema_registry is not None

    def parse(self, shape: str) -> ShapeSpec:
        """Parse a shape string into a ShapeSpec

        Args:
            shape: Shape string to parse (e.g., "key,piid,recipient(display_name)")

        Returns:
            ShapeSpec object representing the parsed shape

        Raises:
            ShapeParseError: If the shape string has invalid syntax

        Examples:
            >>> parser = ShapeParser()
            >>> spec = parser.parse("key,piid,description")
            >>> len(spec.fields)
            3

            >>> spec = parser.parse("recipient(display_name,uei)")
            >>> spec.fields[0].nested_fields[0].name
            'display_name'
        """
        if not shape or not shape.strip():
            error_msg = "Shape string cannot be empty."
            error_msg += "\n\nExample shapes:"
            error_msg += '\n  - Simple fields: "key,piid,description"'
            error_msg += '\n  - Nested fields: "key,recipient(display_name,uei)"'
            error_msg += '\n  - Wildcards: "key,recipient(*)"'
            raise ShapeParseError(error_msg, shape=shape or "", position=0)

        # Check cache
        if self._cache_enabled and shape in self._parse_cache:
            return self._parse_cache[shape]

        # Parse the shape
        try:
            fields = self._parse_field_list(shape, 0)[0]
            shape_spec = ShapeSpec(fields=fields)

            # Cache the result
            if self._cache_enabled:
                self._parse_cache[shape] = shape_spec

            return shape_spec

        except ShapeParseError as e:
            # Enhance parse errors with examples
            if "Expected field after comma" in e.message:
                e.message += "\n\nRemove trailing commas from your shape string."
                e.message += '\n\nCorrect: "key,piid,description"'
                e.message += '\nIncorrect: "key,piid,description,"'
            elif "Unmatched" in e.message:
                e.message += "\n\nMake sure all parentheses are properly balanced."
                e.message += '\n\nCorrect: "recipient(display_name,uei)"'
                e.message += '\nIncorrect: "recipient(display_name,uei"'
            elif "Invalid field name" in e.message:
                e.message += "\n\nField names must be valid Python identifiers (letters, numbers, underscores)."
                e.message += '\n\nCorrect: "field_name", "field123"'
                e.message += '\nIncorrect: "field-name", "123field"'
            raise
        except Exception as e:
            error_msg = f"Unexpected error parsing shape: {e}"
            error_msg += "\n\nPlease check your shape syntax."
            error_msg += "\n\nValid shape examples:"
            error_msg += '\n  - "key,piid,description"'
            error_msg += '\n  - "key,recipient(display_name)"'
            error_msg += '\n  - "key,recipient(*)"'
            raise ShapeParseError(error_msg, shape=shape, position=0) from e

    def _parse_field_list(self, shape: str, start_pos: int) -> tuple[list[FieldSpec], int]:
        """Parse a comma-separated list of fields

        Args:
            shape: Full shape string
            start_pos: Starting position in the string

        Returns:
            Tuple of (list of FieldSpec objects, end position)

        Raises:
            ShapeParseError: If syntax is invalid
        """
        fields: list[FieldSpec] = []
        pos = start_pos
        expect_field = True  # Track if we expect a field after a comma

        while pos < len(shape):
            # Skip whitespace
            while pos < len(shape) and shape[pos].isspace():
                pos += 1

            if pos >= len(shape):
                if expect_field and fields:
                    # We had a trailing comma
                    raise ShapeParseError(
                        "Expected field after comma but reached end of string",
                        shape=shape,
                        position=pos,
                    )
                break

            # Check for end of nested section
            if shape[pos] == ")":
                if expect_field and fields:
                    # We had a trailing comma before the closing paren
                    raise ShapeParseError(
                        "Expected field after comma but found ')'", shape=shape, position=pos
                    )
                break

            # Parse a single field
            field, pos = self._parse_field(shape, pos)
            fields.append(field)
            expect_field = False

            # Skip whitespace
            while pos < len(shape) and shape[pos].isspace():
                pos += 1

            if pos >= len(shape):
                break

            # Expect comma or end of nested section
            if shape[pos] == ",":
                pos += 1
                expect_field = True
            elif shape[pos] == ")":
                break
            else:
                raise ShapeParseError(
                    f"Expected ',' or ')' but found '{shape[pos]}'", shape=shape, position=pos
                )

        if not fields:
            raise ShapeParseError("Expected at least one field", shape=shape, position=start_pos)

        return fields, pos

    def _parse_field(self, shape: str, start_pos: int) -> tuple[FieldSpec, int]:
        """Parse a single field specification

        Args:
            shape: Full shape string
            start_pos: Starting position in the string

        Returns:
            Tuple of (FieldSpec object, end position)

        Raises:
            ShapeParseError: If syntax is invalid
        """
        pos = start_pos

        # Skip whitespace
        while pos < len(shape) and shape[pos].isspace():
            pos += 1

        if pos >= len(shape):
            raise ShapeParseError("Unexpected end of shape string", shape=shape, position=pos)

        # Parse field name (or wildcard)
        field_name, pos = self._parse_field_name(shape, pos)

        # Check for wildcard
        is_wildcard = field_name == "*"

        # Skip whitespace
        while pos < len(shape) and shape[pos].isspace():
            pos += 1

        # Check for alias (::)
        alias = None
        if pos < len(shape) - 1 and shape[pos : pos + 2] == "::":
            pos += 2
            alias, pos = self._parse_field_name(shape, pos)

            # Validate alias is not a wildcard
            if alias == "*":
                raise ShapeParseError(
                    "Alias cannot be a wildcard (*)", shape=shape, position=pos - 1
                )

            # Skip whitespace
            while pos < len(shape) and shape[pos].isspace():
                pos += 1

        # Check for nested fields
        nested_fields = None
        if pos < len(shape) and shape[pos] == "(":
            pos += 1

            # Skip whitespace
            while pos < len(shape) and shape[pos].isspace():
                pos += 1

            # Check if this is a wildcard nested field: recipient(*)
            if pos < len(shape) and shape[pos] == "*":
                # This is recipient(*) pattern - mark parent as wildcard
                is_wildcard = True
                pos += 1

                # Skip whitespace
                while pos < len(shape) and shape[pos].isspace():
                    pos += 1

                # Expect closing parenthesis
                if pos >= len(shape) or shape[pos] != ")":
                    raise ShapeParseError(
                        "Expected ')' after wildcard in nested field", shape=shape, position=pos
                    )

                pos += 1
            else:
                # Regular nested fields
                nested_fields, pos = self._parse_field_list(shape, pos)

                # Skip whitespace
                while pos < len(shape) and shape[pos].isspace():
                    pos += 1

                # Expect closing parenthesis
                if pos >= len(shape) or shape[pos] != ")":
                    raise ShapeParseError(
                        "Expected ')' to close nested field list", shape=shape, position=pos
                    )

                pos += 1

        return FieldSpec(
            name=field_name, alias=alias, nested_fields=nested_fields, is_wildcard=is_wildcard
        ), pos

    def _parse_field_name(self, shape: str, start_pos: int) -> tuple[str, int]:
        """Parse a field name or wildcard

        Args:
            shape: Full shape string
            start_pos: Starting position in the string

        Returns:
            Tuple of (field name, end position)

        Raises:
            ShapeParseError: If field name is invalid
        """
        pos = start_pos

        # Skip whitespace
        while pos < len(shape) and shape[pos].isspace():
            pos += 1

        if pos >= len(shape):
            raise ShapeParseError(
                "Expected field name but reached end of string", shape=shape, position=pos
            )

        # Check for wildcard
        if shape[pos] == "*":
            return "*", pos + 1

        # Parse identifier
        start = pos
        while pos < len(shape) and (shape[pos].isalnum() or shape[pos] == "_"):
            pos += 1

        if pos == start:
            raise ShapeParseError(
                f"Invalid field name character: '{shape[pos]}'", shape=shape, position=pos
            )

        field_name = shape[start:pos]

        # Validate field name follows Python identifier rules
        if not self._FIELD_NAME_PATTERN.match(field_name):
            raise ShapeParseError(
                f"Invalid field name: '{field_name}' (must be a valid Python identifier)",
                shape=shape,
                position=start,
            )

        return field_name, pos

    def validate_syntax(self, shape: str) -> None:
        """Validate shape string syntax without full parsing

        This is a lightweight validation that checks for common syntax errors
        without building the full ShapeSpec object.

        Args:
            shape: Shape string to validate

        Raises:
            ShapeParseError: If syntax is invalid

        Examples:
            >>> parser = ShapeParser()
            >>> parser.validate_syntax("key,piid,description")  # OK
            >>> parser.validate_syntax("key,piid,")  # Raises ShapeParseError
        """
        if not shape or not shape.strip():
            raise ShapeParseError("Shape string cannot be empty", shape=shape or "", position=0)

        # Check for balanced parentheses
        paren_count = 0
        for i, char in enumerate(shape):
            if char == "(":
                paren_count += 1
            elif char == ")":
                paren_count -= 1
                if paren_count < 0:
                    raise ShapeParseError("Unmatched closing parenthesis", shape=shape, position=i)

        if paren_count > 0:
            raise ShapeParseError(
                f"Unmatched opening parenthesis ({paren_count} unclosed)",
                shape=shape,
                position=len(shape),
            )

        # Check for trailing comma
        stripped = shape.strip()
        if stripped.endswith(","):
            raise ShapeParseError(
                "Shape string cannot end with a comma", shape=shape, position=len(shape) - 1
            )

        # Check for empty parentheses (except for wildcards)
        if "()" in shape and "(*)" not in shape:
            pos = shape.index("()")
            raise ShapeParseError("Empty nested field list", shape=shape, position=pos)

        # Full parse to catch other errors
        self.parse(shape)

    def clear_cache(self) -> None:
        """Clear the parse cache

        This can be useful for testing or when memory usage is a concern.
        """
        self._parse_cache.clear()

    def get_cache_size(self) -> int:
        """Get the current size of the parse cache

        Returns:
            Number of cached shape specifications
        """
        return len(self._parse_cache)

    def validate(self, shape_spec: ShapeSpec, model_class: type) -> None:
        """Validate that all fields in the shape exist in the model schema

        This method validates that:
        1. All top-level fields exist in the model
        2. All nested fields exist in their respective nested models
        3. Nested field selections are only used on fields that are actually nested objects

        Args:
            shape_spec: Parsed shape specification to validate
            model_class: Model class to validate against (e.g., Contract, Agency)

        Raises:
            ShapeValidationError: If shape contains invalid fields or structure

        Examples:
            >>> from tango.models import Contract
            >>> parser = ShapeParser()
            >>> spec = parser.parse("key,piid,recipient(display_name)")
            >>> parser.validate(spec, Contract)  # OK

            >>> spec = parser.parse("invalid_field")
            >>> parser.validate(spec, Contract)  # Raises ShapeValidationError
        """
        # Lazy initialize schema registry
        if not self._schema_registry_initialized:
            self._schema_registry = SchemaRegistry()
            self._schema_registry_initialized = True

        # Ensure model is registered
        if not self._schema_registry.is_registered(model_class):
            self._schema_registry.register(model_class)

        # Validate each field
        for field_spec in shape_spec.fields:
            self._validate_field_spec(field_spec, model_class)

    def _validate_field_spec(self, field_spec: FieldSpec, model_class: type) -> None:
        """Validate a single field specification against a model

        Args:
            field_spec: Field specification to validate
            model_class: Model class to validate against

        Raises:
            ShapeValidationError: If field is invalid
        """
        # Wildcards are always valid (they expand to all fields)
        if field_spec.is_wildcard:
            return

        # Lazy initialize schema registry if needed
        if not self._schema_registry_initialized:
            self._schema_registry = SchemaRegistry()
            self._schema_registry_initialized = True

        # Validate field exists in model
        try:
            field_schema = self._schema_registry.validate_field(model_class, field_spec.name)
        except ShapeValidationError as e:
            # Enhance error message with suggestions
            model_name = (
                model_class.__name__ if hasattr(model_class, "__name__") else str(model_class)
            )
            model_schema = self._schema_registry.get_schema(model_class)
            valid_fields = list(model_schema.keys())

            error_msg = f"Field '{field_spec.name}' does not exist in {model_name}."

            # Suggest correction
            suggestion = _suggest_field_correction(field_spec.name, valid_fields)
            if suggestion:
                error_msg += f" Did you mean '{suggestion}'?"

            # Show some valid fields as examples
            if valid_fields:
                if len(valid_fields) <= 10:
                    error_msg += f"\n\nValid fields: {', '.join(valid_fields)}"
                else:
                    shown = sorted(valid_fields)[:10]
                    error_msg += f"\n\nExample valid fields: {', '.join(shown)}, ... ({len(valid_fields) - 10} more)"

                # Provide usage example
                if len(valid_fields) >= 1:
                    second_field = valid_fields[1] if len(valid_fields) > 1 else valid_fields[0]
                    error_msg += f'\n\nExample shape: "{valid_fields[0]},{second_field}"'
            else:
                error_msg += "\n\nNo valid fields found in model schema."

            raise ShapeValidationError(error_msg) from e

        # If field has nested selections, validate them
        if field_spec.nested_fields:
            # Check that the field is actually a nested object
            if not field_schema.nested_model:
                model_name = (
                    model_class.__name__ if hasattr(model_class, "__name__") else str(model_class)
                )
                error_msg = (
                    f"Field '{field_spec.name}' in {model_name} is not a nested object "
                    f"and cannot have nested field selections."
                )

                # Provide example of correct usage
                error_msg += (
                    f'\n\nTo include this field, use: "{field_spec.name}" (without parentheses)'
                )
                error_msg += "\n\nNested selections are only valid for object fields like 'recipient', 'agency', 'location', etc."

                # Find some nested fields as examples
                model_schema = self._schema_registry.get_schema(model_class)
                nested_examples = [
                    name for name, schema in model_schema.items() if schema.nested_model
                ]
                if nested_examples:
                    example = nested_examples[0]
                    error_msg += f'\n\nExample with nested field: "{example}(*)" or "{example}(field1,field2)"'

                raise ShapeValidationError(error_msg)

            # Recursively validate nested fields
            for nested_field in field_spec.nested_fields:
                self._validate_field_spec(nested_field, field_schema.nested_model)

    def print_shape_spec(self, shape_spec: ShapeSpec, indent: int = 0) -> None:
        """Print a human-readable representation of a shape specification

        This method prints the shape specification structure to stdout in a formatted way,
        making it easy to understand what fields are included in the shape.

        Args:
            shape_spec: Shape specification to print
            indent: Indentation level for nested fields (default: 0)

        Examples:
            >>> parser = ShapeParser()
            >>> spec = parser.parse("key,piid,recipient(display_name,uei)")
            >>> parser.print_shape_spec(spec)
            Shape Specification:
              - key
              - piid
              - recipient
                - display_name
                - uei
        """

        if indent == 0:
            print("Shape Specification:")
            if shape_spec.is_flat:
                print("  (flat response)")
            if shape_spec.is_flat_lists:
                print("  (flat lists)")

        for field_spec in shape_spec.fields:
            self._print_field_spec(field_spec, indent + 1)

    def _print_field_spec(self, field_spec: FieldSpec, indent: int) -> None:
        """Print a single field specification

        Args:
            field_spec: Field specification to print
            indent: Indentation level
        """
        indent_str = "  " * indent

        # Build field display string
        field_display = field_spec.name

        if field_spec.is_wildcard:
            field_display = "*"

        if field_spec.alias:
            field_display = f"{field_spec.name} (alias: {field_spec.alias})"

        print(f"{indent_str}- {field_display}")

        # Print nested fields
        if field_spec.nested_fields:
            for nested_field in field_spec.nested_fields:
                self._print_field_spec(nested_field, indent + 1)

    def format_shape_spec(self, shape_spec: ShapeSpec) -> str:
        """Format a shape specification as a shape string

        This method converts a ShapeSpec object back into a shape string,
        which can be useful for debugging or displaying the shape.

        Args:
            shape_spec: Shape specification to format

        Returns:
            Shape string representation

        Examples:
            >>> parser = ShapeParser()
            >>> spec = parser.parse("key,piid,recipient(display_name,uei)")
            >>> shape_string = parser.format_shape_spec(spec)
            >>> print(shape_string)
            'key,piid,recipient(display_name,uei)'
        """
        field_strings = [self._format_field_spec(field) for field in shape_spec.fields]
        return ",".join(field_strings)

    def _format_field_spec(self, field_spec: FieldSpec) -> str:
        """Format a single field specification as a string

        Args:
            field_spec: Field specification to format

        Returns:
            String representation of the field
        """
        if field_spec.is_wildcard and not field_spec.nested_fields:
            return "*"

        result = field_spec.name

        if field_spec.alias:
            result += f"::{field_spec.alias}"

        if field_spec.nested_fields:
            nested_strings = [self._format_field_spec(f) for f in field_spec.nested_fields]
            result += f"({','.join(nested_strings)})"
        elif field_spec.is_wildcard:
            result += "(*)"

        return result
