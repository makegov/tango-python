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
    GsaElibraryContract,
    ITDashboardInvestment,
    PaginatedResponse,
    RateLimitInfo,
    SearchFilters,
    ShapeConfig,
    WebhookEndpoint,
    WebhookEventType,
    WebhookEventTypesResponse,
    WebhookSubjectTypeDefinition,
    WebhookSubscription,
    WebhookTestDeliveryResult,
)
from .shapes import (
    ModelFactory,
    SchemaRegistry,
    ShapeParser,
    TypeGenerator,
)

__version__ = "0.4.3"
__all__ = [
    "TangoClient",
    "TangoAPIError",
    "TangoAuthError",
    "TangoNotFoundError",
    "TangoValidationError",
    "TangoRateLimitError",
    "RateLimitInfo",
    "GsaElibraryContract",
    "ITDashboardInvestment",
    "PaginatedResponse",
    "SearchFilters",
    "ShapeConfig",
    "WebhookEndpoint",
    "WebhookEventType",
    "WebhookEventTypesResponse",
    "WebhookSubscription",
    "WebhookSubjectTypeDefinition",
    "WebhookTestDeliveryResult",
    "ShapeParser",
    "ModelFactory",
    "TypeGenerator",
    "SchemaRegistry",
]
