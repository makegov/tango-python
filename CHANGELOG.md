# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **DIBBS, exclusions, and SBIR/STTR endpoint support.** Six endpoint families
  Tango shipped in v4.16–v4.18 had no SDK support at all — no models, no methods.
  Added `list_dibbs_rfqs`/`get_dibbs_rfq`, `list_dibbs_rfps`/`get_dibbs_rfp`,
  `list_dibbs_awards`/`get_dibbs_award`, `list_exclusions`/`get_exclusion`,
  `list_sbir_topics`/`get_sbir_topic`, and
  `list_sbir_solicitations`/`get_sbir_solicitation`, with all 85 filter params,
  shape schemas, and `ShapeConfig` defaults. New models: `DibbsRfq`, `DibbsRfp`,
  `DibbsAward`, `Exclusion`, `SbirTopic`, `SbirSolicitation`.

  Two API behaviors are worth knowing. `is_open` (DIBBS) and
  `is_currently_excluded` (exclusions) are derived at query time, so filter with
  the `open` / `active` kwargs rather than shaping on those fields. And DIBBS
  `total_contract_price` is the *order* total repeated on every line item —
  never sum it across rows; deduplicate on award + delivery-order number first.
- **Reverse shape-coverage: the SDK now captures every field and expand the API
  returns.** The conformance check only validated one direction — that the SDK's
  shape constants reference *allowed* fields. Nothing checked the reverse, so the
  hand-maintained `tango/shapes/explicit_schemas.py` had silently fallen ~200+
  fields behind the API: 209 leaf fields, 41 whole nested expand branches, and 3
  resources (naics, psc, mas_sins) the typed shape API could not request at all.
  A new generated overlay (`tango/shapes/generated_overlay.py`, produced by
  `scripts/generate_shape_overlay.py` and merged over the base by `SchemaRegistry`)
  closes all of them, with types resolved from live-API sampling rather than
  guessed. Notable now-shapeable data: contract/IDV acquisition attributes
  (`fair_opportunity_limited_sources`, `subcontracting_plan`, …), `contracts.officers`
  and `period_of_performance`, the full `organizations` hierarchy
  (`obligation_rank`, `l1..l8_fh_key`, `budget_appropriation`, `children`/`parent`),
  `otas`/`otidvs` `transactions`, and the deep `vehicles.awardees[.orders]` tree.
  Code-object expands (`set_aside`, `award_type`, `idv_type`, …), previously
  modeled inconsistently as `str`/bare `dict`, now uniformly resolve to
  `{code, description}`.
- **Reverse shape-coverage gate.** `scripts/check_shape_coverage.py` walks Tango's
  shape trees (from the vendored contract) against the SDK schemas and fails when
  the SDK misses anything the API exposes and it isn't in
  `contracts/shape_coverage_baseline.json`. Offline against the vendored contract —
  no token, runs on forks — and wired into the `lint.yml` conformance job.
  Regenerate the overlay with `scripts/generate_shape_overlay.py` (from the vendored
  contract + `contracts/observed_shape_types.json`, no API key); refresh the type
  observations with `scripts/probe_shape_types.py` (maintainer-run, needs a key).

### Fixed
- **Refreshed the vendored API contract, which had gone stale by seven
  resources.** It tracked 25 resources against Tango's current 32, so the
  conformance and coverage checks were validating against out-of-date truth and
  could not see DIBBS, exclusions, SBIR, or `budget/accounts` at all. Refreshing
  it also surfaced 72 additional fields on existing resources, now covered.
  Nested routes are keyed with a slash (`budget/accounts`), which silently broke
  the old `budget_accounts` mapping — both keys are now accepted.
- **`check_filter_shape_conformance.py` no longer reports false stale params.**
  It resolved SDK arguments to API params only through an explicit
  `api_param_mapping` dict, so methods that express the translation as tuple
  tables — `("account_title__icontains", account_title)` and
  `range_filters = (("apportioned", apportioned, apportioned_gte, ...))` — looked
  like they exposed dozens of params the API rejects. They do not:
  `list_budget_accounts` correctly sends `apportioned__gte`, `fiscal_year__lte`,
  and `account_title__icontains`. The checker now understands both tuple forms
  (in `Assign`, `AnnAssign`, and inline `for` iterables), with an explicit
  `api_param_mapping` still taking precedence. This let `budget/accounts` be
  conformance-checked for the first time; its genuinely missing lookup variants
  (`agency_code__in`, `bureau_name__icontains`, …) are now baselined.

