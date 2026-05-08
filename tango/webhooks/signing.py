"""HMAC-SHA256 signing for Tango webhook deliveries.

Tango signs each delivery with::

    X-Tango-Signature: sha256=<lowercase hex HMAC-SHA256 of raw body>

These helpers mirror the canonical implementation in the tango server
(``webhooks/utils.py``). Verifiers must operate on the **raw request body
bytes** — re-serializing parsed JSON will produce a different signature.
"""

from __future__ import annotations

import hashlib
import hmac

SIGNATURE_HEADER = "X-Tango-Signature"
SIGNATURE_PREFIX = "sha256="


def generate_signature(body: bytes, secret: str) -> str:
    """Return the lowercase hex HMAC-SHA256 of ``body`` keyed by ``secret``."""
    return hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()


def parse_signature_header(value: str | None) -> str | None:
    """Strip the ``sha256=`` prefix from a header value; return ``None`` if empty.

    Accepts the bare hex form too, for forward compatibility.
    """
    if not value:
        return None
    stripped = value.strip()
    if stripped.startswith(SIGNATURE_PREFIX):
        return stripped[len(SIGNATURE_PREFIX) :]
    return stripped


def verify_signature(body: bytes, secret: str, signature_header: str | None) -> bool:
    """Return True if ``signature_header`` matches the HMAC of ``body``.

    Uses :func:`hmac.compare_digest` for constant-time comparison.
    Returns False for an absent or malformed header rather than raising — let
    callers decide how to respond (typically a 401 / 403).
    """
    received = parse_signature_header(signature_header)
    if not received:
        return False
    expected = generate_signature(body, secret)
    return hmac.compare_digest(expected, received)
