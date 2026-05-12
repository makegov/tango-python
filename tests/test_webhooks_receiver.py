"""Tests for tango.webhooks.receiver.WebhookReceiver."""

from __future__ import annotations

import json

import httpx
import pytest

from tango.webhooks import generate_signature
from tango.webhooks.receiver import WebhookReceiver

SECRET = "test_secret"
PAYLOAD = {"events": [{"event_type": "entities.updated", "uei": "TEST123"}]}


def _post_signed(url: str, body: bytes, secret: str) -> httpx.Response:
    # generate_signature returns the wire form ("sha256=<hex>") so it can
    # be assigned to the header directly with no wrapping.
    return httpx.post(
        url,
        content=body,
        headers={
            "Content-Type": "application/json",
            "X-Tango-Signature": generate_signature(body, secret),
        },
        timeout=5.0,
    )


def test_receiver_records_verified_delivery() -> None:
    body = json.dumps(PAYLOAD).encode("utf-8")
    with WebhookReceiver(secret=SECRET).run() as rx:
        resp = _post_signed(rx.url, body, SECRET)
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "application/json"
        assert resp.json() == {"ok": True}
        assert rx.deliveries[0].verified is True
        assert rx.deliveries[0].body_bytes == body
        assert rx.deliveries[0].body_json == PAYLOAD


def test_receiver_rejects_bad_signature_with_401() -> None:
    body = json.dumps(PAYLOAD).encode("utf-8")
    with WebhookReceiver(secret=SECRET).run() as rx:
        resp = httpx.post(
            rx.url,
            content=body,
            headers={"X-Tango-Signature": "sha256=deadbeef"},
            timeout=5.0,
        )
        assert resp.status_code == 401
        assert resp.headers["content-type"] == "application/json"
        assert resp.json() == {"ok": False, "error": "invalid_signature"}
        # The bad delivery is still recorded, marked unverified, so devs
        # can debug what arrived.
        assert len(rx.deliveries) == 1
        assert rx.deliveries[0].verified is False


def test_receiver_rejects_missing_signature_with_401() -> None:
    body = json.dumps(PAYLOAD).encode("utf-8")
    with WebhookReceiver(secret=SECRET).run() as rx:
        resp = httpx.post(rx.url, content=body, timeout=5.0)
        assert resp.status_code == 401


def test_receiver_with_no_secret_accepts_unsigned() -> None:
    body = json.dumps(PAYLOAD).encode("utf-8")
    with WebhookReceiver(secret="").run() as rx:
        resp = httpx.post(rx.url, content=body, timeout=5.0)
        assert resp.status_code == 200
        assert rx.deliveries[0].verified is False


def test_receiver_404s_on_unknown_path() -> None:
    with WebhookReceiver(secret=SECRET, path="/tango/webhooks").run() as rx:
        wrong = rx.url.replace("/tango/webhooks", "/elsewhere")
        resp = httpx.post(wrong, content=b"{}", timeout=5.0)
        assert resp.status_code == 404
        assert resp.headers["content-type"] == "application/json"
        assert resp.json() == {"ok": False, "error": "not_found"}


def test_receiver_invokes_on_delivery_callback() -> None:
    seen: list[str] = []
    body = json.dumps(PAYLOAD).encode("utf-8")
    with WebhookReceiver(
        secret=SECRET, on_delivery=lambda d: seen.append(d.body_bytes.decode())
    ).run() as rx:
        _post_signed(rx.url, body, SECRET)
    assert seen == [body.decode()]


def test_receiver_max_history_caps_deliveries() -> None:
    body = json.dumps(PAYLOAD).encode("utf-8")
    with WebhookReceiver(secret=SECRET, max_history=3).run() as rx:
        for _ in range(5):
            _post_signed(rx.url, body, SECRET)
        assert len(rx.deliveries) == 3


def test_receiver_forwards_to_downstream() -> None:
    body = json.dumps(PAYLOAD).encode("utf-8")
    with WebhookReceiver(secret=SECRET, max_history=10).run() as downstream:
        with WebhookReceiver(secret=SECRET, forward_to=downstream.url, port=0).run() as upstream:
            resp = _post_signed(upstream.url, body, SECRET)
            assert resp.status_code == 200
        # Downstream should have received the same bytes with the same signature.
        assert len(downstream.deliveries) == 1
        assert downstream.deliveries[0].body_bytes == body
        assert downstream.deliveries[0].verified is True


def test_url_property_raises_before_start() -> None:
    rx = WebhookReceiver(secret=SECRET)
    with pytest.raises(RuntimeError):
        _ = rx.url


def test_double_start_raises() -> None:
    rx = WebhookReceiver(secret=SECRET)
    rx.start()
    try:
        with pytest.raises(RuntimeError):
            rx.start()
    finally:
        rx.stop()
