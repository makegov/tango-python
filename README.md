# Tango Python SDK

A modern Python SDK for the [Tango API](https://tango.makegov.com) by MakeGov, featuring dynamic response shaping and comprehensive type hints.

## Features

- **Dynamic Response Shaping** - Request only the fields you need, reducing payload sizes by 60-80%
- **Full Type Safety** - Runtime-generated TypedDict types with accurate type hints for IDE autocomplete
- **Comprehensive API Coverage** - All major Tango API endpoints (contracts, IDVs, OTAs, entities, forecasts, opportunities, notices, grants, protests, webhooks, and more)
- **Flexible Data Access** - Dictionary-based response objects with validation
- **Modern Python** - Built for Python 3.12+ using modern async-ready patterns
- **Production-Ready** - Comprehensive test suite with VCR.py-based integration tests

## Installation

**Requirements:** Python 3.12 or higher

```bash
pip install tango-python
```

Or with uv:

```bash
uv pip install tango-python
```

## Quick Start

```python
from tango import TangoClient, ShapeConfig

# Initialize the client
client = TangoClient(api_key="your-api-key")

# List agencies
agencies = client.list_agencies()
print(f"Found {agencies.count} agencies")

# Get specific agency
agency = client.get_agency("GSA")
print(f"Agency: {agency['name']}")

# Search contracts
contracts = client.list_contracts(
    limit=10
)
## Authentication

Most endpoints require an API key. You can obtain one from the [Tango API portal](https://tango.makegov.com).

```python
# With API key
client = TangoClient(api_key="your-api-key")

# From environment variable (TANGO_API_KEY)
client = TangoClient()
```

## Core Concepts

### Dynamic Response Shaping

Response shaping is the most powerful feature of the Tango SDK. It lets you request only the fields you need, dramatically reducing payload sizes and improving performance.

```python
from tango import TangoClient, ShapeConfig

client = TangoClient(api_key="your-api-key")

# Custom shape - only fields you need
contracts = client.list_contracts(
    shape="key,piid,recipient(display_name,uei),total_contract_value",
    limit=10
)

# Access fields using dictionary syntax OR as an attribute
for contract in contracts.results:
    print(f"PIID: {contract['piid']}")
    print(f"Recipient: {contract['recipient']['display_name']}")

for contract in contracts.results:
    print(f"PIID: {contract.piid}")
    print(f"Recipient: {contract.recipient.display_name}")

```

## API Methods

### Agencies

```python
# List all agencies
agencies = client.list_agencies(page=1, limit=25)

# Get specific agency by code
agency = client.get_agency("GSA")
```

### Contracts

```python
# List/search contracts with filtering
contracts = client.list_contracts(
    page=1,
    limit=25,
    # Filter parameters
    keyword="software",
    awarding_agency="4700",  # GSA agency code
    award_date_gte="2023-01-01",
    fiscal_year=2024,
    naics_code="541511"
)

# Filter by specific agency
contracts = client.list_contracts(
    awarding_agency="4700",  # GSA
    limit=50
)
```

**Available Filter Parameters:**

**Text Search:**
- `keyword` - Search contract descriptions (mapped to 'search' API param)

**Date Filters:**
- `award_date_gte`, `award_date_lte` - Award date range
- `pop_start_date_gte`, `pop_start_date_lte` - Period of performance start date range
- `pop_end_date_gte`, `pop_end_date_lte` - Period of performance end date range
- `expiring_gte`, `expiring_lte` - Contract expiration date range

**Party Filters:**
- `awarding_agency`, `funding_agency` - Agency codes
- `recipient_name`, `recipient_uei` - Vendor/recipient filters

**Classification:**
- `naics_code`, `psc_code` - Industry/product codes
- `set_aside_type` - Set-aside type

**Type Filters:**
- `fiscal_year`, `fiscal_year_gte`, `fiscal_year_lte` - Fiscal year filters
- `award_type` - Award type code

**Identifiers:**
- `piid` - Procurement Instrument Identifier
- `solicitation_identifier` - Solicitation ID

**Sorting:**
- `sort`, `order` - Sort results (e.g., `sort="award_date"`, `order="desc"`)

**Response Options:**
- `shape`, `flat`, `flat_lists` - Response shaping options

### IDVs, OTAs, OTIDVs

```python
# List IDVs (keyset pagination)
idvs = client.list_idvs(limit=25, awarding_agency="4700")

# Get single IDV with shaping
idv = client.get_idv("IDV_KEY", shape=ShapeConfig.IDVS_COMPREHENSIVE)

# OTAs and OTIDVs follow the same pattern
otas = client.list_otas(limit=25)
otidvs = client.list_otidvs(limit=25)
```

### Vehicles

```python
vehicles = client.list_vehicles(search="GSA schedule", shape=ShapeConfig.VEHICLES_MINIMAL)
vehicle = client.get_vehicle("UUID", shape=ShapeConfig.VEHICLES_COMPREHENSIVE)
awardees = client.list_vehicle_awardees("UUID")
```

### Entities (Vendors/Recipients)

```python
# List entities with filters
entities = client.list_entities(search="Booz Allen", state="VA", limit=25)

# Get specific entity by UEI or CAGE code
entity = client.get_entity("ZQGGHJH74DW7")
```

### Forecasts

```python
forecasts = client.list_forecasts(agency="GSA", fiscal_year=2025, limit=25)
```

### Opportunities

```python
opportunities = client.list_opportunities(agency="DOD", active=True, limit=25)
```

### Notices

```python
notices = client.list_notices(agency="DOD", notice_type="award", limit=25)
```

### Grants

```python
grants = client.list_grants(agency="HHS", status="forecasted", limit=25)
```

### Protests

```python
protests = client.list_protests(source_system="gao", outcome="Sustained", limit=25)
protest = client.get_protest("CASE_UUID")
```

### GSA eLibrary Contracts

```python
contracts = client.list_gsa_elibrary_contracts(schedule="MAS", limit=25)
contract = client.get_gsa_elibrary_contract("UUID")
```

### Reference Data

```python
# Offices, organizations, NAICS, subawards, business types
offices = client.list_offices(search="acquisitions")
organizations = client.list_organizations(level=1)
naics = client.list_naics(search="software")
subawards = client.list_subawards(prime_uei="UEI123")
business_types = client.list_business_types()
```

## Pagination

All list methods return a `PaginatedResponse` object with metadata:

```python
response = client.list_contracts(limit=25)

print(f"Total results: {response.count}")
print(f"Next page URL: {response.next}")
print(f"Previous page URL: {response.previous}")

# Iterate through results
for contract in response.results:
    print(contract['description'])

# Get next page
if response.next:
    next_response = client.list_contracts(page=2, limit=25)
```

## Error Handling

The SDK provides specific exception types for different error scenarios:

```python
from tango import (
    TangoClient,
    TangoAPIError,
    TangoAuthError,
    TangoNotFoundError,
    TangoRateLimitError,
    TangoValidationError
)

client = TangoClient(api_key="your-api-key")

try:
    contracts = client.list_contracts(limit=10)
except TangoAuthError:
    print("Invalid API key or authentication required")
except TangoNotFoundError:
    print("Resource not found")
except TangoValidationError as e:
    print(f"Invalid parameters: {e.message}")
    print(f"Details: {e.details}")
except TangoRateLimitError:
    print("Rate limit exceeded")
except TangoAPIError as e:
    print(f"API error: {e.message}")
```

## Advanced Features

### Custom Shapes

Create custom shapes to request exactly the fields you need:

```python
# Simple fields
contracts = client.list_contracts(
    shape="key,piid,description,total_contract_value"
)

# Nested relationships
contracts = client.list_contracts(
    shape="key,piid,recipient(display_name,uei),place_of_performance(*))"
)

# Wildcards for all fields
contracts = client.list_contracts(
    shape="key,piid,recipient(*)"
)
```

### Flattened Responses

Enable flattening to get dot-notation field names:

```python
contracts = client.list_contracts(
    shape="key,piid,recipient(display_name,uei)",
    flat=True
)
# Returns: {"key": "...", "piid": "...", "recipient.display_name": "...", "recipient.uei": "..."}

# Flatten arrays with indexed keys
contracts = client.list_contracts(
    shape="key,transactions(*)",
    flat=True,
    flat_lists=True
)
# Returns: {"key": "...", "transactions.0.action_date": "...", "transactions.0.obligated": "..."}
```

### Type Hints with IDE Support

Import TypedDict types for IDE autocomplete:

```python
from tango import TangoClient, ShapeConfig
from tango.shapes import ContractMinimalShaped

client = TangoClient(api_key="your-api-key")
contracts = client.list_contracts(shape=ShapeConfig.CONTRACTS_MINIMAL)

# Type hint enables IDE autocomplete
contract: ContractMinimalShaped = contracts.results[0]
print(contract["piid"])  # IDE knows this field exists
print(contract["recipient"]["display_name"])  # Nested fields too
```

## Development

This project uses [uv](https://docs.astral.sh/uv/) for dependency management and tooling.

### Setup

```bash
# Clone the repository
git clone https://github.com/makegov/tango-python.git
cd tango-python

# Install dependencies with uv
uv sync --all-extras

# Or install dev dependencies only
uv sync --group dev
```

### Testing

The SDK includes a comprehensive test suite with:
- **Unit tests** - Fast tests for core functionality
- **Integration tests** - Real API validation using VCR.py cassettes

```bash
# Run all tests
uv run pytest

# Run only unit tests
uv run pytest tests/ -m "not integration"

# Run only integration tests
uv run pytest tests/integration/

# Run integration tests with live API (requires TANGO_API_KEY)
export TANGO_API_KEY=your-api-key
export TANGO_USE_LIVE_API=true
uv run pytest tests/integration/

# Refresh cassettes with fresh API responses
export TANGO_API_KEY=your-api-key
export TANGO_REFRESH_CASSETTES=true
uv run pytest tests/integration/
```

See [tests/integration/README.md](tests/integration/README.md) for detailed testing documentation.

### Code Quality

```bash
# Format code
uv run ruff format tango/

# Lint code
uv run ruff check tango/

# Type checking
uv run mypy tango/

# Run all checks
uv run ruff format tango/ && uv run ruff check tango/ && uv run mypy tango/
```

### Project Structure

```
tango-python/
├── tango/                    # Main SDK package
│   ├── __init__.py          # Public API exports
│   ├── client.py            # TangoClient implementation
│   ├── models.py            # Data models and shape configs
│   ├── exceptions.py        # Exception classes
│   └── shapes/              # Dynamic model system
│       ├── __init__.py      # Shapes package exports
│       ├── parser.py        # Shape string parser
│       ├── generator.py     # TypedDict generator
│       ├── factory.py       # Instance factory
│       ├── schema.py        # Schema registry
│       ├── explicit_schemas.py  # Predefined schemas (Contract, Entity, Grant, etc.)
│       ├── models.py        # Shape specification models
│       └── types.py         # TypedDict exports
├── tests/                    # Test suite
│   ├── __init__.py
│   ├── conftest.py          # Pytest configuration
│   ├── test_client.py       # Unit tests for client
│   ├── test_models.py       # Model tests
│   ├── test_shapes.py       # Shape system tests
│   ├── cassettes/           # VCR.py HTTP cassettes
│   └── integration/         # Integration tests
│       ├── __init__.py
│       ├── README.md        # Integration test docs
│       ├── conftest.py      # Integration test fixtures
│       ├── validation.py    # Validation utilities
│       ├── test_agencies_integration.py
│       ├── test_contracts_integration.py
│       ├── test_entities_integration.py
│       ├── test_forecasts_integration.py
│       ├── test_grants_integration.py
│       ├── test_naics_integration.py
│       ├── test_notices_integration.py
│       ├── test_offices_integration.py
│       ├── test_opportunities_integration.py
│       ├── test_organizations_integration.py
│       ├── test_otas_otidvs_integration.py
│       ├── test_protests_integration.py
│       ├── test_reference_data_integration.py
│       ├── test_subawards_integration.py
│       ├── test_vehicles_idvs_integration.py
│       └── test_edge_cases_integration.py
├── docs/                     # Documentation
│   ├── API_REFERENCE.md     # Complete API reference
│   ├── DEVELOPERS.md        # Developer guide
│   ├── SHAPES.md            # Shape system guide
│   └── quick_start.ipynb    # Interactive quick start
├── scripts/                  # Utility scripts
│   ├── README.md
│   ├── check_filter_shape_conformance.py  # Filter + shape conformance (CI)
│   ├── fetch_api_schema.py
│   ├── generate_schemas_from_api.py
│   └── pr_review.py          # PR validation (lint, types, tests, conformance)
├── pyproject.toml           # Project configuration
├── uv.lock                  # Dependency lock file
├── LICENSE                  # MIT License
├── CHANGELOG.md            # Version history
└── README.md               # This file
```

## Documentation

- [Shape System Guide](docs/SHAPES.md) - Comprehensive guide to response shaping
- [API Reference](docs/API_REFERENCE.md) - Detailed API documentation
- [Developer Guide](docs/DEVELOPERS.md) - Technical documentation for developers
- [Quick Start Notebook](docs/quick_start.ipynb) - Interactive Jupyter notebook with examples

## Requirements

- Python 3.12 or higher
- httpx >= 0.27.0

## License

MIT License - see [LICENSE](LICENSE) for details.

## Support

For questions, issues, or feature requests:

- **Email**: [tango@makegov.com](mailto:tango@makegov.com)
- **Issues**: [GitHub Issues](https://github.com/makegov/tango-python/issues)
- **Documentation**: [https://docs.makegov.com/tango-python](https://docs.makegov.com/tango-python)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Run lint and format: `uv run ruff format tango/ && uv run ruff check tango/`
4. Run type checking: `uv run mypy tango/`
5. Run tests: `uv run pytest`
6. (Optional) Run [filter and shape conformance](scripts/README.md#filter-and-shape-conformance) if you have the tango API manifest; CI will run it on push/PR
7. Commit your changes (`git commit -m 'Add amazing feature'`)
8. Push to the branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

For a single command that runs formatting, linting, type checking, and tests (and conformance when the manifest is present), use: `uv run python scripts/pr_review.py --mode full`
