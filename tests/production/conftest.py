"""Pytest configuration and fixtures for production smoke tests"""

import os
from functools import wraps

import pytest
from dotenv import load_dotenv

from tango.exceptions import TangoAuthError, TangoRateLimitError

# Load environment variables from .env file if it exists
load_dotenv()

# Environment variables for test configuration
API_KEY = os.getenv("TANGO_API_KEY")


@pytest.fixture
def production_client():
    """
    Create TangoClient for production smoke tests

    Requires TANGO_API_KEY environment variable to be set.
    """
    from tango import TangoClient

    if not API_KEY:
        pytest.skip("TANGO_API_KEY environment variable required for production tests")

    return TangoClient(api_key=API_KEY)


def handle_auth_error(func):
    """Decorator to handle authentication errors in production tests

    Skips the test if authentication fails, which allows the test suite
    to continue even if API key is invalid or expired.

    Usage:
        @handle_auth_error
        def test_something(production_client):
            response = production_client.list_contracts()
            ...
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except TangoAuthError as e:
            pytest.skip(f"Authentication failed: {e}")

    return wrapper


def handle_rate_limit(func):
    """Decorator to handle rate limit errors in production tests

    Skips the test if rate limit is exceeded, which allows the test suite
    to continue even if API rate limits are hit.

    Usage:
        @handle_rate_limit
        def test_something(production_client):
            response = production_client.list_contracts()
            ...
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except TangoRateLimitError as e:
            pytest.skip(f"Rate limit exceeded: {e}")

    return wrapper
