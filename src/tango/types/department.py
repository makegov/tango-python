# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel

__all__ = ["Department"]


class Department(BaseModel):
    name: str
    """The Department name"""

    abbreviation: Optional[str] = None

    code: Optional[int] = None
