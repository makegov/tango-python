"""Local webhook receiver for development and integration testing.

A small stdlib-based HTTP server that accepts Tango-style POSTs, verifies
the ``X-Tango-Signature`` header against a shared secret, optionally
forwards the request to a downstream URL (e.g. your real handler running on
another port), and records each delivery in memory for later inspection.

Typical use from the CLI::

    tango webhooks listen --port 8011 --secret $TANGO_WEBHOOK_SECRET \\
        --forward-to http://localhost:4242/webhooks

Or programmatically inside an integration test::

    from tango.webhooks import WebhookReceiver

    with WebhookReceiver(secret="dev_secret").run() as rx:
        # ... cause a webhook to fire at rx.url ...
        deliveries = rx.deliveries
"""

from __future__ import annotations

import contextlib
import json
import threading
from collections import deque
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
from datetime import UTC, datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from tango.webhooks.signing import SIGNATURE_HEADER, verify_signature

DEFAULT_PATH = "/tango/webhooks"
DEFAULT_MAX_HISTORY = 256


@dataclass
class Delivery:
    """A recorded webhook delivery."""

    received_at: str
    path: str
    signature_header: str | None
    body_bytes: bytes
    body_json: Any
    verified: bool
    remote_addr: str | None = None
    forward_status: int | None = None
    forward_error: str | None = None


@dataclass
class WebhookReceiver:
    """A configurable local receiver for Tango webhook deliveries.

    Args:
        secret: Shared secret. If empty, signatures are not verified and
            every delivery is recorded with ``verified=False`` — useful for
            inspecting payloads without a configured endpoint.
        path: URL path to accept deliveries on. Defaults to ``/tango/webhooks``.
        host: Bind address. Defaults to ``127.0.0.1`` (loopback only).
        port: TCP port. ``0`` lets the OS choose a free port.
        forward_to: Optional URL to mirror each delivery to, preserving body
            bytes and the signature header.
        max_history: Cap on the in-memory ``deliveries`` deque.
        on_delivery: Optional callback invoked for each recorded delivery.
        require_signature: If True (the default when a secret is set),
            unsigned or invalid deliveries get a 401 response.
    """

    secret: str = ""
    path: str = DEFAULT_PATH
    host: str = "127.0.0.1"
    port: int = 0
    forward_to: str | None = None
    max_history: int = DEFAULT_MAX_HISTORY
    on_delivery: Callable[[Delivery], None] | None = None
    require_signature: bool | None = None

    _server: ThreadingHTTPServer | None = field(default=None, init=False, repr=False)
    _thread: threading.Thread | None = field(default=None, init=False, repr=False)
    _deliveries: deque[Delivery] = field(default_factory=deque, init=False, repr=False)

    @property
    def deliveries(self) -> list[Delivery]:
        """Snapshot of recorded deliveries, oldest first."""
        return list(self._deliveries)

    @property
    def url(self) -> str:
        """Full URL the receiver is bound to (only valid while running)."""
        if self._server is None:
            raise RuntimeError("Receiver is not running")
        host_addr, port = self._server.server_address[:2]
        host = host_addr.decode() if isinstance(host_addr, bytes) else str(host_addr)
        return f"http://{host}:{port}{self.path}"

    def start(self) -> None:
        """Bind the socket and start serving in a background thread."""
        if self._server is not None:
            raise RuntimeError("Receiver already started")
        receiver = self
        deliveries = self._deliveries
        max_history = self.max_history

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
                # Suppress stderr access logging; users see deliveries through
                # the on_delivery callback or the deliveries list instead.
                return

            def do_POST(self) -> None:  # noqa: N802 (stdlib API)
                if self.path != receiver.path:
                    self.send_error(404, "Not Found")
                    return
                length = int(self.headers.get("Content-Length", "0") or 0)
                body = self.rfile.read(length) if length > 0 else b""
                signature = self.headers.get(SIGNATURE_HEADER)
                verified = bool(receiver.secret) and verify_signature(
                    body, receiver.secret, signature
                )

                require = (
                    receiver.require_signature
                    if receiver.require_signature is not None
                    else bool(receiver.secret)
                )
                if require and not verified:
                    self._record(body, signature, verified=False)
                    self.send_error(401, "Invalid signature")
                    return

                forward_status: int | None = None
                forward_error: str | None = None
                if receiver.forward_to:
                    forward_status, forward_error = _forward(receiver.forward_to, body, signature)

                self._record(
                    body,
                    signature,
                    verified=verified,
                    forward_status=forward_status,
                    forward_error=forward_error,
                )
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(b'{"ok": true}')

            def _record(
                self,
                body: bytes,
                signature: str | None,
                *,
                verified: bool,
                forward_status: int | None = None,
                forward_error: str | None = None,
            ) -> None:
                try:
                    parsed: Any = json.loads(body.decode("utf-8")) if body else None
                except (UnicodeDecodeError, json.JSONDecodeError):
                    parsed = None
                delivery = Delivery(
                    received_at=datetime.now(UTC).isoformat().replace("+00:00", "Z"),
                    path=self.path,
                    signature_header=signature,
                    body_bytes=body,
                    body_json=parsed,
                    verified=verified,
                    remote_addr=self.client_address[0] if self.client_address else None,
                    forward_status=forward_status,
                    forward_error=forward_error,
                )
                while len(deliveries) >= max_history:
                    deliveries.popleft()
                deliveries.append(delivery)
                if receiver.on_delivery is not None:
                    receiver.on_delivery(delivery)

        self._server = ThreadingHTTPServer((self.host, self.port), Handler)
        self._thread = threading.Thread(
            target=self._server.serve_forever,
            name="tango-webhook-receiver",
            daemon=True,
        )
        self._thread.start()

    def stop(self) -> None:
        """Stop the server and join the background thread."""
        if self._server is None:
            return
        self._server.shutdown()
        self._server.server_close()
        if self._thread is not None:
            self._thread.join(timeout=5)
        self._server = None
        self._thread = None

    @contextlib.contextmanager
    def run(self) -> Iterator[WebhookReceiver]:
        """Context manager that starts the receiver and stops it on exit."""
        self.start()
        try:
            yield self
        finally:
            self.stop()


def _forward(url: str, body: bytes, signature: str | None) -> tuple[int | None, str | None]:
    """POST ``body`` to ``url`` preserving the signature header.

    Returns ``(status, error_message)``. httpx is imported lazily so unit
    tests that don't exercise forwarding don't pay the import cost.
    """
    import httpx

    headers = {"Content-Type": "application/json"}
    if signature:
        headers[SIGNATURE_HEADER] = signature
    try:
        resp = httpx.post(url, content=body, headers=headers, timeout=10.0)
    except httpx.HTTPError as exc:
        return None, str(exc)
    return resp.status_code, None
