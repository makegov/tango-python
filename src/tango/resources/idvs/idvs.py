# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from .awards import (
    AwardsResource,
    AsyncAwardsResource,
    AwardsResourceWithRawResponse,
    AsyncAwardsResourceWithRawResponse,
    AwardsResourceWithStreamingResponse,
    AsyncAwardsResourceWithStreamingResponse,
)
from ...types import idv_list_params
from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ..._utils import (
    maybe_transform,
    async_maybe_transform,
)
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...types.idv import Idv
from ..._base_client import make_request_options
from ...types.idv_list_response import IdvListResponse

__all__ = ["IdvsResource", "AsyncIdvsResource"]


class IdvsResource(SyncAPIResource):
    @cached_property
    def awards(self) -> AwardsResource:
        return AwardsResource(self._client)

    @cached_property
    def with_raw_response(self) -> IdvsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return the
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/makegov/tango-python#accessing-raw-response-data-eg-headers
        """
        return IdvsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> IdvsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/makegov/tango-python#with_streaming_response
        """
        return IdvsResourceWithStreamingResponse(self)

    def retrieve(
        self,
        contract_award_unique_key: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Idv:
        """
        API endpoint that allows IDV lookup.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not contract_award_unique_key:
            raise ValueError(
                f"Expected a non-empty value for `contract_award_unique_key` but received {contract_award_unique_key!r}"
            )
        return self._get(
            f"/api/idvs/{contract_award_unique_key}/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Idv,
        )

    def list(
        self,
        *,
        award_date: str | NotGiven = NOT_GIVEN,
        award_date_gte: str | NotGiven = NOT_GIVEN,
        award_date_lte: str | NotGiven = NOT_GIVEN,
        awarding_agency: str | NotGiven = NOT_GIVEN,
        fiscal_year: str | NotGiven = NOT_GIVEN,
        fiscal_year_gte: str | NotGiven = NOT_GIVEN,
        fiscal_year_lte: str | NotGiven = NOT_GIVEN,
        funding_agency: str | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        naics: str | NotGiven = NOT_GIVEN,
        ordering: str | NotGiven = NOT_GIVEN,
        page: int | NotGiven = NOT_GIVEN,
        psc: str | NotGiven = NOT_GIVEN,
        set_aside: str | NotGiven = NOT_GIVEN,
        uei: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> IdvListResponse:
        """
        API endpoint that allows IDV lookup.

        Args:
          award_date: <details><summary>Filter by award date</summary><ul><li><span>Accepted values: <var>2024-08-01</var>, <var>2024-08</var></span></li></ul></details>

          award_date_gte: <details><summary>Filter by award date</summary><ul><li><span>Accepted values: <var>2024-08-01</var></span></li></ul></details>

          award_date_lte: <details><summary>Filter by award date</summary><ul><li><span>Accepted values: <var>2024-08-01</var></span></li></ul></details>

          awarding_agency: <details><summary>Filter by awarding agency</summary><ul><li>Accepts any agency or department code, acronym, or (partial) name</li><li>Disjunctive with <var>|</var> or <var>OR</var></li></ul></details>

          fiscal_year: <details><summary>Filter by fiscal year</summary><ul><li><span>Accepted values: <var>2024</var></span></li></ul></details>

          fiscal_year_gte: <details><summary>Filter by fiscal year</summary><ul><li><span>Accepted values: <var>2024</var></span></li></ul></details>

          fiscal_year_lte: <details><summary>Filter by fiscal year</summary><ul><li><span>Accepted values: <var>2024</var></span></li></ul></details>

          funding_agency: <details><summary>Filter by funding agency</summary><ul><li>Accepts any agency or department code, acronym, or (partial) name</li><li>Disjunctive with <var>|</var> or <var>OR</var></li></ul></details>

          limit: Number of results to return per page.

          naics: <details><summary>Filter by NAICS Code</summary><ul><li><span>Accepted values: <var>541511</var>, <var>541512</var>, <var>etc.</var></span></li><li>Disjunctive with <var>|</var> or <var>OR</var></li></ul></details>

          ordering: <details><summary>Order results by a field of your choice.</summary><ul><li><span>Accepted values: <var>award_date</var>, <var>obligated</var>, <var>potential_total_value</var>, <var>recipient_name</var></span></li><li>Prefix with <var>-</var> to reverse order (e.g. <var>-award_date</var>)</li></ul></details>

          page: A page number within the paginated result set.

          psc: <details><summary>Filter by PSC (Product Service Code)</summary><ul><li><span>Accepted values: <var>S222</var>, <var>T005</var>, <var>etc.</var></span></li><li>Disjunctive with <var>|</var> or <var>OR</var></li></ul></details>

          set_aside: <details><summary>Filter by set-aside type</summary><ul><li><span>Accepted values: <var>8A</var>, <var>8AN</var>, <var>BICiv</var>, <var>EDWOSB</var>, <var>EDWOSBSS</var>, <var>HUBZONE</var>, <var>HZC</var>, <var>HZS</var>, <var>IEE</var>, <var>ISBEE</var>, <var>LAS</var>, <var>NONE</var>, <var>SB</var>, <var>SBA</var>, <var>SBP</var>, <var>SDB</var>, <var>SDVOSB</var>, <var>SDVOSBC</var>, <var>SDVOSBS</var>, <var>VOSB</var>, <var>VSA</var>, <var>VSS</var>, <var>WOSB</var>, <var>WOSBSS</var></span></li><li>Disjunctive with <var>|</var> or <var>OR</var></li></ul></details>

          uei: Filter by recipient UEI (Unique Entity Identifier)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/api/idvs/",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "award_date": award_date,
                        "award_date_gte": award_date_gte,
                        "award_date_lte": award_date_lte,
                        "awarding_agency": awarding_agency,
                        "fiscal_year": fiscal_year,
                        "fiscal_year_gte": fiscal_year_gte,
                        "fiscal_year_lte": fiscal_year_lte,
                        "funding_agency": funding_agency,
                        "limit": limit,
                        "naics": naics,
                        "ordering": ordering,
                        "page": page,
                        "psc": psc,
                        "set_aside": set_aside,
                        "uei": uei,
                    },
                    idv_list_params.IdvListParams,
                ),
            ),
            cast_to=IdvListResponse,
        )


