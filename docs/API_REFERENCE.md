# API Reference

Complete reference for all Tango Python SDK methods and functionality.

## Table of Contents

- [Client Initialization](#client-initialization)
- [Agencies](#agencies)
- [Contracts](#contracts)
- [Entities](#entities)
- [Forecasts](#forecasts)
- [Opportunities](#opportunities)
- [Notices](#notices)
- [Business Types](#business-types)
- [Response Objects](#response-objects)
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

**Returns:** [PaginatedResponse](#paginatedresponse) with agency dictionaries

**Example:**
```python
agencies = client.list_agencies(limit=10)
print(f"Found {agencies.count} total agencies")

for agency in agencies.results:
    print(f"{agency['code']}: {agency['name']}")
```

### get_agency()

Get a specific agency by code.

```python
agency = client.get_agency(code="GSA")
```

**Parameters:**
- `code` (str): Agency code (e.g., "GSA", "DOD", "HHS")

**Returns:** Dictionary with agency details

**Example:**
```python
gsa = client.get_agency("GSA")
print(f"Name: {gsa['name']}")
print(f"Abbreviation: {gsa.get('abbreviation', 'N/A')}")
if gsa.get('department'):
    print(f"Department: {gsa['department']['name']}")
```

**Agency Fields:**
- `code` - Agency code
- `name` - Full agency name
- `abbreviation` - Short name
- `department` - Parent department (if applicable)

---

## Contracts

Federal contract awards and procurement data.

### list_contracts()

Search and filter contracts with extensive options.

```python
contracts = client.list_contracts(
    page=1,
    limit=25,
    shape=None,
    flat=False,
    flat_lists=False,
    # Filter parameters (all optional)
    keyword=None,
    award_date_gte=None,
    award_date_lte=None,
    award_amount_gte=None,
    award_amount_lte=None,
    awarding_agency=None,
    funding_agency=None,
    recipient_name=None,
    recipient_uei=None,
    naics_code=None,
    psc_code=None,
    place_of_performance_state=None,
    place_of_performance_zip=None,
    fiscal_year=None,
    contract_type=None,
    award_type=None,
    set_aside_type=None,
    extent_competed=None,
)
```

**Common Parameters:**
- `page` (int): Page number
- `limit` (int): Results per page (max: 100)
- `shape` (str): Fields to return (see [Shaping Guide](SHAPES.md))
- `flat` (bool): Flatten nested objects to dot-notation keys
- `flat_lists` (bool): Flatten arrays with indexed keys

**Filter Parameters:**

**Text Search:**
- `keyword` - Search contract descriptions and titles

**Date Filters:**
- `award_date_gte` - Awarded on or after date (YYYY-MM-DD)
- `award_date_lte` - Awarded on or before date (YYYY-MM-DD)

**Amount Filters:**
- `award_amount_gte` - Minimum award amount
- `award_amount_lte` - Maximum award amount

**Party Filters:**
- `awarding_agency` - Agency code awarding the contract
- `funding_agency` - Agency code funding the contract
- `recipient_name` - Vendor/recipient name (partial match)
- `recipient_uei` - Vendor UEI (exact match)

**Classification:**
- `naics_code` - NAICS industry code
- `psc_code` - Product/Service code

**Location:**
- `place_of_performance_state` - State code (e.g., "CA", "NY")
- `place_of_performance_zip` - ZIP code

**Type Filters:**
- `fiscal_year` - Federal fiscal year
- `contract_type` - Type of contract
- `award_type` - Award type
- `set_aside_type` - Small business set-aside type
- `extent_competed` - Competition extent

**Returns:** [PaginatedResponse](#paginatedresponse) with contract dictionaries

**Examples:**

```python
# Basic search
contracts = client.list_contracts(limit=10)

# Filter by agency
contracts = client.list_contracts(
    awarding_agency="GSA",
    limit=50
)

# Date range
contracts = client.list_contracts(
    award_date_gte="2023-01-01",
    award_date_lte="2023-12-31",
    limit=100
)

# Amount range
contracts = client.list_contracts(
    award_amount_gte=100000,
    award_amount_lte=1000000,
    limit=50
)

# Multiple filters
contracts = client.list_contracts(
    awarding_agency="DOD",
    naics_code="541511",  # IT services
    fiscal_year=2024,
    limit=100
)

# With shaping for performance
contracts = client.list_contracts(
    shape="key,piid,recipient(display_name),total_contract_value,award_date",
    awarding_agency="GSA",
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
    # Additional filters can be passed as **kwargs
)
```

**Parameters:**
- `page` (int): Page number
- `limit` (int): Results per page
- `shape` (str): Fields to return
- `flat` (bool): Flatten nested objects

**Returns:** [PaginatedResponse](#paginatedresponse) with entity dictionaries

**Example:**
```python
entities = client.list_entities(limit=20)

for entity in entities.results:
    print(f"{entity['display_name']}")
    print(f"UEI: {entity.get('uei', 'N/A')}")
    if entity.get('business_types'):
        print(f"Types: {', '.join(entity['business_types'])}")
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
    # Additional filters
    agency=None,
)
```

**Parameters:**
- `page` (int): Page number
- `limit` (int): Results per page
- `shape` (str): Fields to return
- `flat` (bool): Flatten nested objects
- `agency` (str): Filter by agency code

**Returns:** [PaginatedResponse](#paginatedresponse) with forecast dictionaries

**Example:**
```python
forecasts = client.list_forecasts(agency="GSA", limit=20)

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

List contract opportunities.

```python
opportunities = client.list_opportunities(
    page=1,
    limit=25,
    shape=None,
    flat=False,
    # Additional filters
    agency=None,
)
```

**Parameters:**
- `page` (int): Page number
- `limit` (int): Results per page
- `shape` (str): Fields to return
- `flat` (bool): Flatten nested objects
- `agency` (str): Filter by agency code

**Returns:** [PaginatedResponse](#paginatedresponse) with opportunity dictionaries

**Example:**
```python
opportunities = client.list_opportunities(agency="DOD", limit=20)

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
    # Additional filters
    agency=None,
)
```

**Parameters:**
- `page` (int): Page number
- `limit` (int): Results per page
- `shape` (str): Fields to return
- `flat` (bool): Flatten nested objects
- `agency` (str): Filter by agency code

**Returns:** [PaginatedResponse](#paginatedresponse) with notice dictionaries

**Example:**
```python
notices = client.list_notices(agency="GSA", limit=20)

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
    print(f"{biz_type['code']}: {biz_type['name']}")
```

**Business Type Fields:**
- `code` - Business type code
- `name` - Business type name
- `description` - Description

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

# Check for more pages
if contracts.next:
    next_page = client.list_contracts(page=2, limit=25)
```

**Pagination Example:**
```python
page = 1
all_results = []

while True:
    response = client.list_contracts(page=page, limit=100)
    all_results.extend(response.results)

    print(f"Page {page}: {len(response.results)} results")

    if not response.next:
        break

    page += 1

print(f"Total collected: {len(all_results)} results")
```

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
    if e.details:
        print(f"Details: {e.details}")

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
# ✅ Good - process page by page
page = 1
while page <= 10:  # Limit to 10 pages
    contracts = client.list_contracts(page=page, limit=100)
    process_contracts(contracts.results)

    if not contracts.next:
        break
    page += 1
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

- [Shaping Guide](SHAPES.md) - Comprehensive guide to response shaping
- [Quick Start](quick_start.ipynb) - Interactive notebook with examples
- [GitHub Repository](https://github.com/makegov/tango-python) - Source code and examples
- [Tango API Documentation](https://tango.makegov.com/docs) - Full API documentation
