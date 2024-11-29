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
from ..types.department import Department
from ..types.department_list_response import DepartmentListResponse

__all__ = ["DepartmentsResource", "AsyncDepartmentsResource"]


class DepartmentsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> DepartmentsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return the
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/makegov/tango-python#accessing-raw-response-data-eg-headers
        """
        return DepartmentsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> DepartmentsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/makegov/tango-python#with_streaming_response
        """
        return DepartmentsResourceWithStreamingResponse(self)

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
    ) -> Department:
        """
        API endpoint that allows departments to be viewed.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            f"/api/departments/{code}/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Department,
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
    ) -> DepartmentListResponse:
        """API endpoint that allows departments to be viewed."""
        return self._get(
            "/api/departments/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DepartmentListResponse,
        )


class AsyncDepartmentsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncDepartmentsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return the
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/makegov/tango-python#accessing-raw-response-data-eg-headers
        """
        return AsyncDepartmentsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncDepartmentsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/makegov/tango-python#with_streaming_response
        """
        return AsyncDepartmentsResourceWithStreamingResponse(self)

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
    ) -> Department:
        """
        API endpoint that allows departments to be viewed.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            f"/api/departments/{code}/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Department,
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
    ) -> DepartmentListResponse:
        """API endpoint that allows departments to be viewed."""
        return await self._get(
            "/api/departments/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DepartmentListResponse,
        )


class DepartmentsResourceWithRawResponse:
    def __init__(self, departments: DepartmentsResource) -> None:
        self._departments = departments

        self.retrieve = to_raw_response_wrapper(
            departments.retrieve,
        )
        self.list = to_raw_response_wrapper(
            departments.list,
        )


class AsyncDepartmentsResourceWithRawResponse:
    def __init__(self, departments: AsyncDepartmentsResource) -> None:
        self._departments = departments

        self.retrieve = async_to_raw_response_wrapper(
            departments.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            departments.list,
        )


class DepartmentsResourceWithStreamingResponse:
    def __init__(self, departments: DepartmentsResource) -> None:
        self._departments = departments

        self.retrieve = to_streamed_response_wrapper(
            departments.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            departments.list,
        )


class AsyncDepartmentsResourceWithStreamingResponse:
    def __init__(self, departments: AsyncDepartmentsResource) -> None:
        self._departments = departments

        self.retrieve = async_to_streamed_response_wrapper(
            departments.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            departments.list,
        )
