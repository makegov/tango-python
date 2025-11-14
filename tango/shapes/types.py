"""Predefined TypedDict type for the default contract shape

This module provides an explicit TypedDict definition for the default contract shape
used by list_contracts(). This enables better IDE autocomplete
and static type checking for shaped responses.

Examples:
    >>> from tango import TangoClient, ShapeConfig
    >>> from tango.shapes.types import ContractMinimalShaped
    >>>
    >>> client = TangoClient(api_key="your-key")
    >>> response = client.list_contracts(shape=ShapeConfig.CONTRACTS_MINIMAL)
    >>> contract: ContractMinimalShaped = response.results[0]
    >>> print(contract['key'])
"""

from datetime import date
from decimal import Decimal
from typing import TypedDict


class RecipientMinimalShaped(TypedDict):
    """Shaped type for minimal recipient information"""

    display_name: str


class ContractMinimalShaped(TypedDict):
    """Shaped type for ShapeConfig.CONTRACTS_MINIMAL (default for list_contracts)

    Fields: key, piid, award_date, recipient(display_name),
            description, total_contract_value
    """

    key: str
    piid: str | None
    award_date: date | None
    recipient: RecipientMinimalShaped | None
    description: str
    total_contract_value: Decimal | None


__all__ = [
    "ContractMinimalShaped",
    "RecipientMinimalShaped",
]