class AsyncIdvsResource(AsyncAPIResource):
    @cached_property
    def awards(self) -> AsyncAwardsResource:
        return AsyncAwardsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncIdvsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return the
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/makegov/tango-python#accessing-raw-response-data-eg-headers
        """
        return AsyncIdvsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncIdvsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/makegov/tango-python#with_streaming_response
        """
        return AsyncIdvsResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        contract_award_unique_key: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Idv:
        """
        API endpoint that allows IDV lookup.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not contract_award_unique_key:
            raise ValueError(
                f"Expected a non-empty value for `contract_award_unique_key` but received {contract_award_unique_key!r}"
            )
        return await self._get(
            f"/api/idvs/{contract_award_unique_key}/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Idv,
        )

    async def list(
        self,
        *,
        award_date: str | NotGiven = NOT_GIVEN,
        award_date_gte: str | NotGiven = NOT_GIVEN,
        award_date_lte: str | NotGiven = NOT_GIVEN,
        awarding_agency: str | NotGiven = NOT_GIVEN,
        fiscal_year: str | NotGiven = NOT_GIVEN,
        fiscal_year_gte: str | NotGiven = NOT_GIVEN,
        fiscal_year_lte: str | NotGiven = NOT_GIVEN,
        funding_agency: str | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        naics: str | NotGiven = NOT_GIVEN,
        ordering: str | NotGiven = NOT_GIVEN,
        page: int | NotGiven = NOT_GIVEN,
        psc: str | NotGiven = NOT_GIVEN,
        set_aside: str | NotGiven = NOT_GIVEN,
        uei: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> IdvListResponse:
        """
        API endpoint that allows IDV lookup.

        Args:
          award_date: <details><summary>Filter by award date</summary><ul><li><span>Accepted values: <var>2024-08-01</var>, <var>2024-08</var></span></li></ul></details>

          award_date_gte: <details><summary>Filter by award date</summary><ul><li><span>Accepted values: <var>2024-08-01</var></span></li></ul></details>

          award_date_lte: <details><summary>Filter by award date</summary><ul><li><span>Accepted values: <var>2024-08-01</var></span></li></ul></details>

          awarding_agency: <details><summary>Filter by awarding agency</summary><ul><li>Accepts any agency or department code, acronym, or (partial) name</li><li>Disjunctive with <var>|</var> or <var>OR</var></li></ul></details>

          fiscal_year: <details><summary>Filter by fiscal year</summary><ul><li><span>Accepted values: <var>2024</var></span></li></ul></details>

          fiscal_year_gte: <details><summary>Filter by fiscal year</summary><ul><li><span>Accepted values: <var>2024</var></span></li></ul></details>

          fiscal_year_lte: <details><summary>Filter by fiscal year</summary><ul><li><span>Accepted values: <var>2024</var></span></li></ul></details>

          funding_agency: <details><summary>Filter by funding agency</summary><ul><li>Accepts any agency or department code, acronym, or (partial) name</li><li>Disjunctive with <var>|</var> or <var>OR</var></li></ul></details>

          limit: Number of results to return per page.

          naics: <details><summary>Filter by NAICS Code</summary><ul><li><span>Accepted values: <var>541511</var>, <var>541512</var>, <var>etc.</var></span></li><li>Disjunctive with <var>|</var> or <var>OR</var></li></ul></details>

          ordering: <details><summary>Order results by a field of your choice.</summary><ul><li><span>Accepted values: <var>award_date</var>, <var>obligated</var>, <var>potential_total_value</var>, <var>recipient_name</var></span></li><li>Prefix with <var>-</var> to reverse order (e.g. <var>-award_date</var>)</li></ul></details>

          page: A page number within the paginated result set.

          psc: <details><summary>Filter by PSC (Product Service Code)</summary><ul><li><span>Accepted values: <var>S222</var>, <var>T005</var>, <var>etc.</var></span></li><li>Disjunctive with <var>|</var> or <var>OR</var></li></ul></details>

          set_aside: <details><summary>Filter by set-aside type</summary><ul><li><span>Accepted values: <var>8A</var>, <var>8AN</var>, <var>BICiv</var>, <var>EDWOSB</var>, <var>EDWOSBSS</var>, <var>HUBZONE</var>, <var>HZC</var>, <var>HZS</var>, <var>IEE</var>, <var>ISBEE</var>, <var>LAS</var>, <var>NONE</var>, <var>SB</var>, <var>SBA</var>, <var>SBP</var>, <var>SDB</var>, <var>SDVOSB</var>, <var>SDVOSBC</var>, <var>SDVOSBS</var>, <var>VOSB</var>, <var>VSA</var>, <var>VSS</var>, <var>WOSB</var>, <var>WOSBSS</var></span></li><li>Disjunctive with <var>|</var> or <var>OR</var></li></ul></details>

          uei: Filter by recipient UEI (Unique Entity Identifier)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/api/idvs/",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "award_date": award_date,
                        "award_date_gte": award_date_gte,
                        "award_date_lte": award_date_lte,
                        "awarding_agency": awarding_agency,
                        "fiscal_year": fiscal_year,
                        "fiscal_year_gte": fiscal_year_gte,
                        "fiscal_year_lte": fiscal_year_lte,
                        "funding_agency": funding_agency,
                        "limit": limit,
                        "naics": naics,
                        "ordering": ordering,
                        "page": page,
                        "psc": psc,
                        "set_aside": set_aside,
                        "uei": uei,
                    },
                    idv_list_params.IdvListParams,
                ),
            ),
            cast_to=IdvListResponse,
        )


