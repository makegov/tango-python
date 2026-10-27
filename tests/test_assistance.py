"""Tests for the financial-assistance award endpoints (`/api/assistance/{grants,loans,direct_payments,other}/`).

Covers the request contract for every method (path, filters under the API's own param names, the API's default shape, both pagination styles) and the shape schema behind them. Requests are mocked.
"""

import inspect
import json
from datetime import UTC, date, datetime
from decimal import Decimal
from pathlib import Path
from unittest.mock import Mock, patch

import httpx
import pytest

from tango import TangoClient
from tango.exceptions import ShapeValidationError, TangoValidationError
from tango.models import AssistanceAward, ShapeConfig
from tango.shapes.parser import ShapeParser

CONTRACT_PATH = Path(__file__).resolve().parents[1] / "contracts" / "filter_shape_contract.json"

AWARD_KEY = "ASST_NON_693JF72640002_069"

# (route segment, list method, get method, transactions method, listings method)
GROUPS = [
    (
        "grants",
        "list_assistance_grants",
        "get_assistance_grant",
        "list_assistance_grant_transactions",
        "list_assistance_grant_listings",
    ),
    (
        "loans",
        "list_assistance_loans",
        "get_assistance_loan",
        "list_assistance_loan_transactions",
        "list_assistance_loan_listings",
    ),
    (
        "direct_payments",
        "list_assistance_direct_payments",
        "get_assistance_direct_payment",
        "list_assistance_direct_payment_transactions",
        "list_assistance_direct_payment_listings",
    ),
    (
        "other",
        "list_assistance_other",
        "get_assistance_other",
        "list_assistance_other_transactions",
        "list_assistance_other_listings",
    ),
]
SEGMENTS = [group[0] for group in GROUPS]

ALL_FILTERS = {
    "key": "ASST_NON_A|ASST_NON_B",
    "fain": "693JF72640002",
    "uri": "27QQCACCDD-4106687094",
    "uei": "HS97F2C9NME3",
    "recipient": "port authority",
    "search": "wildfire resilience",
    "awarding_agency": "DOT",
    "funding_agency": "069",
    "cfda_number": "20.823|93.778",
    "assistance_type": "F001",
    "record_type": "2",
    "business_funds_indicator": "NON",
    "disaster_emergency_fund_code": "L",
    "funding_opportunity_number": "USDA-FS-2024-CWDG-CWSF",
    "award_date": "2026-10-19",
    "award_date_gte": "2026-01-01",
    "award_date_lte": "2026-12-31",
    "fiscal_year": 2027,
    "fiscal_year_gte": 2020,
    "fiscal_year_lte": 2027,
    "pop_start_date_gte": "2026-01-01",
    "pop_start_date_lte": "2026-12-31",
    "pop_end_date_gte": "2027-01-01",
    "pop_end_date_lte": "2029-12-31",
    "pop_state": "AL|VA",
    "pop_country": "USA",
    "pop_zip": "36633",
    "obligated_gte": 1000,
    "obligated_lte": "2500000.50",
    "ordering": "-pragmatic_obligations",
}


def _mock(mock_request, payload=None, headers=None):
    response = Mock()
    response.is_success = True
    response.status_code = 200
    response.headers = httpx.Headers(headers or {})
    response.json.return_value = (
        payload
        if payload is not None
        else {"count": 0, "next": None, "previous": None, "results": []}
    )
    response.content = b"{}"
    mock_request.return_value = response
    return response


def _call_params(mock_request) -> dict:
    return mock_request.call_args.kwargs.get("params") or {}


def _call_url(mock_request) -> str:
    return str(mock_request.call_args.kwargs.get("url", ""))


