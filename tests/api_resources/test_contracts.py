# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tango import Tango, AsyncTango
from tango.types import ContractListResponse, ContractRetrieveResponse
from tests.utils import assert_matches_type

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestContracts:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_retrieve(self, client: Tango) -> None:
        contract = client.contracts.retrieve(
            "contract_award_unique_key",
        )
        assert_matches_type(ContractRetrieveResponse, contract, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: Tango) -> None:
        response = client.contracts.with_raw_response.retrieve(
            "contract_award_unique_key",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        contract = response.parse()
        assert_matches_type(ContractRetrieveResponse, contract, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: Tango) -> None:
        with client.contracts.with_streaming_response.retrieve(
            "contract_award_unique_key",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            contract = response.parse()
            assert_matches_type(ContractRetrieveResponse, contract, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: Tango) -> None:
        with pytest.raises(
            ValueError, match=r"Expected a non-empty value for `contract_award_unique_key` but received ''"
        ):
            client.contracts.with_raw_response.retrieve(
                "",
            )

    @parametrize
    def test_method_list(self, client: Tango) -> None:
        contract = client.contracts.list()
        assert_matches_type(ContractListResponse, contract, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: Tango) -> None:
        contract = client.contracts.list(
            award_date="award_date",
            award_date_gte="award_date_gte",
            award_date_lte="award_date_lte",
            awarding_agency="awarding_agency",
            fiscal_year="fiscal_year",
            fiscal_year_gte="fiscal_year_gte",
            fiscal_year_lte="fiscal_year_lte",
            funding_agency="funding_agency",
            limit=0,
            naics="naics",
            ordering="ordering",
            page=0,
            psc="psc",
            set_aside="set_aside",
            uei="uei",
        )
        assert_matches_type(ContractListResponse, contract, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: Tango) -> None:
        response = client.contracts.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        contract = response.parse()
        assert_matches_type(ContractListResponse, contract, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: Tango) -> None:
        with client.contracts.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            contract = response.parse()
            assert_matches_type(ContractListResponse, contract, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncContracts:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncTango) -> None:
        contract = await async_client.contracts.retrieve(
            "contract_award_unique_key",
        )
        assert_matches_type(ContractRetrieveResponse, contract, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncTango) -> None:
        response = await async_client.contracts.with_raw_response.retrieve(
            "contract_award_unique_key",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        contract = await response.parse()
        assert_matches_type(ContractRetrieveResponse, contract, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncTango) -> None:
        async with async_client.contracts.with_streaming_response.retrieve(
            "contract_award_unique_key",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            contract = await response.parse()
            assert_matches_type(ContractRetrieveResponse, contract, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncTango) -> None:
        with pytest.raises(
            ValueError, match=r"Expected a non-empty value for `contract_award_unique_key` but received ''"
        ):
            await async_client.contracts.with_raw_response.retrieve(
                "",
            )

    @parametrize
    async def test_method_list(self, async_client: AsyncTango) -> None:
        contract = await async_client.contracts.list()
        assert_matches_type(ContractListResponse, contract, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncTango) -> None:
        contract = await async_client.contracts.list(
            award_date="award_date",
            award_date_gte="award_date_gte",
            award_date_lte="award_date_lte",
            awarding_agency="awarding_agency",
            fiscal_year="fiscal_year",
            fiscal_year_gte="fiscal_year_gte",
            fiscal_year_lte="fiscal_year_lte",
            funding_agency="funding_agency",
            limit=0,
            naics="naics",
            ordering="ordering",
            page=0,
            psc="psc",
            set_aside="set_aside",
            uei="uei",
        )
        assert_matches_type(ContractListResponse, contract, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncTango) -> None:
        response = await async_client.contracts.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        contract = await response.parse()
        assert_matches_type(ContractListResponse, contract, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncTango) -> None:
        async with async_client.contracts.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            contract = await response.parse()
            assert_matches_type(ContractListResponse, contract, path=["response"])

        assert cast(Any, response.is_closed) is True
