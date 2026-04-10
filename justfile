# Tango Python SDK task runner
# Requires: just (https://github.com/casey/just), uv, op (1Password CLI)

# Default: list available recipes
default:
    @just --list

# Run all tests
test *args:
    uv run pytest {{ args }}

# Run unit tests only
test-unit *args:
    uv run pytest tests/ -m "not integration" {{ args }}

# Run integration tests (requires API key in 1Password)
test-integration *args:
    op run --env-file .env -- uv run pytest tests/integration/ {{ args }}

# Run integration tests with live API
test-live *args:
    TANGO_USE_LIVE_API=true op run --env-file .env -- uv run pytest tests/integration/ {{ args }}

# Refresh VCR cassettes with fresh API responses
refresh-cassettes *args:
    TANGO_REFRESH_CASSETTES=true op run --env-file .env -- uv run pytest tests/integration/ {{ args }}

# Format code
fmt:
    uv run ruff format tango/

# Lint code
lint:
    uv run ruff check tango/

# Type checking
typecheck:
    uv run mypy tango/

# Security scan with bandit
bandit:
    uv run bandit -r tango/ -c pyproject.toml

# Run all code quality checks
check: fmt lint typecheck bandit

# Full PR review (format, lint, types, tests, conformance)
pr-review *args:
    uv run python scripts/pr_review.py --mode full {{ args }}
