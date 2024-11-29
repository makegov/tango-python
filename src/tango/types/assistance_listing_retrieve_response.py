# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import date

from .._models import BaseModel

__all__ = ["AssistanceListingRetrieveResponse"]


class AssistanceListingRetrieveResponse(BaseModel):
    number: str

    published_date: date

    title: str

    applicant_eligibility: Optional[str] = None

    archived_date: Optional[date] = None

    benefit_eligibility: Optional[str] = None

    objectives: Optional[str] = None

    popular_name: Optional[str] = None
