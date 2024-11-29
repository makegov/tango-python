# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tango import Tango, AsyncTango
from tango.types import EntityListResponse, EntityRetrieveResponse
from tests.utils import assert_matches_type

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestEntities:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_retrieve(self, client: Tango) -> None:
        entity = client.entities.retrieve(
            "uei",
        )
        assert_matches_type(EntityRetrieveResponse, entity, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: Tango) -> None:
        response = client.entities.with_raw_response.retrieve(
            "uei",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        entity = response.parse()
        assert_matches_type(EntityRetrieveResponse, entity, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: Tango) -> None:
        with client.entities.with_streaming_response.retrieve(
            "uei",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            entity = response.parse()
            assert_matches_type(EntityRetrieveResponse, entity, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: Tango) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `uei` but received ''"):
            client.entities.with_raw_response.retrieve(
                "",
            )

    @parametrize
    def test_method_list(self, client: Tango) -> None:
        entity = client.entities.list()
        assert_matches_type(EntityListResponse, entity, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: Tango) -> None:
        entity = client.entities.list(
            cage_code="cage_code",
            limit=0,
            naics="naics",
            name="name",
            page=0,
            psc="psc",
            purpose_of_registration_code="purpose_of_registration_code",
            search="search",
            socioeconomic="socioeconomic",
            state="state",
            uei="uei",
            zip_code="zip_code",
        )
        assert_matches_type(EntityListResponse, entity, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: Tango) -> None:
        response = client.entities.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        entity = response.parse()
        assert_matches_type(EntityListResponse, entity, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: Tango) -> None:
        with client.entities.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            entity = response.parse()
            assert_matches_type(EntityListResponse, entity, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncEntities:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncTango) -> None:
        entity = await async_client.entities.retrieve(
            "uei",
        )
        assert_matches_type(EntityRetrieveResponse, entity, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncTango) -> None:
        response = await async_client.entities.with_raw_response.retrieve(
            "uei",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        entity = await response.parse()
        assert_matches_type(EntityRetrieveResponse, entity, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncTango) -> None:
        async with async_client.entities.with_streaming_response.retrieve(
            "uei",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            entity = await response.parse()
            assert_matches_type(EntityRetrieveResponse, entity, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncTango) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `uei` but received ''"):
            await async_client.entities.with_raw_response.retrieve(
                "",
            )

    @parametrize
    async def test_method_list(self, async_client: AsyncTango) -> None:
        entity = await async_client.entities.list()
        assert_matches_type(EntityListResponse, entity, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncTango) -> None:
        entity = await async_client.entities.list(
            cage_code="cage_code",
            limit=0,
            naics="naics",
            name="name",
            page=0,
            psc="psc",
            purpose_of_registration_code="purpose_of_registration_code",
            search="search",
            socioeconomic="socioeconomic",
            state="state",
            uei="uei",
            zip_code="zip_code",
        )
        assert_matches_type(EntityListResponse, entity, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncTango) -> None:
        response = await async_client.entities.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        entity = await response.parse()
        assert_matches_type(EntityListResponse, entity, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncTango) -> None:
        async with async_client.entities.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            entity = await response.parse()
            assert_matches_type(EntityListResponse, entity, path=["response"])

        assert cast(Any, response.is_closed) is True
