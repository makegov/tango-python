# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, List, Optional
from datetime import datetime

from .office import Office
from .._compat import PYDANTIC_V2
from .._models import BaseModel

__all__ = ["Idv", "ContractSet", "ContractSetRecipient", "Recipient"]


class ContractSetRecipient(BaseModel):
    legal_business_name: str

    uei: str

    dba_name: Optional[str] = None


class ContractSet(BaseModel):
    awarding_office: Office

    contract_award_unique_key: str

    funding_office: Office

    recipient: ContractSetRecipient

    set_aside: str

    award_date: Optional[datetime] = None

    award_piid: Optional[str] = None

    current_total_value: Optional[float] = None

    description: Optional[str] = None

    naics_code: Optional[int] = None

    obligated: Optional[float] = None

    potential_total_value: Optional[float] = None

    psc_code: Optional[str] = None


class Recipient(BaseModel):
    legal_business_name: str

    uei: str

    dba_name: Optional[str] = None


class Idv(BaseModel):
    awarding_office: Office

    contract_award_unique_key: str

    contract_set: List[ContractSet]

    funding_office: Office

    idv_set: List[Idv]

    idv_type: Dict[str, str]

    recipient: Recipient

    set_aside: str

    award_date: Optional[datetime] = None

    award_piid: Optional[str] = None

    current_total_value: Optional[float] = None

    description: Optional[str] = None

    naics_code: Optional[int] = None

    obligated: Optional[float] = None

    potential_total_value: Optional[float] = None

    psc_code: Optional[str] = None


if PYDANTIC_V2:
    Idv.model_rebuild()
    ContractSet.model_rebuild()
    ContractSetRecipient.model_rebuild()
    Recipient.model_rebuild()
else:
    Idv.update_forward_refs()  # type: ignore
    ContractSet.update_forward_refs()  # type: ignore
    ContractSetRecipient.update_forward_refs()  # type: ignore
    Recipient.update_forward_refs()  # type: ignore
