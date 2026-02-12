"""Integration tests for NAICS endpoints

Pytest Markers:
    @pytest.mark.integration: Marks tests as integration tests that may hit external APIs
    @pytest.mark.vcr(): Enables VCR recording/playback for HTTP interactions

Usage:
    pytest tests/integration/test_naics_integration.py
"""

import pytest

from tests.integration.validation import validate_pagination


def validate_naics_fields(naics: dict) -> None:
    """Validate NAICS item has expected fields."""
    assert "code" in naics, "NAICS item must have 'code'"
    assert naics.get("code") is not None, "NAICS 'code' must not be None"


@pytest.mark.vcr()
@pytest.mark.integration
class TestNaicsIntegration:
    """Integration tests for NAICS code endpoints"""

    def test_list_naics(self, tango_client):
        """Test listing NAICS codes with production data."""
        response = tango_client.list_naics(limit=10)

        validate_pagination(response)
        assert response.count >= 0
        assert isinstance(response.results, list)

        if response.results:
            validate_naics_fields(response.results[0])
