# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, Union, Mapping
from typing_extensions import Self, override

import httpx

from . import resources, _exceptions
from ._qs import Querystring
from ._types import (
    NOT_GIVEN,
    Omit,
    Timeout,
    NotGiven,
    Transport,
    ProxiesTypes,
    RequestOptions,
)
from ._utils import (
    is_given,
    get_async_library,
)
from ._version import __version__
from ._streaming import Stream as Stream, AsyncStream as AsyncStream
from ._exceptions import TangoError, APIStatusError
from ._base_client import (
    DEFAULT_MAX_RETRIES,
    SyncAPIClient,
    AsyncAPIClient,
)

__all__ = [
    "Timeout",
    "Transport",
    "ProxiesTypes",
    "RequestOptions",
    "resources",
    "Tango",
    "AsyncTango",
    "Client",
    "AsyncClient",
]


class Tango(SyncAPIClient):
    agencies: resources.AgenciesResource
    assistance_listings: resources.AssistanceListingsResource
    bulk: resources.BulkResource
    business_types: resources.BusinessTypesResource
    contracts: resources.ContractsResource
    departments: resources.DepartmentsResource
    entities: resources.EntitiesResource
    idvs: resources.IdvsResource
    naics: resources.NaicsResource
    notices: resources.NoticesResource
    offices: resources.OfficesResource
    opportunities: resources.OpportunitiesResource
    pscs: resources.PscsResource
    schemas: resources.SchemasResource
    subawards: resources.SubawardsResource
    versions: resources.VersionsResource
    with_raw_response: TangoWithRawResponse
    with_streaming_response: TangoWithStreamedResponse

    # client options
    client_id: str
    client_secret: str

    def __init__(
        self,
        *,
        client_id: str | None = None,
        client_secret: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: Union[float, Timeout, None, NotGiven] = NOT_GIVEN,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        # Configure a custom httpx client.
        # We provide a `DefaultHttpxClient` class that you can pass to retain the default values we use for `limits`, `timeout` & `follow_redirects`.
        # See the [httpx documentation](https://www.python-httpx.org/api/#client) for more details.
        http_client: httpx.Client | None = None,
        # Enable or disable schema validation for data returned by the API.
        # When enabled an error APIResponseValidationError is raised
        # if the API responds with invalid data for the expected schema.
        #
        # This parameter may be removed or changed in the future.
        # If you rely on this feature, please open a GitHub issue
        # outlining your use-case to help us decide if it should be
        # part of our public interface in the future.
        _strict_response_validation: bool = False,
    ) -> None:
        """Construct a new synchronous tango client instance.

        This automatically infers the following arguments from their corresponding environment variables if they are not provided:
        - `client_id` from `CLIENT_ID`
        - `client_secret` from `CLIENT_SECRET`
        """
        if client_id is None:
            client_id = os.environ.get("CLIENT_ID")
        if client_id is None:
            raise TangoError(
                "The client_id client option must be set either by passing client_id to the client or by setting the CLIENT_ID environment variable"
            )
        self.client_id = client_id

        if client_secret is None:
            client_secret = os.environ.get("CLIENT_SECRET")
        if client_secret is None:
            raise TangoError(
                "The client_secret client option must be set either by passing client_secret to the client or by setting the CLIENT_SECRET environment variable"
            )
        self.client_secret = client_secret

        if base_url is None:
            base_url = os.environ.get("TANGO_BASE_URL")
        if base_url is None:
            base_url = f"https://tango.makegov.com"

        super().__init__(
            version=__version__,
            base_url=base_url,
            max_retries=max_retries,
            timeout=timeout,
            http_client=http_client,
            custom_headers=default_headers,
            custom_query=default_query,
            _strict_response_validation=_strict_response_validation,
        )

        self.agencies = resources.AgenciesResource(self)
        self.assistance_listings = resources.AssistanceListingsResource(self)
        self.bulk = resources.BulkResource(self)
        self.business_types = resources.BusinessTypesResource(self)
        self.contracts = resources.ContractsResource(self)
        self.departments = resources.DepartmentsResource(self)
        self.entities = resources.EntitiesResource(self)
        self.idvs = resources.IdvsResource(self)
        self.naics = resources.NaicsResource(self)
        self.notices = resources.NoticesResource(self)
        self.offices = resources.OfficesResource(self)
        self.opportunities = resources.OpportunitiesResource(self)
        self.pscs = resources.PscsResource(self)
        self.schemas = resources.SchemasResource(self)
        self.subawards = resources.SubawardsResource(self)
        self.versions = resources.VersionsResource(self)
        self.with_raw_response = TangoWithRawResponse(self)
        self.with_streaming_response = TangoWithStreamedResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="comma")

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": "false",
            **self._custom_headers,
        }

    def copy(
        self,
        *,
        client_id: str | None = None,
        client_secret: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = NOT_GIVEN,
        http_client: httpx.Client | None = None,
        max_retries: int | NotGiven = NOT_GIVEN,
        default_headers: Mapping[str, str] | None = None,
        set_default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        set_default_query: Mapping[str, object] | None = None,
        _extra_kwargs: Mapping[str, Any] = {},
    ) -> Self:
        """
        Create a new client instance re-using the same options given to the current client with optional overriding.
        """
        if default_headers is not None and set_default_headers is not None:
            raise ValueError("The `default_headers` and `set_default_headers` arguments are mutually exclusive")

        if default_query is not None and set_default_query is not None:
            raise ValueError("The `default_query` and `set_default_query` arguments are mutually exclusive")

        headers = self._custom_headers
        if default_headers is not None:
            headers = {**headers, **default_headers}
        elif set_default_headers is not None:
            headers = set_default_headers

        params = self._custom_query
        if default_query is not None:
            params = {**params, **default_query}
        elif set_default_query is not None:
            params = set_default_query

        http_client = http_client or self._client
        return self.__class__(
            client_id=client_id or self.client_id,
            client_secret=client_secret or self.client_secret,
            base_url=base_url or self.base_url,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            **_extra_kwargs,
        )

    # Alias for `copy` for nicer inline usage, e.g.
    # client.with_options(timeout=10).foo.create(...)
    with_options = copy

    @override
    def _make_status_error(
        self,
        err_msg: str,
        *,
        body: object,
        response: httpx.Response,
    ) -> APIStatusError:
        if response.status_code == 400:
            return _exceptions.BadRequestError(err_msg, response=response, body=body)

        if response.status_code == 401:
            return _exceptions.AuthenticationError(err_msg, response=response, body=body)

        if response.status_code == 403:
            return _exceptions.PermissionDeniedError(err_msg, response=response, body=body)

        if response.status_code == 404:
            return _exceptions.NotFoundError(err_msg, response=response, body=body)

        if response.status_code == 409:
            return _exceptions.ConflictError(err_msg, response=response, body=body)

        if response.status_code == 422:
            return _exceptions.UnprocessableEntityError(err_msg, response=response, body=body)

        if response.status_code == 429:
            return _exceptions.RateLimitError(err_msg, response=response, body=body)

        if response.status_code >= 500:
            return _exceptions.InternalServerError(err_msg, response=response, body=body)
        return APIStatusError(err_msg, response=response, body=body)


