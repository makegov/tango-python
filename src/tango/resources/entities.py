# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import entity_list_params
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
from ..types.entity_list_response import EntityListResponse
from ..types.entity_retrieve_response import EntityRetrieveResponse

__all__ = ["EntitiesResource", "AsyncEntitiesResource"]


class EntitiesResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> EntitiesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return the
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/makegov/tango-python#accessing-raw-response-data-eg-headers
        """
        return EntitiesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> EntitiesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/makegov/tango-python#with_streaming_response
        """
        return EntitiesResourceWithStreamingResponse(self)

    def retrieve(
        self,
        uei: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> EntityRetrieveResponse:
        """
        API endpoint that allows entities lookup.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not uei:
            raise ValueError(f"Expected a non-empty value for `uei` but received {uei!r}")
        return self._get(
            f"/api/entities/{uei}/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EntityRetrieveResponse,
        )

    def list(
        self,
        *,
        cage_code: str | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        naics: str | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        page: int | NotGiven = NOT_GIVEN,
        psc: str | NotGiven = NOT_GIVEN,
        purpose_of_registration_code: str | NotGiven = NOT_GIVEN,
        search: str | NotGiven = NOT_GIVEN,
        socioeconomic: str | NotGiven = NOT_GIVEN,
        state: str | NotGiven = NOT_GIVEN,
        uei: str | NotGiven = NOT_GIVEN,
        zip_code: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> EntityListResponse:
        """
        API endpoint that allows entities lookup.

        Args:
          cage_code: CAGE Code

          limit: Number of results to return per page.

          name: The company name

          page: A page number within the paginated result set.

          uei: Unique Entity Identifier

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/api/entities/",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "cage_code": cage_code,
                        "limit": limit,
                        "naics": naics,
                        "name": name,
                        "page": page,
                        "psc": psc,
                        "purpose_of_registration_code": purpose_of_registration_code,
                        "search": search,
                        "socioeconomic": socioeconomic,
                        "state": state,
                        "uei": uei,
                        "zip_code": zip_code,
                    },
                    entity_list_params.EntityListParams,
                ),
            ),
            cast_to=EntityListResponse,
        )


class AsyncEntitiesResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncEntitiesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return the
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/makegov/tango-python#accessing-raw-response-data-eg-headers
        """
        return AsyncEntitiesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncEntitiesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/makegov/tango-python#with_streaming_response
        """
        return AsyncEntitiesResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        uei: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> EntityRetrieveResponse:
        """
        API endpoint that allows entities lookup.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not uei:
            raise ValueError(f"Expected a non-empty value for `uei` but received {uei!r}")
        return await self._get(
            f"/api/entities/{uei}/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EntityRetrieveResponse,
        )

    async def list(
        self,
        *,
        cage_code: str | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        naics: str | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        page: int | NotGiven = NOT_GIVEN,
        psc: str | NotGiven = NOT_GIVEN,
        purpose_of_registration_code: str | NotGiven = NOT_GIVEN,
        search: str | NotGiven = NOT_GIVEN,
        socioeconomic: str | NotGiven = NOT_GIVEN,
        state: str | NotGiven = NOT_GIVEN,
        uei: str | NotGiven = NOT_GIVEN,
        zip_code: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> EntityListResponse:
        """
        API endpoint that allows entities lookup.

        Args:
          cage_code: CAGE Code

          limit: Number of results to return per page.

          name: The company name

          page: A page number within the paginated result set.

          uei: Unique Entity Identifier

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/api/entities/",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "cage_code": cage_code,
                        "limit": limit,
                        "naics": naics,
                        "name": name,
                        "page": page,
                        "psc": psc,
                        "purpose_of_registration_code": purpose_of_registration_code,
                        "search": search,
                        "socioeconomic": socioeconomic,
                        "state": state,
                        "uei": uei,
                        "zip_code": zip_code,
                    },
                    entity_list_params.EntityListParams,
                ),
            ),
            cast_to=EntityListResponse,
        )


class EntitiesResourceWithRawResponse:
    def __init__(self, entities: EntitiesResource) -> None:
        self._entities = entities

        self.retrieve = to_raw_response_wrapper(
            entities.retrieve,
        )
        self.list = to_raw_response_wrapper(
            entities.list,
        )


class AsyncEntitiesResourceWithRawResponse:
    def __init__(self, entities: AsyncEntitiesResource) -> None:
        self._entities = entities

        self.retrieve = async_to_raw_response_wrapper(
            entities.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            entities.list,
        )


class EntitiesResourceWithStreamingResponse:
    def __init__(self, entities: EntitiesResource) -> None:
        self._entities = entities

        self.retrieve = to_streamed_response_wrapper(
            entities.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            entities.list,
        )


class AsyncEntitiesResourceWithStreamingResponse:
    def __init__(self, entities: AsyncEntitiesResource) -> None:
        self._entities = entities

        self.retrieve = async_to_streamed_response_wrapper(
            entities.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            entities.list,
        )
