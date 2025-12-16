from __future__ import annotations

import datetime as dt

from sqlalchemy import DateTime, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from backend.db.base import Base
from backend.utils.time import now_utc


class PromptVersion(Base):
    __tablename__ = "prompt_versions"
    __table_args__ = (
        UniqueConstraint("name", "version", name="uq_prompt_versions_name_version"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(String(128), index=True)
    version: Mapped[str] = mapped_column(String(64))
    content_hash: Mapped[str] = mapped_column(String(64), index=True)
    content: Mapped[str] = mapped_column(Text)

    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
