# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tango import Tango, AsyncTango
from tango.types import Subaward, SubawardListResponse
from tests.utils import assert_matches_type

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestSubawards:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_retrieve(self, client: Tango) -> None:
        subaward = client.subawards.retrieve(
            0,
        )
        assert_matches_type(Subaward, subaward, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: Tango) -> None:
        response = client.subawards.with_raw_response.retrieve(
            0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        subaward = response.parse()
        assert_matches_type(Subaward, subaward, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: Tango) -> None:
        with client.subawards.with_streaming_response.retrieve(
            0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            subaward = response.parse()
            assert_matches_type(Subaward, subaward, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_list(self, client: Tango) -> None:
        subaward = client.subawards.list()
        assert_matches_type(SubawardListResponse, subaward, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: Tango) -> None:
        subaward = client.subawards.list(
            awarding_agency="awarding_agency",
            fiscal_year=0,
            fiscal_year_gte=0,
            fiscal_year_lte=0,
            funding_agency="funding_agency",
            limit=0,
            page=0,
            prime_uei="prime_uei",
            sub_uei="sub_uei",
        )
        assert_matches_type(SubawardListResponse, subaward, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: Tango) -> None:
        response = client.subawards.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        subaward = response.parse()
        assert_matches_type(SubawardListResponse, subaward, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: Tango) -> None:
        with client.subawards.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            subaward = response.parse()
            assert_matches_type(SubawardListResponse, subaward, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncSubawards:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncTango) -> None:
        subaward = await async_client.subawards.retrieve(
            0,
        )
        assert_matches_type(Subaward, subaward, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncTango) -> None:
        response = await async_client.subawards.with_raw_response.retrieve(
            0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        subaward = await response.parse()
        assert_matches_type(Subaward, subaward, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncTango) -> None:
        async with async_client.subawards.with_streaming_response.retrieve(
            0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            subaward = await response.parse()
            assert_matches_type(Subaward, subaward, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_list(self, async_client: AsyncTango) -> None:
        subaward = await async_client.subawards.list()
        assert_matches_type(SubawardListResponse, subaward, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncTango) -> None:
        subaward = await async_client.subawards.list(
            awarding_agency="awarding_agency",
            fiscal_year=0,
            fiscal_year_gte=0,
            fiscal_year_lte=0,
            funding_agency="funding_agency",
            limit=0,
            page=0,
            prime_uei="prime_uei",
            sub_uei="sub_uei",
        )
        assert_matches_type(SubawardListResponse, subaward, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncTango) -> None:
        response = await async_client.subawards.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        subaward = await response.parse()
        assert_matches_type(SubawardListResponse, subaward, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncTango) -> None:
        async with async_client.subawards.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            subaward = await response.parse()
            assert_matches_type(SubawardListResponse, subaward, path=["response"])

        assert cast(Any, response.is_closed) is True
