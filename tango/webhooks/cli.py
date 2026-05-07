"""Command-line interface for Tango webhook tooling.

This module is the entry point for the ``tango`` console script. Click is an
optional dependency installed via the ``tango[webhooks]`` extra; importing
this module without it raises a friendly error that points users at the
right install command.
"""

from __future__ import annotations

import json
import sys
import threading
from pathlib import Path
from typing import Any

try:
    import click
except ImportError as _import_error:  # pragma: no cover - tested via subprocess
    sys.stderr.write(
        "tango CLI requires the 'webhooks' extra. Install it with:\n"
        "    pip install 'tango-python[webhooks]'\n"
    )
    raise SystemExit(1) from _import_error

from tango.webhooks import simulate
from tango.webhooks.receiver import Delivery, WebhookReceiver
from tango.webhooks.signing import SIGNATURE_HEADER


@click.group()
@click.version_option(package_name="tango-python", prog_name="tango")
def main() -> None:
    """Tango developer tooling."""


@main.group()
def webhooks() -> None:
    """Receive, trigger, and simulate Tango webhook deliveries."""


@webhooks.command("listen")
@click.option("--port", type=int, default=8011, show_default=True, help="TCP port to bind.")
@click.option("--host", default="127.0.0.1", show_default=True, help="Bind address.")
@click.option(
    "--path",
    default="/tango/webhooks",
    show_default=True,
    help="URL path to accept deliveries on.",
)
@click.option(
    "--secret",
    envvar="TANGO_WEBHOOK_SECRET",
    default="",
    help="Shared secret. Reads TANGO_WEBHOOK_SECRET if unset. "
    "If empty, deliveries are accepted without signature verification.",
)
@click.option(
    "--forward-to",
    default=None,
    help="Optional URL to mirror each delivery to (preserves body and signature).",
)
@click.option(
    "--require-signature/--allow-unsigned",
    default=None,
    help="Override default policy. Default: require when --secret is set.",
)
def listen_cmd(
    port: int,
    host: str,
    path: str,
    secret: str,
    forward_to: str | None,
    require_signature: bool | None,
) -> None:
    """Run a local receiver and stream deliveries to stdout."""
    receiver = WebhookReceiver(
        secret=secret,
        path=path,
        host=host,
        port=port,
        forward_to=forward_to,
        require_signature=require_signature,
        on_delivery=_print_delivery,
    )
    receiver.start()
    try:
        click.echo(f"Listening on {receiver.url}")
        if not secret:
            click.echo(
                "  WARNING: no --secret provided; signatures will not be verified.",
                err=True,
            )
        if forward_to:
            click.echo(f"  Forwarding to {forward_to}")
        click.echo("  Press Ctrl+C to stop.")
        threading.Event().wait()  # block until interrupted
    except KeyboardInterrupt:
        click.echo("\nStopping...")
    finally:
        receiver.stop()


@webhooks.command("trigger")
@click.option(
    "--endpoint-id",
    default=None,
    help="Endpoint UUID. If omitted, the server's default endpoint is used.",
)
@click.option(
    "--api-key",
    envvar="TANGO_API_KEY",
    help="Tango API key (or set TANGO_API_KEY).",
)
@click.option(
    "--base-url",
    envvar="TANGO_BASE_URL",
    default="https://tango.makegov.com",
    show_default=True,
    help="Tango base URL (or set TANGO_BASE_URL).",
)
def trigger_cmd(endpoint_id: str | None, api_key: str | None, base_url: str) -> None:
    """Ask Tango to send a real test delivery to your configured endpoint."""
    from tango import TangoClient

    client = TangoClient(api_key=api_key, base_url=base_url)
    result = client.test_webhook_delivery(endpoint_id=endpoint_id)
    click.echo(
        json.dumps(
            {
                "success": result.success,
                "status_code": result.status_code,
                "response_time_ms": result.response_time_ms,
                "endpoint_url": result.endpoint_url,
                "message": result.message,
                "error": result.error,
            },
            indent=2,
        )
    )
    if not result.success:
        raise SystemExit(1)


