"""Tests for the GSA eBuy requests endpoints.

Covers the request contract for the four methods (paths, filters passed through under the API's own param names, the documented default shapes, the attachment redirect read without following it) plus the shape schema that backs them. Requests are mocked.
"""

from datetime import datetime
from typing import Any
from unittest.mock import Mock, patch

import pytest

from tango import EbuyAccess, TangoClient
from tango.exceptions import (
    ShapeValidationError,
    TangoAPIError,
    TangoAttachmentLinkError,
    TangoNotFoundError,
    TangoValidationError,
)
from tango.models import EbuyRequest, ShapeConfig
from tango.shapes.parser import ShapeParser

RFQ_ID = "RFQ1835158"
SIGNED_URL = "https://documents.example.com/rfq/solicitation.pdf?signature=abc"


def _response(
    status: int = 200,
    payload: Any = None,
    headers: dict[str, str] | None = None,
) -> Mock:
    response = Mock()
    response.status_code = status
    response.is_success = 200 <= status < 300
    response.is_redirect = status in (301, 302, 303, 307, 308)
    response.headers = headers or {}
    response.json.return_value = payload if payload is not None else {}
    response.content = b"{}" if payload is not None else b""
    return response


def _mock(mock_request, payload=None):
    body = (
        payload
        if payload is not None
        else {"count": 0, "next": None, "previous": None, "results": []}
    )
    mock_request.return_value = _response(200, body)
    return mock_request.return_value


def _call_params(mock_request) -> dict:
    return mock_request.call_args.kwargs.get("params") or {}


def _call_url(mock_request) -> str:
    args = mock_request.call_args.args
    return str(args[1]) if len(args) > 1 else str(mock_request.call_args.kwargs.get("url", ""))


def _row(**overrides) -> dict:
    row = {
        "rfq_id": RFQ_ID,
        "request_type": "RFQ",
        "title": "Cybersecurity assessment support",
        "schedule": "MAS",
        "sin": "54151HACS",
        "status": "Open",
        "buyer_name": "Jane Buyer",
        "buyer_agency": "General Services Administration",
        "buyer_agency_code": None,
        "reference_number": "W912DY-26-Q-0012",
        "issue_date": "2026-09-01T14:30:00Z",
        "close_date": "2026-09-30T21:00:00Z",
        "attachment_count": 2,
        "link_count": 1,
        "last_seen": "2026-09-27T06:00:00Z",
    }
    row.update(overrides)
    return row


class TestListEbuyRequests:
    @patch("tango.client.httpx.Client.request")
    def test_list_path_and_filters(self, mock_request):
        _mock(mock_request)
        TangoClient(api_key="k").list_ebuy_requests(
            search="cybersecurity assessment",
            rfq_id="RFQ1835158|RFQ1835159",
            reference_number="W912DY26Q0012",
            request_type="RFQ|RFP",
            status="Open",
            sin="54151HACS",
            schedule="MAS",
            buyer_agency="General Services Administration",
            agency="GSA",
            contract_number="EXAMPLE-0001",
            issue_date_after="2026-01-01",
            issue_date_before="2026-06-30",
            close_date_after="2026-07-01",
            close_date_before="2026-12-31",
            ordering="-close_date",
            limit=10,
        )

        assert "/api/ebuy/requests/" in _call_url(mock_request)
        assert _call_params(mock_request) == {
            "page": 1,
            "limit": 10,
            "shape": ShapeConfig.EBUY_REQUESTS_MINIMAL,
            "search": "cybersecurity assessment",
            "rfq_id": "RFQ1835158|RFQ1835159",
            "reference_number": "W912DY26Q0012",
            "request_type": "RFQ|RFP",
            "status": "Open",
            "sin": "54151HACS",
            "schedule": "MAS",
            "buyer_agency": "General Services Administration",
            "agency": "GSA",
            "contract_number": "EXAMPLE-0001",
            "issue_date_after": "2026-01-01",
            "issue_date_before": "2026-06-30",
            "close_date_after": "2026-07-01",
            "close_date_before": "2026-12-31",
            "ordering": "-close_date",
        }

    @patch("tango.client.httpx.Client.request")
    def test_no_filters_are_synthesized(self, mock_request):
        _mock(mock_request)
        TangoClient(api_key="k").list_ebuy_requests()
        assert set(_call_params(mock_request)) == {"page", "limit", "shape"}

    @patch("tango.client.httpx.Client.request")
    def test_limit_is_capped_at_the_api_maximum(self, mock_request):
        _mock(mock_request)
        TangoClient(api_key="k").list_ebuy_requests(limit=500)
        assert _call_params(mock_request)["limit"] == 100

    @patch("tango.client.httpx.Client.request")
    def test_results_are_parsed(self, mock_request):
        _mock(mock_request, {"count": 1, "next": None, "previous": None, "results": [_row()]})
        page = TangoClient(api_key="k").list_ebuy_requests()

        assert page.count == 1
        row = page.results[0]
        assert row["rfq_id"] == RFQ_ID
        assert isinstance(row["issue_date"], datetime)
        assert (row["issue_date"].year, row["issue_date"].month, row["issue_date"].day) == (
            2026,
            9,
            1,
        )
        assert row["attachment_count"] == 2
        assert row["buyer_agency_code"] is None


