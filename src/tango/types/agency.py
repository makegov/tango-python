# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel

__all__ = ["Agency"]


class Agency(BaseModel):
    code: str

    department: int

    name: str

    abbreviation: Optional[str] = None
