"""Integration tests for OTA and OTIDV endpoints

Pytest Markers:
    @pytest.mark.integration: Marks tests as integration tests that may hit external APIs
    @pytest.mark.vcr(): Enables VCR recording/playback for HTTP interactions

Usage:
    pytest tests/integration/test_otas_otidvs_integration.py
"""

import pytest

from tango import TangoAuthError
from tests.integration.conftest import handle_api_exceptions
from tests.integration.validation import validate_no_parsing_errors, validate_pagination


def validate_ota_fields(item: object) -> None:
    """Validate OTA/OTIDV item has key (dict or attribute access)."""
    is_dict = isinstance(item, dict)
    key = item.get("key") if is_dict else getattr(item, "key", None)
    assert key is not None, "OTA/OTIDV item must have 'key'"


@pytest.mark.vcr()
@pytest.mark.integration
class TestOTAsIntegration:
    """Integration tests for OTA (Other Transaction Agreement) endpoints"""

    @handle_api_exceptions("otas")
    def test_list_otas(self, tango_client):
        """Test listing OTAs with production data."""
        try:
            response = tango_client.list_otas(limit=5)
        except TangoAuthError:
            pytest.skip("No matching cassette for OTAs; re-record with TANGO_REFRESH_CASSETTES=1")

        validate_pagination(response)
        assert response.count >= 0
        assert isinstance(response.results, list)

        if response.results:
            validate_ota_fields(response.results[0])
            validate_no_parsing_errors(response.results[0])

    @handle_api_exceptions("otas")
    def test_get_ota(self, tango_client):
        """Test getting a single OTA by key (if available)."""
        try:
            list_response = tango_client.list_otas(limit=1)
        except TangoAuthError:
            pytest.skip("No matching cassette for OTAs; re-record with TANGO_REFRESH_CASSETTES=1")
        if not list_response.results:
            pytest.skip("No OTAs available to test get_ota")

        item = list_response.results[0]
        is_dict = isinstance(item, dict)
        key = item.get("key") if is_dict else getattr(item, "key", None)
        if key is None:
            pytest.skip("First OTA has no key")

        result = tango_client.get_ota(key)
        validate_ota_fields(result)
        validate_no_parsing_errors(result)


@pytest.mark.vcr()
@pytest.mark.integration
class TestOTIDVsIntegration:
    """Integration tests for OTIDV (Other Transaction IDV) endpoints"""

    @handle_api_exceptions("otidvs")
    def test_list_otidvs(self, tango_client):
        """Test listing OTIDVs with production data."""
        response = tango_client.list_otidvs(limit=5)

        validate_pagination(response)
        assert response.count >= 0
        assert isinstance(response.results, list)

        if response.results:
            validate_ota_fields(response.results[0])
            validate_no_parsing_errors(response.results[0])

    @handle_api_exceptions("otidvs")
    def test_get_otidv(self, tango_client):
        """Test getting a single OTIDV by key (if available)."""
        list_response = tango_client.list_otidvs(limit=1)
        if not list_response.results:
            pytest.skip("No OTIDVs available to test get_otidv")

        item = list_response.results[0]
        is_dict = isinstance(item, dict)
        key = item.get("key") if is_dict else getattr(item, "key", None)
        if key is None:
            pytest.skip("First OTIDV has no key")

        result = tango_client.get_otidv(key)
        validate_ota_fields(result)
        validate_no_parsing_errors(result)
