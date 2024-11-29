# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .office import Office
from .._models import BaseModel

__all__ = ["OfficeListResponse"]


class OfficeListResponse(BaseModel):
    count: int

    results: List[Office]

    next: Optional[str] = None

    previous: Optional[str] = None
