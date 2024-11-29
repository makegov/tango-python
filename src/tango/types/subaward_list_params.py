# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["SubawardListParams"]


class SubawardListParams(TypedDict, total=False):
    awarding_agency: str
    """Awarding agency code"""

    fiscal_year: int

    fiscal_year_gte: int

    fiscal_year_lte: int

    funding_agency: str
    """Awarding agency code"""

    limit: int
    """Number of results to return per page."""

    page: int
    """A page number within the paginated result set."""

    prime_uei: str
    """Unique Entity Identifier"""

    sub_uei: str
    """Unique Entity Identifier"""
