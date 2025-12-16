from __future__ import annotations

import datetime as dt

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from backend.db.base import Base
from backend.utils.time import now_utc


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    deal_id: Mapped[str] = mapped_column(String(36), ForeignKey("deals.id", ondelete="CASCADE"), index=True)
    filename: Mapped[str] = mapped_column(String(512))
    content_type: Mapped[str | None] = mapped_column(String(128), nullable=True)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    storage_path: Mapped[str] = mapped_column(String(1024))
    sha256: Mapped[str] = mapped_column(String(64), index=True)

    # NOTE: MVP stores extracted text. TODO: encrypt at rest.
    extracted_text: Mapped[str] = mapped_column(Text)

    metadata_json: Mapped[dict] = mapped_column(JSONB, default=dict)

    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
