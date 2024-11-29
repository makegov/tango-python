# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from datetime import datetime

import httpx

from ..types import opportunity_list_params
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
from ..types.opportunity_list_response import OpportunityListResponse
from ..types.opportunity_retrieve_response import OpportunityRetrieveResponse

__all__ = ["OpportunitiesResource", "AsyncOpportunitiesResource"]


class OpportunitiesResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> OpportunitiesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return the
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/makegov/tango-python#accessing-raw-response-data-eg-headers
        """
        return OpportunitiesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> OpportunitiesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/makegov/tango-python#with_streaming_response
        """
        return OpportunitiesResourceWithStreamingResponse(self)

    def retrieve(
        self,
        opportunity_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> OpportunityRetrieveResponse:
        """
        API endpoint that allows opportunities lookup.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not opportunity_id:
            raise ValueError(f"Expected a non-empty value for `opportunity_id` but received {opportunity_id!r}")
        return self._get(
            f"/api/opportunities/{opportunity_id}/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=OpportunityRetrieveResponse,
        )

    def list(
        self,
        *,
        active: bool | NotGiven = NOT_GIVEN,
        agency: str | NotGiven = NOT_GIVEN,
        first_notice_date_after: Union[str, datetime] | NotGiven = NOT_GIVEN,
        first_notice_date_before: Union[str, datetime] | NotGiven = NOT_GIVEN,
        last_notice_date_after: Union[str, datetime] | NotGiven = NOT_GIVEN,
        last_notice_date_before: Union[str, datetime] | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        naics: str | NotGiven = NOT_GIVEN,
        notice_type: str | NotGiven = NOT_GIVEN,
        ordering: str | NotGiven = NOT_GIVEN,
        page: int | NotGiven = NOT_GIVEN,
        place_of_performance: str | NotGiven = NOT_GIVEN,
        posted_date_after: str | NotGiven = NOT_GIVEN,
        posted_date_before: str | NotGiven = NOT_GIVEN,
        psc: str | NotGiven = NOT_GIVEN,
        response_deadline_after: str | NotGiven = NOT_GIVEN,
        response_deadline_before: str | NotGiven = NOT_GIVEN,
        search: str | NotGiven = NOT_GIVEN,
        set_aside: str | NotGiven = NOT_GIVEN,
        solicitation_number: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> OpportunityListResponse:
        """
        API endpoint that allows opportunities lookup.

        Args:
          active: Filter active and inactive

          agency: <details><summary>Filter by agency</summary><ul><li>Accepts any agency or department code, acronym, or (partial) name</li><li>Disjunctive with <var>|</var> or <var>OR</var></li></ul></details>

          first_notice_date_after: Filter by the first notice date

          first_notice_date_before: Filter by the first notice date

          last_notice_date_after: Filter by the last notice date

          last_notice_date_before: Filter by the last notice date

          limit: Number of results to return per page.

          naics: <details><summary>Filter by NAICS Code</summary><ul><li><span>Accepted values: <var>541511</var>, <var>541512</var>, <var>etc.</var></span></li><li>Disjunctive with <var>|</var> or <var>OR</var></li></ul></details>

          notice_type: <details><summary>Filter by notice type</summary><ul><li><span>Accepted values: <var>a</var>, <var>g</var>, <var>f</var>, <var>i</var>, <var>j</var>, <var>k</var>, <var>l</var>, <var>m</var>, <var>o</var>, <var>p</var>, <var>r</var>, <var>s</var>, <var>u</var></span></li><li>Disjunctive with <var>|</var> or <var>OR</var></li></ul></details>

          ordering: <details><summary>Order results by a field of your choice.</summary><ul><li><span>Accepted values: <var>last_updated</var>, <var>posted_date</var>, <var>response_deadline</var></span></li><li>Prefix with <var>-</var> to reverse order (e.g. <var>-last_updated</var>)</li></ul></details>

          page: A page number within the paginated result set.

          place_of_performance: <details><summary>Filter by place of performance</summary><ul><li>Accepts cities, states, zip codes, and 3-character country codes</li><li>Disjunctive with <var>|</var> or <var>OR</var></li></ul></details>

          posted_date_after: <details><summary>Filter by posted date</summary><ul><li><span>Accepted values: <var>2024-08-01</var></span></li></ul></details>

          posted_date_before: <details><summary>Filter by posted date</summary><ul><li><span>Accepted values: <var>2024-08-01</var></span></li></ul></details>

          psc: <details><summary>Filter by PSC (Product Service Code)</summary><ul><li><span>Accepted values: <var>S222</var>, <var>T005</var>, <var>etc.</var></span></li><li>Disjunctive with <var>|</var> or <var>OR</var></li></ul></details>

          response_deadline_after: <details><summary>Filter by response deadline</summary><ul><li><span>Accepted values: <var>2024-08-01</var></span></li></ul></details>

          response_deadline_before: <details><summary>Filter by response deadline</summary><ul><li><span>Accepted values: <var>2024-08-01</var></span></li></ul></details>

          search: <details><summary>Search within a notice/opportunity's title, description, or solicitation number</summary><ul><li>Disjunctive with <var>|</var> or <var>OR</var></li><li>Conjunctive with <var>,</var> or <var>AND</var></li><li>Accepts phrases with <var>"</var></li></ul></details>

          set_aside: <details><summary>Filter by set-aside type</summary><ul><li><span>Accepted values: <var>8A</var>, <var>8AN</var>, <var>BICiv</var>, <var>EDWOSB</var>, <var>EDWOSBSS</var>, <var>HUBZONE</var>, <var>HZC</var>, <var>HZS</var>, <var>IEE</var>, <var>ISBEE</var>, <var>LAS</var>, <var>NONE</var>, <var>SB</var>, <var>SBA</var>, <var>SBP</var>, <var>SDB</var>, <var>SDVOSB</var>, <var>SDVOSBC</var>, <var>SDVOSBS</var>, <var>VOSB</var>, <var>VSA</var>, <var>VSS</var>, <var>WOSB</var>, <var>WOSBSS</var></span></li><li>Disjunctive with <var>|</var> or <var>OR</var></li></ul></details>

          solicitation_number: Search by solicitation number

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/api/opportunities/",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "active": active,
                        "agency": agency,
                        "first_notice_date_after": first_notice_date_after,
                        "first_notice_date_before": first_notice_date_before,
                        "last_notice_date_after": last_notice_date_after,
                        "last_notice_date_before": last_notice_date_before,
                        "limit": limit,
                        "naics": naics,
                        "notice_type": notice_type,
                        "ordering": ordering,
                        "page": page,
                        "place_of_performance": place_of_performance,
                        "posted_date_after": posted_date_after,
                        "posted_date_before": posted_date_before,
                        "psc": psc,
                        "response_deadline_after": response_deadline_after,
                        "response_deadline_before": response_deadline_before,
                        "search": search,
                        "set_aside": set_aside,
                        "solicitation_number": solicitation_number,
                    },
                    opportunity_list_params.OpportunityListParams,
                ),
            ),
            cast_to=OpportunityListResponse,
        )


class AsyncOpportunitiesResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncOpportunitiesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return the
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/makegov/tango-python#accessing-raw-response-data-eg-headers
        """
        return AsyncOpportunitiesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncOpportunitiesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/makegov/tango-python#with_streaming_response
        """
        return AsyncOpportunitiesResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        opportunity_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> OpportunityRetrieveResponse:
        """
        API endpoint that allows opportunities lookup.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not opportunity_id:
            raise ValueError(f"Expected a non-empty value for `opportunity_id` but received {opportunity_id!r}")
        return await self._get(
            f"/api/opportunities/{opportunity_id}/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=OpportunityRetrieveResponse,
        )

    async def list(
        self,
        *,
        active: bool | NotGiven = NOT_GIVEN,
        agency: str | NotGiven = NOT_GIVEN,
        first_notice_date_after: Union[str, datetime] | NotGiven = NOT_GIVEN,
        first_notice_date_before: Union[str, datetime] | NotGiven = NOT_GIVEN,
        last_notice_date_after: Union[str, datetime] | NotGiven = NOT_GIVEN,
        last_notice_date_before: Union[str, datetime] | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        naics: str | NotGiven = NOT_GIVEN,
        notice_type: str | NotGiven = NOT_GIVEN,
        ordering: str | NotGiven = NOT_GIVEN,
        page: int | NotGiven = NOT_GIVEN,
        place_of_performance: str | NotGiven = NOT_GIVEN,
        posted_date_after: str | NotGiven = NOT_GIVEN,
        posted_date_before: str | NotGiven = NOT_GIVEN,
        psc: str | NotGiven = NOT_GIVEN,
        response_deadline_after: str | NotGiven = NOT_GIVEN,
        response_deadline_before: str | NotGiven = NOT_GIVEN,
        search: str | NotGiven = NOT_GIVEN,
        set_aside: str | NotGiven = NOT_GIVEN,
        solicitation_number: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> OpportunityListResponse:
        """
        API endpoint that allows opportunities lookup.

        Args:
          active: Filter active and inactive

          agency: <details><summary>Filter by agency</summary><ul><li>Accepts any agency or department code, acronym, or (partial) name</li><li>Disjunctive with <var>|</var> or <var>OR</var></li></ul></details>

          first_notice_date_after: Filter by the first notice date

          first_notice_date_before: Filter by the first notice date

          last_notice_date_after: Filter by the last notice date

          last_notice_date_before: Filter by the last notice date

          limit: Number of results to return per page.

          naics: <details><summary>Filter by NAICS Code</summary><ul><li><span>Accepted values: <var>541511</var>, <var>541512</var>, <var>etc.</var></span></li><li>Disjunctive with <var>|</var> or <var>OR</var></li></ul></details>

          notice_type: <details><summary>Filter by notice type</summary><ul><li><span>Accepted values: <var>a</var>, <var>g</var>, <var>f</var>, <var>i</var>, <var>j</var>, <var>k</var>, <var>l</var>, <var>m</var>, <var>o</var>, <var>p</var>, <var>r</var>, <var>s</var>, <var>u</var></span></li><li>Disjunctive with <var>|</var> or <var>OR</var></li></ul></details>

          ordering: <details><summary>Order results by a field of your choice.</summary><ul><li><span>Accepted values: <var>last_updated</var>, <var>posted_date</var>, <var>response_deadline</var></span></li><li>Prefix with <var>-</var> to reverse order (e.g. <var>-last_updated</var>)</li></ul></details>

          page: A page number within the paginated result set.

          place_of_performance: <details><summary>Filter by place of performance</summary><ul><li>Accepts cities, states, zip codes, and 3-character country codes</li><li>Disjunctive with <var>|</var> or <var>OR</var></li></ul></details>

          posted_date_after: <details><summary>Filter by posted date</summary><ul><li><span>Accepted values: <var>2024-08-01</var></span></li></ul></details>

          posted_date_before: <details><summary>Filter by posted date</summary><ul><li><span>Accepted values: <var>2024-08-01</var></span></li></ul></details>

          psc: <details><summary>Filter by PSC (Product Service Code)</summary><ul><li><span>Accepted values: <var>S222</var>, <var>T005</var>, <var>etc.</var></span></li><li>Disjunctive with <var>|</var> or <var>OR</var></li></ul></details>

          response_deadline_after: <details><summary>Filter by response deadline</summary><ul><li><span>Accepted values: <var>2024-08-01</var></span></li></ul></details>

          response_deadline_before: <details><summary>Filter by response deadline</summary><ul><li><span>Accepted values: <var>2024-08-01</var></span></li></ul></details>

          search: <details><summary>Search within a notice/opportunity's title, description, or solicitation number</summary><ul><li>Disjunctive with <var>|</var> or <var>OR</var></li><li>Conjunctive with <var>,</var> or <var>AND</var></li><li>Accepts phrases with <var>"</var></li></ul></details>

          set_aside: <details><summary>Filter by set-aside type</summary><ul><li><span>Accepted values: <var>8A</var>, <var>8AN</var>, <var>BICiv</var>, <var>EDWOSB</var>, <var>EDWOSBSS</var>, <var>HUBZONE</var>, <var>HZC</var>, <var>HZS</var>, <var>IEE</var>, <var>ISBEE</var>, <var>LAS</var>, <var>NONE</var>, <var>SB</var>, <var>SBA</var>, <var>SBP</var>, <var>SDB</var>, <var>SDVOSB</var>, <var>SDVOSBC</var>, <var>SDVOSBS</var>, <var>VOSB</var>, <var>VSA</var>, <var>VSS</var>, <var>WOSB</var>, <var>WOSBSS</var></span></li><li>Disjunctive with <var>|</var> or <var>OR</var></li></ul></details>

          solicitation_number: Search by solicitation number

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/api/opportunities/",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "active": active,
                        "agency": agency,
                        "first_notice_date_after": first_notice_date_after,
                        "first_notice_date_before": first_notice_date_before,
                        "last_notice_date_after": last_notice_date_after,
                        "last_notice_date_before": last_notice_date_before,
                        "limit": limit,
                        "naics": naics,
                        "notice_type": notice_type,
                        "ordering": ordering,
                        "page": page,
                        "place_of_performance": place_of_performance,
                        "posted_date_after": posted_date_after,
                        "posted_date_before": posted_date_before,
                        "psc": psc,
                        "response_deadline_after": response_deadline_after,
                        "response_deadline_before": response_deadline_before,
                        "search": search,
                        "set_aside": set_aside,
                        "solicitation_number": solicitation_number,
                    },
                    opportunity_list_params.OpportunityListParams,
                ),
            ),
            cast_to=OpportunityListResponse,
        )


class OpportunitiesResourceWithRawResponse:
    def __init__(self, opportunities: OpportunitiesResource) -> None:
        self._opportunities = opportunities

        self.retrieve = to_raw_response_wrapper(
            opportunities.retrieve,
        )
        self.list = to_raw_response_wrapper(
            opportunities.list,
        )


class AsyncOpportunitiesResourceWithRawResponse:
    def __init__(self, opportunities: AsyncOpportunitiesResource) -> None:
        self._opportunities = opportunities

        self.retrieve = async_to_raw_response_wrapper(
            opportunities.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            opportunities.list,
        )


class OpportunitiesResourceWithStreamingResponse:
    def __init__(self, opportunities: OpportunitiesResource) -> None:
        self._opportunities = opportunities

        self.retrieve = to_streamed_response_wrapper(
            opportunities.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            opportunities.list,
        )


class AsyncOpportunitiesResourceWithStreamingResponse:
    def __init__(self, opportunities: AsyncOpportunitiesResource) -> None:
        self._opportunities = opportunities

        self.retrieve = async_to_streamed_response_wrapper(
            opportunities.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            opportunities.list,
        )
