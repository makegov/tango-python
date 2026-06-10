# Dynamic Models User Guide

The Tango SDK uses dynamic models that generate runtime types matching the exact structure of API responses based on shape parameters. This provides better type safety, IDE autocomplete, and developer experience.

## Table of Contents

- [Overview](#overview)
- [Benefits](#benefits)
- [Getting Started](#getting-started)
- [Using Predefined Shapes](#using-predefined-shapes)
- [Creating Custom Shapes](#creating-custom-shapes)
- [Type Hints and IDE Support](#type-hints-and-ide-support)
- [Performance Considerations](#performance-considerations)
- [Troubleshooting](#troubleshooting)
- [SDK conformance (maintainers)](#sdk-conformance-maintainers)

## Overview

The SDK uses dynamic models that generate types at runtime to match the exact fields you request through response shaping. This means you only get the fields you need, with accurate type information for IDE autocomplete and type checking.

**Dynamic models approach:**
```python
# Returns typed dict with only requested fields
contracts = client.list_contracts(
    shape="key,piid,recipient(display_name)"
)
contract = contracts.results[0]
# contract["key"] ✓
# contract["piid"] ✓
# contract["recipient"]["display_name"] ✓
# No other fields exist - cleaner and more memory efficient
```

## Benefits

### 1. Accurate Type Information
Your IDE and type checkers understand exactly what fields are available:

```python
# With dynamic models, your IDE knows these fields exist
contract["key"]  # ✓ Autocomplete works
contract["piid"]  # ✓ Type checker validates
contract["recipient"]["display_name"]  # ✓ Nested fields work

# Fields not in shape don't exist
contract["award_date"]  # ✗ KeyError at runtime, caught by type checker
```

### 2. Better IDE Autocomplete
Get accurate autocomplete suggestions for only the fields in your shape:

```python
contracts = client.list_contracts(
    shape=ShapeConfig.CONTRACTS_MINIMAL,
)
contract = contracts.results[0]
# Typing "contract[" shows only: key, piid, award_date, award_type,
# recipient, description, total_contract_value
```

### 3. Memory Efficiency
Dynamic models only store the fields you requested, reducing memory usage by 60-80%:

```python
# Static model: ~2KB per contract (50+ fields, mostly None)
# Dynamic model with MINIMAL shape: ~400 bytes per contract (7 fields)
# 5x memory reduction for large datasets
```

### 4. Runtime Validation
Catch shape mismatches early with clear error messages:

```python
# If you request a field that doesn't exist
contracts = client.list_contracts(
    shape="key,invalid_field",
)
# ShapeValidationError: Field 'invalid_field' does not exist in Contract
```

### 5. Cleaner Data Structures
No more `None` fields cluttering your objects:

```python
# Static model
print(contract)  # Shows 50+ fields, most are None

# Dynamic model
print(contract)  # Shows only the 7 fields you requested
```

## Getting Started

### Installation

Dynamic models are included in all versions of the Tango SDK. No additional installation required.

```bash
pip install tango-python
```

### Basic Usage

Dynamic models are always enabled. Simply use shape parameters to specify which fields you need:

```python
from tango import TangoClient, ShapeConfig

client = TangoClient(api_key="your-api-key")

# All shaped requests use dynamic models
contracts = client.list_contracts(
    shape=ShapeConfig.CONTRACTS_MINIMAL,
    limit=10
)

# Access fields using dictionary syntax
for contract in contracts.results:
    print(f"Contract: {contract['piid']}")
    print(f"Recipient: {contract['recipient']['display_name']}")
    print(f"Amount: ${contract['total_contract_value']}")
```

## Using Predefined Shapes

The SDK includes 25+ predefined shapes optimized for common use cases. These shapes provide precise type definitions for IDE autocomplete:

### Contracts

```python
from tango import TangoClient, ShapeConfig

client = TangoClient(api_key="your-key")

# Default minimal shape for lists
contracts = client.list_contracts(
    shape=ShapeConfig.CONTRACTS_MINIMAL,
    limit=100
)
# Fields: key, piid, award_date, recipient(display_name), description, total_contract_value

# Or use a custom shape for specific needs
contracts = client.list_contracts(
    shape="key,piid,recipient(display_name),total_contract_value",
    limit=100
)
```

### Entities

```python
# Fast lookups (default for list_entities)
entities = client.list_entities(
    shape=ShapeConfig.ENTITIES_MINIMAL,
    limit=50
)
# Fields: uei, legal_business_name, cage_code, business_types
# Note: Entities do NOT have a 'key' field - use 'uei' as identifier

# Full vendor details (default for get_entity)
entities = client.list_entities(
    shape=ShapeConfig.ENTITIES_COMPREHENSIVE,
    limit=50
)
# Fields: uei, legal_business_name, dba_name, cage_code,
#         business_types, primary_naics, naics_codes, psc_codes,
#         email_address, entity_url, description, capabilities, keywords,
#         physical_address, mailing_address,
#         federal_obligations(*), congressional_district
```

### Forecasts, Opportunities, Notices

Each resource type has predefined minimal shapes:

```python
# Forecasts
forecasts = client.list_forecasts(shape=ShapeConfig.FORECASTS_MINIMAL)

# Opportunities
opportunities = client.list_opportunities(shape=ShapeConfig.OPPORTUNITIES_MINIMAL)

# Notices
notices = client.list_notices(shape=ShapeConfig.NOTICES_MINIMAL)
```

## Creating Custom Shapes

Create your own shapes for specialized use cases:

### Simple Custom Shapes

```python
# Select specific fields
custom_shape = "key,piid,award_date,total_contract_value"
contracts = client.list_contracts(shape=custom_shape)

for contract in contracts.results:
    print(f"{contract['piid']}: ${contract['total_contract_value']}")
```

### Nested Field Selection

```python
# Select specific fields from nested objects
custom_shape = "key,piid,recipient(display_name,uei,cage_code)"
contracts = client.list_contracts(shape=custom_shape)

for contract in contracts.results:
    recipient = contract['recipient']
    if recipient:
        print(f"Recipient: {recipient['display_name']}")
        print(f"UEI: {recipient['uei']}")
        print(f"CAGE: {recipient['cage_code']}")
```

### Multiple Nested Objects

```python
# Select from multiple nested relations
# Note: awarding_office(*) returns organization_id, office_code, office_name,
#       agency_code, agency_name, department_code, department_name
# Note: place_of_performance uses city_name (not city); no congressional_district
custom_shape = (
    "key,piid,award_date,"
    "recipient(display_name,uei),"
    "awarding_office(office_code,office_name,agency_code,agency_name,department_code,department_name),"
    "place_of_performance(city_name,state_code,state_name,country_code,country_name)"
)
contracts = client.list_contracts(shape=custom_shape)

for contract in contracts.results:
    print(f"Contract: {contract['piid']}")
    print(f"Recipient: {contract['recipient']['display_name']}")
    office = contract.get('awarding_office', {})
    print(f"Agency: {office.get('agency_name')} ({office.get('agency_code')})")
    print(f"Department: {office.get('department_name')}")
    location = contract.get('place_of_performance', {})
    print(f"Location: {location.get('city_name')}, "
          f"{location.get('state_name') or location.get('state_code')}, "
          f"{location.get('country_name') or location.get('country_code')}")
```

### Using Wildcards

```python
# Get all fields from a nested object
custom_shape = "key,piid,recipient(*)"
contracts = client.list_contracts(shape=custom_shape)

# recipient now includes all available fields
for contract in contracts.results:
    recipient = contract['recipient']
    if recipient:
        # All recipient fields are available
        print(recipient.keys())
```

### Field Aliasing

```python
# Rename fields in the response
custom_shape = "key,piid,recipient(display_name::vendor_name,uei)"
contracts = client.list_contracts(shape=custom_shape)

for contract in contracts.results:
    # Access using the alias
    print(f"Vendor: {contract['recipient']['vendor_name']}")
```

## Type Hints and IDE Support

Dynamic models provide excellent type checking and IDE support:

### With Predefined Shapes

```python
from tango import TangoClient, ShapeConfig
from tango.shapes import ContractMinimalShaped

client = TangoClient(api_key="your-key")

# Type checkers understand predefined shapes
contracts = client.list_contracts(
    shape=ShapeConfig.CONTRACTS_MINIMAL,
    limit=10
)

# Use type hints for IDE autocomplete
contract: ContractMinimalShaped = contracts.results[0]
contract["key"]  # ✓ IDE suggests this
contract["piid"]  # ✓ IDE suggests this
contract["recipient"]["display_name"]  # ✓ IDE suggests this
contract["invalid_field"]  # ✗ Type checker warns
```

### Type Annotations

```python
from typing import TypedDict, List

# Define your expected shape type
class ContractMinimal(TypedDict):
    key: str
    piid: str | None
    award_date: str | None
    award_type: str | None
    recipient: dict | None
    description: str
    total_contract_value: str | None

def process_contracts(contracts: List[ContractMinimal]) -> None:
    for contract in contracts:
        # Type checker validates field access
        print(contract["piid"])
```

### Using mypy

```python
from tango.shapes import ContractMinimalShaped

# mypy will validate your code
contracts = client.list_contracts(shape=ShapeConfig.CONTRACTS_MINIMAL)

for contract in contracts.results:
    # ✓ mypy validates this
    piid: str | None = contract["piid"]
    
    # ✗ mypy catches this error
    invalid: str = contract["nonexistent_field"]
```

### Using pyright/pylance

```python
# Pyright provides excellent autocomplete and validation
contracts = client.list_contracts(shape=ShapeConfig.CONTRACTS_MINIMAL)

contract = contracts.results[0]
# Hover over contract to see its type
# Ctrl+Space shows available fields
```



## Performance Considerations

### Type Generation Performance

Dynamic models generate types on first use and cache them:

```python
# First request: generates type (~5-10ms)
contracts = client.list_contracts(shape=ShapeConfig.CONTRACTS_MINIMAL)

# Subsequent requests: uses cached type (~0.1ms)
more_contracts = client.list_contracts(shape=ShapeConfig.CONTRACTS_MINIMAL)
```

**Performance characteristics:**
- Type generation: < 10ms for typical shapes
- Cache lookup: < 0.1ms
- Memory usage: 60-80% reduction for shaped responses

### Caching Strategy

The SDK caches generated types automatically:

```python
# These use the same cached type
contracts1 = client.list_contracts(shape="key,piid")
contracts2 = client.list_contracts(shape="key,piid")
contracts3 = client.list_contracts(shape="key,piid")
# Type generated once, reused 3 times
```

### Pre-warming the Cache

For performance-critical applications, pre-generate types:

```python
# Pre-warm cache with common shapes
common_shapes = [
    ShapeConfig.CONTRACTS_MINIMAL,
    ShapeConfig.ENTITIES_MINIMAL,
    ShapeConfig.IDVS_MINIMAL,
]

for shape in common_shapes:
    # Make a minimal request to generate and cache the type
    client.list_contracts(shape=shape, limit=1)

# Now all subsequent requests use cached types
```

### Memory Optimization

Dynamic models use significantly less memory:

```python
# Example: Fetching 10,000 contracts with MINIMAL shape
contracts = client.list_contracts(
    shape=ShapeConfig.CONTRACTS_MINIMAL,
    limit=10000
)
# ~4 MB (7 fields per contract)
# 80% memory reduction compared to full responses
```

## Troubleshooting

### Common Issues

#### Issue: "Field 'X' does not exist in Model"

**Cause:** You requested a field that doesn't exist in the model schema.

**Solution:** Check the field name spelling and refer to the API documentation.

```python
# ✗ Wrong
contracts = client.list_contracts(shape="key,piid,invalid_field")
# ShapeValidationError: Field 'invalid_field' does not exist in Contract

# ✓ Correct
contracts = client.list_contracts(shape="key,piid,award_date")
```

#### Issue: KeyError when accessing fields

**Cause:** Trying to access a field that wasn't included in the shape.

**Solution:** Add the field to your shape or check if the field exists before accessing.

```python
# ✗ Wrong
contracts = client.list_contracts(shape="key,piid")
contract = contracts.results[0]
print(contract["award_date"])  # KeyError: 'award_date'

# ✓ Correct - include field in shape
contracts = client.list_contracts(shape="key,piid,award_date")
contract = contracts.results[0]
print(contract["award_date"])  # Works

# ✓ Correct - check before accessing
contract = contracts.results[0]
if "award_date" in contract:
    print(contract["award_date"])
```

#### Issue: Type checker doesn't recognize fields

**Cause:** Using custom shapes without type annotations.

**Solution:** Add type annotations for custom shapes or use predefined shapes.

```python
from typing import TypedDict

# Define your shape type
class MyCustomShape(TypedDict):
    key: str
    piid: str | None
    award_date: str | None

# Use type annotation
contracts = client.list_contracts(shape="key,piid,award_date")
contract: MyCustomShape = contracts.results[0]
# Now type checker understands the structure
```

#### Issue: Performance slower than expected

**Cause:** Shapes not being reused or cache thrashing.

**Solution:** Reuse shapes consistently.

```python
# Reuse shapes
COMMON_SHAPE = "key,piid,recipient(display_name)"
contracts1 = client.list_contracts(shape=COMMON_SHAPE)
contracts2 = client.list_contracts(shape=COMMON_SHAPE)
# Second request uses cached type
```

### Debugging

Enable debug logging to see what's happening:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('tango')

# Now you'll see cache hits/misses and type generation
contracts = client.list_contracts(shape=ShapeConfig.CONTRACTS_MINIMAL)
```

### Getting Help

If you encounter issues:

1. Check the [API Reference](API_REFERENCE.md) for detailed documentation
2. Review the [Migration Guide](MIGRATION_GUIDE.md) for common patterns
3. See [examples/](../examples/) for working code samples
4. Contact support at [tango@makegov.com](mailto:tango@makegov.com)

## SDK conformance (maintainers)

The SDK is kept in sync with the Tango API and its own shape schemas via conformance checks against the canonical API contract, which is **vendored** in this repo at `contracts/filter_shape_contract.json`. All checks run in CI on every push and PR (see [Lint workflow](../.github/workflows/lint.yml)) and locally with [scripts/check_filter_shape_conformance.py](../scripts/check_filter_shape_conformance.py) — no extra setup needed.

### The contract

- **Source:** Generated by the [tango](https://github.com/makegov/tango) repo's `scripts/filter_shape_conformance.py` from the API runtime (FilterSets, ordering fields, shape specs). Since `schema_version: 2` it carries per-filter type metadata (`filter_params_detail`: value type, choices, filter class).
- **Vendored copy:** `contracts/filter_shape_contract.json` pins exactly which API surface this SDK version conforms to. Refresh it with `uv run python scripts/refresh_contract.py` (reads the sibling `../tango` checkout, falling back to the GitHub API via `gh`). CI emits a staleness notice when the vendored copy drifts from tango HEAD.

### Filter conformance

- **Coverage:** Every list endpoint in the contract has a mapped SDK method exposing the contract's filter params — explicit arguments or via the method's `api_param_mapping`. Missing params are **errors**, unless listed in `contracts/conformance_baseline.json`, which downgrades them to warnings as tracked backlog (remove the baseline entry in the same PR that adds the param). Run `--suggest` for ready-to-paste typed parameter scaffolds.
- **Staleness:** Every filter-like SDK argument must resolve to a param the API still accepts — a stale param silently no-ops for users, so this is always an **error** (deprecate the argument, don't just delete it; the surface is contract).
- **Types:** Each SDK argument's annotation must be compatible with the contract value type (`date`/`choice`/`ordering` → `str`, `boolean` → `bool`, `number` → `int`/`float`/`str`; `string` is the API's catch-all and doesn't constrain).
- **Warnings:** Methods that take filters only via `**kwargs` are reported as warnings (filter names cannot be verified against the contract).

### Shape conformance

- **What it checks:** Every predefined shape in `ShapeConfig` (e.g. `CONTRACTS_MINIMAL`, `IDVS_MINIMAL`, `GRANTS_MINIMAL`) is parsed and validated against the SDK’s explicit schemas in `tango/shapes/explicit_schemas.py`. Each shape must only reference fields that exist for that model (including nested fields).
- **Why it matters:** Ensures default shapes never reference invalid or renamed fields, so default list/get behavior stays valid after schema or API changes.
- **Errors:** Parse failures or invalid field names in any `ShapeConfig` constant are reported as errors and fail the check.

### Running the conformance check

```bash
# Full check against the vendored contract (what CI runs)
uv run python scripts/check_filter_shape_conformance.py

# Scaffolds for missing params; unmapped-resource checklist
uv run python scripts/check_filter_shape_conformance.py --suggest
uv run python scripts/check_filter_shape_conformance.py --list-unmapped

# Refresh the vendored contract from tango
uv run python scripts/refresh_contract.py
```

- **Output:** JSON with `errors` and `warnings`. Exit code 1 if there are any errors. See [scripts/README.md](../scripts/README.md#filter-and-shape-conformance) for full usage.
- **When the API adds a filter:** refresh the contract, run `--suggest`, add the param (or baseline it deliberately), and commit the refreshed contract together with the SDK change.

## Next Steps

- Read the [API Reference](API_REFERENCE.md) for detailed class and method documentation
- Check the [Migration Guide](MIGRATION_GUIDE.md) to migrate existing code
- Explore [code examples](../examples/) for common use cases
- Learn about [Response Shaping](SHAPES.md) to optimize your queries

---

**See also:**
- [Response Shaping Guide](SHAPES.md)
- [API Reference](API_REFERENCE.md)
- [Migration Guide](MIGRATION_GUIDE.md)
- [Type Hints Limitations](TYPE_HINTS_LIMITATIONS.md)
