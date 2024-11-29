# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List
from typing_extensions import TypeAlias

from .naics_code import NaicsCode

__all__ = ["NaicListResponse"]

NaicListResponse: TypeAlias = List[NaicsCode]
