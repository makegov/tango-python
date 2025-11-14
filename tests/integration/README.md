# Integration Tests

This directory contains integration tests for the Tango API client that validate the client against real API responses using production data.

## Overview

Integration tests use [pytest-recording](https://github.com/kiwicom/pytest-recording) (VCR.py) to record and replay HTTP interactions. This allows tests to:

- Validate parsing logic against real API responses
- Run quickly without network access (using cached responses)
- Detect API schema changes
- Test with production data without hitting rate limits

## Pytest Markers

The following pytest markers are available for integration tests:

### `@pytest.mark.integration`

Marks tests as integration tests that may hit external APIs. All tests in this directory should use this marker.

**Usage:**
```python
@pytest.mark.integration
class TestContractsIntegration:
    def test_list_contracts(self, tango_client):
        # Test implementation
        pass
```

### `@pytest.mark.vcr()`

Enables VCR recording/playback for HTTP interactions. This marker is automatically applied to all test classes in this directory.

**Usage:**
```python
@pytest.mark.vcr()
@pytest.mark.integration
class TestContractsIntegration:
    # Tests will use cassettes for HTTP recording/playback
    pass
```

### `@pytest.mark.live`

Forces tests to always use the live API, skipping cassettes. Use this for tests that must validate against current API state.

**Usage:**
```python
@pytest.mark.live
@pytest.mark.integration
def test_api_current_state(tango_client):
    # This test will always hit the live API
    pass
```

### `@pytest.mark.cached`

Forces tests to only run with cached responses. Tests will fail if cassettes don't exist. Use this for CI/CD pipelines where you want to ensure tests don't hit the live API.

**Usage:**
```python
@pytest.mark.cached
@pytest.mark.integration
def test_with_cached_only(tango_client):
    # This test will only use cassettes, never live API
    pass
```

### `@pytest.mark.slow`

Marks tests that are slow to execute (e.g., tests with large result sets or multiple API calls). Use this to allow selective test execution.

**Usage:**
```python
@pytest.mark.slow
@pytest.mark.integration
def test_large_dataset(tango_client):
    # This test processes many results and may be slow
    response = tango_client.list_contracts(limit=100)
    # ...
```

## Running Tests

### Default Mode (Cached Responses)

Run all integration tests using cached responses (cassettes) if available:

```bash
pytest tests/integration/
```

This is the fastest mode and doesn't require network access or an API key.

### Live API Mode

Run tests against the live API (requires `TANGO_API_KEY` environment variable):

```bash
export TANGO_API_KEY=your-api-key-here
export TANGO_USE_LIVE_API=true
pytest tests/integration/
```

### Refresh Cassettes Mode

Re-record all cassettes with fresh API responses:

```bash
export TANGO_API_KEY=your-api-key-here
export TANGO_REFRESH_CASSETTES=true
pytest tests/integration/
```

### Selective Test Execution

Run only specific test files:

```bash
pytest tests/integration/test_contracts_integration.py
```

Run only tests with specific markers:

```bash
# Run only integration tests (excludes unit tests)
pytest -m integration

# Run only slow tests
pytest -m slow

# Run integration tests but exclude slow ones
pytest -m "integration and not slow"

# Run only live API tests
pytest -m live
```

Run a specific test:

```bash
pytest tests/integration/test_contracts_integration.py::TestContractsIntegration::test_list_contracts_minimal_shape
```

## Environment Variables

Configure test behavior using environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `TANGO_API_KEY` | None | Your Tango API key (required for live tests) |
| `TANGO_USE_LIVE_API` | `false` | Set to `true` to always use live API |
| `TANGO_REFRESH_CASSETTES` | `false` | Set to `true` to re-record all cassettes |

### Using .env File

Create a `.env` file in the project root (copy from `.env.example`):

```bash
# .env
TANGO_API_KEY=your-api-key-here
TANGO_USE_LIVE_API=false
TANGO_REFRESH_CASSETTES=false
```

The test suite will automatically load these variables using `python-dotenv`.

## Test Organization

Integration tests are organized by API resource:

- `test_agencies_integration.py` - Agency endpoints
- `test_contracts_integration.py` - Contract endpoints (most comprehensive)
- `test_entities_integration.py` - Entity search and retrieval
- `test_forecasts_integration.py` - Forecast endpoints
- `test_opportunities_integration.py` - Opportunity endpoints
- `test_notices_integration.py` - Notice endpoints
- `test_edge_cases_integration.py` - Edge cases and error handling

## Cassette Management

### Cassette Location

HTTP interaction recordings (cassettes) are stored in `tests/cassettes/` as YAML files.

### Cassette Format

Cassettes contain:
- Request details (method, URL, headers, body)
- Response details (status, headers, body)
- Metadata (VCR version, interaction count)

**Note:** API keys are automatically filtered from cassettes for security.

### When to Refresh Cassettes

Refresh cassettes when:
- The Tango API adds or changes fields
- You add new client methods or tests
- You fix parsing issues and need updated test data
- Cassettes become stale (monthly or quarterly refresh recommended)

### Refreshing Specific Cassettes

Delete specific cassettes to force re-recording:

```bash
# Delete all cassettes
rm -rf tests/cassettes/*.yaml

# Delete cassettes for a specific test file
rm tests/cassettes/TestContractsIntegration.*.yaml

# Re-record
export TANGO_API_KEY=your-api-key-here
pytest tests/integration/test_contracts_integration.py
```

## Writing New Integration Tests

### Test Structure

```python
"""Integration tests for [resource] endpoints

Pytest Markers:
    @pytest.mark.integration: Marks tests as integration tests
    @pytest.mark.vcr(): Enables VCR recording/playback
    @pytest.mark.live: Forces live API usage
    @pytest.mark.cached: Forces cached responses only
    @pytest.mark.slow: Marks slow tests

Usage:
    pytest tests/integration/test_[resource]_integration.py
"""

import pytest
from tests.integration.validation import (
    validate_pagination,
    validate_no_parsing_errors,
)

@pytest.mark.vcr()
@pytest.mark.integration
class Test[Resource]Integration:
    """Integration tests for [resource] endpoints"""
    
    def test_list_[resource](self, tango_client):
        """Test listing [resource] with production data
        
        Validates:
        - Paginated response structure
        - [Resource] parsing from real API responses
        - Required fields are present
        """
        response = tango_client.list_[resource](limit=5)
        
        # Validate response structure
        validate_pagination(response)
        assert len(response.results) > 0
        
        # Validate first result
        item = response.results[0]
        validate_no_parsing_errors(item)
        assert item.id is not None
```

### Best Practices

1. **Use small limits**: Keep test data small (limit=5 or limit=10) to reduce cassette size
2. **Validate parsing**: Always validate that fields are correctly parsed and typed
3. **Handle missing data**: Use conditional checks for optional fields
4. **Document expectations**: Add docstrings explaining what each test validates
5. **Use validation utilities**: Leverage functions in `validation.py` for common checks
6. **Test edge cases**: Include tests for null values, missing fields, and nested objects

## Validation Utilities

The `validation.py` module provides reusable validation functions:

- `validate_pagination(response)` - Validates paginated response structure
- `validate_contract_fields(contract, minimal=True)` - Validates contract field types
- `validate_entity_fields(entity)` - Validates entity field types
- `validate_agency_fields(agency)` - Validates agency field types
- `validate_no_parsing_errors(obj)` - Ensures object has non-None fields

## CI/CD Integration

Integration tests can be run in CI/CD pipelines:

### GitHub Actions Example

```yaml
name: Integration Tests

on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly
  workflow_dispatch:

jobs:
  integration-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          pip install -e ".[dev]"
      
      - name: Run integration tests (cached)
        run: pytest tests/integration/ -m integration
      
      - name: Run integration tests (live)
        if: github.event_name == 'schedule'
        env:
          TANGO_USE_LIVE_API: true
          TANGO_API_KEY: ${{ secrets.TANGO_API_KEY }}
        run: pytest tests/integration/ -m integration
```

## Troubleshooting

### Tests fail with "No cassette found"

**Solution:** Run tests with live API to create cassettes:
```bash
export TANGO_API_KEY=your-key
pytest tests/integration/
```

### Tests fail with "API key required"

**Solution:** Set the `TANGO_API_KEY` environment variable:
```bash
export TANGO_API_KEY=your-api-key-here
```

### Cassettes contain sensitive data

**Solution:** Cassettes automatically filter API keys. Review cassettes before committing:
```bash
cat tests/cassettes/TestContractsIntegration.test_list_contracts.yaml
```

### Tests are slow

**Solution:** Use cached mode or run specific tests:
```bash
# Use cached responses only
pytest tests/integration/ -m "integration and not slow"

# Run specific test file
pytest tests/integration/test_contracts_integration.py
```

### API schema changed

**Solution:** Refresh cassettes to get updated responses:
```bash
export TANGO_API_KEY=your-key
export TANGO_REFRESH_CASSETTES=true
pytest tests/integration/
```

## Additional Resources

- [pytest-recording documentation](https://github.com/kiwicom/pytest-recording)
- [VCR.py documentation](https://vcrpy.readthedocs.io/)
- [pytest markers documentation](https://docs.pytest.org/en/stable/how-to/mark.html)
- [Tango API documentation](https://docs.makegov.com/tango-api)
