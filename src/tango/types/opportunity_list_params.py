# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from datetime import datetime
from typing_extensions import Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["OpportunityListParams"]


class OpportunityListParams(TypedDict, total=False):
    active: bool
    """Filter active and inactive"""

    agency: str
    """
    <details><summary>Filter by agency</summary><ul><li>Accepts any agency or department code, acronym, or (partial) name</li><li>Disjunctive with <var>|</var> or <var>OR</var></li></ul></details>
    """

    first_notice_date_after: Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]
    """Filter by the first notice date"""

    first_notice_date_before: Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]
    """Filter by the first notice date"""

    last_notice_date_after: Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]
    """Filter by the last notice date"""

    last_notice_date_before: Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]
    """Filter by the last notice date"""

    limit: int
    """Number of results to return per page."""

    naics: str
    """
    <details><summary>Filter by NAICS Code</summary><ul><li><span>Accepted values: <var>541511</var>, <var>541512</var>, <var>etc.</var></span></li><li>Disjunctive with <var>|</var> or <var>OR</var></li></ul></details>
    """

    notice_type: str
    """
    <details><summary>Filter by notice type</summary><ul><li><span>Accepted values: <var>a</var>, <var>g</var>, <var>f</var>, <var>i</var>, <var>j</var>, <var>k</var>, <var>l</var>, <var>m</var>, <var>o</var>, <var>p</var>, <var>r</var>, <var>s</var>, <var>u</var></span></li><li>Disjunctive with <var>|</var> or <var>OR</var></li></ul></details>
    """

    ordering: str
    """
    <details><summary>Order results by a field of your choice.</summary><ul><li><span>Accepted values: <var>last_updated</var>, <var>posted_date</var>, <var>response_deadline</var></span></li><li>Prefix with <var>-</var> to reverse order (e.g. <var>-last_updated</var>)</li></ul></details>
    """

    page: int
    """A page number within the paginated result set."""

    place_of_performance: str
    """
    <details><summary>Filter by place of performance</summary><ul><li>Accepts cities, states, zip codes, and 3-character country codes</li><li>Disjunctive with <var>|</var> or <var>OR</var></li></ul></details>
    """

    posted_date_after: str
    """
    <details><summary>Filter by posted date</summary><ul><li><span>Accepted values: <var>2024-08-01</var></span></li></ul></details>
    """

    posted_date_before: str
    """
    <details><summary>Filter by posted date</summary><ul><li><span>Accepted values: <var>2024-08-01</var></span></li></ul></details>
    """

    psc: str
    """
    <details><summary>Filter by PSC (Product Service Code)</summary><ul><li><span>Accepted values: <var>S222</var>, <var>T005</var>, <var>etc.</var></span></li><li>Disjunctive with <var>|</var> or <var>OR</var></li></ul></details>
    """

    response_deadline_after: str
    """
    <details><summary>Filter by response deadline</summary><ul><li><span>Accepted values: <var>2024-08-01</var></span></li></ul></details>
    """

    response_deadline_before: str
    """
    <details><summary>Filter by response deadline</summary><ul><li><span>Accepted values: <var>2024-08-01</var></span></li></ul></details>
    """

    search: str
    """
    <details><summary>Search within a notice/opportunity's title, description, or solicitation number</summary><ul><li>Disjunctive with <var>|</var> or <var>OR</var></li><li>Conjunctive with <var>,</var> or <var>AND</var></li><li>Accepts phrases with <var>"</var></li></ul></details>
    """

    set_aside: str
    """
    <details><summary>Filter by set-aside type</summary><ul><li><span>Accepted values: <var>8A</var>, <var>8AN</var>, <var>BICiv</var>, <var>EDWOSB</var>, <var>EDWOSBSS</var>, <var>HUBZONE</var>, <var>HZC</var>, <var>HZS</var>, <var>IEE</var>, <var>ISBEE</var>, <var>LAS</var>, <var>NONE</var>, <var>SB</var>, <var>SBA</var>, <var>SBP</var>, <var>SDB</var>, <var>SDVOSB</var>, <var>SDVOSBC</var>, <var>SDVOSBS</var>, <var>VOSB</var>, <var>VSA</var>, <var>VSS</var>, <var>WOSB</var>, <var>WOSBSS</var></span></li><li>Disjunctive with <var>|</var> or <var>OR</var></li></ul></details>
    """

    solicitation_number: str
    """Search by solicitation number"""
