# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import naic_list_params
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
from ..types.naic_list_response import NaicListResponse
from ..types.naic_retrieve_response import NaicRetrieveResponse

__all__ = ["NaicsResource", "AsyncNaicsResource"]


class NaicsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> NaicsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return the
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/makegov/tango-python#accessing-raw-response-data-eg-headers
        """
        return NaicsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> NaicsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/makegov/tango-python#with_streaming_response
        """
        return NaicsResourceWithStreamingResponse(self)

    def retrieve(
        self,
        code: int,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> NaicRetrieveResponse:
        """
        API endpoint that allows NAICS codes lookup.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            f"/api/naics/{code}/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NaicRetrieveResponse,
        )

    def list(
        self,
        *,
        employee_limit: str | NotGiven = NOT_GIVEN,
        employee_limit_gte: str | NotGiven = NOT_GIVEN,
        employee_limit_lte: str | NotGiven = NOT_GIVEN,
        revenue_limit: str | NotGiven = NOT_GIVEN,
        revenue_limit_gte: str | NotGiven = NOT_GIVEN,
        revenue_limit_lte: str | NotGiven = NOT_GIVEN,
        search: str | NotGiven = NOT_GIVEN,
        show_limits: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> NaicListResponse:
        """
        API endpoint that allows NAICS codes lookup.

        Args:
          employee_limit: <details><summary>Filter by employee limit</summary><ul><li><span>Accepted values: <var>100</var>, <var>750</var>, <var>1500</var></span></li></ul></details>

          employee_limit_gte: <details><summary>Filter by employee limit</summary><ul><li><span>Accepted values: <var>100</var>, <var>750</var>, <var>1500</var></span></li></ul></details>

          employee_limit_lte: <details><summary>Filter by employee limit</summary><ul><li><span>Accepted values: <var>100</var>, <var>750</var>, <var>1500</var></span></li></ul></details>

          revenue_limit: <details><summary>Filter by revenue limit</summary><ul><li><span>Accepted values: <var>20000000</var>, <var>50000000</var></span></li></ul></details>

          revenue_limit_gte: <details><summary>Filter by revenue limit</summary><ul><li><span>Accepted values: <var>20000000</var>, <var>50000000</var></span></li></ul></details>

          revenue_limit_lte: <details><summary>Filter by revenue limit</summary><ul><li><span>Accepted values: <var>20000000</var>, <var>50000000</var></span></li></ul></details>

          search: <details><summary>Filter by code or description</summary><ul><li><span>Accepted values: <var>111110</var>, <var>111</var>, <var>forestry</var></span></li></ul></details>

          show_limits: If included, size standards will be included in the response

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/api/naics/",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "employee_limit": employee_limit,
                        "employee_limit_gte": employee_limit_gte,
                        "employee_limit_lte": employee_limit_lte,
                        "revenue_limit": revenue_limit,
                        "revenue_limit_gte": revenue_limit_gte,
                        "revenue_limit_lte": revenue_limit_lte,
                        "search": search,
                        "show_limits": show_limits,
                    },
                    naic_list_params.NaicListParams,
                ),
            ),
            cast_to=NaicListResponse,
        )


class AsyncNaicsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncNaicsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return the
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/makegov/tango-python#accessing-raw-response-data-eg-headers
        """
        return AsyncNaicsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncNaicsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/makegov/tango-python#with_streaming_response
        """
        return AsyncNaicsResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        code: int,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> NaicRetrieveResponse:
        """
        API endpoint that allows NAICS codes lookup.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            f"/api/naics/{code}/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NaicRetrieveResponse,
        )

    async def list(
        self,
        *,
        employee_limit: str | NotGiven = NOT_GIVEN,
        employee_limit_gte: str | NotGiven = NOT_GIVEN,
        employee_limit_lte: str | NotGiven = NOT_GIVEN,
        revenue_limit: str | NotGiven = NOT_GIVEN,
        revenue_limit_gte: str | NotGiven = NOT_GIVEN,
        revenue_limit_lte: str | NotGiven = NOT_GIVEN,
        search: str | NotGiven = NOT_GIVEN,
        show_limits: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> NaicListResponse:
        """
        API endpoint that allows NAICS codes lookup.

        Args:
          employee_limit: <details><summary>Filter by employee limit</summary><ul><li><span>Accepted values: <var>100</var>, <var>750</var>, <var>1500</var></span></li></ul></details>

          employee_limit_gte: <details><summary>Filter by employee limit</summary><ul><li><span>Accepted values: <var>100</var>, <var>750</var>, <var>1500</var></span></li></ul></details>

          employee_limit_lte: <details><summary>Filter by employee limit</summary><ul><li><span>Accepted values: <var>100</var>, <var>750</var>, <var>1500</var></span></li></ul></details>

          revenue_limit: <details><summary>Filter by revenue limit</summary><ul><li><span>Accepted values: <var>20000000</var>, <var>50000000</var></span></li></ul></details>

          revenue_limit_gte: <details><summary>Filter by revenue limit</summary><ul><li><span>Accepted values: <var>20000000</var>, <var>50000000</var></span></li></ul></details>

          revenue_limit_lte: <details><summary>Filter by revenue limit</summary><ul><li><span>Accepted values: <var>20000000</var>, <var>50000000</var></span></li></ul></details>

          search: <details><summary>Filter by code or description</summary><ul><li><span>Accepted values: <var>111110</var>, <var>111</var>, <var>forestry</var></span></li></ul></details>

          show_limits: If included, size standards will be included in the response

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/api/naics/",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "employee_limit": employee_limit,
                        "employee_limit_gte": employee_limit_gte,
                        "employee_limit_lte": employee_limit_lte,
                        "revenue_limit": revenue_limit,
                        "revenue_limit_gte": revenue_limit_gte,
                        "revenue_limit_lte": revenue_limit_lte,
                        "search": search,
                        "show_limits": show_limits,
                    },
                    naic_list_params.NaicListParams,
                ),
            ),
            cast_to=NaicListResponse,
        )


class NaicsResourceWithRawResponse:
    def __init__(self, naics: NaicsResource) -> None:
        self._naics = naics

        self.retrieve = to_raw_response_wrapper(
            naics.retrieve,
        )
        self.list = to_raw_response_wrapper(
            naics.list,
        )


class AsyncNaicsResourceWithRawResponse:
    def __init__(self, naics: AsyncNaicsResource) -> None:
        self._naics = naics

        self.retrieve = async_to_raw_response_wrapper(
            naics.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            naics.list,
        )


class NaicsResourceWithStreamingResponse:
    def __init__(self, naics: NaicsResource) -> None:
        self._naics = naics

        self.retrieve = to_streamed_response_wrapper(
            naics.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            naics.list,
        )


class AsyncNaicsResourceWithStreamingResponse:
    def __init__(self, naics: AsyncNaicsResource) -> None:
        self._naics = naics

        self.retrieve = async_to_streamed_response_wrapper(
            naics.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            naics.list,
        )
