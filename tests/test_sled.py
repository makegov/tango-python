"""Tests for the state, local and education (SLED) endpoint family.

Covers the request contract for each method — correct path, filters passed
through under the API's own param names, the documented default shape — plus the
shape schemas that back them. Requests are mocked; live behavior is exercised by
the production smoke tests.
"""

from datetime import UTC, datetime
from unittest.mock import Mock, patch

import pytest

from tango import TangoClient
from tango.models import (
    ShapeConfig,
    SledForecast,
    SledOpportunity,
    SledOpportunityRevision,
)
from tango.shapes.parser import ShapeParser


def _mock(mock_request, payload=None):
    response = Mock()
    response.is_success = True
    body = (
        payload
        if payload is not None
        else {"count": 0, "next": None, "previous": None, "results": []}
    )
    response.json.return_value = body
    response.content = b"{}"
    mock_request.return_value = response
    return response


def _call_params(mock_request) -> dict:
    return mock_request.call_args.kwargs.get("params") or {}


def _call_url(mock_request) -> str:
    args = mock_request.call_args.args
    return str(args[1]) if len(args) > 1 else str(mock_request.call_args.kwargs.get("url", ""))


class TestSledOpportunities:
    @patch("tango.client.httpx.Client.request")
    def test_list_path_and_filters(self, mock_request):
        _mock(mock_request)
        TangoClient(api_key="k").list_sled_opportunities(
            state="TX|OK",
            jurisdiction="local|education",
            status="open|unknown",
            has_documents=True,
            response_deadline_before="2026-10-01",
            limit=10,
        )

        params = _call_params(mock_request)
        assert "/api/sled/opportunities/" in _call_url(mock_request)
        assert params["state"] == "TX|OK"
        assert params["jurisdiction"] == "local|education"
        assert params["status"] == "open|unknown"
        assert params["has_documents"] is True
        assert params["response_deadline_before"] == "2026-10-01"
        assert params["limit"] == 10
        assert params["shape"] == ShapeConfig.SLED_OPPORTUNITIES_MINIMAL

    @patch("tango.client.httpx.Client.request")
    def test_no_liveness_filter_is_sent_when_none_requested(self, mock_request):
        """The open-only default is the API's, not the SDK's.

        The SDK must not synthesize `status=open` — a caller who wants the whole
        corpus passes an explicit `status`, and a caller who passes nothing is
        relying on the server-side default. Sending one here would make
        `active=False` unreachable.
        """
        _mock(mock_request)
        TangoClient(api_key="k").list_sled_opportunities()
        params = _call_params(mock_request)
        assert "status" not in params
        assert "active" not in params

    @patch("tango.client.httpx.Client.request")
    def test_active_false_is_sent_not_dropped(self, mock_request):
        """`active=False` is a real filter value, not an absent one."""
        _mock(mock_request)
        TangoClient(api_key="k").list_sled_opportunities(active=False)
        assert _call_params(mock_request)["active"] is False

    @patch("tango.client.httpx.Client.request")
    def test_source_status_is_not_a_filter(self, mock_request):
        """`status` is Tango-derived liveness; the portal's own word is served but not filterable."""
        _mock(mock_request)
        TangoClient(api_key="k").list_sled_opportunities(status="closed")
        params = _call_params(mock_request)
        assert params["status"] == "closed"
        assert "source_status" not in params

    @patch("tango.client.httpx.Client.request")
    def test_category_filters_are_distinct_params(self, mock_request):
        _mock(mock_request)
        TangoClient(api_key="k").list_sled_opportunities(
            naics="541620", nigp="962-47", unspsc="77101500", category_code="541620"
        )
        params = _call_params(mock_request)
        assert params["naics"] == "541620"
        assert params["nigp"] == "962-47"
        assert params["unspsc"] == "77101500"
        assert params["category_code"] == "541620"

    @patch("tango.client.httpx.Client.request")
    def test_get_uses_opportunity_id_route_and_comprehensive_shape(self, mock_request):
        _mock(mock_request, {"opportunity_id": "abc"})
        TangoClient(api_key="k").get_sled_opportunity("abc")
        assert "/api/sled/opportunities/abc/" in _call_url(mock_request)
        assert _call_params(mock_request)["shape"] == ShapeConfig.SLED_OPPORTUNITIES_COMPREHENSIVE

    @patch("tango.client.httpx.Client.request")
    def test_results_are_parsed(self, mock_request):
        _mock(
            mock_request,
            {
                "count": 1,
                "next": None,
                "previous": None,
                "results": [
                    {
                        "opportunity_id": "u1",
                        "title": "Environmental mitigation services",
                        "state": "TX",
                        "status": "open",
                    }
                ],
            },
        )
        page = TangoClient(api_key="k").list_sled_opportunities()
        assert page.count == 1
        assert page.results[0]["state"] == "TX"

    @patch("tango.client.httpx.Client.request")
    def test_delisted_at_is_requested_by_default_and_served(self, mock_request):
        _mock(
            mock_request,
            {
                "count": 1,
                "next": None,
                "previous": None,
                "results": [
                    {
                        "opportunity_id": "u1",
                        "status": "closed",
                        "status_reason": "delisted",
                        "delisted_at": "2026-09-10T06:00:00Z",
                    }
                ],
            },
        )
        page = TangoClient(api_key="k").list_sled_opportunities()
        assert "delisted_at" in _call_params(mock_request)["shape"].split(",")
        assert page.results[0]["delisted_at"] == datetime(2026, 9, 10, 6, 0, tzinfo=UTC)

    @patch("tango.client.httpx.Client.request")
    def test_detail_fields_keep_the_api_types(self, mock_request):
        _mock(
            mock_request,
            {
                "opportunity_id": "u1",
                "posted_date": "2026-09-01T14:30:00Z",
                "response_deadline": "2026-10-01T17:00:00Z",
                "category_codes": [{"scheme": "nigp", "code": "91000"}],
                "meta": {"jurisdiction_declared": False, "last_change_source_declared": True},
                "attachments": [{"name": "rfp.pdf", "size_bytes": 1024, "pages": 3}],
            },
        )
        row = TangoClient(api_key="k").get_sled_opportunity(
            "u1",
            shape=(
                "opportunity_id,posted_date,response_deadline,category_codes,"
                "meta(jurisdiction_declared,last_change_source_declared),"
                "attachments(name,size_bytes,pages)"
            ),
        )
        assert row["posted_date"] == datetime(2026, 9, 1, 14, 30, tzinfo=UTC)
        assert row["response_deadline"] == datetime(2026, 10, 1, 17, 0, tzinfo=UTC)
        assert row["category_codes"] == [{"scheme": "nigp", "code": "91000"}]
        assert row["meta"]["jurisdiction_declared"] is False
        assert row["attachments"][0]["size_bytes"] == 1024


