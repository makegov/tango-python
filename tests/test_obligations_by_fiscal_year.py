"""The `obligations_by_fiscal_year(...)` expand on contracts, IDVs, OTAs and OT IDVs."""

from decimal import Decimal
from unittest.mock import Mock, patch

import pytest

from tango import TangoClient
from tango.models import IDV, OTA, OTIDV, Contract, Notice, Opportunity
from tango.shapes.parser import ShapeParser

SHAPE = "key,obligations_by_fiscal_year(fiscal_year,obligated)"


def _mock(mock_request, payload):
    response = Mock()
    response.is_success = True
    response.json.return_value = payload
    response.content = b"{}"
    mock_request.return_value = response


def _page(rows):
    return {"count": len(rows), "next": None, "previous": None, "results": rows}


class TestObligationsByFiscalYearShape:
    @pytest.mark.parametrize("model", [Contract, IDV, OTA, OTIDV])
    @pytest.mark.parametrize(
        "shape",
        [
            SHAPE,
            "key,obligations_by_fiscal_year(*)",
            "key,obligations_by_fiscal_year",
        ],
    )
    def test_shape_validates(self, model, shape):
        parser = ShapeParser(cache_enabled=False)
        parser.validate(parser.parse(shape), model)

    @pytest.mark.parametrize("model", [Contract, OTA])
    def test_unknown_sub_field_is_rejected(self, model):
        parser = ShapeParser(cache_enabled=False)
        with pytest.raises(Exception, match="amount"):
            parser.validate(parser.parse("key,obligations_by_fiscal_year(amount)"), model)


class TestObligationsByFiscalYearResponses:
    @pytest.mark.parametrize("method", ["list_contracts", "list_otas"])
    @patch("tango.client.httpx.Client.request")
    def test_list_parses_each_year(self, mock_request, method):
        _mock(
            mock_request,
            _page(
                [
                    {
                        "key": "K1",
                        "obligations_by_fiscal_year": [
                            {"fiscal_year": 2023, "obligated": 1000.0},
                            {"fiscal_year": 2024, "obligated": -250.5},
                        ],
                    }
                ]
            ),
        )

        (row,) = getattr(TangoClient(api_key="k"), method)(shape=SHAPE).results

        years = row["obligations_by_fiscal_year"]
        assert [y["fiscal_year"] for y in years] == [2023, 2024]
        assert [y["obligated"] for y in years] == [Decimal("1000.0"), Decimal("-250.5")]
        assert all(isinstance(y["obligated"], Decimal) for y in years)

    @pytest.mark.parametrize("method", ["list_idvs", "list_otidvs"])
    @patch("tango.client.httpx.Client.request")
    def test_cumulative_award_types_return_none(self, mock_request, method):
        _mock(mock_request, _page([{"key": "K1", "obligations_by_fiscal_year": None}]))

        (row,) = getattr(TangoClient(api_key="k"), method)(shape=SHAPE).results

        assert row["obligations_by_fiscal_year"] is None


class TestAttachmentExtractionStatusShape:
    @pytest.mark.parametrize("model", [Opportunity, Notice])
    def test_shape_validates(self, model):
        parser = ShapeParser(cache_enabled=False)
        parser.validate(parser.parse("title,attachments(name,extraction_status)"), model)
