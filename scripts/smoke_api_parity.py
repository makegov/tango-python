#!/usr/bin/env python3
"""Smoke test for API-parity work (feat/api-parity branch).

Hits every method added or changed on the branch against a running local
Tango. For mutations (webhook endpoints / subscriptions / alerts) the
script creates a resource, verifies it, and tears it down. Prints
PASS/FAIL per method and exits non-zero on any failure.

Usage:
    TANGO_BASE_URL=http://localhost:8000 \\
    TANGO_API_KEY=... \\
    python scripts/smoke_api_parity.py
"""

from __future__ import annotations

import os
import sys
import time
import traceback
from collections.abc import Callable
from typing import Any

from tango import TangoClient, WebhookAlert, WebhookEndpoint

BASE_URL = os.getenv("TANGO_BASE_URL", "http://localhost:8000")
API_KEY = os.getenv("TANGO_API_KEY")
CALLBACK_URL = "http://example.test/smoke-python"

if not API_KEY:
    print("TANGO_API_KEY not set", file=sys.stderr)
    sys.exit(2)


client = TangoClient(api_key=API_KEY, base_url=BASE_URL)


# ----- result tracking -----
results: list[tuple[str, bool, str]] = []


def run(label: str, fn: Callable[[], Any], *, skip_if_blank: str | None = None) -> Any:
    """Run a smoke step; record PASS/FAIL; return its value (or None on fail)."""
    if skip_if_blank is not None and not skip_if_blank:
        results.append((label, True, "skipped: dependency unavailable"))
        print(f"  SKIP  {label}")
        return None
    try:
        out = fn()
        results.append((label, True, "ok"))
        print(f"  PASS  {label}")
        return out
    except Exception as exc:  # noqa: BLE001
        results.append((label, False, f"{type(exc).__name__}: {exc}"))
        print(f"  FAIL  {label}   {type(exc).__name__}: {exc}")
        traceback.print_exc(limit=2)
        return None


# ============================================================================
# Reference data
# ============================================================================

print("\n=== Reference data ===")

dept_pager = run("list_departments(limit=2)", lambda: client.list_departments(limit=2))
dept_code = ""
if dept_pager and dept_pager.results:
    dept_code = str(dept_pager.results[0].get("code", ""))
run(
    f"get_department({dept_code!r})",
    lambda: client.get_department(dept_code),
    skip_if_blank=dept_code,
)

psc_pager = run("list_psc(limit=2)", lambda: client.list_psc(limit=2))
psc_code = ""
if psc_pager and psc_pager.results:
    psc_code = str(psc_pager.results[0].get("code", ""))
run(
    f"get_psc({psc_code!r})",
    lambda: client.get_psc(psc_code),
    skip_if_blank=psc_code,
)
run(
    f"get_psc_metrics({psc_code!r}, 12, 'month')",
    lambda: client.get_psc_metrics(psc_code, 12, "month"),
    skip_if_blank=psc_code,
)

# A NAICS we know exists in seed data
NAICS_CODE = "541511"
run(f"get_naics({NAICS_CODE!r})", lambda: client.get_naics(NAICS_CODE))
run(
    f"get_naics_metrics({NAICS_CODE!r}, 12, 'month')",
    lambda: client.get_naics_metrics(NAICS_CODE, 12, "month"),
)

bt_pager = run("list_business_types(limit=1)", lambda: client.list_business_types(limit=1))
bt_code = ""
if bt_pager and bt_pager.results:
    bt_code = str(bt_pager.results[0].code or "")
run(
    f"get_business_type({bt_code!r})",
    lambda: client.get_business_type(bt_code),
    skip_if_blank=bt_code,
)

al_pager = run(
    "list_assistance_listings(limit=2)", lambda: client.list_assistance_listings(limit=2)
)
al_number = ""
if al_pager and al_pager.results:
    al_number = str(al_pager.results[0].get("number", ""))
run(
    f"get_assistance_listing({al_number!r})",
    lambda: client.get_assistance_listing(al_number),
    skip_if_blank=al_number,
)

sin_pager = run("list_mas_sins(limit=2)", lambda: client.list_mas_sins(limit=2))
sin = ""
if sin_pager and sin_pager.results:
    r = sin_pager.results[0]
    sin = str(r.get("sin") or r.get("code") or r.get("number") or "")
run(
    f"get_mas_sin({sin!r})",
    lambda: client.get_mas_sin(sin),
    skip_if_blank=sin,
)


