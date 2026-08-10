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
    def test_list_offices(self, mock_request):
        """Test list_offices method"""
        mock_response = Mock()
        mock_response.is_success = True
        mock_response.json.return_value = {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [{"code": "OFF1", "name": "Office One", "agency": "4700"}],
        }
        mock_response.content = b'{"count": 1}'
        mock_request.return_value = mock_response

        client = TangoClient(api_key="test-key")
        offices = client.list_offices(limit=10)

        assert offices.count == 1
        assert len(offices.results) == 1
        assert offices.results[0]["code"] == "OFF1"
        assert offices.results[0]["name"] == "Office One"

    @patch("tango.client.httpx.Client.request")
    def test_get_office(self, mock_request):
        """Test get_office method"""
        mock_response = Mock()
        mock_response.is_success = True
        mock_response.json.return_value = {"code": "OFF1", "name": "Office One", "agency": "4700"}
        mock_response.content = b'{"code": "OFF1"}'
        mock_request.return_value = mock_response

        client = TangoClient(api_key="test-key")
        office = client.get_office("OFF1")

        assert office["code"] == "OFF1"
        assert office["name"] == "Office One"

    @patch("tango.client.httpx.Client.request")
    def test_list_naics(self, mock_request):
        """Test list_naics method"""
        mock_response = Mock()
        mock_response.is_success = True
        mock_response.json.return_value = {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [{"code": "541511", "description": "Custom Computer Programming"}],
        }
        mock_response.content = b'{"count": 1}'
        mock_request.return_value = mock_response

        client = TangoClient(api_key="test-key")
        naics = client.list_naics(limit=10, search="programming")

        assert naics.count == 1
        assert len(naics.results) == 1
        assert naics.results[0]["code"] == "541511"
        call_args = mock_request.call_args
        assert call_args[1]["params"]["search"] == "programming"

    @patch("tango.client.httpx.Client.request")
    def test_list_organizations_with_default_shape(self, mock_request):
        """Test list_organizations uses default minimal shape"""
        mock_response = Mock()
        mock_response.is_success = True
        mock_response.json.return_value = {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [{"key": "ORG1", "fh_key": "DOD", "name": "Department of Defense"}],
        }
        mock_response.content = b'{"count": 1}'
        mock_request.return_value = mock_response

        client = TangoClient(api_key="test-key")
        orgs = client.list_organizations(limit=10)

        call_args = mock_request.call_args
        assert call_args[1]["params"]["shape"] == ShapeConfig.ORGANIZATIONS_MINIMAL
        assert orgs.count == 1
        assert orgs.results[0]["key"] == "ORG1"

    @patch("tango.client.httpx.Client.request")
    def test_list_otas_with_default_shape(self, mock_request):
        """Test list_otas uses default minimal shape and cursor pagination"""
        mock_response = Mock()
        mock_response.is_success = True
        mock_response.json.return_value = {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "key": "OTA-1",
                    "piid": "PIID-OTA",
                    "award_date": "2024-01-01",
                    "recipient": {"display_name": "Acme", "uei": "UEI123"},
                    "description": "OTA award",
                    "total_contract_value": "50000.00",
                    "obligated": "25000.00",
                }
            ],
            "cursor": "next-page-token",
        }
        mock_response.content = b'{"count": 1}'
        mock_request.return_value = mock_response

        client = TangoClient(api_key="test-key")
        otas = client.list_otas(limit=10)

        call_args = mock_request.call_args
        assert call_args[1]["params"]["shape"] == ShapeConfig.OTAS_MINIMAL
        assert otas.count == 1
        assert otas.results[0]["key"] == "OTA-1"
        assert otas.cursor == "next-page-token"

    @patch("tango.client.httpx.Client.request")
    def test_list_otidvs_with_default_shape(self, mock_request):
        """Test list_otidvs uses default minimal shape"""
        mock_response = Mock()
        mock_response.is_success = True
        mock_response.json.return_value = {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "key": "OTIDV-1",
                    "piid": "PIID-OT",
                    "award_date": "2024-01-01",
                    "recipient": {"display_name": "Acme", "uei": "UEI123"},
                    "description": "OTIDV",
                    "total_contract_value": "100000.00",
                    "obligated": "50000.00",
                    "idv_type": {},
                }
            ],
        }
        mock_response.content = b'{"count": 1}'
        mock_request.return_value = mock_response

        client = TangoClient(api_key="test-key")
        otidvs = client.list_otidvs(limit=10)

        call_args = mock_request.call_args
        assert call_args[1]["params"]["shape"] == ShapeConfig.OTIDVS_MINIMAL
        assert otidvs.count == 1
        assert otidvs.results[0]["key"] == "OTIDV-1"

    @patch("tango.client.httpx.Client.request")
    def test_list_subawards_with_default_shape(self, mock_request):
        """Test list_subawards uses default minimal shape"""
        mock_response = Mock()
        mock_response.is_success = True
        mock_response.json.return_value = {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "id": "SUB-1",
                    "award_key": "CONT_AWD_123",
                    "prime_recipient": {"uei": "P1", "display_name": "Prime"},
                    "subaward_recipient": {"uei": "S1", "display_name": "Sub"},
                    "amount": "10000.00",
                }
            ],
        }
        mock_response.content = b'{"count": 1}'
        mock_request.return_value = mock_response

        client = TangoClient(api_key="test-key")
        subawards = client.list_subawards(limit=10)

        call_args = mock_request.call_args
        assert call_args[1]["params"]["shape"] == ShapeConfig.SUBAWARDS_MINIMAL
        assert subawards.count == 1
        # Default shape does not include id (API rejects it); assert on award_key
        assert subawards.results[0]["award_key"] == "CONT_AWD_123"

    @patch("tango.client.httpx.Client.request")
    def test_list_itdashboard_investments_with_default_shape(self, mock_request):
        """Test list_itdashboard_investments uses default minimal shape and hits the right URL."""
        mock_response = Mock()
        mock_response.is_success = True
        mock_response.json.return_value = {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "uii": "021-000000001",
                    "agency_name": "Department of Transportation",
                    "bureau_name": "Federal Aviation Administration",
                    "investment_title": "NextGen Air Traffic",
                    "type_of_investment": "Major IT Investment",
                    "part_of_it_portfolio": "Yes",
                    "updated_time": "2024-01-15T12:00:00Z",
                    "url": "https://www.itdashboard.gov/investment-details/021-000000001",
                }
            ],
        }
        mock_response.content = b'{"count": 1}'
        mock_request.return_value = mock_response

        client = TangoClient(api_key="test-key")
        investments = client.list_itdashboard_investments(limit=10)

        call_args = mock_request.call_args
        # Hits /api/itdashboard/, not /api/itdashboard_investments/
        assert call_args[1]["url"].endswith("/api/itdashboard/")
        assert call_args[1]["params"]["shape"] == ShapeConfig.ITDASHBOARD_INVESTMENTS_MINIMAL
        assert investments.count == 1
        assert investments.results[0]["uii"] == "021-000000001"
        assert isinstance(investments.results[0]["updated_time"], datetime)

    @patch("tango.client.httpx.Client.request")
    def test_list_itdashboard_investments_passes_filters(self, mock_request):
        """Test that all filter params are forwarded with correct serialization."""
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
        client.list_itdashboard_investments(
            search="cyber",
            agency_code=21,
            agency_name="defense",
            type_of_investment="Major IT Investment",
            updated_time_after=date(2024, 1, 1),
            updated_time_before="2024-12-31",
            cio_rating=1,
            cio_rating_max=2,
            performance_risk=True,
        )

        params = mock_request.call_args[1]["params"]
        assert params["search"] == "cyber"
        assert params["agency_code"] == 21
        assert params["agency_name"] == "defense"
        assert params["type_of_investment"] == "Major IT Investment"
        assert params["updated_time_after"] == "2024-01-01"
        assert params["updated_time_before"] == "2024-12-31"
        assert params["cio_rating"] == 1
        assert params["cio_rating_max"] == 2
        # Booleans are serialized as the lowercase strings the API expects.
        assert params["performance_risk"] == "true"

    @patch("tango.client.httpx.Client.request")
    def test_get_itdashboard_investment_by_uii(self, mock_request):
        """Test get_itdashboard_investment uses UII in path and comprehensive default shape."""
        mock_response = Mock()
        mock_response.is_success = True
        mock_response.json.return_value = {
            "uii": "021-000000001",
            "agency_code": 21,
            "agency_name": "DOT",
            "bureau_code": 12,
            "bureau_name": "FAA",
            "investment_title": "NextGen",
            "type_of_investment": "Major IT Investment",
            "part_of_it_portfolio": "Yes",
            "updated_time": "2024-01-15T12:00:00Z",
            "url": "https://www.itdashboard.gov/investment-details/021-000000001",
        }
        mock_response.content = b'{"uii": "021-000000001"}'
        mock_request.return_value = mock_response

        client = TangoClient(api_key="test-key")
        investment = client.get_itdashboard_investment("021-000000001")

        call_args = mock_request.call_args
        assert call_args[1]["url"].endswith("/api/itdashboard/021-000000001/")
        assert call_args[1]["params"]["shape"] == ShapeConfig.ITDASHBOARD_INVESTMENTS_COMPREHENSIVE
        assert investment["uii"] == "021-000000001"
        assert investment["agency_code"] == 21

    @patch("tango.client.httpx.Client.request")
    def test_list_itdashboard_investments_funding_expansion(self, mock_request):
        """Test that funding/details dict expansions and nested-list expansions parse through."""
        mock_response = Mock()
        mock_response.is_success = True
        mock_response.json.return_value = {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "uii": "021-X",
                    "agency_name": "DOT",
                    "funding": {
                        "fy2024_internal_funding": "1000000.00",
                        "fy2024_contribution": "50000.00",
                    },
                    "cio_evaluation": [{"cioRating": "3 - Medium Risk", "latestIndicator": "Y"}],
                }
            ],
        }
        mock_response.content = b'{"count": 1}'
        mock_request.return_value = mock_response

        client = TangoClient(api_key="test-key")
        investments = client.list_itdashboard_investments(
            shape="uii,agency_name,funding(*),cio_evaluation(*)"
        )

        result = investments.results[0]
        assert result["uii"] == "021-X"
        assert result["funding"]["fy2024_internal_funding"] == "1000000.00"
        assert result["cio_evaluation"][0]["latestIndicator"] == "Y"

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

    @patch("tango.client.httpx.Client.request")
    def test_list_budget_accounts_range_filters(self, mock_request):
        """Range filters serialize to the API's ``field__gte`` / ``field__lte`` form."""
        mock_response = Mock()
        mock_response.is_success = True
        mock_response.json.return_value = {
            "count": 0,
            "next": None,
            "previous": None,
            "results": [],
        }
        mock_response.content = b'{"count": 0, "results": []}'
        mock_request.return_value = mock_response

        client = TangoClient(api_key="test-key")
        client.list_budget_accounts(
            fiscal_year=2024,
            contract_share_of_obligated_capped_gte=0.6,
            ba_growth_next_year_pct_gte=0.15,
            unobligated_balance_gte=200_000_000,
            unobligated_balance_lte=10_000_000_000,
            enacted_ba=3_135_000_000,
            ordering="-unobligated_balance",
        )

        params = mock_request.call_args[1]["params"]
        # Exact-match scalar filter still works.
        assert params["fiscal_year"] == 2024
        # Range filters use the API's double-underscore form.
        assert params["contract_share_of_obligated_capped__gte"] == 0.6
        assert params["ba_growth_next_year_pct__gte"] == 0.15
        assert params["unobligated_balance__gte"] == 200_000_000
        assert params["unobligated_balance__lte"] == 10_000_000_000
        # Range fields also accept exact-match.
        assert params["enacted_ba"] == 3_135_000_000
        # Ordering passes through untouched (callers prefix with '-' for desc).
        assert params["ordering"] == "-unobligated_balance"
        # Unspecified filters are not sent.
        assert "apportioned__gte" not in params
        assert "obligated_yoy_pct__lte" not in params

    @patch("tango.client.httpx.Client.request")
    def test_list_budget_accounts_no_filters_sends_only_pagination_and_shape(self, mock_request):
        """With no filter args, the request carries only paging + default shape."""
        mock_response = Mock()
        mock_response.is_success = True
        mock_response.json.return_value = {
            "count": 0,
            "next": None,
            "previous": None,
            "results": [],
        }
        mock_response.content = b'{"count": 0, "results": []}'
        mock_request.return_value = mock_response

        client = TangoClient(api_key="test-key")
        client.list_budget_accounts()

        params = mock_request.call_args[1]["params"]
        assert params["page"] == 1
        assert params["limit"] == 25
        assert "shape" in params
        # None of the new range filters leak through as null.
        leaked = [
            k for k in params if k.endswith("__gte") or k.endswith("__lte") or k == "fiscal_year"
        ]
        assert leaked == [], f"unexpected filter keys sent: {leaked}"


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


