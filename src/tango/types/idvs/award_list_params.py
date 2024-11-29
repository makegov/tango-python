# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from datetime import date
from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["AwardListParams"]


class AwardListParams(TypedDict, total=False):
    path_contract_award_unique_key: Required[Annotated[str, PropertyInfo(alias="contract_award_unique_key")]]

    award_date: str
    """Filter by the award date"""

    award_date_gte: Annotated[Union[str, date], PropertyInfo(format="iso8601")]

    award_date_lte: Annotated[Union[str, date], PropertyInfo(format="iso8601")]

    awarding_agency: str
    """Filter by awarding agency or department"""

    query_contract_award_unique_key: Annotated[str, PropertyInfo(alias="contract_award_unique_key")]
    """The unique key for the contract award."""

    fiscal_year: int

    fiscal_year_gte: int

    fiscal_year_lte: int

    funding_agency: str
    """Filter by funding agency or department"""

    limit: int
    """Number of results to return per page."""

    naics: str

    ordering: str
    """Which field to use when ordering the results."""

    page: int
    """A page number within the paginated result set."""

    psc: str

    set_aside: str

    uei: str
    """Unique Entity Identifier"""