class AsyncTango(AsyncAPIClient):
    agencies: resources.AsyncAgenciesResource
    assistance_listings: resources.AsyncAssistanceListingsResource
    bulk: resources.AsyncBulkResource
    business_types: resources.AsyncBusinessTypesResource
    contracts: resources.AsyncContractsResource
    departments: resources.AsyncDepartmentsResource
    entities: resources.AsyncEntitiesResource
    idvs: resources.AsyncIdvsResource
    naics: resources.AsyncNaicsResource
    notices: resources.AsyncNoticesResource
    offices: resources.AsyncOfficesResource
    opportunities: resources.AsyncOpportunitiesResource
    pscs: resources.AsyncPscsResource
    schemas: resources.AsyncSchemasResource
    subawards: resources.AsyncSubawardsResource
    versions: resources.AsyncVersionsResource
    with_raw_response: AsyncTangoWithRawResponse
    with_streaming_response: AsyncTangoWithStreamedResponse

    # client options
    client_id: str
    client_secret: str

    def __init__(
        self,
        *,
        client_id: str | None = None,
        client_secret: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: Union[float, Timeout, None, NotGiven] = NOT_GIVEN,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        # Configure a custom httpx client.
        # We provide a `DefaultAsyncHttpxClient` class that you can pass to retain the default values we use for `limits`, `timeout` & `follow_redirects`.
        # See the [httpx documentation](https://www.python-httpx.org/api/#asyncclient) for more details.
        http_client: httpx.AsyncClient | None = None,
        # Enable or disable schema validation for data returned by the API.
        # When enabled an error APIResponseValidationError is raised
        # if the API responds with invalid data for the expected schema.
        #
        # This parameter may be removed or changed in the future.
        # If you rely on this feature, please open a GitHub issue
        # outlining your use-case to help us decide if it should be
        # part of our public interface in the future.
        _strict_response_validation: bool = False,
    ) -> None:
        """Construct a new async tango client instance.

        This automatically infers the following arguments from their corresponding environment variables if they are not provided:
        - `client_id` from `CLIENT_ID`
        - `client_secret` from `CLIENT_SECRET`
        """
        if client_id is None:
            client_id = os.environ.get("CLIENT_ID")
        if client_id is None:
            raise TangoError(
                "The client_id client option must be set either by passing client_id to the client or by setting the CLIENT_ID environment variable"
            )
        self.client_id = client_id

        if client_secret is None:
            client_secret = os.environ.get("CLIENT_SECRET")
        if client_secret is None:
            raise TangoError(
                "The client_secret client option must be set either by passing client_secret to the client or by setting the CLIENT_SECRET environment variable"
            )
        self.client_secret = client_secret

        if base_url is None:
            base_url = os.environ.get("TANGO_BASE_URL")
        if base_url is None:
            base_url = f"https://tango.makegov.com"

        super().__init__(
            version=__version__,
            base_url=base_url,
            max_retries=max_retries,
            timeout=timeout,
            http_client=http_client,
            custom_headers=default_headers,
            custom_query=default_query,
            _strict_response_validation=_strict_response_validation,
        )

        self.agencies = resources.AsyncAgenciesResource(self)
        self.assistance_listings = resources.AsyncAssistanceListingsResource(self)
        self.bulk = resources.AsyncBulkResource(self)
        self.business_types = resources.AsyncBusinessTypesResource(self)
        self.contracts = resources.AsyncContractsResource(self)
        self.departments = resources.AsyncDepartmentsResource(self)
        self.entities = resources.AsyncEntitiesResource(self)
        self.idvs = resources.AsyncIdvsResource(self)
        self.naics = resources.AsyncNaicsResource(self)
        self.notices = resources.AsyncNoticesResource(self)
        self.offices = resources.AsyncOfficesResource(self)
        self.opportunities = resources.AsyncOpportunitiesResource(self)
        self.pscs = resources.AsyncPscsResource(self)
        self.schemas = resources.AsyncSchemasResource(self)
        self.subawards = resources.AsyncSubawardsResource(self)
        self.versions = resources.AsyncVersionsResource(self)
        self.with_raw_response = AsyncTangoWithRawResponse(self)
        self.with_streaming_response = AsyncTangoWithStreamedResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="comma")

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": f"async:{get_async_library()}",
            **self._custom_headers,
        }

    def copy(
        self,
        *,
        client_id: str | None = None,
        client_secret: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = NOT_GIVEN,
        http_client: httpx.AsyncClient | None = None,
        max_retries: int | NotGiven = NOT_GIVEN,
        default_headers: Mapping[str, str] | None = None,
        set_default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        set_default_query: Mapping[str, object] | None = None,
        _extra_kwargs: Mapping[str, Any] = {},
    ) -> Self:
        """
        Create a new client instance re-using the same options given to the current client with optional overriding.
        """
        if default_headers is not None and set_default_headers is not None:
            raise ValueError("The `default_headers` and `set_default_headers` arguments are mutually exclusive")

        if default_query is not None and set_default_query is not None:
            raise ValueError("The `default_query` and `set_default_query` arguments are mutually exclusive")

        headers = self._custom_headers
        if default_headers is not None:
            headers = {**headers, **default_headers}
        elif set_default_headers is not None:
            headers = set_default_headers

        params = self._custom_query
        if default_query is not None:
            params = {**params, **default_query}
        elif set_default_query is not None:
            params = set_default_query

        http_client = http_client or self._client
        return self.__class__(
            client_id=client_id or self.client_id,
            client_secret=client_secret or self.client_secret,
            base_url=base_url or self.base_url,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            **_extra_kwargs,
        )

    # Alias for `copy` for nicer inline usage, e.g.
    # client.with_options(timeout=10).foo.create(...)
    with_options = copy

    @override
    def _make_status_error(
        self,
        err_msg: str,
        *,
        body: object,
        response: httpx.Response,
    ) -> APIStatusError:
        if response.status_code == 400:
            return _exceptions.BadRequestError(err_msg, response=response, body=body)

        if response.status_code == 401:
            return _exceptions.AuthenticationError(err_msg, response=response, body=body)

        if response.status_code == 403:
            return _exceptions.PermissionDeniedError(err_msg, response=response, body=body)

        if response.status_code == 404:
            return _exceptions.NotFoundError(err_msg, response=response, body=body)

        if response.status_code == 409:
            return _exceptions.ConflictError(err_msg, response=response, body=body)

        if response.status_code == 422:
            return _exceptions.UnprocessableEntityError(err_msg, response=response, body=body)

        if response.status_code == 429:
            return _exceptions.RateLimitError(err_msg, response=response, body=body)

        if response.status_code >= 500:
            return _exceptions.InternalServerError(err_msg, response=response, body=body)
        return APIStatusError(err_msg, response=response, body=body)


