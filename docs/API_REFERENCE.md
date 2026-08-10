# API Reference

Complete reference for all Tango Python SDK methods and functionality.

## Table of Contents

- [Client Initialization](#client-initialization)
- [Agencies](#agencies)
- [Offices](#offices)
- [Organizations](#organizations)
- [Contracts](#contracts)
- [IDVs](#idvs)
- [OTAs](#otas)
- [OTIDVs](#otidvs)
- [Subawards](#subawards)
- [Vehicles](#vehicles)
- [Entities](#entities)
- [Forecasts](#forecasts)
- [Opportunities](#opportunities)
- [Notices](#notices)
- [Grants](#grants)
- [GSA eLibrary Contracts](#gsa-elibrary-contracts)
- [Protests](#protests)
- [Budget](#budget)
- [Business Types](#business-types)
- [NAICS](#naics)
- [Webhooks](#webhooks)
- [Response Objects](#response-objects)
- [ShapeConfig (predefined shapes)](#shapeconfig-predefined-shapes)
- [Error Handling](#error-handling)

## Client Initialization

### TangoClient

Initialize the Tango API client.

```python
from tango import TangoClient

# With API key
client = TangoClient(api_key="your-api-key")

# From environment variable (TANGO_API_KEY)
client = TangoClient()

# Custom base URL (for testing or different environments)
client = TangoClient(api_key="your-api-key", base_url="https://custom.api.url")
```

**Parameters:**
- `api_key` (str, optional): Your Tango API key. If not provided, will load from `TANGO_API_KEY` environment variable.
- `base_url` (str, optional): Base URL for the API. Defaults to `https://tango.makegov.com`.

---

## Agencies

Government agencies that award contracts and manage programs.

### list_agencies()

List all federal agencies.

```python
agencies = client.list_agencies(page=1, limit=25)
```

**Parameters:**
- `page` (int): Page number (default: 1)
- `limit` (int): Results per page (default: 25, max: 100)
- `search` (str, optional): Search term to filter agencies by name

**Returns:** [PaginatedResponse](#paginatedresponse) with `Agency` dataclass objects

**Example:**
```python
agencies = client.list_agencies(limit=10)
print(f"Found {agencies.count} total agencies")

for agency in agencies.results:
    print(f"{agency.code}: {agency.name}")
```

### get_agency()

Get a specific agency by code.

```python
agency = client.get_agency("GSA")
```

**Parameters:**
- `code` (str): Agency identifier. Accepts CGAC ("097"), FPDS code ("4712"), short code ("GSA"), abbreviation, or canonical name. See [Federal agency hierarchy](https://docs.makegov.com/api-reference/concepts/federal-agency-hierarchy/) for code semantics.

**Returns:** `Agency` dataclass with agency details

**Example:**
```python
gsa = client.get_agency("GSA")
print(f"Name: {gsa.name}")
print(f"Abbreviation: {gsa.abbreviation or 'N/A'}")
if gsa.department:
    print(f"Department: {gsa.department.name}")
```

**Agency Fields:**
- `code` - Agency code
- `name` - Full agency name
- `abbreviation` - Short name
- `department` - Parent department (if applicable)

---

## Offices

Federal agency offices.

### list_offices()

List offices with optional search.

```python
offices = client.list_offices(page=1, limit=25, search="acquisitions")
```

**Parameters:**
- `page` (int): Page number (default: 1)
- `limit` (int): Results per page (default: 25, max: 100)
- `search` (str, optional): Search term

**Returns:** [PaginatedResponse](#paginatedresponse) with office dictionaries

### get_office()

Get a specific office by code.

```python
office = client.get_office(code="4732XX")
```

**Parameters:**
- `code` (str): Office code

**Returns:** Dictionary with office details

---

## Organizations

Federal organizations (hierarchical agency structure).

### list_organizations()

List organizations with filtering and shaping.

```python
organizations = client.list_organizations(
    page=1,
    limit=25,
    shape=ShapeConfig.ORGANIZATIONS_MINIMAL,
    # Filter parameters
    cgac=None,
    include_inactive=None,
    level=None,
    parent=None,
    search=None,
    type=None,
)
```

**Parameters:**
- `page` (int): Page number (default: 1)
- `limit` (int): Results per page (default: 25, max: 100)
- `shape` (str, optional): Response shape string
- `flat` (bool): Flatten nested objects (default: False)
- `flat_lists` (bool): Flatten arrays with indexed keys (default: False)

**Filter Parameters:**
- `cgac` - Filter by CGAC code
- `include_inactive` - Include inactive organizations
- `level` - Filter by organization level
- `parent` - Filter by parent organization
- `search` - Search term
- `type` - Filter by organization type

**Returns:** [PaginatedResponse](#paginatedresponse) with organization dictionaries

### get_organization()

Get a specific organization by fh_key.

```python
org = client.get_organization(fh_key="ORG_KEY", shape=ShapeConfig.ORGANIZATIONS_MINIMAL)
```

**Parameters:**
- `fh_key` (str): Organization key
- `shape` (str, optional): Response shape string
- `flat` (bool): Flatten nested objects (default: False)
- `flat_lists` (bool): Flatten arrays with indexed keys (default: False)

**Returns:** Dictionary with organization details

---

## Contracts

Federal contract awards and procurement data.

### list_contracts()

Search and filter contracts with extensive options.

```python
contracts = client.list_contracts(
    cursor=None,  # keyset pagination token (not page number)
    limit=25,
    shape=None,
    flat=False,
    flat_lists=False,
    # Filter parameters (all optional)
    # Text search
    keyword=None,  # Mapped to 'search' API param
    # Date filters
    award_date_gte=None,
    award_date_lte=None,
    pop_start_date_gte=None,
    pop_start_date_lte=None,
    pop_end_date_gte=None,
    pop_end_date_lte=None,
    expiring_gte=None,
    expiring_lte=None,
    # Party filters
    awarding_agency=None,
    funding_agency=None,
    recipient_name=None,  # Mapped to 'recipient' API param
    recipient_uei=None,  # Mapped to 'uei' API param
    # Classification
    naics_code=None,  # Mapped to 'naics' API param
    psc_code=None,  # Mapped to 'psc' API param
    set_aside_type=None,  # Mapped to 'set_aside' API param
    # Type filters
    fiscal_year=None,
    fiscal_year_gte=None,
    fiscal_year_lte=None,
    award_type=None,
    # Identifiers
    piid=None,
    solicitation_identifier=None,
    # Sorting
    sort=None,  # Combined with 'order' into 'ordering' API param
    order=None,  # 'asc' or 'desc'
)
```

**Common Parameters:**
- `cursor` (str, optional): Keyset pagination token from `response.next` (contracts use keyset pagination, not page numbers)
- `limit` (int): Results per page (max: 100)
- `shape` (str): Fields to return (see [Shaping Guide](SHAPES.md))
- `flat` (bool): Flatten nested objects to dot-notation keys
- `flat_lists` (bool): Flatten arrays with indexed keys

**Filter Parameters:**

**Text Search:**
- `keyword` - Search contract descriptions (automatically mapped to API's 'search' parameter)

**Date Filters:**
- `award_date_gte` - Awarded on or after date (YYYY-MM-DD)
- `award_date_lte` - Awarded on or before date (YYYY-MM-DD)
- `pop_start_date_gte` - Period of performance start date ≥
- `pop_start_date_lte` - Period of performance start date ≤
- `pop_end_date_gte` - Period of performance end date ≥
- `pop_end_date_lte` - Period of performance end date ≤
- `expiring_gte` - Expiring on or after date
- `expiring_lte` - Expiring on or before date

**Party Filters:**
- `awarding_agency` - Agency code (e.g., "4700" for GSA)
- `funding_agency` - Funding agency code
- `recipient_name` - Vendor/recipient name (mapped to 'recipient' API param)
- `recipient_uei` - Vendor UEI (mapped to 'uei' API param)

**Classification:**
- `naics_code` - NAICS industry code (mapped to 'naics' API param)
- `psc_code` - Product/Service code (mapped to 'psc' API param)
- `set_aside_type` - Set-aside type (mapped to 'set_aside' API param)

**Type Filters:**
- `fiscal_year` - Federal fiscal year (exact match)
- `fiscal_year_gte` - Fiscal year ≥
- `fiscal_year_lte` - Fiscal year ≤
- `award_type` - Award type code

**Identifiers:**
- `piid` - Procurement Instrument Identifier (exact match)
- `solicitation_identifier` - Solicitation ID

**Sorting:**
- `sort` - Field to sort by (e.g., "award_date", "obligated")
- `order` - Sort order: "asc" or "desc" (default: "asc")

**Returns:** [PaginatedResponse](#paginatedresponse) with contract dictionaries

**Examples:**

```python
# Basic search
contracts = client.list_contracts(limit=10)

# Filter by agency
contracts = client.list_contracts(
    awarding_agency="4700",  # GSA agency code
    limit=50
)

# Text search
contracts = client.list_contracts(
    keyword="software development",
    limit=50
)

# Date range
contracts = client.list_contracts(
    award_date_gte="2023-01-01",
    award_date_lte="2023-12-31",
    limit=100
)

# Expiring contracts
contracts = client.list_contracts(
    expiring_gte="2025-01-01",
    expiring_lte="2025-12-31",
    limit=50
)

# Multiple filters
contracts = client.list_contracts(
    keyword="IT services",
    awarding_agency="4700",  # GSA
    fiscal_year=2024,
    naics_code="541511",
    limit=100
)

# With shaping for performance
contracts = client.list_contracts(
    shape="key,piid,recipient(display_name),total_contract_value,award_date",
    awarding_agency="4700",
    fiscal_year=2024,
    limit=100
)

# Sorting results
contracts = client.list_contracts(
    sort="award_date",
    order="desc",
    limit=100
)
```

**Common Contract Fields:**
- `key` - Unique identifier
- `piid` - Procurement Instrument Identifier
- `description` - Contract description
- `award_date` - Date awarded
- `fiscal_year` - Fiscal year
- `total_contract_value` - Total value
- `total_obligated` - Total obligated amount
- `recipient` - Vendor information (nested)
- `awarding_agency` - Awarding agency (nested)
- `funding_agency` - Funding agency (nested)
- `naics` - Industry classification (nested)
- `psc` - Product/service code (nested)
- `place_of_performance` - Location (nested)

---

## OTAs

Other Transaction Agreements — non-FAR-based awards.

### list_otas()

List OTAs with keyset pagination, filtering, and shaping.

```python
otas = client.list_otas(
    limit=25,
    cursor=None,
    shape=ShapeConfig.OTAS_MINIMAL,
    # Filter parameters (all optional)
    award_date=None,
    award_date_gte=None,
    award_date_lte=None,
    awarding_agency=None,
    expiring_gte=None,
    expiring_lte=None,
    fiscal_year=None,
    fiscal_year_gte=None,
    fiscal_year_lte=None,
    funding_agency=None,
    ordering=None,
    piid=None,
    pop_end_date_gte=None,
    pop_end_date_lte=None,
    pop_start_date_gte=None,
    pop_start_date_lte=None,
    psc=None,
    recipient=None,
    search=None,
    uei=None,
)
```

**Notes:**
- Uses **keyset pagination** (`cursor` + `limit`) rather than page numbers.
- Filter parameters mirror those on `list_contracts`.

**Returns:** [PaginatedResponse](#paginatedresponse) with OTA dictionaries

### get_ota()

```python
ota = client.get_ota("OTA_KEY", shape=ShapeConfig.OTAS_MINIMAL)
```

---

## OTIDVs

Other Transaction IDVs — umbrella OT agreements that can have child awards.

### list_otidvs()

List OTIDVs with keyset pagination, filtering, and shaping.

```python
otidvs = client.list_otidvs(
    limit=25,
    cursor=None,
    shape=ShapeConfig.OTIDVS_MINIMAL,
    # Same filter parameters as list_otas()
)
```

**Notes:**
- Uses **keyset pagination** (`cursor` + `limit`) rather than page numbers.
- Filter parameters are identical to `list_otas()`.

**Returns:** [PaginatedResponse](#paginatedresponse) with OTIDV dictionaries

### get_otidv()

```python
otidv = client.get_otidv("OTIDV_KEY", shape=ShapeConfig.OTIDVS_MINIMAL)
```

---

## Subawards

Subcontract and subaward data under prime awards.

### list_subawards()

List subawards with filtering and shaping.

```python
subawards = client.list_subawards(
    page=1,
    limit=25,
    shape=ShapeConfig.SUBAWARDS_MINIMAL,
    # Filter parameters (all optional)
    award_key=None,
    awarding_agency=None,
    fiscal_year=None,
    fiscal_year_gte=None,
    fiscal_year_lte=None,
    funding_agency=None,
    prime_uei=None,
    recipient=None,
    sub_uei=None,
)
```

**Filter Parameters:**
- `award_key` - Filter by prime award key
- `awarding_agency` - Filter by awarding agency code
- `fiscal_year` - Exact fiscal year
- `fiscal_year_gte` / `fiscal_year_lte` - Fiscal year range
- `funding_agency` - Filter by funding agency code
- `prime_uei` - Filter by prime awardee UEI
- `recipient` - Search by subrecipient name
- `sub_uei` - Filter by subrecipient UEI

**Returns:** [PaginatedResponse](#paginatedresponse) with subaward dictionaries

---

## Vehicles

Vehicles provide a solicitation-centric way to discover groups of related IDVs and (optionally) expand into the underlying awards via shaping.

### list_vehicles()

List vehicles with optional vehicle-level full-text search and ordering.

```python
vehicles = client.list_vehicles(
    page=1,
    limit=25,
    search="GSA schedule",
    ordering="-vehicle_obligations",
    shape=ShapeConfig.VEHICLES_MINIMAL,
    flat=False,
    flat_lists=False,
)
```

**Parameters:**
- `page` (int): Page number (default: 1)
- `limit` (int): Results per page (default: 25, max: 100)
- `search` (str, optional): Vehicle-level search term
- `ordering` (str, optional): Server-side sort. Allowed: `vehicle_obligations`, `latest_award_date`. Prefix with `-` for descending.
- `shape` (str, optional): Shape string (defaults to `ShapeConfig.VEHICLES_MINIMAL`)
- `flat` (bool): Flatten nested objects in shaped response
- `flat_lists` (bool): Flatten arrays using indexed keys
- `joiner` (str): Joiner used when `flat=True` (default: `"."`)

**Returns:** [PaginatedResponse](#paginatedresponse) with vehicle dictionaries

### get_vehicle()

Get a single vehicle by UUID.

```python
vehicle = client.get_vehicle(
    uuid="00000000-0000-0000-0000-000000000001",
    shape=ShapeConfig.VEHICLES_COMPREHENSIVE,
)
```

**Notes:**
- On the vehicle detail endpoint, `search` filters **expanded awardees** when your `shape` includes `awardees(...)` (it does not filter the vehicle itself).

### list_vehicle_awardees()

List the IDV awardees for a vehicle.

```python
awardees = client.list_vehicle_awardees(
    uuid="00000000-0000-0000-0000-000000000001",
    shape=ShapeConfig.VEHICLE_AWARDEES_MINIMAL,
)
```

### list_vehicle_orders()

List task orders under a vehicle's IDVs (`/api/vehicles/{uuid}/orders/`). Optimized for fast pagination over large vehicles.

```python
orders = client.list_vehicle_orders(
    uuid="00000000-0000-0000-0000-000000000001",
    limit=25,
    ordering="-obligated",
    shape=ShapeConfig.VEHICLE_ORDERS_MINIMAL,
)
```

**Parameters:**
- `uuid` (str): Vehicle UUID
- `page` (int): Page number (default: 1)
- `limit` (int): Results per page (default: 25, max: 100)
- `ordering` (str, optional): Server-side sort. Allowed: `award_date` (default), `obligated`, `total_contract_value`. Prefix with `-` for descending.
- `shape` (str, optional): Shape string (defaults to `ShapeConfig.VEHICLE_ORDERS_MINIMAL`)
- `flat`, `flat_lists`, `joiner`: as on other vehicles methods

**Returns:** [PaginatedResponse](#paginatedresponse) with order (Contract) dictionaries

### Vehicle response fields

The post-cutover (May 2026) vehicle response includes these top-level fields, all addressable via the `shape` parameter:

| Field | Type | Notes |
| ----- | ---- | ----- |
| `uuid` | str | Stable identifier. |
| `solicitation_identifier` | str | Solicitation shared by underlying IDVs. |
| `is_synthetic_solicitation` | bool | `True` for GWAC orphans recovered via `ACRO:` prefix. |
| `agency_id` | str | From IDV award-key suffix. |
| `program_acronym` | str \| None | New post-cutover field. |
| `organization_id` | str \| None | Awarding organization. |
| `organization` | dict \| None | Live awarding-org snapshot `{organization_id, office_code, office_name, agency_code, agency_name, department_code, department_name}`. Selected as a leaf field (`shape=...,organization`); not currently sub-selectable. |
| `vehicle_type`, `who_can_use`, `type_of_idc`, `contract_type` | dict \| None | Returned as `{code, description}`. |
| `description` | str \| None | Common text across IDV descriptions. |
| `descriptions` | list[str] \| None | Distinct IDV descriptions. |
| `idv_count`, `awardee_count`, `order_count` | int \| None | Denormalized rollups. |
| `total_obligated`, `vehicle_obligations`, `vehicle_contracts_value` | Decimal \| None | Denormalized rollups. |
| `award_date`, `latest_award_date`, `last_date_to_order` | date \| None | |
| `solicitation_title`, `solicitation_description`, `solicitation_date`, `opportunity_id` | str / date / None | From SAM.gov via the linked Opportunity. |
| `naics_code`, `psc_code`, `set_aside`, `fiscal_year` | int / str / None | |

### Vehicle shape expansions

- `awardees(...)` — underlying IDV awards. Supports nested `orders(...)`.
- `metrics(*)` — bundled computed metrics: `avg_offers_received`, `award_concentration_hhi`, `order_concentration_hhi`, `competed_rate`, `using_agency_count`, `avg_order_value`, `max_order_value`, `top_recipient_share`, `recent_obligations_24mo`, `recent_orders_24mo`, `days_since_last_order`, `obligation_to_ceiling_ratio`. Defaults included in `ShapeConfig.VEHICLES_COMPREHENSIVE`.
- `organization` — live awarding-org snapshot (selected as a leaf field; not sub-selectable).

### Deprecated shape fields

The following fields and expansions are still served by the API (recomputed at request time from the underlying IDVs) but the API now returns a `Deprecation: true` response header for them. They will be removed in a future tango API release.

- `agency_details` (top-level field and `agency_details(*)` expansion)
- `competition_details` (top-level field and `competition_details(*)` expansion)
- `opportunity(*)` expansion (use the new top-level `solicitation_*` and `opportunity_id` fields instead)

If you pass any of these in `shape=...`, the SDK will emit a Python `DeprecationWarning`. The default shapes (`VEHICLES_MINIMAL`, `VEHICLES_COMPREHENSIVE`) no longer include them.

---

## IDVs

IDVs (indefinite delivery vehicles) are the parent “vehicle award” records that can have child awards/orders under them.

### list_idvs()

```python
idvs = client.list_idvs(
    limit=25,
    cursor=None,
    shape=ShapeConfig.IDVS_MINIMAL,
    awarding_agency="4700",
)
```

Notes:

- This endpoint uses **keyset pagination** (`cursor` + `limit`) rather than page numbers.

### get_idv()

```python
idv = client.get_idv("SOME_IDV_KEY", shape=ShapeConfig.IDVS_COMPREHENSIVE)
```

### list_idv_awards()

Lists child awards (contracts) under an IDV.

```python
awards = client.list_idv_awards("SOME_IDV_KEY", limit=25)
```

### list_idv_child_idvs()

Lists child IDVs under an IDV.

```python
children = client.list_idv_child_idvs("SOME_IDV_KEY", limit=25)
```

### list_idv_transactions()

```python
tx = client.list_idv_transactions("SOME_IDV_KEY", limit=100)
```

---

## Entities

Vendors, recipients, and organizations doing business with the government.

### list_entities()

List and search for entities (vendors/recipients).

```python
entities = client.list_entities(
    page=1,
    limit=25,
    shape=None,
    flat=False,
    flat_lists=False,
    # Filter parameters (all optional)
    search=None,
    cage_code=None,
    naics=None,
    name=None,
    psc=None,
    purpose_of_registration_code=None,
    socioeconomic=None,
    state=None,
    total_awards_obligated_gte=None,
    total_awards_obligated_lte=None,
    uei=None,
    zip_code=None,
)
```

**Parameters:**
- `page` (int): Page number
- `limit` (int): Results per page
- `shape` (str): Fields to return
- `flat` (bool): Flatten nested objects
- `flat_lists` (bool): Flatten arrays with indexed keys

**Filter Parameters:**
- `search` - Full-text search
- `cage_code` - Filter by CAGE code
- `naics` - Filter by NAICS code
- `name` - Filter by entity name
- `psc` - Filter by PSC code
- `purpose_of_registration_code` - Filter by registration purpose
- `socioeconomic` - Filter by socioeconomic status; accepts pipe-separated values for OR semantics, e.g. `socioeconomic="8A|WOSB"`
- `state` - Filter by state
- `total_awards_obligated_gte` / `total_awards_obligated_lte` - Obligation amount range
- `uei` - Filter by UEI
- `zip_code` - Filter by ZIP code

**Returns:** [PaginatedResponse](#paginatedresponse) with entity dictionaries

**Example:**
```python
entities = client.list_entities(search="Booz Allen", limit=20)

for entity in entities.results:
    print(f"{entity['legal_business_name']}")
    print(f"UEI: {entity.get('uei', 'N/A')}")
    if entity.get('business_types'):
        print(f"Types: {', '.join(bt['code'] for bt in entity['business_types'])}")
```

### get_entity()

Get a specific entity by UEI or CAGE code.

```python
entity = client.get_entity(key="ZQGGHJH74DW7", shape=None)
```

**Parameters:**
- `key` (str): UEI or CAGE code
- `shape` (str, optional): Fields to return

**Returns:** Dictionary with entity details

**Example:**
```python
entity = client.get_entity("ZQGGHJH74DW7")
print(f"Name: {entity['legal_business_name']}")
print(f"UEI: {entity['uei']}")

if entity.get('physical_address'):
    addr = entity['physical_address']
    print(f"Location: {addr.get('city')}, {addr.get('state_code')}")
```

**Common Entity Fields:**
- `uei` - Unique Entity Identifier
- `cage_code` - CAGE code
- `legal_business_name` - Official business name
- `display_name` - Display name
- `dba_name` - Doing Business As name
- `business_types` - Array of business type codes
- `primary_naics` - Primary NAICS code
- `physical_address` - Physical address (nested)
- `mailing_address` - Mailing address (nested)
- `email_address` - Contact email
- `entity_url` - Website

---

## Forecasts

Contract forecast and planning information.

### list_forecasts()

List contract forecasts.

```python
forecasts = client.list_forecasts(
    page=1,
    limit=25,
    shape=None,
    flat=False,
    flat_lists=False,
    # Filter parameters (all optional)
    agency=None,
    award_date_after=None,
    award_date_before=None,
    fiscal_year=None,
    fiscal_year_gte=None,
    fiscal_year_lte=None,
    modified_after=None,
    modified_before=None,
    naics_code=None,
    naics_starts_with=None,
    search=None,
    source_system=None,
    status=None,
)
```

**Parameters:**
- `page` (int): Page number
- `limit` (int): Results per page
- `shape` (str): Fields to return
- `flat` (bool): Flatten nested objects
- `flat_lists` (bool): Flatten arrays with indexed keys

**Filter Parameters:**
- `agency` - Filter by agency code
- `award_date_after` / `award_date_before` - Expected award date range
- `fiscal_year` - Exact fiscal year
- `fiscal_year_gte` / `fiscal_year_lte` - Fiscal year range
- `modified_after` / `modified_before` - Last-modified date range
- `naics_code` - NAICS code (exact match)
- `naics_starts_with` - NAICS code prefix
- `search` - Full-text search
- `source_system` - Filter by source system
- `status` - Filter by status

**Returns:** [PaginatedResponse](#paginatedresponse) with forecast dictionaries

**Example:**
```python
forecasts = client.list_forecasts(agency="GSA", fiscal_year=2025, limit=20)

for forecast in forecasts.results:
    print(f"{forecast['title']}")
    print(f"Anticipated: {forecast.get('anticipated_award_date', 'TBD')}")
    print(f"Fiscal Year: {forecast.get('fiscal_year', 'N/A')}")
```

**Common Forecast Fields:**
- `id` - Forecast identifier
- `title` - Forecast title
- `description` - Description
- `anticipated_award_date` - Expected award date
- `fiscal_year` - Fiscal year
- `naics_code` - Industry code
- `status` - Current status

---

## Opportunities

Active contract opportunities and solicitations.

### list_opportunities()

List contract opportunities/solicitations.

```python
opportunities = client.list_opportunities(
    page=1,
    limit=25,
    shape=None,
    flat=False,
    flat_lists=False,
    # Filter parameters (all optional)
    active=None,
    agency=None,
    first_notice_date_after=None,
    first_notice_date_before=None,
    last_notice_date_after=None,
    last_notice_date_before=None,
    naics=None,
    notice_type=None,
    place_of_performance=None,
    psc=None,
    response_deadline_after=None,
    response_deadline_before=None,
    search=None,
    set_aside=None,
    solicitation_number=None,
)
```

**Parameters:**
- `page` (int): Page number
- `limit` (int): Results per page
- `shape` (str): Fields to return
- `flat` (bool): Flatten nested objects
- `flat_lists` (bool): Flatten arrays with indexed keys

**Filter Parameters:**
- `active` - Filter by active status (bool)
- `agency` - Filter by agency code
- `first_notice_date_after` / `first_notice_date_before` - First notice date range
- `last_notice_date_after` / `last_notice_date_before` - Last notice date range
- `naics` - NAICS code
- `notice_type` - Filter by notice type
- `place_of_performance` - Filter by place of performance
- `psc` - PSC code
- `response_deadline_after` / `response_deadline_before` - Response deadline range
- `search` - Full-text search
- `set_aside` - Set-aside type
- `solicitation_number` - Solicitation number (exact match)

**Returns:** [PaginatedResponse](#paginatedresponse) with opportunity dictionaries

**Example:**
```python
opportunities = client.list_opportunities(agency="DOD", active=True, limit=20)

for opp in opportunities.results:
    print(f"{opp['title']}")
    print(f"Solicitation: {opp.get('solicitation_number', 'N/A')}")
    print(f"Deadline: {opp.get('response_deadline', 'Not specified')}")
    print(f"Active: {opp.get('active', False)}")
```

**Common Opportunity Fields:**
- `opportunity_id` - Unique identifier
- `title` - Opportunity title
- `solicitation_number` - Solicitation number
- `description` - Description
- `response_deadline` - Response deadline
- `active` - Is currently active
- `naics_code` - Industry code
- `psc_code` - Product/service code

---

## Notices

Contract award notices and modifications.

### list_notices()

List contract notices.

```python
notices = client.list_notices(
    page=1,
    limit=25,
    shape=None,
    flat=False,
    flat_lists=False,
    # Filter parameters (all optional)
    active=None,
    agency=None,
    naics=None,
    notice_type=None,
    posted_date_after=None,
    posted_date_before=None,
    psc=None,
    response_deadline_after=None,
    response_deadline_before=None,
    search=None,
    set_aside=None,
    solicitation_number=None,
)
```

**Parameters:**
- `page` (int): Page number
- `limit` (int): Results per page
- `shape` (str): Fields to return
- `flat` (bool): Flatten nested objects
- `flat_lists` (bool): Flatten arrays with indexed keys

**Filter Parameters:**
- `active` - Filter by active status (bool)
- `agency` - Filter by agency code
- `naics` - NAICS code
- `notice_type` - Filter by notice type
- `posted_date_after` / `posted_date_before` - Posted date range
- `psc` - PSC code
- `response_deadline_after` / `response_deadline_before` - Response deadline range
- `search` - Full-text search
- `set_aside` - Set-aside type
- `solicitation_number` - Solicitation number (exact match)

**Returns:** [PaginatedResponse](#paginatedresponse) with notice dictionaries

**Example:**
```python
notices = client.list_notices(agency="GSA", notice_type="Presolicitation", limit=20)

for notice in notices.results:
    print(f"{notice['title']}")
    print(f"Solicitation: {notice.get('solicitation_number', 'N/A')}")
    print(f"Posted: {notice.get('posted_date', 'N/A')}")
```

**Common Notice Fields:**
- `notice_id` - Notice identifier
- `title` - Notice title
- `solicitation_number` - Solicitation number
- `description` - Description
- `posted_date` - Date posted
- `naics_code` - Industry code

---

## Grants

Federal grant opportunities and assistance listings.

### list_grants()

List grant opportunities.

```python
grants = client.list_grants(
    page=1,
    limit=25,
    shape=None,
    flat=False,
    flat_lists=False,
    # Filter parameters (all optional)
    agency=None,
    applicant_types=None,
    cfda_number=None,
    funding_categories=None,
    funding_instruments=None,
    opportunity_number=None,
    posted_date_after=None,
    posted_date_before=None,
    response_date_after=None,
    response_date_before=None,
    search=None,
    status=None,
)
```

**Parameters:**
- `page` (int): Page number
- `limit` (int): Results per page (max 100)
- `shape` (str): Response shape string
- `flat` (bool): Flatten nested objects in shaped response
- `flat_lists` (bool): Flatten arrays using indexed keys

**Filter Parameters:**
- `agency` - Filter by agency code
- `applicant_types` - Filter by applicant type
- `cfda_number` - Filter by CFDA number
- `funding_categories` - Filter by funding category
- `funding_instruments` - Filter by funding instrument
- `opportunity_number` - Filter by opportunity number (exact match)
- `posted_date_after` / `posted_date_before` - Posted date range
- `response_date_after` / `response_date_before` - Response date range
- `search` - Full-text search
- `status` - Filter by status

**Returns:** [PaginatedResponse](#paginatedresponse) with grant dictionaries

**Example:**
```python
grants = client.list_grants(agency="HHS", status="F", limit=20)  # F = Forecasted, P = Posted

for grant in grants.results:
    print(f"{grant['title']}")
    print(f"Opportunity: {grant.get('opportunity_number', 'N/A')}")
    print(f"Status: {grant.get('status', {}).get('description', 'N/A')}")
```

**Common Grant Fields:**
- `grant_id` - Grant identifier
- `opportunity_number` - Opportunity number
- `title` - Grant title
- `status` - Status information (nested object with code and description)
- `agency_code` - Agency code
- `description` - Description
- `last_updated` - Last updated timestamp
- `cfda_numbers` - CFDA numbers (list of objects with number and title)
- `applicant_types` - Applicant types (list of objects with code and description)
- `funding_categories` - Funding categories (list of objects with code and description)
- `funding_instruments` - Funding instruments (list of objects with code and description)
- `category` - Category (object with code and description)
- `important_dates` - Important dates (list)
- `attachments` - Attachments (list of objects)

**Example with Expanded Fields:**
```python
# Get grants with expanded status and CFDA numbers
grants = client.list_grants(
    shape="grant_id,title,opportunity_number,status(*),cfda_numbers(number,title)",
    limit=10
)

for grant in grants.results:
    print(f"Grant: {grant['title']}")
    if grant.get('status'):
        print(f"Status: {grant['status'].get('description')}")
    if grant.get('cfda_numbers'):
        for cfda in grant['cfda_numbers']:
            print(f"CFDA: {cfda.get('number')} - {cfda.get('title')}")
```

---

## GSA eLibrary Contracts

GSA Schedule contracts from the GSA eLibrary.

### list_gsa_elibrary_contracts()

List GSA eLibrary contracts with filtering and shaping.

```python
contracts = client.list_gsa_elibrary_contracts(
    page=1,
    limit=25,
    shape=ShapeConfig.GSA_ELIBRARY_CONTRACTS_MINIMAL,
    # Filter parameters (all optional)
    contract_number=None,
    key=None,
    piid=None,
    schedule=None,
    search=None,
    sin=None,
    uei=None,
)
```

**Filter Parameters:**
- `contract_number` - Filter by contract number
- `key` - Filter by key
- `piid` - Filter by PIID
- `schedule` - Filter by GSA schedule
- `search` - Full-text search
- `sin` - Filter by SIN (Special Item Number)
- `uei` - Filter by UEI

**Returns:** [PaginatedResponse](#paginatedresponse) with GSA eLibrary contract dictionaries

### get_gsa_elibrary_contract()

Get a single GSA eLibrary contract by UUID.

```python
contract = client.get_gsa_elibrary_contract("UUID_HERE")
```

---

## Protests

Bid protest records (GAO, COFC, etc.).

### list_protests()

List bid protests with filtering and shaping.

```python
protests = client.list_protests(
    page=1,
    limit=25,
    shape=ShapeConfig.PROTESTS_MINIMAL,
    # Filter parameters (all optional)
    source_system=None,
    outcome=None,
    case_type=None,
    agency=None,
    case_number=None,
    solicitation_number=None,
    protester=None,
    filed_date_after=None,
    filed_date_before=None,
    decision_date_after=None,
    decision_date_before=None,
    search=None,
)
```

**Filter Parameters:**
- `source_system` - Filter by source system (e.g., `"gao"`)
- `outcome` - Filter by outcome (e.g., `"Denied"`, `"Dismissed"`, `"Withdrawn"`, `"Sustained"`)
- `case_type` - Filter by case type
- `agency` - Filter by protested agency
- `case_number` - Filter by case number (e.g., `"b-423274"`)
- `solicitation_number` - Filter by solicitation number
- `protester` - Search by protester name
- `filed_date_after` / `filed_date_before` - Filed date range
- `decision_date_after` / `decision_date_before` - Decision date range
- `search` - Full-text search

**Returns:** [PaginatedResponse](#paginatedresponse) with protest dictionaries

**Example:**
```python
protests = client.list_protests(
    source_system="gao",
    outcome="Sustained",
    filed_date_after="2024-01-01",
    shape="case_id,case_number,title,outcome,filed_date,dockets(docket_number,outcome)",
    limit=25,
)

for protest in protests.results:
    print(f"{protest['case_number']}: {protest['title']} — {protest['outcome']}")
```

### get_protest()

Get a single protest by case_id (UUID).

```python
protest = client.get_protest(
    "CASE_UUID",
    shape="case_id,case_number,title,source_system,outcome,filed_date,dockets(*)",
)
```

**Notes:**
- Use `shape=...,dockets(...)` to include nested docket records.

---

## Budget

Federal account × fiscal year budget rollups, covering the full budget lifecycle (requested → enacted → apportioned → obligated → outlayed), pre-computed ratios and trends, the contract / assistance / unlinked breakdown, and request-vs-actual spend.

### list_budget_accounts()

List budget accounts. One row per `(federal_account_symbol, fiscal_year)`.

```python
accounts = client.list_budget_accounts(
    page=1,
    limit=25,
    shape=ShapeConfig.BUDGET_ACCOUNTS_MINIMAL,
    # Filter parameters (all optional)
    federal_account_symbol=None,
    fiscal_year=None,
    fiscal_year_gte=None,
    fiscal_year_lte=None,
    agency_code=None,
    bureau_name=None,
    account_title=None,
    bea_category=None,
    on_off_budget=None,
    subfunction_code=None,
    search=None,
    ordering=None,
)
```

**Filter Parameters:**
- `federal_account_symbol` - Exact federal account symbol (e.g., `"097-0100"`)
- `fiscal_year` - Fiscal year (exact)
- `fiscal_year_gte` / `fiscal_year_lte` - Fiscal year range
- `agency_code` - Agency code (exact)
- `bureau_name` - Bureau name (exact)
- `account_title` - Account title (case-insensitive substring match)
- `bea_category` - BEA category (exact)
- `on_off_budget` - On/off budget flag (exact)
- `subfunction_code` - Subfunction code (exact)
- `search` - Full-text search over `account_title`, `agency_name`, `bureau_name`
- `ordering` - Sort field; prefix with `-` for descending

**Returns:** [PaginatedResponse](#paginatedresponse) of `BudgetAccount` records (see [ShapeConfig](#shapeconfig-predefined-shapes) for the default shape).

**Example:**
```python
accounts = client.list_budget_accounts(
    agency_code="097",
    fiscal_year_gte=2023,
    ordering="-enacted_ba",
    limit=10,
)

for acct in accounts.results:
    print(f"{acct.federal_account_symbol} FY{acct.fiscal_year}: "
          f"enacted ${acct.enacted_ba:,}")
```

### get_budget_account()

Get a single budget account by id.

```python
account = client.get_budget_account(
    12345,
    shape=ShapeConfig.BUDGET_ACCOUNTS_MINIMAL,
)
```

**Parameters:**
- `id` (str | int): Budget account id.
- `shape` (str, optional): Response shape. Defaults to `BUDGET_ACCOUNTS_MINIMAL`.
- `flat` / `flat_lists` / `joiner`: See [Shaping Guide](SHAPES.md).

**Returns:** A `BudgetAccount` record.

### get_budget_account_quarters()

Get quarterly TAS-grain flow for a budget account. FY21+ only.

```python
quarters = client.get_budget_account_quarters(12345, limit=25)
```

**Parameters:**
- `id` (str | int): Budget account id.
- `tas` (str, optional): Narrow to a single Treasury Account Symbol.
- `limit` (int): Results per page (max 100).

**Returns:** [PaginatedResponse](#paginatedresponse) of quarterly flow records.

### get_budget_account_recipients()

Get funding-office × recipient contract-flow detail for a budget account.

```python
recipients = client.get_budget_account_recipients(
    12345,
    funding_organization_id=None,
    limit=25,
)
```

**Parameters:**
- `id` (str | int): Budget account id.
- `funding_organization_id` (str, optional): Narrow to a single funding office (Organization UUID).
- `limit` (int): Results per page (max 100).

**Returns:** [PaginatedResponse](#paginatedresponse) of `(funding_office, recipient)` flow records.

---

## Business Types

Business type classifications.

### list_business_types()

List available business type codes.

```python
business_types = client.list_business_types(page=1, limit=25)
```

**Parameters:**
- `page` (int): Page number
- `limit` (int): Results per page

**Returns:** [PaginatedResponse](#paginatedresponse) with business type dictionaries

**Example:**
```python
business_types = client.list_business_types(limit=50)

for biz_type in business_types.results:
    print(f"{biz_type.code}: {biz_type.name}")
```

**Business Type Fields:**
- `code` - Business type code
- `name` - Business type name
- `description` - Description

---

## NAICS

NAICS (North American Industry Classification System) codes.

### list_naics()

List NAICS codes with optional filtering.

```python
naics = client.list_naics(
    page=1,
    limit=25,
    # Filter parameters (all optional)
    employee_limit=None,
    employee_limit_gte=None,
    employee_limit_lte=None,
    revenue_limit=None,
    revenue_limit_gte=None,
    revenue_limit_lte=None,
    search=None,
)
```

**Filter Parameters:**
- `employee_limit` - Exact employee size standard
- `employee_limit_gte` / `employee_limit_lte` - Employee limit range
- `revenue_limit` - Exact revenue size standard
- `revenue_limit_gte` / `revenue_limit_lte` - Revenue limit range
- `search` - Full-text search (code or description)

**Returns:** [PaginatedResponse](#paginatedresponse) with NAICS dictionaries

**Example:**
```python
naics = client.list_naics(search="software", limit=10)

for code in naics.results:
    print(f"{code['code']}: {code['description']}")
```

### get_naics()

Get a single NAICS code by code string.

```python
naics = client.get_naics("541511")
```

**Returns:** Dictionary with NAICS code details.

### get_naics_metrics()

Get computed metrics for a NAICS code.

```python
metrics = client.get_naics_metrics(code="541511", months=12, period_grouping="month")
```

---

## PSC

Product and Service Codes.

### list_psc()

```python
psc = client.list_psc(page=1, limit=25)
```

### get_psc()

```python
psc = client.get_psc("D302")
```

### get_psc_metrics()

```python
metrics = client.get_psc_metrics(code="D302", months=12, period_grouping="month")
```

---

## MAS SINs

GSA Multiple Award Schedule Special Item Numbers.

### list_mas_sins()

```python
sins = client.list_mas_sins(page=1, limit=25)
```

### get_mas_sin()

```python
sin = client.get_mas_sin("54151S")
```

---

## Assistance Listings (CFDA)

Catalog of Federal Domestic Assistance listings.

### list_assistance_listings()

```python
listings = client.list_assistance_listings(page=1, limit=25)
```

### get_assistance_listing()

```python
listing = client.get_assistance_listing("10.310")
```

---

## Departments

### list_departments()

```python
depts = client.list_departments(page=1, limit=25)
```

### get_department()

```python
dept = client.get_department("097")
```

---

## Business Types (by code)

### get_business_type()

Get a single business type by code.

```python
bt = client.get_business_type("A6")
```

---

## IT Dashboard

Federal IT investments from the OMB IT Dashboard.

### list_itdashboard_investments()

```python
investments = client.list_itdashboard_investments(
    page=1,
    limit=25,
    search=None,
    agency_code=None,
    type_of_investment=None,
    # Pro/Business+ tier-gated filters available
)
```

**Notes:**
- Filter tier-gating: `search` is free; `agency_code`, `type_of_investment` require Pro; `agency_name`, `cio_rating`, `performance_risk` require Business+.
- Shape defaults to `ShapeConfig.ITDASHBOARD_INVESTMENTS_MINIMAL`.

### get_itdashboard_investment()

```python
investment = client.get_itdashboard_investment("023-000001234")
```

---

## Entity Sub-resources

### list_entity_contracts()

```python
contracts = client.list_entity_contracts("ABCDEF123456", limit=25)
```

### list_entity_idvs()

```python
idvs = client.list_entity_idvs("ABCDEF123456", limit=25)
```

### list_entity_otas() / list_entity_otidvs()

```python
otas = client.list_entity_otas("ABCDEF123456", limit=25)
otidvs = client.list_entity_otidvs("ABCDEF123456", limit=25)
```

### list_entity_subawards()

```python
subawards = client.list_entity_subawards("ABCDEF123456", limit=25)
```

### list_entity_lcats()

```python
lcats = client.list_entity_lcats("ABCDEF123456", limit=25)
```

### get_entity_metrics()

```python
metrics = client.get_entity_metrics("ABCDEF123456", months=12, period_grouping="month")
```

### get_entity_budget_flows()

Get budget flows for an entity (`/api/entities/{uei}/budget-flows/`) — the federal accounts that funded contracts and assistance awarded to this entity.

```python
flows = client.get_entity_budget_flows("ABCDEF123456", fiscal_year=2024)
for row in flows.results:
    print(row["federal_account_symbol"], row["contract_obligated"])
# next page
more = client.get_entity_budget_flows("ABCDEF123456", page=2, fiscal_year=2024)
```

**Parameters:**
- `uei` (str): Entity UEI. Required.
- `page` (int): Page number. Default 1.
- `limit` (int): Results per page. Default 25, max 100.
- `fiscal_year` (int | None): Optional fiscal year filter.

**Returns:** `PaginatedResponse[dict[str, Any]]` — standard `count / next / previous / results`. Result rows are raw dicts from the API (not shape-controlled).

---

## IDV LCATs

### list_idv_lcats()

```python
lcats = client.list_idv_lcats("GS-00F-XXXX", limit=25)
```

---

## Agency Sub-resources

### list_agency_awarding_contracts()

List contracts where the agency is the awarding agency.

```python
contracts = client.list_agency_awarding_contracts("4700", limit=25)
```

### list_agency_funding_contracts()

List contracts where the agency is the funding agency.

```python
contracts = client.list_agency_funding_contracts("4700", limit=25)
```

---

## Resolve / Validate

### resolve()

Resolve a free-text name to ranked entity or organization candidates.

```python
result = client.resolve(
    name="Lockheed Martin",
    target_type="entity",  # or "organization"
    state="MD",     # optional
    city="Bethesda", # optional
    context="defense contractor",  # optional
)

for candidate in result.candidates:
    print(candidate.identifier, candidate.display_name)
```

**Notes:**
- Free-tier: up to 3 candidates with `identifier` and `display_name`.
- Pro+: up to 5 candidates with additional `match_tier` field.

### validate()

Validate the format of a PIID, solicitation number, or UEI.

```python
result = client.validate(identifier_type="uei", value="ABCDEF123456")
# identifier_type is one of: "piid", "solicitation", "uei"
```

**Note:** The parameter is named `identifier_type` (not `type`) to avoid shadowing the Python builtin.

---

## Opportunities (attachments)

### search_opportunity_attachments()

Semantic search over opportunity attachments. `q` is required.

```python
results = client.search_opportunity_attachments(
    q="cybersecurity",
    top_k=10,
    include_extracted_text=False,
)
```

**Parameters:**
- `q` (str): Search query (required)
- `top_k` (int, optional): Number of top results to return
- `include_extracted_text` (bool, optional): Whether to include extracted text from attachments in results

**Returns:** dict with search results

---

## Webhook Alerts

The Alerts API is the canonical (and only) write surface for webhook subscriptions. Every alert maps to one of the five `alerts.*.match` event types and delivers when its saved-search filters match new or modified records.

### list_webhook_alerts()

```python
alerts = client.list_webhook_alerts(page=1, page_size=25)
```

### get_webhook_alert()

```python
alert = client.get_webhook_alert("ALERT_UUID")
```

### create_webhook_alert()

```python
alert = client.create_webhook_alert(
    name="New cloud IT contracts",
    query_type="contract",
    filters={"naics": "541511"},
)
```

For multi-endpoint accounts, pin the delivery target with `endpoint=`:

```python
alert = client.create_webhook_alert(
    name="New cloud IT contracts",
    query_type="contract",
    filters={"naics": "541511"},
    endpoint="ENDPOINT_UUID",
)
```

**Notes:**
- `name` and `query_type` are required. `query_type` is **singular** (e.g. `"contract"`, not `"contracts"`).
- `endpoint=` is optional and only required when the account has multiple webhook endpoints; for single-endpoint accounts the server auto-resolves.

### update_webhook_alert()

```python
alert = client.update_webhook_alert("ALERT_UUID", name="Updated name")
```

### delete_webhook_alert()

```python
client.delete_webhook_alert("ALERT_UUID")
```

---

## Utility

### get_version()

```python
version = client.get_version()
```

### list_api_keys()

```python
keys = client.list_api_keys()
```

---

## Webhooks

Webhook APIs let **Large / Enterprise** users manage delivery endpoints and discover the supported event-type catalog. Filter subscriptions (alerts) live in the [Webhook Alerts](#webhook-alerts) section above.

> **For testing, signing, and a CLI tool**, see [`docs/WEBHOOKS.md`](WEBHOOKS.md). This section covers SDK method signatures only.

### list_webhook_event_types()

Discover supported `event_type` values.

```python
info = client.list_webhook_event_types()
print(info.event_types[0].event_type)
```

### list_webhook_endpoints()

List your webhook endpoint(s).

```python
endpoints = client.list_webhook_endpoints(page=1, limit=25)
```

### get_webhook_endpoint()

```python
endpoint = client.get_webhook_endpoint("ENDPOINT_UUID")
```

### create_webhook_endpoint() / update_webhook_endpoint() / delete_webhook_endpoint()

In production, MakeGov provisions the initial endpoint for you. These are most useful for dev/self-service.

```python
endpoint = client.create_webhook_endpoint("https://example.com/tango/webhooks")
endpoint = client.update_webhook_endpoint(endpoint.id, is_active=False)
client.delete_webhook_endpoint(endpoint.id)
```

### test_webhook_delivery()

Send an immediate test webhook to your configured endpoint.

```python
result = client.test_webhook_delivery()
print(result.success, result.status_code)
```

### get_webhook_sample_payload()

Fetch Tango-shaped sample deliveries.

```python
sample = client.get_webhook_sample_payload(event_type="alerts.contract.match")
print(sample["event_type"])
```

### Deliveries / redelivery

The API does not currently expose a public `/api/webhooks/deliveries/` or redelivery endpoint. Use:

- `test_webhook_delivery()` for connectivity checks
- `get_webhook_sample_payload()` for building handlers

### Receiving webhooks (signature verification)

Every delivery includes an HMAC signature header:

- `X-Tango-Signature: sha256=<hex digest>`

Compute the digest over the **raw request body bytes** using your shared secret.

The SDK ships a stdlib-only verifier that mirrors the Tango server's signing scheme byte-for-byte. Use it instead of hand-rolling — it's importable from a default install (no extras needed):

```python
from tango.webhooks import verify_signature

if not verify_signature(raw_body, secret, request.headers.get("X-Tango-Signature")):
    return 401
```

`verify_signature` returns `False` for missing/empty/malformed headers — it never raises. Comparison is constant-time.

---

## Webhook tooling (`tango.webhooks`)

The `tango.webhooks` subpackage adds testing and developer-tooling primitives on top of the API methods above. Signing helpers ship with the default install; the receiver and CLI ship with `pip install 'tango-python[webhooks]'`. See [`docs/WEBHOOKS.md`](WEBHOOKS.md) for usage guides; this section is the import-level reference.

### Signing (default install)

```python
from tango.webhooks import (
    verify_signature,        # (body: bytes, secret: str, header: str | None) -> bool
    generate_signature,      # (body: bytes, secret: str) -> str  ("sha256=<hex>" wire form)
    parse_signature_header,  # (header: str | None) -> str | None  (strips "sha256=")
    SIGNATURE_HEADER,        # "X-Tango-Signature"
    SIGNATURE_PREFIX,        # "sha256="
)
```

### `WebhookReceiver` (with `[webhooks]` extra)

A stdlib-based local HTTP receiver, useful in tests and during local development.

```python
from tango import WebhookReceiver, Delivery  # exported from top-level tango package
# or: from tango.webhooks.receiver import WebhookReceiver, Delivery

with WebhookReceiver(secret="dev").run() as rx:
    # ... cause something to POST to rx.url ...
    deliveries: list[Delivery] = rx.deliveries
```

Constructor (all keyword arguments):

| Arg | Default | Meaning |
|---|---|---|
| `secret` | `""` | Shared secret. Empty means signatures are not verified. |
| `path` | `/tango/webhooks` | URL path to accept POSTs on. |
| `host` | `127.0.0.1` | Bind address. |
| `port` | `0` | TCP port. `0` = OS picks a free port. |
| `forward_to` | `None` | Optional URL to mirror each delivery to. |
| `max_history` | `256` | Cap on the in-memory `deliveries` deque. |
| `on_delivery` | `None` | Callback fired for every delivery (verified or not). |
| `require_signature` | `None` | Override default (require iff `secret` is set). |

Each `Delivery` is a dataclass: `received_at`, `path`, `signature_header`, `body_bytes`, `body_json`, `verified`, `remote_addr`, `forward_status`, `forward_error`.

### `simulate.sign` and `simulate.deliver`

```python
from tango.webhooks import sign, SignedRequest
from tango.webhooks import simulate

# Offline — produce the signed wire form without POSTing:
signed: SignedRequest = sign({"events": [{"event_type": "..."}]}, secret="s")
signed.body         # bytes you would put on the wire
signed.signature    # bare lowercase hex
signed.headers      # {"Content-Type": ..., "X-Tango-Signature": "sha256=..."}

# With delivery — sign and POST to a target URL:
result = simulate.deliver(target_url="http://localhost:8011/tango/webhooks",
                          payload={...}, secret="s")
result.status_code   # status from the receiver
result.signature     # bare hex
result.sent_bytes    # exact bytes that were POSTed
result.response_body # body the receiver returned
```

`simulate.deliver` and `simulate.sign` accept payloads as `dict`, `list`, `str`, or raw `bytes`. Dicts/lists are serialized via `json.dumps(..., sort_keys=True, separators=(",", ":"))` so signatures are reproducible across runs.

### CLI entry point

The `tango[webhooks]` extra also installs a `tango` console script. See [`docs/WEBHOOKS.md` § CLI reference](WEBHOOKS.md#cli-reference) for the full command list.

---

## Response Objects

### PaginatedResponse

All list methods return a `PaginatedResponse` object with the following attributes:

```python
response = client.list_contracts(limit=25)

# Attributes
response.count      # Total number of results
response.next       # URL to next page (or None)
response.previous   # URL to previous page (or None)
response.results    # List of result dictionaries
```

**Example:**
```python
contracts = client.list_contracts(limit=25)

print(f"Total contracts: {contracts.count:,}")
print(f"Results on this page: {len(contracts.results)}")

# Iterate through results
for contract in contracts.results:
    print(contract['piid'])

# Check for more pages (contracts use keyset pagination via cursor)
if contracts.next:
    next_page = client.list_contracts(cursor=contracts.cursor, limit=25)
```

**Pagination Example (contracts use keyset pagination, not page numbers):**
```python
cursor = None
all_results = []
page_num = 1

while True:
    response = client.list_contracts(cursor=cursor, limit=100)
    all_results.extend(response.results)

    print(f"Batch {page_num}: {len(response.results)} results")

    if not response.next:
        break

    cursor = response.cursor  # use cursor for next page
    page_num += 1

print(f"Total collected: {len(all_results)} results")
```

---

## ShapeConfig (predefined shapes)

The SDK provides predefined shape strings as constants on `ShapeConfig`. Use them as the `shape` argument for list/get methods when you want a consistent, validated set of fields without building a custom shape string.

```python
from tango import TangoClient, ShapeConfig

client = TangoClient()

# List methods default to the minimal shape when shape is omitted
contracts = client.list_contracts(limit=10)  # uses CONTRACTS_MINIMAL

# Or pass the constant explicitly
contracts = client.list_contracts(shape=ShapeConfig.CONTRACTS_MINIMAL, limit=10)
entity = client.get_entity("UEI_KEY", shape=ShapeConfig.ENTITIES_COMPREHENSIVE)
```

**Available constants (by resource):**

| Constant | Used by | Description |
|----------|---------|-------------|
| `CONTRACTS_MINIMAL` | `list_contracts` | key, piid, award_date, recipient(display_name), description, total_contract_value |
| `ENTITIES_MINIMAL` | `list_entities` | uei, legal_business_name, cage_code, business_types |
| `ENTITIES_COMPREHENSIVE` | `get_entity` | Full entity profile (addresses, naics, psc, obligations, etc.) |
| `FORECASTS_MINIMAL` | `list_forecasts` | id, title, anticipated_award_date, fiscal_year, naics_code, status |
| `OPPORTUNITIES_MINIMAL` | `list_opportunities` | opportunity_id, title, solicitation_number, response_deadline, active |
| `NOTICES_MINIMAL` | `list_notices` | notice_id, title, solicitation_number, posted_date |
| `GRANTS_MINIMAL` | `list_grants` | grant_id, opportunity_number, title, status(*), agency_code |
| `IDVS_MINIMAL` | `list_idvs`, `list_vehicle_awardees` | key, piid, award_date, recipient(display_name,uei), description, total_contract_value, obligated, idv_type |
| `IDVS_COMPREHENSIVE` | `get_idv` | Full IDV with offices, place_of_performance, competition, transactions, etc. |
| `VEHICLES_MINIMAL` | `list_vehicles` | uuid, solicitation_identifier, is_synthetic_solicitation, program_acronym, organization_id, organization, vehicle_type, description, idv_count, awardee_count, order_count, total_obligated, vehicle_obligations, vehicle_contracts_value, latest_award_date, solicitation_title, solicitation_date |
| `VEHICLES_COMPREHENSIVE` | `get_vehicle` | Full vehicle with competition_details, fiscal_year, set_aside, etc. |
| `VEHICLE_AWARDEES_MINIMAL` | `list_vehicle_awardees` | uuid, key, piid, award_date, title, order_count, idv_obligations, idv_contracts_value, recipient(display_name,uei) |
| `ORGANIZATIONS_MINIMAL` | `list_organizations` | key, fh_key, name, level, type, short_name |
| `OTAS_MINIMAL` | `list_otas` | key, piid, award_date, recipient(display_name,uei), description, total_contract_value, obligated |
| `OTIDVS_MINIMAL` | `list_otidvs` | key, piid, award_date, recipient(display_name,uei), description, total_contract_value, obligated, idv_type |
| `SUBAWARDS_MINIMAL` | `list_subawards` | award_key, prime_recipient(uei,display_name), subaward_recipient(uei,display_name) |
| `GSA_ELIBRARY_CONTRACTS_MINIMAL` | `list_gsa_elibrary_contracts` | uuid, contract_number, schedule, recipient(display_name,uei), idv(key,award_date) |
| `PROTESTS_MINIMAL` | `list_protests` | case_id, case_number, title, source_system, outcome, filed_date |
| `BUDGET_ACCOUNTS_MINIMAL` | `list_budget_accounts`, `get_budget_account` | id, federal_account_symbol, fiscal_year, agency_code/name, bureau_name, account_title, bea_category, on_off_budget, subfunction_code, lifecycle (requested/enacted/apportioned/obligated/outlayed/unobligated), contract & assistance rollups, key ratios, next-year growth |
| `VEHICLE_ORDERS_MINIMAL` | `list_vehicle_orders` | key, piid, award_date, recipient(display_name,uei), total_contract_value, obligated |
| `ITDASHBOARD_INVESTMENTS_MINIMAL` | `list_itdashboard_investments` | Minimal IT Dashboard investment fields |
| `ITDASHBOARD_INVESTMENTS_COMPREHENSIVE` | `get_itdashboard_investment` | Full investment fields: uii, agency_code, agency_name, bureau_code, bureau_name, investment_title, type_of_investment, part_of_it_portfolio, updated_time, url |

All predefined shapes are validated at SDK release time (see [Developer Guide](DEVELOPERS.md#sdk-conformance-maintainers)). For custom shapes, see the [Shaping Guide](SHAPES.md).

---

## Error Handling

The SDK provides specific exception types for different error scenarios.

### Exception Types

```python
from tango import (
    TangoAPIError,       # Base exception
    TangoAuthError,      # 401 - Authentication failed
    TangoNotFoundError,  # 404 - Resource not found
    TangoValidationError,  # 400 - Invalid parameters
    TangoRateLimitError,  # 429 - Rate limit exceeded
)
```

### TangoAPIError

Base exception for all Tango API errors.

**Attributes:**
- `message` (str): Error message
- `status_code` (int, optional): HTTP status code

### TangoAuthError

Raised when authentication fails (401).

**Common causes:**
- Invalid API key
- Expired API key
- Missing API key for protected endpoint

### TangoNotFoundError

Raised when a resource is not found (404).

**Common causes:**
- Invalid agency code
- Invalid entity key
- Resource doesn't exist

### TangoValidationError

Raised when request parameters are invalid (400).

**Attributes:**
- `message` (str): Error message
- `status_code` (int): HTTP status code (400)
- `details` (dict): Validation error details from API

### TangoRateLimitError

Raised when rate limit is exceeded (429).

### Error Handling Examples

```python
from tango import (
    TangoClient,
    TangoAPIError,
    TangoAuthError,
    TangoNotFoundError,
    TangoValidationError,
    TangoRateLimitError,
)

client = TangoClient(api_key="your-api-key")

# Handle specific errors
try:
    agency = client.get_agency("INVALID")
except TangoNotFoundError:
    print("Agency not found")
except TangoAuthError:
    print("Authentication failed - check your API key")
except TangoAPIError as e:
    print(f"API error: {e.message}")

# Handle validation errors with details
try:
    contracts = client.list_contracts(
        award_date_gte="invalid-date"
    )
except TangoValidationError as e:
    print(f"Validation error: {e.message}")
    if e.response_data:
        print(f"Details: {e.response_data}")

# Handle rate limiting
try:
    contracts = client.list_contracts(limit=100)
except TangoRateLimitError:
    print("Rate limit exceeded - please wait before retrying")
    # Implement exponential backoff here

# Catch-all for any API error
try:
    result = client.list_contracts()
except TangoAPIError as e:
    print(f"An error occurred: {e.message}")
    if e.status_code:
        print(f"Status code: {e.status_code}")
```

---

## Best Practices

### 1. Use Response Shaping

Always use response shaping for better performance:

```python
# ❌ Without shaping (slow, large response)
contracts = client.list_contracts(limit=100)

# ✅ With shaping (fast, small response)
contracts = client.list_contracts(
    shape="key,piid,recipient(display_name),total_contract_value",
    limit=100
)
```

See [Shaping Guide](SHAPES.md) for details.

### 2. Handle Pagination Properly

Don't fetch all results at once - paginate responsibly:

```python
# ✅ Good - process batch by batch (contracts use keyset/cursor pagination)
cursor = None
batches = 0
while batches < 10:  # Limit to 10 batches
    contracts = client.list_contracts(cursor=cursor, limit=100)
    process_contracts(contracts.results)

    if not contracts.next:
        break
    cursor = contracts.cursor
    batches += 1
```

### 3. Use Filters to Narrow Results

Filter on the server side instead of client side:

```python
# ❌ Don't do this
all_contracts = client.list_contracts(limit=1000)
gsa_contracts = [c for c in all_contracts.results if c['awarding_agency']['code'] == 'GSA']

# ✅ Do this instead
gsa_contracts = client.list_contracts(
    awarding_agency="GSA",
    limit=100
)
```

### 4. Handle Errors Gracefully

Always wrap API calls in try-except blocks:

```python
try:
    contracts = client.list_contracts(limit=10)
except TangoAPIError as e:
    logger.error(f"Failed to fetch contracts: {e.message}")
    # Handle error appropriately
```

### 5. Use Environment Variables for API Keys

Never hardcode API keys:

```python
# ❌ Don't do this
client = TangoClient(api_key="sk_live_abc123...")

# ✅ Do this instead
import os
client = TangoClient(api_key=os.getenv("TANGO_API_KEY"))

# Or just use the default (loads from environment)
client = TangoClient()
```

---

## Additional Resources

- [Shaping Guide](SHAPES.md) - Response shaping syntax, examples, and field reference
- [Developer Guide](DEVELOPERS.md) - Dynamic models, predefined shapes, and SDK conformance (maintainers)
- [Quick Start](quick_start.ipynb) - Interactive notebook with examples
- [GitHub Repository](https://github.com/makegov/tango-python) - Source code and examples
- [Tango API Documentation](https://tango.makegov.com/docs) - Full API documentation
