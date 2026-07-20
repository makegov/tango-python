"""Tests for the DIBBS, exclusions, and SBIR/STTR endpoint families.

Covers the request contract for each new method — correct path, filters passed
through under the API's own param names, the documented default shape — plus the
shape schemas that back them. Requests are mocked; live behavior is exercised by
the production smoke tests.
"""

from unittest.mock import Mock, patch

import pytest

from tango import TangoClient
from tango.models import (
    DibbsAward,
    DibbsRfp,
    DibbsRfq,
    Exclusion,
    SbirSolicitation,
    SbirTopic,
    ShapeConfig,
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
    """The query params the client actually sent."""
    return mock_request.call_args.kwargs.get("params") or {}


def _call_url(mock_request) -> str:
    args = mock_request.call_args.args
    return str(args[1]) if len(args) > 1 else str(mock_request.call_args.kwargs.get("url", ""))


class TestDibbs:
    @patch("tango.client.httpx.Client.request")
    def test_list_dibbs_rfqs_path_and_filters(self, mock_request):
        _mock(mock_request)
        client = TangoClient(api_key="k")
        client.list_dibbs_rfqs(nsn="5310-00-000-0000", open=True, quantity_min=5, limit=10)

        params = _call_params(mock_request)
        assert "/api/dibbs/rfqs/" in _call_url(mock_request)
        assert params["nsn"] == "5310-00-000-0000"
        # `open` is the filter; `is_open` is query-time derived and not filterable
        assert params["open"] is True
        assert "is_open" not in params
        assert params["quantity_min"] == 5
        assert params["shape"] == ShapeConfig.DIBBS_RFQS_MINIMAL

    @patch("tango.client.httpx.Client.request")
    def test_get_dibbs_rfq_uses_uuid_route(self, mock_request):
        _mock(mock_request, {"uuid": "abc"})
        TangoClient(api_key="k").get_dibbs_rfq("abc")
        assert "/api/dibbs/rfqs/abc/" in _call_url(mock_request)

    @patch("tango.client.httpx.Client.request")
    def test_list_dibbs_rfps_filters(self, mock_request):
        _mock(mock_request)
        TangoClient(api_key="k").list_dibbs_rfps(buyer_code="ABC", closes_date_after="2026-01-01")
        params = _call_params(mock_request)
        assert "/api/dibbs/rfps/" in _call_url(mock_request)
        assert params["buyer_code"] == "ABC"
        assert params["closes_date_after"] == "2026-01-01"

    @patch("tango.client.httpx.Client.request")
    def test_list_dibbs_awards_price_bounds(self, mock_request):
        _mock(mock_request)
        TangoClient(api_key="k").list_dibbs_awards(
            total_contract_price_min=100, total_contract_price_max=5000, awardee_cage="1ABC2"
        )
        params = _call_params(mock_request)
        assert "/api/dibbs/awards/" in _call_url(mock_request)
        assert params["total_contract_price_min"] == 100
        assert params["total_contract_price_max"] == 5000
        assert params["awardee_cage"] == "1ABC2"

    @patch("tango.client.httpx.Client.request")
    def test_dibbs_award_results_are_parsed(self, mock_request):
        _mock(
            mock_request,
            {
                "count": 1,
                "next": None,
                "previous": None,
                "results": [
                    {"uuid": "u1", "award_number": "SPE123", "total_contract_price": "42.00"}
                ],
            },
        )
        page = TangoClient(api_key="k").list_dibbs_awards()
        assert page.count == 1
        assert len(page.results) == 1


class TestExclusions:
    @patch("tango.client.httpx.Client.request")
    def test_list_exclusions_filters(self, mock_request):
        _mock(mock_request)
        TangoClient(api_key="k").list_exclusions(
            uei="ABC123", active=True, classification_type="Firm"
        )
        params = _call_params(mock_request)
        assert "/api/exclusions/" in _call_url(mock_request)
        assert params["uei"] == "ABC123"
        # `active` is the filter; is_currently_excluded is query-time derived
        assert params["active"] is True
        assert "is_currently_excluded" not in params
        assert params["classification_type"] == "Firm"

    @patch("tango.client.httpx.Client.request")
    def test_get_exclusion_uses_exclusion_key_route(self, mock_request):
        _mock(mock_request, {"exclusion_key": "k1"})
        TangoClient(api_key="k").get_exclusion("k1")
        assert "/api/exclusions/k1/" in _call_url(mock_request)


class TestSbir:
    @patch("tango.client.httpx.Client.request")
    def test_list_sbir_topics_filters(self, mock_request):
        _mock(mock_request)
        TangoClient(api_key="k").list_sbir_topics(agency="DOD", year=2026, topic_number="A26-001")
        params = _call_params(mock_request)
        assert "/api/sbir/topics/" in _call_url(mock_request)
        assert params["agency"] == "DOD"
        assert params["year"] == 2026
        assert params["topic_number"] == "A26-001"

    @patch("tango.client.httpx.Client.request")
    def test_get_sbir_topic_uses_topic_id_route(self, mock_request):
        _mock(mock_request, {"topic_id": "t1"})
        TangoClient(api_key="k").get_sbir_topic("t1")
        assert "/api/sbir/topics/t1/" in _call_url(mock_request)

    @patch("tango.client.httpx.Client.request")
    def test_list_sbir_solicitations_filters(self, mock_request):
        _mock(mock_request)
        TangoClient(api_key="k").list_sbir_solicitations(program="SBIR", out_of_cycle=False)
        params = _call_params(mock_request)
        assert "/api/sbir/solicitations/" in _call_url(mock_request)
        assert params["program"] == "SBIR"
        assert params["out_of_cycle"] is False

    @patch("tango.client.httpx.Client.request")
    def test_get_sbir_solicitation_uses_solicitation_id_route(self, mock_request):
        _mock(mock_request, {"solicitation_id": "s1"})
        TangoClient(api_key="k").get_sbir_solicitation("s1")
        assert "/api/sbir/solicitations/s1/" in _call_url(mock_request)


class TestNewFamilyShapes:
    """The default shapes must validate against the generated schemas."""

    @pytest.mark.parametrize(
        ("shape", "model"),
        [
            (ShapeConfig.DIBBS_RFQS_MINIMAL, DibbsRfq),
            (ShapeConfig.DIBBS_RFPS_MINIMAL, DibbsRfp),
            (ShapeConfig.DIBBS_AWARDS_MINIMAL, DibbsAward),
            (ShapeConfig.EXCLUSIONS_MINIMAL, Exclusion),
            (ShapeConfig.SBIR_TOPICS_MINIMAL, SbirTopic),
            (ShapeConfig.SBIR_SOLICITATIONS_MINIMAL, SbirSolicitation),
        ],
    )
    def test_default_shape_validates(self, shape, model):
        parser = ShapeParser(cache_enabled=True)
        parser.validate(parser.parse(shape), model)

    @pytest.mark.parametrize(
        ("shape", "model"),
        [
            # nested expands the API exposes on these families
            ("uuid,organization(agency_code,office_name)", DibbsRfq),
            ("uuid,awardee(uei,legal_business_name),organization(agency_name)", DibbsAward),
            ("topic_id,solicitation(solicitation_number,program),opportunity(title)", SbirTopic),
            ("solicitation_id,topics(topic_id,title),documents(filename)", SbirSolicitation),
        ],
    )
    def test_nested_expands_validate(self, shape, model):
        parser = ShapeParser(cache_enabled=True)
        parser.validate(parser.parse(shape), model)

    def test_unknown_field_still_rejected(self):
        from tango.exceptions import ShapeValidationError

        parser = ShapeParser(cache_enabled=True)
        with pytest.raises(ShapeValidationError):
            parser.validate(parser.parse("uuid,definitely_not_a_field"), DibbsRfq)
