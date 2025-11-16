"""Tests for TangoClient"""

from datetime import date, datetime
from decimal import Decimal
from unittest.mock import Mock, patch

import pytest

from tango import (
    SearchFilters,
    ShapeConfig,
    TangoAPIError,
    TangoAuthError,
    TangoClient,
    TangoRateLimitError,
    TangoValidationError,
)


class TestTangoClient:
    """Test TangoClient initialization and basic functionality"""

    def test_client_initialization(self, clear_env_api_key):
        """Test client can be initialized with and without API key"""
        client = TangoClient()
        assert client.api_key is None
        assert client.base_url == "https://tango.makegov.com"

        client_with_key = TangoClient(api_key="test-key")
        assert client_with_key.api_key == "test-key"
        assert client_with_key.client.headers.get("X-API-KEY") == "test-key"

    def test_custom_base_url(self):
        """Test client can be initialized with custom base URL"""
        client = TangoClient(base_url="https://custom.example.com")
        assert client.base_url == "https://custom.example.com"

    @patch("tango.client.httpx.Client.request")
    def test_authentication_header(self, mock_request):
        """Test that X-API-KEY header is used for authentication"""
        mock_response = Mock()
        mock_response.is_success = True
        mock_response.json.return_value = {"count": 0, "results": []}
        mock_response.content = b'{"count": 0, "results": []}'
        mock_request.return_value = mock_response

        client = TangoClient(api_key="test-key-123")
        client.list_agencies()

        # Verify the client has the correct header
        assert client.client.headers.get("X-API-KEY") == "test-key-123"

    @patch("tango.client.httpx.Client.request")
    def test_list_agencies(self, mock_request):
        """Test list_agencies method"""
        mock_response = Mock()
        mock_response.is_success = True
        mock_response.json.return_value = {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [{"code": "GSA", "name": "General Services Administration"}],
        }
        mock_response.content = b'{"count": 1}'
        mock_request.return_value = mock_response

        client = TangoClient(api_key="test-key")
        agencies = client.list_agencies()

        assert agencies.count == 1
        assert len(agencies.results) == 1
        assert agencies.results[0].code == "GSA"

    @patch("tango.client.httpx.Client.request")
    def test_list_contracts_with_default_shape(self, mock_request):
        """Test list_contracts uses default minimal shape"""
        mock_response = Mock()
        mock_response.is_success = True
        mock_response.json.return_value = {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "key": "CONTRACT-123",
                    "piid": "PIID-123",
                    "award_date": "2024-01-01",
                    "recipient": {"display_name": "Acme Corp", "uei": "ABC123"},
                    "description": "Test contract",
                    "total_contract_value": "100000.00",
                }
            ],
        }
        mock_response.content = b'{"count": 1}'
        mock_request.return_value = mock_response

        client = TangoClient(api_key="test-key")
        contracts = client.list_contracts(limit=10)

        # Verify shape parameter was passed
        call_args = mock_request.call_args
        assert call_args[1]["params"]["shape"] == ShapeConfig.CONTRACTS_MINIMAL

        assert contracts.count == 1
        assert len(contracts.results) == 1
        # Use dictionary access for shaped responses
        assert contracts.results[0]["key"] == "CONTRACT-123"
        assert contracts.results[0]["recipient"]["display_name"] == "Acme Corp"

    @patch("tango.client.httpx.Client.request")
    def test_list_contracts_custom_shape(self, mock_request):
        """Test list_contracts with custom shape"""
        mock_response = Mock()
        mock_response.is_success = True
        mock_response.json.return_value = {
            "count": 0,
            "next": None,
            "previous": None,
            "results": [],
        }
        mock_response.content = b'{"count": 0}'
        mock_request.return_value = mock_response

        client = TangoClient(api_key="test-key")
        custom_shape = "key,piid,recipient(display_name)"
        client.list_contracts(shape=custom_shape)

        call_args = mock_request.call_args
        assert call_args[1]["params"]["shape"] == custom_shape

    @patch("tango.client.httpx.Client.request")
    def test_list_entities(self, mock_request):
        """Test list_entities method"""
        mock_response = Mock()
        mock_response.is_success = True
        mock_response.json.return_value = {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "key": "ENTITY-123",
                    "legal_business_name": "Test Company",
                    "uei": "ABC123DEF456",
                }
            ],
        }
        mock_response.content = b'{"count": 1}'
        mock_request.return_value = mock_response

        client = TangoClient(api_key="test-key")
        entities = client.list_entities(search="Test")

        assert entities.count == 1
        assert entities.results[0]["legal_business_name"] == "Test Company"
        assert entities.results[0]["uei"] == "ABC123DEF456"

    @patch("tango.client.httpx.Client.request")
    def test_error_handling_401(self, mock_request):
        """Test 401 authentication error handling"""
        mock_response = Mock()
        mock_response.is_success = False
        mock_response.status_code = 401
        mock_request.return_value = mock_response

        client = TangoClient(api_key="invalid-key")

        with pytest.raises(TangoAuthError) as exc_info:
            client.list_agencies()

        assert exc_info.value.status_code == 401

    @patch("tango.client.httpx.Client.request")
    def test_error_handling_404(self, mock_request):
        """Test 404 not found error handling"""
        from tango import TangoNotFoundError

        mock_response = Mock()
        mock_response.is_success = False
        mock_response.status_code = 404
        mock_request.return_value = mock_response

        client = TangoClient(api_key="test-key")

        with pytest.raises(TangoNotFoundError) as exc_info:
            client.get_agency("INVALID")

        assert exc_info.value.status_code == 404


