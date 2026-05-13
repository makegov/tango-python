# Client Configuration

`TangoClient` is the entry point for every API call. This guide covers the constructor, the rate-limit and response-inspection properties, and how the client handles authentication and transport.

For per-method signatures, see [`API_REFERENCE.md`](API_REFERENCE.md). For error handling, see [`ERRORS.md`](ERRORS.md). For shaping responses, see [`SHAPES.md`](SHAPES.md).

## Constructor

```python
from tango import TangoClient

client = TangoClient(
    api_key="your-api-key",           # or set TANGO_API_KEY env var
    base_url="https://tango.makegov.com",  # default
    user_agent="my-app/1.0",          # optional custom User-Agent
    extra_headers={"X-Custom": "val"},  # optional additional headers
)
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `api_key` | `str \| None` | `None` | API key. Falls back to `TANGO_API_KEY` environment variable. |
| `base_url` | `str` | `"https://tango.makegov.com"` | Base URL for the Tango API. |
| `user_agent` | `str \| None` | `None` | Custom User-Agent string appended to the default. |
| `extra_headers` | `dict[str, str] \| None` | `None` | Additional HTTP headers sent with every request. |

The client uses [httpx](https://www.python-httpx.org/) under the hood with a 30-second timeout. The API key is sent as an `X-API-KEY` header on every request.

## Properties

### `rate_limit_info`

Returns rate limit information from the most recent API response.

```python
resp = client.list_contracts(limit=5)
info = client.rate_limit_info

if info:
    print(f"Remaining: {info.remaining}/{info.limit}")
    print(f"Resets in: {info.reset}s")
    print(f"Daily remaining: {info.daily_remaining}/{info.daily_limit}")
```

The `RateLimitInfo` object exposes:

| Field | Type | Description |
|---|---|---|
| `limit` | `int \| None` | Request limit for the current window |
| `remaining` | `int \| None` | Requests remaining in the current window |
| `reset` | `int \| None` | Seconds until the window resets |
| `daily_limit` | `int \| None` | Daily request limit |
| `daily_remaining` | `int \| None` | Daily requests remaining |
| `daily_reset` | `int \| None` | Seconds until the daily limit resets |
| `burst_limit` | `int \| None` | Burst request limit |
| `burst_remaining` | `int \| None` | Burst requests remaining |
| `burst_reset` | `int \| None` | Seconds until the burst limit resets |

### `last_response_headers`

Returns the full HTTP headers from the most recent API response, as an `httpx.Headers` object.

```python
resp = client.list_contracts(limit=5)
headers = client.last_response_headers
print(headers["content-type"])
```

## Retry Semantics

The SDK does **not** include built-in retry or backoff. Each method call maps to exactly one HTTP request. If you need retry-on-429 or retry-on-transient-error behavior, wrap your calls (or catch [`TangoRateLimitError`](ERRORS.md#tangoratelimiterror-429) and use `wait_in_seconds`).

See the [Rate Limits guide](https://docs.makegov.com/guides/patterns/rate-limits/) for recommended strategies.
