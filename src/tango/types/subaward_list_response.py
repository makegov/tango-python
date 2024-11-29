# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel
from .subaward import Subaward

__all__ = ["SubawardListResponse"]


class SubawardListResponse(BaseModel):
    count: int

    results: List[Subaward]

    next: Optional[str] = None

    previous: Optional[str] = None