class TestWebhooksEndpoints:
    @patch("tango.client.httpx.Client.request")
    def test_list_webhook_event_types(self, mock_request):
        mock_response = Mock()
        mock_response.is_success = True
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "event_types": [
                {
                    "event_type": "alerts.contract.match",
                    "description": "",
                    "schema_version": 1,
                }
            ],
        }
        mock_response.content = b'{"event_types": []}'
        mock_request.return_value = mock_response

        client = TangoClient(api_key="test-key")
        resp = client.list_webhook_event_types()

        assert resp.event_types[0].event_type == "alerts.contract.match"

        call_args = mock_request.call_args
        assert call_args[1]["method"] == "GET"
        assert call_args[1]["url"].endswith("/api/webhooks/event-types/")

    @patch("tango.client.httpx.Client.request")
    def test_webhook_test_delivery_and_sample_payload(self, mock_request):
        client = TangoClient(api_key="test-key", base_url="https://example.test")

        test_delivery_response = Mock()
        test_delivery_response.is_success = True
        test_delivery_response.status_code = 200
        test_delivery_response.json.return_value = {
            "success": True,
            "status_code": 200,
            "message": "ok",
        }
        test_delivery_response.content = b'{"success": true}'

        sample_response = Mock()
        sample_response.is_success = True
        sample_response.status_code = 200
        sample_response.json.return_value = {
            "event_type": "awards.new_award",
            "sample_delivery": {
                "timestamp": "2026-01-01T00:00:00Z",
                "events": [{"event_type": "awards.new_award"}],
            },
        }
        sample_response.content = b'{"event_type": "awards.new_award"}'

        mock_request.side_effect = [test_delivery_response, sample_response]

        result = client.test_webhook_delivery()
        assert result.success is True

        sample = client.get_webhook_sample_payload(event_type="awards.new_award")
        assert sample["event_type"] == "awards.new_award"

        calls = mock_request.call_args_list
        assert calls[0][1]["method"] == "POST"
        assert calls[0][1]["url"].endswith("/api/webhooks/endpoints/test-delivery/")
        assert calls[0][1]["json"] == {}

        assert calls[1][1]["method"] == "GET"
        assert calls[1][1]["url"].endswith("/api/webhooks/endpoints/sample-payload/")
        assert calls[1][1]["params"]["event_type"] == "awards.new_award"

    @patch("tango.client.httpx.Client.request")
    def test_webhook_endpoints_crud(self, mock_request):
        client = TangoClient(api_key="test-key", base_url="https://example.test")

        list_response = Mock()
        list_response.is_success = True
        list_response.status_code = 200
        list_response.json.return_value = {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "id": "ep-1",
                    "name": "yoni",
                    "callback_url": "https://example.com/tango/webhooks",
                    "is_active": True,
                    "created_at": "2026-01-01T00:00:00Z",
                    "updated_at": "2026-01-01T00:00:00Z",
                }
            ],
        }
        list_response.content = b'{"count": 1}'

        create_response = Mock()
        create_response.is_success = True
        create_response.status_code = 201
        create_response.json.return_value = {
            "id": "ep-1",
            "name": "yoni",
            "callback_url": "https://example.com/tango/webhooks",
            "secret": "secret",
            "is_active": True,
            "created_at": "2026-01-01T00:00:00Z",
            "updated_at": "2026-01-01T00:00:00Z",
        }
        create_response.content = b'{"id": "ep-1"}'

        update_response = Mock()
        update_response.is_success = True
        update_response.status_code = 200
        update_response.json.return_value = {
            "id": "ep-1",
            "name": "yoni",
            "callback_url": "https://example.com/tango/webhooks",
            "is_active": False,
            "created_at": "2026-01-01T00:00:00Z",
            "updated_at": "2026-01-02T00:00:00Z",
        }
        update_response.content = b'{"id": "ep-1"}'

        delete_response = Mock()
        delete_response.is_success = True
        delete_response.status_code = 204
        delete_response.content = b""

        mock_request.side_effect = [
            list_response,
            create_response,
            update_response,
            delete_response,
        ]

        endpoints = client.list_webhook_endpoints(page=2, limit=10)
        assert endpoints.count == 1
        assert endpoints.results[0].name == "yoni"

        created = client.create_webhook_endpoint(
            "https://example.com/tango/webhooks", is_active=True, name="primary"
        )
        assert created.secret == "secret"

        updated = client.update_webhook_endpoint("ep-1", is_active=False)
        assert updated.is_active is False

        client.delete_webhook_endpoint("ep-1")

        calls = mock_request.call_args_list
        assert calls[0][1]["method"] == "GET"
        assert calls[0][1]["params"]["page"] == 2
        assert calls[0][1]["params"]["limit"] == 10

        assert calls[1][1]["method"] == "POST"
        assert calls[1][1]["json"]["callback_url"] == "https://example.com/tango/webhooks"
        assert calls[1][1]["json"]["is_active"] is True
        assert calls[1][1]["json"]["name"] == "primary"

        assert calls[2][1]["method"] == "PATCH"
        assert calls[2][1]["json"]["is_active"] is False

        assert calls[3][1]["method"] == "DELETE"

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
    def test_400_structured_shape_error(self, mock_request):
        """Test 400 with structured shape-error body surfaces issues and available_fields"""
        body = {
            "error": "Invalid shape",
            "issues": [{"path": "fair_opportunity_limited_sources", "reason": "unknown_field"}],
            "available_fields": {"fields": ["piid", "competition"]},
        }
        mock_response = Mock()
        mock_response.is_success = False
        mock_response.status_code = 400
        mock_response.content = b"x"
        mock_response.json.return_value = body
        mock_request.return_value = mock_response

        client = TangoClient(api_key="test-key")

        with pytest.raises(TangoValidationError) as exc_info:
            client.list_agencies()

        err = exc_info.value
        assert str(err) == (
            "Invalid request parameters: Invalid shape: "
            "fair_opportunity_limited_sources (unknown_field)"
        )
        assert err.issues == [
            {"path": "fair_opportunity_limited_sources", "reason": "unknown_field"}
        ]
        assert err.available_fields == {"fields": ["piid", "competition"]}
        assert err.response_data == body

    @patch("tango.client.httpx.Client.request")
    def test_400_validation_error_issues_accessors_empty(self, mock_request):
        """Test issues/available_fields accessors on a plain 400 body"""
        mock_response = Mock()
        mock_response.is_success = False
        mock_response.status_code = 400
        mock_response.content = b'{"error": "invalid params"}'
        mock_response.json.return_value = {"error": "invalid params"}
        mock_request.return_value = mock_response

        client = TangoClient(api_key="test-key")

        with pytest.raises(TangoValidationError) as exc_info:
            client.list_agencies()

        assert exc_info.value.issues == []
        assert exc_info.value.available_fields is None

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
        """Test 429 Rate Limit raises TangoRateLimitError with parsed body"""
        mock_response = Mock()
        mock_response.is_success = False
        mock_response.status_code = 429
        mock_response.content = b'{"detail": "Rate limit exceeded for burst. Please try again in 45 seconds.", "wait_in_seconds": 45}'
        mock_response.json.return_value = {
            "detail": "Rate limit exceeded for burst. Please try again in 45 seconds.",
            "wait_in_seconds": 45,
        }
        mock_response.headers = {}
        mock_request.return_value = mock_response

        client = TangoClient(api_key="test-key")

        with pytest.raises(TangoRateLimitError) as exc_info:
            client.list_agencies()

        assert exc_info.value.status_code == 429
        assert exc_info.value.wait_in_seconds == 45
        assert "burst" in exc_info.value.detail
        assert exc_info.value.limit_type == "burst"

    @patch("tango.client.httpx.Client.request")
    def test_429_daily_limit_error(self, mock_request):
        """Test 429 for daily limit includes correct limit_type"""
        mock_response = Mock()
        mock_response.is_success = False
        mock_response.status_code = 429
        mock_response.content = b'{"detail": "Rate limit exceeded for daily. Please try again in 3600 seconds.", "wait_in_seconds": 3600}'
        mock_response.json.return_value = {
            "detail": "Rate limit exceeded for daily. Please try again in 3600 seconds.",
            "wait_in_seconds": 3600,
        }
        mock_response.headers = {}
        mock_request.return_value = mock_response

        client = TangoClient(api_key="test-key")

        with pytest.raises(TangoRateLimitError) as exc_info:
            client.list_agencies()

        assert exc_info.value.limit_type == "daily"
        assert exc_info.value.wait_in_seconds == 3600

    @patch("tango.client.httpx.Client.request")
    def test_429_empty_body(self, mock_request):
        """Test 429 with no content body still works"""
        mock_response = Mock()
        mock_response.is_success = False
        mock_response.status_code = 429
        mock_response.content = None
        mock_response.headers = {}
        mock_request.return_value = mock_response

        client = TangoClient(api_key="test-key")

        with pytest.raises(TangoRateLimitError) as exc_info:
            client.list_agencies()

        assert exc_info.value.status_code == 429
        assert exc_info.value.wait_in_seconds is None
        assert exc_info.value.limit_type is None

    @patch("tango.client.httpx.Client.request")
    def test_rate_limit_headers_parsed(self, mock_request):
        """Test rate limit headers are parsed from successful responses"""
        mock_response = Mock()
        mock_response.is_success = True
        mock_response.status_code = 200
        mock_response.content = b'{"results": []}'
        mock_response.json.return_value = {"results": []}
        mock_response.headers = {
            "X-RateLimit-Limit": "100",
            "X-RateLimit-Remaining": "95",
            "X-RateLimit-Reset": "45",
            "X-RateLimit-Daily-Limit": "2400",
            "X-RateLimit-Daily-Remaining": "2350",
            "X-RateLimit-Daily-Reset": "86400",
            "X-RateLimit-Burst-Limit": "100",
            "X-RateLimit-Burst-Remaining": "95",
            "X-RateLimit-Burst-Reset": "45",
        }
        mock_request.return_value = mock_response

        client = TangoClient(api_key="test-key")
        assert client.rate_limit_info is None

        client._request("GET", "/api/agencies/")

        info = client.rate_limit_info
        assert info is not None
        assert info.limit == 100
        assert info.remaining == 95
        assert info.reset == 45
        assert info.daily_limit == 2400
        assert info.daily_remaining == 2350
        assert info.burst_remaining == 95

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
        assert "naics_code" not in params, (
            "naics_code should be mapped to 'naics', not sent as naics_code"
        )

        # Verify naics_code is NOT in the shape parameter
        shape = params.get("shape", "")
        assert "naics_code" not in shape, (
            f"naics_code should NOT be in shape parameter, but shape is: {shape}"
        )

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
    def test_get_entity_budget_flows_defaults(self, mock_request):
        """Default call uses page=1, limit=25, no fiscal_year, and returns
        a PaginatedResponse."""
        mock_response = Mock()
        mock_response.is_success = True
        mock_response.content = b'{"count": 1}'
        mock_response.json.return_value = {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "federal_account_symbol": "075-0140",
                    "fiscal_year": 2024,
                    "contract_obligated": "1000.00",
                }
            ],
        }
        mock_request.return_value = mock_response

        client = TangoClient(api_key="test-key")
        flows = client.get_entity_budget_flows("ABC123")

        params = mock_request.call_args[1]["params"]
        assert params == {"page": 1, "limit": 25}

        assert flows.count == 1
        assert flows.next is None
        assert flows.previous is None
        assert flows.results[0]["federal_account_symbol"] == "075-0140"

    @patch("tango.client.httpx.Client.request")
    def test_get_entity_budget_flows_with_params(self, mock_request):
        """page, limit, and fiscal_year flow through; limit caps at 100."""
        mock_response = Mock()
        mock_response.is_success = True
        mock_response.content = b'{"count": 0}'
        mock_response.json.return_value = {
            "count": 0,
            "next": "https://example/next",
            "previous": None,
            "results": [],
        }
        mock_request.return_value = mock_response

        client = TangoClient(api_key="test-key")
        flows = client.get_entity_budget_flows("ABC123", page=2, limit=500, fiscal_year=2024)

        params = mock_request.call_args[1]["params"]
        assert params == {"page": 2, "limit": 100, "fiscal_year": 2024}
        assert flows.next == "https://example/next"

    def test_get_entity_budget_flows_requires_uei(self):
        """Empty UEI raises TangoValidationError without issuing a request."""
        client = TangoClient(api_key="test-key")
        with pytest.raises(TangoValidationError):
            client.get_entity_budget_flows("")

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


