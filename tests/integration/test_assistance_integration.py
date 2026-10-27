"""Integration tests for the financial-assistance award endpoints

Pytest Markers:
    @pytest.mark.integration: Marks tests as integration tests that may hit external APIs
    @pytest.mark.vcr(): Enables VCR recording/playback for HTTP interactions

Usage:
    pytest tests/integration/test_assistance_integration.py
"""

import pytest

from tests.integration.conftest import handle_api_exceptions
from tests.integration.validation import validate_no_parsing_errors, validate_pagination

# (route segment, list method, get method, transactions method, listings method, GSDM codes)
GROUPS = [
    (
        "grants",
        "list_assistance_grants",
        "get_assistance_grant",
        "list_assistance_grant_transactions",
        "list_assistance_grant_listings",
        {"F001", "F002"},
    ),
    (
        "loans",
        "list_assistance_loans",
        "get_assistance_loan",
        "list_assistance_loan_transactions",
        "list_assistance_loan_listings",
        {"F003", "F004"},
    ),
    (
        "direct_payments",
        "list_assistance_direct_payments",
        "get_assistance_direct_payment",
        "list_assistance_direct_payment_transactions",
        "list_assistance_direct_payment_listings",
        {"F006", "F007"},
    ),
    (
        "other",
        "list_assistance_other",
        "get_assistance_other",
        "list_assistance_other_transactions",
        "list_assistance_other_listings",
        {"F005", "F008", "F009", "F010"},
    ),
]
SEGMENTS = [group[0] for group in GROUPS]


@pytest.mark.vcr()
@pytest.mark.integration
class TestAssistanceAwardsIntegration:
    @pytest.mark.parametrize(
        ("segment", "list_method", "codes"),
        [(g[0], g[1], g[5]) for g in GROUPS],
        ids=SEGMENTS,
    )
    @handle_api_exceptions("assistance")
    def test_list_pages_by_cursor(self, tango_client, segment, list_method, codes):
        list_awards = getattr(tango_client, list_method)
        first = list_awards(limit=2)

        validate_pagination(first)
        assert len(first.results) == 2
        assert first.cursor
        for award in first.results:
            validate_no_parsing_errors(award)
            assert award["key"]
            assert award["assistance_type"]["code"] in codes

        second = list_awards(limit=2, cursor=first.cursor)
        assert {a["key"] for a in first.results}.isdisjoint(a["key"] for a in second.results)

    @pytest.mark.parametrize(
        ("segment", "list_method", "get_method", "transactions_method", "listings_method"),
        [g[:5] for g in GROUPS],
        ids=SEGMENTS,
    )
    @handle_api_exceptions("assistance")
    def test_get_and_sub_routes(
        self, tango_client, segment, list_method, get_method, transactions_method, listings_method
    ):
        key = getattr(tango_client, list_method)(limit=1, shape="key").results[0]["key"]

        award = getattr(tango_client, get_method)(key)
        assert award["key"] == key
        validate_no_parsing_errors(award)

        transactions = getattr(tango_client, transactions_method)(key, limit=5)
        assert transactions.count >= 1
        assert all(row["key"] for row in transactions.results)

        listings = getattr(tango_client, listings_method)(key)
        assert listings.count >= 1
        assert listings.results[0]["is_primary"] is True

    @handle_api_exceptions("assistance")
    def test_filters_narrow_the_list(self, tango_client):
        response = tango_client.list_assistance_grants(
            cfda_number="93.778",
            fiscal_year=2026,
            shape="key,cfda_number,fiscal_year,obligated",
            ordering="-obligated",
            limit=3,
        )

        validate_pagination(response)
        assert response.results
        for award in response.results:
            assert award["cfda_number"] == "93.778"
            assert award["fiscal_year"] == 2026
        amounts = [award["obligated"] for award in response.results]
        assert amounts == sorted(amounts, reverse=True)
