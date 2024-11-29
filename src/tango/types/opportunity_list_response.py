# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional
from datetime import datetime

from .._models import BaseModel

__all__ = [
    "OpportunityListResponse",
    "Result",
    "ResultMeta",
    "ResultMetaNoticeType",
    "ResultAgency",
    "ResultDepartment",
    "ResultOffice",
]


class ResultMetaNoticeType(BaseModel):
    code: str

    type: str


class ResultMeta(BaseModel):
    attachments_count: int

    notice_type: ResultMetaNoticeType

    notices_count: int


class ResultAgency(BaseModel):
    code: str

    name: str

    abbreviation: Optional[str] = None


class ResultDepartment(BaseModel):
    name: str
    """The Department name"""

    abbreviation: Optional[str] = None

    code: Optional[int] = None


class ResultOffice(BaseModel):
    code: str

    name: Optional[str] = None


class Result(BaseModel):
    meta: ResultMeta

    notices: List[str]

    opportunity_id: str

    sam_url: str

    set_aside: Dict[str, str]

    title: str

    active: Optional[bool] = None

    agency: Optional[ResultAgency] = None

    award_number: Optional[str] = None

    department: Optional[ResultDepartment] = None

    first_notice_date: Optional[datetime] = None

    last_notice_date: Optional[datetime] = None

    naics_code: Optional[int] = None

    office: Optional[ResultOffice] = None

    place_of_performance: Optional[object] = None

    psc_code: Optional[str] = None

    response_deadline: Optional[datetime] = None

    solicitation_number: Optional[str] = None


class OpportunityListResponse(BaseModel):
    count: int

    results: List[Result]

    next: Optional[str] = None

    previous: Optional[str] = None
