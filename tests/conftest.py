"""Pytest configuration and fixtures"""

import os
from unittest.mock import Mock

import pytest

# Load environment variables from .env file if it exists
# This ensures TANGO_API_KEY and other env vars are available when running tests
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    # dotenv is optional - tests can still run with environment variables set directly
    pass


@pytest.fixture
def clear_env_api_key():
    """Clear TANGO_API_KEY environment variable for tests that need it"""
    original_value = os.environ.get("TANGO_API_KEY")
    if "TANGO_API_KEY" in os.environ:
        del os.environ["TANGO_API_KEY"]
    yield
    if original_value is not None:
        os.environ["TANGO_API_KEY"] = original_value


@pytest.fixture
def mock_api_response():
    """Create a mock API response"""

    def _create_response(data, status_code=200):
        response = Mock()
        response.ok = status_code < 400
        response.status_code = status_code
        response.json.return_value = data
        response.content = b'{"test": "data"}'
        return response

    return _create_response


@pytest.fixture
def sample_contract_data():
    """Sample contract data for testing"""
    return {
        "key": "CONTRACT-123",
        "piid": "PIID-123",
        "award_date": "2024-01-01",
        "recipient": {"display_name": "Acme Corporation"},
        "description": "Test contract description",
        "total_contract_value": "250000.00",
        "awarding_office": {"code": "GSA-001", "name": "GSA Office", "agency": "GSA"},
    }


@pytest.fixture
def sample_entity_data():
    """Sample entity data for testing"""
    return {
        "key": "ENTITY-456",
        "legal_business_name": "Test Company, LLC",
        "uei": "ABC123DEF456GHI7",
        "cage_code": "1A2B3",
        "business_types": ["Small Business", "Woman-Owned"],
    }