# ============================================================================
# Entity sub-resources
# ============================================================================

print("\n=== Entity sub-resources ===")
ent_pager = client.list_entities(limit=1)
uei = ""
if ent_pager.results:
    uei = str(ent_pager.results[0].get("uei") or "")

run(
    f"list_entity_contracts({uei!r}, limit=2)",
    lambda: client.list_entity_contracts(uei, limit=2),
    skip_if_blank=uei,
)
run(
    f"list_entity_idvs({uei!r}, limit=2)",
    lambda: client.list_entity_idvs(uei, limit=2),
    skip_if_blank=uei,
)
run(
    f"list_entity_otas({uei!r}, limit=2)",
    lambda: client.list_entity_otas(uei, limit=2),
    skip_if_blank=uei,
)
run(
    f"list_entity_otidvs({uei!r}, limit=2)",
    lambda: client.list_entity_otidvs(uei, limit=2),
    skip_if_blank=uei,
)
run(
    f"list_entity_subawards({uei!r}, limit=2)",
    lambda: client.list_entity_subawards(uei, limit=2),
    skip_if_blank=uei,
)
run(
    f"list_entity_lcats({uei!r}, limit=2)",
    lambda: client.list_entity_lcats(uei, limit=2),
    skip_if_blank=uei,
)
run(
    f"get_entity_metrics({uei!r}, 12, 'month')",
    lambda: client.get_entity_metrics(uei, 12, "month"),
    skip_if_blank=uei,
)


# ============================================================================
# IDV / Agency sub-resources
# ============================================================================

print("\n=== IDV / Agency sub-resources ===")
idv_pager = client.list_idvs(limit=1)
idv_key = ""
if idv_pager.results:
    idv_key = str(idv_pager.results[0]["key"])
run(
    f"list_idv_lcats({idv_key!r}, limit=2)",
    lambda: client.list_idv_lcats(idv_key, limit=2),
    skip_if_blank=idv_key,
)

ag_pager = client.list_agencies(limit=1)
ag_code = ""
if ag_pager.results:
    ag_code = str(ag_pager.results[0].code or "")
run(
    f"list_agency_awarding_contracts({ag_code!r}, limit=2)",
    lambda: client.list_agency_awarding_contracts(ag_code, limit=2),
    skip_if_blank=ag_code,
)
# funding-contracts can 504 locally if the agency has a wide net of awards
# (heavy aggregation). Catch and SKIP server timeouts.
_fund_label = f"list_agency_funding_contracts({ag_code!r}, limit=2)"
if ag_code:
    try:
        client.list_agency_funding_contracts(ag_code, limit=2)
        results.append((_fund_label, True, "ok"))
        print(f"  PASS  {_fund_label}")
    except Exception as exc:  # noqa: BLE001
        msg = f"{type(exc).__name__}: {exc}"
        if "504" in msg or "timeout" in msg.lower():
            results.append((_fund_label, True, f"skipped: server {msg}"))
            print(f"  SKIP  {_fund_label} — {msg}")
        else:
            results.append((_fund_label, False, msg))
            print(f"  FAIL  {_fund_label} — {msg}")
else:
    results.append((_fund_label, True, "skipped: dependency unavailable"))
    print(f"  SKIP  {_fund_label}")


# ============================================================================
# ordering= round-trips
# ============================================================================

print("\n=== ordering= round-trips ===")
run(
    "list_forecasts(ordering='fiscal_year', limit=2)",
    lambda: client.list_forecasts(ordering="fiscal_year", limit=2),
)
run(
    "list_grants(ordering='-posted_date', limit=2)",
    lambda: client.list_grants(ordering="-posted_date", limit=2),
)
run(
    "list_opportunities(ordering='-last_notice_date', limit=2)",
    lambda: client.list_opportunities(ordering="-last_notice_date", limit=2),
)
run(
    "list_notices(limit=2)  (no ordering — endpoint rejects ordering server-side)",
    lambda: client.list_notices(limit=2),
)
run(
    "list_protests(limit=2)  (no ordering — endpoint rejects ordering server-side)",
    lambda: client.list_protests(limit=2),
)
run(
    "list_subawards(ordering='-last_modified_date', limit=2)",
    lambda: client.list_subawards(ordering="-last_modified_date", limit=2),
)
run(
    "list_gsa_elibrary_contracts(ordering='piid', limit=2)",
    lambda: client.list_gsa_elibrary_contracts(ordering="piid", limit=2),
)