@webhooks.command("simulate")
@click.option(
    "--to",
    "target_url",
    default=None,
    help="Receiver URL to POST to. If omitted, the signed request is printed but not sent.",
)
@click.option(
    "--secret",
    envvar="TANGO_WEBHOOK_SECRET",
    required=True,
    help="Shared secret used to sign the payload (or TANGO_WEBHOOK_SECRET).",
)
@click.option(
    "--payload-file",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    default=None,
    help="Path to a JSON file with the body to send. Mutually exclusive with --event-type.",
)
@click.option(
    "--event-type",
    default=None,
    help="Fetch a canonical sample for this event type from Tango and send that.",
)
@click.option(
    "--api-key",
    envvar="TANGO_API_KEY",
    help="Tango API key, only needed with --event-type (or TANGO_API_KEY).",
)
@click.option(
    "--base-url",
    envvar="TANGO_BASE_URL",
    default="https://tango.makegov.com",
    show_default=True,
    help="Tango base URL, only needed with --event-type.",
)
def simulate_cmd(
    target_url: str | None,
    secret: str,
    payload_file: Path | None,
    event_type: str | None,
    api_key: str | None,
    base_url: str,
) -> None:
    """Sign a payload like Tango would. With --to, also POST it to a receiver."""
    if payload_file and event_type:
        raise click.UsageError("Use either --payload-file or --event-type, not both.")

    payload: dict[str, Any] | list[Any]
    if payload_file:
        payload = json.loads(payload_file.read_text(encoding="utf-8"))
    elif event_type:
        from tango import TangoClient

        client = TangoClient(api_key=api_key, base_url=base_url)
        payload = client.get_webhook_sample_payload(event_type=event_type)
    else:
        payload = {"events": [{"event_type": "tango.cli.simulated", "subject_ids": []}]}

    if target_url is None:
        signed = simulate.sign(payload, secret)
        click.echo(
            json.dumps(
                {
                    "delivered": False,
                    "headers": signed.headers,
                    "sent_payload": payload,
                },
                indent=2,
                sort_keys=True,
            )
        )
        return

    result = simulate.deliver(target_url=target_url, payload=payload, secret=secret)
    click.echo(
        json.dumps(
            {
                "delivered": True,
                "target_url": target_url,
                "status_code": result.status_code,
                "signature": f"sha256={result.signature}",
                "sent_payload": payload,
                "receiver_response": result.response_body[:500],
            },
            indent=2,
            sort_keys=True,
        )
    )
    if result.status_code >= 400:
        raise SystemExit(1)


@webhooks.command("fetch-sample")
@click.option(
    "--event-type",
    default=None,
    help="If set, fetch the canonical sample for that event type. "
    "Otherwise return the full samples mapping for every event type.",
)
@click.option(
    "--api-key",
    envvar="TANGO_API_KEY",
    help="Tango API key (or TANGO_API_KEY).",
)
@click.option(
    "--base-url",
    envvar="TANGO_BASE_URL",
    default="https://tango.makegov.com",
    show_default=True,
    help="Tango base URL (or TANGO_BASE_URL).",
)
def fetch_sample_cmd(event_type: str | None, api_key: str | None, base_url: str) -> None:
    """Print the canonical sample payload Tango emits for a given event type."""
    from tango import TangoClient

    client = TangoClient(api_key=api_key, base_url=base_url)
    payload = client.get_webhook_sample_payload(event_type=event_type)
    click.echo(json.dumps(payload, indent=2, sort_keys=True))


@webhooks.command("list-event-types")
@click.option(
    "--api-key",
    envvar="TANGO_API_KEY",
    help="Tango API key (or TANGO_API_KEY).",
)
@click.option(
    "--base-url",
    envvar="TANGO_BASE_URL",
    default="https://tango.makegov.com",
    show_default=True,
    help="Tango base URL (or TANGO_BASE_URL).",
)
def list_event_types_cmd(api_key: str | None, base_url: str) -> None:
    """List webhook event types Tango supports, with descriptions."""
    from tango import TangoClient

    client = TangoClient(api_key=api_key, base_url=base_url)
    response = client.list_webhook_event_types()
    width = max((len(et.event_type) for et in response.event_types), default=0)
    for et in response.event_types:
        click.echo(f"{et.event_type:<{width}}  {et.description}")


def _print_delivery(delivery: Delivery) -> None:
    """Default ``listen`` callback: write a one-line summary plus body."""
    summary = _summarize(delivery.body_json)
    status = "verified" if delivery.verified else "UNVERIFIED"
    parts = [delivery.received_at, status, summary]
    if delivery.forward_status is not None:
        parts.append(f"forwarded={delivery.forward_status}")
    if delivery.forward_error:
        parts.append(f"forward_error={delivery.forward_error}")
    click.echo(" | ".join(parts))
    if delivery.body_json is not None:
        click.echo(json.dumps(delivery.body_json, indent=2, sort_keys=True))
    click.echo("")


def _summarize(body: Any) -> str:
    if isinstance(body, dict):
        events = body.get("events")
        if isinstance(events, list) and events and isinstance(events[0], dict):
            event_type = events[0].get("event_type", "?")
            count = len(events)
            return f"{event_type} (n={count})"
    return "(no events)"


# Make ``X-Tango-Signature`` accessible from this module for IDE completion.
__all__ = ["main", "SIGNATURE_HEADER"]
