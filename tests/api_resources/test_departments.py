# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tango import Tango, AsyncTango
from tango.types import Department, DepartmentListResponse
from tests.utils import assert_matches_type

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestDepartments:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_retrieve(self, client: Tango) -> None:
        department = client.departments.retrieve(
            -2147483648,
        )
        assert_matches_type(Department, department, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: Tango) -> None:
        response = client.departments.with_raw_response.retrieve(
            -2147483648,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        department = response.parse()
        assert_matches_type(Department, department, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: Tango) -> None:
        with client.departments.with_streaming_response.retrieve(
            -2147483648,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            department = response.parse()
            assert_matches_type(Department, department, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_list(self, client: Tango) -> None:
        department = client.departments.list()
        assert_matches_type(DepartmentListResponse, department, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: Tango) -> None:
        response = client.departments.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        department = response.parse()
        assert_matches_type(DepartmentListResponse, department, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: Tango) -> None:
        with client.departments.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            department = response.parse()
            assert_matches_type(DepartmentListResponse, department, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncDepartments:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncTango) -> None:
        department = await async_client.departments.retrieve(
            -2147483648,
        )
        assert_matches_type(Department, department, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncTango) -> None:
        response = await async_client.departments.with_raw_response.retrieve(
            -2147483648,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        department = await response.parse()
        assert_matches_type(Department, department, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncTango) -> None:
        async with async_client.departments.with_streaming_response.retrieve(
            -2147483648,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            department = await response.parse()
            assert_matches_type(Department, department, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_list(self, async_client: AsyncTango) -> None:
        department = await async_client.departments.list()
        assert_matches_type(DepartmentListResponse, department, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncTango) -> None:
        response = await async_client.departments.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        department = await response.parse()
        assert_matches_type(DepartmentListResponse, department, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncTango) -> None:
        async with async_client.departments.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            department = await response.parse()
            assert_matches_type(DepartmentListResponse, department, path=["response"])

        assert cast(Any, response.is_closed) is True