def _award(**overrides) -> dict:
    row = {
        "key": AWARD_KEY,
        "fain": "693JF72640002",
        "uri": None,
        "award_date": "2026-10-19",
        "fiscal_year": 2027,
        "assistance_type": {"code": "F001", "description": "Grant"},
        "record_type": "2",
        "cfda_number": "20.823",
        "assistance_listing": {
            "number": "20.823",
            "title": "Port Infrastructure Development Program",
        },
        "title": "AWARD PURPOSE THE PROJECT INCLUDES ELECTRICAL…",
        "obligated": 2000000.0,
        "pragmatic_obligations": 2000000.0,
        "face_value_of_loan": 0.0,
        "loan_subsidy_cost": 0.0,
        "awarding_office": {
            "organization_id": "261f885d-c8b6-5e0d-b2f8-e0799a4e1de2",
            "office_code": "69A334",
            "office_name": "MARITIME ADMINISTRATION",
            "agency_code": "6938",
            "agency_name": "MARITIME ADMINISTRATION",
            "department_code": "069",
            "department_name": "TRANSPORTATION, DEPARTMENT OF",
        },
        "funding_office": None,
        "recipient": {
            "uuid": "88f47661-874f-5298-8b0b-0971be0c746d",
            "uei": "HS97F2C9NME3",
            "duns": None,
            "legal_business_name": "ALABAMA PORT AUTHORITY",
            "legal_business_name_raw": "ALABAMA PORT AUTHORITY",
            "county": "MOBILE",
            "congressional_district": "AL-02",
            "congressional_district_original": "AL-02",
            "highest_owner": None,
            "business_types": [{"code": "A", "description": "State Government"}],
        },
        "place_of_performance": {
            "city_name": "MOBILE",
            "code": "AL36633",
            "country": "USA",
            "county_fips": "01097",
            "county_name": "MOBILE",
            "foreign_location": None,
            "scope": "SINGLE ZIP CODE",
            "state_code": "AL",
            "state_fips": "01",
            "state_name": "ALABAMA",
            "zip_code": "36633",
            "zip_plus_four": "1588",
        },
        "period_of_performance": {"start_date": "2026-10-19", "current_end_date": "2029-04-30"},
    }
    row.update(overrides)
    return row


def _contract_filter_params(segment: str) -> set[str]:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    return set(contract["resources"][f"assistance/{segment}"]["runtime"]["filter_params"])


def _filter_args(method) -> set[str]:
    non_filter = {"self", "cursor", "limit", "shape", "flat", "flat_lists", "joiner", "exact"}
    return set(inspect.signature(method).parameters) - non_filter


class TestListAssistanceAwards:
    @pytest.mark.parametrize(("segment", "list_method"), [(g[0], g[1]) for g in GROUPS])
    def test_filters_go_out_under_the_api_names(self, segment, list_method):
        with patch("tango.client.httpx.Client.request") as mock_request:
            _mock(mock_request)
            getattr(TangoClient(api_key="k"), list_method)(limit=10, **ALL_FILTERS)

        assert _call_url(mock_request).endswith(f"/api/assistance/{segment}/")
        assert _call_params(mock_request) == {
            "limit": 10,
            "shape": ShapeConfig.ASSISTANCE_AWARDS_MINIMAL,
            **ALL_FILTERS,
        }

    @pytest.mark.parametrize(("segment", "list_method"), [(g[0], g[1]) for g in GROUPS])
    def test_signature_exposes_exactly_the_contract_filters(self, segment, list_method):
        assert _filter_args(getattr(TangoClient, list_method)) == _contract_filter_params(segment)

    def test_contract_lists_every_assistance_resource(self):
        contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        assert {f"assistance/{s}" for s in SEGMENTS} <= set(contract["resources"])
        assert {"fain", "cfda_number", "pop_state", "obligated_gte"} <= _contract_filter_params(
            "grants"
        )

    @patch("tango.client.httpx.Client.request")
    def test_no_filters_are_synthesized(self, mock_request):
        _mock(mock_request)
        TangoClient(api_key="k").list_assistance_loans()
        assert _call_params(mock_request) == {
            "limit": 25,
            "shape": ShapeConfig.ASSISTANCE_AWARDS_MINIMAL,
        }

    @patch("tango.client.httpx.Client.request")
    def test_cursor_exact_and_flattening_are_passed(self, mock_request):
        _mock(mock_request)
        TangoClient(api_key="k").list_assistance_direct_payments(
            cursor="WyIyMDI2LTEwLTE2Il0",
            limit=500,
            shape="key,recipient(uei)",
            flat=True,
            joiner="__",
            flat_lists=True,
            exact=True,
        )
        assert _call_params(mock_request) == {
            "limit": 100,
            "cursor": "WyIyMDI2LTEwLTE2Il0",
            "shape": "key,recipient(uei)",
            "flat": "true",
            "joiner": "__",
            "flat_lists": "true",
            "exact": "true",
        }

    @patch("tango.client.httpx.Client.request")
    def test_empty_shape_sends_no_shape(self, mock_request):
        _mock(mock_request)
        TangoClient(api_key="k").list_assistance_other(shape="", flat=True)
        assert _call_params(mock_request) == {"limit": 25}

    @patch("tango.client.httpx.Client.request")
    def test_results_and_paging_are_parsed(self, mock_request):
        _mock(
            mock_request,
            {
                "count": 151,
                "next": "https://tango.makegov.com/api/assistance/grants/?cursor=abc",
                "previous": None,
                "cursor": "abc",
                "previous_cursor": None,
                "results": [_award()],
            },
            headers={"X-Results-CountType": "Approximate"},
        )
        page = TangoClient(api_key="k").list_assistance_grants(cfda_number="20.823")

        assert page.count == 151
        assert page.cursor == "abc"
        assert page.count_type == "approximate"
        row = page.results[0]
        assert row["key"] == AWARD_KEY
        assert row["award_date"] == date(2026, 10, 19)
        assert row["obligated"] == Decimal("2000000.0")
        assert isinstance(row["obligated"], Decimal)
        assert row["assistance_type"]["code"] == "F001"
        assert row["assistance_listing"]["title"] == "Port Infrastructure Development Program"
        assert row["recipient"]["legal_business_name"] == "ALABAMA PORT AUTHORITY"
        assert row["recipient"]["business_types"] == [
            {"code": "A", "description": "State Government"}
        ]
        assert row["awarding_office"]["office_code"] == "69A334"
        assert row["funding_office"] is None
        assert row["place_of_performance"]["state_code"] == "AL"
        assert row["period_of_performance"]["current_end_date"] == date(2029, 4, 30)


