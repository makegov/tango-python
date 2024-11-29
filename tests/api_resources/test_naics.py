# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tango import Tango, AsyncTango
from tango.types import NaicListResponse, NaicRetrieveResponse
from tests.utils import assert_matches_type

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestNaics:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_retrieve(self, client: Tango) -> None:
        naic = client.naics.retrieve(
            -2147483648,
        )
        assert_matches_type(NaicRetrieveResponse, naic, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: Tango) -> None:
        response = client.naics.with_raw_response.retrieve(
            -2147483648,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        naic = response.parse()
        assert_matches_type(NaicRetrieveResponse, naic, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: Tango) -> None:
        with client.naics.with_streaming_response.retrieve(
            -2147483648,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            naic = response.parse()
            assert_matches_type(NaicRetrieveResponse, naic, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_list(self, client: Tango) -> None:
        naic = client.naics.list()
        assert_matches_type(NaicListResponse, naic, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: Tango) -> None:
        naic = client.naics.list(
            employee_limit="employee_limit",
            employee_limit_gte="employee_limit_gte",
            employee_limit_lte="employee_limit_lte",
            revenue_limit="revenue_limit",
            revenue_limit_gte="revenue_limit_gte",
            revenue_limit_lte="revenue_limit_lte",
            search="search",
            show_limits="show_limits",
        )
        assert_matches_type(NaicListResponse, naic, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: Tango) -> None:
        response = client.naics.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        naic = response.parse()
        assert_matches_type(NaicListResponse, naic, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: Tango) -> None:
        with client.naics.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            naic = response.parse()
            assert_matches_type(NaicListResponse, naic, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncNaics:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncTango) -> None:
        naic = await async_client.naics.retrieve(
            -2147483648,
        )
        assert_matches_type(NaicRetrieveResponse, naic, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncTango) -> None:
        response = await async_client.naics.with_raw_response.retrieve(
            -2147483648,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        naic = await response.parse()
        assert_matches_type(NaicRetrieveResponse, naic, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncTango) -> None:
        async with async_client.naics.with_streaming_response.retrieve(
            -2147483648,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            naic = await response.parse()
            assert_matches_type(NaicRetrieveResponse, naic, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_list(self, async_client: AsyncTango) -> None:
        naic = await async_client.naics.list()
        assert_matches_type(NaicListResponse, naic, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncTango) -> None:
        naic = await async_client.naics.list(
            employee_limit="employee_limit",
            employee_limit_gte="employee_limit_gte",
            employee_limit_lte="employee_limit_lte",
            revenue_limit="revenue_limit",
            revenue_limit_gte="revenue_limit_gte",
            revenue_limit_lte="revenue_limit_lte",
            search="search",
            show_limits="show_limits",
        )
        assert_matches_type(NaicListResponse, naic, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncTango) -> None:
        response = await async_client.naics.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        naic = await response.parse()
        assert_matches_type(NaicListResponse, naic, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncTango) -> None:
        async with async_client.naics.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            naic = await response.parse()
            assert_matches_type(NaicListResponse, naic, path=["response"])

        assert cast(Any, response.is_closed) is True
