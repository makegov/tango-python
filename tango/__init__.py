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
    WebhookTestDeliveryResult,
)
from .shapes import (
    ModelFactory,
    SchemaRegistry,
    ShapeParser,
    TypeGenerator,
)
from .webhooks import (
    generate_signature,
    parse_signature_header,
    verify_signature,
)
from .webhooks.receiver import Delivery, WebhookReceiver

__version__ = "0.7.0"
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
    "WebhookTestDeliveryResult",
    "ShapeParser",
    "ModelFactory",
    "TypeGenerator",
    "SchemaRegistry",
    "Delivery",
    "WebhookReceiver",
    "generate_signature",
    "parse_signature_header",
    "verify_signature",
]
