# Development Scripts

This directory contains utility scripts used during development and maintenance of the tango-python library.

## Scripts

- **`fetch_api_schema.py`** - Fetches the OpenAPI schema from the Tango API and saves it locally
- **`generate_schemas_from_api.py`** - Generates schema definitions from the API reference (outputs to stdout)

## Usage

These scripts are primarily for maintainers and are not part of the public API. They require:
- `TANGO_API_KEY` environment variable