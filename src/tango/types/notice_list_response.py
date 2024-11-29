# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime

from .._models import BaseModel

__all__ = ["NoticeListResponse", "Result", "ResultOpportunity"]


class ResultOpportunity(BaseModel):
    link: str

    opportunity_id: str


class Result(BaseModel):
    attachment_count: int

    last_updated: datetime

    notice_id: str
    """This corresponds to the uuid in SAM.gov.

    You can have multiple notices for a given solicitation.
    """

    opportunity: ResultOpportunity

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


class NoticeListResponse(BaseModel):
    count: int

    results: List[Result]

    next: Optional[str] = None

    previous: Optional[str] = None
