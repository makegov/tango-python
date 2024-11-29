# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.


from .._models import BaseModel

__all__ = ["BusinessType"]


class BusinessType(BaseModel):
    code: str
    """The SAM code for the business type"""

    name: str
    """Business types that can classify an entity"""
