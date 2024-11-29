# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["EntityListParams"]


class EntityListParams(TypedDict, total=False):
    cage_code: str
    """CAGE Code"""

    limit: int
    """Number of results to return per page."""

    naics: str

    name: str
    """The company name"""

    page: int
    """A page number within the paginated result set."""

    psc: str

    purpose_of_registration_code: str

    search: str

    socioeconomic: str

    state: str

    uei: str
    """Unique Entity Identifier"""

    zip_code: str
