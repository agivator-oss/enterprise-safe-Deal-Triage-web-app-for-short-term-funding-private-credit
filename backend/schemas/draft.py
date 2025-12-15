from __future__ import annotations

from pydantic import Field

from backend.schemas.common import BaseSchema


class ICDraft(BaseSchema):
    banner: str = "Decision support only. Not investment advice."

    ic_summary_3_lines: str
    top_risks_ranked: list[str] = Field(default_factory=list, max_length=5)
    mitigants_or_conditions: list[str] = Field(default_factory=list, max_length=8)
    diligence_questions: list[str] = Field(default_factory=list)
    what_changes_my_mind: str
