"""Core data models for shape specifications"""

from dataclasses import dataclass


@dataclass
class FieldSpec:
    """Specification for a single field in a shape

    Attributes:
        name: The field name (e.g., "key", "piid", "recipient")
        alias: Optional alias for the field (e.g., "vendor_name" for "display_name")
        nested_fields: List of nested field specifications for nested objects
        is_wildcard: Whether this field uses wildcard selection (*)

    Examples:
        Simple field: FieldSpec(name="key")
        Aliased field: FieldSpec(name="display_name", alias="vendor_name")
        Nested field: FieldSpec(name="recipient", nested_fields=[...])
        Wildcard: FieldSpec(name="recipient", is_wildcard=True)
    """

    name: str
    alias: str | None = None
    nested_fields: list["FieldSpec"] | None = None
    is_wildcard: bool = False

    def __hash__(self) -> int:
        """Make hashable for caching"""
        return hash(
            (
                self.name,
                self.alias,
                tuple(self.nested_fields) if self.nested_fields else None,
                self.is_wildcard,
            )
        )

    def __repr__(self) -> str:
        """String representation for debugging"""
        parts = [f"name='{self.name}'"]
        if self.alias:
            parts.append(f"alias='{self.alias}'")
        if self.is_wildcard:
            parts.append("wildcard=True")
        if self.nested_fields:
            parts.append(f"nested_fields={len(self.nested_fields)} fields")
        return f"FieldSpec({', '.join(parts)})"


@dataclass
class ShapeSpec:
    """Complete specification of a shape string

    Attributes:
        fields: List of field specifications
        is_flat: Whether the response should be flattened
        is_flat_lists: Whether lists in the response should be flattened

    Examples:
        Simple shape: ShapeSpec(fields=[FieldSpec(name="key"), FieldSpec(name="piid")])
        Nested shape: ShapeSpec(fields=[FieldSpec(name="recipient", nested_fields=[...])])
    """

    fields: list[FieldSpec]
    is_flat: bool = False
    is_flat_lists: bool = False

    def __hash__(self) -> int:
        """Make hashable for caching"""
        return hash((tuple(self.fields), self.is_flat, self.is_flat_lists))

    def to_cache_key(self, base_model_name: str) -> str:
        """Generate cache key for type generation

        Args:
            base_model_name: Name of the base model class (e.g., "Contract")

        Returns:
            Cache key string combining model name and shape hash
        """
        return f"{base_model_name}:{hash(self)}"

    def __repr__(self) -> str:
        """String representation for debugging"""
        flags = []
        if self.is_flat:
            flags.append("flat=True")
        if self.is_flat_lists:
            flags.append("flat_lists=True")

        flag_str = f", {', '.join(flags)}" if flags else ""
        return f"ShapeSpec(fields={len(self.fields)} fields{flag_str})"
