# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel

__all__ = ["EntityListResponse", "Result"]


class Result(BaseModel):
    legal_business_name: str

    purpose_of_registration_code: str

    uei: str

    business_types: Optional[object] = None

    dba_name: Optional[str] = None

    entity_url: Optional[str] = None

    physical_address: Optional[object] = None

    primary_naics: Optional[str] = None

    sba_business_types: Optional[object] = None


class EntityListResponse(BaseModel):
    count: int

    results: List[Result]

    next: Optional[str] = None

    previous: Optional[str] = None