### Added
- **Contract-first conformance system.** The canonical API filter/shape
  contract is now vendored at `contracts/filter_shape_contract.json` (refresh
  with the new `scripts/refresh_contract.py`), so the conformance check runs
  out of the box — locally, in CI, and on forks — with no tango checkout or
  access token. `scripts/check_filter_shape_conformance.py` gained three new
  checks on top of filter coverage: **staleness** (an SDK filter argument the
  API no longer accepts is an error — it would silently no-op), **types**
  (each argument's annotation is validated against the contract's
  `schema_version: 2` per-filter type metadata), and a **known-gaps baseline**
  (`contracts/conformance_baseline.json`) that downgrades accepted missing
  params from errors to warnings so backlog is tracked instead of silent. A
  new `--suggest` flag prints ready-to-paste typed parameter scaffolds for
  any missing filters. The first run against the current API surface found 7
  real coverage gaps, now baselined: `key` on contracts/IDVs/OTAs/OTIDVs,
  `cage` on entities, `id` on forecasts, and `opportunity_id` on
  opportunities.
- `TangoValidationError` now exposes the API's structured validation details
  directly: `.issues` (the list of `{"path": ..., "reason": ...}` entries the
  server returns for shape errors) and `.available_fields` (the endpoint's
  valid field set, when included). Both were previously reachable only by
  digging through `.response_data`. ([#45](https://github.com/makegov/tango-python/issues/45))

### Changed
- The CI conformance job (`lint.yml`) now runs unconditionally against the
  vendored contract instead of silently skipping when
  `TANGO_API_REPO_ACCESS_TOKEN` is absent; the token is only used for a
  best-effort staleness notice comparing the vendored contract to tango HEAD.
  `scripts/pr_review.py` likewise defaults its conformance step to the
  vendored contract (override with `TANGO_CONTRACT_MANIFEST`).
- 400 error messages now name the rejected field(s) and reason when the API
  returns structured `issues` — e.g.
  `Invalid request parameters: Invalid shape: tradeoff_process (unknown_field)`
  instead of just `Invalid request parameters: Invalid shape`. ([#45](https://github.com/makegov/tango-python/issues/45))

## [1.2.0] - 2026-06-05

### Added
- `list_budget_accounts()` now exposes the full range-filter surface that the
  REST endpoint has always supported. Every numeric metric on
  `/api/budget/accounts/` — the 26 fields in the backend's
  `RANGE_NUMERIC_FIELDS` list (`enacted_ba`, `apportioned`, `obligated_total`,
  `unobligated_balance`, `contract_obligated`,
  `contract_share_of_obligated_capped`, `ba_growth_next_year_pct`,
  `actual_vs_requested_contract`, all the ratio fields and their `_capped`
  variants, etc.) — is now accepted in three forms: exact match (`field=`),
  greater-or-equal (`field_gte=`), and less-or-equal (`field_lte=`).
  Previously only the identity / taxonomy filters were exposed, which forced
  callers to discover accounts by exact symbol lookup; the new surface makes
  pipeline-style queries (e.g. "all FY24 accounts where contract share ≥ 60%,
  unobligated balance ≥ $200M, and next-year growth ≥ 15%, sorted by largest
  headroom first") a single SDK call. The new params map to the API's
  `field__gte` / `field__lte` form; `ordering=` already accepted any of these
  fields and continues to.

## [1.1.3] - 2026-06-04

### Added
- Reference-data list/get methods now accept `shape` (and the associated
  `flat` / `flat_lists`) parameters, matching the underlying API which has
  always supported the shape system via `ShapeOnDemandMixin`. Affected:
  `list_naics` / `get_naics`, `list_psc` / `get_psc`,
  `list_assistance_listings` / `get_assistance_listing`,
  `list_business_types` / `get_business_type`,
  `list_mas_sins` / `get_mas_sin`. When `shape` is omitted, behavior is
  unchanged — the API applies its own per-resource default.
  `list_business_types` returns raw dicts (instead of `BusinessType`
  instances) when a `shape` is supplied so the caller gets exactly the
  shape requested.

## [1.1.2] - 2026-06-04

### Changed
- `get_entity_budget_flows()` now exposes the backend's standard page/limit
  pagination and `fiscal_year` filter, and returns
  `PaginatedResponse[dict[str, Any]]` instead of a raw dict. The backend has
  always paginated this endpoint via `StandardResultsSetPagination`; the
  previous signature gave callers no way to reach pages beyond the first or
  to narrow by fiscal year. Callers that were indexing `result["results"]`
  on the old return value should switch to `result.results` (and can now use
  `result.next` / `page=` to walk further pages).
- Completed the strict-`mypy` burn-down across `tango/shapes/` (parser,
  generator, factory, schema). All changes are type-annotation/typing
  corrections with no runtime behavior change, except:
  - `FieldSchema.nested_model` is now typed `type | str | None` (it always
    accepted string model names from the explicit schemas; the annotation was
    wrong). `ModelFactory.validate_data` and `ShapeParser._validate_field_spec`
    likewise accept `type | str` for the model argument.
  - Removed two dead `elif field_spec.is_wildcard:` branches (in
    `TypeGenerator.generate_type` and `ModelFactory.create_instance`) and the
    now-orphaned `_parse_nested_wildcard` helper. These were unreachable —
    wildcard field specs are fully handled by the top-of-loop branch that
    `continue`s before reaching them — so removal is behavior-preserving.

### Docs
- `docs/API_REFERENCE.md` now documents the Budget surface that shipped in
  v1.1.0: a new `## Budget` section covering `list_budget_accounts`,
  `get_budget_account`, `get_budget_account_quarters`, and
  `get_budget_account_recipients`; a `get_entity_budget_flows()` entry under
  Entity Sub-resources; a `BUDGET_ACCOUNTS_MINIMAL` row in the ShapeConfig
  table; and a Budget entry in the table of contents.

### CI
- Bumped GitHub Actions off the deprecated Node 20 runtime (forced off
  2026-06-02): `actions/checkout` v4→v6, `astral-sh/setup-uv` v4→v8.1.0
  (pinned exact — no floating `v8` major tag is published yet), and
  `codecov/codecov-action` v3→v5 (with the renamed `files:` input).
- `mypy` is now a **hard gate** in `lint.yml` (no longer advisory). The
  `tango/` package type-checks cleanly under strict mypy.

## [1.1.1] - 2026-05-29

### Removed
- The `notebooks` optional extra (`jupyter`, `ipykernel`). It only powered local
  editing of `docs/quick_start.ipynb`, which still renders on GitHub/PyPI without
  it, and its transitive tree (jupyter-server, jupyterlab, nbconvert, tornado,
  etc.) accounted for the bulk of the repo's open Dependabot alerts. Contributors
  who want to re-run the notebook can `pip install jupyter` directly. The shipped
  SDK is unaffected — its only runtime dependency remains `httpx`.

### Changed
- Refreshed the dev/test dependency lock to clear the remaining Dependabot
  alerts (patched `idna`, `pygments`, `pytest`, `python-dotenv`; dropped
  `urllib3`/`requests` transitives). Dev-tool majors moved forward
  (`mypy` 1.18→2.1, `pytest` 8→9, `ruff` 0.14→0.15, `vcrpy` 7→8); all lint,
  type, and test gates stay green. No change to the shipped SDK's runtime deps.

## [1.1.0] - 2026-05-29

### Fixed
- `_parse_webhook_alert`: aligned the parser output with the `WebhookAlert`
  type contract. Sparse server payloads now hydrate `query_type` and `filters`
  as `""` / `{}` (matching their declared non-null types) rather than `None`,
  and `status` is typed as the `Literal["active", "paused"]` the model promises.
  Clears the four type-check errors this introduced; no change for full payloads.
- `Contract` model: removed dead fields (`id`, `award_id`, `recipient_name`,
  `award_amount`, `awarding_agency`, `funding_agency`) and added the real API
  fields (`key`, `piid`, `obligated`, `total_contract_value`,
  `base_and_exercised_options_value`, `awarding_office`, `funding_office`,
  `naics_code`, `psc_code`, `set_aside`, `solicitation_identifier`,
  `parent_award`, `legislative_mandates`, `subawards_summary`,
  `place_of_performance`). The deprecated fields remain declared with `None`
  defaults for one minor cycle (they never returned data) and will be removed
  in `2.0.0`. New `OrganizationOfficePayload` dataclass for the office fields.
  (`Contract` is a documentation-only dataclass — not instantiated or exported
  — so there is no runtime impact.)
- `list_contracts`: no longer sends `page=1` to the cursor-only `/api/contracts/`
  endpoint. When no cursor is supplied, neither `page` nor `cursor` is sent and
  the API returns the first page by default.
- Shape validation: registered the `ContractOrIDVCompetition` nested schema
  (alias of `Competition`) so nested selections like
  `competition(extent_competed,number_of_offers_received)` on contract / IDV
  shapes validate instead of raising `ShapeValidationError`.

### Added
- Budget accounts surface (tango v4.6.8): `list_budget_accounts`,
  `get_budget_account`, `get_budget_account_quarters`,
  `get_budget_account_recipients`. New `BudgetAccount` dataclass exported from
  the top-level package, plus `ShapeConfig.BUDGET_ACCOUNTS_MINIMAL`.
- Singleton detail GETs: `get_contract`, `get_contract_subawards`,
  `get_contract_transactions`, `get_forecast`, `get_grant`, `get_notice`,
  `get_opportunity`, `get_subaward`.
- `get_entity_budget_flows(uei)` for `/api/entities/{uei}/budget-flows/`.
- `list_otidv_awards(key)` for `/api/otidvs/{key}/awards/` (parity with Node).
- `grant_id` filter kwarg on `list_grants` (supports multi-value OR via `|`).

### CI
- Re-enabled `lint.yml` as a PR + push-to-main gate. `ruff format` and
  `ruff check` are hard gates; `mypy` runs advisory (continue-on-error) pending
  burn-down of ~28 pre-existing type errors. The filter/shape conformance check
  is a separate job that skips cleanly until a `TANGO_API_REPO_ACCESS_TOKEN`
  secret for the private manifest repo is configured, at which point it becomes
  a hard gate.

## [1.0.0] - 2026-05-13

> First stable release. `tango-python` is now at full API parity with the
> Tango HTTP surface, the legacy subject-based webhook subscription
> mechanism has been removed in favor of filter alerts, the shape parser
> agrees byte-for-byte with the server's expand-alias handling, and the
> SDK's docs are auto-published to `docs.makegov.com/sdks/python/` via the
> composer pipeline (makegov/docs#15 / makegov/docs#16). From `1.x` on,
> we'll only do breaking changes on a major bump.
>
> Originally tracked as: API parity (PR #25), subject-based webhook
> removal (PR #27 / issue #2275), shape-validator alias support (PR #28 /
> issue #2266), and the docs-only content port (makegov/docs#16).

### Added
- `ordering` parameter on `list_forecasts`, `list_grants`, `list_subawards`, `list_gsa_elibrary_contracts`, and `list_opportunities`. Prefix with `-` for descending. Closes a parity gap with the API surface (these endpoints all accept `?ordering=` server-side).
- `create_webhook_endpoint` accepts `name=` (keyword-only) and now **requires** it. The Tango API enforces unique `(user, name)` on endpoints; omitting `name` returns a 400 server-side, so the SDK raises `TangoValidationError` client-side instead of round-tripping. (0.7.0 — never publicly released — emitted a `DeprecationWarning` instead.)
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
- `TangoClient._post()` and `_patch()` accept both `json_data=` (positional) and `json=` (keyword) for backward compatibility. Internal callers and docs examples that use `json=` no longer fail with `TypeError`. Passing **both** now raises `TangoValidationError` rather than silently preferring one — that ambiguity would hide caller bugs.
- `get_psc_metrics` / `get_naics_metrics` / `get_entity_metrics` docstrings — `period_grouping` values are `"month"` / `"quarter"` / `"year"` (the path-segment values the API accepts), not `"monthly"` / `"quarterly"`.
- `docs/API_REFERENCE.md#get_agency` — example uses `client.get_agency("GSA")` consistently and notes the parameter accepts CGAC / FPDS / short code / abbreviation / canonical name.
- `README.md` Quick Start — `get_agency()` returns an `Agency` dataclass, so the example uses attribute access (`agency.name`) instead of `agency['name']` which would `TypeError`.
- `scripts/smoke_api_parity.py` — `list_business_types(limit=1)` is now wrapped in the `run(...)` helper so a failure on that call records FAIL instead of aborting the smoke run.
- `tango webhooks endpoints create` CLI now accepts and requires `--name` (passed through to `create_webhook_endpoint(name=...)`). Previously the option was absent, meaning the CLI could never set a custom endpoint name and every call would 400 server-side (the server enforces `unique(user, name)`).
- `WebhookAlert.query_type` and `WebhookAlert.filters` tightened from `Optional` to non-optional (`str` and `dict[str, Any]` respectively). Legacy nullable rows were purged by the tango#2275 migration; the server model and serializer guarantee non-null values for all current data. `WebhookAlert.status` narrowed from `str` to `Literal["active", "paused"]` — the server serializer produces exactly those two values.
- **Shape validator agrees with server on `naics(...)` / `psc(...)` expansions.** The client-side `ShapeParser.validate()` previously rejected the canonical `shape=naics(code,description)` form (which the server has always accepted) and also rejected the alias `shape=naics_code(code,description)`. The parser now mirrors the server's `_EXPAND_ALIASES` (introduced in Tango PR makegov/tango#2259) and rewrites `naics_code(...)` / `psc_code(...)` to their canonical `naics(...)` / `psc(...)` form at parse time. Bare scalar leaves (`shape=naics_code` / `shape=psc_code`) are left untouched and still return the raw column value, matching the server. Schemas for `Contract`, `Forecast`, `Opportunity`, `Notice`, and `Vehicle` gained explicit `naics` / `psc` expand entries backed by the existing `CodeDescription` nested model. Fixes makegov/tango#2266.
- **`Subaward` schema matches the server's `SubawardSerializer`.** The previous `SUBAWARD_SCHEMA` declared two fields the server has never exposed (`id`, `amount`) and was missing every real field on the resource — including `piid`, `key`, `awarding_office` / `funding_office` / `place_of_performance` / `subaward_details` / `fsrs_details` / `highly_compensated_officers` / `usaspending_permalink`, and the denormalized `prime_awardee_*` / `recipient_*` lookup columns. Shape strings that referenced any real field (e.g. `shape="piid"`) would fail client-side validation with `unknown_field`, and conversely the SDK happily passed `shape="id"` / `shape="amount"` through to the server, where they were rejected. `SUBAWARD_SCHEMA` is now derived directly from `awards.serializers.subawards.SubawardSerializer` and the resource's runtime `available_fields`. The `Subaward` dataclass in `tango/models.py` was updated to match. New nested schemas `SubawardDetails`, `FsrsDetails`, `SubawardPlaceOfPerformance`, and `HighlyCompensatedOfficer` are registered so the corresponding shape expansions validate end-to-end.

### Documentation
- New `docs/ERRORS.md` — full exception hierarchy, recovery patterns, and the shape-error classes (`ShapeValidationError`, `ShapeParseError`, `TypeGenerationError`, `ModelInstantiationError`). Ported from `docs.makegov.com/sdks/python/errors.md` ahead of the docs-site auto-pull cutover (makegov/docs#15 / makegov/docs#16).
- New `docs/PAGINATION.md` — page-based vs cursor-based strategies, iteration patterns, and the `PaginatedResponse` field reference. Ported from `docs.makegov.com/sdks/python/pagination.md`.
- New `docs/CLIENT.md` — `TangoClient` constructor reference, `rate_limit_info` / `last_response_headers` properties, and retry-semantics note (the SDK has no built-in retry). Ported from `docs.makegov.com/sdks/python/client.md`.

### CI
- New `.github/workflows/docs-dispatch.yml` — fires on push to `main` when `docs/**`, `README.md`, or `CHANGELOG.md` changes and dispatches `external_updated` at `makegov/docs` so the public docs site rebuilds with the latest SDK content. Required for the makegov/docs#15 auto-pull pipeline.

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
