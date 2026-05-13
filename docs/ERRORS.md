# Error Handling

The SDK raises typed exceptions for HTTP errors and for shape-related failures. All exceptions are importable from `tango.exceptions` (and re-exported from the top-level `tango` package for the API errors).

For a compact reference of each class, see [`API_REFERENCE.md` § Error Handling](API_REFERENCE.md#error-handling). This guide covers the hierarchy, recovery patterns, and the shape-error classes that don't have a dedicated section there.

## Exception Hierarchy

```
TangoAPIError
├── TangoAuthError           (401 Unauthorized)
├── TangoNotFoundError       (404 Not Found)
├── TangoValidationError     (400 Bad Request)
├── TangoRateLimitError      (429 Too Many Requests)
└── ShapeError
    ├── ShapeValidationError    (invalid field names)
    ├── ShapeParseError         (invalid shape syntax)
    ├── TypeGenerationError     (dynamic type generation failure)
    └── ModelInstantiationError (model creation failure)
```

## API Errors

### TangoAPIError (base)

All API errors inherit from this class.

| Attribute | Type | Description |
|---|---|---|
| `status_code` | `int \| None` | HTTP status code |
| `response_data` | `dict` | Parsed response body (credentials redacted) |
| `message` | `str` | Human-readable error message |

```python
from tango import TangoClient
from tango.exceptions import TangoAPIError

client = TangoClient()

try:
    resp = client.list_contracts(limit=10)
except TangoAPIError as e:
    print(f"API error {e.status_code}: {e.message}")
```

### TangoAuthError (401)

Raised when the API key is missing, invalid, or expired.

```python
from tango.exceptions import TangoAuthError

try:
    client = TangoClient(api_key="invalid-key")
    client.list_contracts(limit=1)
except TangoAuthError:
    print("Check your API key")
```

### TangoNotFoundError (404)

Raised when a resource doesn't exist.

```python
from tango.exceptions import TangoNotFoundError

try:
    entity = client.get_entity("INVALID_UEI")
except TangoNotFoundError:
    print("Entity not found")
```

### TangoValidationError (400)

Raised for invalid request parameters (bad date format, unknown filter, etc.).

### TangoRateLimitError (429)

Raised when you exceed rate limits. Includes retry information.

| Attribute | Type | Description |
|---|---|---|
| `wait_in_seconds` | `int \| None` | Seconds to wait before retrying |
| `detail` | `str \| None` | Human-readable rate limit message |
| `limit_type` | `str \| None` | `"burst"` or `"daily"` |

```python
import time
from tango.exceptions import TangoRateLimitError

try:
    resp = client.list_contracts(limit=10)
except TangoRateLimitError as e:
    if e.wait_in_seconds:
        print(f"Rate limited ({e.limit_type}). Retrying in {e.wait_in_seconds}s...")
        time.sleep(e.wait_in_seconds)
        resp = client.list_contracts(limit=10)
```

> **Note:** The SDK does not include built-in retry or backoff. You are responsible for handling rate limit errors. See the [Rate Limits guide](https://docs.makegov.com/guides/patterns/rate-limits/) for strategies.

## Shape Errors

These are raised when there's a problem with the response shaping configuration, not the API itself. See [`SHAPES.md`](SHAPES.md) for shape syntax.

### ShapeValidationError

Raised when a shape string references field names that don't exist on the model.

```python
from tango.exceptions import ShapeValidationError

try:
    resp = client.list_contracts(shape="key,piid,nonexistent_field", limit=1)
except ShapeValidationError as e:
    print(f"Invalid shape: {e}")
    print(f"Shape string: {e.shape}")
```

### ShapeParseError

Raised when the shape string has invalid syntax (unbalanced parentheses, etc.).

| Attribute | Type | Description |
|---|---|---|
| `shape` | `str` | The invalid shape string |
| `position` | `int \| None` | Character position where parsing failed |

### TypeGenerationError

Raised when the SDK fails to generate a dynamic TypedDict for a shaped response.

### ModelInstantiationError

Raised when the SDK fails to create a model instance from API data.

| Attribute | Type | Description |
|---|---|---|
| `field_name` | `str \| None` | Field that caused the failure |
| `expected_type` | `type \| None` | Expected Python type |
| `actual_value` | `Any` | Value that couldn't be coerced |

## Catching Everything

To handle any SDK-raised error in one place, catch `TangoAPIError` and `ShapeError` (or just `Exception` at the outermost boundary):

```python
from tango.exceptions import TangoAPIError, ShapeError

try:
    resp = client.list_contracts(shape="key,piid", limit=10)
except TangoAPIError as e:
    # HTTP-layer problems (auth, rate limit, validation, etc.)
    print(f"API error {e.status_code}: {e.message}")
except ShapeError as e:
    # Shape-string or model-construction problems
    print(f"Shape error: {e}")
```
