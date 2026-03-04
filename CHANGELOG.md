# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.4.2] - 2026-03-04

### Added
- Protests endpoints: `list_protests`, `get_protest` with shaping and filter params (`source_system`, `outcome`, `case_type`, `agency`, `case_number`, `solicitation_number`, `protester`, `filed_date_after`, `filed_date_before`, `decision_date_after`, `decision_date_before`, `search`).

### Changed
- Lint CI workflow disabled for push/PR (runs only on manual trigger) until the private `makegov/tango` repo is accessible to the workflow.
- Updated documents to reflect changes since v0.4.0

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