class TestGetAssistanceAward:
    @pytest.mark.parametrize(("segment", "get_method"), [(g[0], g[2]) for g in GROUPS])
    def test_get_uses_the_key_route_and_default_shape(self, segment, get_method):
        with patch("tango.client.httpx.Client.request") as mock_request:
            _mock(mock_request, _award())
            row = getattr(TangoClient(api_key="k"), get_method)(AWARD_KEY)

        assert _call_url(mock_request).endswith(f"/api/assistance/{segment}/{AWARD_KEY}/")
        assert _call_params(mock_request) == {"shape": ShapeConfig.ASSISTANCE_AWARDS_MINIMAL}
        assert row["key"] == AWARD_KEY

    @patch("tango.client.httpx.Client.request")
    def test_key_is_escaped_as_one_path_segment(self, mock_request):
        _mock(mock_request, _award())
        TangoClient(api_key="k").get_assistance_grant("ASST_NON_A/B#1")
        assert _call_url(mock_request).endswith("/api/assistance/grants/ASST_NON_A%2FB%231/")

    def test_empty_key_is_refused_before_any_request(self):
        with patch("tango.client.httpx.Client.request") as mock_request:
            with pytest.raises(TangoValidationError):
                TangoClient(api_key="k").get_assistance_loan("")
        mock_request.assert_not_called()

    @patch("tango.client.httpx.Client.request")
    def test_detail_expansions_parse(self, mock_request):
        _mock(
            mock_request,
            {
                "key": AWARD_KEY,
                "last_modified_date": "2026-10-20T13:59:38+00:00",
                "former_award_keys": ["ASST_NON_8606059100_7300"],
                "officers": {"highly_compensated_officer_1_name": "JANE DOE"},
                "obligations_by_fiscal_year": [{"fiscal_year": 2027, "obligated": 2000000.0}],
                "listings": [
                    {
                        "cfda_number": "20.823",
                        "is_primary": True,
                        "obligated": 2000000.0,
                        "transactions_count": 1,
                        "first_action_date": "2026-10-19",
                    }
                ],
                "transactions": [
                    {"key": "6938_693JF72640002", "transaction_date": "2026-10-19"},
                ],
            },
        )
        row = TangoClient(api_key="k").get_assistance_grant(
            AWARD_KEY,
            shape=(
                "key,last_modified_date,former_award_keys,officers(*),"
                "obligations_by_fiscal_year(fiscal_year,obligated),"
                "listings(cfda_number,is_primary,first_action_date),transactions(key,transaction_date)"
            ),
        )

        assert row["last_modified_date"] == datetime(2026, 10, 20, 13, 59, 38, tzinfo=UTC)
        assert row["former_award_keys"] == ["ASST_NON_8606059100_7300"]
        assert row["officers"]["highly_compensated_officer_1_name"] == "JANE DOE"
        assert isinstance(row["obligations_by_fiscal_year"][0]["obligated"], Decimal)
        assert row["listings"][0]["is_primary"] is True
        assert row["listings"][0]["first_action_date"] == date(2026, 10, 19)
        assert row["transactions"][0]["transaction_date"] == date(2026, 10, 19)


