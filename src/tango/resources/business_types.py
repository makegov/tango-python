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
from ..types.business_type import BusinessType
from ..types.business_type_list_response import BusinessTypeListResponse

__all__ = ["BusinessTypesResource", "AsyncBusinessTypesResource"]


class BusinessTypesResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> BusinessTypesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return the
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/makegov/tango-python#accessing-raw-response-data-eg-headers
        """
        return BusinessTypesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> BusinessTypesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/makegov/tango-python#with_streaming_response
        """
        return BusinessTypesResourceWithStreamingResponse(self)

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
    ) -> BusinessType:
        """
        API endpoint that allows Business Types to be viewed.

        Args:
          code: The SAM code for the business type

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not code:
            raise ValueError(f"Expected a non-empty value for `code` but received {code!r}")
        return self._get(
            f"/api/business_types/{code}/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BusinessType,
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
    ) -> BusinessTypeListResponse:
        """API endpoint that allows Business Types to be viewed."""
        return self._get(
            "/api/business_types/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BusinessTypeListResponse,
        )


class AsyncBusinessTypesResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncBusinessTypesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return the
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/makegov/tango-python#accessing-raw-response-data-eg-headers
        """
        return AsyncBusinessTypesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncBusinessTypesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/makegov/tango-python#with_streaming_response
        """
        return AsyncBusinessTypesResourceWithStreamingResponse(self)

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
    ) -> BusinessType:
        """
        API endpoint that allows Business Types to be viewed.

        Args:
          code: The SAM code for the business type

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not code:
            raise ValueError(f"Expected a non-empty value for `code` but received {code!r}")
        return await self._get(
            f"/api/business_types/{code}/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BusinessType,
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
    ) -> BusinessTypeListResponse:
        """API endpoint that allows Business Types to be viewed."""
        return await self._get(
            "/api/business_types/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BusinessTypeListResponse,
        )


class BusinessTypesResourceWithRawResponse:
    def __init__(self, business_types: BusinessTypesResource) -> None:
        self._business_types = business_types

        self.retrieve = to_raw_response_wrapper(
            business_types.retrieve,
        )
        self.list = to_raw_response_wrapper(
            business_types.list,
        )


class AsyncBusinessTypesResourceWithRawResponse:
    def __init__(self, business_types: AsyncBusinessTypesResource) -> None:
        self._business_types = business_types

        self.retrieve = async_to_raw_response_wrapper(
            business_types.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            business_types.list,
        )


class BusinessTypesResourceWithStreamingResponse:
    def __init__(self, business_types: BusinessTypesResource) -> None:
        self._business_types = business_types

        self.retrieve = to_streamed_response_wrapper(
            business_types.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            business_types.list,
        )


class AsyncBusinessTypesResourceWithStreamingResponse:
    def __init__(self, business_types: AsyncBusinessTypesResource) -> None:
        self._business_types = business_types

        self.retrieve = async_to_streamed_response_wrapper(
            business_types.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            business_types.list,
        )
