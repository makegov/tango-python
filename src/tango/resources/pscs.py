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
from ..types.psc_list_response import PscListResponse
from ..types.product_service_code import ProductServiceCode

__all__ = ["PscsResource", "AsyncPscsResource"]


class PscsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> PscsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return the
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/makegov/tango-python#accessing-raw-response-data-eg-headers
        """
        return PscsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> PscsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/makegov/tango-python#with_streaming_response
        """
        return PscsResourceWithStreamingResponse(self)

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
    ) -> ProductServiceCode:
        """
        API endpoint that allows PSC codes to be viewed.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            f"/api/psc/{id}/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ProductServiceCode,
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
    ) -> PscListResponse:
        """API endpoint that allows PSC codes to be viewed."""
        return self._get(
            "/api/psc/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PscListResponse,
        )


class AsyncPscsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncPscsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return the
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/makegov/tango-python#accessing-raw-response-data-eg-headers
        """
        return AsyncPscsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncPscsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/makegov/tango-python#with_streaming_response
        """
        return AsyncPscsResourceWithStreamingResponse(self)

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
    ) -> ProductServiceCode:
        """
        API endpoint that allows PSC codes to be viewed.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            f"/api/psc/{id}/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ProductServiceCode,
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
    ) -> PscListResponse:
        """API endpoint that allows PSC codes to be viewed."""
        return await self._get(
            "/api/psc/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PscListResponse,
        )


class PscsResourceWithRawResponse:
    def __init__(self, pscs: PscsResource) -> None:
        self._pscs = pscs

        self.retrieve = to_raw_response_wrapper(
            pscs.retrieve,
        )
        self.list = to_raw_response_wrapper(
            pscs.list,
        )


class AsyncPscsResourceWithRawResponse:
    def __init__(self, pscs: AsyncPscsResource) -> None:
        self._pscs = pscs

        self.retrieve = async_to_raw_response_wrapper(
            pscs.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            pscs.list,
        )


class PscsResourceWithStreamingResponse:
    def __init__(self, pscs: PscsResource) -> None:
        self._pscs = pscs

        self.retrieve = to_streamed_response_wrapper(
            pscs.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            pscs.list,
        )


class AsyncPscsResourceWithStreamingResponse:
    def __init__(self, pscs: AsyncPscsResource) -> None:
        self._pscs = pscs

        self.retrieve = async_to_streamed_response_wrapper(
            pscs.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            pscs.list,
        )
