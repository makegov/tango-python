"""Integration tests for assistance (financial assistance) endpoints

Pytest Markers:
    @pytest.mark.integration: Marks tests as integration tests that may hit external APIs
    @pytest.mark.vcr(): Enables VCR recording/playback for HTTP interactions

Usage:
    pytest tests/integration/test_assistance_integration.py
"""

import pytest

from tango import TangoAPIError, TangoAuthError
from tests.integration.conftest import handle_api_exceptions
from tests.integration.validation import validate_pagination


@pytest.mark.vcr()
@pytest.mark.integration
class TestAssistanceIntegration:
    """Integration tests for assistance transaction endpoints"""

    @handle_api_exceptions("assistance")
    def test_list_assistance(self, tango_client):
        """Test listing assistance transactions with production data."""
        try:
            response = tango_client.list_assistance(limit=10)
        except TangoAuthError:
            pytest.skip(
                "No matching cassette for assistance; re-record with TANGO_REFRESH_CASSETTES=1"
            )
        except TangoAPIError as e:
            if e.status_code == 504:
                pytest.skip(
                    "Cassette contains 504 Gateway Timeout; re-record with "
                    "TANGO_REFRESH_CASSETTES=true when API is healthy."
                )
            raise

        validate_pagination(response)
        assert response.count >= 0
        assert isinstance(response.results, list)

        if response.results:
            item = response.results[0]
            assert isinstance(item, dict), "Assistance results are raw dicts"
