# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime

from .office import Office
from .._models import BaseModel

__all__ = ["ContractListResponse", "Result", "ResultRecipient"]


class ResultRecipient(BaseModel):
    legal_business_name: str

    uei: str

    dba_name: Optional[str] = None


class Result(BaseModel):
    awarding_office: Office

    contract_award_unique_key: str

    funding_office: Office

    recipient: ResultRecipient

    set_aside: str

    award_date: Optional[datetime] = None

    award_piid: Optional[str] = None

    current_total_value: Optional[float] = None

    description: Optional[str] = None

    naics_code: Optional[int] = None

    obligated: Optional[float] = None

    potential_total_value: Optional[float] = None

    psc_code: Optional[str] = None


class ContractListResponse(BaseModel):
    count: int

    results: List[Result]

    next: Optional[str] = None

    previous: Optional[str] = None
