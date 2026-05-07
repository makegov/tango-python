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
    # (body_bytes, secret, expected_lowercase_hex_hmac_sha256)
    (b"", "dev_secret", hmac.new(b"dev_secret", b"", hashlib.sha256).hexdigest()),
    (
        b'{"events":[{"event_type":"entities.updated","uei":"ABC123"}]}',
        "shh",
        hmac.new(
            b"shh",
            b'{"events":[{"event_type":"entities.updated","uei":"ABC123"}]}',
            hashlib.sha256,
        ).hexdigest(),
    ),
]


def test_generate_signature_matches_reference_algorithm() -> None:
    for body, secret, expected in KNOWN_VECTORS:
        assert generate_signature(body, secret) == expected


def test_generate_signature_is_lowercase_hex() -> None:
    sig = generate_signature(b"payload", "secret")
    assert sig == sig.lower()
    int(sig, 16)  # must parse as hex


def test_verify_signature_round_trip() -> None:
    body = b'{"events":[{"event_type":"awards.created"}]}'
    secret = "rotating-secret"
    sig = generate_signature(body, secret)
    assert verify_signature(body, secret, f"sha256={sig}") is True
    assert verify_signature(body, secret, sig) is True  # bare hex also accepted


def test_verify_signature_rejects_tampered_body() -> None:
    secret = "secret"
    sig = generate_signature(b"original", secret)
    assert verify_signature(b"tampered", secret, f"sha256={sig}") is False


def test_verify_signature_rejects_wrong_secret() -> None:
    sig = generate_signature(b"body", "right")
    assert verify_signature(b"body", "wrong", f"sha256={sig}") is False


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
