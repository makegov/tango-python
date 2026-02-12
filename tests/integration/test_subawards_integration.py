"""Integration tests for subaward endpoints

Pytest Markers:
    @pytest.mark.integration: Marks tests as integration tests that may hit external APIs
    @pytest.mark.vcr(): Enables VCR recording/playback for HTTP interactions

Usage:
    pytest tests/integration/test_subawards_integration.py
"""

import pytest

from tests.integration.conftest import handle_api_exceptions
from tests.integration.validation import validate_no_parsing_errors, validate_pagination


def validate_subaward_fields(item: object) -> None:
    """Validate subaward item has an identifier (award_key or id if present)."""
    is_dict = isinstance(item, dict)
    id_val = item.get("id") if is_dict else getattr(item, "id", None)
    award_key = item.get("award_key") if is_dict else getattr(item, "award_key", None)
    assert id_val is not None or award_key is not None, (
        "Subaward item must have 'id' or 'award_key'"
    )


@pytest.mark.vcr()
@pytest.mark.integration
class TestSubawardsIntegration:
    """Integration tests for subaward endpoints"""

    @handle_api_exceptions("subawards")
    def test_list_subawards(self, tango_client):
        """Test listing subawards with production data."""
        response = tango_client.list_subawards(limit=10)

        validate_pagination(response)
        assert response.count >= 0
        assert isinstance(response.results, list)

        if response.results:
            validate_subaward_fields(response.results[0])
            validate_no_parsing_errors(response.results[0])
