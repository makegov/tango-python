# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tango import Tango, AsyncTango
from tango.types import NoticeListResponse, NoticeRetrieveResponse
from tests.utils import assert_matches_type

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestNotices:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_retrieve(self, client: Tango) -> None:
        notice = client.notices.retrieve(
            "notice_id",
        )
        assert_matches_type(NoticeRetrieveResponse, notice, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: Tango) -> None:
        response = client.notices.with_raw_response.retrieve(
            "notice_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        notice = response.parse()
        assert_matches_type(NoticeRetrieveResponse, notice, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: Tango) -> None:
        with client.notices.with_streaming_response.retrieve(
            "notice_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            notice = response.parse()
            assert_matches_type(NoticeRetrieveResponse, notice, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: Tango) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `notice_id` but received ''"):
            client.notices.with_raw_response.retrieve(
                "",
            )

    @parametrize
    def test_method_list(self, client: Tango) -> None:
        notice = client.notices.list()
        assert_matches_type(NoticeListResponse, notice, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: Tango) -> None:
        notice = client.notices.list(
            active=True,
            agency="agency",
            limit=0,
            naics="naics",
            notice_type="notice_type",
            ordering="ordering",
            page=0,
            place_of_performance="place_of_performance",
            posted_date_after="posted_date_after",
            posted_date_before="posted_date_before",
            psc="psc",
            response_deadline_after="response_deadline_after",
            response_deadline_before="response_deadline_before",
            search="search",
            set_aside="set_aside",
            solicitation_number="solicitation_number",
        )
        assert_matches_type(NoticeListResponse, notice, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: Tango) -> None:
        response = client.notices.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        notice = response.parse()
        assert_matches_type(NoticeListResponse, notice, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: Tango) -> None:
        with client.notices.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            notice = response.parse()
            assert_matches_type(NoticeListResponse, notice, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncNotices:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncTango) -> None:
        notice = await async_client.notices.retrieve(
            "notice_id",
        )
        assert_matches_type(NoticeRetrieveResponse, notice, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncTango) -> None:
        response = await async_client.notices.with_raw_response.retrieve(
            "notice_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        notice = await response.parse()
        assert_matches_type(NoticeRetrieveResponse, notice, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncTango) -> None:
        async with async_client.notices.with_streaming_response.retrieve(
            "notice_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            notice = await response.parse()
            assert_matches_type(NoticeRetrieveResponse, notice, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncTango) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `notice_id` but received ''"):
            await async_client.notices.with_raw_response.retrieve(
                "",
            )

    @parametrize
    async def test_method_list(self, async_client: AsyncTango) -> None:
        notice = await async_client.notices.list()
        assert_matches_type(NoticeListResponse, notice, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncTango) -> None:
        notice = await async_client.notices.list(
            active=True,
            agency="agency",
            limit=0,
            naics="naics",
            notice_type="notice_type",
            ordering="ordering",
            page=0,
            place_of_performance="place_of_performance",
            posted_date_after="posted_date_after",
            posted_date_before="posted_date_before",
            psc="psc",
            response_deadline_after="response_deadline_after",
            response_deadline_before="response_deadline_before",
            search="search",
            set_aside="set_aside",
            solicitation_number="solicitation_number",
        )
        assert_matches_type(NoticeListResponse, notice, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncTango) -> None:
        response = await async_client.notices.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        notice = await response.parse()
        assert_matches_type(NoticeListResponse, notice, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncTango) -> None:
        async with async_client.notices.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            notice = await response.parse()
            assert_matches_type(NoticeListResponse, notice, path=["response"])

        assert cast(Any, response.is_closed) is True
