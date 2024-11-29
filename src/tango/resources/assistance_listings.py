# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.assistance_listing_list_response import AssistanceListingListResponse
from ..types.assistance_listing_retrieve_response import AssistanceListingRetrieveResponse

__all__ = ["AssistanceListingsResource", "AsyncAssistanceListingsResource"]


class AssistanceListingsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AssistanceListingsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return the
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/makegov/tango-python#accessing-raw-response-data-eg-headers
        """
        return AssistanceListingsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AssistanceListingsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/makegov/tango-python#with_streaming_response
        """
        return AssistanceListingsResourceWithStreamingResponse(self)

    def retrieve(
        self,
        number: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AssistanceListingRetrieveResponse:
        """
        API endpoint that allows Assistance Listing to be viewed.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not number:
            raise ValueError(f"Expected a non-empty value for `number` but received {number!r}")
        return self._get(
            f"/api/assistance_listings/{number}/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AssistanceListingRetrieveResponse,
        )

    def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AssistanceListingListResponse:
        """API endpoint that allows Assistance Listing to be viewed."""
        return self._get(
            "/api/assistance_listings/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AssistanceListingListResponse,
        )


class AsyncAssistanceListingsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncAssistanceListingsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return the
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/makegov/tango-python#accessing-raw-response-data-eg-headers
        """
        return AsyncAssistanceListingsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncAssistanceListingsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/makegov/tango-python#with_streaming_response
        """
        return AsyncAssistanceListingsResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        number: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AssistanceListingRetrieveResponse:
        """
        API endpoint that allows Assistance Listing to be viewed.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not number:
            raise ValueError(f"Expected a non-empty value for `number` but received {number!r}")
        return await self._get(
            f"/api/assistance_listings/{number}/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AssistanceListingRetrieveResponse,
        )

    async def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AssistanceListingListResponse:
        """API endpoint that allows Assistance Listing to be viewed."""
        return await self._get(
            "/api/assistance_listings/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AssistanceListingListResponse,
        )


class AssistanceListingsResourceWithRawResponse:
    def __init__(self, assistance_listings: AssistanceListingsResource) -> None:
        self._assistance_listings = assistance_listings

        self.retrieve = to_raw_response_wrapper(
            assistance_listings.retrieve,
        )
        self.list = to_raw_response_wrapper(
            assistance_listings.list,
        )


class AsyncAssistanceListingsResourceWithRawResponse:
    def __init__(self, assistance_listings: AsyncAssistanceListingsResource) -> None:
        self._assistance_listings = assistance_listings

        self.retrieve = async_to_raw_response_wrapper(
            assistance_listings.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            assistance_listings.list,
        )


class AssistanceListingsResourceWithStreamingResponse:
    def __init__(self, assistance_listings: AssistanceListingsResource) -> None:
        self._assistance_listings = assistance_listings

        self.retrieve = to_streamed_response_wrapper(
            assistance_listings.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            assistance_listings.list,
        )


class AsyncAssistanceListingsResourceWithStreamingResponse:
    def __init__(self, assistance_listings: AsyncAssistanceListingsResource) -> None:
        self._assistance_listings = assistance_listings

        self.retrieve = async_to_streamed_response_wrapper(
            assistance_listings.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            assistance_listings.list,
        )
