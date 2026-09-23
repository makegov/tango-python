"""The `attachments(...)` expand on opportunities and notices, including the Pro-plan document-role fields."""

from unittest.mock import Mock, patch

import pytest

from tango import TangoClient
from tango.models import Notice, Opportunity
from tango.shapes.parser import ShapeParser

ROLE_SHAPE = "title,attachments(name,doc_role,doc_role_alt)"


def _mock(mock_request, payload):
    response = Mock()
    response.is_success = True
    response.json.return_value = payload
    response.content = b"{}"
    mock_request.return_value = response


def _attachments():
    return [
        {"name": "sow.pdf", "doc_role": "requirement", "doc_role_alt": None},
        {"name": "pricing.xlsx", "doc_role": "pricing", "doc_role_alt": "terms"},
        {"name": "unclassified.docx"},
    ]


class TestAttachmentShapes:
    @pytest.mark.parametrize("model", [Opportunity, Notice])
    @pytest.mark.parametrize(
        "shape",
        [
            ROLE_SHAPE,
            "title,attachments(name,url,extracted_text)",
            "title,attachments(*)",
        ],
    )
    def test_attachment_shape_validates(self, model, shape):
        parser = ShapeParser(cache_enabled=False)
        parser.validate(parser.parse(shape), model)


class TestAttachmentRoles:
    @pytest.mark.parametrize("method", ["get_opportunity", "get_notice"])
    @patch("tango.client.httpx.Client.request")
    def test_detail_returns_document_roles(self, mock_request, method):
        _mock(mock_request, {"title": "Base ops support", "attachments": _attachments()})
        row = getattr(TangoClient(api_key="k"), method)("abc", shape=ROLE_SHAPE)
        assert [a.get("doc_role") for a in row["attachments"]] == ["requirement", "pricing", None]
        assert row["attachments"][1]["doc_role_alt"] == "terms"

    @pytest.mark.parametrize("method", ["list_opportunities", "list_notices"])
    @patch("tango.client.httpx.Client.request")
    def test_list_returns_document_roles(self, mock_request, method):
        _mock(
            mock_request,
            {
                "count": 1,
                "next": None,
                "previous": None,
                "results": [{"title": "Amendment 1", "attachments": _attachments()}],
            },
        )
        page = getattr(TangoClient(api_key="k"), method)(shape=ROLE_SHAPE)
        assert mock_request.call_args.kwargs["params"]["shape"] == ROLE_SHAPE
        assert [a.get("doc_role") for a in page.results[0]["attachments"]] == [
            "requirement",
            "pricing",
            None,
        ]
