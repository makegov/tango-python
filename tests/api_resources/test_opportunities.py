# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tango import Tango, AsyncTango
from tango.types import OpportunityListResponse, OpportunityRetrieveResponse
from tests.utils import assert_matches_type
from tango._utils import parse_datetime

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestOpportunities:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_retrieve(self, client: Tango) -> None:
        opportunity = client.opportunities.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(OpportunityRetrieveResponse, opportunity, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: Tango) -> None:
        response = client.opportunities.with_raw_response.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        opportunity = response.parse()
        assert_matches_type(OpportunityRetrieveResponse, opportunity, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: Tango) -> None:
        with client.opportunities.with_streaming_response.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            opportunity = response.parse()
            assert_matches_type(OpportunityRetrieveResponse, opportunity, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: Tango) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `opportunity_id` but received ''"):
            client.opportunities.with_raw_response.retrieve(
                "",
            )

    @parametrize
    def test_method_list(self, client: Tango) -> None:
        opportunity = client.opportunities.list()
        assert_matches_type(OpportunityListResponse, opportunity, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: Tango) -> None:
        opportunity = client.opportunities.list(
            active=True,
            agency="agency",
            first_notice_date_after=parse_datetime("2019-12-27T18:11:19.117Z"),
            first_notice_date_before=parse_datetime("2019-12-27T18:11:19.117Z"),
            last_notice_date_after=parse_datetime("2019-12-27T18:11:19.117Z"),
            last_notice_date_before=parse_datetime("2019-12-27T18:11:19.117Z"),
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
        assert_matches_type(OpportunityListResponse, opportunity, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: Tango) -> None:
        response = client.opportunities.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        opportunity = response.parse()
        assert_matches_type(OpportunityListResponse, opportunity, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: Tango) -> None:
        with client.opportunities.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            opportunity = response.parse()
            assert_matches_type(OpportunityListResponse, opportunity, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncOpportunities:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncTango) -> None:
        opportunity = await async_client.opportunities.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(OpportunityRetrieveResponse, opportunity, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncTango) -> None:
        response = await async_client.opportunities.with_raw_response.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        opportunity = await response.parse()
        assert_matches_type(OpportunityRetrieveResponse, opportunity, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncTango) -> None:
        async with async_client.opportunities.with_streaming_response.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            opportunity = await response.parse()
            assert_matches_type(OpportunityRetrieveResponse, opportunity, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncTango) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `opportunity_id` but received ''"):
            await async_client.opportunities.with_raw_response.retrieve(
                "",
            )

    @parametrize
    async def test_method_list(self, async_client: AsyncTango) -> None:
        opportunity = await async_client.opportunities.list()
        assert_matches_type(OpportunityListResponse, opportunity, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncTango) -> None:
        opportunity = await async_client.opportunities.list(
            active=True,
            agency="agency",
            first_notice_date_after=parse_datetime("2019-12-27T18:11:19.117Z"),
            first_notice_date_before=parse_datetime("2019-12-27T18:11:19.117Z"),
            last_notice_date_after=parse_datetime("2019-12-27T18:11:19.117Z"),
            last_notice_date_before=parse_datetime("2019-12-27T18:11:19.117Z"),
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
        assert_matches_type(OpportunityListResponse, opportunity, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncTango) -> None:
        response = await async_client.opportunities.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        opportunity = await response.parse()
        assert_matches_type(OpportunityListResponse, opportunity, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncTango) -> None:
        async with async_client.opportunities.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            opportunity = await response.parse()
            assert_matches_type(OpportunityListResponse, opportunity, path=["response"])

        assert cast(Any, response.is_closed) is True
