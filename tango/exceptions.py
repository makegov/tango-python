"""Tango API exceptions"""

from typing import Any


class TangoAPIError(Exception):
    """Base exception for Tango API errors"""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response_data: dict[str, Any] | None = None,
    ):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data or {}
        super().__init__(self.message)


class TangoAuthError(TangoAPIError):
    """Authentication error"""

    pass


class TangoNotFoundError(TangoAPIError):
    """Resource not found error"""

    pass


class TangoValidationError(TangoAPIError):
    """Request validation error"""

    pass


class TangoRateLimitError(TangoAPIError):
    """Rate limit exceeded error"""

    @property
    def wait_in_seconds(self) -> int | None:
        """Seconds to wait before retrying, from API response."""
        val = self.response_data.get("wait_in_seconds")
        if val is not None:
            try:
                return int(val)
            except (ValueError, TypeError):
                return None
        return None

    @property
    def detail(self) -> str | None:
        """Human-readable detail from API response."""
        return self.response_data.get("detail")

    @property
    def limit_type(self) -> str | None:
        """Which limit was hit: 'burst' or 'daily', parsed from detail."""
        d = self.detail
        if not d:
            return None
        lower = d.lower()
        if "burst" in lower or "minute" in lower:
            return "burst"
        if "daily" in lower or "day" in lower:
            return "daily"
        return None


class ShapeError(TangoAPIError):
    """Base exception for shape-related errors"""

    pass


class ShapeValidationError(ShapeError):
    """Shape validation error

    Raised when a shape string contains invalid field names or structure
    that doesn't match the model schema.
    """

    def __init__(self, message: str, shape: str | None = None):
        super().__init__(message)
        self.shape = shape


class ShapeParseError(ShapeError):
    """Shape parsing error

    Raised when a shape string has invalid syntax and cannot be parsed.
    """

    def __init__(self, message: str, shape: str, position: int | None = None):
        super().__init__(message)
        self.shape = shape
        self.position = position


class TypeGenerationError(ShapeError):
    """Error during dynamic type generation

    Raised when the system cannot generate a dynamic type from a shape specification.
    """

    pass


class ModelInstantiationError(ShapeError):
    """Error during model instance creation

    Raised when creating a typed model instance from API response data fails.
    """

    def __init__(
        self,
        message: str,
        field_name: str | None = None,
        expected_type: type | None = None,
        actual_value: Any = None,
    ):
        super().__init__(message)
        self.field_name = field_name
        self.expected_type = expected_type
        self.actual_value = actual_value
