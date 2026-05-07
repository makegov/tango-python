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
    Vehicle,
    VehicleMetrics,
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

__version__ = "0.6.0"
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
    "Vehicle",
    "VehicleMetrics",
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
