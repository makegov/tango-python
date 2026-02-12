# Development Scripts

This directory contains utility scripts used during development and maintenance of the tango-python library.

## Scripts

### Schema and API Tools

- **`fetch_api_schema.py`** - Fetches the OpenAPI schema from the Tango API and saves it locally
- **`generate_schemas_from_api.py`** - Generates schema definitions from the API reference (outputs to stdout)

### Testing and Validation

- **`test_production.py`** - Runs production API smoke tests against the live API
- **`pr_review.py`** - Runs configurable validation checks for PR review (linting, type checking, tests, conformance)
- **`check_filter_shape_conformance.py`** - Validates SDK filter and shape conformance (see [Filter and shape conformance](#filter-and-shape-conformance))

## Usage

These scripts are primarily for maintainers and are not part of the public API.

### Production API Testing

Run smoke tests against the production API:

```bash
# Requires TANGO_API_KEY environment variable
uv run python scripts/test_production.py
```

This runs fast smoke tests (~30-60 seconds) that validate core SDK functionality against the live production API.

### PR Review Validation

Run validation checks for PR review. **Automatically detects PR context** from GitHub Actions, GitHub CLI, or git branch.

```bash
# Auto-detect PR and run validation (default: production mode)
uv run python scripts/pr_review.py

# Review a specific PR number
uv run python scripts/pr_review.py --pr-number 123

# Smoke tests only
uv run python scripts/pr_review.py --mode smoke

# Quick validation (linting + type checking, no tests)
uv run python scripts/pr_review.py --mode quick

# Full validation (all checks including all tests)
uv run python scripts/pr_review.py --mode full

# Check only changed files (auto-enabled when PR is detected)
uv run python scripts/pr_review.py --mode production --changed-files-only
```

**Validation Modes:**
- `smoke` - Production API smoke tests only
- `quick` - Linting + type checking (no tests)
- `full` - All checks (linting + type checking + filter/shape conformance + all tests)
- `production` - Linting + type checking + filter/shape conformance + production API smoke tests (default)

When the conformance manifest is present (`tango-api/contracts/filter_shape_contract.json` or `TANGO_CONTRACT_MANIFEST`), both `full` and `production` run the [filter and shape conformance](#filter-and-shape-conformance) check. If the manifest is missing, that step is skipped with a warning.

**PR Detection:**
The script automatically detects PR information from:
- GitHub Actions environment variables (`GITHUB_EVENT_PATH`, `GITHUB_PR_NUMBER`)
- GitHub CLI (`gh pr view` - requires `gh auth login`)
- Current git branch

When a PR is detected, the script displays PR information and automatically:
- Detects the base branch from the PR
- Checks only changed files
- Shows PR URL in summary

### Filter and shape conformance

The SDK is validated against a canonical manifest (from the [tango](https://github.com/makegov/tango) API repo) for **filter conformance** and against its own schemas for **shape conformance**:

1. **Filter conformance** – Ensures every list/get method exposes the filter parameters defined in the manifest (e.g. `award_date`, `naics_code`, `agency`). Methods that use `**kwargs` for filters are reported as warnings because their filter names cannot be verified.
2. **Shape conformance** – Ensures every `ShapeConfig` constant (e.g. `CONTRACTS_MINIMAL`, `IDVS_MINIMAL`) parses correctly and only references fields that exist in the SDK’s explicit schemas for that model. Invalid or unknown fields in default shapes are reported as errors.

This script runs in CI on every push/PR (see [Lint workflow](.github/workflows/lint.yml)). The manifest file is produced by the tango API repo and must be available for the full check.

```bash
# Full check (filter + shape). Requires manifest from tango API repo.
uv run python scripts/check_filter_shape_conformance.py --manifest tango-api/contracts/filter_shape_contract.json

# List resources that have no matching SDK method (for implementation checklist)
uv run python scripts/check_filter_shape_conformance.py --manifest tango-api/contracts/filter_shape_contract.json --list-missing
```

**Output:** JSON with `manifest`, `errors`, and `warnings`. Exit code 1 if there are any errors (missing filters, invalid shapes, or missing SDK methods for manifest resources).

**Local runs:** To run the full check locally, you need a copy of `filter_shape_contract.json` (from the [tango](https://github.com/makegov/tango) repo’s `contracts/` directory—wherever you keep that repo). Pass it with `--manifest` or set `TANGO_CONTRACT_MANIFEST`. The script runs both filter and shape conformance; shape conformance validates all `ShapeConfig` defaults against `tango/shapes/explicit_schemas.py`.

## Requirements

- `TANGO_API_KEY` environment variable (required for production API tests)
- All dependencies installed: `uv sync --all-extras`