"""Smoke tests for the `tango webhooks` CLI."""

from __future__ import annotations

import json

from click.testing import CliRunner

from tango.webhooks.cli import main
from tango.webhooks.receiver import WebhookReceiver


def test_cli_help() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["webhooks", "--help"])
    assert result.exit_code == 0
    assert "listen" in result.output
    assert "trigger" in result.output
    assert "simulate" in result.output
    assert "fetch-sample" in result.output
    assert "list-event-types" in result.output


def test_cli_simulate_without_to_prints_signed_request() -> None:
    """Without --to, simulate signs and prints — no POST, no listener required."""
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["webhooks", "simulate", "--secret", "dev"],
    )
    assert result.exit_code == 0, result.output
    body = json.loads(result.output)
    assert body["delivered"] is False
    assert body["headers"]["Content-Type"] == "application/json"
    assert body["headers"]["X-Tango-Signature"].startswith("sha256=")
    assert "events" in body["sent_payload"]


def test_cli_simulate_signs_and_posts(tmp_path: object) -> None:
    runner = CliRunner()
    secret = "cli-secret"
    payload = {"events": [{"event_type": "cli.smoke"}]}
    with WebhookReceiver(secret=secret).run() as rx:
        result = runner.invoke(
            main,
            [
                "webhooks",
                "simulate",
                "--to",
                rx.url,
                "--secret",
                secret,
            ],
            input=json.dumps(payload),  # ignored by current command, harmless
        )
        assert result.exit_code == 0, result.output
        # The default body is the built-in placeholder envelope.
        assert len(rx.deliveries) == 1
        assert rx.deliveries[0].verified is True
        body = json.loads(result.output)
        assert body["delivered"] is True
        assert body["status_code"] == 200
        assert body["signature"].startswith("sha256=")
        assert body["target_url"] == rx.url
        # Output now includes the actual payload that was sent (the dev's
        # main artifact of interest), not just its byte length.
        assert isinstance(body["sent_payload"], dict)
        assert "events" in body["sent_payload"]
        assert body["receiver_response"] == '{"ok": true}'


def test_cli_simulate_with_payload_file(tmp_path: object) -> None:
    import pathlib

    p = pathlib.Path(str(tmp_path)) / "payload.json"
    payload = {"events": [{"event_type": "from.file", "subject_ids": ["S1"]}]}
    p.write_text(json.dumps(payload), encoding="utf-8")

    runner = CliRunner()
    secret = "file-secret"
    with WebhookReceiver(secret=secret).run() as rx:
        result = runner.invoke(
            main,
            [
                "webhooks",
                "simulate",
                "--to",
                rx.url,
                "--secret",
                secret,
                "--payload-file",
                str(p),
            ],
        )
        assert result.exit_code == 0, result.output
        assert rx.deliveries[0].body_json == payload


def test_cli_fetch_sample_prints_payload() -> None:
    """fetch-sample hits the SDK's get_webhook_sample_payload and pretty-prints."""
    from unittest.mock import Mock, patch

    sample = {"events": [{"event_type": "entities.updated", "uei": "ABC"}]}
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.headers = {}
    mock_response.json.return_value = sample
    mock_response.raise_for_status = Mock()

    runner = CliRunner()
    with patch("tango.client.httpx.Client.request", return_value=mock_response):
        result = runner.invoke(
            main,
            [
                "webhooks",
                "fetch-sample",
                "--event-type",
                "entities.updated",
                "--api-key",
                "k",
            ],
        )
    assert result.exit_code == 0, result.output
    assert json.loads(result.output) == sample


def test_cli_list_event_types_prints_table() -> None:
    from unittest.mock import Mock, patch

    api_response = {
        "event_types": [
            {
                "event_type": "entities.updated",
                "default_subject_type": "entity",
                "description": "Entity updated",
                "schema_version": 1,
            },
            {
                "event_type": "awards.created",
                "default_subject_type": "award",
                "description": "New award",
                "schema_version": 1,
            },
        ],
        "subject_types": [],
        "subject_type_definitions": [],
    }
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.headers = {}
    mock_response.json.return_value = api_response
    mock_response.raise_for_status = Mock()

    runner = CliRunner()
    with patch("tango.client.httpx.Client.request", return_value=mock_response):
        result = runner.invoke(main, ["webhooks", "list-event-types", "--api-key", "k"])
    assert result.exit_code == 0, result.output
    assert "entities.updated" in result.output
    assert "Entity updated" in result.output
    assert "awards.created" in result.output


def test_cli_simulate_rejects_both_modes() -> None:
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "webhooks",
            "simulate",
            "--to",
            "http://example.invalid/",
            "--secret",
            "x",
            "--payload-file",
            "/dev/null",
            "--event-type",
            "entities.updated",
        ],
    )
    assert result.exit_code != 0
    assert "either --payload-file or --event-type" in result.output