class TestAssistanceAwardSubRoutes:
    @pytest.mark.parametrize(
        ("segment", "method", "sub_route", "default_limit"),
        [(g[0], g[3], "transactions", 100) for g in GROUPS]
        + [(g[0], g[4], "listings", 10) for g in GROUPS],
    )
    def test_route_and_page_number_paging(self, segment, method, sub_route, default_limit):
        with patch("tango.client.httpx.Client.request") as mock_request:
            _mock(mock_request)
            getattr(TangoClient(api_key="k"), method)(AWARD_KEY)

        assert _call_url(mock_request).endswith(
            f"/api/assistance/{segment}/{AWARD_KEY}/{sub_route}/"
        )
        assert _call_params(mock_request) == {"page": 1, "limit": default_limit}

    @pytest.mark.parametrize(
        ("method", "cap"),
        [("list_assistance_grant_transactions", 500), ("list_assistance_grant_listings", 100)],
    )
    def test_limit_is_capped_at_the_route_maximum(self, method, cap):
        with patch("tango.client.httpx.Client.request") as mock_request:
            _mock(mock_request)
            getattr(TangoClient(api_key="k"), method)(AWARD_KEY, page=3, limit=10_000)
        assert _call_params(mock_request) == {"page": 3, "limit": cap}

    @patch("tango.client.httpx.Client.request")
    def test_rows_come_back_as_dicts(self, mock_request):
        transaction = {
            "key": "6938_693JF72640002_-NONE-_20.823_-NONE-",
            "transaction_date": "2026-10-19",
            "action_type": "A1",
            "obligated": 2000000.0,
            "action_date_fiscal_year": 2027,
        }
        _mock(
            mock_request,
            {
                "count": 2,
                "next": "https://tango.makegov.com/api/assistance/loans/K/transactions/?page=2",
                "previous": None,
                "results": [transaction],
            },
        )
        page = TangoClient(api_key="k").list_assistance_loan_transactions("K", limit=1)

        assert page.count == 2
        assert page.next is not None
        assert page.results == [transaction]

    def test_empty_key_is_refused_before_any_request(self):
        with patch("tango.client.httpx.Client.request") as mock_request:
            with pytest.raises(TangoValidationError):
                TangoClient(api_key="k").list_assistance_other_listings("")
        mock_request.assert_not_called()


class TestAssistanceAwardShapes:
    def test_default_shape_mirrors_the_api_default(self):
        assert ShapeConfig.ASSISTANCE_AWARDS_MINIMAL == (
            "key,fain,uri,award_date,fiscal_year,assistance_type(code,description),"
            "record_type,cfda_number,assistance_listing(number,title),title,"
            "obligated,pragmatic_obligations,face_value_of_loan,loan_subsidy_cost,"
            "awarding_office(*),funding_office(*),recipient(*),place_of_performance(*),"
            "period_of_performance(start_date,current_end_date)"
        )

    @pytest.mark.parametrize("segment", SEGMENTS)
    def test_every_field_and_expansion_the_api_allows_validates(self, segment):
        contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        tree = contract["resources"][f"assistance/{segment}"]["runtime"]["shape"]
        leaves = [field for field in tree["fields"] if field not in tree["expands"]]
        expands = [f"{name}({','.join(node['fields'])})" for name, node in tree["expands"].items()]
        assert len(leaves) > 40 and len(expands) == 12

        parser = ShapeParser(cache_enabled=True)
        parser.validate(parser.parse(",".join(leaves + expands)), AssistanceAward)

    @pytest.mark.parametrize("shape", ["key,transactions", "key,assistance_type"])
    def test_leaf_forms_of_expansions_validate(self, shape):
        parser = ShapeParser(cache_enabled=True)
        parser.validate(parser.parse(shape), AssistanceAward)

    @pytest.mark.parametrize("field", ["piid", "naics_code", "description", "recipient_name"])
    def test_procurement_only_fields_are_rejected(self, field):
        parser = ShapeParser(cache_enabled=True)
        with pytest.raises(ShapeValidationError):
            parser.validate(parser.parse(f"key,{field}"), AssistanceAward)
