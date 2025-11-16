"""Dynamic type generator for Tango SDK

This module provides functionality to generate TypedDict types at runtime based on
shape specifications. Generated types provide IDE autocomplete and static type checking
support for shaped API responses.

Examples:
    >>> from tango.models import Contract
    >>> from tango.shapes import ShapeParser, TypeGenerator
    >>>
    >>> parser = ShapeParser()
    >>> generator = TypeGenerator()
    >>>
    >>> shape_spec = parser.parse("key,piid,recipient(display_name)")
    >>> dynamic_type = generator.generate_type(shape_spec, Contract)
    >>>
    >>> # dynamic_type is now a TypedDict with only the specified fields
"""

import logging
import threading
from collections import OrderedDict
from typing import Any, get_args, get_origin, get_type_hints

from tango.exceptions import TypeGenerationError
from tango.shapes.models import ShapeSpec
from tango.shapes.schema import SchemaRegistry

logger = logging.getLogger(__name__)


class LRUCache:
    """Thread-safe LRU cache implementation

    This is a simple LRU (Least Recently Used) cache that evicts the least
    recently used items when the cache reaches its maximum size.

    Attributes:
        max_size: Maximum number of items in the cache
        cache: Ordered dictionary storing cached items
        lock: Thread lock for thread-safe access
    """

    def __init__(self, max_size: int = 100):
        """Initialize the LRU cache

        Args:
            max_size: Maximum number of items to cache
        """
        self.max_size = max_size
        self.cache: OrderedDict[str, type] = OrderedDict()
        self.lock = threading.Lock()
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> type | None:
        """Get an item from the cache

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        with self.lock:
            if key in self.cache:
                # Move to end (most recently used)
                self.cache.move_to_end(key)
                self._hits += 1
                return self.cache[key]
            self._misses += 1
            return None

    def put(self, key: str, value: type) -> None:
        """Put an item in the cache

        Args:
            key: Cache key
            value: Value to cache
        """
        with self.lock:
            if key in self.cache:
                # Update existing item and move to end
                self.cache.move_to_end(key)
            else:
                # Add new item
                self.cache[key] = value
                # Evict oldest if over max size
                if len(self.cache) > self.max_size:
                    self.cache.popitem(last=False)

    def clear(self) -> None:
        """Clear all items from the cache"""
        with self.lock:
            self.cache.clear()
            self._hits = 0
            self._misses = 0

    def size(self) -> int:
        """Get the current size of the cache

        Returns:
            Number of items in the cache
        """
        with self.lock:
            return len(self.cache)

    def stats(self) -> dict[str, Any]:
        """Get cache statistics

        Returns:
            Dictionary with cache statistics
        """
        with self.lock:
            total = self._hits + self._misses
            hit_rate = (self._hits / total * 100) if total > 0 else 0.0
            return {
                "size": len(self.cache),
                "max_size": self.max_size,
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": f"{hit_rate:.1f}%",
                "keys": list(self.cache.keys()),
            }


class TypeGenerator:
    """Generate dynamic TypedDict types from shape specifications

    This class creates TypedDict types at runtime that match the exact structure
    of shaped API responses. Generated types are cached using an LRU cache for performance.

    Attributes:
        _schema_registry: Registry for model schema information
        _type_cache: LRU cache of generated types
        _cache_enabled: Whether caching is enabled

    Examples:
        >>> from tango.models import Contract
        >>> generator = TypeGenerator()
        >>> shape_spec = ShapeSpec(fields=[FieldSpec(name="key"), FieldSpec(name="piid")])
        >>> contract_type = generator.generate_type(shape_spec, Contract, "ContractShaped")
    """

    def __init__(
        self,
        cache_enabled: bool = True,
        cache_size: int = 100,
        schema_registry: SchemaRegistry | None = None,
        enable_logging: bool = False,
    ):
        """Initialize the type generator

        Args:
            cache_enabled: Whether to cache generated types
            cache_size: Maximum number of types to cache (default: 100)
            schema_registry: Optional schema registry for field type information
            enable_logging: Whether to log cache hits/misses (default: False)
        """
        self._schema_registry = schema_registry or SchemaRegistry()
        self._type_cache = LRUCache(max_size=cache_size)
        self._cache_enabled = cache_enabled
        self._enable_logging = enable_logging
        # Cache for get_type_hints results to avoid repeated introspection
        self._type_hints_cache: dict[type, dict[str, Any]] = {}

    def generate_type(
        self, shape_spec: ShapeSpec, base_model: type, type_name: str | None = None
    ) -> type:
        """Generate a TypedDict type matching the shape specification

        This method creates a new TypedDict class with only the fields specified
        in the shape. Nested fields are recursively converted to nested TypedDict types.

        Args:
            shape_spec: Parsed shape specification
            base_model: Base static model class (e.g., Contract, Agency)
            type_name: Optional name for the generated type (defaults to "{BaseModel}Shaped")

        Returns:
            A new TypedDict type with the specified fields

        Raises:
            TypeGenerationError: If type generation fails

        Examples:
            >>> from tango.models import Contract
            >>> from tango.shapes import ShapeParser
            >>>
            >>> parser = ShapeParser()
            >>> generator = TypeGenerator()
            >>>
            >>> spec = parser.parse("key,piid,description")
            >>> shaped_type = generator.generate_type(spec, Contract)
            >>>
            >>> # shaped_type is a TypedDict with key, piid, and description fields
        """
        # Generate cache key
        cache_key = shape_spec.to_cache_key(base_model.__name__)

        # Check cache
        if self._cache_enabled:
            cached_type = self._type_cache.get(cache_key)
            if cached_type is not None:
                if self._enable_logging:
                    logger.debug(f"Type cache HIT for {base_model.__name__} (key: {cache_key})")
                return cached_type
            else:
                if self._enable_logging:
                    logger.debug(f"Type cache MISS for {base_model.__name__} (key: {cache_key})")

        # Generate type name if not provided
        if type_name is None:
            type_name = f"{base_model.__name__}Shaped"

        try:
            # Ensure model is registered
            if not self._schema_registry.is_registered(base_model):
                self._schema_registry.register(base_model)

            # Get model schema
            model_schema = self._schema_registry.get_schema(base_model)

            # Build field annotations for TypedDict
            annotations: dict[str, Any] = {}

            for field_spec in shape_spec.fields:
                field_name = field_spec.alias or field_spec.name

                # Handle wildcard - include all fields from base model
                if field_spec.is_wildcard:
                    # Get all fields from base model (use cache to avoid repeated introspection)
                    try:
                        if base_model not in self._type_hints_cache:
                            self._type_hints_cache[base_model] = get_type_hints(base_model)
                        base_hints = self._type_hints_cache[base_model]
                        annotations.update(base_hints)
                    except Exception as e:
                        raise TypeGenerationError(
                            f"Failed to expand wildcard for {base_model.__name__}: {e}"
                        ) from e
                    continue

                # Get field schema
                if field_spec.name not in model_schema:
                    # Field doesn't exist in schema - this should have been caught by validation
                    # but we'll handle it gracefully
                    annotations[field_name] = Any
                    continue

                field_schema = model_schema[field_spec.name]

                # Determine field type
                if field_spec.nested_fields:
                    # Generate nested type
                    if not field_schema.nested_model:
                        raise TypeGenerationError(
                            f"Field '{field_spec.name}' is not a nested model but has nested field selections"
                        )

                    # Resolve nested model if it's a string
                    resolved_nested_model = self._resolve_nested_model(field_schema.nested_model)

                    nested_shape = ShapeSpec(fields=field_spec.nested_fields)
                    nested_type_name = f"{type_name}_{field_name.capitalize()}"
                    nested_type = self._generate_nested_type(
                        nested_shape, resolved_nested_model, nested_type_name
                    )

                    # Handle list types
                    if field_schema.is_list:
                        field_type = list[nested_type]  # type: ignore
                    else:
                        field_type = nested_type

                    # Handle optional types
                    if field_schema.is_optional:
                        field_type = field_type | None  # type: ignore

                    annotations[field_name] = field_type

                elif field_spec.is_wildcard:
                    # Wildcard on nested field - use full model type
                    if field_schema.nested_model:
                        # Resolve nested model if it's a string
                        field_type = self._resolve_nested_model(field_schema.nested_model)
                    else:
                        field_type = field_schema.type

                    # Handle list types
                    if field_schema.is_list:
                        field_type = list[field_type]  # type: ignore

                    # Handle optional types
                    if field_schema.is_optional:
                        field_type = field_type | None  # type: ignore

                    annotations[field_name] = field_type

                else:
                    # Simple field - use schema type
                    field_type = field_schema.type

                    # Handle list types
                    if field_schema.is_list:
                        field_type = list[field_type]  # type: ignore

                    # Handle optional types
                    if field_schema.is_optional:
                        field_type = field_type | None  # type: ignore

                    annotations[field_name] = field_type

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

            for auto_field in automatic_fields:
                if auto_field not in annotations and auto_field in model_schema:
                    field_schema = model_schema[auto_field]
                    field_type = field_schema.type
                    # Handle optional types
                    if field_schema.is_optional:
                        field_type = field_type | None  # type: ignore
                    annotations[auto_field] = field_type

            # Create TypedDict dynamically
            # We use type() to create the class dynamically
            shaped_type = type(
                type_name,
                (dict,),
                {
                    "__annotations__": annotations,
                    "__module__": base_model.__module__,
                    "__doc__": f"Shaped type for {base_model.__name__} with fields: {', '.join(annotations.keys())}",
                },
            )

            # Cache the generated type
            if self._cache_enabled:
                self._type_cache.put(cache_key, shaped_type)
                if self._enable_logging:
                    logger.debug(f"Cached new type for {base_model.__name__} (key: {cache_key})")

            return shaped_type

        except TypeGenerationError:
            raise
        except Exception as e:
            raise TypeGenerationError(
                f"Failed to generate type for {base_model.__name__}: {e}"
            ) from e

    def _generate_nested_type(
        self, shape_spec: ShapeSpec, base_model: type, type_name: str
    ) -> type:
        """Generate a TypedDict for a nested field selection

        This is a helper method that recursively generates types for nested objects.

        Args:
            shape_spec: Shape specification for the nested fields
            base_model: Base model class for the nested object
            type_name: Name for the generated nested type

        Returns:
            A new TypedDict type for the nested object

        Raises:
            TypeGenerationError: If type generation fails
        """
        # Use the main generate_type method for consistency
        return self.generate_type(shape_spec, base_model, type_name)

    def _resolve_nested_model(self, nested_model: type | str) -> type:
        """Resolve a nested model reference to an actual model class

        Args:
            nested_model: Model class or string name of the model

        Returns:
            Resolved model class

        Raises:
            TypeGenerationError: If model cannot be resolved
        """
        if isinstance(nested_model, str):
            # First check if it's in the schema registry (for schema-only models)
            schema = self._schema_registry.get_schema(nested_model)
            if schema:
                # Create a simple type to represent this schema-only model
                # We'll use a dynamically created type that the schema registry can work with
                # Create a type that can be used as a model class
                # The schema registry will handle the actual schema lookup
                class_name = nested_model
                model_type = type(class_name, (object,), {"__name__": class_name})
                # Register it with the schema registry if not already registered
                if not self._schema_registry.is_registered(model_type):
                    self._schema_registry._schemas[model_type] = schema
                return model_type

            # Try to import the model from tango.models
            try:
                from tango import models

                model_class = getattr(models, nested_model, None)
                if model_class is None:
                    raise TypeGenerationError(f"Could not resolve nested model '{nested_model}'")
                return model_class
            except ImportError as err:
                raise TypeGenerationError(
                    f"Could not import models module to resolve '{nested_model}'"
                ) from err
        return nested_model

    def clear_cache(self) -> None:
        """Clear the type cache

        This can be useful for testing or when memory usage is a concern.

        Examples:
            >>> generator = TypeGenerator()
            >>> # ... generate some types ...
            >>> generator.clear_cache()
            >>> generator.get_cache_size()
            0
        """
        self._type_cache.clear()

    def get_cache_size(self) -> int:
        """Get the current size of the type cache

        Returns:
            Number of cached types

        Examples:
            >>> generator = TypeGenerator()
            >>> generator.get_cache_size()
            0
        """
        return self._type_cache.size()

    def get_cache_stats(self) -> dict[str, Any]:
        """Get statistics about the type cache

        Returns:
            Dictionary with cache statistics including size, hits, misses, and hit rate

        Examples:
            >>> generator = TypeGenerator()
            >>> stats = generator.get_cache_stats()
            >>> print(stats['size'])
            0
            >>> print(stats['hit_rate'])
            '0.0%'
        """
        stats = self._type_cache.stats()
        stats["enabled"] = self._cache_enabled
        stats["logging_enabled"] = self._enable_logging
        return stats

    def enable_cache_logging(self, enabled: bool = True) -> None:
        """Enable or disable cache hit/miss logging

        When enabled, the type generator will log debug messages for cache hits and misses.
        This is useful for debugging and performance analysis.

        Args:
            enabled: Whether to enable logging (default: True)

        Examples:
            >>> generator = TypeGenerator()
            >>> generator.enable_cache_logging(True)
            >>> # Now cache operations will be logged at DEBUG level
        """
        self._enable_logging = enabled
        if enabled:
            logger.info("Type generator cache logging enabled")
        else:
            logger.info("Type generator cache logging disabled")

    def inspect_type(self, generated_type: type) -> dict[str, Any]:
        """Inspect the structure of a generated type

        This method provides detailed information about a dynamically generated type,
        including its fields, types, and documentation.

        Args:
            generated_type: The dynamically generated type to inspect

        Returns:
            Dictionary with type information including:
            - name: Type name
            - fields: Dictionary of field names to type annotations
            - doc: Type documentation string
            - module: Module where type is defined

        Examples:
            >>> from tango.models import Contract
            >>> from tango.shapes import ShapeParser
            >>>
            >>> parser = ShapeParser()
            >>> generator = TypeGenerator()
            >>>
            >>> spec = parser.parse("key,piid,description")
            >>> shaped_type = generator.generate_type(spec, Contract)
            >>> info = generator.inspect_type(shaped_type)
            >>> print(info['name'])
            'ContractShaped'
            >>> print(list(info['fields'].keys()))
            ['key', 'piid', 'description']
        """
        type_info: dict[str, Any] = {
            "name": generated_type.__name__
            if hasattr(generated_type, "__name__")
            else str(generated_type),
            "fields": {},
            "doc": generated_type.__doc__ if hasattr(generated_type, "__doc__") else None,
            "module": generated_type.__module__ if hasattr(generated_type, "__module__") else None,
        }

        # Extract field annotations
        if hasattr(generated_type, "__annotations__"):
            type_info["fields"] = generated_type.__annotations__.copy()

        # Format field types as strings for readability
        formatted_fields = {}
        for field_name, field_type in type_info["fields"].items():
            formatted_fields[field_name] = self._format_type_annotation(field_type)

        type_info["fields_formatted"] = formatted_fields

        return type_info

    def _format_type_annotation(self, type_annotation: Any) -> str:
        """Format a type annotation as a readable string

        Args:
            type_annotation: Type annotation to format

        Returns:
            String representation of the type
        """
        # Handle None type
        if type_annotation is type(None):
            return "None"

        # Handle basic types
        if hasattr(type_annotation, "__name__"):
            type_name = type_annotation.__name__
        else:
            type_name = str(type_annotation)

        # Handle generic types (list, dict, etc.)
        origin = get_origin(type_annotation)
        if origin is not None:
            args = get_args(type_annotation)
            if origin is list:
                if args:
                    return f"list[{self._format_type_annotation(args[0])}]"
                return "list"
            elif origin is dict:
                if args and len(args) == 2:
                    return f"dict[{self._format_type_annotation(args[0])}, {self._format_type_annotation(args[1])}]"
                return "dict"
            elif hasattr(origin, "__name__"):
                # Union types (e.g., str | None)
                if args:
                    formatted_args = [self._format_type_annotation(arg) for arg in args]
                    return f"{origin.__name__}[{', '.join(formatted_args)}]"
                return origin.__name__

        return type_name

    def print_type_structure(self, generated_type: type, indent: int = 0) -> None:
        """Print a human-readable representation of a generated type structure

        This method prints the type structure to stdout in a formatted way,
        making it easy to understand the shape of the generated type.

        Args:
            generated_type: The dynamically generated type to print
            indent: Indentation level for nested types (default: 0)

        Examples:
            >>> from tango.models import Contract
            >>> from tango.shapes import ShapeParser
            >>>
            >>> parser = ShapeParser()
            >>> generator = TypeGenerator()
            >>>
            >>> spec = parser.parse("key,piid,recipient(display_name,uei)")
            >>> shaped_type = generator.generate_type(spec, Contract)
            >>> generator.print_type_structure(shaped_type)
            ContractShaped:
              key: str
              piid: str | None
              recipient: ContractShaped_Recipient | None
        """
        type_info = self.inspect_type(generated_type)
        indent_str = "  " * indent

        print(f"{indent_str}{type_info['name']}:")

        for field_name, field_type_str in type_info["fields_formatted"].items():
            print(f"{indent_str}  {field_name}: {field_type_str}")

        # If there are nested types, we could recursively print them
        # but for now, we'll just show the top-level structure
