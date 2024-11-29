# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import office_list_params
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
from ..types.office import Office
from ..types.office_list_response import OfficeListResponse

__all__ = ["OfficesResource", "AsyncOfficesResource"]


class OfficesResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> OfficesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return the
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/makegov/tango-python#accessing-raw-response-data-eg-headers
        """
        return OfficesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> OfficesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/makegov/tango-python#with_streaming_response
        """
        return OfficesResourceWithStreamingResponse(self)

    def retrieve(
        self,
        code: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Office:
        """
        API endpoint that allows offices to be viewed.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not code:
            raise ValueError(f"Expected a non-empty value for `code` but received {code!r}")
        return self._get(
            f"/api/offices/{code}/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Office,
        )

    def list(
        self,
        *,
        limit: int | NotGiven = NOT_GIVEN,
        page: int | NotGiven = NOT_GIVEN,
        search: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> OfficeListResponse:
        """
        API endpoint that allows offices to be viewed.

        Args:
          limit: Number of results to return per page.

          page: A page number within the paginated result set.

          search: Search for an office

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/api/offices/",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "limit": limit,
                        "page": page,
                        "search": search,
                    },
                    office_list_params.OfficeListParams,
                ),
            ),
            cast_to=OfficeListResponse,
        )


class AsyncOfficesResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncOfficesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return the
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/makegov/tango-python#accessing-raw-response-data-eg-headers
        """
        return AsyncOfficesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncOfficesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/makegov/tango-python#with_streaming_response
        """
        return AsyncOfficesResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        code: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Office:
        """
        API endpoint that allows offices to be viewed.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not code:
            raise ValueError(f"Expected a non-empty value for `code` but received {code!r}")
        return await self._get(
            f"/api/offices/{code}/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Office,
        )

    async def list(
        self,
        *,
        limit: int | NotGiven = NOT_GIVEN,
        page: int | NotGiven = NOT_GIVEN,
        search: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> OfficeListResponse:
        """
        API endpoint that allows offices to be viewed.

        Args:
          limit: Number of results to return per page.

          page: A page number within the paginated result set.

          search: Search for an office

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/api/offices/",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "limit": limit,
                        "page": page,
                        "search": search,
                    },
                    office_list_params.OfficeListParams,
                ),
            ),
            cast_to=OfficeListResponse,
        )


class OfficesResourceWithRawResponse:
    def __init__(self, offices: OfficesResource) -> None:
        self._offices = offices

        self.retrieve = to_raw_response_wrapper(
            offices.retrieve,
        )
        self.list = to_raw_response_wrapper(
            offices.list,
        )


class AsyncOfficesResourceWithRawResponse:
    def __init__(self, offices: AsyncOfficesResource) -> None:
        self._offices = offices

        self.retrieve = async_to_raw_response_wrapper(
            offices.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            offices.list,
        )


class OfficesResourceWithStreamingResponse:
    def __init__(self, offices: OfficesResource) -> None:
        self._offices = offices

        self.retrieve = to_streamed_response_wrapper(
            offices.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            offices.list,
        )


class AsyncOfficesResourceWithStreamingResponse:
    def __init__(self, offices: AsyncOfficesResource) -> None:
        self._offices = offices

        self.retrieve = async_to_streamed_response_wrapper(
            offices.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            offices.list,
        )
