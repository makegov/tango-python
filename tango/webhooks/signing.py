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
    """Return the wire-format signature for ``body`` keyed by ``secret``.

    Output is the full ``sha256=<lowercase hex>`` form Tango emits in the
    ``X-Tango-Signature`` header, so the return value can be assigned to
    the header directly without a wrapping format string. To get the bare
    hex digest, strip the prefix with :func:`parse_signature_header`.
    """
    digest = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    return f"{SIGNATURE_PREFIX}{digest}"


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

    Accepts both the prefixed form (``sha256=<hex>``) and the bare-hex form
    in ``signature_header`` — callers passing in pre-stripped headers keep
    working. Uses :func:`hmac.compare_digest` for constant-time comparison.
    Returns False for an absent or malformed header rather than raising —
    let callers decide how to respond (typically a 401 / 403).
    """
    received = parse_signature_header(signature_header)
    if not received:
        return False
    # generate_signature now returns the prefixed wire form; strip it for
    # the bare-hex comparison.
    expected = parse_signature_header(generate_signature(body, secret))
    if not expected:
        return False
    return hmac.compare_digest(expected, received)
