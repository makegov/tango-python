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
        assert body["status_code"] == 200
        assert body["signature"].startswith("sha256=")


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
