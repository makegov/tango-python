"""Tests for the Federal Register documents endpoint.

Covers the request contract for both methods (path, filters passed through under the API's own param names, the documented default shape) plus the shape schema that backs them. Requests are mocked.
"""

from datetime import date
from unittest.mock import Mock, patch

import pytest

from tango import TangoClient
from tango.exceptions import ShapeValidationError
from tango.models import FederalRegisterDocument, ShapeConfig
from tango.shapes.parser import ShapeParser

DOC_UUID = "7cf9c379-3d17-5059-a1e5-930ffd421a85"


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
        "uuid": DOC_UUID,
        "document_number": "2026-19694",
        "publication_date": "2026-09-25",
        "type": "Rule",
        "subtype": None,
        "title": "Annual Notices on Explosive Materials Storage Facilities",
        "abstract": "The Department amends its regulations.",
        "action": "Final rule.",
        "agencies": [
            {"id": 268, "name": "Justice Department", "slug": "justice-department"},
        ],
        "cfr_references": [{"part": "555", "title": 27, "chapter": None, "citation_url": None}],
        "citation": "91 FR 51234",
        "significant": True,
        "comments_close_on": None,
        "effective_on": "2026-10-26",
        "html_url": "https://www.federalregister.gov/d/2026-19694",
        "pdf_url": "https://www.govinfo.gov/content/pkg/FR-2026-09-25/pdf/2026-19694.pdf",
    }
    row.update(overrides)
    return row


class TestListFederalRegisterDocuments:
    @patch("tango.client.httpx.Client.request")
    def test_list_path_and_filters(self, mock_request):
        _mock(mock_request)
        TangoClient(api_key="k").list_federal_register_documents(
            search='"greenhouse gas"',
            document_number="2016-31922|2016-31923",
            type="Proposed Rule",
            agency="EPA",
            fr_agency="environmental-protection-agency",
            publication_date_after="2025-01-01",
            publication_date_before="2026-01-01",
            effective_on_after="2025-02-01",
            effective_on_before="2026-02-01",
            comments_close_on_after="2025-03-01",
            comments_close_on_before="2026-03-01",
            comments_open=True,
            cfr_title="40",
            cfr_part="52",
            significant=True,
            rin="2060-AV16",
            executive_order_number="14028",
            ordering="-effective_on",
            limit=10,
        )

        params = _call_params(mock_request)
        assert "/api/federal_register/" in _call_url(mock_request)
        assert params == {
            "page": 1,
            "limit": 10,
            "shape": ShapeConfig.FEDERAL_REGISTER_MINIMAL,
            "search": '"greenhouse gas"',
            "document_number": "2016-31922|2016-31923",
            "type": "Proposed Rule",
            "agency": "EPA",
            "fr_agency": "environmental-protection-agency",
            "publication_date_after": "2025-01-01",
            "publication_date_before": "2026-01-01",
            "effective_on_after": "2025-02-01",
            "effective_on_before": "2026-02-01",
            "comments_close_on_after": "2025-03-01",
            "comments_close_on_before": "2026-03-01",
            "comments_open": True,
            "cfr_title": "40",
            "cfr_part": "52",
            "significant": True,
            "rin": "2060-AV16",
            "executive_order_number": "14028",
            "ordering": "-effective_on",
        }

    @patch("tango.client.httpx.Client.request")
    def test_no_filters_are_synthesized(self, mock_request):
        _mock(mock_request)
        TangoClient(api_key="k").list_federal_register_documents()
        assert set(_call_params(mock_request)) == {"page", "limit", "shape"}

    @patch("tango.client.httpx.Client.request")
    def test_false_booleans_are_sent_not_dropped(self, mock_request):
        """`comments_open=False` is the closed set, not "no filter"."""
        _mock(mock_request)
        TangoClient(api_key="k").list_federal_register_documents(
            comments_open=False, significant=False
        )
        params = _call_params(mock_request)
        assert params["comments_open"] is False
        assert params["significant"] is False

    @patch("tango.client.httpx.Client.request")
    def test_limit_is_capped_at_the_api_maximum(self, mock_request):
        _mock(mock_request)
        TangoClient(api_key="k").list_federal_register_documents(limit=500)
        assert _call_params(mock_request)["limit"] == 100

    @patch("tango.client.httpx.Client.request")
    def test_results_are_parsed(self, mock_request):
        _mock(
            mock_request,
            {"count": 1, "next": None, "previous": None, "results": [_row()]},
        )
        page = TangoClient(api_key="k").list_federal_register_documents()

        assert page.count == 1
        row = page.results[0]
        assert row["document_number"] == "2026-19694"
        assert row["publication_date"] == date(2026, 9, 25)
        assert row["effective_on"] == date(2026, 10, 26)
        assert row["significant"] is True
        assert row["agencies"][0]["slug"] == "justice-department"
        assert row["cfr_references"][0]["title"] == 27


