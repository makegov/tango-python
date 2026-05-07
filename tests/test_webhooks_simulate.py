"""Tests for tango.webhooks.simulate.deliver."""

from __future__ import annotations

from tango.webhooks import simulate
from tango.webhooks.receiver import WebhookReceiver

SECRET = "shared"


def test_deliver_signs_and_posts_dict_payload() -> None:
    payload = {"events": [{"event_type": "awards.created", "award_key": "X"}]}
    with WebhookReceiver(secret=SECRET).run() as rx:
        result = simulate.deliver(target_url=rx.url, payload=payload, secret=SECRET)
        assert result.status_code == 200
        assert len(result.signature) == 64  # hex sha256
        # Receiver verified the signature, so the bytes round-tripped intact.
        assert rx.deliveries[0].verified is True
        assert rx.deliveries[0].body_json == payload


def test_deliver_accepts_raw_bytes() -> None:
    raw = b'{"events":[{"event_type":"x"}]}'
    with WebhookReceiver(secret=SECRET).run() as rx:
        result = simulate.deliver(target_url=rx.url, payload=raw, secret=SECRET)
        assert result.status_code == 200
        assert result.sent_bytes == raw


def test_deliver_dict_serialization_is_deterministic() -> None:
    """Same dict in two calls produces the same signature (sort_keys + compact)."""
    payload = {"b": 2, "a": 1}
    with WebhookReceiver(secret=SECRET).run() as rx:
        first = simulate.deliver(target_url=rx.url, payload=payload, secret=SECRET)
        second = simulate.deliver(target_url=rx.url, payload=payload, secret=SECRET)
        assert first.signature == second.signature
        assert first.sent_bytes == second.sent_bytes


def test_deliver_wrong_secret_yields_401() -> None:
    with WebhookReceiver(secret=SECRET).run() as rx:
        result = simulate.deliver(target_url=rx.url, payload={"x": 1}, secret="not-the-secret")
        assert result.status_code == 401
