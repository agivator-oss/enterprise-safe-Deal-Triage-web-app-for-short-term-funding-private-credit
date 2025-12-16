from __future__ import annotations

import datetime as dt
import uuid

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.db.base import Base
from backend.utils.time import now_utc


class Deal(Base):
    __tablename__ = "deals"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(255))

    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
