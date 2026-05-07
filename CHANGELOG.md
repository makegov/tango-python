# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Vehicles: `list_vehicles` gained 21 explicit filter parameters and `ordering` per API 4.3.0: `vehicle_type`, `type_of_idc`, `contract_type`, `set_aside` (multi-value via `|`), `who_can_use`, `naics_code`, `psc_code`, `program_acronym`, `agency`, `organization_id`, `total_obligated_min`/`max`, `idv_count_min`/`max`, `order_count_min`/`max`, `fiscal_year`, `award_date_after`/`before`, `last_date_to_order_after`/`before`, `ordering` (whitelist: `vehicle_obligations`, `latest_award_date`, `total_obligated`, `award_date`, `last_date_to_order`, `fiscal_year`, `idv_count`, `order_count`).
- Vehicles: `list_vehicle_awardees` gained a `search` parameter for entity-aware full-text search across IDV fields and recipient entity details (API 4.3.0).
- Vehicles: New top-level fields on `Vehicle` shape — `is_synthetic_solicitation`, `program_acronym`, `idv_count`, `total_obligated`, `latest_award_date` — plus a bundled `metrics` expansion (12 lakehouse rollups) on detail (API 4.2.1).
- Shaping: New `organization(*)` expand on `Vehicle`, `Forecast`, `Grant`, `ITDashboardInvestment`, and `Protest` schemas — returns the canonical 7-key office payload (`organization_id`, `office_code`, `office_name`, `agency_code`, `agency_name`, `department_code`, `department_name`).
- Shaping: New `vehicle(*)` expand on `Contract` — request the parent vehicle inline from `/api/contracts/` (API 4.2.0).

### Changed
- Default vehicle shapes (`ShapeConfig.VEHICLES_MINIMAL` / `VEHICLES_COMPREHENSIVE`) updated to surface the new top-level fields; comprehensive default now includes `organization(*)` and `metrics(*)`.

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
