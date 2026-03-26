from __future__ import annotations

import json

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def add_audit_log(
    db: Session,
    *,
    user_id: str | None,
    action: str,
    entity: str,
    entity_id: str | None = None,
    details: dict | None = None,
) -> None:
    payload = json.dumps(details, ensure_ascii=False) if details else None
    row = AuditLog(
        user_id=user_id,
        action=action,
        entity=entity,
        entity_id=entity_id,
        details=payload,
    )
    db.add(row)