class TangoWithRawResponse:
    def __init__(self, client: Tango) -> None:
        self.agencies = resources.AgenciesResourceWithRawResponse(client.agencies)
        self.assistance_listings = resources.AssistanceListingsResourceWithRawResponse(client.assistance_listings)
        self.bulk = resources.BulkResourceWithRawResponse(client.bulk)
        self.business_types = resources.BusinessTypesResourceWithRawResponse(client.business_types)
        self.contracts = resources.ContractsResourceWithRawResponse(client.contracts)
        self.departments = resources.DepartmentsResourceWithRawResponse(client.departments)
        self.entities = resources.EntitiesResourceWithRawResponse(client.entities)
        self.idvs = resources.IdvsResourceWithRawResponse(client.idvs)
        self.naics = resources.NaicsResourceWithRawResponse(client.naics)
        self.notices = resources.NoticesResourceWithRawResponse(client.notices)
        self.offices = resources.OfficesResourceWithRawResponse(client.offices)
        self.opportunities = resources.OpportunitiesResourceWithRawResponse(client.opportunities)
        self.pscs = resources.PscsResourceWithRawResponse(client.pscs)
        self.schemas = resources.SchemasResourceWithRawResponse(client.schemas)
        self.subawards = resources.SubawardsResourceWithRawResponse(client.subawards)
        self.versions = resources.VersionsResourceWithRawResponse(client.versions)