class TestShapeConfig:
    """Test ShapeConfig class"""

    def test_shape_config_values(self):
        """Test that ShapeConfig has expected shape strings"""
        assert isinstance(ShapeConfig.CONTRACTS_MINIMAL, str)
        assert isinstance(ShapeConfig.ENTITIES_MINIMAL, str)
        assert "key" in ShapeConfig.CONTRACTS_MINIMAL
        assert "recipient" in ShapeConfig.CONTRACTS_MINIMAL


class TestDynamicModelsIntegration:
    """Test dynamic model generation integration with TangoClient"""

    def test_client_initialization_always_has_dynamic_models(self):
        """Test client always initializes with dynamic models"""
        client = TangoClient()
        assert client._shape_parser is not None
        assert client._type_generator is not None
        assert client._model_factory is not None

    @patch("tango.client.httpx.Client.request")
    def test_list_contracts_returns_dynamic_models(self, mock_request):
        """Test list_contracts always returns dynamic models"""
        mock_response = Mock()
        mock_response.is_success = True
        mock_response.json.return_value = {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "key": "CONTRACT-123",
                    "piid": "PIID-123",
                    "award_date": "2024-01-01",
                    "recipient": {"display_name": "Acme Corp"},
                    "description": "Test contract",
                    "total_contract_value": "100000.00",
                }
            ],
        }
        mock_response.content = b'{"count": 1}'
        mock_request.return_value = mock_response

        client = TangoClient(api_key="test-key")
        contracts = client.list_contracts(limit=10)

        assert contracts.count == 1
        assert len(contracts.results) == 1
        # Result should be a dictionary (dynamic model)
        result = contracts.results[0]
        assert isinstance(result, dict)
        assert result["key"] == "CONTRACT-123"
        assert result["piid"] == "PIID-123"

    @patch("tango.client.httpx.Client.request")
    def test_list_contracts_with_predefined_shape(self, mock_request):
        """Test list_contracts with predefined shape (CONTRACTS_MINIMAL)"""
        mock_response = Mock()
        mock_response.is_success = True
        mock_response.json.return_value = {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "key": "CONTRACT-123",
                    "piid": "PIID-123",
                    "award_date": "2024-01-01",
                    "recipient": {"display_name": "Acme Corp"},
                    "description": "Test contract",
                    "total_contract_value": "100000.00",
                }
            ],
        }
        mock_response.content = b'{"count": 1}'
        mock_request.return_value = mock_response

        client = TangoClient(api_key="test-key")
        contracts = client.list_contracts(shape=ShapeConfig.CONTRACTS_MINIMAL)

        assert contracts.count == 1
        result = contracts.results[0]
        assert isinstance(result, dict)
        assert "key" in result
        assert "piid" in result

    @patch("tango.client.httpx.Client.request")
    def test_list_contracts_with_custom_shape(self, mock_request):
        """Test list_contracts with custom shape string"""
        mock_response = Mock()
        mock_response.is_success = True
        mock_response.json.return_value = {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "key": "CONTRACT-123",
                    "piid": "PIID-123",
                    "recipient": {"display_name": "Acme Corp", "uei": "ABC123"},
                }
            ],
        }
        mock_response.content = b'{"count": 1}'
        mock_request.return_value = mock_response

        client = TangoClient(api_key="test-key")
        custom_shape = "key,piid,recipient(display_name,uei)"
        contracts = client.list_contracts(shape=custom_shape)

        assert contracts.count == 1
        result = contracts.results[0]
        assert isinstance(result, dict)
        assert result["key"] == "CONTRACT-123"
        assert result["piid"] == "PIID-123"
        assert result["recipient"]["display_name"] == "Acme Corp"
        assert result["recipient"]["uei"] == "ABC123"

    @patch("tango.client.httpx.Client.request")
    def test_list_contracts_with_flat_response(self, mock_request):
        """Test list_contracts with flat response (flat=True)"""
        mock_response = Mock()
        mock_response.is_success = True
        mock_response.json.return_value = {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "key": "CONTRACT-123",
                    "piid": "PIID-123",
                    "recipient.display_name": "Acme Corp",
                    "recipient.uei": "ABC123",
                }
            ],
        }
        mock_response.content = b'{"count": 1}'
        mock_request.return_value = mock_response

        client = TangoClient(api_key="test-key")
        custom_shape = "key,piid,recipient(display_name,uei)"
        contracts = client.list_contracts(shape=custom_shape, flat=True)

        assert contracts.count == 1
        result = contracts.results[0]
        assert isinstance(result, dict)
        # Should be unflattened by the parser
        assert result["key"] == "CONTRACT-123"
        assert result["recipient"]["display_name"] == "Acme Corp"

    @patch("tango.client.httpx.Client.request")
    def test_list_entities_returns_dynamic_models(self, mock_request):
        """Test list_entities returns dynamic models"""
        mock_response = Mock()
        mock_response.is_success = True
        mock_response.json.return_value = {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "uei": "ABC123DEF456",
                    "legal_business_name": "Test Company",
                }
            ],
        }
        mock_response.content = b'{"count": 1}'
        mock_request.return_value = mock_response

        client = TangoClient(api_key="test-key")
        entities = client.list_entities()

        assert entities.count == 1
        result = entities.results[0]
        assert isinstance(result, dict)
        assert result["uei"] == "ABC123DEF456"
        assert result["legal_business_name"] == "Test Company"

    @patch("tango.client.httpx.Client.request")
    def test_list_forecasts_returns_dynamic_models(self, mock_request):
        """Test list_forecasts returns dynamic models"""
        mock_response = Mock()
        mock_response.is_success = True
        mock_response.json.return_value = {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "id": 123,
                    "title": "Test Forecast",
                    "anticipated_award_date": "2024-06-01",
                    "fiscal_year": 2024,
                    "naics_code": "541330",
                    "status": "active",
                }
            ],
        }
        mock_response.content = b'{"count": 1}'
        mock_request.return_value = mock_response

        client = TangoClient(api_key="test-key")
        forecasts = client.list_forecasts()

        assert forecasts.count == 1
        result = forecasts.results[0]
        assert isinstance(result, dict)
        assert result["id"] == 123

    @patch("tango.client.httpx.Client.request")
    def test_list_opportunities_returns_dynamic_models(self, mock_request):
        """Test list_opportunities returns dynamic models"""
        mock_response = Mock()
        mock_response.is_success = True
        mock_response.json.return_value = {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "opportunity_id": "OPP-123",
                    "title": "Test Opportunity",
                    "solicitation_number": "SOL-123",
                    "response_deadline": "2024-06-01T12:00:00Z",
                    "active": True,
                }
            ],
        }
        mock_response.content = b'{"count": 1}'
        mock_request.return_value = mock_response

        client = TangoClient(api_key="test-key")
        opportunities = client.list_opportunities()

        assert opportunities.count == 1
        result = opportunities.results[0]
        assert isinstance(result, dict)
        assert result["opportunity_id"] == "OPP-123"

    @patch("tango.client.httpx.Client.request")
    def test_list_notices_returns_dynamic_models(self, mock_request):
        """Test list_notices returns dynamic models"""
        mock_response = Mock()
        mock_response.is_success = True
        mock_response.json.return_value = {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "notice_id": "NOTICE-123",
                    "title": "Test Notice",
                    "notice_type": "Solicitation",
                }
            ],
        }
        mock_response.content = b'{"count": 1}'
        mock_request.return_value = mock_response

        client = TangoClient(api_key="test-key")
        notices = client.list_notices()

        assert notices.count == 1
        result = notices.results[0]
        assert isinstance(result, dict)
        assert result["notice_id"] == "NOTICE-123"

    @patch("tango.client.httpx.Client.request")
    def test_list_grants_returns_dynamic_models(self, mock_request):
        """Test list_grants returns dynamic models"""
        mock_response = Mock()
        mock_response.is_success = True
        mock_response.json.return_value = {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "grant_id": 12345,
                    "opportunity_number": "OPP-123",
                    "title": "Test Grant",
                    "status": {"code": "OPEN", "description": "Open"},
                }
            ],
        }
        mock_response.content = b'{"count": 1}'
        mock_request.return_value = mock_response

        client = TangoClient(api_key="test-key")
        grants = client.list_grants()

        assert grants.count == 1
        result = grants.results[0]
        assert isinstance(result, dict)
        assert result["grant_id"] == 12345

    @patch("tango.client.httpx.Client.request")
    def test_default_shape_applied_when_none_provided(self, mock_request):
        """Test default shape is applied when no shape is provided"""
        mock_response = Mock()
        mock_response.is_success = True
        mock_response.json.return_value = {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "key": "CONTRACT-123",
                    "piid": "PIID-123",
                    "award_date": "2024-01-01",
                    "recipient": {"display_name": "Acme Corp"},
                    "description": "Test contract",
                    "total_contract_value": "100000.00",
                }
            ],
        }
        mock_response.content = b'{"count": 1}'
        mock_request.return_value = mock_response

        client = TangoClient(api_key="test-key")
        contracts = client.list_contracts()

        assert contracts.count == 1
        result = contracts.results[0]
        assert isinstance(result, dict)

    @patch("tango.client.httpx.Client.request")
    def test_dynamic_model_raises_error_on_invalid_shape(self, mock_request):
        """Test that dynamic model generation raises exception on error"""
        from tango.exceptions import ShapeParseError

        mock_response = Mock()
        mock_response.is_success = True
        mock_response.json.return_value = {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "key": "CONTRACT-123",
                    "piid": "PIID-123",
                }
            ],
        }
        mock_response.content = b'{"count": 1}'
        mock_request.return_value = mock_response

        client = TangoClient(api_key="test-key")

        # Use an invalid shape that will cause parsing to fail
        # The client should raise an exception instead of falling back
        with pytest.raises(ShapeParseError):
            client.list_contracts(shape="invalid(shape")