class TestProtestFilters:
    """`naics_code` reached the SDK late — the conformance check could not see
    the protests resource at all until makegov/tango#2944 fixed the contract's
    shape blind spot and the resource was wired into RESOURCE_TO_METHOD.
    """

    @patch("tango.client.httpx.Client.request")
    def test_list_protests_forwards_naics_code(self, mock_request):
        mock_response = Mock()
        mock_response.is_success = True
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "count": 0,
            "next": None,
            "previous": None,
            "results": [],
        }
        mock_response.content = b'{"count": 0}'
        mock_request.return_value = mock_response

        client = TangoClient(api_key="test-key")
        client.list_protests(naics_code="541519", outcome="Sustained")

        params = mock_request.call_args[1]["params"]
        assert params["naics_code"] == "541519"
        assert params["outcome"] == "Sustained"

    @patch("tango.client.httpx.Client.request")
    def test_list_protests_omits_unset_naics_code(self, mock_request):
        mock_response = Mock()
        mock_response.is_success = True
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "count": 0,
            "next": None,
            "previous": None,
            "results": [],
        }
        mock_response.content = b'{"count": 0}'
        mock_request.return_value = mock_response

        client = TangoClient(api_key="test-key")
        client.list_protests()

        assert "naics_code" not in mock_request.call_args[1]["params"]


