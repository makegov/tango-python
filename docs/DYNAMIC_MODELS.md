# Tango Python SDK – Dynamic Models Guide

This document explains how the **Python dynamic shaping system** works.
It mirrors the Node.js `DYNAMIC_MODELS.md` guide for the Python SDK.

---

## Overview

Tango's dynamic modeling allows you to:

- Request _exactly the fields you want_
- Validate the shape string against Tango's schemas
- Generate a typed model descriptor at runtime
- Materialize shaped objects using correct:
  - date parsing
  - datetime parsing
  - decimal handling
  - list vs scalar logic
  - nested structure

---

## Components

### ShapeParser

Parses shape strings into a `ShapeSpec`.

```python
from tango.shapes import ShapeParser

parser = ShapeParser()
spec = parser.parse("key,piid,recipient(display_name)")
```

### SchemaRegistry

Holds the field schemas for all models.

```python
from tango.shapes import SchemaRegistry
from tango.models import Contract

registry = SchemaRegistry()
schema = registry.get_schema(Contract)
award_date_field = schema["award_date"]
# FieldSchema(name='award_date', type=date | None)
```

### TypeGenerator

Builds a dynamic `TypedDict`-backed type from `(shape_spec, base_model)`.

```python
from tango.shapes import ShapeParser, TypeGenerator
from tango.models import Contract

parser = ShapeParser()
spec = parser.parse("key,piid,recipient(display_name)")

gen = TypeGenerator()
dynamic_type = gen.generate_type(
    shape_spec=spec,
    base_model=Contract,
    type_name="ContractShaped",
)
```

### ModelFactory

Takes a dynamic type + raw API JSON and produces typed `ShapedModel` instances.
The `TangoClient` uses this pipeline automatically after fetching data.

```python
from tango import TangoClient

client = TangoClient(api_key="your-api-key")
contracts = client.list_contracts(
    shape="key,award_date,recipient(display_name)",
)

# contracts.results are ShapedModel instances materialized by ModelFactory:
# - date/datetime strings parsed to date/datetime objects
# - decimals normalized via Decimal
# - nested structures are themselves ShapedModel instances
```

---

## Example: Full Shaping Pipeline (manual)

```python
from tango.shapes import ShapeParser, TypeGenerator, ModelFactory, create_default_parser_registry
from tango.models import Contract

parser = ShapeParser()
spec = parser.parse("key,award_date,recipient(display_name)")

gen = TypeGenerator()
dynamic_type = gen.generate_type(
    shape_spec=spec,
    base_model=Contract,
    type_name="ContractShaped",
)

parsers = create_default_parser_registry()
factory = ModelFactory(gen, parsers)

shaped = factory.create_instance(
    data={
        "key": "C-1",
        "award_date": "2024-01-15",
        "recipient": {"display_name": "Acme"},
    },
    shape_spec=spec,
    base_model=Contract,
    dynamic_type=dynamic_type,
)
```

`shaped` becomes:

```python
ContractShaped(key='C-1', award_date=datetime.date(2024, 1, 15), recipient=ContractShaped_Recipient(display_name='Acme'))
```

---

## Attribute Access

`ShapedModel` is a `dict` subclass with `__getattr__` so fields are accessible
both as dictionary keys and as attributes:

```python
# Both styles work
shaped["key"]           # "C-1"
shaped.key              # "C-1"

# Nested models are also ShapedModel instances
shaped.recipient["display_name"]   # "Acme"
shaped.recipient.display_name      # "Acme"
```

Accessing a field that was not included in your shape raises a descriptive
`AttributeError` with suggestions:

```python
shaped.award_amount
# AttributeError: Field 'award_amount' not found in ContractShaped.
#   Available fields: 'key', 'award_date', 'recipient'
#   This field may not be included in your shape specification.
#   To include this field, add it to your shape parameter.
```

---

## Type Safety

The Python SDK enforces shape correctness at parse time via `ShapeParser.validate()`.
Nested structures are recursively materialized as `ShapedModel` instances, guaranteeing
the same access patterns at every depth. No static class generation happens at build time;
shapes are resolved at runtime.

---

## Caching

`TypeGenerator` caches descriptors using a thread-safe LRU cache (default: 100 entries).

`ShapeParser` also caches parse results keyed on the raw shape string.

---

## Nested Models

If a field is nested in the schema (e.g. `"recipient"` → `RecipientProfile`),
the generator recursively builds the nested descriptor, naming it
`{ParentType}_{FieldName}` (e.g. `ContractShaped_Recipient`). Each nested object
is also a `ShapedModel`, so attribute access and `repr` work uniformly at every level.

---

## Predefined Shape Constants

`ShapeConfig` provides opinionated defaults for each resource's list and detail methods.
Each `TangoClient` method applies its corresponding default automatically; pass `shape=`
to override.

```python
from tango import TangoClient, ShapeConfig

client = TangoClient(api_key="your-api-key")

# These are equivalent — list_contracts defaults to CONTRACTS_MINIMAL
contracts = client.list_contracts(limit=10)
contracts = client.list_contracts(shape=ShapeConfig.CONTRACTS_MINIMAL, limit=10)

# Other resources
entities = client.list_entities(shape=ShapeConfig.ENTITIES_MINIMAL)
idvs = client.list_idvs(shape=ShapeConfig.IDVS_MINIMAL)
```

See [API Reference – ShapeConfig](API_REFERENCE.md#shapeconfig-predefined-shapes) for the
full table of constants.
