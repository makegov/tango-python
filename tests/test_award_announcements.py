"""Tests for the award announcements endpoint.

Covers the request contract for both methods (path, filters passed through under the API's own param names, the documented default shape) plus the shape schema that backs them. Requests are mocked.
"""

import json
from datetime import date
from decimal import Decimal
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from tango import AwardAnnouncement, ShapeConfig, TangoClient
from tango.exceptions import ShapeValidationError
from tango.shapes.parser import ShapeParser

ANNOUNCEMENT_UUID = "7d1e3a5c-2b4f-5a6e-8c0d-9f1b3d5e7a9c"
CONTRACT_PATH = Path(__file__).resolve().parents[1] / "contracts" / "filter_shape_contract.json"


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
        "uuid": ANNOUNCEMENT_UUID,
        "source": "official_release",
        "source_name": "Department of War contracts release",
        "source_url": "https://www.war.gov/News/Contracts/Contract/Article/1234567/",
        "published_date": "2026-10-22",
        "award_date": "2026-10-21",
        "title": "Example Systems Corp., Arlington, Virginia",
        "amount": "125000000.00",
        "value_kind": "ceiling",
        "action_type": "new_award",
        "announcement_type": None,
        "awardee_count": 1,
        "piids": ["N0001925C0070"],
        "is_modification": False,
        "is_multiple_award": False,
        "is_withdrawn": False,
    }
    row.update(overrides)
    return row


class TestListAwardAnnouncements:
    @patch("tango.client.httpx.Client.request")
    def test_list_path_and_filters(self, mock_request):
        _mock(mock_request)
        TangoClient(api_key="k").list_award_announcements(
            search='"hypersonic"',
            source="official_release",
            agency="Navy",
            component="NAVY|ARMY",
            published_date_after="2026-09-01",
            published_date_before="2026-10-01",
            award_date_after="2026-08-01",
            award_date_before="2026-09-30",
            amount_min=100000000,
            amount_max="500000000",
            piid="N00019-25-C-0070",
            awardee="lockheed",
            uei="ABC123DEF456",
            action_type="new_award",
            announcement_type="new_vehicle",
            civilian=True,
            small_business=True,
            is_modification=True,
            is_multiple_award=True,
            include_withdrawn=True,
            ordering="-amount",
            limit=10,
        )

        assert "/api/news/award_announcements/" in _call_url(mock_request)
        assert _call_params(mock_request) == {
            "page": 1,
            "limit": 10,
            "shape": ShapeConfig.AWARD_ANNOUNCEMENTS_MINIMAL,
            "search": '"hypersonic"',
            "source": "official_release",
            "agency": "Navy",
            "component": "NAVY|ARMY",
            "published_date_after": "2026-09-01",
            "published_date_before": "2026-10-01",
            "award_date_after": "2026-08-01",
            "award_date_before": "2026-09-30",
            "amount_min": 100000000,
            "amount_max": "500000000",
            "piid": "N00019-25-C-0070",
            "awardee": "lockheed",
            "uei": "ABC123DEF456",
            "action_type": "new_award",
            "announcement_type": "new_vehicle",
            "civilian": True,
            "small_business": True,
            "is_modification": True,
            "is_multiple_award": True,
            "include_withdrawn": True,
            "ordering": "-amount",
        }

    @patch("tango.client.httpx.Client.request")
    def test_no_filters_are_synthesized(self, mock_request):
        _mock(mock_request)
        TangoClient(api_key="k").list_award_announcements()
        assert set(_call_params(mock_request)) == {"page", "limit", "shape"}

    @patch("tango.client.httpx.Client.request")
    def test_false_booleans_are_sent_not_dropped(self, mock_request):
        """`small_business=False` keeps awardees stated not to be small, which is not "no filter"."""
        _mock(mock_request)
        TangoClient(api_key="k").list_award_announcements(
            small_business=False, civilian=False, amount_min=0
        )
        params = _call_params(mock_request)
        assert params["small_business"] is False
        assert params["civilian"] is False
        assert params["amount_min"] == 0

    @patch("tango.client.httpx.Client.request")
    def test_limit_is_capped_at_the_api_maximum(self, mock_request):
        _mock(mock_request)
        TangoClient(api_key="k").list_award_announcements(limit=500)
        assert _call_params(mock_request)["limit"] == 100

    @patch("tango.client.httpx.Client.request")
    def test_results_are_parsed(self, mock_request):
        _mock(
            mock_request,
            {"count": 1, "next": None, "previous": None, "results": [_row()]},
        )
        page = TangoClient(api_key="k").list_award_announcements()

        assert page.count == 1
        row = page.results[0]
        assert row["source"] == "official_release"
        assert row["published_date"] == date(2026, 10, 22)
        assert row["amount"] == Decimal("125000000.00")
        assert row["piids"] == ["N0001925C0070"]
        assert row["is_withdrawn"] is False


