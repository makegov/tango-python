"""Integration tests for IT Dashboard investment endpoints

Pytest Markers:
    @pytest.mark.integration: Marks tests as integration tests that may hit external APIs
    @pytest.mark.vcr(): Enables VCR recording/playback for HTTP interactions

Usage:
    # Run only IT Dashboard integration tests
    pytest tests/integration/test_itdashboard_integration.py

    # Refresh cassettes (re-record all interactions) - requires API key
    TANGO_REFRESH_CASSETTES=true TANGO_API_KEY=xxx pytest tests/integration/test_itdashboard_integration.py

API reference: https://tango.makegov.com/docs/api-reference/itdashboard.md

Note on tier-gated filters:
    The API gates several filters by access tier:

    - **Free**: ``search``
    - **Pro**: ``agency_code``, ``type_of_investment``,
      ``updated_time_after`` / ``updated_time_before``
    - **Business+**: ``agency_name``, ``cio_rating``, ``cio_rating_max``,
      ``performance_risk``

    Cassettes here were recorded with a business+ key. If you re-record with a
    lower-tier key, the gated filter tests will receive 403s and need updating.
"""

from datetime import datetime

import pytest

from tango import ShapeConfig
from tests.integration.conftest import handle_api_exceptions
from tests.integration.validation import (
    validate_no_parsing_errors,
    validate_pagination,
)


def _get(obj, attr):
    """Read a field from a dict-like or attribute-bearing instance."""
    if isinstance(obj, dict):
        return obj.get(attr)
    return getattr(obj, attr, None)


def validate_investment_fields(investment, comprehensive: bool = False) -> None:
    """Validate IT Dashboard investment has required fields and correct types."""
    uii = _get(investment, "uii")
    assert uii is not None, "Investment 'uii' must not be None"
    assert isinstance(uii, str), f"Investment 'uii' must be string, got {type(uii)}"

    # Optional string fields
    for field in (
        "agency_name",
        "bureau_name",
        "investment_title",
        "type_of_investment",
        "part_of_it_portfolio",
        "url",
    ):
        value = _get(investment, field)
        if value is not None:
            assert isinstance(value, str), f"Investment '{field}' must be string, got {type(value)}"

    updated_time = _get(investment, "updated_time")
    if updated_time is not None:
        assert isinstance(updated_time, datetime), (
            f"Investment 'updated_time' must be datetime, got {type(updated_time)}"
        )

    if comprehensive:
        agency_code = _get(investment, "agency_code")
        if agency_code is not None:
            assert isinstance(agency_code, int), (
                f"Investment 'agency_code' must be int, got {type(agency_code)}"
            )


