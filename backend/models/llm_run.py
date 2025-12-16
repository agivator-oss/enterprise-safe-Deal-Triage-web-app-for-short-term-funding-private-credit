from __future__ import annotations

import datetime as dt

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from backend.db.base import Base
from backend.utils.time import now_utc


class LLMRun(Base):
    __tablename__ = "llm_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    deal_id: Mapped[str] = mapped_column(String(36), ForeignKey("deals.id", ondelete="CASCADE"), index=True)

    prompt_name: Mapped[str] = mapped_column(String(128))
    prompt_version: Mapped[str] = mapped_column(String(64))

    model: Mapped[str] = mapped_column(String(128))
    temperature: Mapped[float] = mapped_column(Float)

    input_hash: Mapped[str] = mapped_column(String(64), index=True)
    output_json: Mapped[dict] = mapped_column(JSONB)

    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
