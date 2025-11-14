"""Pytest configuration and fixtures for integration tests"""

import hashlib
import os
from functools import wraps
from pathlib import Path

import pytest
from dotenv import load_dotenv

from tango.exceptions import TangoAPIError, TangoAuthError, TangoNotFoundError

# Load environment variables from .env file if it exists
load_dotenv()

# Environment variables for test configuration
USE_LIVE_API = os.getenv("TANGO_USE_LIVE_API", "false").lower() == "true"
REFRESH_CASSETTES = os.getenv("TANGO_REFRESH_CASSETTES", "false").lower() == "true"
API_KEY = os.getenv("TANGO_API_KEY")


def path_transformer(path: str) -> str:
    """
    Transform cassette path to shorten long filenames for Windows compatibility.
    
    Windows has a 260 character path limit. This function shortens long parameter
    values in test names by replacing them with a hash, keeping the filename
    under the limit while maintaining uniqueness.
    
    Args:
        path: Original cassette path (e.g., "tests/cassettes/TestClass.test_method[param1-param2].yaml")
        
    Returns:
        Shortened path with long parameters replaced by hash
    """
    # Maximum safe filename length (accounting for path prefix)
    MAX_FILENAME_LENGTH = 200
    
    path_obj = Path(path)
    filename = path_obj.name
    directory = path_obj.parent
    
    # If filename is already short enough, return as-is
    if len(filename) <= MAX_FILENAME_LENGTH:
        return path
    
    # Extract base name and extension
    if filename.endswith('.yaml'):
        base_name = filename[:-5]  # Remove .yaml
        ext = '.yaml'
    elif filename.endswith('.yml'):
        base_name = filename[:-4]  # Remove .yml
        ext = '.yml'
    else:
        # Unknown extension, return as-is
        return path
    
    # Check if this is a parameterized test (has brackets)
    if '[' not in base_name or ']' not in base_name:
        # Not parameterized, just truncate if needed
        if len(filename) > MAX_FILENAME_LENGTH:
            truncated = base_name[:MAX_FILENAME_LENGTH - len(ext) - 8] + ext
            return str(directory / truncated)
        return path
    
    # Split into test name and parameters
    test_name, params = base_name.split('[', 1)
    if not params.endswith(']'):
        return path  # Malformed, return as-is
    
    params = params[:-1]  # Remove trailing ]
    
    # If parameters are too long, hash them
    if len(params) > 100:  # Threshold for hashing
        # Create a hash of the parameters (first 8 chars for readability)
        param_hash = hashlib.md5(params.encode()).hexdigest()[:8]
        new_filename = f"{test_name}[{param_hash}]{ext}"
    else:
        # Parameters are short enough, but total might still be too long
        new_filename = filename
        if len(new_filename) > MAX_FILENAME_LENGTH:
            # Truncate the parameters part
            max_params_len = MAX_FILENAME_LENGTH - len(test_name) - len(ext) - 2  # -2 for []
            if max_params_len > 0:
                truncated_params = params[:max_params_len]
                new_filename = f"{test_name}[{truncated_params}]{ext}"
            else:
                # Even test name is too long, use hash
                param_hash = hashlib.md5(params.encode()).hexdigest()[:8]
                new_filename = f"{test_name[:MAX_FILENAME_LENGTH - 15]}[{param_hash}]{ext}"
    
    return str(directory / new_filename)


@pytest.fixture(scope="module")
def vcr_config():
    """
    VCR configuration for recording/replaying HTTP interactions

    This fixture configures pytest-recording (VCR.py) to:
    - Store cassettes in tests/cassettes/
    - Record new interactions if cassette doesn't exist
    - Match requests by method, scheme, host, port, path, and query
    - Filter sensitive headers (API keys) from recordings
    - Decode compressed responses for readability
    - Shorten long filenames for Windows compatibility
    """
    record_mode = "once"  # Default: record if cassette doesn't exist

    if REFRESH_CASSETTES:
        record_mode = "all"  # Re-record all cassettes
    elif USE_LIVE_API:
        record_mode = "none"  # Always use live API, don't record

    return {
        "cassette_library_dir": "tests/cassettes",
        "record_mode": record_mode,
        "match_on": ["method", "scheme", "host", "port", "path", "query"],
        "filter_headers": ["X-API-KEY", "x-api-key"],  # Don't record API keys
        "decode_compressed_response": True,
        "filter_query_parameters": [],  # Can add query params to filter if needed
        "path_transformer": path_transformer,  # Shorten long filenames for Windows
    }


@pytest.fixture
def tango_client():
    """
    Create TangoClient for integration tests

    Uses real API key when USE_LIVE_API=true, otherwise uses a test key
    for cassette playback (the actual key doesn't matter for playback).
    """
    from tango import TangoClient

    # Use real API key for live tests, placeholder for cassette playback
    api_key = API_KEY if USE_LIVE_API or REFRESH_CASSETTES else "test-key-for-cassettes"

    if (USE_LIVE_API or REFRESH_CASSETTES) and not API_KEY:
        pytest.skip("TANGO_API_KEY environment variable required for live API tests")

    return TangoClient(api_key=api_key)


@pytest.fixture(scope="session")
def cassette_dir():
    """Ensure cassette directory exists"""
    cassette_path = Path("tests/cassettes")
    cassette_path.mkdir(parents=True, exist_ok=True)
    return cassette_path


def handle_api_exceptions(endpoint_name: str = "endpoint"):
    """Decorator to handle common API exceptions in integration tests

    Only skips tests when using live API. When using cassettes, exceptions
    are allowed to propagate so tests can validate error handling or fail
    if cassettes need to be re-recorded.

    Args:
        endpoint_name: Name of the endpoint for error messages

    Usage:
        @handle_api_exceptions("opportunities")
        def test_something(tango_client):
            response = tango_client.list_opportunities()
            ...
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except (TangoNotFoundError, TangoAuthError, TangoAPIError) as e:
                # Only skip for live API calls - let cassettes fail normally
                # so we can detect if cassettes need to be re-recorded
                if USE_LIVE_API or REFRESH_CASSETTES:
                    if isinstance(e, TangoNotFoundError):
                        pytest.skip(f"{endpoint_name.capitalize()} endpoint not available (404)")
                    elif isinstance(e, TangoAuthError):
                        pytest.skip(
                            "Authentication required - run with valid API key to record cassettes"
                        )
                    else:
                        pytest.skip(f"{endpoint_name.capitalize()} endpoint not available: {e}")
                else:
                    # When using cassettes, re-raise the exception
                    # This allows tests to handle errors or fail if cassettes are invalid
                    raise

        return wrapper

    return decorator


@pytest.fixture(
    params=[
        ("minimal", None),  # None means use default shape
        ("custom", "key,title"),
    ]
)
def shape_config(request):
    """Parameterized fixture for testing different shapes

    Returns:
        tuple: (shape_name, shape_value) where shape_value can be None (default),
               a ShapeConfig constant, or a custom shape string
    """
    return request.param
