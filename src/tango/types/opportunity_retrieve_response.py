# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional
from datetime import date, datetime

from .._models import BaseModel

__all__ = [
    "OpportunityRetrieveResponse",
    "Attachments",
    "Meta",
    "MetaNoticeType",
    "Notices",
    "Agency",
    "Department",
    "Office",
]


class Attachments(BaseModel):
    attachment_id: str

    resource_id: str

    mime_type: Optional[str] = None

    name: Optional[str] = None

    posted_date: Optional[datetime] = None

    type: Optional[str] = None

    url: Optional[str] = None


class MetaNoticeType(BaseModel):
    code: str

    type: str


class Meta(BaseModel):
    attachments_count: int

    notice_type: MetaNoticeType

    notices_count: int


class Notices(BaseModel):
    notice_id: str

    notice_type: str

    posted_date: date

    title: str


class Agency(BaseModel):
    code: str

    name: str

    abbreviation: Optional[str] = None


class Department(BaseModel):
    name: str
    """The Department name"""

    abbreviation: Optional[str] = None

    code: Optional[int] = None


class Office(BaseModel):
    code: str

    name: Optional[str] = None


class OpportunityRetrieveResponse(BaseModel):
    attachments: Attachments
    """Base serializer for opportunity attachments"""

    description: str

    meta: Meta

    notices: Notices

    opportunity_id: str

    sam_url: str

    set_aside: Dict[str, str]

    title: str

    active: Optional[bool] = None

    agency: Optional[Agency] = None

    award_number: Optional[str] = None

    department: Optional[Department] = None

    first_notice_date: Optional[datetime] = None

    last_notice_date: Optional[datetime] = None

    naics_code: Optional[int] = None

    office: Optional[Office] = None

    place_of_performance: Optional[object] = None

    psc_code: Optional[str] = None

    response_deadline: Optional[datetime] = None

    solicitation_number: Optional[str] = None
