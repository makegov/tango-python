# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel

__all__ = ["Office"]


class Office(BaseModel):
    agency: str

    code: str

    name: Optional[str] = None
