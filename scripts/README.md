# Development Scripts

This directory contains utility scripts used during development and maintenance of the tango-python library.

## Scripts

### Schema and API Tools

- **`fetch_api_schema.py`** - Fetches the OpenAPI schema from the Tango API and saves it locally
- **`generate_schemas_from_api.py`** - Generates schema definitions from the API reference (outputs to stdout)

### Testing and Validation

- **`test_production.py`** - Runs production API smoke tests against the live API
- **`pr_review.py`** - Runs configurable validation checks for PR review (linting, type checking, tests)

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
- `full` - All checks (linting + type checking + all tests)
- `production` - Production API smoke tests + linting + type checking (default)

**PR Detection:**
The script automatically detects PR information from:
- GitHub Actions environment variables (`GITHUB_EVENT_PATH`, `GITHUB_PR_NUMBER`)
- GitHub CLI (`gh pr view` - requires `gh auth login`)
- Current git branch

When a PR is detected, the script displays PR information and automatically:
- Detects the base branch from the PR
- Checks only changed files
- Shows PR URL in summary

## Requirements

- `TANGO_API_KEY` environment variable (required for production API tests)
- All dependencies installed: `uv sync --all-extras`