class TestSledRevisions:
    @patch("tango.client.httpx.Client.request")
    def test_nested_route_and_filters(self, mock_request):
        _mock(mock_request)
        TangoClient(api_key="k").list_sled_opportunity_revisions(
            "abc", kind="deadline_change", source_declared=True
        )
        params = _call_params(mock_request)
        assert "/api/sled/opportunities/abc/revisions/" in _call_url(mock_request)
        assert params["kind"] == "deadline_change"
        assert params["source_declared"] is True
        assert params["shape"] == ShapeConfig.SLED_REVISIONS_MINIMAL

    def test_default_shape_omits_the_plan_gated_changes_leaf(self):
        """`changes` needs a Small plan, so naming it by default would 403 a Free caller."""
        assert "changed_fields" in ShapeConfig.SLED_REVISIONS_MINIMAL
        assert "changes," not in ShapeConfig.SLED_REVISIONS_MINIMAL
        assert not ShapeConfig.SLED_REVISIONS_MINIMAL.endswith("changes")

    @patch("tango.client.httpx.Client.request")
    def test_enrichment_is_reachable_here(self, mock_request):
        """The expand excludes enrichment rows; this route is how a caller reaches them."""
        _mock(mock_request)
        TangoClient(api_key="k").list_sled_opportunity_revisions("abc", kind="enrichment")
        assert _call_params(mock_request)["kind"] == "enrichment"


class TestSledCoverage:
    @patch("tango.client.httpx.Client.request")
    def test_coverage_route_takes_no_params(self, mock_request):
        _mock(
            mock_request,
            {
                "generated_at": "2026-09-10T14:00:00Z",
                "totals": {"opportunities": 3, "forecasts": 1},
                "states": [{"state": "TX", "total_count": 3}],
            },
        )
        payload = TangoClient(api_key="k").get_sled_coverage()
        assert "/api/sled/opportunities/coverage/" in _call_url(mock_request)
        assert _call_params(mock_request) == {}
        assert payload["totals"]["opportunities"] == 3
        assert payload["states"][0]["state"] == "TX"


