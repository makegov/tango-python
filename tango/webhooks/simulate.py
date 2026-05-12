"""Locally sign and POST a webhook payload to a URL.

This module is the offline counterpart to ``test_webhook_delivery``: it
never talks to the Tango API. Use it when you want to drive a downstream
receiver without provisioning a real alert, or when you want to
fuzz event shapes that Tango wouldn't naturally emit.

Example::

    from tango.webhooks import simulate

    result = simulate.deliver(
        target_url="http://localhost:4242/webhooks",
        payload={"events": [{"event_type": "entities.updated", "uei": "ABC123"}]},
        secret="dev_secret",
    )
    assert result.status_code == 200
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from tango.webhooks.signing import SIGNATURE_HEADER, generate_signature, parse_signature_header


@dataclass(frozen=True)
class SignedRequest:
    """A Tango-shaped signed request, ready to be POSTed."""

    body: bytes
    signature: str  # bare lowercase hex (header-prefix stripped)
    headers: dict[str, str]  # includes Content-Type and X-Tango-Signature


@dataclass(frozen=True)
class SimulationResult:
    """Outcome of a simulated delivery."""

    status_code: int
    response_body: str
    signature: str
    sent_bytes: bytes


def sign(payload: dict[str, Any] | list[Any] | bytes | str, secret: str) -> SignedRequest:
    """Serialize and sign ``payload`` without sending it.

    Useful for showing devs the exact wire form their handler would
    receive, or for hand-rolling deliveries with a custom HTTP client.
    """
    body = _to_bytes(payload)
    header_value = generate_signature(body, secret)
    bare_hex = parse_signature_header(header_value) or ""
    return SignedRequest(
        body=body,
        signature=bare_hex,
        headers={
            "Content-Type": "application/json",
            SIGNATURE_HEADER: header_value,
        },
    )


def deliver(
    *,
    target_url: str,
    payload: dict[str, Any] | list[Any] | bytes | str,
    secret: str,
    extra_headers: dict[str, str] | None = None,
    timeout: float = 10.0,
) -> SimulationResult:
    """Sign ``payload`` with ``secret`` and POST it to ``target_url``.

    ``payload`` may be a ``dict``/``list`` (serialized via :func:`json.dumps`
    with ``sort_keys=True`` to keep signatures reproducible across runs),
    a pre-serialized ``str``, or raw ``bytes``. Signing is computed over the
    exact bytes that go on the wire.
    """
    import httpx

    signed = sign(payload, secret)
    headers = dict(signed.headers)
    if extra_headers:
        headers.update(extra_headers)

    resp = httpx.post(target_url, content=signed.body, headers=headers, timeout=timeout)
    return SimulationResult(
        status_code=resp.status_code,
        response_body=resp.text,
        signature=signed.signature,
        sent_bytes=signed.body,
    )


def _to_bytes(payload: dict[str, Any] | list[Any] | bytes | str) -> bytes:
    if isinstance(payload, bytes):
        return payload
    if isinstance(payload, str):
        return payload.encode("utf-8")
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
