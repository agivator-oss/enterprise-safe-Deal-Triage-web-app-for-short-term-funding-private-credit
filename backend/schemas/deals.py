from __future__ import annotations

from pydantic import Field

from backend.schemas.common import BaseSchema


class DealCreate(BaseSchema):
    name: str = Field(min_length=1, max_length=255)


class DealOut(BaseSchema):
    id: str
    name: str
    created_at: str


class DocumentOut(BaseSchema):
    id: int
    deal_id: str
    filename: str
    sha256: str
    created_at: str
