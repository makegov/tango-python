# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["NaicListParams"]


class NaicListParams(TypedDict, total=False):
    employee_limit: str
    """
    <details><summary>Filter by employee limit</summary><ul><li><span>Accepted values: <var>100</var>, <var>750</var>, <var>1500</var></span></li></ul></details>
    """

    employee_limit_gte: str
    """
    <details><summary>Filter by employee limit</summary><ul><li><span>Accepted values: <var>100</var>, <var>750</var>, <var>1500</var></span></li></ul></details>
    """

    employee_limit_lte: str
    """
    <details><summary>Filter by employee limit</summary><ul><li><span>Accepted values: <var>100</var>, <var>750</var>, <var>1500</var></span></li></ul></details>
    """

    revenue_limit: str
    """
    <details><summary>Filter by revenue limit</summary><ul><li><span>Accepted values: <var>20000000</var>, <var>50000000</var></span></li></ul></details>
    """

    revenue_limit_gte: str
    """
    <details><summary>Filter by revenue limit</summary><ul><li><span>Accepted values: <var>20000000</var>, <var>50000000</var></span></li></ul></details>
    """

    revenue_limit_lte: str
    """
    <details><summary>Filter by revenue limit</summary><ul><li><span>Accepted values: <var>20000000</var>, <var>50000000</var></span></li></ul></details>
    """

    search: str
    """
    <details><summary>Filter by code or description</summary><ul><li><span>Accepted values: <var>111110</var>, <var>111</var>, <var>forestry</var></span></li></ul></details>
    """

    show_limits: str
    """If included, size standards will be included in the response"""
