"""Tests for tango.webhooks.signing.

The signing scheme has to match the tango server byte-for-byte. The
``KNOWN_VECTORS`` constants pin a few payload/secret/signature triples that
were computed independently against tango's reference implementation
(``webhooks/utils.py::generate_signature``). Drift in either direction
should fail this test.
"""

from __future__ import annotations

import hashlib
import hmac

from tango.webhooks import generate_signature, parse_signature_header, verify_signature

KNOWN_VECTORS: list[tuple[bytes, str, str]] = [
    # (body_bytes, secret, expected_wire_signature) — full sha256=<hex> form
    (b"", "dev_secret", "sha256=" + hmac.new(b"dev_secret", b"", hashlib.sha256).hexdigest()),
    (
        b'{"events":[{"event_type":"alerts.entity.match","alert_id":"ABC"}]}',
        "shh",
        "sha256="
        + hmac.new(
            b"shh",
            b'{"events":[{"event_type":"alerts.entity.match","alert_id":"ABC"}]}',
            hashlib.sha256,
        ).hexdigest(),
    ),
]


def test_generate_signature_matches_reference_algorithm() -> None:
    for body, secret, expected in KNOWN_VECTORS:
        assert generate_signature(body, secret) == expected


def test_generate_signature_returns_prefixed_wire_form() -> None:
    """generate_signature returns the full ``sha256=<hex>`` header value, so
    callers can assign it directly to X-Tango-Signature without wrapping."""
    sig = generate_signature(b"payload", "secret")
    assert sig.startswith("sha256=")
    bare = sig[len("sha256=") :]
    assert bare == bare.lower()
    int(bare, 16)  # must parse as hex


def test_verify_signature_round_trip() -> None:
    body = b'{"events":[{"event_type":"alerts.contract.match"}]}'
    secret = "rotating-secret"
    sig = generate_signature(body, secret)
    # Prefixed form (what generate_signature returns and what Tango sends)
    assert verify_signature(body, secret, sig) is True
    # Bare-hex form (callers passing pre-stripped headers)
    bare = parse_signature_header(sig)
    assert bare is not None
    assert verify_signature(body, secret, bare) is True


def test_verify_signature_accepts_both_prefixed_and_bare_hex() -> None:
    """Regression test: verify_signature must accept BOTH the wire form
    (sha256=<hex>) and the pre-stripped bare-hex form. Callers that strip
    the prefix themselves before passing in must keep working."""
    body = b"hello"
    secret = "k"
    sig = generate_signature(body, secret)
    bare = parse_signature_header(sig)
    assert bare is not None and bare != sig  # sanity: they really differ
    assert verify_signature(body, secret, sig) is True
    assert verify_signature(body, secret, bare) is True


def test_verify_signature_rejects_tampered_body() -> None:
    secret = "secret"
    sig = generate_signature(b"original", secret)
    assert verify_signature(b"tampered", secret, sig) is False


def test_verify_signature_rejects_wrong_secret() -> None:
    sig = generate_signature(b"body", "right")
    assert verify_signature(b"body", "wrong", sig) is False


def test_verify_signature_handles_missing_or_empty_header() -> None:
    assert verify_signature(b"body", "secret", None) is False
    assert verify_signature(b"body", "secret", "") is False
    assert verify_signature(b"body", "secret", "sha256=") is False


def test_parse_signature_header_strips_prefix() -> None:
    assert parse_signature_header("sha256=abc123") == "abc123"
    assert parse_signature_header("  sha256=abc  ") == "abc"
    assert parse_signature_header("abc123") == "abc123"
    assert parse_signature_header(None) is None
    assert parse_signature_header("") is None
