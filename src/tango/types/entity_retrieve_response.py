# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional
from datetime import date

from .._models import BaseModel

__all__ = ["EntityRetrieveResponse"]


class EntityRetrieveResponse(BaseModel):
    awards_summary: Dict[str, object]

    legal_business_name: str

    purpose_of_registration_code: str

    purpose_of_registration_desc: str

    registration_status: str

    sam_registration_date: date

    uei: str

    business_types: Optional[object] = None

    cage_code: Optional[str] = None

    capabilities: Optional[str] = None

    congressional_district: Optional[str] = None

    country_of_incorporation_code: Optional[str] = None

    country_of_incorporation_desc: Optional[str] = None

    dba_name: Optional[str] = None

    description: Optional[str] = None

    dodaac: Optional[str] = None

    email_address: Optional[str] = None

    entity_division_name: Optional[str] = None

    entity_division_number: Optional[str] = None

    entity_start_date: Optional[str] = None

    entity_structure_code: Optional[str] = None

    entity_structure_desc: Optional[str] = None

    entity_type_code: Optional[str] = None

    entity_type_desc: Optional[str] = None

    entity_url: Optional[str] = None

    evs_source: Optional[str] = None

    exclusion_status_flag: Optional[str] = None

    exclusion_url: Optional[str] = None

    fiscal_year_end_close_date: Optional[str] = None

    highest_owner: Optional[object] = None

    immediate_owner: Optional[object] = None

    keywords: Optional[str] = None

    last_update_date: Optional[date] = None

    mailing_address: Optional[object] = None

    naics_codes: Optional[object] = None

    organization_structure_code: Optional[str] = None

    organization_structure_desc: Optional[str] = None

    physical_address: Optional[object] = None

    primary_naics: Optional[str] = None

    profit_structure_code: Optional[str] = None

    profit_structure_desc: Optional[str] = None

    psc_codes: Optional[object] = None

    public_display_flag: Optional[str] = None

    registered: Optional[str] = None

    sam_activation_date: Optional[date] = None

    sam_expiration_date: Optional[date] = None

    sba_business_types: Optional[object] = None

    state_of_incorporation_code: Optional[str] = None

    state_of_incorporation_desc: Optional[str] = None

    submission_date: Optional[date] = None

    uei_creation_date: Optional[date] = None

    uei_expiration_date: Optional[date] = None

    uei_status: Optional[str] = None