class TestGetAwardAnnouncement:
    @patch("tango.client.httpx.Client.request")
    def test_get_uses_uuid_route_and_comprehensive_shape(self, mock_request):
        _mock(mock_request, _row())
        TangoClient(api_key="k").get_award_announcement(ANNOUNCEMENT_UUID)

        assert f"/api/news/award_announcements/{ANNOUNCEMENT_UUID}/" in _call_url(mock_request)
        assert _call_params(mock_request)["shape"] == ShapeConfig.AWARD_ANNOUNCEMENTS_COMPREHENSIVE

    @patch("tango.client.httpx.Client.request")
    def test_detail_fields_and_expands_parse(self, mock_request):
        _mock(
            mock_request,
            _row(
                source_record_id="4321:7",
                text="Example Systems Corp., Arlington, Virginia, was awarded...",
                obligated_at_award="1500000.00",
                award_kind="contract",
                award_uuids=["0066dc77-13ad-5a1c-9da1-d718e290969b"],
                civilian=False,
                component="NAVY",
                contracting_activity="Naval Air Systems Command",
                corrections=[
                    {
                        "publish_date": "2026-10-23",
                        "text": "The contract announced Oct. 22 was for...",
                        "changes": [
                            {
                                "field": "announced_value",
                                "previous": "120000000",
                                "corrected": "125000000",
                            }
                        ],
                    }
                ],
                awardees=[
                    {
                        "name": "Example Systems Corp.",
                        "uei": None,
                        "location": "Arlington, Virginia",
                        "small_business": True,
                    }
                ],
                organization={
                    "organization_id": "9f1b3d5e-7a9c-4d1e-8c0d-2b4f5a6e7d1e",
                    "office_code": "N00019",
                    "office_name": "NAVAL AIR SYSTEMS COMMAND",
                    "agency_code": "1700",
                    "agency_name": "DEPT OF THE NAVY",
                    "department_code": "9700",
                    "department_name": "DEPT OF DEFENSE",
                },
            ),
        )
        row = TangoClient(api_key="k").get_award_announcement(ANNOUNCEMENT_UUID)

        assert row["obligated_at_award"] == Decimal("1500000.00")
        assert row["award_uuids"] == ["0066dc77-13ad-5a1c-9da1-d718e290969b"]
        assert row["component"] == "NAVY"
        assert row["corrections"][0]["changes"][0]["corrected"] == "125000000"
        assert row["awardees"][0]["name"] == "Example Systems Corp."
        assert row["awardees"][0]["small_business"] is True
        assert row["awardees"][0]["uei"] is None
        assert row["organization"]["agency_name"] == "DEPT OF THE NAVY"

    @patch("tango.client.httpx.Client.request")
    def test_awardees_subselection_parses(self, mock_request):
        _mock(mock_request, {"uuid": ANNOUNCEMENT_UUID, "awardees": [{"name": "Example"}]})
        row = TangoClient(api_key="k").get_award_announcement(
            ANNOUNCEMENT_UUID, shape="uuid,awardees(name)"
        )
        assert _call_params(mock_request)["shape"] == "uuid,awardees(name)"
        assert row["awardees"][0]["name"] == "Example"

    def test_list_default_leaves_out_text(self):
        assert "text" not in ShapeConfig.AWARD_ANNOUNCEMENTS_MINIMAL.split(",")
        assert "text" in ShapeConfig.AWARD_ANNOUNCEMENTS_COMPREHENSIVE.split(",")


class TestAwardAnnouncementShapes:
    @pytest.mark.parametrize(
        "shape",
        [
            ShapeConfig.AWARD_ANNOUNCEMENTS_MINIMAL,
            ShapeConfig.AWARD_ANNOUNCEMENTS_COMPREHENSIVE,
            "uuid,awardees(name,uei,location,small_business)",
            "uuid,organization(organization_id,office_code,office_name,agency_code,agency_name,department_code,department_name)",
        ],
    )
    def test_shape_validates(self, shape):
        parser = ShapeParser(cache_enabled=True)
        parser.validate(parser.parse(shape), AwardAnnouncement)

    def test_every_field_in_the_vendored_contract_validates(self):
        contract = json.loads(CONTRACT_PATH.read_text())
        shape = contract["resources"]["news/award_announcements"]["runtime"]["shape"]
        assert "piids" in shape["fields"]

        parser = ShapeParser(cache_enabled=True)
        parser.validate(parser.parse(",".join(shape["fields"])), AwardAnnouncement)

    @pytest.mark.parametrize("field", ["piid", "awardee", "search"])
    def test_filter_only_params_are_not_response_fields(self, field):
        parser = ShapeParser(cache_enabled=True)
        with pytest.raises(ShapeValidationError):
            parser.validate(parser.parse(f"uuid,{field}"), AwardAnnouncement)