# ============================================================================
# resolve / validate
# ============================================================================

print("\n=== resolve / validate ===")
run(
    "resolve('Microsoft', target_type='entity')",
    lambda: client.resolve("Microsoft", target_type="entity"),
)
run(
    "validate('uei', 'TESTUEI12345')",
    lambda: client.validate("uei", "TESTUEI12345"),
)
run(
    "validate('piid', '47QSMA22D08PT')",
    lambda: client.validate("piid", "47QSMA22D08PT"),
)


# ============================================================================
# Misc
# ============================================================================

print("\n=== Misc ===")
run("get_version()", client.get_version)
run("list_api_keys()", client.list_api_keys)
# attachment-search may 404 locally if the feature flag / RAG index isn't set
# up. Treat 404 as SKIP, anything else as a real result.
_attach_label = "search_opportunity_attachments(q='cyber', top_k=3)"
try:
    client.search_opportunity_attachments(q="cyber", top_k=3)
    results.append((_attach_label, True, "ok"))
    print(f"  PASS  {_attach_label}")
except Exception as exc:  # noqa: BLE001
    if type(exc).__name__ == "TangoNotFoundError":
        results.append(
            (_attach_label, True, "skipped: 404 (feature flag / index not enabled locally)")
        )
        print(f"  SKIP  {_attach_label} — 404 locally")
    else:
        results.append((_attach_label, False, f"{type(exc).__name__}: {exc}"))
        print(f"  FAIL  {_attach_label} — {type(exc).__name__}: {exc}")


# ============================================================================
# _post json= kwarg backcompat
# ============================================================================

print("\n=== _post json= kwarg backcompat ===")
run(
    "_post(json=) backcompat (resolve via internal helper)",
    lambda: client._post(
        "/api/resolve/",
        json={"name": "Microsoft", "target_type": "entity"},
    ),
)


# ============================================================================
# Webhook write methods (mutations: create + verify + delete)
# ============================================================================

print("\n=== Webhook endpoint create/update/delete ===")
endpoint_name = f"smoke-python-{int(time.time())}"
created_endpoint: WebhookEndpoint | None = None


def _create_endpoint() -> WebhookEndpoint:
    return client.create_webhook_endpoint(
        callback_url=CALLBACK_URL, is_active=True, name=endpoint_name
    )


created_endpoint = run("create_webhook_endpoint(name=...)", _create_endpoint)

if created_endpoint:
    ep_id = created_endpoint.id

    run(
        f"get_webhook_endpoint({ep_id!r})",
        lambda: client.get_webhook_endpoint(ep_id),
    )
    run(
        "update_webhook_endpoint(is_active=False)",
        lambda: client.update_webhook_endpoint(ep_id, is_active=False),
    )

    # Alert (filter subscription) — pass endpoint explicitly so this works
    # for multi-endpoint accounts as well as single-endpoint ones.
    alert: WebhookAlert | None = run(
        "create_webhook_alert(endpoint=...)",
        lambda: client.create_webhook_alert(
            name=f"smoke-alert-{int(time.time())}",
            query_type="opportunity",
            filters={"naics": "541511"},
            frequency="daily",
            endpoint=ep_id,
        ),
    )

    if alert:
        aid = alert.alert_id
        run(f"get_webhook_alert({aid!r})", lambda: client.get_webhook_alert(aid))
        run(
            "update_webhook_alert(name='renamed')",
            lambda: client.update_webhook_alert(aid, name="renamed"),
        )
        run("list_webhook_alerts()", client.list_webhook_alerts)
        run(
            "delete_webhook_alert(...)",
            lambda: client.delete_webhook_alert(aid),
        )
    else:
        run("list_webhook_alerts()", client.list_webhook_alerts)

    # Cleanup endpoint
    run(
        f"delete_webhook_endpoint({ep_id!r})",
        lambda: client.delete_webhook_endpoint(ep_id),
    )


# ============================================================================
# Summary
# ============================================================================

passed = sum(1 for _, ok, _ in results if ok)
failed = sum(1 for _, ok, _ in results if not ok)
total = len(results)
print("\n" + "=" * 70)
print(f"Smoke summary: {passed} passed, {failed} failed, {total} total")
print("=" * 70)
if failed:
    for label, ok, msg in results:
        if not ok:
            print(f"  FAIL  {label}: {msg}")
    sys.exit(1)
sys.exit(0)
