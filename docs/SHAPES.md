# Response Shaping Guide

Response shaping lets you control which fields the API returns, making your requests faster and more efficient. Instead of receiving hundreds of fields you don't need, you specify exactly what you want.

## Why Use Response Shaping?

**Performance Benefits:**
- **60-80% smaller responses** - Faster downloads, lower bandwidth costs
- **Faster API responses** - Less data to process and serialize
- **Clearer code** - Explicitly state what data you're using

**Example:** A full contract response is ~2.4 MB. With shaping, you can reduce it to 320 KB (87% smaller) while getting all the data you actually need.

## Quick Start

```python
from tango import TangoClient

client = TangoClient(api_key="your-api-key")

# Without shaping - returns ALL fields (slower, larger)
contracts = client.list_contracts(limit=10)

# With shaping - returns only what you specify (faster, smaller)
contracts = client.list_contracts(
    limit=10,
    shape="key,piid,recipient(display_name),total_contract_value"
)

# Access the data
for contract in contracts.results:
    print(f"{contract['piid']}: {contract['recipient']['display_name']}")
```

## Basic Shaping

### Simple Fields

List the fields you want, separated by commas:

```python
# Just the basics
contracts = client.list_contracts(
    shape="key,piid,description,award_date",
    limit=10
)

# Access the fields
for contract in contracts.results:
    print(f"{contract['piid']}: {contract['description']}")
    print(f"Date: {contract['award_date']}")
```

### Nested Fields

Use parentheses to select fields from nested objects:

```python
# Get recipient information
contracts = client.list_contracts(
    shape="key,piid,recipient(display_name,uei,cage_code)",
    limit=10
)

for contract in contracts.results:
    recipient = contract['recipient']
    print(f"Recipient: {recipient['display_name']}")
    print(f"UEI: {recipient['uei']}")
```

### Multiple Levels

You can nest as deeply as needed:

```python
# Get location details from recipient
contracts = client.list_contracts(
    shape="key,recipient(display_name,location(city,state_code,zip_code))",
    limit=10
)

for contract in contracts.results:
    location = contract['recipient']['location']
    print(f"{location['city']}, {location['state_code']} {location['zip_code']}")
```

## Common Use Cases

### 1. Quick Lists and Dropdowns

When you just need basic info for a list or dropdown:

```python
# Minimal data for a dropdown
contracts = client.list_contracts(
    shape="key,piid,recipient(display_name)",
    limit=100
)

# Build a dropdown
for contract in contracts.results:
    print(f"{contract['piid']} - {contract['recipient']['display_name']}")
```

### 2. Data Analysis

When analyzing contracts, focus on the metrics:

```python
# Get financial and timing data
contracts = client.list_contracts(
    shape="key,piid,award_date,fiscal_year,total_contract_value,total_obligated",
    awarding_agency="GSA",
    limit=1000
)

# Analyze
total_value = sum(c.get('total_contract_value', 0) for c in contracts.results)
print(f"Total contract value: ${total_value:,.2f}")
```

### 3. Geographic Analysis

When you need location data:

```python
# Get place of performance details
contracts = client.list_contracts(
    shape="key,piid,place_of_performance(city,state_code,congressional_district)",
    limit=100
)

# Group by state
from collections import Counter
states = Counter(c['place_of_performance']['state_code'] for c in contracts.results)
print(f"Top states: {states.most_common(5)}")
```

### 4. Vendor Research

When researching vendors and recipients:

```python
# Get detailed vendor information
entities = client.list_entities(
    shape="uei,legal_business_name,dba_name,business_types,physical_address(city,state_code)",
    limit=50
)

for entity in entities.results:
    print(f"{entity['legal_business_name']}")
    print(f"Business Types: {', '.join(entity.get('business_types', []))}")
    if entity.get('physical_address'):
        addr = entity['physical_address']
        print(f"Location: {addr.get('city')}, {addr.get('state_code')}")
```

### 5. Agency Research