class TestGetEbuyRequest:
    @patch("tango.client.httpx.Client.request")
    def test_get_uses_rfq_id_route_and_comprehensive_shape(self, mock_request):
        _mock(mock_request, _row())
        TangoClient(api_key="k").get_ebuy_request(RFQ_ID)

        assert f"/api/ebuy/requests/{RFQ_ID}/" in _call_url(mock_request)
        assert _call_params(mock_request)["shape"] == ShapeConfig.EBUY_REQUESTS_COMPREHENSIVE

    @patch("tango.client.httpx.Client.request")
    def test_detail_fields_and_expands_parse(self, mock_request):
        _mock(
            mock_request,
            _row(
                description="Assess the agency's boundary controls.",
                follow_on=False,
                mod_version=3,
                line_items=[{"description": "Assessment"}],
                organization={
                    "organization_id": "0f6c1d9e-5b7a-4c2e-9a41-3e8d2b7c6a10",
                    "department_code": "047",
                    "department_name": "General Services Administration",
                    "agency_code": "4732",
                    "agency_name": "Federal Acquisition Service",
                    "office_code": None,
                    "office_name": None,
                },
                attachments=[
                    {
                        "doc_seq_num": 1,
                        "doc_name": "solicitation.pdf",
                        "doc_type": 1,
                        "doc_path": "solicitation.pdf",
                        "is_link": False,
                        "doc_session_date": "2026-09-01T14:31:00Z",
                    },
                    {
                        "doc_seq_num": 2,
                        "doc_name": "Q&A portal",
                        "doc_type": 3,
                        "doc_path": "https://example.gov/qa",
                        "is_link": True,
                        "doc_session_date": None,
                    },
                ],
            ),
        )
        row = TangoClient(api_key="k").get_ebuy_request(RFQ_ID)

        assert row["follow_on"] is False
        assert row["mod_version"] == 3
        assert row["line_items"] == [{"description": "Assessment"}]
        assert row["organization"]["agency_code"] == "4732"
        assert [a["doc_seq_num"] for a in row["attachments"]] == [1, 2]
        assert row["attachments"][1]["is_link"] is True
        assert isinstance(row["attachments"][0]["doc_session_date"], datetime)

    @patch("tango.client.httpx.Client.request")
    def test_out_of_scope_request_is_not_found(self, mock_request):
        mock_request.return_value = _response(404, {"detail": "No EbuyRequest matches."})
        with pytest.raises(TangoNotFoundError):
            TangoClient(api_key="k").get_ebuy_request("RFQ0000000")