class AsyncTangoWithRawResponse:
    def __init__(self, client: AsyncTango) -> None:
        self.agencies = resources.AsyncAgenciesResourceWithRawResponse(client.agencies)
        self.assistance_listings = resources.AsyncAssistanceListingsResourceWithRawResponse(client.assistance_listings)
        self.bulk = resources.AsyncBulkResourceWithRawResponse(client.bulk)
        self.business_types = resources.AsyncBusinessTypesResourceWithRawResponse(client.business_types)
        self.contracts = resources.AsyncContractsResourceWithRawResponse(client.contracts)
        self.departments = resources.AsyncDepartmentsResourceWithRawResponse(client.departments)
        self.entities = resources.AsyncEntitiesResourceWithRawResponse(client.entities)
        self.idvs = resources.AsyncIdvsResourceWithRawResponse(client.idvs)
        self.naics = resources.AsyncNaicsResourceWithRawResponse(client.naics)
        self.notices = resources.AsyncNoticesResourceWithRawResponse(client.notices)
        self.offices = resources.AsyncOfficesResourceWithRawResponse(client.offices)
        self.opportunities = resources.AsyncOpportunitiesResourceWithRawResponse(client.opportunities)
        self.pscs = resources.AsyncPscsResourceWithRawResponse(client.pscs)
        self.schemas = resources.AsyncSchemasResourceWithRawResponse(client.schemas)
        self.subawards = resources.AsyncSubawardsResourceWithRawResponse(client.subawards)
        self.versions = resources.AsyncVersionsResourceWithRawResponse(client.versions)


