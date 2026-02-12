"""Integration tests for organization endpoints

Pytest Markers:
    @pytest.mark.integration: Marks tests as integration tests that may hit external APIs
    @pytest.mark.vcr(): Enables VCR recording/playback for HTTP interactions

Usage:
    pytest tests/integration/test_organizations_integration.py
"""

import pytest

from tests.integration.validation import validate_no_parsing_errors, validate_pagination


def validate_organization_fields(org: object, minimal: bool = True) -> None:
    """Validate organization object has required fields (dict or attribute access)."""
    is_dict = isinstance(org, dict)
    key = org.get("key") if is_dict else getattr(org, "key", None)
    # key or fh_key is the identifier
    fh_key = org.get("fh_key") if is_dict else getattr(org, "fh_key", None)
    assert key is not None or fh_key is not None, "Organization must have 'key' or 'fh_key'"


@pytest.mark.vcr()
@pytest.mark.integration
class TestOrganizationsIntegration:
    """Integration tests for organization endpoints"""

    def test_list_organizations(self, tango_client):
        """Test listing organizations with production data."""
        response = tango_client.list_organizations(limit=10)

        validate_pagination(response)
        assert response.count >= 0
        assert isinstance(response.results, list)

        if response.results:
            org = response.results[0]
            validate_organization_fields(org)
            validate_no_parsing_errors(org)

    def test_get_organization(self, tango_client):
        """Test getting a specific organization by fh_key (if available)."""
        list_response = tango_client.list_organizations(limit=1)
        if not list_response.results:
            pytest.skip("No organizations available to test get_organization")

        org = list_response.results[0]
        is_dict = isinstance(org, dict)
        fh_key = org.get("fh_key") if is_dict else getattr(org, "fh_key", None)
        if fh_key is None:
            pytest.skip("First organization has no fh_key")

        result = tango_client.get_organization(fh_key)
        validate_organization_fields(result)
        validate_no_parsing_errors(result)
