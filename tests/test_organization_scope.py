"""Tests for the organization-scoped `agency` filter and the `organization` expand added in API 5.3.0."""

from unittest.mock import Mock, patch

import pytest

from tango import TangoClient
from tango.models import BudgetAccount, Exclusion, SbirSolicitation, SbirTopic
from tango.shapes.parser import ShapeParser

ORGANIZATION = {
    "organization_id": "0f6c1d9e-5b7a-4c2e-9a41-3e8d2b7c6a10",
    "department_code": "068",
    "department_name": "Environmental Protection Agency",
    "agency_code": "6800",
    "agency_name": "Environmental Protection Agency",
    "office_code": None,
    "office_name": None,
}

ORGANIZATION_SHAPE = (
    "organization(agency_code,agency_name,department_code,department_name,"
    "office_code,office_name,organization_id)"
)


def _mock(mock_request, payload=None):
    response = Mock()
    response.is_success = True
    response.json.return_value = (
        payload
        if payload is not None
        else {"count": 0, "next": None, "previous": None, "results": []}
    )
    response.content = b"{}"
    mock_request.return_value = response
    return response


def _call(mock_request) -> tuple[str, dict]:
    args = mock_request.call_args.args
    url = str(args[1]) if len(args) > 1 else str(mock_request.call_args.kwargs.get("url", ""))
    return url, mock_request.call_args.kwargs.get("params") or {}


class TestAgencyFilter:
    @pytest.mark.parametrize(
        ("method", "path"),
        [
            ("list_budget_accounts", "/api/budget/accounts/"),
            ("list_exclusions", "/api/exclusions/"),
            ("list_itdashboard_investments", "/api/itdashboard/"),
        ],
    )
    @patch("tango.client.httpx.Client.request")
    def test_agency_is_sent_as_the_api_param(self, mock_request, method, path):
        _mock(mock_request)
        getattr(TangoClient(api_key="k"), method)(agency="EPA|DOT")
        url, params = _call(mock_request)
        assert path in url
        assert params["agency"] == "EPA|DOT"

    @pytest.mark.parametrize(
        "method", ["list_budget_accounts", "list_exclusions", "list_itdashboard_investments"]
    )
    @patch("tango.client.httpx.Client.request")
    def test_agency_is_omitted_when_unset(self, mock_request, method):
        _mock(mock_request)
        getattr(TangoClient(api_key="k"), method)()
        assert "agency" not in _call(mock_request)[1]


class TestOrganizationExpand:
    @pytest.mark.parametrize("model", [BudgetAccount, Exclusion, SbirTopic, SbirSolicitation])
    def test_organization_expand_validates(self, model):
        parser = ShapeParser(cache_enabled=True)
        parser.validate(parser.parse(ORGANIZATION_SHAPE), model)
        parser.validate(parser.parse("organization(*)"), model)

    @pytest.mark.parametrize("model", [BudgetAccount, Exclusion])
    def test_organization_id_validates(self, model):
        parser = ShapeParser(cache_enabled=True)
        parser.validate(parser.parse("organization_id"), model)

    @patch("tango.client.httpx.Client.request")
    def test_exclusion_row_parses_the_organization(self, mock_request):
        _mock(
            mock_request,
            {
                "count": 1,
                "next": None,
                "previous": None,
                "results": [
                    {
                        "organization_id": ORGANIZATION["organization_id"],
                        "organization": ORGANIZATION,
                    }
                ],
            },
        )
        page = TangoClient(api_key="k").list_exclusions(
            shape=f"organization_id,{ORGANIZATION_SHAPE}"
        )
        row = page.results[0]
        assert row["organization_id"] == ORGANIZATION["organization_id"]
        assert row["organization"]["agency_code"] == "6800"
        assert row["organization"]["office_code"] is None
