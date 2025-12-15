from __future__ import annotations

from typing import Any

from pydantic import Field

from backend.schemas.common import BaseSchema, LienPosition


class Fee(BaseSchema):
    type: str
    pct_or_amount: str


class ExtractedTerms(BaseSchema):
    loan_amount: float | None = None
    currency: str = "AUD"
    term_months: int | None = None
    interest_rate_pct: float | None = None

    fees: list[Fee] = Field(default_factory=list)

    collateral_type: str
    collateral_value_appraised: float | None = None
    collateral_value_as_is: float | None = None
    collateral_value_stressed: float | None = None

    lien_position: LienPosition = LienPosition.unknown

    jurisdiction: str | None = None
    enforcement_timeline_months: int | None = None

    repayment_source: str | None = None
    repayment_timeline_months: int | None = None

    key_conditions: list[str] = Field(default_factory=list)
    notes: str | None = None

    # Each extracted field -> list of short supporting snippets (<=200 chars). If unknown: null.
    citations: dict[str, list[str] | None] = Field(default_factory=dict)


class TermsUpdate(BaseSchema):
    terms: ExtractedTerms
    confirmed_fields: dict[str, bool] = Field(default_factory=dict)