class TangoWithStreamedResponse:
    def __init__(self, client: Tango) -> None:
        self.agencies = resources.AgenciesResourceWithStreamingResponse(client.agencies)
        self.assistance_listings = resources.AssistanceListingsResourceWithStreamingResponse(client.assistance_listings)
        self.bulk = resources.BulkResourceWithStreamingResponse(client.bulk)
        self.business_types = resources.BusinessTypesResourceWithStreamingResponse(client.business_types)
        self.contracts = resources.ContractsResourceWithStreamingResponse(client.contracts)
        self.departments = resources.DepartmentsResourceWithStreamingResponse(client.departments)
        self.entities = resources.EntitiesResourceWithStreamingResponse(client.entities)
        self.idvs = resources.IdvsResourceWithStreamingResponse(client.idvs)
        self.naics = resources.NaicsResourceWithStreamingResponse(client.naics)
        self.notices = resources.NoticesResourceWithStreamingResponse(client.notices)
        self.offices = resources.OfficesResourceWithStreamingResponse(client.offices)
        self.opportunities = resources.OpportunitiesResourceWithStreamingResponse(client.opportunities)
        self.pscs = resources.PscsResourceWithStreamingResponse(client.pscs)
        self.schemas = resources.SchemasResourceWithStreamingResponse(client.schemas)
        self.subawards = resources.SubawardsResourceWithStreamingResponse(client.subawards)
        self.versions = resources.VersionsResourceWithStreamingResponse(client.versions)


class AsyncTangoWithStreamedResponse:
    def __init__(self, client: AsyncTango) -> None:
        self.agencies = resources.AsyncAgenciesResourceWithStreamingResponse(client.agencies)
        self.assistance_listings = resources.AsyncAssistanceListingsResourceWithStreamingResponse(
            client.assistance_listings
        )
        self.bulk = resources.AsyncBulkResourceWithStreamingResponse(client.bulk)
        self.business_types = resources.AsyncBusinessTypesResourceWithStreamingResponse(client.business_types)
        self.contracts = resources.AsyncContractsResourceWithStreamingResponse(client.contracts)
        self.departments = resources.AsyncDepartmentsResourceWithStreamingResponse(client.departments)
        self.entities = resources.AsyncEntitiesResourceWithStreamingResponse(client.entities)
        self.idvs = resources.AsyncIdvsResourceWithStreamingResponse(client.idvs)
        self.naics = resources.AsyncNaicsResourceWithStreamingResponse(client.naics)
        self.notices = resources.AsyncNoticesResourceWithStreamingResponse(client.notices)
        self.offices = resources.AsyncOfficesResourceWithStreamingResponse(client.offices)
        self.opportunities = resources.AsyncOpportunitiesResourceWithStreamingResponse(client.opportunities)
        self.pscs = resources.AsyncPscsResourceWithStreamingResponse(client.pscs)
        self.schemas = resources.AsyncSchemasResourceWithStreamingResponse(client.schemas)
        self.subawards = resources.AsyncSubawardsResourceWithStreamingResponse(client.subawards)
        self.versions = resources.AsyncVersionsResourceWithStreamingResponse(client.versions)


Client = Tango

AsyncClient = AsyncTango