def _stub_empty_page(mock_request):
    """Wire a mocked httpx response for an empty paginated result."""
    mock_response = Mock()
    mock_response.is_success = True
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "count": 0,
        "next": None,
        "previous": None,
        "results": [],
    }
    mock_response.content = b'{"count": 0}'
    mock_request.return_value = mock_response


class TestPscFilters:
    """`has_awards` reached the SDK only after makegov/tango#2948 published it.

    The param filtered for real but was absent from the contract, so the conformance check had nothing to compare against and the gap went unreported.
    """

    @patch("tango.client.httpx.Client.request")
    def test_list_psc_forwards_has_awards_true(self, mock_request):
        _stub_empty_page(mock_request)
        TangoClient(api_key="test-key").list_psc(has_awards=True)
        assert mock_request.call_args[1]["params"]["has_awards"] == "true"

    @patch("tango.client.httpx.Client.request")
    def test_list_psc_forwards_has_awards_false(self, mock_request):
        """False must be sent, not dropped — the API distinguishes them."""
        _stub_empty_page(mock_request)
        TangoClient(api_key="test-key").list_psc(has_awards=False)
        assert mock_request.call_args[1]["params"]["has_awards"] == "false"

    @patch("tango.client.httpx.Client.request")
    def test_list_psc_omits_unset_has_awards(self, mock_request):
        _stub_empty_page(mock_request)
        TangoClient(api_key="test-key").list_psc()
        assert "has_awards" not in mock_request.call_args[1]["params"]


