from __future__ import annotations

import datetime as dt

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from backend.db.base import Base
from backend.utils.time import now_utc


class DealAnalysis(Base):
    __tablename__ = "deal_analysis"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    deal_id: Mapped[str] = mapped_column(String(36), ForeignKey("deals.id", ondelete="CASCADE"), unique=True, index=True)

    metrics_json: Mapped[dict] = mapped_column(JSONB)
    risk_flags_json: Mapped[list] = mapped_column(JSONB)
    diligence_questions_json: Mapped[list] = mapped_column(JSONB)
    overall_triage: Mapped[str] = mapped_column(String(32))

    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
