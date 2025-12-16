from __future__ import annotations

import datetime as dt

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from backend.db.base import Base
from backend.utils.time import now_utc


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    actor: Mapped[str] = mapped_column(String(256), index=True)
    action: Mapped[str] = mapped_column(String(128), index=True)

    deal_id: Mapped[str | None] = mapped_column(String(36), index=True, nullable=True)

    metadata_json: Mapped[dict] = mapped_column(JSONB)

    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