class IdvsResourceWithRawResponse:
    def __init__(self, idvs: IdvsResource) -> None:
        self._idvs = idvs

        self.retrieve = to_raw_response_wrapper(
            idvs.retrieve,
        )
        self.list = to_raw_response_wrapper(
            idvs.list,
        )

    @cached_property
    def awards(self) -> AwardsResourceWithRawResponse:
        return AwardsResourceWithRawResponse(self._idvs.awards)


class AsyncIdvsResourceWithRawResponse:
    def __init__(self, idvs: AsyncIdvsResource) -> None:
        self._idvs = idvs

        self.retrieve = async_to_raw_response_wrapper(
            idvs.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            idvs.list,
        )

    @cached_property
    def awards(self) -> AsyncAwardsResourceWithRawResponse:
        return AsyncAwardsResourceWithRawResponse(self._idvs.awards)


class IdvsResourceWithStreamingResponse:
    def __init__(self, idvs: IdvsResource) -> None:
        self._idvs = idvs

        self.retrieve = to_streamed_response_wrapper(
            idvs.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            idvs.list,
        )

    @cached_property
    def awards(self) -> AwardsResourceWithStreamingResponse:
        return AwardsResourceWithStreamingResponse(self._idvs.awards)


class AsyncIdvsResourceWithStreamingResponse:
    def __init__(self, idvs: AsyncIdvsResource) -> None:
        self._idvs = idvs

        self.retrieve = async_to_streamed_response_wrapper(
            idvs.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            idvs.list,
        )

    @cached_property
    def awards(self) -> AsyncAwardsResourceWithStreamingResponse:
        return AsyncAwardsResourceWithStreamingResponse(self._idvs.awards)
