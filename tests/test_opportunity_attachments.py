"""The `attachments(...)` expand on opportunities and notices, including the Pro-plan document-role fields, and the attachment, file and link counts."""

from unittest.mock import Mock, patch

import pytest

from tango import TangoClient
from tango.models import Notice, Opportunity, Vehicle
from tango.shapes import SchemaRegistry
from tango.shapes.parser import ShapeParser

ROLE_SHAPE = "title,attachments(name,doc_role,doc_role_alt)"
OPPORTUNITY_COUNT_SHAPE = "opportunity_id,meta(attachments_count,files_count,links_count)"
NOTICE_COUNT_SHAPE = "notice_id,attachment_count,file_count,link_count"


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


class TestAttachmentCountShapes:
    @pytest.mark.parametrize(
        ("shape", "model"),
        [
            (OPPORTUNITY_COUNT_SHAPE, Opportunity),
            (NOTICE_COUNT_SHAPE, Notice),
            ("uuid,opportunity(opportunity_id,meta(files_count,links_count))", Vehicle),
        ],
    )
    def test_count_shape_validates(self, shape, model):
        parser = ShapeParser(cache_enabled=False)
        parser.validate(parser.parse(shape), model)

    @pytest.mark.parametrize(
        ("model", "path"),
        [
            (Opportunity, ("meta", "files_count")),
            (Opportunity, ("meta", "links_count")),
            (Notice, ("file_count",)),
            (Notice, ("link_count",)),
        ],
    )
    def test_count_is_typed_as_nullable_int(self, model, path):
        registry = SchemaRegistry()
        schema = registry.get_schema(model)
        for name in path[:-1]:
            schema = registry.get_schema(schema[name].nested_model)
        field = schema[path[-1]]
        assert (field.type, field.is_optional, field.is_list) == (int, True, False)


class TestAttachmentCounts:
    @patch("tango.client.httpx.Client.request")
    def test_get_opportunity_returns_file_and_link_counts(self, mock_request):
        _mock(
            mock_request,
            {
                "opportunity_id": "abc",
                "meta": {"attachments_count": 6, "files_count": 3, "links_count": 2},
            },
        )
        row = TangoClient(api_key="k").get_opportunity("abc", shape=OPPORTUNITY_COUNT_SHAPE)
        assert mock_request.call_args.kwargs["params"]["shape"] == OPPORTUNITY_COUNT_SHAPE
        assert row["meta"] == {"attachments_count": 6, "files_count": 3, "links_count": 2}

    @patch("tango.client.httpx.Client.request")
    def test_get_opportunity_keeps_uncounted_as_none(self, mock_request):
        _mock(
            mock_request,
            {
                "opportunity_id": "abc",
                "meta": {"attachments_count": 4, "files_count": None, "links_count": None},
            },
        )
        row = TangoClient(api_key="k").get_opportunity("abc", shape=OPPORTUNITY_COUNT_SHAPE)
        assert row["meta"]["attachments_count"] == 4
        assert row["meta"]["files_count"] is None
        assert row["meta"]["links_count"] is None

    @patch("tango.client.httpx.Client.request")
    def test_list_notices_returns_file_and_link_counts(self, mock_request):
        _mock(
            mock_request,
            {
                "count": 2,
                "next": None,
                "previous": None,
                "results": [
                    {"notice_id": "n1", "attachment_count": 6, "file_count": 3, "link_count": 2},
                    {
                        "notice_id": "n2",
                        "attachment_count": 1,
                        "file_count": None,
                        "link_count": None,
                    },
                ],
            },
        )
        page = TangoClient(api_key="k").list_notices(shape=NOTICE_COUNT_SHAPE)
        assert mock_request.call_args.kwargs["params"]["shape"] == NOTICE_COUNT_SHAPE
        counted, uncounted = page.results
        assert (counted["attachment_count"], counted["file_count"], counted["link_count"]) == (
            6,
            3,
            2,
        )
        assert uncounted["attachment_count"] == 1
        assert uncounted["file_count"] is None
        assert uncounted["link_count"] is None
