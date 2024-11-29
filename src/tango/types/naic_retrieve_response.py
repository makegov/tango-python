# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.


from .._models import BaseModel

__all__ = ["NaicRetrieveResponse"]


class NaicRetrieveResponse(BaseModel):
    code: int

    description: str
    """Naics Description"""
