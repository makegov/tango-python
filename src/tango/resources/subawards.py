# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import subaward_list_params
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._utils import (
    maybe_transform,
    async_maybe_transform,
)
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.subaward import Subaward
from ..types.subaward_list_response import SubawardListResponse

__all__ = ["SubawardsResource", "AsyncSubawardsResource"]


class SubawardsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> SubawardsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return the
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/makegov/tango-python#accessing-raw-response-data-eg-headers
        """
        return SubawardsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> SubawardsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/makegov/tango-python#with_streaming_response
        """
        return SubawardsResourceWithStreamingResponse(self)

    def retrieve(
        self,
        id: int,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Subaward:
        """
        API endpoint that allows subaward lookup.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            f"/api/subawards/{id}/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Subaward,
        )

    def list(
        self,
        *,
        awarding_agency: str | NotGiven = NOT_GIVEN,
        fiscal_year: int | NotGiven = NOT_GIVEN,
        fiscal_year_gte: int | NotGiven = NOT_GIVEN,
        fiscal_year_lte: int | NotGiven = NOT_GIVEN,
        funding_agency: str | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        page: int | NotGiven = NOT_GIVEN,
        prime_uei: str | NotGiven = NOT_GIVEN,
        sub_uei: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SubawardListResponse:
        """
        API endpoint that allows subaward lookup.

        Args:
          awarding_agency: Awarding agency code

          funding_agency: Awarding agency code

          limit: Number of results to return per page.

          page: A page number within the paginated result set.

          prime_uei: Unique Entity Identifier

          sub_uei: Unique Entity Identifier

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/api/subawards/",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "awarding_agency": awarding_agency,
                        "fiscal_year": fiscal_year,
                        "fiscal_year_gte": fiscal_year_gte,
                        "fiscal_year_lte": fiscal_year_lte,
                        "funding_agency": funding_agency,
                        "limit": limit,
                        "page": page,
                        "prime_uei": prime_uei,
                        "sub_uei": sub_uei,
                    },
                    subaward_list_params.SubawardListParams,
                ),
            ),
            cast_to=SubawardListResponse,
        )


class AsyncSubawardsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncSubawardsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return the
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/makegov/tango-python#accessing-raw-response-data-eg-headers
        """
        return AsyncSubawardsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncSubawardsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/makegov/tango-python#with_streaming_response
        """
        return AsyncSubawardsResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        id: int,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Subaward:
        """
        API endpoint that allows subaward lookup.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            f"/api/subawards/{id}/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Subaward,
        )

    async def list(
        self,
        *,
        awarding_agency: str | NotGiven = NOT_GIVEN,
        fiscal_year: int | NotGiven = NOT_GIVEN,
        fiscal_year_gte: int | NotGiven = NOT_GIVEN,
        fiscal_year_lte: int | NotGiven = NOT_GIVEN,
        funding_agency: str | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        page: int | NotGiven = NOT_GIVEN,
        prime_uei: str | NotGiven = NOT_GIVEN,
        sub_uei: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SubawardListResponse:
        """
        API endpoint that allows subaward lookup.

        Args:
          awarding_agency: Awarding agency code

          funding_agency: Awarding agency code

          limit: Number of results to return per page.

          page: A page number within the paginated result set.

          prime_uei: Unique Entity Identifier

          sub_uei: Unique Entity Identifier

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/api/subawards/",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "awarding_agency": awarding_agency,
                        "fiscal_year": fiscal_year,
                        "fiscal_year_gte": fiscal_year_gte,
                        "fiscal_year_lte": fiscal_year_lte,
                        "funding_agency": funding_agency,
                        "limit": limit,
                        "page": page,
                        "prime_uei": prime_uei,
                        "sub_uei": sub_uei,
                    },
                    subaward_list_params.SubawardListParams,
                ),
            ),
            cast_to=SubawardListResponse,
        )


class SubawardsResourceWithRawResponse:
    def __init__(self, subawards: SubawardsResource) -> None:
        self._subawards = subawards

        self.retrieve = to_raw_response_wrapper(
            subawards.retrieve,
        )
        self.list = to_raw_response_wrapper(
            subawards.list,
        )


class AsyncSubawardsResourceWithRawResponse:
    def __init__(self, subawards: AsyncSubawardsResource) -> None:
        self._subawards = subawards

        self.retrieve = async_to_raw_response_wrapper(
            subawards.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            subawards.list,
        )


class SubawardsResourceWithStreamingResponse:
    def __init__(self, subawards: SubawardsResource) -> None:
        self._subawards = subawards

        self.retrieve = to_streamed_response_wrapper(
            subawards.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            subawards.list,
        )


class AsyncSubawardsResourceWithStreamingResponse:
    def __init__(self, subawards: AsyncSubawardsResource) -> None:
        self._subawards = subawards

        self.retrieve = async_to_streamed_response_wrapper(
            subawards.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            subawards.list,
        )
