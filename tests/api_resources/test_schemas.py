# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tango import Tango, AsyncTango
from tango.types import SchemaRetrieveResponse
from tests.utils import assert_matches_type

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestSchemas:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_retrieve(self, client: Tango) -> None:
        schema = client.schemas.retrieve()
        assert_matches_type(SchemaRetrieveResponse, schema, path=["response"])

    @parametrize
    def test_method_retrieve_with_all_params(self, client: Tango) -> None:
        schema = client.schemas.retrieve(
            format="json",
            lang="af",
        )
        assert_matches_type(SchemaRetrieveResponse, schema, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: Tango) -> None:
        response = client.schemas.with_raw_response.retrieve()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        schema = response.parse()
        assert_matches_type(SchemaRetrieveResponse, schema, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: Tango) -> None:
        with client.schemas.with_streaming_response.retrieve() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            schema = response.parse()
            assert_matches_type(SchemaRetrieveResponse, schema, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncSchemas:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncTango) -> None:
        schema = await async_client.schemas.retrieve()
        assert_matches_type(SchemaRetrieveResponse, schema, path=["response"])

    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncTango) -> None:
        schema = await async_client.schemas.retrieve(
            format="json",
            lang="af",
        )
        assert_matches_type(SchemaRetrieveResponse, schema, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncTango) -> None:
        response = await async_client.schemas.with_raw_response.retrieve()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        schema = await response.parse()
        assert_matches_type(SchemaRetrieveResponse, schema, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncTango) -> None:
        async with async_client.schemas.with_streaming_response.retrieve() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            schema = await response.parse()
            assert_matches_type(SchemaRetrieveResponse, schema, path=["response"])

        assert cast(Any, response.is_closed) is True
