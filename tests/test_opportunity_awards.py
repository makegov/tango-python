"""Award fields on opportunities and notices, the `awards(...)` expand, and the `awarded` / `awardee_uei` filters."""

from datetime import date
from unittest.mock import Mock, patch

import pytest

from tango import TangoClient
from tango.models import Notice, Opportunity
from tango.shapes.parser import ShapeParser

AWARD_LEAVES = "award_date,award_amount,awardee,awardee_uei"
OPPORTUNITY_AWARD_SHAPE = (
    f"opportunity_id,awarded,{AWARD_LEAVES},award_count,solicitation_opportunity_id,awards(*)"
)


def _mock(mock_request, payload):
    response = Mock()
    response.is_success = True
    response.json.return_value = payload
    response.content = b"{}"
    mock_request.return_value = response


def _page(results):
    return {"count": len(results), "next": None, "previous": None, "results": results}


class TestAwardShapes:
    @pytest.mark.parametrize(
        "shape",
        [
            OPPORTUNITY_AWARD_SHAPE,
            "opportunity_id,awards(opportunity_id,notice_id,award_number,award_date,award_amount,awardee,awardee_uei)",
        ],
    )
    def test_opportunity_award_shape_validates(self, shape):
        parser = ShapeParser(cache_enabled=False)
        parser.validate(parser.parse(shape), Opportunity)

    def test_notice_award_shape_validates(self):
        parser = ShapeParser(cache_enabled=False)
        parser.validate(parser.parse(f"notice_id,award_number,{AWARD_LEAVES}"), Notice)


class TestAwardResponses:
    @patch("tango.client.httpx.Client.request")
    def test_get_opportunity_parses_award_fields_and_linked_awards(self, mock_request):
        _mock(
            mock_request,
            {
                "opportunity_id": "solicitation-1",
                "awarded": True,
                "award_date": None,
                "award_amount": None,
                "awardee": None,
                "awardee_uei": None,
                "award_count": 12,
                "solicitation_opportunity_id": None,
                "awards": [
                    {
                        "opportunity_id": "award-1",
                        "notice_id": "notice-1",
                        "award_number": "W912-26-C-0001",
                        "award_date": "2026-08-14",
                        "award_amount": "$1,250,000.00",
                        "awardee": "Example Corp",
                        "awardee_uei": "ABCDEF123456",
                    }
                ],
            },
        )
        row = TangoClient(api_key="k").get_opportunity(
            "solicitation-1", shape=OPPORTUNITY_AWARD_SHAPE
        )
        assert row["awarded"] is True
        assert row["award_count"] == 12
        assert row["awards"][0]["award_number"] == "W912-26-C-0001"
        assert row["awards"][0]["award_amount"] == "$1,250,000.00"
        assert row["awards"][0]["awardee_uei"] == "ABCDEF123456"

    @patch("tango.client.httpx.Client.request")
    def test_list_notices_returns_award_fields(self, mock_request):
        shape = f"notice_id,{AWARD_LEAVES}"
        _mock(
            mock_request,
            _page(
                [
                    {
                        "notice_id": "notice-1",
                        "award_date": "2026-08-14",
                        "award_amount": "1250000",
                        "awardee": "Example Corp",
                        "awardee_uei": "ABCDEF123456",
                    }
                ]
            ),
        )
        page = TangoClient(api_key="k").list_notices(shape=shape)
        assert page.results[0]["award_date"] == date(2026, 8, 14)
        assert page.results[0]["award_amount"] == "1250000"


class TestAwardFilters:
    @patch("tango.client.httpx.Client.request")
    def test_list_opportunities_sends_award_filters(self, mock_request):
        _mock(mock_request, _page([]))
        TangoClient(api_key="k").list_opportunities(
            awarded=True, awardee_uei="ABCDEF123456|abcdef654321"
        )
        params = mock_request.call_args.kwargs["params"]
        assert params["awarded"] is True
        assert params["awardee_uei"] == "ABCDEF123456|abcdef654321"

    @patch("tango.client.httpx.Client.request")
    def test_list_opportunities_sends_awarded_false(self, mock_request):
        _mock(mock_request, _page([]))
        TangoClient(api_key="k").list_opportunities(awarded=False)
        params = mock_request.call_args.kwargs["params"]
        assert params["awarded"] is False
        assert "awardee_uei" not in params
