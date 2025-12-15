from __future__ import annotations

import datetime as dt

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from backend.db.base import Base
from backend.utils.time import now_utc


class DealTerms(Base):
    __tablename__ = "deal_terms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    deal_id: Mapped[str] = mapped_column(String(36), ForeignKey("deals.id", ondelete="CASCADE"), unique=True, index=True)

    terms_json: Mapped[dict] = mapped_column(JSONB)
    citations_json: Mapped[dict] = mapped_column(JSONB)

    # { field_name: true/false } – used to gate drafting
    confirmed_fields_json: Mapped[dict] = mapped_column(JSONB, default=dict)

    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    updated_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
