# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime

from .._models import BaseModel

__all__ = ["NoticeRetrieveResponse", "Attachments", "NoticeHistory", "Opportunity"]


class Attachments(BaseModel):
    attachment_id: str

    resource_id: str

    mime_type: Optional[str] = None

    name: Optional[str] = None

    posted_date: Optional[datetime] = None

    type: Optional[str] = None

    url: Optional[str] = None


class NoticeHistory(BaseModel):
    deleted: bool

    index: int

    latest: bool

    notice_id: str

    notice_type: str

    parent_notice: str

    posted_date: str

    related_notice: str

    solicitation_number: str

    title: str


class Opportunity(BaseModel):
    link: str

    opportunity_id: str


class NoticeRetrieveResponse(BaseModel):
    attachment_count: int

    attachments: Attachments
    """Base serializer for opportunity attachments"""

    last_updated: datetime

    notice_history: List[NoticeHistory]

    notice_id: str
    """This corresponds to the uuid in SAM.gov.

    You can have multiple notices for a given solicitation.
    """

    opportunity: Opportunity

    psc_code: Optional[str] = None

    sam_url: Optional[str] = None

    title: str

    active: Optional[bool] = None

    award_number: Optional[str] = None

    description: Optional[str] = None

    naics_code: Optional[str] = None

    posted_date: Optional[datetime] = None

    response_deadline: Optional[datetime] = None

    set_aside: Optional[str] = None

    solicitation_number: Optional[str] = None