class TestDynamicModelsConvenienceMethods:
    """Test dynamic models with convenience methods"""

    @patch("tango.client.httpx.Client.request")
    def test_search_contracts_returns_dynamic_models(self, mock_request):
        """Test list_contracts returns dynamic models"""
        from tango.models import SearchFilters

        mock_response = Mock()
        mock_response.is_success = True
        mock_response.json.return_value = {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "key": "CONTRACT-123",
                    "piid": "PIID-123",
                }
            ],
        }
        mock_response.content = b'{"count": 1}'
        mock_request.return_value = mock_response

        client = TangoClient(api_key="test-key")
        filters = SearchFilters(keyword="test")
        contracts = client.list_contracts(filters=filters)

        assert contracts.count == 1
        result = contracts.results[0]
        assert isinstance(result, dict)


# ============================================================================
# Error Handling Tests
# ============================================================================


class TestErrorHandling:
    """Test all error handling paths"""

    @patch("tango.client.httpx.Client.request")
    def test_400_validation_error(self, mock_request):
        """Test 400 Bad Request raises TangoValidationError"""
        mock_response = Mock()
        mock_response.is_success = False
        mock_response.status_code = 400
        mock_response.content = b'{"error": "invalid params"}'
        mock_response.json.return_value = {"error": "invalid params"}
        mock_request.return_value = mock_response

        client = TangoClient(api_key="test-key")

        with pytest.raises(TangoValidationError) as exc_info:
            client.list_agencies()

        assert exc_info.value.status_code == 400
        assert exc_info.value.response_data == {"error": "invalid params"}

    @patch("tango.client.httpx.Client.request")
    def test_400_validation_error_no_content(self, mock_request):
        """Test 400 with no content"""
        mock_response = Mock()
        mock_response.is_success = False
        mock_response.status_code = 400
        mock_response.content = None
        mock_request.return_value = mock_response

        client = TangoClient(api_key="test-key")

        with pytest.raises(TangoValidationError) as exc_info:
            client.list_agencies()

        assert exc_info.value.response_data == {}

    @patch("tango.client.httpx.Client.request")
    def test_429_rate_limit_error(self, mock_request):
        """Test 429 Rate Limit raises TangoRateLimitError"""
        mock_response = Mock()
        mock_response.is_success = False
        mock_response.status_code = 429
        mock_request.return_value = mock_response

        client = TangoClient(api_key="test-key")

        with pytest.raises(TangoRateLimitError) as exc_info:
            client.list_agencies()

        assert exc_info.value.status_code == 429

    @patch("tango.client.httpx.Client.request")
    def test_500_server_error(self, mock_request):
        """Test 500 Server Error raises TangoAPIError"""
        mock_response = Mock()
        mock_response.is_success = False
        mock_response.status_code = 500
        mock_request.return_value = mock_response

        client = TangoClient(api_key="test-key")

        with pytest.raises(TangoAPIError) as exc_info:
            client.list_agencies()

        assert exc_info.value.status_code == 500
        assert "500" in str(exc_info.value)

    @patch("tango.client.httpx.Client.request")
    def test_network_error(self, mock_request):
        """Test network errors raise TangoAPIError"""
        import httpx

        mock_request.side_effect = httpx.ConnectError("Connection failed")

        client = TangoClient(api_key="test-key")

        with pytest.raises(TangoAPIError) as exc_info:
            client.list_agencies()

        assert "Connection failed" in str(exc_info.value)

    @patch("tango.client.httpx.Client.request")
    def test_empty_response_content(self, mock_request):
        """Test handling of empty response content"""
        mock_response = Mock()
        mock_response.is_success = True
        mock_response.content = None
        mock_request.return_value = mock_response

        client = TangoClient(api_key="test-key")
        result = client._request("GET", "/test/")

        assert result == {}


