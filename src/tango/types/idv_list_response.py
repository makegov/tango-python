# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Optional

from .idv import Idv
from .._compat import PYDANTIC_V2
from .._models import BaseModel

__all__ = ["IdvListResponse"]


class IdvListResponse(BaseModel):
    count: int

    results: List[Idv]

    next: Optional[str] = None

    previous: Optional[str] = None


if PYDANTIC_V2:
    IdvListResponse.model_rebuild()
else:
    IdvListResponse.update_forward_refs()  # type: ignore
