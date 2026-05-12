# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

> Combined release: API parity (formerly tracked as PR #25) + subject-based
> webhook removal (formerly tracked as PR #27 / issue #2275). Bumped to
> `0.7.0` because removing `create_webhook_subscription` /
> `update_webhook_subscription` / `delete_webhook_subscription` /
> `list_webhook_subscriptions` / `get_webhook_subscription` and the
> `WebhookSubscription` + `WebhookSubjectTypeDefinition` dataclasses is a
> breaking change.

### Added
- `ordering` parameter on `list_forecasts`, `list_grants`, `list_subawards`, `list_gsa_elibrary_contracts`, and `list_opportunities`. Prefix with `-` for descending. Closes a parity gap with the API surface (these endpoints all accept `?ordering=` server-side).
- `create_webhook_endpoint` accepts `name=` (keyword-only). Required by the Tango API since multi-endpoint support landed; omitting it now emits a `DeprecationWarning` and will become an error in a future major version.
- `update_webhook_endpoint` accepts `name=` for renaming an endpoint.
- Webhook alerts (filter subscriptions): `list_webhook_alerts`, `get_webhook_alert`, `create_webhook_alert`, `update_webhook_alert`, `delete_webhook_alert` — the canonical write surface over `/api/webhooks/alerts/`. New `WebhookAlert` dataclass exported from the top-level package.
- `resolve(name, target_type, ...)` — POST `/api/resolve/` to rank entity / organization candidates from a free-text name. Returns `ResolveResult` with `ResolveCandidate` entries (both exported).
- `validate(identifier_type, value)` — POST `/api/validate/` to validate the format of a PIID, solicitation number, or UEI. Returns `ValidateResult` (exported).
- Reference data: `list_departments`, `get_department`, `list_psc`, `get_psc`, `get_psc_metrics`, `get_naics`, `get_naics_metrics`, `get_business_type`, `list_assistance_listings`, `get_assistance_listing`, `list_mas_sins`, `get_mas_sin`.
- Entity sub-resources: `list_entity_contracts`, `list_entity_idvs`, `list_entity_otas`, `list_entity_otidvs`, `list_entity_subawards`, `list_entity_lcats`, `get_entity_metrics`. All shape-aware where the underlying endpoint supports shaping.
- IDV sub-resources: `list_idv_lcats`.
- Agency sub-resources: `list_agency_awarding_contracts`, `list_agency_funding_contracts`.
- Misc: `search_opportunity_attachments(q, top_k, include_extracted_text)` for `/api/opportunities/attachment-search/`; `get_version()` for `/api/version/`; `list_api_keys()` for `/api/api-keys/`.

### Changed
- `create_webhook_alert` accepts `endpoint=` (keyword-only). Required for accounts with multiple webhook endpoints; auto-resolves for single-endpoint accounts. Closes the multi-endpoint smoke-test gap (tango#2256).
- `test_webhook_delivery` now sends the canonical `endpoint` body key instead of the deprecated `endpoint_id` alias (tango#2252). The Python kwarg name stays `endpoint_id=` for backwards compatibility; the wire payload is what changed.
- **`generate_signature(body, secret)` now returns the full wire form `"sha256=<hex>"`** instead of bare hex. Callers can assign the return value directly to the `X-Tango-Signature` header without wrapping in a format string. This is a breaking change for code that relied on the bare-hex return; pass it through `parse_signature_header()` to recover the previous form. `verify_signature` accepts both prefixed and bare-hex inputs (unchanged), so receivers continue to work either way.

### Removed
- **Subject-based webhook subscription surface** (tango#2275). Migrate to `create_webhook_alert(...)` and the alerts API.
  - Methods: `list_webhook_subscriptions`, `get_webhook_subscription`, `create_webhook_subscription`, `update_webhook_subscription`, `delete_webhook_subscription`.
  - Dataclasses: `WebhookSubscription`, `WebhookSubjectTypeDefinition`. Both are no longer exported from the top-level `tango` package — importing them raises `ImportError`.
  - Fields: `default_subject_type` removed from `WebhookEventType`; `subject_types` and `subject_type_definitions` removed from `WebhookEventTypesResponse`. The server's `/api/webhooks/event-types/` response no longer carries these.
  - CLI: the entire `tango webhooks subscriptions` Click subgroup (`list` / `get` / `create` / `delete`). Use the SDK's `client.create_webhook_alert(...)` etc. directly — there is no CLI subgroup for alerts.
- `ordering` kwarg from `list_notices` and `list_protests`. The notices and protests viewsets reject every `?ordering=` value at runtime (tango#2254); the kwarg silently sent unsupported values. Other five list methods retain `ordering`.

### Fixed
- `TangoClient._post()` and `_patch()` now accept both `json_data=` (positional) and `json=` (keyword) for backward compatibility. Internal callers and docs examples that use `json=` no longer fail with `TypeError`.

## [0.6.0] - 2026-05-07

### Added
- Vehicles: new top-level fields `program_acronym`, `idv_count`, `total_obligated`, `is_synthetic_solicitation`, `latest_award_date`, `description`, `opportunity_id`.
- Vehicles: new `metrics(*)` shape expansion bundling 12 computed metrics: `avg_offers_received`, `award_concentration_hhi`, `order_concentration_hhi`, `competed_rate`, `using_agency_count`, `avg_order_value`, `max_order_value`, `top_recipient_share`, `recent_obligations_24mo`, `recent_orders_24mo`, `days_since_last_order`, `obligation_to_ceiling_ratio`. Backed by a new `VehicleMetrics` schema.
- `list_vehicle_orders(uuid, ...)` for the new `/api/vehicles/{uuid}/orders/` endpoint, returning task orders under the vehicle's IDVs with two-phase pagination.
- `list_vehicles` gained 21 explicit filter parameters per API 4.3.0: `vehicle_type`, `type_of_idc`, `contract_type`, `set_aside` (multi-value via `|`), `who_can_use`, `naics_code`, `psc_code`, `program_acronym`, `agency`, `organization_id`, `total_obligated_min`/`max`, `idv_count_min`/`max`, `order_count_min`/`max`, `fiscal_year`, `award_date_after`/`before`, `last_date_to_order_after`/`before`.
- `list_vehicle_awardees` gained a `search` parameter for entity-aware full-text search across IDV fields and recipient entity details (API 4.3.0).
- `ordering` parameter on `list_vehicles` (whitelist: `vehicle_obligations`, `latest_award_date`, `total_obligated`, `award_date`, `last_date_to_order`, `fiscal_year`, `idv_count`, `order_count`) and on `list_vehicle_orders` (whitelist: `award_date`, `obligated`, `total_contract_value`). Prefix with `-` for descending.
- `ShapeConfig.VEHICLE_ORDERS_MINIMAL` default for the new orders endpoint.
- Shaping: New `organization(*)` expand on `Vehicle`, `Forecast`, `Grant`, `ITDashboardInvestment`, and `Protest` schemas — returns the canonical 7-key office payload (`organization_id`, `office_code`, `office_name`, `agency_code`, `agency_name`, `department_code`, `department_name`). Selectable as the bare leaf (`shape=...,organization`) or as a sub-selectable expansion (`shape=...,organization(office_code,...)`).
- Shaping: New `vehicle(*)` expand on `Contract` — request the parent vehicle inline from `/api/contracts/` (API 4.2.0).
- `Vehicle` and `VehicleMetrics` are now exported from the top-level `tango` package.
- `tango.webhooks` subpackage with HMAC-SHA256 signing helpers (`verify_signature`, `generate_signature`, `parse_signature_header`) that mirror the canonical Tango server scheme byte-for-byte. Importable from a default `pip install tango-python` (pure stdlib).
- `WebhookReceiver`: a stdlib-based local HTTP listener for development and integration tests. Verifies signatures, optionally forwards each delivery to a downstream URL, and records deliveries in memory for inspection. Usable as a context manager (`with WebhookReceiver(secret=...).run() as rx: ...`).
- `tango.webhooks.simulate.deliver(...)`: locally sign and POST a payload to any URL — no Tango involvement. Useful for offline iteration on receiver code.
- New `tango[webhooks]` extra (adds `click`) ships a `tango` console script covering the full webhook lifecycle for developer integrations:
  - `listen` — local receiver
  - `simulate` — sign a payload locally; with `--to`, also POST it
  - `trigger` — ask Tango to send a real test delivery
  - `fetch-sample` — print the canonical payload Tango emits for an event type
  - `list-event-types` — discover what's subscribable
  - `endpoints list|get|create|delete` — manage delivery endpoints
  - `subscriptions list|get|create|delete` — manage what events you receive
  Together these let a developer go from zero to receiving real Tango webhooks without leaving the shell or dropping into Python.

### Changed
- `ShapeConfig.VEHICLES_MINIMAL` and `VEHICLES_COMPREHENSIVE` now include the new top-level fields and the `organization` expansion. `VEHICLES_COMPREHENSIVE` defaults to `metrics(*)` and no longer pulls the deprecated `competition_details(*)` blob.

### Deprecated
- Vehicles shape fields `agency_details`, `competition_details`, and the `opportunity` expansion. The upstream API now sends a `Deprecation: true` header for these and recomputes them at request time. Explicit use in `shape=...` emits a Python `DeprecationWarning`. Sunset timeline TBD upstream.

### Notes
- Console script name `tango` may be revisited in a future release if it conflicts with sibling tooling (`tango-scripts` reuses the bare name).

### Documentation
- New `docs/WEBHOOKS.md` — comprehensive guide covering install, concepts, a zero-to-receiving quickstart, full CLI reference, and programmatic patterns for `WebhookReceiver` / `simulate.sign` / `simulate.deliver` in pytest fixtures.
- `docs/API_REFERENCE.md`: filled in `get_webhook_subscription`, replaced the hand-rolled signature-verification snippet with a pointer to `tango.webhooks.verify_signature`, and added a new "Webhook tooling (`tango.webhooks`)" section that documents every importable from the new subpackage.
- `README.md`: new "Webhook Tooling" section under Advanced Features, plus the new guide is linked from the Documentation index.

## [0.5.0] - 2026-04-08

### Added
- IT Dashboard investments: `list_itdashboard_investments`, `get_itdashboard_investment` (`/api/itdashboard/`) with shaping and filter params (`search`, `agency_code`, `agency_name`, `type_of_investment`, `updated_time_after`, `updated_time_before`, `cio_rating`, `cio_rating_max`, `performance_risk`). Tier-gated by the API: free tier gets `search`, pro adds structured filters, business+ adds CIO/performance analytics. New `ITDashboardInvestment` model and `ShapeConfig.ITDASHBOARD_INVESTMENTS_MINIMAL` / `ITDASHBOARD_INVESTMENTS_COMPREHENSIVE` defaults.

## [0.4.4] - 2026-03-25

### Added
- `parent_piid` filter parameter on `list_contracts` for filtering orders under a specific parent IDV PIID.
- `user_agent` and `extra_headers` parameters on `TangoClient` for custom request headers.
- `TangoClient.last_response_headers` property for accessing full HTTP headers from the most recent API response.

## [0.4.3] - 2026-03-21

### Added
- `TangoRateLimitError` now exposes `wait_in_seconds`, `detail`, and `limit_type` properties parsed from the API's 429 response body.
- `RateLimitInfo` dataclass for structured access to rate limit headers (`X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`, and per-window daily/burst variants).
- `TangoClient.rate_limit_info` property returns rate limit info from the most recent API response.

### Changed
- `_request` now passes the full 429 response body to `TangoRateLimitError` (previously discarded), enabling callers to access `wait_in_seconds` and the specific limit type that was exceeded.

## [0.4.2] - 2026-03-04

### Added
- Protests endpoints: `list_protests`, `get_protest` with shaping and filter params (`source_system`, `outcome`, `case_type`, `agency`, `case_number`, `solicitation_number`, `protester`, `filed_date_after`, `filed_date_before`, `decision_date_after`, `decision_date_before`, `search`).

### Changed
- Lint CI workflow disabled for push/PR (runs only on manual trigger) until the private `makegov/tango` repo is accessible to the workflow.
- Updated documents to reflect changes since v0.4.0
- Entities: `ENTITIES_COMPREHENSIVE` now uses `federal_obligations(*)` expansion; the API treats federal obligations as an expansion rather than a plain shape field.
- Docs: `SHAPES.md` documents `federal_obligations(*)` as an expansion for entity shaping.
- Integration tests: `test_parsing_nested_objects_with_missing_data` accepts award office fields (`office_code`, `agency_code`, `department_code`) and empty nested objects when the API returns partial data.

### Removed
- Assistance: `list_assistance` endpoint and all related tests, docs, and references.
- IDV summaries: `get_idv_summary` and `list_idv_summary_awards` endpoints and related integration tests, cassettes, and API reference section.

## [0.4.1] - 2026-03-03

### Added
- GSA eLibrary contracts: `list_gsa_elibrary_contracts`, `get_gsa_elibrary_contract` with shaping and filter params (`contract_number`, `key`, `piid`, `schedule`, `search`, `sin`, `uei`).

### Changed
- Conformance: replaced `**kwargs`/`**filters` with explicit filter parameters on `list_contracts`, `list_idvs`, `list_entities`, `list_forecasts`, `list_grants`, `list_notices`, `list_opportunities` for full filter/shape conformance. Backward compatibility preserved for `list_contracts(filters=SearchFilters(...))`.

## [0.4.0] - 2026-02-24

### Added
- Offices, Organizations, OTAs, OTIDVs, Subawards, NAICS, and Assistance endpoints.
- Filter/shape conformance tooling and documentation.

### Changed
- CI lint workflow runs filter/shape conformance when the manifest is available.

## [0.3.0] - 2026-02-09

### Added
- Vehicles endpoints: `list_vehicles`, `get_vehicle`, and `list_vehicle_awardees` (supports shaping + flattening). (refs `makegov/tango#1328`)
- IDV endpoints: `list_idvs`, `get_idv`, `list_idv_awards`, `list_idv_child_idvs`, `list_idv_transactions`, `get_idv_summary`, `list_idv_summary_awards`. (refs `makegov/tango#1328`)
- Webhooks v2 client support: event type discovery, subscription CRUD, endpoint management, test delivery, and sample payload helpers. (refs `makegov/tango#1274`)

### Changed
- Expanded explicit schemas to support common IDV shaping expansions (award offices, officers, period of performance, etc.).
- HTTP client now supports PATCH/DELETE helpers for webhook management endpoints.

## [0.2.0] - 2025-11-16

- Entirely refactored SDK
