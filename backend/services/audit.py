from __future__ import annotations

from sqlalchemy.orm import Session

from backend.models.audit_log import AuditLog
from backend.utils.time import now_utc


def audit(db: Session, *, actor: str, action: str, deal_id: str | None, metadata: dict) -> None:
    db.add(
        AuditLog(
            actor=actor,
            action=action,
            deal_id=deal_id,
            metadata_json=metadata,
            created_at=now_utc(),
        )
    )
