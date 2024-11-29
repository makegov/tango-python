# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel

__all__ = ["ProductServiceCode"]


class ProductServiceCode(BaseModel):
    code: str

    level_1_category: Optional[str] = None

    level_1_category_code: Optional[int] = None

    level_2_category: Optional[str] = None

    level_2_category_code: Optional[str] = None

    parent: Optional[str] = None
