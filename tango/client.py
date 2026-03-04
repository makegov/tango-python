"""Tango API Client"""

import os
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
    BusinessType,
    Contract,
    Entity,
    Forecast,
    Grant,
    GsaElibraryContract,
    Location,
    Notice,
    Opportunity,
    Organization,
    PaginatedResponse,
    Protest,
    SearchFilters,
    ShapeConfig,
    Subaward,
    Vehicle,
    WebhookEndpoint,
    WebhookEventType,
    WebhookEventTypesResponse,
    WebhookSubjectTypeDefinition,
    WebhookSubscription,
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
    ):
        """
        Initialize the Tango API client

        Args:
            api_key: API key for authentication. If not provided, will attempt to load from
                    TANGO_API_KEY environment variable.
            base_url: Base URL for the API
        """
        # Load API key from environment if not provided
        self.api_key = api_key or os.getenv("TANGO_API_KEY")
        self.base_url = base_url.rstrip("/")

        # Build headers
        headers = {}
        if self.api_key:
            headers["X-API-KEY"] = self.api_key

        self.client = httpx.Client(headers=headers, timeout=30.0)

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
                raise TangoRateLimitError("Rate limit exceeded", response.status_code)
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

    def _post(self, endpoint: str, json_data: dict[str, Any]) -> dict[str, Any]:
        """Make a POST request"""
        return self._request("POST", endpoint, json_data=json_data)

    def _patch(self, endpoint: str, json_data: dict[str, Any]) -> dict[str, Any]:
        """Make a PATCH request"""
        return self._request("PATCH", endpoint, json_data=json_data)

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
        else:
            params["page"] = 1

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
    # Vehicles (Awards)
    # ============================================================================

    def list_vehicles(
        self,
        page: int = 1,
        limit: int = 25,
        shape: str | None = None,
        flat: bool = False,
        flat_lists: bool = False,
        joiner: str = ".",
        search: str | None = None,
    ) -> PaginatedResponse:
        """List Vehicles (solicitation-centric groupings of IDVs)."""
        params: dict[str, Any] = {"page": page, "limit": min(limit, 100)}

        if shape is None:
            shape = ShapeConfig.VEHICLES_MINIMAL
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
    ) -> PaginatedResponse:
        """List the IDV awardees for a Vehicle (`/api/vehicles/{uuid}/awardees/`)."""
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
        opportunity_number: str | None = None,
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
            opportunity_number: Opportunity number filter
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
            ("opportunity_number", opportunity_number),
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

    # ============================================================================
    # Webhooks (v2)
    # ============================================================================

    def list_webhook_event_types(self) -> WebhookEventTypesResponse:
        """Discover supported webhook event types and subject types."""
        data = self._get("/api/webhooks/event-types/")

        event_types = [
            WebhookEventType(
                event_type=str(e.get("event_type", "")),
                default_subject_type=str(e.get("default_subject_type", "")),
                description=str(e.get("description", "")),
                schema_version=int(e.get("schema_version", 1)),
            )
            for e in (data.get("event_types") or [])
            if isinstance(e, dict)
        ]

        subject_types = [str(x) for x in (data.get("subject_types") or [])]

        subject_type_definitions = [
            WebhookSubjectTypeDefinition(
                subject_type=str(d.get("subject_type", "")),
                description=str(d.get("description", "")),
                id_format=str(d.get("id_format", "")),
                status=str(d.get("status", "active")),
            )
            for d in (data.get("subject_type_definitions") or [])
            if isinstance(d, dict)
        ]

        return WebhookEventTypesResponse(
            event_types=event_types,
            subject_types=subject_types,
            subject_type_definitions=subject_type_definitions,
        )

    def list_webhook_subscriptions(
        self, page: int = 1, page_size: int | None = None
    ) -> PaginatedResponse[WebhookSubscription]:
        """
        List webhook subscriptions for the authenticated user's endpoint.

        Notes:
        - This endpoint uses `page` + `page_size` (tier-capped) rather than `limit`.
        """
        params: dict[str, Any] = {"page": page}
        if page_size is not None:
            params["page_size"] = page_size

        data = self._get("/api/webhooks/subscriptions/", params)
        results = [
            WebhookSubscription(
                id=str(item.get("id", "")),
                endpoint=str(item.get("endpoint")) if item.get("endpoint") is not None else None,
                subscription_name=str(item.get("subscription_name", "")),
                payload=item.get("payload"),
                created_at=str(item.get("created_at", "")),
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

    def get_webhook_subscription(self, subscription_id: str) -> WebhookSubscription:
        """Get a single webhook subscription by id (UUID)."""
        if not subscription_id:
            raise TangoValidationError("Webhook subscription_id is required")

        data = self._get(f"/api/webhooks/subscriptions/{subscription_id}/")
        return WebhookSubscription(
            id=str(data.get("id", "")),
            endpoint=str(data.get("endpoint")) if data.get("endpoint") is not None else None,
            subscription_name=str(data.get("subscription_name", "")),
            payload=data.get("payload"),
            created_at=str(data.get("created_at", "")),
        )

    def create_webhook_subscription(
        self, subscription_name: str, payload: dict[str, Any]
    ) -> WebhookSubscription:
        """Create a webhook subscription."""
        if not subscription_name:
            raise TangoValidationError("Webhook subscription_name is required")

        data = self._post(
            "/api/webhooks/subscriptions/",
            {"subscription_name": subscription_name, "payload": payload},
        )

        return WebhookSubscription(
            id=str(data.get("id", "")),
            endpoint=str(data.get("endpoint")) if data.get("endpoint") is not None else None,
            subscription_name=str(data.get("subscription_name", "")),
            payload=data.get("payload"),
            created_at=str(data.get("created_at", "")),
        )

    def update_webhook_subscription(
        self,
        subscription_id: str,
        *,
        subscription_name: str | None = None,
        payload: dict[str, Any] | None = None,
    ) -> WebhookSubscription:
        """Patch a webhook subscription."""
        if not subscription_id:
            raise TangoValidationError("Webhook subscription_id is required")

        body: dict[str, Any] = {}
        if subscription_name is not None:
            body["subscription_name"] = subscription_name
        if payload is not None:
            body["payload"] = payload

        data = self._patch(f"/api/webhooks/subscriptions/{subscription_id}/", body)
        return WebhookSubscription(
            id=str(data.get("id", "")),
            endpoint=str(data.get("endpoint")) if data.get("endpoint") is not None else None,
            subscription_name=str(data.get("subscription_name", "")),
            payload=data.get("payload"),
            created_at=str(data.get("created_at", "")),
        )

    def delete_webhook_subscription(self, subscription_id: str) -> None:
        """Delete a webhook subscription."""
        if not subscription_id:
            raise TangoValidationError("Webhook subscription_id is required")
        self._delete(f"/api/webhooks/subscriptions/{subscription_id}/")

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

    def create_webhook_endpoint(self, callback_url: str, is_active: bool = True) -> WebhookEndpoint:
        """
        Create a webhook endpoint for the authenticated user.

        Note:
        - The server generates `secret` and manages `name`.
        - Only one endpoint per user is allowed; if one already exists, this will fail.
        """
        if not callback_url:
            raise TangoValidationError("Webhook callback_url is required")

        data = self._post(
            "/api/webhooks/endpoints/",
            {"callback_url": callback_url, "is_active": is_active},
        )
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
        callback_url: str | None = None,
        is_active: bool | None = None,
    ) -> WebhookEndpoint:
        """Patch a webhook endpoint."""
        if not endpoint_id:
            raise TangoValidationError("Webhook endpoint_id is required")

        body: dict[str, Any] = {}
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

        If endpoint_id is not provided, the server will use your default endpoint.
        """
        body: dict[str, Any] = {}
        if endpoint_id:
            body["endpoint_id"] = endpoint_id
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

    def get_webhook_sample_payload(self, event_type: str | None = None) -> dict[str, Any]:
        """
        Fetch Tango-shaped sample webhook deliveries.

        - If event_type is provided, returns the single-event response.
        - Otherwise returns a `samples` mapping for all supported event types.
        """
        params: dict[str, Any] = {}
        if event_type:
            params["event_type"] = event_type
        return self._get("/api/webhooks/endpoints/sample-payload/", params)