# ============================================================================
# Additional Endpoint Tests
# ============================================================================


class TestAdditionalEndpoints:
    """Test additional endpoint methods"""

    @patch("tango.client.httpx.Client.request")
    def test_get_agency(self, mock_request):
        """Test get_agency endpoint"""
        mock_response = Mock()
        mock_response.is_success = True
        mock_response.content = b'{"code": "GSA"}'
        mock_response.json.return_value = {
            "code": "GSA",
            "name": "General Services Administration",
        }
        mock_request.return_value = mock_response

        client = TangoClient(api_key="test-key")
        agency = client.get_agency("GSA")

        assert agency.code == "GSA"
        assert agency.name == "General Services Administration"

    @patch("tango.client.httpx.Client.request")
    def test_list_business_types(self, mock_request):
        """Test list_business_types endpoint"""
        mock_response = Mock()
        mock_response.is_success = True
        mock_response.content = b'{"count": 1}'
        mock_response.json.return_value = {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [{"code": "SB", "name": "Small Business"}],
        }
        mock_request.return_value = mock_response

        client = TangoClient(api_key="test-key")
        types = client.list_business_types()

        assert types.count == 1
        assert types.results[0].code == "SB"

    @patch("tango.client.httpx.Client.request")
    def test_search_contracts_with_filters(self, mock_request):
        """Test list_contracts with SearchFilters"""
        mock_response = Mock()
        mock_response.is_success = True
        mock_response.content = b'{"count": 0}'
        mock_response.json.return_value = {
            "count": 0,
            "next": None,
            "previous": None,
            "results": [],
        }
        mock_request.return_value = mock_response

        client = TangoClient(api_key="test-key")
        filters = SearchFilters(
            keyword="test",
            awarding_agency="GSA",
            fiscal_year=2024,
        )

        results = client.list_contracts(filters=filters)

        # Verify filter parameters were passed (with correct mappings)
        call_args = mock_request.call_args
        params = call_args[1]["params"]

        # keyword should be mapped to 'search'
        assert params["search"] == "test", "keyword should be mapped to 'search'"
        assert "keyword" not in params, "keyword should not be in params"

        # awarding_agency should pass through as-is
        assert params["awarding_agency"] == "GSA"

        # fiscal_year should pass through as-is
        assert params["fiscal_year"] == 2024

        # Verify results were returned correctly
        assert results.count == 0
        assert len(results.results) == 0

    @patch("tango.client.httpx.Client.request")
    def test_list_contracts_naics_code_filter_separation(self, mock_request):
        """Test that naics_code filter is in query params, not in shape parameter"""
        mock_response = Mock()
        mock_response.is_success = True
        mock_response.content = b'{"count": 0}'
        mock_response.json.return_value = {
            "count": 0,
            "next": None,
            "previous": None,
            "results": [],
        }
        mock_request.return_value = mock_response

        client = TangoClient(api_key="test-key")
        
        # Test with naics_code as keyword argument
        client.list_contracts(naics_code="541511", limit=10)
        
        # Verify the HTTP request was made
        assert mock_request.called
        
        # Get the call arguments
        call_args = mock_request.call_args
        params = call_args[1]["params"]
        
        # Verify naics_code is mapped to 'naics' in query params (API expects 'naics' not 'naics_code')
        assert "naics" in params, "naics should be in query parameters (mapped from naics_code)"
        assert params["naics"] == "541511", "naics value should be '541511'"
        assert "naics_code" not in params, "naics_code should be mapped to 'naics', not sent as naics_code"
        
        # Verify naics_code is NOT in the shape parameter
        shape = params.get("shape", "")
        assert "naics_code" not in shape, f"naics_code should NOT be in shape parameter, but shape is: {shape}"
        
        # Verify shape parameter exists and is separate
        assert "shape" in params, "shape parameter should exist"
        assert isinstance(params["shape"], str), "shape should be a string"

    @pytest.mark.parametrize(
        "client_param,api_param,test_value",
        [
            ("keyword", "search", "software"),
            ("psc_code", "psc", "R425"),
            ("recipient_name", "recipient", "Acme Corp"),
            ("recipient_uei", "uei", "ABC123XYZ456"),
            ("set_aside_type", "set_aside", "8A"),
        ],
    )
    @patch("tango.client.httpx.Client.request")
    def test_filter_parameter_mappings(self, mock_request, client_param, api_param, test_value):
        """Test that filter parameters are correctly mapped to API parameters"""
        mock_response = Mock()
        mock_response.is_success = True
        mock_response.content = b'{"count": 0}'
        mock_response.json.return_value = {
            "count": 0,
            "next": None,
            "previous": None,
            "results": [],
        }
        mock_request.return_value = mock_response

        client = TangoClient(api_key="test-key")
        client.list_contracts(**{client_param: test_value}, limit=10)

        call_args = mock_request.call_args
        params = call_args[1]["params"]

        # Verify parameter is mapped to API param
        assert api_param in params, f"{client_param} should be mapped to '{api_param}' API param"
        assert params[api_param] == test_value
        # Verify original parameter is not in params
        assert client_param not in params, f"{client_param} should be mapped, not sent as-is"

    @patch("tango.client.httpx.Client.request")
    def test_sort_and_order_mapped_to_ordering(self, mock_request):
        """Test that 'sort' and 'order' parameters are combined into 'ordering' API param"""
        mock_response = Mock()
        mock_response.is_success = True
        mock_response.content = b'{"count": 0}'
        mock_response.json.return_value = {
            "count": 0,
            "next": None,
            "previous": None,
            "results": [],
        }
        mock_request.return_value = mock_response

        client = TangoClient(api_key="test-key")

        # Test ascending order (default)
        client.list_contracts(sort="award_date", order="asc", limit=10)
        call_args = mock_request.call_args
        params = call_args[1]["params"]

        assert "ordering" in params, "sort+order should be combined into 'ordering'"
        assert params["ordering"] == "award_date", "ascending should have no prefix"
        assert "sort" not in params
        assert "order" not in params

        # Test descending order
        client.list_contracts(sort="award_date", order="desc", limit=10)
        call_args = mock_request.call_args
        params = call_args[1]["params"]

        assert params["ordering"] == "-award_date", "descending should have '-' prefix"

    @patch("tango.client.httpx.Client.request")
    def test_new_api_parameters_are_supported(self, mock_request):
        """Test that new API parameters are passed through correctly"""
        mock_response = Mock()
        mock_response.is_success = True
        mock_response.content = b'{"count": 0}'
        mock_response.json.return_value = {
            "count": 0,
            "next": None,
            "previous": None,
            "results": [],
        }
        mock_request.return_value = mock_response

        client = TangoClient(api_key="test-key")
        client.list_contracts(
            pop_start_date_gte="2024-01-01",
            pop_end_date_lte="2024-12-31",
            expiring_gte="2025-01-01",
            fiscal_year_gte=2020,
            fiscal_year_lte=2024,
            piid="CONTRACT-123",
            solicitation_identifier="SOL-456",
            limit=10,
        )

        call_args = mock_request.call_args
        params = call_args[1]["params"]

        # All new parameters should be present
        assert params["pop_start_date_gte"] == "2024-01-01"
        assert params["pop_end_date_lte"] == "2024-12-31"
        assert params["expiring_gte"] == "2025-01-01"
        assert params["fiscal_year_gte"] == 2020
        assert params["fiscal_year_lte"] == 2024
        assert params["piid"] == "CONTRACT-123"
        assert params["solicitation_identifier"] == "SOL-456"

    @patch("tango.client.httpx.Client.request")
    def test_get_entity(self, mock_request):
        """Test get_entity endpoint"""
        mock_response = Mock()
        mock_response.is_success = True
        mock_response.content = b'{"uei": "ABC123"}'
        mock_response.json.return_value = {
            "key": "ABC123",
            "legal_business_name": "Test Entity Inc",
            "uei": "ABC123",
            "cage_code": "ABC12",
            "business_types": ["Small Business"],
        }
        mock_request.return_value = mock_response

        client = TangoClient(api_key="test-key")
        # Use a simpler shape that doesn't require wildcards
        entity = client.get_entity(
            "ABC123", shape="uei,legal_business_name,cage_code,business_types"
        )

        # Entity should have uei field
        assert entity.uei == "ABC123"
        assert entity.uei == "ABC123"

    @patch("tango.client.httpx.Client.request")
    def test_list_forecasts(self, mock_request):
        """Test list_forecasts endpoint"""
        mock_response = Mock()
        mock_response.is_success = True
        mock_response.content = b'{"count": 1}'
        mock_response.json.return_value = {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [{"key": "F123", "title": "Test Forecast"}],
        }
        mock_request.return_value = mock_response

        client = TangoClient(api_key="test-key")
        forecasts = client.list_forecasts()

        assert forecasts.count == 1
        assert forecasts.results[0].title == "Test Forecast"

    @patch("tango.client.httpx.Client.request")
    def test_list_opportunities(self, mock_request):
        """Test list_opportunities endpoint"""
        mock_response = Mock()
        mock_response.is_success = True
        mock_response.content = b'{"count": 1}'
        mock_response.json.return_value = {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "key": "O123",
                    "title": "Test Opp",
                    "solicitation_number": "SOL-123",
                }
            ],
        }
        mock_request.return_value = mock_response

        client = TangoClient(api_key="test-key")
        opps = client.list_opportunities()

        assert opps.count == 1
        assert opps.results[0].solicitation_number == "SOL-123"

    @patch("tango.client.httpx.Client.request")
    def test_list_notices(self, mock_request):
        """Test list_notices endpoint"""
        mock_response = Mock()
        mock_response.is_success = True
        mock_response.content = b'{"count": 1}'
        mock_response.json.return_value = {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "notice_id": "N123",
                    "title": "Test Notice",
                    "solicitation_number": "SOL-123",
                    "posted_date": "2024-01-01T00:00:00Z",
                }
            ],
        }
        mock_request.return_value = mock_response

        client = TangoClient(api_key="test-key")
        notices = client.list_notices()

        assert notices.count == 1
        assert notices.results[0].notice_id == "N123"
        assert notices.results[0].title == "Test Notice"

    @patch("tango.client.httpx.Client.request")
    def test_list_grants(self, mock_request):
        """Test list_grants endpoint"""
        mock_response = Mock()
        mock_response.is_success = True
        mock_response.content = b'{"count": 1}'
        mock_response.json.return_value = {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "grant_id": 12345,
                    "opportunity_number": "OPP-123",
                    "title": "Test Grant",
                    "status": {"code": "OPEN", "description": "Open"},
                    "agency_code": "HHS",
                }
            ],
        }
        mock_request.return_value = mock_response

        client = TangoClient(api_key="test-key")
        grants = client.list_grants()

        assert grants.count == 1
        assert grants.results[0].grant_id == 12345
        assert grants.results[0].title == "Test Grant"
        assert grants.results[0].opportunity_number == "OPP-123"


