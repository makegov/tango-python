#!/usr/bin/env python3
"""Run production API smoke tests

This script runs smoke tests against the live production API to validate
that the SDK works correctly with the real API.

Usage:
    uv run python scripts/test_production.py
    TANGO_API_KEY=xxx uv run python scripts/test_production.py

Environment Variables:
    TANGO_API_KEY: API key for authentication (required)
"""

import os
import sys
from pathlib import Path

# Add project root to path so we can import tango
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables from .env file
try:
    from dotenv import load_dotenv

    load_dotenv(project_root / ".env")
except ImportError:
    pass  # dotenv is optional

try:
    import pytest
except ImportError:
    print("Error: pytest is not installed. Install with: uv sync --group dev", file=sys.stderr)
    sys.exit(1)


def main() -> int:
    """Run production smoke tests"""
    # Check for API key
    api_key = os.getenv("TANGO_API_KEY")
    if not api_key:
        print(
            "Error: TANGO_API_KEY environment variable is required",
            file=sys.stderr,
        )
        print(
            "Set it with: export TANGO_API_KEY=your-api-key",
            file=sys.stderr,
        )
        return 1

    # Run production tests
    test_path = project_root / "tests" / "production"
    if not test_path.exists():
        print(f"Error: Test directory not found: {test_path}", file=sys.stderr)
        return 1

    print("Running production API smoke tests...")
    print(f"Test directory: {test_path}")
    print()

    # Run pytest with production marker
    # Use -v for verbose output, -x to stop on first failure
    exit_code = pytest.main(
        [
            str(test_path),
            "-v",
            "-m",
            "production",
            "--tb=short",
        ]
    )

    if exit_code == 0:
        print()
        print("✓ All production smoke tests passed!")
    else:
        print()
        print("✗ Some production smoke tests failed. See output above for details.")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
