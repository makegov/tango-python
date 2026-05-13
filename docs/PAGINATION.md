# Pagination

The SDK uses two pagination strategies depending on the endpoint.

For per-method pagination parameters, see [`API_REFERENCE.md`](API_REFERENCE.md). This guide is the conceptual overview and iteration patterns.

## Page-Based Pagination

Most endpoints use traditional page-based pagination with `page` and `limit` parameters.

```python
from tango import TangoClient

client = TangoClient()

# First page
resp = client.list_entities(search="Booz Allen", limit=25)
print(f"Total: {resp.count}")
print(f"This page: {len(resp.results)}")
print(f"Next: {resp.next}")

# Next page
resp2 = client.list_entities(search="Booz Allen", limit=25, page=2)
```

### Iterating All Pages

```python
page = 1
all_results = []

while True:
    resp = client.list_entities(search="Booz Allen", limit=100, page=page)
    all_results.extend(resp.results)
    if not resp.next:
        break
    page += 1

print(f"Fetched {len(all_results)} of {resp.count} entities")
```

**Endpoints using page-based pagination:** entities, forecasts, opportunities, notices, grants, protests, subawards, vehicles, vehicle awardees, organizations, GSA eLibrary contracts, IT Dashboard investments, agencies, offices, business types, NAICS, webhook subscriptions, webhook endpoints.

## Cursor-Based Pagination

High-volume award endpoints use cursor-based (keyset) pagination for better performance on large datasets. Instead of a page number, you pass a `cursor` token from the previous response.

```python
from urllib.parse import parse_qs, urlparse

from tango import TangoClient

client = TangoClient()

# First page
resp = client.list_contracts(limit=25, sort="award_date", order="desc")
print(f"Total: {resp.count}")

# Get cursor from the next URL
if resp.next:
    qs = parse_qs(urlparse(resp.next).query)
    cursor = qs.get("cursor", [None])[0]

    # Fetch next page
    resp2 = client.list_contracts(
        limit=25,
        cursor=cursor,
        sort="award_date",
        order="desc",
    )
```

### Iterating All Pages

```python
from urllib.parse import parse_qs, urlparse

all_results = []
cursor = None

while True:
    resp = client.list_contracts(
        keyword="cloud",
        limit=100,
        cursor=cursor,
        sort="award_date",
        order="desc",
    )
    all_results.extend(resp.results)

    if not resp.next:
        break
    qs = parse_qs(urlparse(resp.next).query)
    cursor = qs.get("cursor", [None])[0]

print(f"Fetched {len(all_results)} of {resp.count} contracts")
```

**Endpoints using cursor-based pagination:** contracts, IDVs, IDV awards, IDV child IDVs, IDV transactions, OTAs, OTIDVs.

## PaginatedResponse

All list methods return a `PaginatedResponse` object:

| Field | Type | Description |
|---|---|---|
| `count` | `int` | Total number of results available |
| `next` | `str \| None` | Full URL for the next page, or `None` |
| `previous` | `str \| None` | Full URL for the previous page, or `None` |
| `results` | `list[T]` | List of results for this page |
| `cursor` | `str \| None` | Cursor token (cursor-based endpoints only) |
| `page_metadata` | `dict \| None` | Optional additional page metadata |
