from __future__ import annotations

from pydantic import Field

from backend.schemas.common import BaseSchema


class RiskFlag(BaseSchema):
    rule_id: str
    severity: str  # HARD_STOP | HIGH | MED | LOW
    message: str


class AnalysisResponse(BaseSchema):
    metrics: dict[str, float | None] = Field(default_factory=dict)
    overall_triage: str
    risk_flags: list[RiskFlag] = Field(default_factory=list)
    diligence_questions: list[str] = Field(default_factory=list)
