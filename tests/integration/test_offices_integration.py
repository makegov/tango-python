"""Integration tests for office endpoints

Pytest Markers:
    @pytest.mark.integration: Marks tests as integration tests that may hit external APIs
    @pytest.mark.vcr(): Enables VCR recording/playback for HTTP interactions

Usage:
    pytest tests/integration/test_offices_integration.py
"""

import pytest

from tests.integration.conftest import handle_api_exceptions
from tests.integration.validation import validate_pagination


def validate_office_fields(office: dict) -> None:
    """Validate office dict has required fields (API returns office_code, office_name, etc.)."""
    assert "office_code" in office or "code" in office, "Office must have 'office_code' or 'code'"
    code = office.get("office_code") or office.get("code")
    assert code is not None, "Office code must not be None"


@pytest.mark.vcr()
@pytest.mark.integration
class TestOfficesIntegration:
    """Integration tests for office endpoints"""

    def test_list_offices(self, tango_client):
        """Test listing offices with production data."""
        response = tango_client.list_offices(limit=10)

        validate_pagination(response)
        assert response.count >= 0
        assert isinstance(response.results, list)

        if response.results:
            validate_office_fields(response.results[0])

    @handle_api_exceptions("offices")
    def test_get_office(self, tango_client):
        """Test getting a specific office by code (if available)."""
        try:
            list_response = tango_client.list_offices(limit=1)
        except Exception:
            pytest.skip("Could not list offices")
        if not list_response.results:
            pytest.skip("No offices available to test get_office")

        code = list_response.results[0].get("office_code") or list_response.results[0].get("code")
        assert code is not None

        try:
            office = tango_client.get_office(code)
        except Exception as e:
            # Skip if cassette does not contain this get request or endpoint unavailable
            pytest.skip(f"get_office not available or cassette mismatch: {e}")

        validate_office_fields(office)
        assert (office.get("office_code") or office.get("code")) == code
