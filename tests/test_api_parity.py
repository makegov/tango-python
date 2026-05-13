"""Unit tests for API-parity additions (feat/api-parity branch).

Mock-driven tests — no network. Verifies that the new methods build the
right HTTP request and parse the response into the expected shapes.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import Mock, patch

import pytest

from tango import (
    ResolveResult,
    TangoClient,
    ValidateResult,
    WebhookAlert,
)
from tango.exceptions import TangoValidationError


def _mock_response(payload: dict[str, Any], status: int = 200) -> Mock:
    resp = Mock()
    resp.is_success = 200 <= status < 400
    resp.status_code = status
    resp.json.return_value = payload
    resp.content = b'{"x": 1}'
    resp.headers = {}
    return resp


@patch("tango.client.httpx.Client.request")
class TestPostJsonKwargAlias:
    """`_post` should accept either `json_data` (positional) or `json` (keyword)."""

    def test_positional_json_data(self, mock_request: Mock) -> None:
        mock_request.return_value = _mock_response({"ok": True})
        client = TangoClient(api_key="x", base_url="https://t.example")
        client._post("/api/foo/", {"a": 1})
        assert mock_request.call_args[1]["json"] == {"a": 1}

    def test_keyword_json_alias(self, mock_request: Mock) -> None:
        mock_request.return_value = _mock_response({"ok": True})
        client = TangoClient(api_key="x", base_url="https://t.example")
        client._post("/api/foo/", json={"a": 2})
        assert mock_request.call_args[1]["json"] == {"a": 2}

    def test_keyword_json_data_alias(self, mock_request: Mock) -> None:
        mock_request.return_value = _mock_response({"ok": True})
        client = TangoClient(api_key="x", base_url="https://t.example")
        client._post("/api/foo/", json_data={"a": 3})
        assert mock_request.call_args[1]["json"] == {"a": 3}

    def test_patch_json_kwarg(self, mock_request: Mock) -> None:
        mock_request.return_value = _mock_response({"ok": True})
        client = TangoClient(api_key="x", base_url="https://t.example")
        client._patch("/api/foo/1/", json={"b": 4})
        assert mock_request.call_args[1]["json"] == {"b": 4}


@patch("tango.client.httpx.Client.request")
class TestResolveValidate:
    def test_resolve_builds_request(self, mock_request: Mock) -> None:
        mock_request.return_value = _mock_response(
            {
                "candidates": [
                    {
                        "identifier": "ABC123",
                        "display_name": "Acme Corp",
                        "match_tier": "high",
                        "score": 0.95,
                    },
                    {"identifier": "DEF456", "display_name": "Acme LLC"},
                ],
                "count": 2,
            }
        )
        client = TangoClient(api_key="x", base_url="https://t.example")
        out = client.resolve("Acme", target_type="entity", state="CA", city="LA", context="cyber")

        # Request shape
        call = mock_request.call_args
        assert call[1]["method"] == "POST"
        assert call[1]["url"].endswith("/api/resolve/")
        body = call[1]["json"]
        assert body["name"] == "Acme"
        assert body["target_type"] == "entity"
        assert body["state"] == "CA"
        assert body["city"] == "LA"
        assert body["context"] == "cyber"

        # Response parsing
        assert isinstance(out, ResolveResult)
        assert out.count == 2
        assert out.candidates[0].identifier == "ABC123"
        assert out.candidates[0].match_tier == "high"
        # extra fields preserved
        assert out.candidates[0].extra == {"score": 0.95}
        assert out.candidates[1].match_tier is None

    def test_resolve_validates_target_type(self, mock_request: Mock) -> None:
        client = TangoClient(api_key="x", base_url="https://t.example")
        with pytest.raises(TangoValidationError):
            client.resolve("Acme", target_type="bogus")

    def test_resolve_requires_name(self, mock_request: Mock) -> None:
        client = TangoClient(api_key="x", base_url="https://t.example")
        with pytest.raises(TangoValidationError):
            client.resolve("", target_type="entity")

    def test_validate_builds_request(self, mock_request: Mock) -> None:
        mock_request.return_value = _mock_response(
            {"result": "valid", "type": "uei", "value": "ABC123"}
        )
        client = TangoClient(api_key="x", base_url="https://t.example")
        out = client.validate("uei", "ABC123")

        call = mock_request.call_args
        assert call[1]["method"] == "POST"
        assert call[1]["url"].endswith("/api/validate/")
        # Maps `identifier_type` -> `type` in the body
        assert call[1]["json"] == {"type": "uei", "value": "ABC123"}

        assert isinstance(out, ValidateResult)
        assert out.result == "valid"
        assert out.type == "uei"
        assert out.value == "ABC123"
        assert out.errors is None

    def test_validate_rejects_unknown_type(self, mock_request: Mock) -> None:
        client = TangoClient(api_key="x", base_url="https://t.example")
        with pytest.raises(TangoValidationError):
            client.validate("naics", "541511")


@patch("tango.client.httpx.Client.request")
class TestWebhookAlerts:
    def test_create_webhook_alert(self, mock_request: Mock) -> None:
        mock_request.return_value = _mock_response(
            {
                "alert_id": "alert-1",
                "name": "my-alert",
                "query_type": "opportunity",
                "filters": {"naics": "541511"},
                "frequency": "daily",
                "cron_expression": None,
                "status": "active",
                "created_at": "2026-05-11T00:00:00Z",
                "last_checked_at": None,
                "match_count": 0,
            }
        )
        client = TangoClient(api_key="x", base_url="https://t.example")
        out = client.create_webhook_alert(
            name="my-alert",
            query_type="opportunity",
            filters={"naics": "541511"},
            frequency="daily",
        )

        call = mock_request.call_args
        assert call[1]["method"] == "POST"
        assert call[1]["url"].endswith("/api/webhooks/alerts/")
        assert call[1]["json"] == {
            "name": "my-alert",
            "query_type": "opportunity",
            "filters": {"naics": "541511"},
            "frequency": "daily",
        }

        assert isinstance(out, WebhookAlert)
        assert out.alert_id == "alert-1"
        assert out.filters == {"naics": "541511"}

    def test_create_webhook_alert_validates_inputs(self, mock_request: Mock) -> None:
        client = TangoClient(api_key="x", base_url="https://t.example")
        with pytest.raises(TangoValidationError):
            client.create_webhook_alert(name="", query_type="entity", filters={"x": 1})
        with pytest.raises(TangoValidationError):
            client.create_webhook_alert(name="n", query_type="", filters={"x": 1})
        with pytest.raises(TangoValidationError):
            client.create_webhook_alert(name="n", query_type="entity", filters={})

    def test_update_webhook_alert(self, mock_request: Mock) -> None:
        mock_request.return_value = _mock_response(
            {
                "alert_id": "alert-1",
                "name": "renamed",
                "query_type": "opportunity",
                "filters": {"naics": "541511"},
                "frequency": "weekly",
                "cron_expression": None,
                "status": "active",
                "created_at": "2026-05-11T00:00:00Z",
            }
        )
        client = TangoClient(api_key="x", base_url="https://t.example")
        out = client.update_webhook_alert("alert-1", name="renamed", frequency="weekly")

        call = mock_request.call_args
        assert call[1]["method"] == "PATCH"
        assert call[1]["json"] == {"name": "renamed", "frequency": "weekly"}
        assert out.name == "renamed"
        assert out.frequency == "weekly"

    def test_list_webhook_alerts(self, mock_request: Mock) -> None:
        mock_request.return_value = _mock_response(
            {
                "count": 1,
                "next": None,
                "previous": None,
                "results": [
                    {
                        "alert_id": "a1",
                        "name": "x",
                        "query_type": "entity",
                        "filters": {"uei": "U"},
                        "frequency": "realtime",
                        "cron_expression": None,
                        "status": "active",
                        "created_at": "2026-01-01T00:00:00Z",
                        "match_count": 5,
                    }
                ],
            }
        )
        client = TangoClient(api_key="x", base_url="https://t.example")
        out = client.list_webhook_alerts()
        assert out.count == 1
        assert out.results[0].alert_id == "a1"
        assert out.results[0].match_count == 5


@patch("tango.client.httpx.Client.request")
class TestWebhookEndpointWriteFixes:
    def test_create_endpoint_passes_name(self, mock_request: Mock) -> None:
        mock_request.return_value = _mock_response(
            {
                "id": "ep-1",
                "name": "primary",
                "callback_url": "https://x/",
                "secret": "s",
                "is_active": True,
                "created_at": "2026-01-01",
                "updated_at": "2026-01-01",
            }
        )
        client = TangoClient(api_key="x", base_url="https://t.example")
        client.create_webhook_endpoint("https://x/", name="primary")

        body = mock_request.call_args[1]["json"]
        assert body["name"] == "primary"
        assert body["callback_url"] == "https://x/"

    def test_create_endpoint_without_name_raises(self, mock_request: Mock) -> None:
        # 1.0.0 turned the 0.7.0 DeprecationWarning into a hard error: the
        # server enforces unique(user, name), so omitting name would 400
        # anyway. Raising client-side gives a better error message and
        # avoids the wasted round-trip.
        mock_request.return_value = _mock_response({})
        client = TangoClient(api_key="x", base_url="https://t.example")
        with pytest.raises(TangoValidationError, match="name"):
            client.create_webhook_endpoint("https://x/")
        # And the request never went out.
        mock_request.assert_not_called()

    def test_update_endpoint_passes_name(self, mock_request: Mock) -> None:
        mock_request.return_value = _mock_response(
            {
                "id": "ep-1",
                "name": "renamed",
                "callback_url": "https://x/",
                "is_active": True,
                "created_at": "2026-01-01",
                "updated_at": "2026-01-01",
            }
        )
        client = TangoClient(api_key="x", base_url="https://t.example")
        client.update_webhook_endpoint("ep-1", name="renamed")
        body = mock_request.call_args[1]["json"]
        assert body == {"name": "renamed"}


@patch("tango.client.httpx.Client.request")
class TestWebhookAlertEndpointKwarg:
    def test_create_alert_passes_endpoint(self, mock_request: Mock) -> None:
        mock_request.return_value = _mock_response(
            {
                "alert_id": "alert-1",
                "name": "ep-pinned",
                "query_type": "opportunity",
                "filters": {"naics": "541511"},
                "frequency": "realtime",
                "cron_expression": None,
                "status": "active",
                "created_at": "2026-01-01",
                "last_checked_at": None,
                "match_count": 0,
            }
        )
        client = TangoClient(api_key="x", base_url="https://t.example")
        client.create_webhook_alert(
            name="ep-pinned",
            query_type="opportunity",
            filters={"naics": "541511"},
            endpoint="ep-1",
        )
        body = mock_request.call_args[1]["json"]
        assert body["endpoint"] == "ep-1"
        assert body["name"] == "ep-pinned"


@patch("tango.client.httpx.Client.request")
class TestOrderingParam:
    """Verify ordering kwarg lands in query params on the five list_* methods
    that the server actually accepts ordering on (notices/protests rejected
    every value at runtime, so no kwarg is exposed for them)."""

    @pytest.mark.parametrize(
        "method,path,extra_kwargs",
        [
            ("list_forecasts", "/api/forecasts/", {}),
            ("list_grants", "/api/grants/", {}),
            ("list_subawards", "/api/subawards/", {}),
            ("list_gsa_elibrary_contracts", "/api/gsa_elibrary_contracts/", {}),
            ("list_opportunities", "/api/opportunities/", {}),
        ],
    )
    def test_ordering_threads_through(
        self,
        mock_request: Mock,
        method: str,
        path: str,
        extra_kwargs: dict[str, Any],
    ) -> None:
        mock_request.return_value = _mock_response(
            {"count": 0, "next": None, "previous": None, "results": []}
        )
        client = TangoClient(api_key="x", base_url="https://t.example")
        fn = getattr(client, method)
        fn(ordering="-foo", **extra_kwargs)

        call = mock_request.call_args
        params = call[1]["params"]
        assert params["ordering"] == "-foo", (
            f"{method}: expected ordering='-foo' in query, got {params}"
        )
        assert call[1]["url"].endswith(path)


@patch("tango.client.httpx.Client.request")
class TestReferenceData:
    def test_list_departments(self, mock_request: Mock) -> None:
        mock_request.return_value = _mock_response(
            {"count": 1, "next": None, "previous": None, "results": [{"code": "97"}]}
        )
        client = TangoClient(api_key="x", base_url="https://t.example")
        out = client.list_departments(limit=2)
        assert out.results == [{"code": "97"}]
        assert mock_request.call_args[1]["url"].endswith("/api/departments/")

    def test_get_department(self, mock_request: Mock) -> None:
        mock_request.return_value = _mock_response({"code": "97", "name": "DoD"})
        client = TangoClient(api_key="x", base_url="https://t.example")
        out = client.get_department("97")
        assert out["code"] == "97"
        assert mock_request.call_args[1]["url"].endswith("/api/departments/97/")

    def test_get_psc_metrics(self, mock_request: Mock) -> None:
        mock_request.return_value = _mock_response({"metrics": []})
        client = TangoClient(api_key="x", base_url="https://t.example")
        client.get_psc_metrics("R425", 12, "month")
        assert mock_request.call_args[1]["url"].endswith("/api/psc/R425/metrics/12/month/")

    def test_get_naics(self, mock_request: Mock) -> None:
        mock_request.return_value = _mock_response({"code": "541511"})
        client = TangoClient(api_key="x", base_url="https://t.example")
        out = client.get_naics("541511")
        assert out["code"] == "541511"

    def test_list_mas_sins_with_search(self, mock_request: Mock) -> None:
        mock_request.return_value = _mock_response(
            {"count": 0, "next": None, "previous": None, "results": []}
        )
        client = TangoClient(api_key="x", base_url="https://t.example")
        client.list_mas_sins(search="cyber")
        assert mock_request.call_args[1]["params"]["search"] == "cyber"


@patch("tango.client.httpx.Client.request")
class TestEntitySubResources:
    def test_list_entity_contracts(self, mock_request: Mock) -> None:
        mock_request.return_value = _mock_response(
            {"count": 0, "next": None, "previous": None, "results": []}
        )
        client = TangoClient(api_key="x", base_url="https://t.example")
        client.list_entity_contracts("UEI123", limit=10, ordering="-award_date", naics="541511")
        call = mock_request.call_args
        assert call[1]["url"].endswith("/api/entities/UEI123/contracts/")
        params = call[1]["params"]
        assert params["ordering"] == "-award_date"
        assert params["naics"] == "541511"
        assert params["limit"] == 10

    def test_get_entity_metrics(self, mock_request: Mock) -> None:
        mock_request.return_value = _mock_response({"obligations": []})
        client = TangoClient(api_key="x", base_url="https://t.example")
        client.get_entity_metrics("UEI1", 24, "quarter")
        assert mock_request.call_args[1]["url"].endswith("/api/entities/UEI1/metrics/24/quarter/")

    def test_list_entity_lcats(self, mock_request: Mock) -> None:
        mock_request.return_value = _mock_response(
            {"count": 0, "next": None, "previous": None, "results": []}
        )
        client = TangoClient(api_key="x", base_url="https://t.example")
        client.list_entity_lcats("UEI1", search="engineer")
        assert mock_request.call_args[1]["params"]["search"] == "engineer"

    def test_uei_required(self, mock_request: Mock) -> None:
        client = TangoClient(api_key="x", base_url="https://t.example")
        with pytest.raises(TangoValidationError):
            client.list_entity_contracts("")


@patch("tango.client.httpx.Client.request")
class TestAgencyContracts:
    def test_list_agency_awarding_contracts(self, mock_request: Mock) -> None:
        mock_request.return_value = _mock_response(
            {"count": 0, "next": None, "previous": None, "results": []}
        )
        client = TangoClient(api_key="x", base_url="https://t.example")
        client.list_agency_awarding_contracts("4732", limit=5)
        assert mock_request.call_args[1]["url"].endswith("/api/agencies/4732/contracts/awarding/")

    def test_list_agency_funding_contracts(self, mock_request: Mock) -> None:
        mock_request.return_value = _mock_response(
            {"count": 0, "next": None, "previous": None, "results": []}
        )
        client = TangoClient(api_key="x", base_url="https://t.example")
        client.list_agency_funding_contracts("4732", limit=5)
        assert mock_request.call_args[1]["url"].endswith("/api/agencies/4732/contracts/funding/")


@patch("tango.client.httpx.Client.request")
class TestMiscMethods:
    def test_get_version(self, mock_request: Mock) -> None:
        mock_request.return_value = _mock_response({"version": "4.5.0"})
        client = TangoClient(api_key="x", base_url="https://t.example")
        out = client.get_version()
        assert out["version"] == "4.5.0"

    def test_list_api_keys(self, mock_request: Mock) -> None:
        mock_request.return_value = _mock_response({"keys": []})
        client = TangoClient(api_key="x", base_url="https://t.example")
        client.list_api_keys()
        assert mock_request.call_args[1]["url"].endswith("/api/api-keys/")

    def test_search_opportunity_attachments(self, mock_request: Mock) -> None:
        mock_request.return_value = _mock_response({"matches": []})
        client = TangoClient(api_key="x", base_url="https://t.example")
        client.search_opportunity_attachments(q="cyber", top_k=5, include_extracted_text=True)
        params = mock_request.call_args[1]["params"]
        assert params["q"] == "cyber"
        assert params["top_k"] == 5
        assert params["include_extracted_text"] == "true"

    def test_list_idv_lcats(self, mock_request: Mock) -> None:
        mock_request.return_value = _mock_response(
            {"count": 0, "next": None, "previous": None, "results": []}
        )
        client = TangoClient(api_key="x", base_url="https://t.example")
        client.list_idv_lcats("IDV-1")
        assert mock_request.call_args[1]["url"].endswith("/api/idvs/IDV-1/lcats/")
