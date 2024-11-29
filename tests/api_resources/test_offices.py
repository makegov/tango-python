# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tango import Tango, AsyncTango
from tango.types import Office, OfficeListResponse
from tests.utils import assert_matches_type

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestOffices:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_retrieve(self, client: Tango) -> None:
        office = client.offices.retrieve(
            "code",
        )
        assert_matches_type(Office, office, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: Tango) -> None:
        response = client.offices.with_raw_response.retrieve(
            "code",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        office = response.parse()
        assert_matches_type(Office, office, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: Tango) -> None:
        with client.offices.with_streaming_response.retrieve(
            "code",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            office = response.parse()
            assert_matches_type(Office, office, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: Tango) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `code` but received ''"):
            client.offices.with_raw_response.retrieve(
                "",
            )

    @parametrize
    def test_method_list(self, client: Tango) -> None:
        office = client.offices.list()
        assert_matches_type(OfficeListResponse, office, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: Tango) -> None:
        office = client.offices.list(
            limit=0,
            page=0,
            search="search",
        )
        assert_matches_type(OfficeListResponse, office, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: Tango) -> None:
        response = client.offices.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        office = response.parse()
        assert_matches_type(OfficeListResponse, office, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: Tango) -> None:
        with client.offices.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            office = response.parse()
            assert_matches_type(OfficeListResponse, office, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncOffices:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncTango) -> None:
        office = await async_client.offices.retrieve(
            "code",
        )
        assert_matches_type(Office, office, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncTango) -> None:
        response = await async_client.offices.with_raw_response.retrieve(
            "code",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        office = await response.parse()
        assert_matches_type(Office, office, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncTango) -> None:
        async with async_client.offices.with_streaming_response.retrieve(
            "code",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            office = await response.parse()
            assert_matches_type(Office, office, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncTango) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `code` but received ''"):
            await async_client.offices.with_raw_response.retrieve(
                "",
            )

    @parametrize
    async def test_method_list(self, async_client: AsyncTango) -> None:
        office = await async_client.offices.list()
        assert_matches_type(OfficeListResponse, office, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncTango) -> None:
        office = await async_client.offices.list(
            limit=0,
            page=0,
            search="search",
        )
        assert_matches_type(OfficeListResponse, office, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncTango) -> None:
        response = await async_client.offices.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        office = await response.parse()
        assert_matches_type(OfficeListResponse, office, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncTango) -> None:
        async with async_client.offices.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            office = await response.parse()
            assert_matches_type(OfficeListResponse, office, path=["response"])

        assert cast(Any, response.is_closed) is True
