# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from datetime import date

import httpx

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
from ...types.idvs import award_list_params
from ..._base_client import make_request_options
from ...types.idvs.award_list_response import AwardListResponse

__all__ = ["AwardsResource", "AsyncAwardsResource"]


class AwardsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AwardsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return the
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/makegov/tango-python#accessing-raw-response-data-eg-headers
        """
        return AwardsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AwardsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/makegov/tango-python#with_streaming_response
        """
        return AwardsResourceWithStreamingResponse(self)

    def list(
        self,
        *,
        path_contract_award_unique_key: str,
        award_date: str | NotGiven = NOT_GIVEN,
        award_date_gte: Union[str, date] | NotGiven = NOT_GIVEN,
        award_date_lte: Union[str, date] | NotGiven = NOT_GIVEN,
        awarding_agency: str | NotGiven = NOT_GIVEN,
        query_contract_award_unique_key: str | NotGiven = NOT_GIVEN,
        fiscal_year: int | NotGiven = NOT_GIVEN,
        fiscal_year_gte: int | NotGiven = NOT_GIVEN,
        fiscal_year_lte: int | NotGiven = NOT_GIVEN,
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
    ) -> AwardListResponse:
        """
        API endpoint that allows awards under a specific IDV to be viewed.

        Args:
          award_date: Filter by the award date

          awarding_agency: Filter by awarding agency or department

          query_contract_award_unique_key: The unique key for the contract award.

          funding_agency: Filter by funding agency or department

          limit: Number of results to return per page.

          ordering: Which field to use when ordering the results.

          page: A page number within the paginated result set.

          uei: Unique Entity Identifier

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not path_contract_award_unique_key:
            raise ValueError(
                f"Expected a non-empty value for `path_contract_award_unique_key` but received {path_contract_award_unique_key!r}"
            )
        return self._get(
            f"/api/idvs/{path_contract_award_unique_key}/awards/",
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
                        "query_contract_award_unique_key": query_contract_award_unique_key,
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
                    award_list_params.AwardListParams,
                ),
            ),
            cast_to=AwardListResponse,
        )


class AsyncAwardsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncAwardsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return the
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/makegov/tango-python#accessing-raw-response-data-eg-headers
        """
        return AsyncAwardsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncAwardsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/makegov/tango-python#with_streaming_response
        """
        return AsyncAwardsResourceWithStreamingResponse(self)

    async def list(
        self,
        *,
        path_contract_award_unique_key: str,
        award_date: str | NotGiven = NOT_GIVEN,
        award_date_gte: Union[str, date] | NotGiven = NOT_GIVEN,
        award_date_lte: Union[str, date] | NotGiven = NOT_GIVEN,
        awarding_agency: str | NotGiven = NOT_GIVEN,
        query_contract_award_unique_key: str | NotGiven = NOT_GIVEN,
        fiscal_year: int | NotGiven = NOT_GIVEN,
        fiscal_year_gte: int | NotGiven = NOT_GIVEN,
        fiscal_year_lte: int | NotGiven = NOT_GIVEN,
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
    ) -> AwardListResponse:
        """
        API endpoint that allows awards under a specific IDV to be viewed.

        Args:
          award_date: Filter by the award date

          awarding_agency: Filter by awarding agency or department

          query_contract_award_unique_key: The unique key for the contract award.

          funding_agency: Filter by funding agency or department

          limit: Number of results to return per page.

          ordering: Which field to use when ordering the results.

          page: A page number within the paginated result set.

          uei: Unique Entity Identifier

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not path_contract_award_unique_key:
            raise ValueError(
                f"Expected a non-empty value for `path_contract_award_unique_key` but received {path_contract_award_unique_key!r}"
            )
        return await self._get(
            f"/api/idvs/{path_contract_award_unique_key}/awards/",
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
                        "query_contract_award_unique_key": query_contract_award_unique_key,
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
                    award_list_params.AwardListParams,
                ),
            ),
            cast_to=AwardListResponse,
        )


class AwardsResourceWithRawResponse:
    def __init__(self, awards: AwardsResource) -> None:
        self._awards = awards

        self.list = to_raw_response_wrapper(
            awards.list,
        )


class AsyncAwardsResourceWithRawResponse:
    def __init__(self, awards: AsyncAwardsResource) -> None:
        self._awards = awards

        self.list = async_to_raw_response_wrapper(
            awards.list,
        )


class AwardsResourceWithStreamingResponse:
    def __init__(self, awards: AwardsResource) -> None:
        self._awards = awards

        self.list = to_streamed_response_wrapper(
            awards.list,
        )


class AsyncAwardsResourceWithStreamingResponse:
    def __init__(self, awards: AsyncAwardsResource) -> None:
        self._awards = awards

        self.list = async_to_streamed_response_wrapper(
            awards.list,
        )