@pytest.mark.vcr()
@pytest.mark.integration
class TestITDashboardIntegration:
    """Integration tests for IT Dashboard investment endpoints using production data"""

    @handle_api_exceptions("itdashboard")
    @pytest.mark.parametrize(
        "shape_name,shape_value",
        [
            ("default", None),
            ("minimal", ShapeConfig.ITDASHBOARD_INVESTMENTS_MINIMAL),
            ("custom", "uii,agency_name,investment_title,updated_time"),
        ],
    )
    def test_list_itdashboard_investments_with_shapes(self, tango_client, shape_name, shape_value):
        """Test listing investments with different shapes."""
        kwargs: dict = {"limit": 5}
        if shape_value is not None:
            kwargs["shape"] = shape_value

        response = tango_client.list_itdashboard_investments(**kwargs)

        validate_pagination(response)
        assert response.count >= 0

        if response.results:
            investment = response.results[0]
            validate_investment_fields(investment)
            validate_no_parsing_errors(investment)

    @handle_api_exceptions("itdashboard")
    def test_list_itdashboard_investments_with_search(self, tango_client):
        """Test free-tier search filter (full-text across UII, title, description, agency, bureau)."""
        response = tango_client.list_itdashboard_investments(limit=5, search="cyber")

        validate_pagination(response)
        if response.results:
            for investment in response.results:
                validate_investment_fields(investment)
                validate_no_parsing_errors(investment)

    @handle_api_exceptions("itdashboard")
    def test_itdashboard_pagination(self, tango_client):
        """Verify pagination returns disjoint pages."""
        page1 = tango_client.list_itdashboard_investments(limit=5, page=1)
        validate_pagination(page1)

        page2 = tango_client.list_itdashboard_investments(limit=5, page=2)
        validate_pagination(page2)

        if page1.results and page2.results:
            uii1 = _get(page1.results[0], "uii")
            uii2 = _get(page2.results[0], "uii")
            assert uii1 != uii2, "Different pages should return different investments"

    @handle_api_exceptions("itdashboard")
    def test_get_itdashboard_investment_by_uii(self, tango_client):
        """Test get_itdashboard_investment detail using a UII from the list response."""
        response = tango_client.list_itdashboard_investments(limit=1)
        validate_pagination(response)

        if not response.results:
            pytest.skip("No investments returned from list to fetch by uii")

        uii = _get(response.results[0], "uii")
        assert uii is not None

        detail = tango_client.get_itdashboard_investment(uii)
        validate_investment_fields(detail, comprehensive=True)
        validate_no_parsing_errors(detail)

        detail_uii = _get(detail, "uii")
        assert detail_uii == uii, "Detail uii should match requested uii"

    # ------------------------------------------------------------------
    # Pro-tier filters
    # ------------------------------------------------------------------

    @handle_api_exceptions("itdashboard")
    def test_filter_by_agency_code(self, tango_client):
        """Pro-tier: filter by integer agency code (21 = Department of Transportation)."""
        response = tango_client.list_itdashboard_investments(limit=5, agency_code=21)
        validate_pagination(response)

        if response.results:
            for investment in response.results:
                validate_investment_fields(investment)
                validate_no_parsing_errors(investment)
                # When the shape includes agency_name, every result should be DOT.
                agency_name = _get(investment, "agency_name")
                if agency_name is not None:
                    assert "Transportation" in agency_name, (
                        f"Expected DOT-affiliated agency, got {agency_name!r}"
                    )

    @handle_api_exceptions("itdashboard")
    def test_filter_by_type_of_investment(self, tango_client):
        """Pro-tier: filter by investment type (case-insensitive iexact match)."""
        response = tango_client.list_itdashboard_investments(
            limit=5, type_of_investment="Major IT Investments"
        )
        validate_pagination(response)

        if response.results:
            for investment in response.results:
                validate_investment_fields(investment)
                validate_no_parsing_errors(investment)
                type_of = _get(investment, "type_of_investment")
                if type_of is not None:
                    assert type_of.lower() == "major it investments", (
                        f"Expected major-it-investments, got {type_of!r}"
                    )

    @handle_api_exceptions("itdashboard")
    def test_filter_by_updated_time_range(self, tango_client):
        """Pro-tier: filter by updated_time range using string-form ISO dates."""
        response = tango_client.list_itdashboard_investments(
            limit=5,
            updated_time_after="2026-01-01",
            updated_time_before="2026-12-31",
        )
        validate_pagination(response)

        if response.results:
            for investment in response.results:
                validate_investment_fields(investment)
                validate_no_parsing_errors(investment)
                updated = _get(investment, "updated_time")
                if updated is not None:
                    assert updated.year == 2026, f"Expected updated_time in 2026, got {updated!r}"

    # ------------------------------------------------------------------
    # Business+ filters
    # ------------------------------------------------------------------

    @handle_api_exceptions("itdashboard")
    def test_filter_by_agency_name_text(self, tango_client):
        """Business+: text search across agency name (icontains)."""
        response = tango_client.list_itdashboard_investments(limit=5, agency_name="defense")
        validate_pagination(response)

        if response.results:
            for investment in response.results:
                validate_investment_fields(investment)
                validate_no_parsing_errors(investment)
                agency_name = _get(investment, "agency_name")
                if agency_name is not None:
                    assert "defense" in agency_name.lower(), (
                        f"Expected agency name containing 'defense', got {agency_name!r}"
                    )

    @handle_api_exceptions("itdashboard")
    def test_filter_by_cio_rating(self, tango_client):
        """Business+: exact CIO risk rating (1 = High Risk)."""
        response = tango_client.list_itdashboard_investments(limit=5, cio_rating=1)
        validate_pagination(response)
        # We only assert structural validity here — verifying the rating itself
        # would require expanding cio_evaluation, which is exercised separately.
        for investment in response.results:
            validate_investment_fields(investment)
            validate_no_parsing_errors(investment)

    @handle_api_exceptions("itdashboard")
    def test_filter_by_cio_rating_max(self, tango_client):
        """Business+: investments at-or-below CIO rating threshold (2 = high + moderately high)."""
        response = tango_client.list_itdashboard_investments(limit=5, cio_rating_max=2)
        validate_pagination(response)
        for investment in response.results:
            validate_investment_fields(investment)
            validate_no_parsing_errors(investment)

    @handle_api_exceptions("itdashboard")
    def test_filter_by_performance_risk(self, tango_client):
        """Business+: investments with at least one NOT MET performance metric."""
        response = tango_client.list_itdashboard_investments(limit=5, performance_risk=True)
        validate_pagination(response)
        for investment in response.results:
            validate_investment_fields(investment)
            validate_no_parsing_errors(investment)

    # ------------------------------------------------------------------
    # Shape expansions
    # ------------------------------------------------------------------

    @handle_api_exceptions("itdashboard")
    def test_funding_and_cio_evaluation_expansions(self, tango_client):
        """Verify ``funding`` (dict) and ``cio_evaluation`` (list-of-dict) expansions parse through."""
        response = tango_client.list_itdashboard_investments(
            limit=3,
            shape="uii,agency_name,funding(*),cio_evaluation(*)",
        )
        validate_pagination(response)

        if not response.results:
            pytest.skip("No investments returned to validate expansions")

        for investment in response.results:
            assert _get(investment, "uii") is not None
            funding = _get(investment, "funding")
            if funding is not None:
                assert isinstance(funding, dict), f"funding must be dict, got {type(funding)}"
            cio_eval = _get(investment, "cio_evaluation")
            if cio_eval is not None:
                assert isinstance(cio_eval, list), (
                    f"cio_evaluation must be list, got {type(cio_eval)}"
                )
                for entry in cio_eval:
                    assert isinstance(entry, dict), (
                        f"cio_evaluation entries must be dicts, got {type(entry)}"
                    )
