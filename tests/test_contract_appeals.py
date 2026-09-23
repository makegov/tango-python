"""Tests for the Contract Disputes Act appeals endpoint.

Covers the request contract for both methods — correct path, filters passed
through under the API's own param names, the documented default shape — plus the
shape schema that backs them and how a row parses at either tier. Requests are
mocked; live behavior is exercised by the production smoke tests.
"""

from datetime import date, datetime
from unittest.mock import Mock, patch

import pytest

from tango import TangoClient
from tango.exceptions import ShapeValidationError
from tango.models import ContractAppeal, ShapeConfig
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


def _row(**overrides) -> dict:
    row = {
        "uuid": "2f1b5a2e-77b8-4f5d-9a3c-0c3d5f1e8b21",
        "board": "asbca",
        "docket_numbers": ["59116"],
        "decision_date": "2026-03-04",
        "appellant": "Tidewater Construction Corp.",
        "judge": "Melnick",
        "decision_type": None,
        "url": "https://www.asbca.mil/Decisions/2026/59116.pdf",
    }
    row.update(overrides)
    return row


class TestListContractAppeals:
    @patch("tango.client.httpx.Client.request")
    def test_list_path_and_filters(self, mock_request):
        _mock(mock_request)
        TangoClient(api_key="k").list_contract_appeals(
            board="cbca|asbca",
            docket="ASBCA No. 59116",
            appellant="construction",
            judge="Melnick",
            decision_type="Dismissal",
            decision_date_after="2025-01-01",
            decision_date_before="2026-01-01",
            document_id="CBCA-7092",
            search="differing site conditions",
            ordering="-decision_date",
            limit=10,
        )

        params = _call_params(mock_request)
        assert "/api/contract_appeals/" in _call_url(mock_request)
        assert params["board"] == "cbca|asbca"
        assert params["docket"] == "ASBCA No. 59116"
        assert params["appellant"] == "construction"
        assert params["judge"] == "Melnick"
        assert params["decision_type"] == "Dismissal"
        assert params["decision_date_after"] == "2025-01-01"
        assert params["decision_date_before"] == "2026-01-01"
        assert params["document_id"] == "CBCA-7092"
        assert params["search"] == "differing site conditions"
        assert params["ordering"] == "-decision_date"
        assert params["limit"] == 10
        assert params["shape"] == ShapeConfig.CONTRACT_APPEALS_MINIMAL

    @patch("tango.client.httpx.Client.request")
    def test_no_filters_are_synthesized(self, mock_request):
        """Every default here is the API's, so an unasked-for filter must not be sent."""
        _mock(mock_request)
        TangoClient(api_key="k").list_contract_appeals()
        params = _call_params(mock_request)
        assert set(params) == {"page", "limit", "shape"}

    @patch("tango.client.httpx.Client.request")
    def test_listed_false_is_sent_not_dropped(self, mock_request):
        """`listed=False` selects the decisions the newest listing dropped, so it is a real value."""
        _mock(mock_request)
        TangoClient(api_key="k").list_contract_appeals(listed=False)
        assert _call_params(mock_request)["listed"] is False

    @patch("tango.client.httpx.Client.request")
    def test_limit_is_capped_at_the_api_maximum(self, mock_request):
        _mock(mock_request)
        TangoClient(api_key="k").list_contract_appeals(limit=500)
        assert _call_params(mock_request)["limit"] == 100

    @patch("tango.client.httpx.Client.request")
    def test_results_are_parsed(self, mock_request):
        _mock(
            mock_request,
            {"count": 1, "next": None, "previous": None, "results": [_row()]},
        )
        page = TangoClient(api_key="k").list_contract_appeals()

        assert page.count == 1
        row = page.results[0]
        assert row["board"] == "asbca"
        assert row["docket_numbers"] == ["59116"]
        assert row["decision_date"] == date(2026, 3, 4)
        assert row["appellant"] == "Tidewater Construction Corp."


class TestGetContractAppeal:
    @patch("tango.client.httpx.Client.request")
    def test_get_uses_uuid_route_and_comprehensive_shape(self, mock_request):
        _mock(mock_request, _row())
        TangoClient(api_key="k").get_contract_appeal("2f1b5a2e-77b8-4f5d-9a3c-0c3d5f1e8b21")

        assert "/api/contract_appeals/2f1b5a2e-77b8-4f5d-9a3c-0c3d5f1e8b21/" in _call_url(
            mock_request
        )
        assert _call_params(mock_request)["shape"] == ShapeConfig.CONTRACT_APPEALS_COMPREHENSIVE

    @patch("tango.client.httpx.Client.request")
    def test_listing_fields_parse_on_the_detail_shape(self, mock_request):
        _mock(
            mock_request,
            _row(
                docket_raw="ASBCA Nos. 59116, 59117",
                docket_source="listing",
                decision_date_repaired=False,
                decision_type_raw=None,
                listing_year=2026,
                first_listed_at="2026-03-05T11:30:00Z",
                listed=True,
                text_status="completed",
                text_char_count=48213,
            ),
        )
        row = TangoClient(api_key="k").get_contract_appeal("2f1b5a2e-77b8-4f5d-9a3c-0c3d5f1e8b21")

        assert row["docket_source"] == "listing"
        assert row["listing_year"] == 2026
        assert row["listed"] is True
        assert row["text_char_count"] == 48213
        assert row["first_listed_at"] == datetime.fromisoformat("2026-03-05T11:30:00+00:00")


class TestContractAppealDecisionText:
    """`decision_text` is Enterprise-only, and below that tier the key is absent, not null."""

    @patch("tango.client.httpx.Client.request")
    def test_row_parses_when_the_body_is_served(self, mock_request):
        _mock(mock_request, _row(decision_text="The appeal is sustained."))
        row = TangoClient(api_key="k").get_contract_appeal(
            "2f1b5a2e-77b8-4f5d-9a3c-0c3d5f1e8b21",
            shape="uuid,board,appellant,decision_text",
        )
        assert row["decision_text"] == "The appeal is sustained."

    @patch("tango.client.httpx.Client.request")
    def test_row_parses_when_the_body_is_withheld(self, mock_request):
        _mock(mock_request, _row())
        row = TangoClient(api_key="k").get_contract_appeal(
            "2f1b5a2e-77b8-4f5d-9a3c-0c3d5f1e8b21",
            shape="uuid,board,appellant,decision_text",
        )
        assert row.get("decision_text") is None
        assert row["appellant"] == "Tidewater Construction Corp."

    def test_no_default_shape_names_the_paid_body(self):
        for shape in (
            ShapeConfig.CONTRACT_APPEALS_MINIMAL,
            ShapeConfig.CONTRACT_APPEALS_COMPREHENSIVE,
        ):
            assert "decision_text" not in shape


class TestContractAppealShapes:
    @pytest.mark.parametrize(
        "shape",
        [
            ShapeConfig.CONTRACT_APPEALS_MINIMAL,
            ShapeConfig.CONTRACT_APPEALS_COMPREHENSIVE,
            "uuid,decision_text",
            "uuid,docket_numbers,docket_raw,docket_source,listing_url",
        ],
    )
    def test_shape_validates(self, shape):
        parser = ShapeParser(cache_enabled=True)
        parser.validate(parser.parse(shape), ContractAppeal)

    def test_filter_only_params_are_not_response_fields(self):
        """`docket` and `search` are filters; the response carries `docket_numbers` instead."""
        parser = ShapeParser(cache_enabled=True)
        for field in ("docket", "search"):
            with pytest.raises(ShapeValidationError):
                parser.validate(parser.parse(f"uuid,{field}"), ContractAppeal)
