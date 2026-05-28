"""Tango API Client"""

import os
import warnings
from datetime import date, datetime
from decimal import Decimal
from typing import Any
from urllib.parse import urljoin

import httpx

from tango.exceptions import (
    TangoAPIError,
    TangoAuthError,
    TangoNotFoundError,
    TangoRateLimitError,
    TangoValidationError,
)
from tango.models import (
    IDV,
    OTA,
    OTIDV,
    Agency,
    BudgetAccount,
    BusinessType,
    Contract,
    Entity,
    Forecast,
    Grant,
    GsaElibraryContract,
    ITDashboardInvestment,
    Location,
    Notice,
    Opportunity,
    Organization,
    PaginatedResponse,
    Protest,
    RateLimitInfo,
    ResolveCandidate,
    ResolveResult,
    SearchFilters,
    ShapeConfig,
    Subaward,
    ValidateResult,
    Vehicle,
    WebhookAlert,
    WebhookEndpoint,
    WebhookEventType,
    WebhookEventTypesResponse,
    WebhookSamplePayloadResponse,
    WebhookTestDeliveryResult,
)
from tango.shapes import (
    ModelFactory,
    ShapeParser,
    TypeGenerator,
    build_parser_registry_from_client,
)


class TangoClient:
    """Tango API Client"""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = "https://tango.makegov.com",
        user_agent: str | None = None,
        extra_headers: dict[str, str] | None = None,
    ):
        """
        Initialize the Tango API client

        Args:
            api_key: API key for authentication. If not provided, will attempt to load from
                    TANGO_API_KEY environment variable.
            base_url: Base URL for the API
            user_agent: Custom User-Agent header value.
            extra_headers: Additional headers to include in every request.
        """
        # Load API key from environment if not provided
        self.api_key = api_key or os.getenv("TANGO_API_KEY")
        self.base_url = base_url.rstrip("/")

        # Build headers
        headers = {}
        if self.api_key:
            headers["X-API-KEY"] = self.api_key
        if user_agent:
            headers["User-Agent"] = user_agent
        if extra_headers:
            headers.update(extra_headers)

        self.client = httpx.Client(headers=headers, timeout=30.0)
        self._last_rate_limit_info: RateLimitInfo | None = None
        self._last_response_headers: httpx.Headers | None = None

        # Use hardcoded sensible defaults
        cache_size = 100

        # Initialize components
        self._shape_parser = ShapeParser(cache_enabled=True)
        self._type_generator = TypeGenerator(cache_enabled=True, cache_size=cache_size)

        # Build parser registry from client methods
        parser_registry = build_parser_registry_from_client(self)

        # Initialize model factory
        self._model_factory = ModelFactory(
            type_generator=self._type_generator,
            parsers=parser_registry,
        )

    # ============================================================================
    # Core HTTP Request Utilities
    # ============================================================================

    @property
    def rate_limit_info(self) -> RateLimitInfo | None:
        """Rate limit info from the most recent API response."""
        return self._last_rate_limit_info

    @property
    def last_response_headers(self) -> httpx.Headers | None:
        """Full HTTP headers from the most recent API response."""
        return self._last_response_headers

    @staticmethod
    def _parse_rate_limit_headers(headers: httpx.Headers) -> RateLimitInfo:
        """Extract rate limit info from response headers."""

        def _int_or_none(val: str | None) -> int | None:
            if val is None:
                return None
            try:
                return int(val)
            except (ValueError, TypeError):
                return None

        return RateLimitInfo(
            limit=_int_or_none(headers.get("X-RateLimit-Limit")),
            remaining=_int_or_none(headers.get("X-RateLimit-Remaining")),
            reset=_int_or_none(headers.get("X-RateLimit-Reset")),
            daily_limit=_int_or_none(headers.get("X-RateLimit-Daily-Limit")),
            daily_remaining=_int_or_none(headers.get("X-RateLimit-Daily-Remaining")),
            daily_reset=_int_or_none(headers.get("X-RateLimit-Daily-Reset")),
            burst_limit=_int_or_none(headers.get("X-RateLimit-Burst-Limit")),
            burst_remaining=_int_or_none(headers.get("X-RateLimit-Burst-Remaining")),
            burst_reset=_int_or_none(headers.get("X-RateLimit-Burst-Reset")),
        )

    def _request(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
        json_data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make an API request"""
        url = urljoin(f"{self.base_url}/", endpoint.lstrip("/"))

        try:
            response = self.client.request(method=method, url=url, params=params, json=json_data)
            self._last_response_headers = response.headers
            self._last_rate_limit_info = self._parse_rate_limit_headers(response.headers)

            if response.status_code == 401:
                raise TangoAuthError(
                    "Invalid API key or authentication required", response.status_code
                )
            elif response.status_code == 404:
                raise TangoNotFoundError("Resource not found", response.status_code)
            elif response.status_code == 400:
                error_data = response.json() if response.content else {}
                error_msg = "Invalid request parameters"
                if error_data:
                    # Try to extract a more specific error message
                    if isinstance(error_data, dict):
                        detail = (
                            error_data.get("detail")
                            or error_data.get("message")
                            or error_data.get("error")
                        )
                        if detail:
                            error_msg = f"Invalid request parameters: {detail}"
                raise TangoValidationError(
                    error_msg,
                    response.status_code,
                    error_data,
                )
            elif response.status_code == 429:
                error_data = response.json() if response.content else {}
                detail = error_data.get("detail", "Rate limit exceeded")
                raise TangoRateLimitError(detail, response.status_code, error_data)
            elif not response.is_success:
                raise TangoAPIError(
                    f"API request failed with status {response.status_code}", response.status_code
                )

            return response.json() if response.content else {}

        except httpx.HTTPError as e:
            raise TangoAPIError(f"Request failed: {str(e)}") from e

    def _get(self, endpoint: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Make a GET request"""
        return self._request("GET", endpoint, params=params)

    def _post(
        self,
        endpoint: str,
        json_data: dict[str, Any] | None = None,
        *,
        json: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make a POST request.

        Accepts either ``json_data`` (positional) or ``json=`` (keyword) for
        backward compatibility with internal callers and docs examples.
        Passing both raises ``TangoValidationError`` rather than silently
        picking one — that ambiguity would hide caller bugs.
        """
        if json_data is not None and json is not None:
            raise TangoValidationError("_post: pass `json_data` or `json`, not both.")
        body = json_data if json_data is not None else json
        if body is None:
            body = {}
        return self._request("POST", endpoint, json_data=body)

    def _patch(
        self,
        endpoint: str,
        json_data: dict[str, Any] | None = None,
        *,
        json: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make a PATCH request.

        Accepts either ``json_data`` (positional) or ``json=`` (keyword) for
        backward compatibility with internal callers and docs examples.
        Passing both raises ``TangoValidationError`` rather than silently
        picking one — that ambiguity would hide caller bugs.
        """
        if json_data is not None and json is not None:
            raise TangoValidationError("_patch: pass `json_data` or `json`, not both.")
        body = json_data if json_data is not None else json
        if body is None:
            body = {}
        return self._request("PATCH", endpoint, json_data=body)

    def _delete(self, endpoint: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Make a DELETE request"""
        return self._request("DELETE", endpoint, params=params)

    # ============================================================================
    # Shape Parsing Utilities
    # ============================================================================

    def _parse_response_with_shape(
        self,
        data: dict[str, Any],
        shape: str,
        base_model: type,
        flat: bool = False,
        flat_lists: bool = False,
        joiner: str = ".",
    ) -> Any:
        """
        Parse API response using dynamic model generation

        Args:
            data: Raw API response data (dictionary)
            shape: Shape string specifying fields to include
            base_model: Base static model class (e.g., Contract, Agency)
            flat: Whether the response is flattened with dot notation
            flat_lists: Whether arrays are flattened with indexed keys

        Returns:
            Instance of dynamically generated type with parsed data

        Raises:
            ShapeError: If shape parsing or validation fails
            TypeGenerationError: If type generation fails
            ModelInstantiationError: If instance creation fails
        """

        # Parse shape string
        shape_spec = self._shape_parser.parse(shape)
        shape_spec.is_flat = flat
        shape_spec.is_flat_lists = flat_lists

        # Validate shape against model
        self._shape_parser.validate(shape_spec, base_model)

        # Generate dynamic type
        dynamic_type = self._type_generator.generate_type(
            shape_spec=shape_spec,
            base_model=base_model,
            type_name=f"{base_model.__name__}Shaped",
        )

        # Unflatten if necessary
        if flat:
            data = self._unflatten_response(data, joiner=joiner)

        # Create typed instance
        return self._model_factory.create_instance(
            data=data,
            shape_spec=shape_spec,
            base_model=base_model,
            dynamic_type=dynamic_type,
        )

    def _unflatten_response(self, data: dict[str, Any], joiner: str = ".") -> dict[str, Any]:
        """
        Unflatten a flat response into nested structure.

        When flat=True is used with response shaping, the API returns dot-notation keys
        like "recipient.display_name" instead of nested {"recipient": {"display_name": "..."}}.

        This utility converts flat responses back to nested format for existing parsers.

        Args:
            data: Flattened response data
            joiner: Character used to join nested keys (default: ".")

        Returns:
            Nested dictionary structure
        """
        # Check if response is actually flat (has dot-notation keys)
        has_flat_keys = any(joiner in str(key) for key in data.keys())
        if not has_flat_keys:
            return data  # Already nested, return as-is

        result: dict[str, Any] = {}

        for flat_key, value in data.items():
            # Split the key by joiner
            parts = str(flat_key).split(joiner)

            # Navigate/create nested structure
            current = result
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                elif not isinstance(current[part], dict):
                    # Key collision - flat key overwrites existing value
                    current[part] = {}
                current = current[part]

            # Set the final value
            current[parts[-1]] = value

        return result

    # ============================================================================
    # Data Parsing Utilities
    # ============================================================================

    def _parse_date(self, date_string: str | None) -> date | None:
        """Parse date string to date object"""
        if not date_string:
            return None
        try:
            # Handle various date formats
            if "T" in date_string:
                return datetime.fromisoformat(date_string.replace("Z", "+00:00")).date()
            else:
                return datetime.strptime(date_string, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            return None

    def _parse_datetime(self, datetime_string: str | None) -> datetime | None:
        """Parse datetime string to datetime object"""
        if not datetime_string:
            return None
        try:
            return datetime.fromisoformat(datetime_string.replace("Z", "+00:00"))
        except (ValueError, TypeError):
            return None

    def _parse_decimal(self, value: Any) -> Decimal | None:
        """Parse numeric value to Decimal"""
        if value is None:
            return None
        try:
            return Decimal(str(value))
        except (ValueError, TypeError, Exception):
            # Catch InvalidOperation and other decimal exceptions
            return None

    def _parse_agency(self, data: dict[str, Any]) -> Agency | None:
        """Parse agency data (for endpoints without shape support)

        Returns an Agency object.
        Handles both standard agency fields and office fields (office_code/office_name).
        """
        if not data:
            return None
        try:
            department = None
            if data.get("department"):
                dept_data = data["department"]
                if isinstance(dept_data, dict):
                    from .models import Department

                    department = Department(
                        name=dept_data.get("name", ""), code=str(dept_data.get("code", ""))
                    )

            # Handle office fields (office_code/office_name) when standard fields aren't present
            code = data.get("code") or data.get("office_code") or data.get("agency_code", "")
            name = data.get("name") or data.get("office_name") or data.get("agency_name", "")

            return Agency(
                code=code,
                name=name,
                abbreviation=data.get("abbreviation"),
                department=department,
            )
        except (KeyError, TypeError):
            return None

    def _parse_location(self, data: dict[str, Any] | None) -> Location | None:
        """Parse location data

        Returns a Location object.
        """
        if not data:
            return None
        try:
            from .models import Location

            # Map zip to zip_code if zip_code is not present
            zip_code = data.get("zip_code") or data.get("zip")
            return Location(
                address_line1=data.get("address_line_1") or data.get("address_line1"),
                address_line2=data.get("address_line_2") or data.get("address_line2"),
                city=data.get("city"),
                state=data.get("state"),
                state_code=data.get("state_code"),
                zip_code=zip_code,
                zip=data.get("zip"),
                zip4=data.get("zip4"),
                country=data.get("country"),
                country_code=data.get("country_code"),
                county=data.get("county"),
                congressional_district=data.get("congressional_district"),
                latitude=data.get("latitude"),
                longitude=data.get("longitude"),
            )
        except (KeyError, TypeError):
            return None

    # ============================================================================
    # API Endpoints
    # ============================================================================

    # Agency endpoints
    def list_agencies(
        self, page: int = 1, limit: int = 25, search: str | None = None
    ) -> PaginatedResponse:
        """List all agencies"""
        params: dict[str, Any] = {"page": page, "limit": min(limit, 100)}
        if search:
            params["search"] = search
        data = self._get("/api/agencies/", params)
        return PaginatedResponse(
            count=data["count"],
            next=data.get("next"),
            previous=data.get("previous"),
            results=[
                ag
                for ag in (self._parse_agency(agency) for agency in data["results"])
                if ag is not None
            ],
        )

    def get_agency(self, code: str) -> Agency:
        """Get agency by code

        Returns:
            Agency object
        """
        data = self._get(f"/api/agencies/{code}/")
        agency = self._parse_agency(data)
        if agency is None:
            raise TangoNotFoundError(f"Agency '{code}' not found", 404)
        return agency

    def list_offices(
        self,
        page: int = 1,
        limit: int = 25,
        search: str | None = None,
    ) -> PaginatedResponse:
        """List offices (`/api/offices/`)."""
        params: dict[str, Any] = {"page": page, "limit": min(limit, 100)}
        if search is not None:
            params["search"] = search
        data = self._get("/api/offices/", params)
        return PaginatedResponse(
            count=data.get("count", 0),
            next=data.get("next"),
            previous=data.get("previous"),
            results=data.get("results", []),
        )

    def get_office(self, code: str) -> dict[str, Any]:
        """Get a single office by code (`/api/offices/{code}/`)."""
        return self._get(f"/api/offices/{code}/")

    def list_organizations(
        self,
        page: int = 1,
        limit: int = 25,
        shape: str | None = None,
        flat: bool = False,
        flat_lists: bool = False,
        cgac: str | None = None,
        include_inactive: bool | None = None,
        level: int | None = None,
        parent: str | None = None,
        search: str | None = None,
        type: str | None = None,
    ) -> PaginatedResponse:
        """List organizations (`/api/organizations/`)."""
        params: dict[str, Any] = {"page": page, "limit": min(limit, 100)}
        if shape is None:
            shape = ShapeConfig.ORGANIZATIONS_MINIMAL
        if shape:
            params["shape"] = shape
            if flat:
                params["flat"] = "true"
            if flat_lists:
                params["flat_lists"] = "true"
        if cgac is not None:
            params["cgac"] = cgac
        if include_inactive is not None:
            params["include_inactive"] = include_inactive
        if level is not None:
            params["level"] = level
        if parent is not None:
            params["parent"] = parent
        if search is not None:
            params["search"] = search
        if type is not None:
            params["type"] = type
        data = self._get("/api/organizations/", params)
        results = [
            self._parse_response_with_shape(obj, shape, Organization, flat, flat_lists)
            for obj in data.get("results", [])
        ]
        return PaginatedResponse(
            count=data.get("count", 0),
            next=data.get("next"),
            previous=data.get("previous"),
            results=results,
        )

    def get_organization(
        self,
        fh_key: str,
        shape: str | None = None,
        flat: bool = False,
        flat_lists: bool = False,
    ) -> Any:
        """Get a single organization by fh_key (`/api/organizations/{fh_key}/`)."""
        params: dict[str, Any] = {}
        if shape is None:
            shape = ShapeConfig.ORGANIZATIONS_MINIMAL
        if shape:
            params["shape"] = shape
            if flat:
                params["flat"] = "true"
            if flat_lists:
                params["flat_lists"] = "true"
        data = self._get(f"/api/organizations/{fh_key}/", params)
        return self._parse_response_with_shape(data, shape, Organization, flat, flat_lists)

    # Contract endpoints
    def list_contracts(
        self,
        cursor: str | None = None,
        limit: int = 25,
        shape: str | None = None,
        flat: bool = False,
        flat_lists: bool = False,
        filters: SearchFilters | dict[str, Any] | None = None,
        award_date: str | None = None,
        award_date_gte: str | None = None,
        award_date_lte: str | None = None,
        award_type: str | None = None,
        awarding_agency: str | None = None,
        expiring_gte: str | None = None,
        expiring_lte: str | None = None,
        fiscal_year: int | None = None,
        fiscal_year_gte: int | None = None,
        fiscal_year_lte: int | None = None,
        funding_agency: str | None = None,
        obligated_gte: str | None = None,
        obligated_lte: str | None = None,
        ordering: str | None = None,
        piid: str | None = None,
        pop_end_date_gte: str | None = None,
        pop_end_date_lte: str | None = None,
        pop_start_date_gte: str | None = None,
        pop_start_date_lte: str | None = None,
        solicitation_identifier: str | None = None,
        keyword: str | None = None,
        naics_code: str | None = None,
        psc_code: str | None = None,
        recipient_name: str | None = None,
        recipient_uei: str | None = None,
        set_aside_type: str | None = None,
        sort: str | None = None,
        order: str | None = None,
    ) -> PaginatedResponse:
        """
        List contracts with optional filtering

        Args:
            cursor: Cursor token for pagination (from previous response.cursor).
                   If not provided, starts from the beginning.
            limit: Results per page (max 100)
            shape: Response shape string (defaults to minimal shape).
                   Use None to disable shaping, ShapeConfig.CONTRACTS_MINIMAL for minimal,
                   or provide custom shape string
            flat: If True, flatten nested objects in shaped response using dot notation
            flat_lists: If True, flatten arrays using indexed keys (e.g., items.0.field)
            filters: Optional SearchFilters object or dict for backward compatibility.
            award_date: Award date (exact match, YYYY-MM-DD)
            award_date_gte: Award date >= (YYYY-MM-DD)
            award_date_lte: Award date <= (YYYY-MM-DD)
            award_type: Award type code
            awarding_agency: Awarding agency code (e.g., "4700" for GSA)
            expiring_gte: Expiring on or after date
            expiring_lte: Expiring on or before date
            fiscal_year: Fiscal year (exact match)
            fiscal_year_gte: Fiscal year >=
            fiscal_year_lte: Fiscal year <=
            funding_agency: Funding agency code
            obligated_gte: Obligated amount >=
            obligated_lte: Obligated amount <=
            ordering: Sort ordering (prefix with '-' for descending)
            piid: Procurement Instrument Identifier
            pop_end_date_gte: Period of performance end date >=
            pop_end_date_lte: Period of performance end date <=
            pop_start_date_gte: Period of performance start date >=
            pop_start_date_lte: Period of performance start date <=
            solicitation_identifier: Solicitation ID
            keyword: Search contract descriptions (mapped to 'search' API param)
            naics_code: NAICS code (mapped to 'naics' API param)
            psc_code: PSC code (mapped to 'psc' API param)
            recipient_name: Vendor/recipient name (mapped to 'recipient' API param)
            recipient_uei: Vendor UEI (mapped to 'uei' API param)
            set_aside_type: Set-aside type (mapped to 'set_aside' API param)
            sort: Field to sort by (combined with 'order' to produce 'ordering')
            order: Sort order ('asc' or 'desc', default 'asc')

        Examples:
            >>> contracts = client.list_contracts(limit=10)
            >>> contracts = client.list_contracts(
            ...     awarding_agency="4700",
            ...     award_date_gte="2023-01-01",
            ...     limit=25,
            ... )
            >>> contracts = client.list_contracts(keyword="software development")
        """
        params: dict[str, Any] = {"limit": min(limit, 100)}
        if cursor:
            params["cursor"] = cursor
        # /api/contracts/ is cursor-only (KeysetPagination). When no cursor is
        # supplied, send neither page nor cursor — the API returns the first
        # page by default. (Previously sent page=1, which the endpoint ignores.)

        # Handle legacy filters parameter (backward compatibility)
        filter_dict: dict[str, Any] = {}
        if filters is not None:
            if hasattr(filters, "to_dict"):
                filter_dict = filters.to_dict()
            else:
                filter_dict = dict(filters)

            if limit == 25 and "limit" in filter_dict:
                params["limit"] = min(filter_dict.pop("limit", 25), 100)

        if shape is None:
            shape = ShapeConfig.CONTRACTS_MINIMAL
        if shape:
            params["shape"] = shape
            if flat:
                params["flat"] = "true"
            if flat_lists:
                params["flat_lists"] = "true"

        api_param_mapping = {
            "naics_code": "naics",
            "keyword": "search",
            "psc_code": "psc",
            "recipient_name": "recipient",
            "recipient_uei": "uei",
            "set_aside_type": "set_aside",
        }

        # Collect explicit filter params; legacy filter_dict values are used as fallback
        filter_params: dict[str, Any] = {}
        for key, val in (
            ("award_date", award_date),
            ("award_date_gte", award_date_gte),
            ("award_date_lte", award_date_lte),
            ("award_type", award_type),
            ("awarding_agency", awarding_agency),
            ("expiring_gte", expiring_gte),
            ("expiring_lte", expiring_lte),
            ("fiscal_year", fiscal_year),
            ("fiscal_year_gte", fiscal_year_gte),
            ("fiscal_year_lte", fiscal_year_lte),
            ("funding_agency", funding_agency),
            ("obligated_gte", obligated_gte),
            ("obligated_lte", obligated_lte),
            ("ordering", ordering),
            ("piid", piid),
            ("pop_end_date_gte", pop_end_date_gte),
            ("pop_end_date_lte", pop_end_date_lte),
            ("pop_start_date_gte", pop_start_date_gte),
            ("pop_start_date_lte", pop_start_date_lte),
            ("solicitation_identifier", solicitation_identifier),
            ("keyword", keyword),
            ("naics_code", naics_code),
            ("psc_code", psc_code),
            ("recipient_name", recipient_name),
            ("recipient_uei", recipient_uei),
            ("set_aside_type", set_aside_type),
        ):
            if val is not None:
                filter_params[key] = val

        # Merge: explicit params take precedence over legacy filter_dict
        excluded = {"shape", "flat", "flat_lists", "cursor", "page", "limit"}
        for k, v in filter_dict.items():
            if k not in excluded and k not in filter_params and v is not None:
                filter_params[k] = v

        # Handle sort + order → ordering conversion
        sort_field = sort or filter_dict.get("sort")
        sort_order = order or filter_dict.get("order")
        if sort_field and "ordering" not in filter_params:
            prefix = "-" if sort_order == "desc" else ""
            filter_params["ordering"] = f"{prefix}{sort_field}"

        # Apply parameter name mapping and add to params
        for key, value in filter_params.items():
            api_key = api_param_mapping.get(key, key)
            params[api_key] = value

        data = self._get("/api/contracts/", params)

        # Always use dynamic parsing
        results = [
            self._parse_response_with_shape(contract, shape, Contract, flat, flat_lists)
            for contract in data["results"]
        ]

        return PaginatedResponse(
            count=data["count"],
            next=data.get("next"),
            previous=data.get("previous"),
            results=results,
            cursor=data.get("cursor"),
        )

    def get_contract(
        self,
        key: str,
        shape: str | None = None,
        flat: bool = False,
        flat_lists: bool = False,
        joiner: str = ".",
    ) -> Any:
        """Get a single contract by key (`/api/contracts/{key}/`)."""
        params: dict[str, Any] = {}
        if shape is None:
            shape = ShapeConfig.CONTRACTS_MINIMAL
        if shape:
            params["shape"] = shape
            if flat:
                params["flat"] = "true"
                if joiner:
                    params["joiner"] = joiner
            if flat_lists:
                params["flat_lists"] = "true"
        data = self._get(f"/api/contracts/{key}/", params)
        return self._parse_response_with_shape(
            data, shape, Contract, flat, flat_lists, joiner=joiner
        )

    def get_contract_subawards(
        self,
        key: str,
        page: int = 1,
        limit: int = 25,
        shape: str | None = None,
        flat: bool = False,
        flat_lists: bool = False,
        ordering: str | None = None,
    ) -> PaginatedResponse:
        """List subawards under a contract (`/api/contracts/{key}/subawards/`)."""
        params: dict[str, Any] = {"page": page, "limit": min(limit, 100)}
        if shape is None:
            shape = ShapeConfig.SUBAWARDS_MINIMAL
        if shape:
            params["shape"] = shape
            if flat:
                params["flat"] = "true"
            if flat_lists:
                params["flat_lists"] = "true"
        if ordering:
            params["ordering"] = ordering
        data = self._get(f"/api/contracts/{key}/subawards/", params)
        raw_results = data.get("results") or []
        results = [
            self._parse_response_with_shape(obj, shape, Subaward, flat, flat_lists)
            for obj in raw_results
        ]
        return PaginatedResponse(
            count=int(data.get("count") or len(results)),
            next=data.get("next"),
            previous=data.get("previous"),
            results=results,
            cursor=data.get("cursor"),
        )

    def get_contract_transactions(
        self,
        key: str,
        limit: int = 100,
        cursor: str | None = None,
        ordering: str | None = None,
    ) -> PaginatedResponse:
        """List transactions under a contract (`/api/contracts/{key}/transactions/`)."""
        params: dict[str, Any] = {"limit": min(limit, 500)}
        if cursor:
            params["cursor"] = cursor
        if ordering:
            params["ordering"] = ordering
        data = self._get(f"/api/contracts/{key}/transactions/", params)
        return PaginatedResponse(
            count=int(data.get("count") or len(data.get("results") or [])),
            next=data.get("next"),
            previous=data.get("previous"),
            results=data.get("results") or [],
            cursor=data.get("cursor"),
        )

    # ============================================================================
    # IDVs (Awards)
    # ============================================================================

    def list_idvs(
        self,
        limit: int = 25,
        cursor: str | None = None,
        shape: str | None = None,
        flat: bool = False,
        flat_lists: bool = False,
        joiner: str = ".",
        award_date: str | None = None,
        award_date_gte: str | None = None,
        award_date_lte: str | None = None,
        awarding_agency: str | None = None,
        expiring_gte: str | None = None,
        expiring_lte: str | None = None,
        fiscal_year: int | None = None,
        fiscal_year_gte: int | None = None,
        fiscal_year_lte: int | None = None,
        funding_agency: str | None = None,
        idv_type: str | None = None,
        last_date_to_order_gte: str | None = None,
        last_date_to_order_lte: str | None = None,
        naics: str | None = None,
        ordering: str | None = None,
        piid: str | None = None,
        pop_start_date_gte: str | None = None,
        pop_start_date_lte: str | None = None,
        psc: str | None = None,
        recipient: str | None = None,
        search: str | None = None,
        set_aside: str | None = None,
        solicitation_identifier: str | None = None,
        uei: str | None = None,
    ) -> PaginatedResponse:
        """
        List IDVs (indefinite delivery vehicles) with keyset pagination.

        This mirrors `/api/idvs/` and supports the same filter parameters as the API,
        plus shaping via `shape`.
        """
        params: dict[str, Any] = {"limit": min(limit, 100)}
        if cursor:
            params["cursor"] = cursor

        if shape is None:
            shape = ShapeConfig.IDVS_MINIMAL
        if shape:
            params["shape"] = shape
            if flat:
                params["flat"] = "true"
                if joiner:
                    params["joiner"] = joiner
            if flat_lists:
                params["flat_lists"] = "true"

        for key, val in (
            ("award_date", award_date),
            ("award_date_gte", award_date_gte),
            ("award_date_lte", award_date_lte),
            ("awarding_agency", awarding_agency),
            ("expiring_gte", expiring_gte),
            ("expiring_lte", expiring_lte),
            ("fiscal_year", fiscal_year),
            ("fiscal_year_gte", fiscal_year_gte),
            ("fiscal_year_lte", fiscal_year_lte),
            ("funding_agency", funding_agency),
            ("idv_type", idv_type),
            ("last_date_to_order_gte", last_date_to_order_gte),
            ("last_date_to_order_lte", last_date_to_order_lte),
            ("naics", naics),
            ("ordering", ordering),
            ("piid", piid),
            ("pop_start_date_gte", pop_start_date_gte),
            ("pop_start_date_lte", pop_start_date_lte),
            ("psc", psc),
            ("recipient", recipient),
            ("search", search),
            ("set_aside", set_aside),
            ("solicitation_identifier", solicitation_identifier),
            ("uei", uei),
        ):
            if val is not None:
                params[key] = val

        data = self._get("/api/idvs/", params)

        raw_results = data.get("results") or []
        results = [
            self._parse_response_with_shape(obj, shape, IDV, flat, flat_lists, joiner=joiner)
            for obj in raw_results
        ]

        return PaginatedResponse(
            count=int(data.get("count") or len(results)),
            next=data.get("next"),
            previous=data.get("previous"),
            results=results,
            page_metadata=data.get("page_metadata"),
        )

    def get_idv(
        self,
        key: str,
        shape: str | None = None,
        flat: bool = False,
        flat_lists: bool = False,
        joiner: str = ".",
    ) -> Any:
        """Get a single IDV by award key (`/api/idvs/{key}/`)."""
        params: dict[str, Any] = {}
        if shape is None:
            shape = ShapeConfig.IDVS_COMPREHENSIVE
        if shape:
            params["shape"] = shape
            if flat:
                params["flat"] = "true"
                if joiner:
                    params["joiner"] = joiner
            if flat_lists:
                params["flat_lists"] = "true"

        data = self._get(f"/api/idvs/{key}/", params)
        return self._parse_response_with_shape(data, shape, IDV, flat, flat_lists, joiner=joiner)

    def list_idv_awards(
        self,
        key: str,
        limit: int = 25,
        cursor: str | None = None,
        shape: str | None = None,
        flat: bool = False,
        flat_lists: bool = False,
        joiner: str = ".",
        filters: SearchFilters | dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> PaginatedResponse:
        """
        List child awards (contracts) under an IDV (`/api/idvs/{key}/awards/`).

        This endpoint behaves like `/api/contracts/`, but scoped to a specific IDV.
        """
        # Reuse list_contracts mapping and behavior by calling the endpoint directly.
        params: dict[str, Any] = {"limit": min(limit, 100)}
        if cursor:
            params["cursor"] = cursor

        if shape is None:
            shape = ShapeConfig.CONTRACTS_MINIMAL
        if shape:
            params["shape"] = shape
            if flat:
                params["flat"] = "true"
                if joiner:
                    params["joiner"] = joiner
            if flat_lists:
                params["flat_lists"] = "true"

        filter_dict: dict[str, Any] = {}
        if filters is not None:
            filter_dict = filters.to_dict() if hasattr(filters, "to_dict") else filters
        filter_params = {**filter_dict, **kwargs}
        for param in {"shape", "flat", "flat_lists", "joiner", "limit", "cursor"}:
            filter_params.pop(param, None)

        # Same mapping used by list_contracts()
        api_param_mapping = {
            "naics_code": "naics",
            "keyword": "search",
            "psc_code": "psc",
            "recipient_name": "recipient",
            "recipient_uei": "uei",
            "set_aside_type": "set_aside",
        }
        sort_field = filter_params.pop("sort", None)
        sort_order = filter_params.pop("order", None)
        if sort_field:
            prefix = "-" if sort_order == "desc" else ""
            filter_params["ordering"] = f"{prefix}{sort_field}"

        api_params: dict[str, Any] = {}
        for k, v in filter_params.items():
            if v is None:
                continue
            api_params[api_param_mapping.get(k, k)] = v
        params.update(api_params)

        data = self._get(f"/api/idvs/{key}/awards/", params)
        raw_results = data.get("results") or []
        results = [
            self._parse_response_with_shape(obj, shape, Contract, flat, flat_lists, joiner=joiner)
            for obj in raw_results
        ]

        return PaginatedResponse(
            count=int(data.get("count") or len(results)),
            next=data.get("next"),
            previous=data.get("previous"),
            results=results,
            page_metadata=data.get("page_metadata"),
        )

    def list_idv_child_idvs(
        self,
        key: str,
        limit: int = 25,
        cursor: str | None = None,
        shape: str | None = None,
        flat: bool = False,
        flat_lists: bool = False,
        joiner: str = ".",
        **filters: Any,
    ) -> PaginatedResponse:
        """List child IDVs under an IDV (`/api/idvs/{key}/idvs/`)."""
        params: dict[str, Any] = {"limit": min(limit, 100)}
        if cursor:
            params["cursor"] = cursor

        if shape is None:
            shape = ShapeConfig.IDVS_MINIMAL
        if shape:
            params["shape"] = shape
            if flat:
                params["flat"] = "true"
                if joiner:
                    params["joiner"] = joiner
            if flat_lists:
                params["flat_lists"] = "true"

        params.update({k: v for k, v in filters.items() if v is not None})

        data = self._get(f"/api/idvs/{key}/idvs/", params)
        raw_results = data.get("results") or []
        results = [
            self._parse_response_with_shape(obj, shape, IDV, flat, flat_lists, joiner=joiner)
            for obj in raw_results
        ]

        return PaginatedResponse(
            count=int(data.get("count") or len(results)),
            next=data.get("next"),
            previous=data.get("previous"),
            results=results,
            page_metadata=data.get("page_metadata"),
        )

    def list_idv_transactions(
        self, key: str, limit: int = 100, cursor: str | None = None
    ) -> PaginatedResponse:
        """List transactions for an IDV (`/api/idvs/{key}/transactions/`)."""
        params: dict[str, Any] = {"limit": min(limit, 500)}
        if cursor:
            params["cursor"] = cursor
        data = self._get(f"/api/idvs/{key}/transactions/", params)
        return PaginatedResponse(
            count=int(data.get("count") or len(data.get("results") or [])),
            next=data.get("next"),
            previous=data.get("previous"),
            results=data.get("results") or [],
            page_metadata=data.get("page_metadata"),
        )

    def list_otas(
        self,
        limit: int = 25,
        cursor: str | None = None,
        shape: str | None = None,
        flat: bool = False,
        flat_lists: bool = False,
        joiner: str = ".",
        award_date: str | None = None,
        award_date_gte: str | None = None,
        award_date_lte: str | None = None,
        awarding_agency: str | None = None,
        expiring_gte: str | None = None,
        expiring_lte: str | None = None,
        fiscal_year: int | None = None,
        fiscal_year_gte: int | None = None,
        fiscal_year_lte: int | None = None,
        funding_agency: str | None = None,
        ordering: str | None = None,
        piid: str | None = None,
        pop_end_date_gte: str | None = None,
        pop_end_date_lte: str | None = None,
        pop_start_date_gte: str | None = None,
        pop_start_date_lte: str | None = None,
        psc: str | None = None,
        recipient: str | None = None,
        search: str | None = None,
        uei: str | None = None,
    ) -> PaginatedResponse:
        """List OTAs (Other Transaction Agreements) (`/api/otas/`). Keyset pagination."""
        params: dict[str, Any] = {"limit": min(limit, 100)}
        if cursor:
            params["cursor"] = cursor
        if shape is None:
            shape = ShapeConfig.OTAS_MINIMAL
        if shape:
            params["shape"] = shape
            if flat:
                params["flat"] = "true"
                if joiner:
                    params["joiner"] = joiner
            if flat_lists:
                params["flat_lists"] = "true"
        for key, val in (
            ("award_date", award_date),
            ("award_date_gte", award_date_gte),
            ("award_date_lte", award_date_lte),
            ("awarding_agency", awarding_agency),
            ("expiring_gte", expiring_gte),
            ("expiring_lte", expiring_lte),
            ("fiscal_year", fiscal_year),
            ("fiscal_year_gte", fiscal_year_gte),
            ("fiscal_year_lte", fiscal_year_lte),
            ("funding_agency", funding_agency),
            ("ordering", ordering),
            ("piid", piid),
            ("pop_end_date_gte", pop_end_date_gte),
            ("pop_end_date_lte", pop_end_date_lte),
            ("pop_start_date_gte", pop_start_date_gte),
            ("pop_start_date_lte", pop_start_date_lte),
            ("psc", psc),
            ("recipient", recipient),
            ("search", search),
            ("uei", uei),
        ):
            if val is not None:
                params[key] = val
        data = self._get("/api/otas/", params)
        raw_results = data.get("results") or []
        results = [
            self._parse_response_with_shape(obj, shape, OTA, flat, flat_lists, joiner=joiner)
            for obj in raw_results
        ]
        return PaginatedResponse(
            count=int(data.get("count") or len(results)),
            next=data.get("next"),
            previous=data.get("previous"),
            results=results,
            cursor=data.get("cursor"),
            page_metadata=data.get("page_metadata"),
        )

    def get_ota(
        self,
        key: str,
        shape: str | None = None,
        flat: bool = False,
        flat_lists: bool = False,
        joiner: str = ".",
    ) -> Any:
        """Get a single OTA by key (`/api/otas/{key}/`)."""
        params: dict[str, Any] = {}
        if shape is None:
            shape = ShapeConfig.OTAS_MINIMAL
        if shape:
            params["shape"] = shape
            if flat:
                params["flat"] = "true"
                if joiner:
                    params["joiner"] = joiner
            if flat_lists:
                params["flat_lists"] = "true"
        data = self._get(f"/api/otas/{key}/", params)
        return self._parse_response_with_shape(data, shape, OTA, flat, flat_lists, joiner=joiner)

    def list_otidvs(
        self,
        limit: int = 25,
        cursor: str | None = None,
        shape: str | None = None,
        flat: bool = False,
        flat_lists: bool = False,
        joiner: str = ".",
        award_date: str | None = None,
        award_date_gte: str | None = None,
        award_date_lte: str | None = None,
        awarding_agency: str | None = None,
        expiring_gte: str | None = None,
        expiring_lte: str | None = None,
        fiscal_year: int | None = None,
        fiscal_year_gte: int | None = None,
        fiscal_year_lte: int | None = None,
        funding_agency: str | None = None,
        ordering: str | None = None,
        piid: str | None = None,
        pop_end_date_gte: str | None = None,
        pop_end_date_lte: str | None = None,
        pop_start_date_gte: str | None = None,
        pop_start_date_lte: str | None = None,
        psc: str | None = None,
        recipient: str | None = None,
        search: str | None = None,
        uei: str | None = None,
    ) -> PaginatedResponse:
        """List OTIDVs (Other Transaction IDVs) (`/api/otidvs/`). Keyset pagination."""
        params: dict[str, Any] = {"limit": min(limit, 100)}
        if cursor:
            params["cursor"] = cursor
        if shape is None:
            shape = ShapeConfig.OTIDVS_MINIMAL
        if shape:
            params["shape"] = shape
            if flat:
                params["flat"] = "true"
                if joiner:
                    params["joiner"] = joiner
            if flat_lists:
                params["flat_lists"] = "true"
        for key, val in (
            ("award_date", award_date),
            ("award_date_gte", award_date_gte),
            ("award_date_lte", award_date_lte),
            ("awarding_agency", awarding_agency),
            ("expiring_gte", expiring_gte),
            ("expiring_lte", expiring_lte),
            ("fiscal_year", fiscal_year),
            ("fiscal_year_gte", fiscal_year_gte),
            ("fiscal_year_lte", fiscal_year_lte),
            ("funding_agency", funding_agency),
            ("ordering", ordering),
            ("piid", piid),
            ("pop_end_date_gte", pop_end_date_gte),
            ("pop_end_date_lte", pop_end_date_lte),
            ("pop_start_date_gte", pop_start_date_gte),
            ("pop_start_date_lte", pop_start_date_lte),
            ("psc", psc),
            ("recipient", recipient),
            ("search", search),
            ("uei", uei),
        ):
            if val is not None:
                params[key] = val
        data = self._get("/api/otidvs/", params)
        raw_results = data.get("results") or []
        results = [
            self._parse_response_with_shape(obj, shape, OTIDV, flat, flat_lists, joiner=joiner)
            for obj in raw_results
        ]
        return PaginatedResponse(
            count=int(data.get("count") or len(results)),
            next=data.get("next"),
            previous=data.get("previous"),
            results=results,
            cursor=data.get("cursor"),
            page_metadata=data.get("page_metadata"),
        )

    def get_otidv(
        self,
        key: str,
        shape: str | None = None,
        flat: bool = False,
        flat_lists: bool = False,
        joiner: str = ".",
    ) -> Any:
        """Get a single OTIDV by key (`/api/otidvs/{key}/`)."""
        params: dict[str, Any] = {}
        if shape is None:
            shape = ShapeConfig.OTIDVS_MINIMAL
        if shape:
            params["shape"] = shape
            if flat:
                params["flat"] = "true"
                if joiner:
                    params["joiner"] = joiner
            if flat_lists:
                params["flat_lists"] = "true"
        data = self._get(f"/api/otidvs/{key}/", params)
        return self._parse_response_with_shape(data, shape, OTIDV, flat, flat_lists, joiner=joiner)

    def list_otidv_awards(
        self,
        key: str,
        limit: int = 25,
        cursor: str | None = None,
        shape: str | None = None,
        flat: bool = False,
        flat_lists: bool = False,
        joiner: str = ".",
        ordering: str | None = None,
    ) -> PaginatedResponse:
        """List child awards under an OTIDV (`/api/otidvs/{key}/awards/`).

        Args:
            key: The OTIDV key.
            limit: Results per page (max 100).
            cursor: Cursor token for keyset pagination.
            shape: Response shape string (defaults to minimal contract shape).
            flat: If True, flatten nested objects using dot notation.
            flat_lists: If True, flatten arrays using indexed keys.
            joiner: Separator used when flattening.
            ordering: Server-side sort (prefix with '-' for descending).
        """
        params: dict[str, Any] = {"limit": min(limit, 100)}
        if cursor:
            params["cursor"] = cursor
        if shape is None:
            shape = ShapeConfig.CONTRACTS_MINIMAL
        if shape:
            params["shape"] = shape
            if flat:
                params["flat"] = "true"
                if joiner:
                    params["joiner"] = joiner
            if flat_lists:
                params["flat_lists"] = "true"
        if ordering:
            params["ordering"] = ordering
        data = self._get(f"/api/otidvs/{key}/awards/", params)
        raw_results = data.get("results") or []
        results = [
            self._parse_response_with_shape(obj, shape, Contract, flat, flat_lists, joiner=joiner)
            for obj in raw_results
        ]
        return PaginatedResponse(
            count=int(data.get("count") or len(results)),
            next=data.get("next"),
            previous=data.get("previous"),
            results=results,
            cursor=data.get("cursor"),
            page_metadata=data.get("page_metadata"),
        )

    def list_subawards(
        self,
        page: int = 1,
        limit: int = 25,
        shape: str | None = None,
        flat: bool = False,
        flat_lists: bool = False,
        award_key: str | None = None,
        awarding_agency: str | None = None,
        fiscal_year: int | None = None,
        fiscal_year_gte: int | None = None,
        fiscal_year_lte: int | None = None,
        funding_agency: str | None = None,
        ordering: str | None = None,
        prime_uei: str | None = None,
        recipient: str | None = None,
        sub_uei: str | None = None,
    ) -> PaginatedResponse:
        """List subawards (`/api/subawards/`)."""
        params: dict[str, Any] = {"page": page, "limit": min(limit, 100)}
        if shape is None:
            shape = ShapeConfig.SUBAWARDS_MINIMAL
        if shape:
            params["shape"] = shape
            if flat:
                params["flat"] = "true"
            if flat_lists:
                params["flat_lists"] = "true"
        for key, val in (
            ("award_key", award_key),
            ("awarding_agency", awarding_agency),
            ("fiscal_year", fiscal_year),
            ("fiscal_year_gte", fiscal_year_gte),
            ("fiscal_year_lte", fiscal_year_lte),
            ("funding_agency", funding_agency),
            ("ordering", ordering),
            ("prime_uei", prime_uei),
            ("recipient", recipient),
            ("sub_uei", sub_uei),
        ):
            if val is not None:
                params[key] = val
        data = self._get("/api/subawards/", params)
        results = [
            self._parse_response_with_shape(obj, shape, Subaward, flat, flat_lists)
            for obj in data.get("results", [])
        ]
        return PaginatedResponse(
            count=data.get("count", 0),
            next=data.get("next"),
            previous=data.get("previous"),
            results=results,
        )

    def get_subaward(
        self,
        key: str,
        shape: str | None = None,
        flat: bool = False,
        flat_lists: bool = False,
        joiner: str = ".",
    ) -> Any:
        """Get a single subaward by key (`/api/subawards/{key}/`)."""
        params: dict[str, Any] = {}
        if shape is None:
            shape = ShapeConfig.SUBAWARDS_MINIMAL
        if shape:
            params["shape"] = shape
            if flat:
                params["flat"] = "true"
                if joiner:
                    params["joiner"] = joiner
            if flat_lists:
                params["flat_lists"] = "true"
        data = self._get(f"/api/subawards/{key}/", params)
        return self._parse_response_with_shape(
            data, shape, Subaward, flat, flat_lists, joiner=joiner
        )

    # ============================================================================
    # GSA eLibrary Contracts
    # ============================================================================

    def list_gsa_elibrary_contracts(
        self,
        page: int = 1,
        limit: int = 25,
        shape: str | None = None,
        flat: bool = False,
        flat_lists: bool = False,
        joiner: str = ".",
        contract_number: str | None = None,
        key: str | None = None,
        ordering: str | None = None,
        piid: str | None = None,
        schedule: str | None = None,
        search: str | None = None,
        sin: str | None = None,
        uei: str | None = None,
    ) -> PaginatedResponse:
        """List GSA eLibrary contracts (`/api/gsa_elibrary_contracts/`)."""
        params: dict[str, Any] = {"page": page, "limit": min(limit, 100)}
        if shape is None:
            shape = ShapeConfig.GSA_ELIBRARY_CONTRACTS_MINIMAL
        if shape:
            params["shape"] = shape
            if flat:
                params["flat"] = "true"
                if joiner:
                    params["joiner"] = joiner
            if flat_lists:
                params["flat_lists"] = "true"
        for k, val in (
            ("contract_number", contract_number),
            ("key", key),
            ("ordering", ordering),
            ("piid", piid),
            ("schedule", schedule),
            ("search", search),
            ("sin", sin),
            ("uei", uei),
        ):
            if val is not None:
                params[k] = val
        data = self._get("/api/gsa_elibrary_contracts/", params)
        results = [
            self._parse_response_with_shape(
                obj, shape, GsaElibraryContract, flat, flat_lists, joiner=joiner
            )
            for obj in data.get("results", [])
        ]
        return PaginatedResponse(
            count=data.get("count", 0),
            next=data.get("next"),
            previous=data.get("previous"),
            results=results,
        )

    def get_gsa_elibrary_contract(
        self,
        uuid: str,
        shape: str | None = None,
        flat: bool = False,
        flat_lists: bool = False,
        joiner: str = ".",
    ) -> Any:
        """Get a single GSA eLibrary contract by UUID (`/api/gsa_elibrary_contracts/{uuid}/`)."""
        params: dict[str, Any] = {}
        if shape is None:
            shape = ShapeConfig.GSA_ELIBRARY_CONTRACTS_MINIMAL
        if shape:
            params["shape"] = shape
            if flat:
                params["flat"] = "true"
                if joiner:
                    params["joiner"] = joiner
            if flat_lists:
                params["flat_lists"] = "true"
        data = self._get(f"/api/gsa_elibrary_contracts/{uuid}/", params)
        return self._parse_response_with_shape(
            data, shape, GsaElibraryContract, flat, flat_lists, joiner=joiner
        )

    # ============================================================================
    # IT Dashboard Investments
    # ============================================================================

    def list_itdashboard_investments(
        self,
        page: int = 1,
        limit: int = 25,
        shape: str | None = None,
        flat: bool = False,
        flat_lists: bool = False,
        joiner: str = ".",
        search: str | None = None,
        agency_code: int | None = None,
        agency_name: str | None = None,
        type_of_investment: str | None = None,
        updated_time_after: str | date | datetime | None = None,
        updated_time_before: str | date | datetime | None = None,
        cio_rating: int | None = None,
        cio_rating_max: int | None = None,
        performance_risk: bool | None = None,
    ) -> PaginatedResponse:
        """List federal IT investments from the IT Dashboard (`/api/itdashboard/`).

        Filters are tier-gated by the API:

        - **Free**: ``search`` (full-text across UII, title, description, agency, bureau)
        - **Pro**: ``agency_code``, ``type_of_investment``,
          ``updated_time_after`` / ``updated_time_before``
        - **Business+**: ``agency_name`` (text), ``cio_rating``,
          ``cio_rating_max``, ``performance_risk``

        Hitting a gated filter on a lower tier returns a 403 with upgrade info.

        CIO ratings: 1=High Risk, 2=Moderately High, 3=Medium, 4=Moderately Low, 5=Low.
        ``performance_risk=True`` returns investments with at least one NOT MET metric.
        """
        params: dict[str, Any] = {"page": page, "limit": min(limit, 100)}
        if shape is None:
            shape = ShapeConfig.ITDASHBOARD_INVESTMENTS_MINIMAL
        if shape:
            params["shape"] = shape
            if flat:
                params["flat"] = "true"
                if joiner:
                    params["joiner"] = joiner
            if flat_lists:
                params["flat_lists"] = "true"
        for k, val in (
            ("search", search),
            ("agency_code", agency_code),
            ("agency_name", agency_name),
            ("type_of_investment", type_of_investment),
            ("updated_time_after", updated_time_after),
            ("updated_time_before", updated_time_before),
            ("cio_rating", cio_rating),
            ("cio_rating_max", cio_rating_max),
            ("performance_risk", performance_risk),
        ):
            if val is None:
                continue
            if isinstance(val, bool):
                params[k] = "true" if val else "false"
            elif isinstance(val, (date, datetime)):
                params[k] = val.isoformat()
            else:
                params[k] = val
        data = self._get("/api/itdashboard/", params)
        results = [
            self._parse_response_with_shape(
                obj, shape, ITDashboardInvestment, flat, flat_lists, joiner=joiner
            )
            for obj in data.get("results", [])
        ]
        return PaginatedResponse(
            count=data.get("count", 0),
            next=data.get("next"),
            previous=data.get("previous"),
            results=results,
        )

    def get_itdashboard_investment(
        self,
        uii: str,
        shape: str | None = None,
        flat: bool = False,
        flat_lists: bool = False,
        joiner: str = ".",
    ) -> Any:
        """Get a single IT Dashboard investment by UII (`/api/itdashboard/{uii}/`)."""
        params: dict[str, Any] = {}
        if shape is None:
            shape = ShapeConfig.ITDASHBOARD_INVESTMENTS_COMPREHENSIVE
        if shape:
            params["shape"] = shape
            if flat:
                params["flat"] = "true"
                if joiner:
                    params["joiner"] = joiner
            if flat_lists:
                params["flat_lists"] = "true"
        data = self._get(f"/api/itdashboard/{uii}/", params)
        return self._parse_response_with_shape(
            data, shape, ITDashboardInvestment, flat, flat_lists, joiner=joiner
        )

    # ============================================================================
    # Vehicles (Awards)
    # ============================================================================

    @staticmethod
    def _warn_deprecated_vehicle_shape(shape: str | None) -> None:
        # Upstream sends `Deprecation: true` for these fields/expansions; warn
        # callers who request them explicitly so they have time to migrate
        # before tango publishes a Sunset timeline.
        from tango.shapes.explicit_schemas import DEPRECATED_VEHICLE_SHAPE_FIELDS

        if not shape:
            return
        # Match top-level field tokens, ignoring nesting inside parentheses.
        depth = 0
        token = ""
        tokens: list[str] = []
        for ch in shape:
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth = max(0, depth - 1)
            elif ch == "," and depth == 0:
                tokens.append(token.strip())
                token = ""
                continue
            token += ch
        tokens.append(token.strip())
        used = {t.split("(", 1)[0] for t in tokens} & DEPRECATED_VEHICLE_SHAPE_FIELDS
        if used:
            warnings.warn(
                f"Vehicle shape field(s) {sorted(used)!r} are deprecated upstream "
                "and may be removed in a future tango API version. The API currently "
                "returns a `Deprecation: true` header for these.",
                DeprecationWarning,
                stacklevel=3,
            )

    def list_vehicles(
        self,
        page: int = 1,
        limit: int = 25,
        shape: str | None = None,
        flat: bool = False,
        flat_lists: bool = False,
        joiner: str = ".",
        search: str | None = None,
        vehicle_type: str | None = None,
        type_of_idc: str | None = None,
        contract_type: str | None = None,
        set_aside: str | None = None,
        who_can_use: str | None = None,
        naics_code: int | None = None,
        psc_code: str | None = None,
        program_acronym: str | None = None,
        agency: str | None = None,
        organization_id: str | None = None,
        total_obligated_min: float | int | Decimal | None = None,
        total_obligated_max: float | int | Decimal | None = None,
        idv_count_min: int | None = None,
        idv_count_max: int | None = None,
        order_count_min: int | None = None,
        order_count_max: int | None = None,
        fiscal_year: int | None = None,
        award_date_after: str | date | datetime | None = None,
        award_date_before: str | date | datetime | None = None,
        last_date_to_order_after: str | date | datetime | None = None,
        last_date_to_order_before: str | date | datetime | None = None,
        ordering: str | None = None,
    ) -> PaginatedResponse:
        """List Vehicles (solicitation-centric groupings of IDVs).

        Multi-value filters (``vehicle_type``, ``type_of_idc``, ``contract_type``,
        ``set_aside``) accept pipe-separated values for OR semantics, e.g.
        ``vehicle_type="A|B|C"``.

        ``ordering`` accepts: ``vehicle_obligations``, ``latest_award_date``,
        ``total_obligated``, ``award_date``, ``last_date_to_order``,
        ``fiscal_year``, ``idv_count``, ``order_count``. Prefix with ``-`` for
        descending.
        """
        params: dict[str, Any] = {"page": page, "limit": min(limit, 100)}

        if shape is None:
            shape = ShapeConfig.VEHICLES_MINIMAL
        else:
            self._warn_deprecated_vehicle_shape(shape)
        if shape:
            params["shape"] = shape
            if flat:
                params["flat"] = "true"
                if joiner:
                    params["joiner"] = joiner
            if flat_lists:
                params["flat_lists"] = "true"

        for k, val in (
            ("search", search),
            ("vehicle_type", vehicle_type),
            ("type_of_idc", type_of_idc),
            ("contract_type", contract_type),
            ("set_aside", set_aside),
            ("who_can_use", who_can_use),
            ("naics_code", naics_code),
            ("psc_code", psc_code),
            ("program_acronym", program_acronym),
            ("agency", agency),
            ("organization_id", organization_id),
            ("total_obligated_min", total_obligated_min),
            ("total_obligated_max", total_obligated_max),
            ("idv_count_min", idv_count_min),
            ("idv_count_max", idv_count_max),
            ("order_count_min", order_count_min),
            ("order_count_max", order_count_max),
            ("fiscal_year", fiscal_year),
            ("award_date_after", award_date_after),
            ("award_date_before", award_date_before),
            ("last_date_to_order_after", last_date_to_order_after),
            ("last_date_to_order_before", last_date_to_order_before),
            ("ordering", ordering),
        ):
            if val is None:
                continue
            if isinstance(val, (date, datetime)):
                params[k] = val.isoformat()
            else:
                params[k] = val

        data = self._get("/api/vehicles/", params)

        results = [
            self._parse_response_with_shape(
                vehicle, shape, Vehicle, flat, flat_lists, joiner=joiner
            )
            for vehicle in data["results"]
        ]

        return PaginatedResponse(
            count=data["count"],
            next=data.get("next"),
            previous=data.get("previous"),
            results=results,
        )

    def get_vehicle(
        self,
        uuid: str,
        shape: str | None = None,
        flat: bool = False,
        flat_lists: bool = False,
        joiner: str = ".",
        search: str | None = None,
    ) -> Any:
        """Get a Vehicle by UUID."""
        params: dict[str, Any] = {}

        if shape is None:
            shape = ShapeConfig.VEHICLES_COMPREHENSIVE
        else:
            self._warn_deprecated_vehicle_shape(shape)
        if shape:
            params["shape"] = shape
            if flat:
                params["flat"] = "true"
                if joiner:
                    params["joiner"] = joiner
            if flat_lists:
                params["flat_lists"] = "true"

        # On vehicle detail, `search` filters expanded awardees when shaping includes `awardees(...)`.
        if search:
            params["search"] = search

        data = self._get(f"/api/vehicles/{uuid}/", params)
        return self._parse_response_with_shape(
            data, shape, Vehicle, flat, flat_lists, joiner=joiner
        )

    def list_vehicle_awardees(
        self,
        uuid: str,
        page: int = 1,
        limit: int = 25,
        shape: str | None = None,
        flat: bool = False,
        flat_lists: bool = False,
        joiner: str = ".",
        search: str | None = None,
    ) -> PaginatedResponse:
        """List the IDV awardees for a Vehicle (`/api/vehicles/{uuid}/awardees/`).

        ``search`` runs entity-aware full-text search across IDV fields
        (PIID, key, solicitation_identifier, NAICS, PSC, idv_type,
        fiscal_year) and recipient entity details (name, address).
        """
        params: dict[str, Any] = {"page": page, "limit": min(limit, 100)}

        if shape is None:
            shape = ShapeConfig.VEHICLE_AWARDEES_MINIMAL
        if shape:
            params["shape"] = shape
            if flat:
                params["flat"] = "true"
                if joiner:
                    params["joiner"] = joiner
            if flat_lists:
                params["flat_lists"] = "true"

        if search:
            params["search"] = search

        data = self._get(f"/api/vehicles/{uuid}/awardees/", params)

        results = [
            self._parse_response_with_shape(awardee, shape, IDV, flat, flat_lists, joiner=joiner)
            for awardee in data["results"]
        ]

        return PaginatedResponse(
            count=data["count"],
            next=data.get("next"),
            previous=data.get("previous"),
            results=results,
        )

    def list_vehicle_orders(
        self,
        uuid: str,
        page: int = 1,
        limit: int = 25,
        shape: str | None = None,
        flat: bool = False,
        flat_lists: bool = False,
        joiner: str = ".",
        ordering: str | None = None,
    ) -> PaginatedResponse:
        """List task orders under a Vehicle's IDVs (``/api/vehicles/{uuid}/orders/``).

        Args:
            ordering: Server-side sort. Allowed: ``award_date`` (default),
                ``obligated``, ``total_contract_value``. Prefix with ``-`` for
                descending.
        """
        params: dict[str, Any] = {"page": page, "limit": min(limit, 100)}

        if shape is None:
            shape = ShapeConfig.VEHICLE_ORDERS_MINIMAL
        if shape:
            params["shape"] = shape
            if flat:
                params["flat"] = "true"
                if joiner:
                    params["joiner"] = joiner
            if flat_lists:
                params["flat_lists"] = "true"

        if ordering:
            params["ordering"] = ordering

        data = self._get(f"/api/vehicles/{uuid}/orders/", params)

        results = [
            self._parse_response_with_shape(order, shape, Contract, flat, flat_lists, joiner=joiner)
            for order in data["results"]
        ]

        return PaginatedResponse(
            count=data["count"],
            next=data.get("next"),
            previous=data.get("previous"),
            results=results,
        )

    # Business Types endpoints
    def list_business_types(self, page: int = 1, limit: int = 25) -> PaginatedResponse:
        """List business types"""
        params = {"page": page, "limit": min(limit, 100)}
        data = self._get("/api/business_types/", params)
        return PaginatedResponse(
            count=data["count"],
            next=data.get("next"),
            previous=data.get("previous"),
            results=[BusinessType(**btype) for btype in data["results"]],
        )

    def list_naics(
        self,
        page: int = 1,
        limit: int = 25,
        employee_limit: int | None = None,
        employee_limit_gte: int | None = None,
        employee_limit_lte: int | None = None,
        revenue_limit: int | None = None,
        revenue_limit_gte: int | None = None,
        revenue_limit_lte: int | None = None,
        search: str | None = None,
    ) -> PaginatedResponse:
        """List NAICS codes (`/api/naics/`)."""
        params: dict[str, Any] = {"page": page, "limit": min(limit, 100)}
        if employee_limit is not None:
            params["employee_limit"] = employee_limit
        if employee_limit_gte is not None:
            params["employee_limit_gte"] = employee_limit_gte
        if employee_limit_lte is not None:
            params["employee_limit_lte"] = employee_limit_lte
        if revenue_limit is not None:
            params["revenue_limit"] = revenue_limit
        if revenue_limit_gte is not None:
            params["revenue_limit_gte"] = revenue_limit_gte
        if revenue_limit_lte is not None:
            params["revenue_limit_lte"] = revenue_limit_lte
        if search is not None:
            params["search"] = search
        data = self._get("/api/naics/", params)
        return PaginatedResponse(
            count=data.get("count", 0),
            next=data.get("next"),
            previous=data.get("previous"),
            results=data.get("results", []),
        )

    # Entity endpoints
    def list_entities(
        self,
        page: int = 1,
        limit: int = 25,
        shape: str | None = None,
        flat: bool = False,
        flat_lists: bool = False,
        search: str | None = None,
        cage_code: str | None = None,
        naics: str | None = None,
        name: str | None = None,
        psc: str | None = None,
        purpose_of_registration_code: str | None = None,
        socioeconomic: str | None = None,
        state: str | None = None,
        total_awards_obligated_gte: str | None = None,
        total_awards_obligated_lte: str | None = None,
        uei: str | None = None,
        zip_code: str | None = None,
    ) -> PaginatedResponse:
        """
        List entities (vendors/recipients)

        Args:
            page: Page number
            limit: Results per page (max 100)
            shape: Response shape string (defaults to minimal shape)
            flat: If True, flatten nested objects in shaped response
            flat_lists: If True, flatten arrays using indexed keys
            search: Search query
            cage_code: CAGE code filter
            naics: NAICS code filter
            name: Entity name filter
            psc: PSC code filter
            purpose_of_registration_code: Purpose of registration code
            socioeconomic: Socioeconomic status filter
            state: State filter
            total_awards_obligated_gte: Total awards obligated >=
            total_awards_obligated_lte: Total awards obligated <=
            uei: Unique Entity Identifier
            zip_code: ZIP code filter
        """
        params: dict[str, Any] = {"page": page, "limit": min(limit, 100)}

        if shape is None:
            shape = ShapeConfig.ENTITIES_MINIMAL
        if shape:
            params["shape"] = shape
            if flat:
                params["flat"] = "true"
            if flat_lists:
                params["flat_lists"] = "true"

        for key, val in (
            ("search", search),
            ("cage_code", cage_code),
            ("naics", naics),
            ("name", name),
            ("psc", psc),
            ("purpose_of_registration_code", purpose_of_registration_code),
            ("socioeconomic", socioeconomic),
            ("state", state),
            ("total_awards_obligated_gte", total_awards_obligated_gte),
            ("total_awards_obligated_lte", total_awards_obligated_lte),
            ("uei", uei),
            ("zip_code", zip_code),
        ):
            if val is not None:
                params[key] = val

        data = self._get("/api/entities/", params)

        # Always use dynamic parsing
        results = [
            self._parse_response_with_shape(entity, shape, Entity, flat, flat_lists)
            for entity in data["results"]
        ]

        return PaginatedResponse(
            count=data["count"],
            next=data.get("next"),
            previous=data.get("previous"),
            results=results,
        )

    def get_entity(
        self, key: str, shape: str | None = None, flat: bool = False, flat_lists: bool = False
    ) -> Any:
        """
        Get entity by key (UEI or CAGE code)

        Args:
            key: Entity identifier (UEI or CAGE code)
            shape: Response shape string (defaults to comprehensive shape)
            flat: If True, flatten nested objects in shaped response
            flat_lists: If True, flatten arrays using indexed keys
        """
        params = {}
        if shape is None:
            shape = ShapeConfig.ENTITIES_COMPREHENSIVE
        if shape:
            params["shape"] = shape
            if flat:
                params["flat"] = "true"
            if flat_lists:
                params["flat_lists"] = "true"

        data = self._get(f"/api/entities/{key}/", params)
        return self._parse_response_with_shape(data, shape, Entity, flat, flat_lists)

    def get_entity_budget_flows(self, uei: str) -> dict[str, Any]:
        """Get budget flows for an entity (`/api/entities/{uei}/budget-flows/`)."""
        if not uei:
            raise TangoValidationError("UEI is required")
        return self._get(f"/api/entities/{uei}/budget-flows/")

    # Forecast endpoints
    def list_forecasts(
        self,
        page: int = 1,
        limit: int = 25,
        shape: str | None = None,
        flat: bool = False,
        flat_lists: bool = False,
        agency: str | None = None,
        award_date_after: str | None = None,
        award_date_before: str | None = None,
        fiscal_year: int | None = None,
        fiscal_year_gte: int | None = None,
        fiscal_year_lte: int | None = None,
        modified_after: str | None = None,
        modified_before: str | None = None,
        naics_code: str | None = None,
        naics_starts_with: str | None = None,
        ordering: str | None = None,
        search: str | None = None,
        source_system: str | None = None,
        status: str | None = None,
    ) -> PaginatedResponse:
        """
        List contract forecasts

        Args:
            page: Page number
            limit: Results per page (max 100)
            shape: Response shape string (defaults to minimal shape)
            flat: If True, flatten nested objects in shaped response
            flat_lists: If True, flatten arrays using indexed keys
            agency: Agency filter
            award_date_after: Award date after (YYYY-MM-DD)
            award_date_before: Award date before (YYYY-MM-DD)
            fiscal_year: Fiscal year (exact match)
            fiscal_year_gte: Fiscal year >=
            fiscal_year_lte: Fiscal year <=
            modified_after: Modified after date
            modified_before: Modified before date
            naics_code: NAICS code filter
            naics_starts_with: NAICS code prefix filter
            ordering: Sort field (prefix with '-' for descending)
            search: Search query
            source_system: Source system filter
            status: Status filter
        """
        params: dict[str, Any] = {"page": page, "limit": min(limit, 100)}

        if shape is None:
            shape = ShapeConfig.FORECASTS_MINIMAL
        if shape:
            params["shape"] = shape
            if flat:
                params["flat"] = "true"
            if flat_lists:
                params["flat_lists"] = "true"

        for key, val in (
            ("agency", agency),
            ("award_date_after", award_date_after),
            ("award_date_before", award_date_before),
            ("fiscal_year", fiscal_year),
            ("fiscal_year_gte", fiscal_year_gte),
            ("fiscal_year_lte", fiscal_year_lte),
            ("modified_after", modified_after),
            ("modified_before", modified_before),
            ("naics_code", naics_code),
            ("naics_starts_with", naics_starts_with),
            ("ordering", ordering),
            ("search", search),
            ("source_system", source_system),
            ("status", status),
        ):
            if val is not None:
                params[key] = val

        data = self._get("/api/forecasts/", params)

        # Always use dynamic parsing
        results = [
            self._parse_response_with_shape(forecast, shape, Forecast, flat, flat_lists)
            for forecast in data["results"]
        ]

        return PaginatedResponse(
            count=data["count"],
            next=data.get("next"),
            previous=data.get("previous"),
            results=results,
        )

    def get_forecast(
        self,
        id: str,
        shape: str | None = None,
        flat: bool = False,
        flat_lists: bool = False,
        joiner: str = ".",
    ) -> Any:
        """Get a single forecast by id (`/api/forecasts/{id}/`)."""
        params: dict[str, Any] = {}
        if shape is None:
            shape = ShapeConfig.FORECASTS_MINIMAL
        if shape:
            params["shape"] = shape
            if flat:
                params["flat"] = "true"
                if joiner:
                    params["joiner"] = joiner
            if flat_lists:
                params["flat_lists"] = "true"
        data = self._get(f"/api/forecasts/{id}/", params)
        return self._parse_response_with_shape(
            data, shape, Forecast, flat, flat_lists, joiner=joiner
        )

    # Opportunity endpoints
    def list_opportunities(
        self,
        page: int = 1,
        limit: int = 25,
        shape: str | None = None,
        flat: bool = False,
        flat_lists: bool = False,
        active: bool | None = None,
        agency: str | None = None,
        first_notice_date_after: str | None = None,
        first_notice_date_before: str | None = None,
        last_notice_date_after: str | None = None,
        last_notice_date_before: str | None = None,
        naics: str | None = None,
        notice_type: str | None = None,
        ordering: str | None = None,
        place_of_performance: str | None = None,
        psc: str | None = None,
        response_deadline_after: str | None = None,
        response_deadline_before: str | None = None,
        search: str | None = None,
        set_aside: str | None = None,
        solicitation_number: str | None = None,
    ) -> PaginatedResponse:
        """
        List contract opportunities/solicitations

        Args:
            page: Page number
            limit: Results per page (max 100)
            shape: Response shape string (defaults to minimal shape)
            flat: If True, flatten nested objects in shaped response
            flat_lists: If True, flatten arrays using indexed keys
            active: Filter by active status
            agency: Agency filter
            first_notice_date_after: First notice date after
            first_notice_date_before: First notice date before
            last_notice_date_after: Last notice date after
            last_notice_date_before: Last notice date before
            naics: NAICS code filter
            notice_type: Notice type filter
            ordering: Sort field (prefix with '-' for descending)
            place_of_performance: Place of performance filter
            psc: PSC code filter
            response_deadline_after: Response deadline after
            response_deadline_before: Response deadline before
            search: Search query
            set_aside: Set-aside type filter
            solicitation_number: Solicitation number filter
        """
        params: dict[str, Any] = {"page": page, "limit": min(limit, 100)}

        if shape is None:
            shape = ShapeConfig.OPPORTUNITIES_MINIMAL
        if shape:
            params["shape"] = shape
            if flat:
                params["flat"] = "true"
            if flat_lists:
                params["flat_lists"] = "true"

        for key, val in (
            ("active", active),
            ("agency", agency),
            ("first_notice_date_after", first_notice_date_after),
            ("first_notice_date_before", first_notice_date_before),
            ("last_notice_date_after", last_notice_date_after),
            ("last_notice_date_before", last_notice_date_before),
            ("naics", naics),
            ("notice_type", notice_type),
            ("ordering", ordering),
            ("place_of_performance", place_of_performance),
            ("psc", psc),
            ("response_deadline_after", response_deadline_after),
            ("response_deadline_before", response_deadline_before),
            ("search", search),
            ("set_aside", set_aside),
            ("solicitation_number", solicitation_number),
        ):
            if val is not None:
                params[key] = val

        data = self._get("/api/opportunities/", params)

        # Always use dynamic parsing
        results = [
            self._parse_response_with_shape(opp, shape, Opportunity, flat, flat_lists)
            for opp in data["results"]
        ]

        return PaginatedResponse(
            count=data["count"],
            next=data.get("next"),
            previous=data.get("previous"),
            results=results,
        )

    def get_opportunity(
        self,
        opportunity_id: str,
        shape: str | None = None,
        flat: bool = False,
        flat_lists: bool = False,
        joiner: str = ".",
    ) -> Any:
        """Get a single opportunity by id (`/api/opportunities/{opportunity_id}/`)."""
        params: dict[str, Any] = {}
        if shape is None:
            shape = ShapeConfig.OPPORTUNITIES_MINIMAL
        if shape:
            params["shape"] = shape
            if flat:
                params["flat"] = "true"
                if joiner:
                    params["joiner"] = joiner
            if flat_lists:
                params["flat_lists"] = "true"
        data = self._get(f"/api/opportunities/{opportunity_id}/", params)
        return self._parse_response_with_shape(
            data, shape, Opportunity, flat, flat_lists, joiner=joiner
        )

    # Notice endpoints
    def list_notices(
        self,
        page: int = 1,
        limit: int = 25,
        shape: str | None = None,
        flat: bool = False,
        flat_lists: bool = False,
        active: bool | None = None,
        agency: str | None = None,
        naics: str | None = None,
        notice_type: str | None = None,
        posted_date_after: str | None = None,
        posted_date_before: str | None = None,
        psc: str | None = None,
        response_deadline_after: str | None = None,
        response_deadline_before: str | None = None,
        search: str | None = None,
        set_aside: str | None = None,
        solicitation_number: str | None = None,
    ) -> PaginatedResponse:
        """
        List contract notices

        Note: the notices viewset rejects every ``?ordering=`` value at
        runtime, so this method does not expose an ``ordering`` kwarg.

        Args:
            page: Page number
            limit: Results per page (max 100)
            shape: Response shape string (defaults to minimal shape)
            flat: If True, flatten nested objects in shaped response
            flat_lists: If True, flatten arrays using indexed keys
            active: Filter by active status
            agency: Agency filter
            naics: NAICS code filter
            notice_type: Notice type filter
            posted_date_after: Posted date after
            posted_date_before: Posted date before
            psc: PSC code filter
            response_deadline_after: Response deadline after
            response_deadline_before: Response deadline before
            search: Search query
            set_aside: Set-aside type filter
            solicitation_number: Solicitation number filter
        """
        params: dict[str, Any] = {"page": page, "limit": min(limit, 100)}

        if shape is None:
            shape = ShapeConfig.NOTICES_MINIMAL
        if shape:
            params["shape"] = shape
            if flat:
                params["flat"] = "true"
            if flat_lists:
                params["flat_lists"] = "true"

        for key, val in (
            ("active", active),
            ("agency", agency),
            ("naics", naics),
            ("notice_type", notice_type),
            ("posted_date_after", posted_date_after),
            ("posted_date_before", posted_date_before),
            ("psc", psc),
            ("response_deadline_after", response_deadline_after),
            ("response_deadline_before", response_deadline_before),
            ("search", search),
            ("set_aside", set_aside),
            ("solicitation_number", solicitation_number),
        ):
            if val is not None:
                params[key] = val

        data = self._get("/api/notices/", params)

        # Always use dynamic parsing
        results = [
            self._parse_response_with_shape(notice, shape, Notice, flat, flat_lists)
            for notice in data["results"]
        ]

        return PaginatedResponse(
            count=data["count"],
            next=data.get("next"),
            previous=data.get("previous"),
            results=results,
        )

    def get_notice(
        self,
        notice_id: str,
        shape: str | None = None,
        flat: bool = False,
        flat_lists: bool = False,
        joiner: str = ".",
    ) -> Any:
        """Get a single notice by id (`/api/notices/{notice_id}/`)."""
        params: dict[str, Any] = {}
        if shape is None:
            shape = ShapeConfig.NOTICES_MINIMAL
        if shape:
            params["shape"] = shape
            if flat:
                params["flat"] = "true"
                if joiner:
                    params["joiner"] = joiner
            if flat_lists:
                params["flat_lists"] = "true"
        data = self._get(f"/api/notices/{notice_id}/", params)
        return self._parse_response_with_shape(data, shape, Notice, flat, flat_lists, joiner=joiner)

    # Protest endpoints
    # See https://tango.makegov.com/docs/api-reference/protests.md
    # Note: Protests API does not support ordering (returns 400 if provided).
    # Use shape=...,dockets(...) to request nested dockets.
    def list_protests(
        self,
        page: int = 1,
        limit: int = 25,
        shape: str | None = None,
        flat: bool = False,
        flat_lists: bool = False,
        source_system: str | None = None,
        outcome: str | None = None,
        case_type: str | None = None,
        agency: str | None = None,
        case_number: str | None = None,
        solicitation_number: str | None = None,
        protester: str | None = None,
        filed_date_after: str | None = None,
        filed_date_before: str | None = None,
        decision_date_after: str | None = None,
        decision_date_before: str | None = None,
        search: str | None = None,
    ) -> PaginatedResponse:
        """
        List bid protests.

        Returns case-level protest records. Use shape=...,dockets(...) to include
        nested dockets. API reference: https://tango.makegov.com/docs/api-reference/protests.md

        Note: the protests viewset does not advertise ``ordering`` and
        rejects every value at runtime, so this method does not expose an
        ``ordering`` kwarg.

        Args:
            page: Page number
            limit: Results per page (max 100)
            shape: Response shape string (defaults to minimal shape)
            flat: If True, flatten nested objects in shaped response
            flat_lists: If True, flatten arrays using indexed keys
            source_system: Filter by source system (e.g. gao)
            outcome: Filter by outcome (e.g. Denied, Dismissed, Withdrawn, Sustained)
            case_type: Filter by case type
            agency: Filter by protested agency text
            case_number: Filter by case number (e.g. b-423274)
            solicitation_number: Filter by exact solicitation number
            protester: Filter by protester name text
            filed_date_after: Filed date on or after
            filed_date_before: Filed date on or before
            decision_date_after: Decision date on or after
            decision_date_before: Decision date on or before
            search: Full-text search over protest searchable fields
        """
        params: dict[str, Any] = {"page": page, "limit": min(limit, 100)}

        if shape is None:
            shape = ShapeConfig.PROTESTS_MINIMAL
        if shape:
            params["shape"] = shape
            if flat:
                params["flat"] = "true"
            if flat_lists:
                params["flat_lists"] = "true"

        for key, val in (
            ("source_system", source_system),
            ("outcome", outcome),
            ("case_type", case_type),
            ("agency", agency),
            ("case_number", case_number),
            ("solicitation_number", solicitation_number),
            ("protester", protester),
            ("filed_date_after", filed_date_after),
            ("filed_date_before", filed_date_before),
            ("decision_date_after", decision_date_after),
            ("decision_date_before", decision_date_before),
            ("search", search),
        ):
            if val is not None:
                params[key] = val

        data = self._get("/api/protests/", params)

        results = [
            self._parse_response_with_shape(item, shape, Protest, flat, flat_lists)
            for item in data["results"]
        ]

        return PaginatedResponse(
            count=data["count"],
            next=data.get("next"),
            previous=data.get("previous"),
            results=results,
        )

    def get_protest(
        self,
        case_id: str,
        shape: str | None = None,
        flat: bool = False,
        flat_lists: bool = False,
    ) -> Any:
        """
        Get a single protest by case_id (RFC 4122 UUID).

        Use shape=...,dockets(...) to include nested dockets.
        API reference: https://tango.makegov.com/docs/api-reference/protests.md

        Args:
            case_id: Deterministic case UUID (from source_system + base_case_number)
            shape: Response shape string (defaults to minimal shape)
            flat: If True, flatten nested objects in shaped response
            flat_lists: If True, flatten arrays using indexed keys
        """
        params: dict[str, Any] = {}
        if shape is None:
            shape = ShapeConfig.PROTESTS_MINIMAL
        if shape:
            params["shape"] = shape
            if flat:
                params["flat"] = "true"
            if flat_lists:
                params["flat_lists"] = "true"

        data = self._get(f"/api/protests/{case_id}/", params)
        return self._parse_response_with_shape(data, shape, Protest, flat, flat_lists)

    # ============================================================================
    # Budget (federal account x fiscal year rollups)
    # ============================================================================

    def list_budget_accounts(
        self,
        page: int = 1,
        limit: int = 25,
        shape: str | None = None,
        flat: bool = False,
        flat_lists: bool = False,
        federal_account_symbol: str | None = None,
        fiscal_year: int | None = None,
        fiscal_year_gte: int | None = None,
        fiscal_year_lte: int | None = None,
        agency_code: str | None = None,
        bureau_name: str | None = None,
        account_title: str | None = None,
        bea_category: str | None = None,
        on_off_budget: str | None = None,
        subfunction_code: str | None = None,
        search: str | None = None,
        ordering: str | None = None,
    ) -> PaginatedResponse:
        """List budget accounts (`/api/budget/accounts/`).

        One row per ``(federal_account_symbol, fiscal_year)`` covering the full
        budget lifecycle, pre-computed ratios + trends, the
        contract/assistance/unlinked breakdown, and request-vs-actual spend.

        Args:
            page: Page number.
            limit: Results per page (max 100).
            shape: Response shape string (defaults to minimal shape).
            flat: If True, flatten nested objects using dot notation.
            flat_lists: If True, flatten arrays using indexed keys.
            federal_account_symbol: Exact federal account symbol.
            fiscal_year: Fiscal year (exact).
            fiscal_year_gte: Fiscal year >=.
            fiscal_year_lte: Fiscal year <=.
            agency_code: Agency code (exact).
            bureau_name: Bureau name (exact).
            account_title: Account title (icontains).
            bea_category: BEA category (exact).
            on_off_budget: On/off budget flag (exact).
            subfunction_code: Subfunction code (exact).
            search: Full-text search over account_title/agency_name/bureau_name.
            ordering: Sort field (prefix with '-' for descending).
        """
        params: dict[str, Any] = {"page": page, "limit": min(limit, 100)}
        if shape is None:
            shape = ShapeConfig.BUDGET_ACCOUNTS_MINIMAL
        if shape:
            params["shape"] = shape
            if flat:
                params["flat"] = "true"
            if flat_lists:
                params["flat_lists"] = "true"
        for key, val in (
            ("federal_account_symbol", federal_account_symbol),
            ("fiscal_year", fiscal_year),
            ("fiscal_year__gte", fiscal_year_gte),
            ("fiscal_year__lte", fiscal_year_lte),
            ("agency_code", agency_code),
            ("bureau_name", bureau_name),
            ("account_title__icontains", account_title),
            ("bea_category", bea_category),
            ("on_off_budget", on_off_budget),
            ("subfunction_code", subfunction_code),
            ("search", search),
            ("ordering", ordering),
        ):
            if val is not None:
                params[key] = val
        data = self._get("/api/budget/accounts/", params)
        results = [
            self._parse_response_with_shape(obj, shape, BudgetAccount, flat, flat_lists)
            for obj in data.get("results", [])
        ]
        return PaginatedResponse(
            count=data.get("count", 0),
            next=data.get("next"),
            previous=data.get("previous"),
            results=results,
        )

    def get_budget_account(
        self,
        id: str | int,
        shape: str | None = None,
        flat: bool = False,
        flat_lists: bool = False,
        joiner: str = ".",
    ) -> Any:
        """Get a single budget account by id (`/api/budget/accounts/{id}/`)."""
        params: dict[str, Any] = {}
        if shape is None:
            shape = ShapeConfig.BUDGET_ACCOUNTS_MINIMAL
        if shape:
            params["shape"] = shape
            if flat:
                params["flat"] = "true"
                if joiner:
                    params["joiner"] = joiner
            if flat_lists:
                params["flat_lists"] = "true"
        data = self._get(f"/api/budget/accounts/{id}/", params)
        return self._parse_response_with_shape(
            data, shape, BudgetAccount, flat, flat_lists, joiner=joiner
        )

    def get_budget_account_quarters(
        self,
        id: str | int,
        tas: str | None = None,
        limit: int = 25,
    ) -> PaginatedResponse:
        """Get quarterly TAS-grain flow for a budget account.

        (`/api/budget/accounts/{id}/quarters/`). FY21+ only.

        Args:
            id: Budget account id.
            tas: Narrow to a single Treasury Account Symbol.
            limit: Results per page (max 100).
        """
        params: dict[str, Any] = {"limit": min(limit, 100)}
        if tas:
            params["tas"] = tas
        data = self._get(f"/api/budget/accounts/{id}/quarters/", params)
        return PaginatedResponse(
            count=int(data.get("count") or len(data.get("results") or [])),
            next=data.get("next"),
            previous=data.get("previous"),
            results=data.get("results") or [],
        )

    def get_budget_account_recipients(
        self,
        id: str | int,
        funding_organization_id: str | None = None,
        limit: int = 25,
    ) -> PaginatedResponse:
        """Get funding-office x recipient contract-flow detail for a budget account.

        (`/api/budget/accounts/{id}/recipients/`).

        Args:
            id: Budget account id.
            funding_organization_id: Narrow to a single funding office
                (Organization UUID).
            limit: Results per page (max 100).
        """
        params: dict[str, Any] = {"limit": min(limit, 100)}
        if funding_organization_id:
            params["funding_organization_id"] = funding_organization_id
        data = self._get(f"/api/budget/accounts/{id}/recipients/", params)
        return PaginatedResponse(
            count=int(data.get("count") or len(data.get("results") or [])),
            next=data.get("next"),
            previous=data.get("previous"),
            results=data.get("results") or [],
        )

    # Grant endpoints
    def list_grants(
        self,
        page: int = 1,
        limit: int = 25,
        shape: str | None = None,
        flat: bool = False,
        flat_lists: bool = False,
        agency: str | None = None,
        applicant_types: str | None = None,
        cfda_number: str | None = None,
        funding_categories: str | None = None,
        funding_instruments: str | None = None,
        grant_id: str | None = None,
        opportunity_number: str | None = None,
        ordering: str | None = None,
        posted_date_after: str | None = None,
        posted_date_before: str | None = None,
        response_date_after: str | None = None,
        response_date_before: str | None = None,
        search: str | None = None,
        status: str | None = None,
    ) -> PaginatedResponse:
        """
        List grants

        Args:
            page: Page number
            limit: Results per page (max 100)
            shape: Response shape string (defaults to minimal shape)
            flat: If True, flatten nested objects in shaped response
            flat_lists: If True, flatten arrays using indexed keys
            agency: Agency filter
            applicant_types: Applicant types filter
            cfda_number: CFDA number filter
            funding_categories: Funding categories filter
            funding_instruments: Funding instruments filter
            grant_id: Filter by grant ID (matches the detail-endpoint
                identifier). Supports multi-value OR via '|' (e.g. "123|456").
            opportunity_number: Opportunity number filter
            ordering: Sort field (prefix with '-' for descending)
            posted_date_after: Posted date after
            posted_date_before: Posted date before
            response_date_after: Response date after
            response_date_before: Response date before
            search: Search query
            status: Status filter
        """
        params: dict[str, Any] = {"page": page, "limit": min(limit, 100)}

        if shape is None:
            shape = ShapeConfig.GRANTS_MINIMAL
        if shape:
            params["shape"] = shape
            if flat:
                params["flat"] = "true"
            if flat_lists:
                params["flat_lists"] = "true"

        for key, val in (
            ("agency", agency),
            ("applicant_types", applicant_types),
            ("cfda_number", cfda_number),
            ("funding_categories", funding_categories),
            ("funding_instruments", funding_instruments),
            ("grant_id", grant_id),
            ("opportunity_number", opportunity_number),
            ("ordering", ordering),
            ("posted_date_after", posted_date_after),
            ("posted_date_before", posted_date_before),
            ("response_date_after", response_date_after),
            ("response_date_before", response_date_before),
            ("search", search),
            ("status", status),
        ):
            if val is not None:
                params[key] = val

        data = self._get("/api/grants/", params)

        # Always use dynamic parsing
        results = [
            self._parse_response_with_shape(grant, shape, Grant, flat, flat_lists)
            for grant in data["results"]
        ]

        return PaginatedResponse(
            count=data["count"],
            next=data.get("next"),
            previous=data.get("previous"),
            results=results,
        )

    def get_grant(
        self,
        grant_id: str,
        shape: str | None = None,
        flat: bool = False,
        flat_lists: bool = False,
        joiner: str = ".",
    ) -> Any:
        """Get a single grant by its grant id (`/api/grants/{grant_id}/`)."""
        params: dict[str, Any] = {}
        if shape is None:
            shape = ShapeConfig.GRANTS_MINIMAL
        if shape:
            params["shape"] = shape
            if flat:
                params["flat"] = "true"
                if joiner:
                    params["joiner"] = joiner
            if flat_lists:
                params["flat_lists"] = "true"
        data = self._get(f"/api/grants/{grant_id}/", params)
        return self._parse_response_with_shape(data, shape, Grant, flat, flat_lists, joiner=joiner)

    # ============================================================================
    # Webhooks (v2)
    # ============================================================================

    def list_webhook_event_types(self) -> WebhookEventTypesResponse:
        """Discover supported webhook event types."""
        data = self._get("/api/webhooks/event-types/")

        event_types = [
            WebhookEventType(
                event_type=str(e.get("event_type", "")),
                description=str(e.get("description", "")),
                schema_version=int(e.get("schema_version", 1)),
            )
            for e in (data.get("event_types") or [])
            if isinstance(e, dict)
        ]

        return WebhookEventTypesResponse(event_types=event_types)

    def get_webhook_endpoint(self, endpoint_id: str) -> WebhookEndpoint:
        """Get a webhook endpoint by id (UUID)."""
        if not endpoint_id:
            raise TangoValidationError("Webhook endpoint_id is required")
        data = self._get(f"/api/webhooks/endpoints/{endpoint_id}/")
        return WebhookEndpoint(
            id=str(data.get("id", "")),
            name=str(data.get("name", "")),
            callback_url=str(data.get("callback_url", "")),
            secret=str(data.get("secret")) if data.get("secret") is not None else None,
            is_active=bool(data.get("is_active", False)),
            created_at=str(data.get("created_at", "")),
            updated_at=str(data.get("updated_at", "")),
        )

    def list_webhook_endpoints(
        self, page: int = 1, limit: int = 25
    ) -> PaginatedResponse[WebhookEndpoint]:
        """
        List webhook endpoints accessible to the authenticated user.

        Notes:
        - In typical production usage, MakeGov provisions the initial endpoint for you.
        - The API is opinionated: endpoints are "owned" by you (name == username/email).
        """
        params: dict[str, Any] = {"page": page, "limit": min(limit, 100)}
        data = self._get("/api/webhooks/endpoints/", params)

        results = [
            WebhookEndpoint(
                id=str(item.get("id", "")),
                name=str(item.get("name", "")),
                callback_url=str(item.get("callback_url", "")),
                secret=str(item.get("secret")) if item.get("secret") is not None else None,
                is_active=bool(item.get("is_active", False)),
                created_at=str(item.get("created_at", "")),
                updated_at=str(item.get("updated_at", "")),
            )
            for item in (data.get("results") or [])
            if isinstance(item, dict)
        ]

        return PaginatedResponse(
            count=int(data.get("count", len(results))),
            next=data.get("next"),
            previous=data.get("previous"),
            results=results,
        )

    def create_webhook_endpoint(
        self,
        callback_url: str,
        is_active: bool = True,
        *,
        name: str | None = None,
    ) -> WebhookEndpoint:
        """
        Create a webhook endpoint for the authenticated user.

        Args:
            callback_url: HTTPS URL to receive POSTed webhook events.
            is_active: Whether deliveries are enabled.
            name: Human-readable name for this endpoint. Required by the
                Tango API (the server enforces ``unique(user, name)``).
                Currently keyword-optional in the SDK for backward
                compatibility — passing it explicitly is strongly
                recommended; a future major version will make it required.
                When omitted, callers will see a server-side 400
                ``"name: This field is required"``.

        Note:
            The server generates ``secret``. A user may have multiple
            endpoints (unique on ``(user, name)``).
        """
        if not callback_url:
            raise TangoValidationError("Webhook callback_url is required")
        if name is None:
            # `name` was a deprecation warning in 0.7.0 (never publicly
            # released). 1.0.0 makes it a hard error since the server
            # enforces unique(user, name) and the warn-then-400 path
            # was a worse DX than just raising client-side.
            raise TangoValidationError(
                "create_webhook_endpoint(): `name=` is required. "
                "The Tango API enforces unique(user, name) on endpoints; "
                "omitting it would return a 400 server-side. "
                "Pass name='your-endpoint-name'."
            )

        body: dict[str, Any] = {"callback_url": callback_url, "is_active": is_active, "name": name}

        data = self._post("/api/webhooks/endpoints/", body)
        return WebhookEndpoint(
            id=str(data.get("id", "")),
            name=str(data.get("name", "")),
            callback_url=str(data.get("callback_url", "")),
            secret=str(data.get("secret")) if data.get("secret") is not None else None,
            is_active=bool(data.get("is_active", False)),
            created_at=str(data.get("created_at", "")),
            updated_at=str(data.get("updated_at", "")),
        )

    def update_webhook_endpoint(
        self,
        endpoint_id: str,
        *,
        name: str | None = None,
        callback_url: str | None = None,
        is_active: bool | None = None,
    ) -> WebhookEndpoint:
        """Patch a webhook endpoint."""
        if not endpoint_id:
            raise TangoValidationError("Webhook endpoint_id is required")

        body: dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        if callback_url is not None:
            body["callback_url"] = callback_url
        if is_active is not None:
            body["is_active"] = is_active

        data = self._patch(f"/api/webhooks/endpoints/{endpoint_id}/", body)
        return WebhookEndpoint(
            id=str(data.get("id", "")),
            name=str(data.get("name", "")),
            callback_url=str(data.get("callback_url", "")),
            secret=str(data.get("secret")) if data.get("secret") is not None else None,
            is_active=bool(data.get("is_active", False)),
            created_at=str(data.get("created_at", "")),
            updated_at=str(data.get("updated_at", "")),
        )

    def delete_webhook_endpoint(self, endpoint_id: str) -> None:
        """Delete a webhook endpoint."""
        if not endpoint_id:
            raise TangoValidationError("Webhook endpoint_id is required")
        self._delete(f"/api/webhooks/endpoints/{endpoint_id}/")

    def test_webhook_delivery(self, endpoint_id: str | None = None) -> WebhookTestDeliveryResult:
        """
        Send an immediate test webhook to your endpoint.

        If endpoint_id is not provided, the server will use your default
        endpoint. The kwarg is named ``endpoint_id`` for backwards-compat;
        the wire payload uses the canonical ``endpoint`` key (the server
        still accepts ``endpoint_id`` as a deprecated alias on this route).
        """
        body: dict[str, Any] = {}
        if endpoint_id:
            body["endpoint"] = endpoint_id
        data = self._post("/api/webhooks/endpoints/test-delivery/", body)
        return WebhookTestDeliveryResult(
            success=bool(data.get("success", False)),
            status_code=int(data["status_code"]) if data.get("status_code") is not None else None,
            response_time_ms=int(data["response_time_ms"])
            if data.get("response_time_ms") is not None
            else None,
            endpoint_url=str(data.get("endpoint_url"))
            if data.get("endpoint_url") is not None
            else None,
            message=str(data.get("message")) if data.get("message") is not None else None,
            error=str(data.get("error")) if data.get("error") is not None else None,
            response_body=str(data.get("response_body"))
            if data.get("response_body") is not None
            else None,
            test_payload=data.get("test_payload"),
        )

    def get_webhook_sample_payload(
        self, event_type: str | None = None
    ) -> WebhookSamplePayloadResponse:
        """
        Fetch Tango-shaped sample webhook deliveries.

        - If ``event_type`` is provided, returns a :class:`WebhookSamplePayloadSingleResponse`.
        - Otherwise returns a :class:`WebhookSamplePayloadAllResponse` with a ``samples``
          mapping keyed by event type.
        """
        params: dict[str, Any] = {}
        if event_type:
            params["event_type"] = event_type
        return self._get("/api/webhooks/endpoints/sample-payload/", params)  # type: ignore[return-value]

    # ============================================================================
    # Webhook Alerts (filter-based subscriptions)
    # ============================================================================

    @staticmethod
    def _parse_webhook_alert(data: dict[str, Any]) -> WebhookAlert:
        """Hydrate an Alert dict from /api/webhooks/alerts/ into a WebhookAlert."""
        return WebhookAlert(
            alert_id=str(data.get("alert_id") or data.get("id") or ""),
            name=str(data.get("name") or data.get("subscription_name") or ""),
            query_type=(str(data["query_type"]) if data.get("query_type") is not None else None),
            filters=data.get("filters") or data.get("filter_definition"),
            frequency=str(data.get("frequency", "realtime")),
            cron_expression=(
                str(data["cron_expression"]) if data.get("cron_expression") is not None else None
            ),
            status=str(data.get("status", "active")),
            created_at=str(data.get("created_at", "")),
            last_checked_at=(
                str(data["last_checked_at"]) if data.get("last_checked_at") is not None else None
            ),
            match_count=int(data.get("match_count", 0) or 0),
        )

    def list_webhook_alerts(
        self, page: int = 1, page_size: int | None = None
    ) -> PaginatedResponse[WebhookAlert]:
        """List filter-based webhook subscriptions (alerts).

        Backed by ``GET /api/webhooks/alerts/`` — the canonical (and only)
        write surface for webhook subscriptions. Uses the cleaner ``alert_id``
        / ``name`` / ``filters`` shape rather than the raw subscriptions
        model fields.
        """
        params: dict[str, Any] = {"page": page}
        if page_size is not None:
            params["page_size"] = page_size
        data = self._get("/api/webhooks/alerts/", params)
        results = [
            self._parse_webhook_alert(item)
            for item in (data.get("results") or [])
            if isinstance(item, dict)
        ]
        return PaginatedResponse(
            count=int(data.get("count", len(results))),
            next=data.get("next"),
            previous=data.get("previous"),
            results=results,
        )

    def get_webhook_alert(self, alert_id: str) -> WebhookAlert:
        """Get a single filter-based webhook subscription by alert_id (UUID)."""
        if not alert_id:
            raise TangoValidationError("Webhook alert_id is required")
        data = self._get(f"/api/webhooks/alerts/{alert_id}/")
        return self._parse_webhook_alert(data)

    def create_webhook_alert(
        self,
        name: str,
        query_type: str,
        filters: dict[str, Any],
        *,
        frequency: str = "realtime",
        cron_expression: str | None = None,
        endpoint: str | None = None,
    ) -> WebhookAlert:
        """Create a filter-based webhook subscription (alert).

        Args:
            name: Human-readable name for this alert.
            query_type: One of ``opportunity``, ``contract``, ``idv``, ``ota``,
                ``otidv``, ``entity``, ``grant``, ``forecast``.
            filters: Dict of query parameters that the alert matches against
                (e.g. ``{"naics": "541330", "set_aside": "SBA"}``).
            frequency: ``realtime`` | ``daily`` | ``weekly`` | ``custom``.
                ``custom`` requires ``cron_expression`` and Pro+ tier.
            cron_expression: 5-field cron expression, only valid when
                ``frequency="custom"``.
            endpoint: Optional UUID of the :class:`WebhookEndpoint` this
                alert delivers to. Required when the account has multiple
                endpoints (the server returns 400 otherwise); for
                single-endpoint accounts the server auto-resolves.

        Returns:
            The created (or, if a dedup-matched alert already exists, the
            existing) :class:`WebhookAlert`. Both 201-Created and 200-OK
            (dedup) responses are normalized to the same shape.
        """
        if not name:
            raise TangoValidationError("Webhook alert name is required")
        if not query_type:
            raise TangoValidationError("Webhook alert query_type is required")
        if not filters or not isinstance(filters, dict):
            raise TangoValidationError(
                "Webhook alert filters must be a non-empty dict of query params"
            )

        body: dict[str, Any] = {
            "name": name,
            "query_type": query_type,
            "filters": filters,
            "frequency": frequency,
        }
        if cron_expression is not None:
            body["cron_expression"] = cron_expression
        if endpoint is not None:
            body["endpoint"] = endpoint

        data = self._post("/api/webhooks/alerts/", body)
        return self._parse_webhook_alert(data)

    def update_webhook_alert(
        self,
        alert_id: str,
        *,
        name: str | None = None,
        frequency: str | None = None,
        cron_expression: str | None = None,
        is_active: bool | None = None,
    ) -> WebhookAlert:
        """Patch a webhook alert (filter subscription).

        Only ``name``, ``frequency``, ``cron_expression``, and ``is_active``
        are writable — ``query_type`` and ``filters`` are read-only after
        creation (the server treats them as part of the alert's identity
        via ``filter_hash``).
        """
        if not alert_id:
            raise TangoValidationError("Webhook alert_id is required")

        body: dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        if frequency is not None:
            body["frequency"] = frequency
        if cron_expression is not None:
            body["cron_expression"] = cron_expression
        if is_active is not None:
            body["is_active"] = is_active

        data = self._patch(f"/api/webhooks/alerts/{alert_id}/", body)
        return self._parse_webhook_alert(data)

    def delete_webhook_alert(self, alert_id: str) -> None:
        """Delete a webhook alert (filter subscription)."""
        if not alert_id:
            raise TangoValidationError("Webhook alert_id is required")
        self._delete(f"/api/webhooks/alerts/{alert_id}/")

    # ============================================================================
    # Resolve & Validate (POST endpoints)
    # ============================================================================

    def resolve(
        self,
        name: str,
        target_type: str,
        *,
        state: str | None = None,
        city: str | None = None,
        context: str | None = None,
    ) -> ResolveResult:
        """Resolve a free-text name to ranked entity or organization candidates.

        ``POST /api/resolve/``

        Args:
            name: Name to resolve.
            target_type: ``"entity"`` or ``"organization"``.
            state: Optional 2-letter US state code to bias matching.
            city: Optional city name to bias matching.
            context: Optional freeform additional context for better matching.

        Returns:
            :class:`ResolveResult` with ranked candidates. Free-tier callers
            get up to 3 candidates with ``identifier`` and ``display_name``;
            Pro+ callers get up to 5 with an additional ``match_tier`` field.
            Other server-returned fields are preserved on each candidate's
            ``extra`` dict.
        """
        if not name:
            raise TangoValidationError("resolve(): name is required")
        if target_type not in ("entity", "organization"):
            raise TangoValidationError("resolve(): target_type must be 'entity' or 'organization'")

        body: dict[str, Any] = {"name": name, "target_type": target_type}
        if state is not None:
            body["state"] = state
        if city is not None:
            body["city"] = city
        if context is not None:
            body["context"] = context

        data = self._post("/api/resolve/", body)
        candidates: list[ResolveCandidate] = []
        for raw in data.get("candidates") or []:
            if not isinstance(raw, dict):
                continue
            extras = {
                k: v
                for k, v in raw.items()
                if k not in {"identifier", "display_name", "match_tier"}
            }
            candidates.append(
                ResolveCandidate(
                    identifier=raw.get("identifier"),
                    display_name=raw.get("display_name"),
                    match_tier=raw.get("match_tier"),
                    extra=extras or None,
                )
            )
        return ResolveResult(
            candidates=candidates,
            count=int(data.get("count", len(candidates))),
        )

    def validate(self, identifier_type: str, value: str) -> ValidateResult:
        """Validate the format of a PIID, solicitation number, or UEI.

        ``POST /api/validate/``

        Args:
            identifier_type: One of ``"piid"``, ``"solicitation"``, ``"uei"``.
                (Maps to the API's ``type`` field — ``identifier_type`` here
                avoids shadowing the Python builtin.)
            value: The identifier value to validate.

        Returns:
            :class:`ValidateResult` with ``result`` in ``{"valid",
            "not_valid", "low_confidence"}``. ``low_confidence`` applies only
            to solicitation numbers that pass basic checks but don't match a
            named pattern.
        """
        if identifier_type not in ("piid", "solicitation", "uei"):
            raise TangoValidationError(
                "validate(): identifier_type must be 'piid', 'solicitation', or 'uei'"
            )
        if not value:
            raise TangoValidationError("validate(): value is required")

        data = self._post("/api/validate/", {"type": identifier_type, "value": value})
        return ValidateResult(
            result=str(data.get("result", "")),
            type=str(data.get("type", identifier_type)),
            value=str(data.get("value", value)),
            errors=list(data.get("errors") or []) or None,
        )

    # ============================================================================
    # Reference data
    # ============================================================================

    def list_departments(self, page: int = 1, limit: int = 25) -> PaginatedResponse[dict[str, Any]]:
        """List departments (`/api/departments/`)."""
        params: dict[str, Any] = {"page": page, "limit": min(limit, 100)}
        data = self._get("/api/departments/", params)
        return PaginatedResponse(
            count=int(data.get("count", 0)),
            next=data.get("next"),
            previous=data.get("previous"),
            results=list(data.get("results") or []),
        )

    def get_department(self, code: str) -> dict[str, Any]:
        """Get a department by code (`/api/departments/{code}/`)."""
        if not code:
            raise TangoValidationError("Department code is required")
        return self._get(f"/api/departments/{code}/")

    def list_psc(self, page: int = 1, limit: int = 25) -> PaginatedResponse[dict[str, Any]]:
        """List Product Service Codes (`/api/psc/`)."""
        params: dict[str, Any] = {"page": page, "limit": min(limit, 100)}
        data = self._get("/api/psc/", params)
        return PaginatedResponse(
            count=int(data.get("count", 0)),
            next=data.get("next"),
            previous=data.get("previous"),
            results=list(data.get("results") or []),
        )

    def get_psc(self, code: str) -> dict[str, Any]:
        """Get a Product Service Code by code (`/api/psc/{code}/`)."""
        if not code:
            raise TangoValidationError("PSC code is required")
        return self._get(f"/api/psc/{code}/")

    def get_psc_metrics(self, code: str, months: int, period_grouping: str) -> dict[str, Any]:
        """Get rolling PSC metrics (`/api/psc/{code}/metrics/{months}/{period_grouping}/`).

        Args:
            code: PSC code.
            months: Window size in months (e.g. 6, 12, 24, 36).
            period_grouping: ``"month"``, ``"quarter"``, or ``"year"`` (the
                values the API accepts on the path segment).
        """
        if not code:
            raise TangoValidationError("PSC code is required")
        return self._get(f"/api/psc/{code}/metrics/{months}/{period_grouping}/")

    def get_naics(self, code: str) -> dict[str, Any]:
        """Get a NAICS code by code (`/api/naics/{code}/`)."""
        if not code:
            raise TangoValidationError("NAICS code is required")
        return self._get(f"/api/naics/{code}/")

    def get_naics_metrics(self, code: str, months: int, period_grouping: str) -> dict[str, Any]:
        """Get rolling NAICS metrics (`/api/naics/{code}/metrics/{months}/{period_grouping}/`)."""
        if not code:
            raise TangoValidationError("NAICS code is required")
        return self._get(f"/api/naics/{code}/metrics/{months}/{period_grouping}/")

    def get_business_type(self, code: str) -> dict[str, Any]:
        """Get a business type by code (`/api/business_types/{code}/`)."""
        if not code:
            raise TangoValidationError("Business type code is required")
        return self._get(f"/api/business_types/{code}/")

    def list_assistance_listings(
        self, page: int = 1, limit: int = 25
    ) -> PaginatedResponse[dict[str, Any]]:
        """List Assistance Listings (CFDA programs) (`/api/assistance_listings/`)."""
        params: dict[str, Any] = {"page": page, "limit": min(limit, 100)}
        data = self._get("/api/assistance_listings/", params)
        return PaginatedResponse(
            count=int(data.get("count", 0)),
            next=data.get("next"),
            previous=data.get("previous"),
            results=list(data.get("results") or []),
        )

    def get_assistance_listing(self, number: str) -> dict[str, Any]:
        """Get an Assistance Listing by CFDA number (`/api/assistance_listings/{number}/`)."""
        if not number:
            raise TangoValidationError("Assistance listing number is required")
        return self._get(f"/api/assistance_listings/{number}/")

    def list_mas_sins(
        self,
        page: int = 1,
        limit: int = 25,
        search: str | None = None,
    ) -> PaginatedResponse[dict[str, Any]]:
        """List GSA MAS SINs (`/api/mas_sins/`)."""
        params: dict[str, Any] = {"page": page, "limit": min(limit, 100)}
        if search is not None:
            params["search"] = search
        data = self._get("/api/mas_sins/", params)
        return PaginatedResponse(
            count=int(data.get("count", 0)),
            next=data.get("next"),
            previous=data.get("previous"),
            results=list(data.get("results") or []),
        )

    def get_mas_sin(self, sin: str) -> dict[str, Any]:
        """Get a MAS SIN by code (`/api/mas_sins/{sin}/`)."""
        if not sin:
            raise TangoValidationError("MAS SIN is required")
        return self._get(f"/api/mas_sins/{sin}/")

    # ============================================================================
    # Entity sub-resources
    # ============================================================================

    def _entity_subresource_contracts(
        self,
        uei: str,
        endpoint_segment: str,
        model: type,
        *,
        limit: int = 25,
        cursor: str | None = None,
        shape: str | None = None,
        flat: bool = False,
        flat_lists: bool = False,
        joiner: str = ".",
        **filters: Any,
    ) -> PaginatedResponse:
        """Shared helper for /api/entities/{uei}/{contracts,idvs,otas,otidvs}/."""
        params: dict[str, Any] = {"limit": min(limit, 100)}
        if cursor:
            params["cursor"] = cursor
        if shape is None:
            # Conservative minimal default — caller can override per-call.
            shape = "key,piid,award_date,recipient(display_name)"
        if shape:
            params["shape"] = shape
            if flat:
                params["flat"] = "true"
                if joiner:
                    params["joiner"] = joiner
            if flat_lists:
                params["flat_lists"] = "true"
        for k, v in filters.items():
            if v is not None:
                params[k] = v
        data = self._get(f"/api/entities/{uei}/{endpoint_segment}/", params)
        results = [
            self._parse_response_with_shape(obj, shape, model, flat, flat_lists, joiner=joiner)
            for obj in (data.get("results") or [])
        ]
        return PaginatedResponse(
            count=int(data.get("count") or len(results)),
            next=data.get("next"),
            previous=data.get("previous"),
            results=results,
            cursor=data.get("cursor"),
            page_metadata=data.get("page_metadata"),
        )

    def list_entity_contracts(
        self,
        uei: str,
        limit: int = 25,
        cursor: str | None = None,
        shape: str | None = None,
        flat: bool = False,
        flat_lists: bool = False,
        joiner: str = ".",
        ordering: str | None = None,
        search: str | None = None,
        **filters: Any,
    ) -> PaginatedResponse:
        """List contracts awarded to an entity (`/api/entities/{uei}/contracts/`).

        Supports the same filter set as /api/contracts/ scoped to the recipient.
        """
        if not uei:
            raise TangoValidationError("UEI is required")
        if shape is None:
            shape = ShapeConfig.CONTRACTS_MINIMAL
        return self._entity_subresource_contracts(
            uei,
            "contracts",
            Contract,
            limit=limit,
            cursor=cursor,
            shape=shape,
            flat=flat,
            flat_lists=flat_lists,
            joiner=joiner,
            ordering=ordering,
            search=search,
            **filters,
        )

    def list_entity_idvs(
        self,
        uei: str,
        limit: int = 25,
        cursor: str | None = None,
        shape: str | None = None,
        flat: bool = False,
        flat_lists: bool = False,
        joiner: str = ".",
        ordering: str | None = None,
        search: str | None = None,
        **filters: Any,
    ) -> PaginatedResponse:
        """List IDVs held by an entity (`/api/entities/{uei}/idvs/`)."""
        if not uei:
            raise TangoValidationError("UEI is required")
        if shape is None:
            shape = ShapeConfig.IDVS_MINIMAL
        return self._entity_subresource_contracts(
            uei,
            "idvs",
            IDV,
            limit=limit,
            cursor=cursor,
            shape=shape,
            flat=flat,
            flat_lists=flat_lists,
            joiner=joiner,
            ordering=ordering,
            search=search,
            **filters,
        )

    def list_entity_otas(
        self,
        uei: str,
        limit: int = 25,
        cursor: str | None = None,
        shape: str | None = None,
        flat: bool = False,
        flat_lists: bool = False,
        joiner: str = ".",
        ordering: str | None = None,
        search: str | None = None,
        **filters: Any,
    ) -> PaginatedResponse:
        """List OTAs held by an entity (`/api/entities/{uei}/otas/`)."""
        if not uei:
            raise TangoValidationError("UEI is required")
        if shape is None:
            shape = ShapeConfig.OTAS_MINIMAL
        return self._entity_subresource_contracts(
            uei,
            "otas",
            OTA,
            limit=limit,
            cursor=cursor,
            shape=shape,
            flat=flat,
            flat_lists=flat_lists,
            joiner=joiner,
            ordering=ordering,
            search=search,
            **filters,
        )

    def list_entity_otidvs(
        self,
        uei: str,
        limit: int = 25,
        cursor: str | None = None,
        shape: str | None = None,
        flat: bool = False,
        flat_lists: bool = False,
        joiner: str = ".",
        ordering: str | None = None,
        search: str | None = None,
        **filters: Any,
    ) -> PaginatedResponse:
        """List OTIDVs held by an entity (`/api/entities/{uei}/otidvs/`)."""
        if not uei:
            raise TangoValidationError("UEI is required")
        if shape is None:
            shape = ShapeConfig.OTIDVS_MINIMAL
        return self._entity_subresource_contracts(
            uei,
            "otidvs",
            OTIDV,
            limit=limit,
            cursor=cursor,
            shape=shape,
            flat=flat,
            flat_lists=flat_lists,
            joiner=joiner,
            ordering=ordering,
            search=search,
            **filters,
        )

    def list_entity_subawards(
        self,
        uei: str,
        page: int = 1,
        limit: int = 25,
        shape: str | None = None,
        flat: bool = False,
        flat_lists: bool = False,
        ordering: str | None = None,
        **filters: Any,
    ) -> PaginatedResponse:
        """List subawards for an entity (`/api/entities/{uei}/subawards/`)."""
        if not uei:
            raise TangoValidationError("UEI is required")
        params: dict[str, Any] = {"page": page, "limit": min(limit, 100)}
        if shape is None:
            shape = ShapeConfig.SUBAWARDS_MINIMAL
        if shape:
            params["shape"] = shape
            if flat:
                params["flat"] = "true"
            if flat_lists:
                params["flat_lists"] = "true"
        if ordering:
            params["ordering"] = ordering
        for k, v in filters.items():
            if v is not None:
                params[k] = v
        data = self._get(f"/api/entities/{uei}/subawards/", params)
        results = [
            self._parse_response_with_shape(obj, shape, Subaward, flat, flat_lists)
            for obj in (data.get("results") or [])
        ]
        return PaginatedResponse(
            count=int(data.get("count", 0)),
            next=data.get("next"),
            previous=data.get("previous"),
            results=results,
        )

    def list_entity_lcats(
        self,
        uei: str,
        page: int = 1,
        limit: int = 25,
        ordering: str | None = None,
        search: str | None = None,
        **filters: Any,
    ) -> PaginatedResponse[dict[str, Any]]:
        """List GSA-eLibrary Labor Categories (LCATs) for an entity
        (`/api/entities/{uei}/lcats/`).
        """
        if not uei:
            raise TangoValidationError("UEI is required")
        params: dict[str, Any] = {"page": page, "limit": min(limit, 100)}
        if ordering:
            params["ordering"] = ordering
        if search is not None:
            params["search"] = search
        for k, v in filters.items():
            if v is not None:
                params[k] = v
        data = self._get(f"/api/entities/{uei}/lcats/", params)
        return PaginatedResponse(
            count=int(data.get("count", 0)),
            next=data.get("next"),
            previous=data.get("previous"),
            results=list(data.get("results") or []),
        )

    def get_entity_metrics(self, uei: str, months: int, period_grouping: str) -> dict[str, Any]:
        """Get rolling metrics for an entity
        (`/api/entities/{uei}/metrics/{months}/{period_grouping}/`).
        """
        if not uei:
            raise TangoValidationError("UEI is required")
        return self._get(f"/api/entities/{uei}/metrics/{months}/{period_grouping}/")

    # ============================================================================
    # IDV sub-resources
    # ============================================================================

    def list_idv_lcats(
        self,
        key: str,
        page: int = 1,
        limit: int = 25,
        ordering: str | None = None,
        search: str | None = None,
        **filters: Any,
    ) -> PaginatedResponse[dict[str, Any]]:
        """List Labor Categories under an IDV (`/api/idvs/{key}/lcats/`)."""
        if not key:
            raise TangoValidationError("IDV key is required")
        params: dict[str, Any] = {"page": page, "limit": min(limit, 100)}
        if ordering:
            params["ordering"] = ordering
        if search is not None:
            params["search"] = search
        for k, v in filters.items():
            if v is not None:
                params[k] = v
        data = self._get(f"/api/idvs/{key}/lcats/", params)
        return PaginatedResponse(
            count=int(data.get("count", 0)),
            next=data.get("next"),
            previous=data.get("previous"),
            results=list(data.get("results") or []),
        )

    # ============================================================================
    # Agency sub-resources
    # ============================================================================

    def _agency_contracts(
        self,
        code: str,
        which: str,
        *,
        limit: int = 25,
        cursor: str | None = None,
        shape: str | None = None,
        flat: bool = False,
        flat_lists: bool = False,
        joiner: str = ".",
        ordering: str | None = None,
        search: str | None = None,
        **filters: Any,
    ) -> PaginatedResponse:
        if not code:
            raise TangoValidationError("Agency code is required")
        if which not in ("awarding", "funding"):
            raise TangoValidationError("Agency contracts which= must be 'awarding' or 'funding'")
        params: dict[str, Any] = {"limit": min(limit, 100)}
        if cursor:
            params["cursor"] = cursor
        if shape is None:
            shape = ShapeConfig.CONTRACTS_MINIMAL
        if shape:
            params["shape"] = shape
            if flat:
                params["flat"] = "true"
                if joiner:
                    params["joiner"] = joiner
            if flat_lists:
                params["flat_lists"] = "true"
        if ordering:
            params["ordering"] = ordering
        if search is not None:
            params["search"] = search
        for k, v in filters.items():
            if v is not None:
                params[k] = v
        data = self._get(f"/api/agencies/{code}/contracts/{which}/", params)
        results = [
            self._parse_response_with_shape(obj, shape, Contract, flat, flat_lists, joiner=joiner)
            for obj in (data.get("results") or [])
        ]
        return PaginatedResponse(
            count=int(data.get("count") or len(results)),
            next=data.get("next"),
            previous=data.get("previous"),
            results=results,
            cursor=data.get("cursor"),
            page_metadata=data.get("page_metadata"),
        )

    def list_agency_awarding_contracts(
        self,
        code: str,
        limit: int = 25,
        cursor: str | None = None,
        shape: str | None = None,
        flat: bool = False,
        flat_lists: bool = False,
        joiner: str = ".",
        ordering: str | None = None,
        search: str | None = None,
        **filters: Any,
    ) -> PaginatedResponse:
        """List contracts where this agency is the awarding agency
        (`/api/agencies/{code}/contracts/awarding/`).
        """
        return self._agency_contracts(
            code,
            "awarding",
            limit=limit,
            cursor=cursor,
            shape=shape,
            flat=flat,
            flat_lists=flat_lists,
            joiner=joiner,
            ordering=ordering,
            search=search,
            **filters,
        )

    def list_agency_funding_contracts(
        self,
        code: str,
        limit: int = 25,
        cursor: str | None = None,
        shape: str | None = None,
        flat: bool = False,
        flat_lists: bool = False,
        joiner: str = ".",
        ordering: str | None = None,
        search: str | None = None,
        **filters: Any,
    ) -> PaginatedResponse:
        """List contracts where this agency is the funding agency
        (`/api/agencies/{code}/contracts/funding/`).
        """
        return self._agency_contracts(
            code,
            "funding",
            limit=limit,
            cursor=cursor,
            shape=shape,
            flat=flat,
            flat_lists=flat_lists,
            joiner=joiner,
            ordering=ordering,
            search=search,
            **filters,
        )

    # ============================================================================
    # Opportunity attachment search & misc
    # ============================================================================

    def search_opportunity_attachments(
        self,
        q: str,
        top_k: int | None = None,
        include_extracted_text: bool | None = None,
    ) -> dict[str, Any]:
        """Semantic search over opportunity attachments
        (`/api/opportunities/attachment-search/`).
        """
        if not q:
            raise TangoValidationError("search_opportunity_attachments(): q is required")
        params: dict[str, Any] = {"q": q}
        if top_k is not None:
            params["top_k"] = top_k
        if include_extracted_text is not None:
            params["include_extracted_text"] = "true" if include_extracted_text else "false"
        return self._get("/api/opportunities/attachment-search/", params)

    def get_version(self) -> dict[str, Any]:
        """Get the Tango API version info (`/api/version/`)."""
        return self._get("/api/version/")

    def list_api_keys(self) -> dict[str, Any]:
        """List the authenticated user's API keys (`/api/api-keys/`)."""
        return self._get("/api/api-keys/")