class TestSledForecasts:
    @patch("tango.client.httpx.Client.request")
    def test_list_path_and_filters(self, mock_request):
        _mock(mock_request)
        TangoClient(api_key="k").list_sled_forecasts(
            state="MD",
            procurement_method="Competitive Sealed Proposals",
            advertisement_after="2026-10-01",
        )
        params = _call_params(mock_request)
        assert "/api/sled/forecasts/" in _call_url(mock_request)
        assert params["state"] == "MD"
        assert params["procurement_method"] == "Competitive Sealed Proposals"
        assert params["advertisement_after"] == "2026-10-01"
        assert params["shape"] == ShapeConfig.SLED_FORECASTS_MINIMAL

    def test_forecasts_carry_no_liveness_filter(self):
        """A forecast has no deadline, so `status` / `active` must not be offered."""
        import inspect

        sig = inspect.signature(TangoClient.list_sled_forecasts)
        assert "status" not in sig.parameters
        assert "active" not in sig.parameters

    @patch("tango.client.httpx.Client.request")
    def test_get_uses_forecast_id_route(self, mock_request):
        _mock(mock_request, {"forecast_id": "f1"})
        TangoClient(api_key="k").get_sled_forecast("f1")
        assert "/api/sled/forecasts/f1/" in _call_url(mock_request)


class TestSledShapes:
    """The default shapes must validate against the generated schemas."""

    @pytest.mark.parametrize(
        ("shape", "model"),
        [
            (ShapeConfig.SLED_OPPORTUNITIES_MINIMAL, SledOpportunity),
            (ShapeConfig.SLED_OPPORTUNITIES_COMPREHENSIVE, SledOpportunity),
            (ShapeConfig.SLED_REVISIONS_MINIMAL, SledOpportunityRevision),
            (ShapeConfig.SLED_FORECASTS_MINIMAL, SledForecast),
            (ShapeConfig.SLED_FORECASTS_COMPREHENSIVE, SledForecast),
        ],
    )
    def test_default_shape_validates(self, shape, model):
        parser = ShapeParser(cache_enabled=True)
        parser.validate(parser.parse(shape), model)

    @pytest.mark.parametrize(
        ("shape", "model"),
        [
            (
                "opportunity_id,organization(state,level,agency),meta(attachment_count,revision_count)",
                SledOpportunity,
            ),
            (
                "opportunity_id,attachments(name,size_bytes,char_count,extraction_status,is_generated_summary)",
                SledOpportunity,
            ),
            (
                "opportunity_id,revisions(observed_at,kind,changed_fields,changes)",
                SledOpportunity,
            ),
            ("opportunity_id,title,snippet", SledOpportunity),
            ("forecast_id,estimated_value(min,max,raw),contact(name,email)", SledForecast),
        ],
    )
    def test_nested_expands_validate(self, shape, model):
        parser = ShapeParser(cache_enabled=True)
        parser.validate(parser.parse(shape), model)

    def test_the_document_body_validates_when_named(self):
        """`extracted_text` needs a Small plan, but the SDK must not reject it client-side."""
        parser = ShapeParser(cache_enabled=True)
        parser.validate(
            parser.parse("opportunity_id,attachments(name,size_bytes,extracted_text)"),
            SledOpportunity,
        )

    @pytest.mark.parametrize(
        "shape",
        [
            "opportunity_id,status,status_reason,delisted_at",
            "opportunity_id,meta(jurisdiction_declared,last_change_source_declared)",
        ],
    )
    def test_fields_added_after_launch_validate(self, shape):
        parser = ShapeParser(cache_enabled=True)
        parser.validate(parser.parse(shape), SledOpportunity)

    def test_no_default_shape_names_the_paid_document_body(self):
        """The API resolves the body only when named, so a default shape that named it would make every detail fetch pay for it."""
        for shape in (
            ShapeConfig.SLED_OPPORTUNITIES_MINIMAL,
            ShapeConfig.SLED_OPPORTUNITIES_COMPREHENSIVE,
        ):
            assert "extracted_text" not in shape

    def test_support_filters_are_not_response_fields(self):
        """`external_id`, `native_id` and `platform` are filters only — never shaped."""
        from tango.exceptions import ShapeValidationError

        parser = ShapeParser(cache_enabled=True)
        for field in ("external_id", "native_id", "platform"):
            with pytest.raises(ShapeValidationError):
                parser.validate(parser.parse(f"opportunity_id,{field}"), SledOpportunity)
