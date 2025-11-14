"""Tango API Python SDK"""

from .client import TangoClient
from .exceptions import (
    TangoAPIError,
    TangoAuthError,
    TangoNotFoundError,
    TangoRateLimitError,
    TangoValidationError,
)
from .models import (
    PaginatedResponse,
    SearchFilters,
    ShapeConfig,
)
from .shapes import (
    ModelFactory,
    SchemaRegistry,
    ShapeParser,
    TypeGenerator,
)

__version__ = "0.2.0"
__all__ = [
    "TangoClient",
    "TangoAPIError",
    "TangoAuthError",
    "TangoNotFoundError",
    "TangoValidationError",
    "TangoRateLimitError",
    "PaginatedResponse",
    "SearchFilters",
    "ShapeConfig",
    "ShapeParser",
    "ModelFactory",
    "TypeGenerator",
    "SchemaRegistry",
]
