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
    Agency,
    BusinessType,
    Contract,
    Entity,
    Forecast,
    Grant,
    Location,
    Notice,
    Opportunity,
    PaginatedResponse,
    SearchFilters,
    ShapeConfig,
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
            data = self._unflatten_response(data)

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
    def list_agencies(self, page: int = 1, limit: int = 25) -> PaginatedResponse:
        """List all agencies"""
        params = {"page": page, "limit": min(limit, 100)}
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

    # Contract endpoints
    def list_contracts(
        self,
        page: int = 1,
        limit: int = 25,
        shape: str | None = None,
        flat: bool = False,
        flat_lists: bool = False,
        filters: SearchFilters | dict[str, Any] | None = None,
        **kwargs,
    ) -> PaginatedResponse:
        """
        List contracts with optional filtering

        Args:
            page: Page number
            limit: Results per page (max 100)
            shape: Response shape string (defaults to minimal shape).
                   Use None to disable shaping, ShapeConfig.CONTRACTS_MINIMAL for minimal,
                   or provide custom shape string
            flat: If True, flatten nested objects in shaped response using dot notation
            flat_lists: If True, flatten arrays using indexed keys (e.g., items.0.field)
            filters: Optional SearchFilters object or dict for backward compatibility.
                    Filter parameters can also be passed as keyword arguments.
            **kwargs: Filter parameters

                    Text search:
                    - keyword: Search contract descriptions (mapped to 'search' API param)

                    Date filters:
                    - award_date_gte: Award date >= (YYYY-MM-DD)
                    - award_date_lte: Award date <= (YYYY-MM-DD)
                    - pop_start_date_gte: Period of performance start date >=
                    - pop_start_date_lte: Period of performance start date <=
                    - pop_end_date_gte: Period of performance end date >=
                    - pop_end_date_lte: Period of performance end date <=
                    - expiring_gte: Expiring on or after date
                    - expiring_lte: Expiring on or before date

                    Party filters:
                    - awarding_agency: Awarding agency code (e.g., "4700" for GSA)
                    - funding_agency: Funding agency code
                    - recipient_name: Vendor/recipient name (mapped to 'recipient' API param)
                    - recipient_uei: Vendor UEI (mapped to 'uei' API param)

                    Classification filters:
                    - naics_code: NAICS code (mapped to 'naics' API param)
                    - psc_code: PSC code (mapped to 'psc' API param)
                    - set_aside_type: Set-aside type (mapped to 'set_aside' API param)

                    Type filters:
                    - fiscal_year: Fiscal year (exact match)
                    - fiscal_year_gte: Fiscal year >=
                    - fiscal_year_lte: Fiscal year <=
                    - award_type: Award type code

                    Identifiers:
                    - piid: Procurement Instrument Identifier
                    - solicitation_identifier: Solicitation ID

                    Sorting:
                    - sort: Field to sort by (combined with 'order')
                    - order: Sort order ('asc' or 'desc', default 'asc')

        Examples:
            >>> # Simple usage
            >>> contracts = client.list_contracts(limit=10)

            >>> # With keyword arguments
            >>> contracts = client.list_contracts(
            ...     awarding_agency="4700",  # GSA
            ...     award_date_gte="2023-01-01",
            ...     limit=25
            ... )

            >>> # Text search
            >>> contracts = client.list_contracts(keyword="software development")

            >>> # With SearchFilters object (legacy)
            >>> filters = SearchFilters(
            ...     keyword="IT",
            ...     awarding_agency="4700",
            ...     fiscal_year=2024
            ... )
            >>> contracts = client.list_contracts(filters=filters)

            >>> # Using new date range filters
            >>> contracts = client.list_contracts(
            ...     expiring_gte="2025-01-01",
            ...     expiring_lte="2025-12-31"
            ... )
        """
        # Start with explicit parameters
        params: dict[str, Any] = {"page": page, "limit": min(limit, 100)}

        # Handle filters parameter (backward compatibility)
        filter_dict: dict[str, Any] = {}
        if filters is not None:
            if hasattr(filters, "to_dict"):
                # SearchFilters object
                filter_dict = filters.to_dict()
            else:
                # dict
                filter_dict = filters

            # Extract page/limit from filters if using defaults
            if page == 1 and "page" in filter_dict:
                params["page"] = filter_dict.pop("page", 1)
            if limit == 25 and "limit" in filter_dict:
                params["limit"] = min(filter_dict.pop("limit", 25), 100)

        # Merge kwargs and filter_dict (kwargs take precedence)
        filter_params = {**filter_dict, **kwargs}

        # Explicitly exclude shape-related parameters from filter_params
        # These are handled separately and should not be sent as query parameters
        shape_related_params = {"shape", "flat", "flat_lists"}
        for param in shape_related_params:
            filter_params.pop(param, None)

        # Extract page/limit from kwargs if provided (override explicit params)
        if "page" in filter_params:
            params["page"] = filter_params.pop("page")
        if "limit" in filter_params:
            params["limit"] = min(filter_params.pop("limit"), 100)

        # Add shape parameter with default minimal shape
        # This is separate from filter parameters and controls response fields, not filtering
        if shape is None:
            shape = ShapeConfig.CONTRACTS_MINIMAL
        if shape:
            params["shape"] = shape
            if flat:
                params["flat"] = "true"
            if flat_lists:
                params["flat_lists"] = "true"

        # Process filter parameters - convert award amounts to strings
        # Map Python parameter names to API parameter names if needed
        # Then update params with all filters (excluding None values)
        # This matches the pattern used by other endpoints (params.update(filters))

        # Map Python parameter names to API parameter names
        # The API may expect different parameter names than our Python interface
        api_param_mapping = {
            "naics_code": "naics",  # API expects 'naics' not 'naics_code'
            "keyword": "search",  # API expects 'search' not 'keyword'
            "psc_code": "psc",  # API expects 'psc' not 'psc_code'
            "recipient_name": "recipient",  # API expects 'recipient' not 'recipient_name'
            "recipient_uei": "uei",  # API expects 'uei' not 'recipient_uei'
            "set_aside_type": "set_aside",  # API expects 'set_aside' not 'set_aside_type'
        }

        # Handle sort + order → ordering conversion
        # API expects single 'ordering' parameter with '-' prefix for descending
        sort_field = filter_params.pop("sort", None)
        sort_order = filter_params.pop("order", None)
        if sort_field:
            # Prefix with '-' for descending order
            prefix = "-" if sort_order == "desc" else ""
            filter_params["ordering"] = f"{prefix}{sort_field}"

        # Apply parameter name mapping and process values
        api_params = {}
        for key, value in filter_params.items():
            if value is None:
                continue  # Skip None values
            # Map to API parameter name if needed
            api_key = api_param_mapping.get(key, key)
            api_params[api_key] = value

        # Update params with all filter parameters
        # This is the same pattern as other endpoints use
        params.update(api_params)

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

    # Entity endpoints
    def list_entities(
        self,
        page: int = 1,
        limit: int = 25,
        shape: str | None = None,
        flat: bool = False,
        flat_lists: bool = False,
        search: str | None = None,
        **filters,
    ) -> PaginatedResponse:
        """
        List entities (vendors/recipients)

        Args:
            page: Page number
            limit: Results per page (max 100)
            shape: Response shape string (defaults to minimal shape)
            flat: If True, flatten nested objects in shaped response
            flat_lists: If True, flatten arrays using indexed keys
            search: Search query (maps to 'q' parameter)
            **filters: Additional filter parameters (uei, cage_code, etc.)
        """
        params = {"page": page, "limit": min(limit, 100)}

        # Add shape parameter with default minimal shape
        if shape is None:
            shape = ShapeConfig.ENTITIES_MINIMAL
        if shape:
            params["shape"] = shape
            if flat:
                params["flat"] = "true"
            if flat_lists:
                params["flat_lists"] = "true"

        # Map 'search' parameter to 'q' (query parameter)
        if search:
            params["search"] = search

        params.update(filters)

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
        **filters,
    ) -> PaginatedResponse:
        """
        List contract forecasts

        Args:
            page: Page number
            limit: Results per page (max 100)
            shape: Response shape string (defaults to minimal shape)
            flat: If True, flatten nested objects in shaped response
            flat_lists: If True, flatten arrays using indexed keys
            **filters: Additional filter parameters
        """
        params = {"page": page, "limit": min(limit, 100)}

        # Add shape parameter with default minimal shape
        if shape is None:
            shape = ShapeConfig.FORECASTS_MINIMAL
        if shape:
            params["shape"] = shape
            if flat:
                params["flat"] = "true"
            if flat_lists:
                params["flat_lists"] = "true"

        params.update(filters)

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
        **filters,
    ) -> PaginatedResponse:
        """
        List contract opportunities/solicitations

        Args:
            page: Page number
            limit: Results per page (max 100)
            shape: Response shape string (defaults to minimal shape)
            flat: If True, flatten nested objects in shaped response
            flat_lists: If True, flatten arrays using indexed keys
            **filters: Additional filter parameters
        """
        params = {"page": page, "limit": min(limit, 100)}

        # Add shape parameter with default minimal shape
        if shape is None:
            shape = ShapeConfig.OPPORTUNITIES_MINIMAL
        if shape:
            params["shape"] = shape
            if flat:
                params["flat"] = "true"
            if flat_lists:
                params["flat_lists"] = "true"

        params.update(filters)

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
        **filters,
    ) -> PaginatedResponse:
        """
        List contract notices

        Args:
            page: Page number
            limit: Results per page (max 100)
            shape: Response shape string (defaults to minimal shape).
                   Use None to disable shaping, ShapeConfig.NOTICES_MINIMAL for minimal,
                   or provide custom shape string
            flat: If True, flatten nested objects in shaped response
            flat_lists: If True, flatten arrays using indexed keys
            **filters: Additional filter parameters
        """
        params = {"page": page, "limit": min(limit, 100)}

        # Add shape parameter with default minimal shape
        if shape is None:
            shape = ShapeConfig.NOTICES_MINIMAL
        if shape:
            params["shape"] = shape
            if flat:
                params["flat"] = "true"
            if flat_lists:
                params["flat_lists"] = "true"

        params.update(filters)

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

    # Grant endpoints
    def list_grants(
        self,
        page: int = 1,
        limit: int = 25,
        shape: str | None = None,
        flat: bool = False,
        flat_lists: bool = False,
        **filters,
    ) -> PaginatedResponse:
        """
        List grants

        Args:
            page: Page number
            limit: Results per page (max 100)
            shape: Response shape string (defaults to minimal shape).
                   Use None to disable shaping, ShapeConfig.GRANTS_MINIMAL for minimal,
                   or provide custom shape string
            flat: If True, flatten nested objects in shaped response
            flat_lists: If True, flatten arrays using indexed keys
            **filters: Additional filter parameters
        """
        params = {"page": page, "limit": min(limit, 100)}

        # Add shape parameter with default minimal shape
        if shape is None:
            shape = ShapeConfig.GRANTS_MINIMAL
        if shape:
            params["shape"] = shape
            if flat:
                params["flat"] = "true"
            if flat_lists:
                params["flat_lists"] = "true"

        params.update(filters)

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
