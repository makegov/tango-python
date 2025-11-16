"""Tango API utility models and shape configurations

This module contains utility classes and predefined shape configurations for the Tango SDK.
All resource models (Contract, Entity, Grant, etc.) are now dynamically generated at runtime
based on the shape parameter provided to API methods.

For schema definitions used by the dynamic model system, see tango.shapes.explicit_schemas.

Note: The minimal class definitions below (Contract, Entity, etc.) are kept ONLY for schema
registry purposes and are NOT used for creating instances. All instances are created dynamically.
"""

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Final, TypeVar

T = TypeVar("T")


# ============================================================================
# UTILITY CLASSES
# ============================================================================


@dataclass
class SearchFilters:
    """Search filter parameters for contract search

    This is a convenience class for passing search parameters to list_contracts().
    All fields are optional and will be converted to query parameters.
    You can also pass these parameters directly to list_contracts() as keyword arguments.

    Note: Some parameters are automatically mapped to the correct API parameter names:
    - keyword → search
    - naics_code → naics
    - psc_code → psc
    - recipient_name → recipient
    - recipient_uei → uei
    - set_aside_type → set_aside
    - sort + order → ordering
    """

    # Pagination
    page: int = 1
    limit: int = 25

    # Text search
    keyword: str | None = None  # Mapped to 'search' API param

    # Date filters
    award_date_gte: str | None = None
    award_date_lte: str | None = None
    pop_start_date_gte: str | None = None  # Period of performance start date >=
    pop_start_date_lte: str | None = None  # Period of performance start date <=
    pop_end_date_gte: str | None = None  # Period of performance end date >=
    pop_end_date_lte: str | None = None  # Period of performance end date <=
    expiring_gte: str | None = None  # Expiring on or after
    expiring_lte: str | None = None  # Expiring on or before

    # Party filters
    awarding_agency: str | None = None
    funding_agency: str | None = None
    recipient_name: str | None = None  # Mapped to 'recipient' API param
    recipient_uei: str | None = None  # Mapped to 'uei' API param

    # Classification filters
    naics_code: str | None = None  # Mapped to 'naics' API param
    psc_code: str | None = None  # Mapped to 'psc' API param
    set_aside_type: str | None = None  # Mapped to 'set_aside' API param

    # Type filters
    fiscal_year: int | None = None
    fiscal_year_gte: int | None = None  # Fiscal year >=
    fiscal_year_lte: int | None = None  # Fiscal year <=
    award_type: str | None = None

    # Identifiers
    piid: str | None = None  # Procurement Instrument Identifier
    solicitation_identifier: str | None = None

    # Sorting
    sort: str | None = None  # Combined with 'order' into 'ordering' API param
    order: str | None = None  # 'asc' or 'desc'

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for API parameters"""
        return {k: v for k, v in self.__dict__.items() if v is not None}


# ============================================================================
# MINIMAL CLASS DEFINITIONS FOR SCHEMA REGISTRY
# These are NOT used for creating instances - only for schema validation
# ============================================================================


@dataclass
class Department:
    """Schema definition for Department (not used for instances)"""

    name: str
    code: str


@dataclass
class Agency:
    """Schema definition for Agency (not used for instances)"""

    code: str
    name: str
    abbreviation: str | None = None
    department: Department | None = None


@dataclass
class Location:
    """Schema definition for Location (not used for instances)"""

    address_line1: str | None = None
    address_line2: str | None = None
    city: str | None = None
    state: str | None = None
    state_code: str | None = None
    zip_code: str | None = None
    zip: str | None = None
    zip4: str | None = None
    country: str | None = None
    country_code: str | None = None
    county: str | None = None
    congressional_district: str | None = None
    latitude: float | None = None
    longitude: float | None = None


@dataclass
class NAICSCode:
    """Schema definition for NAICS Code (not used for instances)"""

    code: str
    description: str | None = None
    year: int | None = None


@dataclass
class PSCCode:
    """Schema definition for PSC Code (not used for instances)"""

    code: str
    description: str | None = None


@dataclass
class BusinessType:
    """Schema definition for Business Type (not used for instances)"""

    code: str
    name: str
    description: str | None = None
    business_type_code: str | None = None


@dataclass
class RecipientProfile:
    """Schema definition for RecipientProfile (not used for instances)"""

    uei: str | None = None
    cage_code: str | None = None
    display_name: str | None = None
    legal_business_name: str | None = None
    parent_uei: str | None = None
    parent_name: str | None = None
    business_types: list[str] | None = None
    location: Location | None = None


@dataclass
class Office:
    """Schema definition for Office (not used for instances)"""

    code: str
    name: str | None = None
    agency: str | None = None


@dataclass
class PlaceOfPerformance:
    """Schema definition for PlaceOfPerformance (not used for instances)"""

    city_name: str | None = None
    state_code: str | None = None
    state_name: str | None = None
    country_code: str | None = None
    country_name: str | None = None
    zip_code: str | None = None


@dataclass
class Competition:
    """Schema definition for Competition (not used for instances)"""

    contract_type: dict[str, Any] | None = None
    extent_competed: dict[str, Any] | None = None
    number_of_offers_received: int | None = None
    other_than_full_and_open_competition: dict[str, Any] | None = None
    solicitation_date: date | None = None
    solicitation_identifier: str | None = None
    solicitation_procedures: dict[str, Any] | None = None


@dataclass
class ContractOrIDVCompetition:
    """Schema definition for ContractOrIDVCompetition (alias for Competition)"""

    contract_type: dict[str, Any] | None = None
    extent_competed: dict[str, Any] | None = None
    number_of_offers_received: int | None = None
    other_than_full_and_open_competition: dict[str, Any] | None = None
    solicitation_date: date | None = None
    solicitation_identifier: str | None = None
    solicitation_procedures: dict[str, Any] | None = None


@dataclass
class ParentAward:
    """Schema definition for ParentAward (not used for instances)"""

    key: str
    piid: str | None = None
    description: str | None = None
    idv_type: str | None = None


@dataclass
class LegislativeMandates:
    """Schema definition for LegislativeMandates (not used for instances)"""

    clinger_cohen_act_planning: dict[str, Any] | None = None
    construction_wage_rate_requirements: dict[str, Any] | None = None
    employment_eligibility_verification: dict[str, Any] | None = None
    interagency_contracting_authority: dict[str, Any] | None = None
    labor_standards: dict[str, Any] | None = None
    materials_supplies_articles_equipment: dict[str, Any] | None = None
    other_statutory_authority: dict[str, Any] | None = None
    service_contract_inventory: dict[str, Any] | None = None


@dataclass
class SubawardsSummary:
    """Schema definition for SubawardsSummary (not used for instances)"""

    count: int
    total_amount: Decimal


@dataclass
class AwardTransaction:
    """Schema definition for AwardTransaction (not used for instances)"""

    modification_number: str
    transaction_date: date
    action_type: dict[str, Any] | None = None
    description: str | None = None
    obligated: Decimal | None = None


@dataclass
class Contract:
    """Schema definition for Contract (not used for instances)"""

    id: str
    award_id: str
    recipient_name: str
    description: str
    award_amount: Decimal | None = None
    award_date: date | None = None
    fiscal_year: int | None = None
    recipient: RecipientProfile | None = None
    awarding_agency: Agency | None = None
    funding_agency: Agency | None = None
    place_of_performance: Location | None = None


@dataclass
class Entity:
    """Schema definition for Entity (not used for instances)"""

    key: str
    display_name: str
    uei: str | None = None
    cage_code: str | None = None
    legal_business_name: str | None = None
    business_types: list[str] | None = None
    physical_address: Location | None = None


@dataclass
class Grant:
    """Schema definition for Grant (not used for instances)"""

    grant_id: int
    opportunity_number: str
    title: str
    agency_code: str | None = None
    status: str | None = None
    description: str | None = None
    last_updated: datetime | None = None


@dataclass
class Forecast:
    """Schema definition for Forecast (not used for instances)"""

    id: int
    title: str
    description: str | None = None
    anticipated_award_date: date | None = None
    fiscal_year: int | None = None
    naics_code: str | None = None
    status: str | None = None
    is_active: bool | None = None
    agency: str | None = None


@dataclass
class Opportunity:
    """Schema definition for Opportunity (not used for instances)"""

    opportunity_id: str
    title: str
    solicitation_number: str | None = None
    description: str | None = None
    response_deadline: datetime | None = None
    active: bool | None = None
    naics_code: str | None = None
    psc_code: str | None = None


@dataclass
class Notice:
    """Schema definition for Notice (not used for instances)"""

    notice_id: str
    title: str
    solicitation_number: str | None = None
    description: str | None = None
    posted_date: datetime | None = None
    naics_code: str | None = None


@dataclass
class AssistanceListing:
    """Schema definition for Assistance Listing (not used for instances)"""

    number: str
    title: str
    cfda_number: str | None = None
    popular_name: str | None = None
    federal_agency: str | None = None
    authorization: str | None = None
    objectives: str | None = None
    types_of_assistance: list[str] | None = None
    uses_and_use_restrictions: str | None = None
    applicant_eligibility: str | None = None
    beneficiary_eligibility: str | None = None
    website_address: str | None = None
    url: str | None = None
    published_date: date | None = None
    archived_date: date | None = None


@dataclass
class APIKey:
    """Schema definition for API Key"""

    key: str
    name: str
    created_at: str | None = None


@dataclass
class PaginatedResponse[T]:
    """Paginated API response

    Generic container for paginated list responses from the Tango API.
    The results list contains dynamically generated model instances based
    on the shape parameter used in the API request.

    Attributes:
        count: Total number of results available
        next: URL for the next page of results (None if last page)
        previous: URL for the previous page of results (None if first page)
        results: List of result items (type depends on shape parameter)
        page_metadata: Optional metadata about the current page

    Examples:
        >>> from tango import TangoClient, ShapeConfig
        >>> client = TangoClient(api_key="your-key")
        >>> response = client.list_contracts(shape=ShapeConfig.CONTRACTS_MINIMAL)
        >>> print(f"Total: {response.count}")
        >>> for contract in response.results:
        ...     print(contract["piid"])
    """

    count: int
    next: str | None
    previous: str | None
    results: list[T]
    page_metadata: dict[str, Any] | None = None


class ShapeConfig:
    """Predefined response shape configurations used as defaults for API methods

    These shapes are used as defaults when no shape parameter is provided.
    Users can provide any valid shape string - these are just convenient defaults.
    """

    # Default for list_contracts() and search_contracts()
    CONTRACTS_MINIMAL: Final = (
        "key,piid,award_date,recipient(display_name),description,total_contract_value"
    )

    # Default for list_entities()
    ENTITIES_MINIMAL: Final = "uei,legal_business_name,cage_code,business_types"

    # Default for get_entity()
    ENTITIES_COMPREHENSIVE: Final = (
        "uei,legal_business_name,dba_name,cage_code,"
        "business_types,primary_naics,naics_codes,psc_codes,"
        "email_address,entity_url,description,capabilities,keywords,"
        "physical_address,mailing_address,"
        "federal_obligations,congressional_district"
    )

    # Default for list_forecasts()
    FORECASTS_MINIMAL: Final = "id,title,anticipated_award_date,fiscal_year,naics_code,status"

    # Default for list_opportunities()
    OPPORTUNITIES_MINIMAL: Final = (
        "opportunity_id,title,solicitation_number,response_deadline,active"
    )

    # Default for list_notices()
    NOTICES_MINIMAL: Final = "notice_id,title,solicitation_number,posted_date"

    # Default for list_grants()
    GRANTS_MINIMAL: Final = "grant_id,opportunity_number,title,status(*),agency_code"