class TestGetEbuyAttachmentUrl:
    @patch("tango.client.httpx.Client.request")
    def test_returns_redirect_target_without_following_it(self, mock_request):
        mock_request.return_value = _response(302, headers={"Location": SIGNED_URL})

        url = TangoClient(api_key="k").get_ebuy_attachment_url(RFQ_ID, 1)

        assert url == SIGNED_URL
        assert mock_request.call_args.kwargs["follow_redirects"] is False
        assert _call_url(mock_request).endswith(
            f"/api/ebuy/requests/{RFQ_ID}/attachments/1/download/"
        )

    @patch("tango.client.httpx.Client.request")
    def test_link_entry_surfaces_the_url(self, mock_request):
        mock_request.return_value = _response(
            400,
            {
                "detail": "This entry is an external link, not a stored document.",
                "url": "https://example.gov/qa",
            },
        )

        with pytest.raises(TangoAttachmentLinkError) as excinfo:
            TangoClient(api_key="k").get_ebuy_attachment_url(RFQ_ID, 2)

        assert isinstance(excinfo.value, TangoValidationError)
        assert excinfo.value.url == "https://example.gov/qa"
        assert "https://example.gov/qa" in str(excinfo.value)

    @patch("tango.client.httpx.Client.request")
    def test_uncaptured_document_is_not_found_with_detail(self, mock_request):
        mock_request.return_value = _response(
            404, {"detail": "The document for this attachment has not been captured yet."}
        )

        with pytest.raises(TangoNotFoundError, match="not been captured yet"):
            TangoClient(api_key="k").get_ebuy_attachment_url(RFQ_ID, 1)

    @patch("tango.client.httpx.Client.request")
    def test_below_tier_raises_api_error(self, mock_request):
        mock_request.return_value = _response(403, {"detail": "Upgrade required."})

        with pytest.raises(TangoAPIError) as excinfo:
            TangoClient(api_key="k").get_ebuy_attachment_url(RFQ_ID, 1)

        assert excinfo.value.status_code == 403

    @patch("tango.client.httpx.Client.request")
    def test_success_without_redirect_is_an_error(self, mock_request):
        mock_request.return_value = _response(200, {})

        with pytest.raises(TangoAPIError, match="Expected a redirect"):
            TangoClient(api_key="k").get_ebuy_attachment_url(RFQ_ID, 1)


class TestGetEbuyAccess:
    @patch("tango.client.httpx.Client.request")
    def test_enabled(self, mock_request):
        mock_request.return_value = _response(
            200, {"enabled": True, "reason": None, "contracts": ["EXAMPLE-0001", "EXAMPLE-0002"]}
        )

        access = TangoClient(api_key="k").get_ebuy_access()

        assert "/api/ebuy/access/" in _call_url(mock_request)
        assert access == EbuyAccess(
            enabled=True, reason=None, contracts=["EXAMPLE-0001", "EXAMPLE-0002"]
        )

    @patch("tango.client.httpx.Client.request")
    def test_no_grant(self, mock_request):
        mock_request.return_value = _response(
            200, {"enabled": False, "reason": "no_contract_grant", "contracts": []}
        )

        access = TangoClient(api_key="k").get_ebuy_access()

        assert access.enabled is False
        assert access.reason == "no_contract_grant"
        assert access.contracts == []


class TestEbuyShapes:
    @pytest.mark.parametrize(
        "shape",
        [
            ShapeConfig.EBUY_REQUESTS_MINIMAL,
            ShapeConfig.EBUY_REQUESTS_COMPREHENSIVE,
            "rfq_id,organization(agency_code,office_name),attachments(doc_seq_num,is_link)",
            "rfq_id,amendments,line_items,addresses,oco_aac,ocs_phone",
        ],
    )
    def test_shape_validates(self, shape):
        parser = ShapeParser(cache_enabled=True)
        parser.validate(parser.parse(shape), EbuyRequest)

    def test_contract_number_is_a_filter_not_a_response_field(self):
        parser = ShapeParser(cache_enabled=True)
        with pytest.raises(ShapeValidationError):
            parser.validate(parser.parse("rfq_id,contract_number"), EbuyRequest)
