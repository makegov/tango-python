# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["OfficeListParams"]


class OfficeListParams(TypedDict, total=False):
    limit: int
    """Number of results to return per page."""

    page: int
    """A page number within the paginated result set."""

    search: str
    """Search for an office"""