When analyzing agency activity:

```python
# Get agency and classification details
contracts = client.list_contracts(
    shape="key,awarding_agency(name,code),naics(code,description),psc(code,description),total_contract_value",
    fiscal_year=2024,
    limit=500
)

# Analyze by agency
from collections import defaultdict
by_agency = defaultdict(float)
for contract in contracts.results:
    if contract.get('awarding_agency'):
        agency = contract['awarding_agency']['name']
        value = contract.get('total_contract_value', 0)
        by_agency[agency] += value

# Top agencies by value
top_agencies = sorted(by_agency.items(), key=lambda x: x[1], reverse=True)[:10]
for agency, value in top_agencies:
    print(f"{agency}: ${value:,.2f}")
```

## Advanced Techniques

### Using Wildcards

Get all fields from a nested object with `*`:

```python
# Get all recipient fields
contracts = client.list_contracts(
    shape="key,piid,recipient(*)",
    limit=10
)

# All recipient fields are now available
for contract in contracts.results:
    recipient = contract['recipient']
    # Has all fields: display_name, uei, cage_code, legal_business_name, etc.
```

### Flattening Responses

Convert nested structures to flat keys with dot notation:

```python
# Flatten nested objects
contracts = client.list_contracts(
    shape="key,piid,recipient(display_name,uei)",
    flat=True,
    limit=10
)

# Fields are now flattened
for contract in contracts.results:
    print(contract['piid'])
    print(contract['recipient.display_name'])
    print(contract['recipient.uei'])
```

## Best Practices

### 1. Start Minimal, Add as Needed

Start with the minimum fields you need, then add more:

```python
# Start here
shape = "key,piid,recipient(display_name)"

# Add more as you need them
shape = "key,piid,recipient(display_name,uei),total_contract_value"

# Keep adding
shape = "key,piid,recipient(display_name,uei),total_contract_value,award_date,fiscal_year"
```

### 2. Use Shapes for Large Queries

The bigger the query, the more important shaping becomes:

```python
# Small query - shaping optional
contracts = client.list_contracts(limit=5)

# Medium query - shaping recommended
contracts = client.list_contracts(
    shape="key,piid,recipient(display_name),total_contract_value",
    limit=100
)

# Large query - shaping highly recommended
contracts = client.list_contracts(
    shape="key,piid,recipient(display_name),total_contract_value",
    limit=1000
)
```

### 3. Reuse Common Shapes

Define shapes as constants for reuse:

```python
# Define your common shapes
SHAPES = {
    'list': "key,piid,recipient(display_name),total_contract_value",
    'detail': "key,piid,description,recipient(*),awarding_agency(*),total_contract_value,award_date",
    'analysis': "key,fiscal_year,total_contract_value,total_obligated,award_date",
    'geographic': "key,piid,place_of_performance(city,state_code,congressional_district)"
}

# Use them
contracts = client.list_contracts(shape=SHAPES['list'], limit=100)
contract_detail = client.list_contracts(shape=SHAPES['detail'], limit=1)
```

### 4. Document Your Shapes

When using custom shapes in production, document why you chose those fields:

```python
# Dashboard summary shape
# - key: Contract identifier
# - piid: Display to users
# - recipient.display_name: Main label
# - total_contract_value: Summary metric
DASHBOARD_SHAPE = "key,piid,recipient(display_name),total_contract_value"

contracts = client.list_contracts(shape=DASHBOARD_SHAPE, limit=50)
```

## Field Reference

### Common Contract Fields

**Identifiers:**
- `key` - Unique contract identifier
- `piid` - Procurement Instrument Identifier
- `award_id` - Award identifier

**Basic Info:**
- `description` - Contract description
- `award_date` - Date awarded
- `fiscal_year` - Fiscal year

**Financial:**
- `total_contract_value` - Total contract value
- `total_obligated` - Total obligated amount
- `award_amount` - Initial award amount

