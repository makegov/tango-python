# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import agency_list_params
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
from ..types.agency import Agency
from ..types.agency_list_response import AgencyListResponse

__all__ = ["AgenciesResource", "AsyncAgenciesResource"]


class AgenciesResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AgenciesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return the
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/makegov/tango-python#accessing-raw-response-data-eg-headers
        """
        return AgenciesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AgenciesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/makegov/tango-python#with_streaming_response
        """
        return AgenciesResourceWithStreamingResponse(self)

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
    ) -> Agency:
        """
        API endpoint that allows agencies lookup.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not code:
            raise ValueError(f"Expected a non-empty value for `code` but received {code!r}")
        return self._get(
            f"/api/agencies/{code}/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Agency,
        )

    def list(
        self,
        *,
        search: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AgencyListResponse:
        """
        API endpoint that allows agencies lookup.

        Args:
          search: <details><summary>Filter by </summary><ul><li>Accepts any agency or department code, acronym, or (partial) name</li><li>Disjunctive with <var>|</var> or <var>OR</var></li></ul></details>

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/api/agencies/",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"search": search}, agency_list_params.AgencyListParams),
            ),
            cast_to=AgencyListResponse,
        )


class AsyncAgenciesResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncAgenciesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return the
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/makegov/tango-python#accessing-raw-response-data-eg-headers
        """
        return AsyncAgenciesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncAgenciesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/makegov/tango-python#with_streaming_response
        """
        return AsyncAgenciesResourceWithStreamingResponse(self)

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
    ) -> Agency:
        """
        API endpoint that allows agencies lookup.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not code:
            raise ValueError(f"Expected a non-empty value for `code` but received {code!r}")
        return await self._get(
            f"/api/agencies/{code}/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Agency,
        )

    async def list(
        self,
        *,
        search: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AgencyListResponse:
        """
        API endpoint that allows agencies lookup.

        Args:
          search: <details><summary>Filter by </summary><ul><li>Accepts any agency or department code, acronym, or (partial) name</li><li>Disjunctive with <var>|</var> or <var>OR</var></li></ul></details>

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/api/agencies/",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"search": search}, agency_list_params.AgencyListParams),
            ),
            cast_to=AgencyListResponse,
        )


class AgenciesResourceWithRawResponse:
    def __init__(self, agencies: AgenciesResource) -> None:
        self._agencies = agencies

        self.retrieve = to_raw_response_wrapper(
            agencies.retrieve,
        )
        self.list = to_raw_response_wrapper(
            agencies.list,
        )


class AsyncAgenciesResourceWithRawResponse:
    def __init__(self, agencies: AsyncAgenciesResource) -> None:
        self._agencies = agencies

        self.retrieve = async_to_raw_response_wrapper(
            agencies.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            agencies.list,
        )


class AgenciesResourceWithStreamingResponse:
    def __init__(self, agencies: AgenciesResource) -> None:
        self._agencies = agencies

        self.retrieve = to_streamed_response_wrapper(
            agencies.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            agencies.list,
        )


class AsyncAgenciesResourceWithStreamingResponse:
    def __init__(self, agencies: AsyncAgenciesResource) -> None:
        self._agencies = agencies

        self.retrieve = async_to_streamed_response_wrapper(
            agencies.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            agencies.list,
        )
