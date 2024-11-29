# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tango import Tango, AsyncTango
from tests.utils import assert_matches_type
from tango._utils import parse_date
from tango.types.idvs import AwardListResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestAwards:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_list(self, client: Tango) -> None:
        award = client.idvs.awards.list(
            path_contract_award_unique_key="contract_award_unique_key",
        )
        assert_matches_type(AwardListResponse, award, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: Tango) -> None:
        award = client.idvs.awards.list(
            path_contract_award_unique_key="contract_award_unique_key",
            award_date="award_date",
            award_date_gte=parse_date("2019-12-27"),
            award_date_lte=parse_date("2019-12-27"),
            awarding_agency="awarding_agency",
            query_contract_award_unique_key="contract_award_unique_key",
            fiscal_year=0,
            fiscal_year_gte=0,
            fiscal_year_lte=0,
            funding_agency="funding_agency",
            limit=0,
            naics="naics",
            ordering="ordering",
            page=0,
            psc="psc",
            set_aside="set_aside",
            uei="uei",
        )
        assert_matches_type(AwardListResponse, award, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: Tango) -> None:
        response = client.idvs.awards.with_raw_response.list(
            path_contract_award_unique_key="contract_award_unique_key",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        award = response.parse()
        assert_matches_type(AwardListResponse, award, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: Tango) -> None:
        with client.idvs.awards.with_streaming_response.list(
            path_contract_award_unique_key="contract_award_unique_key",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            award = response.parse()
            assert_matches_type(AwardListResponse, award, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_list(self, client: Tango) -> None:
        with pytest.raises(
            ValueError, match=r"Expected a non-empty value for `path_contract_award_unique_key` but received ''"
        ):
            client.idvs.awards.with_raw_response.list(
                path_contract_award_unique_key="",
                query_contract_award_unique_key="",
            )


class TestAsyncAwards:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_list(self, async_client: AsyncTango) -> None:
        award = await async_client.idvs.awards.list(
            path_contract_award_unique_key="contract_award_unique_key",
        )
        assert_matches_type(AwardListResponse, award, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncTango) -> None:
        award = await async_client.idvs.awards.list(
            path_contract_award_unique_key="contract_award_unique_key",
            award_date="award_date",
            award_date_gte=parse_date("2019-12-27"),
            award_date_lte=parse_date("2019-12-27"),
            awarding_agency="awarding_agency",
            query_contract_award_unique_key="contract_award_unique_key",
            fiscal_year=0,
            fiscal_year_gte=0,
            fiscal_year_lte=0,
            funding_agency="funding_agency",
            limit=0,
            naics="naics",
            ordering="ordering",
            page=0,
            psc="psc",
            set_aside="set_aside",
            uei="uei",
        )
        assert_matches_type(AwardListResponse, award, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncTango) -> None:
        response = await async_client.idvs.awards.with_raw_response.list(
            path_contract_award_unique_key="contract_award_unique_key",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        award = await response.parse()
        assert_matches_type(AwardListResponse, award, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncTango) -> None:
        async with async_client.idvs.awards.with_streaming_response.list(
            path_contract_award_unique_key="contract_award_unique_key",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            award = await response.parse()
            assert_matches_type(AwardListResponse, award, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_list(self, async_client: AsyncTango) -> None:
        with pytest.raises(
            ValueError, match=r"Expected a non-empty value for `path_contract_award_unique_key` but received ''"
        ):
            await async_client.idvs.awards.with_raw_response.list(
                path_contract_award_unique_key="",
                query_contract_award_unique_key="",
            )