**Parties:**
- `recipient(...)` - The vendor/recipient
- `awarding_agency(...)` - The agency awarding the contract
- `funding_agency(...)` - The agency funding the contract

**Classification:**
- `naics(code,description)` - Industry classification
- `psc(code,description)` - Product/Service code

**Location:**
- `place_of_performance(...)` - Where work is performed
- `recipient_location(...)` - Vendor location

### Common Entity Fields

**Basic:**
- `uei` - Unique Entity Identifier
- `cage_code` - Commercial and Government Entity code
- `legal_business_name` - Official business name
- `display_name` - Display name
- `dba_name` - Doing Business As name

**Classification:**
- `business_types` - Array of business type codes
- `primary_naics` - Primary NAICS code
- `naics_codes` - All NAICS codes

**Contact:**
- `email_address` - Email
- `entity_url` - Website
- `physical_address(...)` - Physical address
- `mailing_address(...)` - Mailing address

**Financial:**
- `federal_obligations` - Total federal obligations

## Performance Comparison

Here's what you can expect when using shapes:

| Use Case | Fields Returned | Payload Size | vs. Full Response |
|----------|----------------|--------------|-------------------|
| Full response | ~200 fields | 2.4 MB | Baseline |
| Dropdown | 3-4 fields | 180 KB | 92% smaller |
| List view | 6-8 fields | 320 KB | 87% smaller |
| Detail view | 20-30 fields | 780 KB | 68% smaller |
| Analysis | 8-10 fields | 250 KB | 90% smaller |

## Troubleshooting

### Fields Not Appearing

If fields aren't showing up in the response:

1. **Check your shape syntax** - Make sure parentheses match and commas are correct
2. **Field doesn't exist** - The field might not exist for that record
3. **Typo** - Double-check field names (they're case-sensitive)

```python
# ❌ Wrong
shape = "key,piid recipient(display_name)"  # Missing comma

# ✅ Correct
shape = "key,piid,recipient(display_name)"
```

### Unexpected Structure

If the structure isn't what you expected:

```python
# Shape specifies nested structure
contracts = client.list_contracts(
    shape="key,recipient(display_name,uei)",
    limit=1
)

# Access nested fields
contract = contracts.results[0]
print(contract['recipient']['display_name'])  # Nested access
print(contract['recipient']['uei'])

# Use .get() for safety
display_name = contract.get('recipient', {}).get('display_name', 'Unknown')
```

## Examples by Resource Type

### Contracts

```python
# Minimal for lists
"key,piid,recipient(display_name),total_contract_value"

# For analysis
"key,fiscal_year,award_date,total_contract_value,total_obligated,naics(code)"

# For geographic analysis
"key,piid,place_of_performance(city,state_code,congressional_district)"

# Full detail
"key,piid,description,recipient(*),awarding_agency(*),total_contract_value,award_date,naics(*),psc(*)"
```

### Entities

```python
# Minimal for lookups
"uei,legal_business_name,cage_code,business_types"

# For vendor research
"uei,legal_business_name,dba_name,business_types,physical_address(city,state_code),primary_naics"

# Full profile
"uei,legal_business_name,dba_name,cage_code,business_types,physical_address(*),email_address,entity_url"
```

### Forecasts

```python
# Minimal
"id,title,anticipated_award_date,fiscal_year"

# With classification
"id,title,anticipated_award_date,fiscal_year,naics_code,status"
```

### Opportunities

```python
# Minimal
"opportunity_id,title,solicitation_number,response_deadline"

# With details
"opportunity_id,title,solicitation_number,description,response_deadline,active,naics_code,psc_code"
```

## Next Steps

- **Try the examples** - Copy and paste these examples to get started
- **Experiment** - Start with minimal shapes and add fields as needed
- **Profile your queries** - Use network tools to see the size difference
- **Define patterns** - Create reusable shapes for your common queries

For more help, see:
- [Quick Start Guide](quick_start.ipynb) - Interactive examples
- [API Reference](API_REFERENCE.md) - Complete field listings