class TestGetFederalRegisterDocument:
    @patch("tango.client.httpx.Client.request")
    def test_get_uses_uuid_route_and_comprehensive_shape(self, mock_request):
        _mock(mock_request, _row())
        TangoClient(api_key="k").get_federal_register_document(DOC_UUID)

        assert f"/api/federal_register/{DOC_UUID}/" in _call_url(mock_request)
        assert _call_params(mock_request)["shape"] == ShapeConfig.FEDERAL_REGISTER_COMPREHENSIVE

    @patch("tango.client.httpx.Client.request")
    def test_detail_fields_parse(self, mock_request):
        _mock(
            mock_request,
            _row(
                dates="This rule is effective October 26, 2026.",
                signing_date="2026-09-19",
                start_page=51234,
                end_page=51252,
                volume=91,
                docket_ids=["Docket No. ATF-2023-0001"],
                dockets=[{"id": "ATF_FRDOC_0001", "documents": []}],
                regulation_id_numbers=["1140-AA51"],
                topics=["Explosives", "Safety"],
                correction_of=None,
                corrections=[],
            ),
        )
        row = TangoClient(api_key="k").get_federal_register_document(DOC_UUID)

        assert row["signing_date"] == date(2026, 9, 19)
        assert row["start_page"] == 51234
        assert row["volume"] == 91
        assert row["regulation_id_numbers"] == ["1140-AA51"]
        assert row["topics"] == ["Explosives", "Safety"]
        assert row["dockets"][0]["id"] == "ATF_FRDOC_0001"

    @patch("tango.client.httpx.Client.request")
    def test_full_text_parses_when_requested(self, mock_request):
        _mock(mock_request, {"uuid": DOC_UUID, "full_text": "SUMMARY: The Department..."})
        row = TangoClient(api_key="k").get_federal_register_document(
            DOC_UUID, shape="uuid,full_text"
        )
        assert _call_params(mock_request)["shape"] == "uuid,full_text"
        assert row["full_text"] == "SUMMARY: The Department..."

    def test_no_default_shape_names_full_text(self):
        for shape in (
            ShapeConfig.FEDERAL_REGISTER_MINIMAL,
            ShapeConfig.FEDERAL_REGISTER_COMPREHENSIVE,
        ):
            assert "full_text" not in shape


class TestFederalRegisterShapes:
    @pytest.mark.parametrize(
        "shape",
        [
            ShapeConfig.FEDERAL_REGISTER_MINIMAL,
            ShapeConfig.FEDERAL_REGISTER_COMPREHENSIVE,
            "uuid,full_text",
            "uuid,regulation_id_number_info,regulations_dot_gov_info,public_inspection_pdf_url",
            "uuid,toc_doc,toc_subject,page_length,disposition_notes,executive_order_notes",
        ],
    )
    def test_shape_validates(self, shape):
        parser = ShapeParser(cache_enabled=True)
        parser.validate(parser.parse(shape), FederalRegisterDocument)

    def test_filter_only_params_are_not_response_fields(self):
        """`rin`, `fr_agency` and `search` are filters; the response carries `regulation_id_numbers` and `agencies` instead."""
        parser = ShapeParser(cache_enabled=True)
        for field in ("rin", "fr_agency", "search"):
            with pytest.raises(ShapeValidationError):
                parser.validate(parser.parse(f"uuid,{field}"), FederalRegisterDocument)