class TestEntityFilters:
    """The server ORs pipe-separated `socioeconomic` values; the SDK's job is to forward the string verbatim."""

    @patch("tango.client.httpx.Client.request")
    def test_list_entities_forwards_pipe_separated_socioeconomic(self, mock_request):
        _stub_empty_page(mock_request)
        TangoClient(api_key="test-key").list_entities(socioeconomic="OY|A2")
        assert mock_request.call_args[1]["params"]["socioeconomic"] == "OY|A2"

    @patch("tango.client.httpx.Client.request")
    def test_list_entities_omits_unset_socioeconomic(self, mock_request):
        _stub_empty_page(mock_request)
        TangoClient(api_key="test-key").list_entities()
        assert "socioeconomic" not in mock_request.call_args[1]["params"]


class TestAgencyFilterDiagnostics:
    """`meta` from the API's agency-filter diagnostics.

    Agency resolution is fuzzy, so a token can be dropped entirely or matched to an
    organization the caller did not intend. Before the API exposed `meta`, both were
    indistinguishable from "no such records exist" — and the SDK is the last place that
    distinction can reach a user.
    """

    HUD = {
        "key": "3f2a0000-0000-0000-0000-000000000001",
        "name": "Department of Housing and Urban Development",
        "level": 1,
        "cgac": "086",
        "fpds_code": None,
    }

    def _mock(self, mock_request, meta=None):
        payload = {"count": 0, "next": None, "previous": None, "results": []}
        if meta is not None:
            payload["meta"] = meta
        response = Mock()
        response.is_success = True
        response.json.return_value = payload
        response.content = b'{"count": 0}'
        mock_request.return_value = response
        return TangoClient(api_key="test-key")

    @patch("tango.client.httpx.Client.request")
    def test_meta_is_carried_through_to_the_response(self, mock_request):
        meta = {
            "resolved_filters": {
                "awarding_agency": [
                    {"token": "HUD", "resolved": self.HUD},
                    {"token": "HUDD", "resolved": None},
                ]
            },
            "warnings": ["Agency filter 'awarding_agency': 'HUDD' did not match."],
        }
        client = self._mock(mock_request, meta)

        response = client.list_contracts(awarding_agency="HUD|HUDD")

        assert response.meta == meta

    @patch("tango.client.httpx.Client.request")
    def test_dropped_tokens_are_reported_per_filter(self, mock_request):
        client = self._mock(
            mock_request,
            {
                "resolved_filters": {
                    "awarding_agency": [
                        {"token": "HUD", "resolved": self.HUD},
                        {"token": "HUDD", "resolved": None},
                    ],
                    "funding_agency": [{"token": "NOPE", "resolved": None}],
                }
            },
        )

        response = client.list_contracts(awarding_agency="HUD|HUDD")

        assert response.unresolved_agency_tokens == {
            "awarding_agency": ["HUDD"],
            "funding_agency": ["NOPE"],
        }

    @patch("tango.client.httpx.Client.request")
    def test_resolved_agencies_expose_the_matched_organization(self, mock_request):
        """The wrong-subtree case: nothing was dropped, so only the resolved name
        reveals that a token matched an organization the caller did not intend."""
        client = self._mock(
            mock_request,
            {"resolved_filters": {"awarding_agency": [{"token": "HUD", "resolved": self.HUD}]}},
        )

        response = client.list_contracts(awarding_agency="HUD")

        assert response.unresolved_agency_tokens == {}
        assert [org["name"] for org in response.resolved_agencies["awarding_agency"]] == [
            "Department of Housing and Urban Development"
        ]

    @patch("tango.client.httpx.Client.request")
    def test_warnings_are_surfaced(self, mock_request):
        client = self._mock(
            mock_request, {"warnings": ["Agency filter 'agency': 'X' did not match."]}
        )

        response = client.list_opportunities()

        assert response.agency_warnings == ["Agency filter 'agency': 'X' did not match."]

    @patch("tango.client.httpx.Client.request")
    def test_absent_meta_yields_empty_accessors_not_errors(self, mock_request):
        """Most responses carry no `meta` at all; the accessors must stay total."""
        client = self._mock(mock_request, meta=None)

        response = client.list_contracts()

        assert response.meta is None
        assert response.agency_warnings == []
        assert response.unresolved_agency_tokens == {}
        assert response.resolved_agencies == {}

    @patch("tango.client.httpx.Client.request")
    def test_malformed_meta_does_not_raise(self, mock_request):
        """`meta` is server-controlled; a shape change must not crash a caller's loop."""
        client = self._mock(
            mock_request,
            {"resolved_filters": "not-a-dict", "warnings": "not-a-list"},
        )

        response = client.list_contracts()

        assert response.agency_warnings == []
        assert response.unresolved_agency_tokens == {}
        assert response.resolved_agencies == {}

    @patch("tango.client.httpx.Client.request")
    def test_full_miss_raises_with_the_offending_token(self, mock_request):
        """A fully-unresolvable agency filter is a 400, not an empty page."""
        response = Mock()
        response.is_success = False
        response.status_code = 400
        response.content = b'{"error": "No agency found matching HUDD."}'
        response.json.return_value = {"error": "No agency found matching 'HUDD'."}
        mock_request.return_value = response

        client = TangoClient(api_key="test-key")

        with pytest.raises(TangoValidationError) as excinfo:
            client.list_contracts(awarding_agency="HUDD")

        assert "HUDD" in str(excinfo.value)
