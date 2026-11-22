"""
Módulo: core/audit_trail.py (rastro de auditoría: infraestructura transversal)
¿Qué? La tabla `audit_log` y la función add_audit_log, que deja constancia de
      quién hizo qué, sobre qué entidad y en qué finca.
¿Para qué? Que CUALQUIER módulo pueda auditar sus acciones sin depender de otro
           módulo, igual que usa el logging. Es la implementación del puerto
           AuditRecorder (app.shared.ports).
¿Impacto? Solo ESCRIBE. Consultar, filtrar y exportar la auditoría (HU015) es una
          funcionalidad de negocio y vive en el módulo app.modules.audit.
          add_audit_log hace db.add (no commit): el registro se guarda en la
          misma transacción que la acción auditada, o no se guarda.
"""

import json
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, Session, mapped_column

from app.core.database import Base

class AuditLog(Base):
    __tablename__ = "audit_log"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    farm_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("farm.id", ondelete="SET NULL"), nullable=True, index=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    entity: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    details: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


def add_audit_log(
    db: Session,
    *,
    user_id: str | None,
    action: str,
    entity: str,
    entity_id: str | None = None,
    farm_id: str | None = None,
    details: dict[str, Any] | None = None,
) -> None:
    """Agrega un registro de auditoría a la transacción en curso (no hace commit)."""
    payload = json.dumps(details, ensure_ascii=False) if details else None
    db.add(
        AuditLog(
            user_id=user_id,
            farm_id=farm_id,
            action=action,
            entity=entity,
            entity_id=entity_id,
            details=payload,
        )
    )