# ============================================================================
# Parser Tests
# ============================================================================


class TestParsers:
    """Test parsing methods and edge cases"""

    def test_parse_date_iso_format(self):
        """Test _parse_date with ISO format"""
        client = TangoClient()
        result = client._parse_date("2024-01-15")
        assert result == date(2024, 1, 15)

    def test_parse_date_with_time(self):
        """Test _parse_date with datetime string"""
        client = TangoClient()
        result = client._parse_date("2024-01-15T10:30:00Z")
        assert result == date(2024, 1, 15)

    def test_parse_date_none(self):
        """Test _parse_date with None"""
        client = TangoClient()
        result = client._parse_date(None)
        assert result is None

    def test_parse_date_invalid(self):
        """Test _parse_date with invalid format"""
        client = TangoClient()
        result = client._parse_date("invalid-date")
        assert result is None

    def test_parse_datetime_iso(self):
        """Test _parse_datetime with ISO format"""
        client = TangoClient()
        result = client._parse_datetime("2024-01-15T10:30:00Z")
        assert isinstance(result, datetime)
        assert result.year == 2024

    def test_parse_datetime_none(self):
        """Test _parse_datetime with None"""
        client = TangoClient()
        result = client._parse_datetime(None)
        assert result is None

    def test_parse_datetime_invalid(self):
        """Test _parse_datetime with invalid format"""
        client = TangoClient()
        result = client._parse_datetime("invalid")
        assert result is None

    def test_parse_decimal_valid(self):
        """Test _parse_decimal with valid value"""
        client = TangoClient()
        result = client._parse_decimal("12345.67")
        assert result == Decimal("12345.67")

    def test_parse_decimal_none(self):
        """Test _parse_decimal with None"""
        client = TangoClient()
        result = client._parse_decimal(None)
        assert result is None

    def test_parse_decimal_invalid(self):
        """Test _parse_decimal with invalid value"""
        client = TangoClient()
        result = client._parse_decimal("not-a-number")
        assert result is None

    def test_parse_location_complete(self):
        """Test _parse_location with full data"""
        client = TangoClient()
        data = {
            "city": "Washington",
            "state_code": "DC",
            "zip": "20001",
            "latitude": 38.9072,
            "longitude": -77.0369,
        }
        result = client._parse_location(data)
        assert result.city == "Washington"
        assert result.state_code == "DC"
        assert result.zip_code == "20001"

    def test_parse_location_none(self):
        """Test _parse_location with None"""
        client = TangoClient()
        result = client._parse_location(None)
        assert result is None

    def test_parse_agency_with_office_fields(self):
        """Test _parse_agency with code/name (shaped response)"""
        client = TangoClient()
        data = {"code": "GSA-001", "name": "GSA Office", "agency": "GSA"}
        result = client._parse_agency(data)
        assert result.code == "GSA-001"
        assert result.name == "GSA Office"

    def test_parse_agency_with_department(self):
        """Test _parse_agency with department"""
        client = TangoClient()
        data = {
            "code": "GSA",
            "name": "General Services Admin",
            "department": {"name": "Executive", "code": 100},
        }
        result = client._parse_agency(data)
        assert result.code == "GSA"
        assert result.department.name == "Executive"

    def test_parse_agency_none(self):
        """Test _parse_agency with None"""
        client = TangoClient()
        result = client._parse_agency(None)
        assert result is None
