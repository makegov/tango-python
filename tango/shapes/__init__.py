"""Dynamic shape models for Tango SDK"""

from tango.shapes.explicit_schemas import (
    EXPLICIT_SCHEMAS,
    get_explicit_schema,
    register_explicit_schemas,
)
from tango.shapes.factory import (
    ModelFactory,
    ShapedModel,
    build_parser_registry_from_client,
    create_default_parser_registry,
)
from tango.shapes.generator import TypeGenerator
from tango.shapes.models import FieldSpec, ShapeSpec
from tango.shapes.parser import ShapeParser
from tango.shapes.schema import FieldSchema, SchemaRegistry
from tango.shapes.types import (
    ContractMinimalShaped,
)

__all__ = [
    # Core classes
    "FieldSpec",
    "ShapeSpec",
    "ShapeParser",
    "FieldSchema",
    "SchemaRegistry",
    "TypeGenerator",
    "ModelFactory",
    "ShapedModel",
    # Parser registry functions
    "build_parser_registry_from_client",
    "create_default_parser_registry",
    # Explicit schemas
    "EXPLICIT_SCHEMAS",
    "get_explicit_schema",
    "register_explicit_schemas",
    # Predefined shaped type for default contract shape
    "ContractMinimalShaped",
]
