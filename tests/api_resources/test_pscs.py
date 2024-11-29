# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tango import Tango, AsyncTango
from tango.types import PscListResponse, ProductServiceCode
from tests.utils import assert_matches_type

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestPscs:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_retrieve(self, client: Tango) -> None:
        psc = client.pscs.retrieve(
            0,
        )
        assert_matches_type(ProductServiceCode, psc, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: Tango) -> None:
        response = client.pscs.with_raw_response.retrieve(
            0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        psc = response.parse()
        assert_matches_type(ProductServiceCode, psc, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: Tango) -> None:
        with client.pscs.with_streaming_response.retrieve(
            0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            psc = response.parse()
            assert_matches_type(ProductServiceCode, psc, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_list(self, client: Tango) -> None:
        psc = client.pscs.list()
        assert_matches_type(PscListResponse, psc, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: Tango) -> None:
        response = client.pscs.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        psc = response.parse()
        assert_matches_type(PscListResponse, psc, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: Tango) -> None:
        with client.pscs.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            psc = response.parse()
            assert_matches_type(PscListResponse, psc, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncPscs:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncTango) -> None:
        psc = await async_client.pscs.retrieve(
            0,
        )
        assert_matches_type(ProductServiceCode, psc, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncTango) -> None:
        response = await async_client.pscs.with_raw_response.retrieve(
            0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        psc = await response.parse()
        assert_matches_type(ProductServiceCode, psc, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncTango) -> None:
        async with async_client.pscs.with_streaming_response.retrieve(
            0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            psc = await response.parse()
            assert_matches_type(ProductServiceCode, psc, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_list(self, async_client: AsyncTango) -> None:
        psc = await async_client.pscs.list()
        assert_matches_type(PscListResponse, psc, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncTango) -> None:
        response = await async_client.pscs.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        psc = await response.parse()
        assert_matches_type(PscListResponse, psc, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncTango) -> None:
        async with async_client.pscs.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            psc = await response.parse()
            assert_matches_type(PscListResponse, psc, path=["response"])

        assert cast(Any, response.is_closed) is True
