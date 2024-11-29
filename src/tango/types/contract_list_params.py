# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["ContractListParams"]


class ContractListParams(TypedDict, total=False):
    award_date: str
    """
    <details><summary>Filter by award date</summary><ul><li><span>Accepted values: <var>2024-08-01</var>, <var>2024-08</var></span></li></ul></details>
    """

    award_date_gte: str
    """
    <details><summary>Filter by award date</summary><ul><li><span>Accepted values: <var>2024-08-01</var></span></li></ul></details>
    """

    award_date_lte: str
    """
    <details><summary>Filter by award date</summary><ul><li><span>Accepted values: <var>2024-08-01</var></span></li></ul></details>
    """

    awarding_agency: str
    """
    <details><summary>Filter by awarding agency</summary><ul><li>Accepts any agency or department code, acronym, or (partial) name</li><li>Disjunctive with <var>|</var> or <var>OR</var></li></ul></details>
    """

    fiscal_year: str
    """
    <details><summary>Filter by fiscal year</summary><ul><li><span>Accepted values: <var>2024</var></span></li></ul></details>
    """

    fiscal_year_gte: str
    """
    <details><summary>Filter by fiscal year</summary><ul><li><span>Accepted values: <var>2024</var></span></li></ul></details>
    """

    fiscal_year_lte: str
    """
    <details><summary>Filter by fiscal year</summary><ul><li><span>Accepted values: <var>2024</var></span></li></ul></details>
    """

    funding_agency: str
    """
    <details><summary>Filter by funding agency</summary><ul><li>Accepts any agency or department code, acronym, or (partial) name</li><li>Disjunctive with <var>|</var> or <var>OR</var></li></ul></details>
    """

    limit: int
    """Number of results to return per page."""

    naics: str
    """
    <details><summary>Filter by NAICS Code</summary><ul><li><span>Accepted values: <var>541511</var>, <var>541512</var>, <var>etc.</var></span></li><li>Disjunctive with <var>|</var> or <var>OR</var></li></ul></details>
    """

    ordering: str
    """
    <details><summary>Order results by a field of your choice.</summary><ul><li><span>Accepted values: <var>award_date</var>, <var>obligated</var>, <var>potential_total_value</var>, <var>recipient_name</var></span></li><li>Prefix with <var>-</var> to reverse order (e.g. <var>-award_date</var>)</li></ul></details>
    """

    page: int
    """A page number within the paginated result set."""

    psc: str
    """
    <details><summary>Filter by PSC (Product Service Code)</summary><ul><li><span>Accepted values: <var>S222</var>, <var>T005</var>, <var>etc.</var></span></li><li>Disjunctive with <var>|</var> or <var>OR</var></li></ul></details>
    """

    set_aside: str
    """
    <details><summary>Filter by set-aside type</summary><ul><li><span>Accepted values: <var>8A</var>, <var>8AN</var>, <var>BICiv</var>, <var>EDWOSB</var>, <var>EDWOSBSS</var>, <var>HUBZONE</var>, <var>HZC</var>, <var>HZS</var>, <var>IEE</var>, <var>ISBEE</var>, <var>LAS</var>, <var>NONE</var>, <var>SB</var>, <var>SBA</var>, <var>SBP</var>, <var>SDB</var>, <var>SDVOSB</var>, <var>SDVOSBC</var>, <var>SDVOSBS</var>, <var>VOSB</var>, <var>VSA</var>, <var>VSS</var>, <var>WOSB</var>, <var>WOSBSS</var></span></li><li>Disjunctive with <var>|</var> or <var>OR</var></li></ul></details>
    """

    uei: str
    """Filter by recipient UEI (Unique Entity Identifier)"""
