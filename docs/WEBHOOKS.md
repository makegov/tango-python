# Webhooks Guide

This guide covers everything `tango-python` provides for **building, testing, and operating webhook integrations against the Tango API**: signing helpers, a local receiver, a command-line tool, and management commands for the underlying endpoints and subscriptions.

If you only need the SDK method signatures, see [`API_REFERENCE.md` § Webhooks](API_REFERENCE.md#webhooks). For the API-level contract (signing scheme, event taxonomy, retry behavior), see the [Tango Webhooks Partner Guide](https://docs.makegov.com/webhooks-user-guide/).

---

## Contents

- [Install](#install)
- [Concepts in 60 seconds](#concepts-in-60-seconds)
- [Quickstart: zero to receiving](#quickstart-zero-to-receiving)
- [CLI reference](#cli-reference)
  - [`tango webhooks listen`](#tango-webhooks-listen)
  - [`tango webhooks simulate`](#tango-webhooks-simulate)
  - [`tango webhooks trigger`](#tango-webhooks-trigger)
  - [`tango webhooks fetch-sample`](#tango-webhooks-fetch-sample)
  - [`tango webhooks list-event-types`](#tango-webhooks-list-event-types)
  - [`tango webhooks endpoints`](#tango-webhooks-endpoints)
  - [`tango webhooks subscriptions`](#tango-webhooks-subscriptions)
- [Programmatic use](#programmatic-use)
  - [Signature verification in your handler](#signature-verification-in-your-handler)
  - [`WebhookReceiver` in pytest fixtures](#webhookreceiver-in-pytest-fixtures)
  - [`simulate.sign` and `simulate.deliver`](#simulatesign-and-simulatedeliver)
- [Common workflows](#common-workflows)
- [Troubleshooting](#troubleshooting)

---

## Install

The signing helpers ship with the default install:

```bash
pip install tango-python
```

The CLI (`tango webhooks ...`) and the local receiver class are gated behind an optional extra:

```bash
pip install 'tango-python[webhooks]'
```

This adds [`click`](https://palletsprojects.com/projects/click) as a runtime dependency. The base SDK install stays unchanged.

After installing the extra, the `tango` console script is on your `PATH`:

```bash
tango webhooks --help
```

---

## Concepts in 60 seconds

Tango webhooks have three pieces of state:

| Concept | What it is | Tango term |
|---|---|---|
| **Endpoint** | The URL Tango POSTs to, plus a generated signing secret | `WebhookEndpoint` |
| **Subscription** | A filter saying *which events* you want delivered to that endpoint | `WebhookSubscription` |
| **Delivery** | A single signed POST Tango makes when a matching event fires | (the request itself) |

A typical setup:

1. **Create an endpoint** (`POST /api/webhooks/endpoints/`) with the public URL of your handler. Tango returns a `secret` — save it; it's used to sign every delivery.
2. **Create one or more subscriptions** (`POST /api/webhooks/subscriptions/`) describing the events your handler cares about (e.g. `entities.updated` for specific UEIs).
3. **Tango POSTs** to your endpoint when matching events fire. The body is JSON; the header `X-Tango-Signature: sha256=<hex>` is the HMAC-SHA256 of the raw body bytes keyed by your endpoint's secret.
4. **Your handler verifies the signature**, parses the body, and acts on it.

---

## Quickstart: zero to receiving

Assumes you have a `TANGO_API_KEY` and want to receive entity-update webhooks for a specific UEI.

### 1. See what you can subscribe to

```bash
export TANGO_API_KEY=...
tango webhooks list-event-types
# entities.updated         An entity record was updated
# awards.created           A new award was published
# ...
```

### 2. See what a payload looks like

```bash
tango webhooks fetch-sample --event-type entities.updated
```

Prints the canonical JSON shape Tango will deliver. No POST, no signature — just the body.

### 3. Run a local receiver

In one shell, start a listener with a chosen secret:

```bash
export TANGO_WEBHOOK_SECRET=dev_secret
tango webhooks listen --port 8011
```

In another shell, drive it with the canonical sample, signed locally:

```bash
tango webhooks simulate \
  --secret $TANGO_WEBHOOK_SECRET \
  --event-type entities.updated \
  --to http://127.0.0.1:8011/tango/webhooks
```

The listener should print a `verified` delivery with the entities-updated body. You now have a feedback loop: edit your handler, re-run `simulate`, see the result.

### 4. Wire up the real Tango → your handler path

When you're ready for end-to-end testing against Tango itself, expose your local listener via a tunnel (`ngrok http 8011`, `cloudflared tunnel`, etc.) and register that public URL with Tango:

```bash
# Use the public URL the tunnel gave you.
tango webhooks endpoints create --url https://<your-tunnel>.ngrok.io/tango/webhooks
# Save the `secret` from the response — that's what your handler uses to verify.

tango webhooks subscriptions create \
  --name "watch UEI ABC123" \
  --event-type entities.updated \
  --subject-type entity \
  --subject-id ABC123
```

To force a real test delivery from Tango (without waiting for an actual event):

```bash
tango webhooks trigger
```

You should see a `verified` delivery in your local listener with the signature value generated by Tango — not by `simulate`.

---

## CLI reference

All commands live under `tango webhooks`. Options that talk to Tango's API (`--api-key`, `--base-url`) read `TANGO_API_KEY` and `TANGO_BASE_URL` if not passed explicitly.

### `tango webhooks listen`

Run a local HTTP receiver. Verifies signatures, optionally forwards each delivery downstream, prints a one-line summary plus the JSON body for each delivery.

```bash
tango webhooks listen \
  --port 8011 \
  --host 127.0.0.1 \
  --path /tango/webhooks \
  --secret $TANGO_WEBHOOK_SECRET \
  --forward-to http://127.0.0.1:4242/wh
```

Options:

- `--port` (default `8011`)
- `--host` (default `127.0.0.1` — loopback only, by design)
- `--path` (default `/tango/webhooks`)
- `--secret` / `TANGO_WEBHOOK_SECRET` — if empty, signatures are not verified (the listener accepts everything; useful for inspecting payloads when you don't have the right secret yet)
- `--forward-to URL` — mirror each delivery to a downstream URL, preserving body bytes and the `X-Tango-Signature` header
- `--require-signature / --allow-unsigned` — override the default policy (default: require when `--secret` is set)

Press Ctrl+C to stop. Rejected (signature-mismatch) deliveries are still printed with the label `UNVERIFIED` so you can debug what arrived.

### `tango webhooks simulate`

Sign a payload locally with the same scheme Tango uses, then either print the signed request or POST it to a receiver.

**Without `--to`** — just print the headers + body a real Tango delivery would have:

```bash
tango webhooks simulate --secret dev_secret --event-type entities.updated
```

Output includes `delivered: false`, the headers (`Content-Type`, `X-Tango-Signature`), and the JSON payload.

**With `--to`** — also POST the signed body to a receiver:

```bash
tango webhooks simulate \
  --secret dev_secret \
  --event-type entities.updated \
  --to http://127.0.0.1:8011/tango/webhooks
```

Output includes `delivered: true`, the receiver's status code, and the receiver's response body.

Three sources for the payload (mutually exclusive):

| Flag | Source | When to use |
|---|---|---|
| `--event-type X` | Fetches the canonical sample for `X` from Tango | You want a realistic body without setting up a subscription |
| `--payload-file PATH` | Reads a JSON file | You're testing a specific shape (regression, edge case) |
| *(neither)* | A built-in placeholder envelope | Smoke-testing the wiring |

### `tango webhooks trigger`

Ask Tango to send a real test delivery to your configured endpoint. Wraps `POST /api/webhooks/endpoints/test-delivery/`. Requires `--api-key`.

```bash
tango webhooks trigger
tango webhooks trigger --endpoint-id <uuid>
```

Output is JSON: `success`, `status_code` (the HTTP code Tango got from your endpoint), `response_time_ms`, `endpoint_url`, `message`, `error`. Exit code is non-zero if delivery failed.

### `tango webhooks fetch-sample`

Print the canonical sample payload for one event type, or the full mapping if `--event-type` is omitted. Wraps `GET /api/webhooks/endpoints/sample-payload/`. Read-only.

```bash
tango webhooks fetch-sample --event-type entities.updated
tango webhooks fetch-sample  # all event types
```

### `tango webhooks list-event-types`

List every event type Tango supports with a one-line description.

```bash
tango webhooks list-event-types
```

### `tango webhooks endpoints`

Manage **where Tango delivers**.

```bash
tango webhooks endpoints list [--page N] [--limit N]
tango webhooks endpoints get  ENDPOINT_ID
tango webhooks endpoints create --url URL [--inactive]
tango webhooks endpoints delete ENDPOINT_ID [--yes]
```

`create` returns the generated `secret` once — save it. `delete` prompts for confirmation; `--yes` skips. `--inactive` registers the endpoint disabled (no deliveries until you re-enable it).

### `tango webhooks subscriptions`

Manage **what Tango delivers**.

```bash
tango webhooks subscriptions list [--page N] [--page-size N]
tango webhooks subscriptions get  SUBSCRIPTION_ID
tango webhooks subscriptions create \
  --name "watch UEI ABC123" \
  --event-type entities.updated \
  --subject-type entity \
  --subject-id ABC123
tango webhooks subscriptions delete SUBSCRIPTION_ID [--yes]
```

`create` builds a single-record subscription (one event type, one subject type, one or more subject IDs). For multi-record subscriptions, call `client.create_webhook_subscription(...)` directly with a hand-crafted `payload` dict.

---

## Programmatic use

The CLI is built on top of small importable pieces. You can use them directly in your own code — most usefully, in tests.

### Signature verification in your handler

`verify_signature` is pure stdlib (no SDK dependencies, no `click`). Call it on the raw request body, not on a re-serialized parsed body — the HMAC is computed over exact bytes.

```python
from tango.webhooks import verify_signature

# In your Flask / FastAPI / Django / Starlette / whatever handler:
def handle_webhook(request):
    body = request.body  # raw bytes
    signature = request.headers.get("X-Tango-Signature")
    if not verify_signature(body, secret=ENDPOINT_SECRET, signature_header=signature):
        return 401, {"error": "invalid_signature"}
    payload = json.loads(body)
    # ... act on the events ...
    return 200, {"ok": True}
```

`verify_signature` returns `False` for missing/empty/malformed headers — it never raises. Comparison is constant-time (`hmac.compare_digest`).

### `WebhookReceiver` in pytest fixtures

The CLI's `listen` command is a thin wrapper around `tango.webhooks.WebhookReceiver`, which is a context-manager-friendly local HTTP server. Use it directly in tests to verify your code emits webhook calls correctly, or to drive your handler with realistic deliveries.

```python
from tango.webhooks import WebhookReceiver, verify_signature
import httpx

def test_my_handler_processes_entity_update():
    with WebhookReceiver(secret="test_secret").run() as rx:
        # Trigger whatever in your code-under-test should send a webhook
        # (e.g. a publisher, or in this case a manual POST).
        body = b'{"events":[{"event_type":"entities.updated","uei":"ABC"}]}'
        from tango.webhooks import generate_signature
        sig = generate_signature(body, "test_secret")
        httpx.post(rx.url, content=body, headers={"X-Tango-Signature": f"sha256={sig}"})

        assert len(rx.deliveries) == 1
        assert rx.deliveries[0].verified
        assert rx.deliveries[0].body_json["events"][0]["uei"] == "ABC"
```

`WebhookReceiver` options:

- `secret: str = ""` — shared secret. Empty means "don't verify."
- `path: str = "/tango/webhooks"` — URL path to accept.
- `host: str = "127.0.0.1"` / `port: int = 0` — bind address. `0` lets the OS pick a free port.
- `forward_to: str | None = None` — mirror each delivery to a downstream URL.
- `max_history: int = 256` — cap on the in-memory `deliveries` deque.
- `on_delivery: Callable[[Delivery], None] | None = None` — fires for every recorded delivery, including signature-failed ones.
- `require_signature: bool | None = None` — override default (require iff `secret` is set).

Each `Delivery` has: `received_at`, `path`, `signature_header`, `body_bytes`, `body_json`, `verified`, `remote_addr`, `forward_status`, `forward_error`.

### `simulate.sign` and `simulate.deliver`

`simulate.sign` is the offline counterpart — it produces the exact wire form a Tango delivery would have, so you can drive your handler from a unit test:

```python
from tango.webhooks import sign

signed = sign({"events": [{"event_type": "entities.updated"}]}, secret="s")
assert signed.headers["X-Tango-Signature"].startswith("sha256=")

# Use `signed.body` as the raw bytes and `signed.headers` directly:
response = my_app.test_client().post(
    "/webhooks", data=signed.body, headers=signed.headers
)
```

`simulate.deliver` does the same but POSTs the result to a URL — `WebhookReceiver` works as a target:

```python
from tango.webhooks import simulate, WebhookReceiver

with WebhookReceiver(secret="s").run() as rx:
    result = simulate.deliver(target_url=rx.url, payload={...}, secret="s")
    assert result.status_code == 200
```

---

## Common workflows

### "I'm starting fresh — set me up to receive entity updates"

```bash
export TANGO_API_KEY=...
# 1. Confirm event types
tango webhooks list-event-types
# 2. Stand up a tunnel so Tango can reach you
ngrok http 8011 &
# 3. Register your endpoint and subscription
tango webhooks endpoints create --url https://<id>.ngrok.io/tango/webhooks
# (save the `secret` from the response into TANGO_WEBHOOK_SECRET)
tango webhooks subscriptions create \
  --name "entities" --event-type entities.updated \
  --subject-type entity --subject-id <UEI>
# 4. Run the listener pointed at your downstream handler
tango webhooks listen --port 8011 --secret $TANGO_WEBHOOK_SECRET \
  --forward-to http://localhost:4242/wh
# 5. Force a test delivery
tango webhooks trigger
```

### "I want to develop my handler offline"

You don't need a Tango account or any tunnel:

```bash
# Run the handler however you normally would on, e.g., :4242
tango webhooks listen --port 8011 --secret dev --forward-to http://127.0.0.1:4242/wh

# In another shell, drive it. Use Tango-shaped bodies if you have an API key:
tango webhooks simulate --secret dev --event-type entities.updated \
  --to http://127.0.0.1:8011/tango/webhooks

# Or use a custom shape from a file (no API key required):
tango webhooks simulate --secret dev --payload-file ./fixtures/edge.json \
  --to http://127.0.0.1:8011/tango/webhooks
```

### "I want to test my handler in CI, no network"

In pytest, use `WebhookReceiver` and `simulate.deliver` together — both are pure-Python and don't talk to Tango:

```python
from tango.webhooks import simulate, WebhookReceiver

def test_handler_round_trip():
    with WebhookReceiver(secret="s").run() as rx:
        result = simulate.deliver(
            target_url=rx.url,
            payload={"events": [{"event_type": "entities.updated", "uei": "X"}]},
            secret="s",
        )
        assert result.status_code == 200
        assert rx.deliveries[0].verified
```

### "I need to inspect what bytes Tango actually sends"

```bash
tango webhooks simulate --secret $TANGO_WEBHOOK_SECRET --event-type entities.updated
# Prints { "delivered": false, "headers": {...}, "sent_payload": {...} }
```

This is the shape your handler will receive — including the exact `X-Tango-Signature` value it should verify.

---

## Troubleshooting

**Signature always fails.** Verify on raw bytes, not on a re-serialized parsed body. The HMAC is over exact bytes; reformatting whitespace or reordering keys breaks it. Most web frameworks expose the raw body separately from a parsed JSON shortcut — use the raw one.

**`tango: command not found`.** Install the extra: `pip install 'tango-python[webhooks]'`. The console script is registered only when `click` is available.

**Listener prints `WARNING: no --secret provided`.** You started `listen` without `--secret` and without `TANGO_WEBHOOK_SECRET` set. Every delivery will be accepted with `verified=False`. Useful for inspecting payloads when you don't have the secret yet, but unsafe in any shared environment.

**`fetch-sample` returns 401.** Set `TANGO_API_KEY` (or pass `--api-key`). `fetch-sample` reads from Tango's API.

**`endpoints create` returns 403 or "endpoint already exists".** Tango limits one endpoint per user. Use `endpoints list` to find the existing one, then either reuse it or delete it first.

**`simulate --event-type X` fails with HTTP 4xx.** Tango doesn't recognize the event type. Run `list-event-types` to see the current list.

**`trigger` returns `success: false`.** Tango reached your endpoint but got a non-2xx response. Check `endpoint_url` and `response_body` in the output, then look at your handler's logs.
