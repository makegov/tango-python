# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["AgencyListParams"]


class AgencyListParams(TypedDict, total=False):
    search: str
    """
    <details><summary>Filter by </summary><ul><li>Accepts any agency or department code, acronym, or (partial) name</li><li>Disjunctive with <var>|</var> or <var>OR</var></li></ul></details>
    """
