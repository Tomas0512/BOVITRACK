"""
Módulo: modules/documents/repository.py
¿Qué? Acceso a datos de la tabla `document` (solo los metadatos; los bytes
      los guarda storage.py).
¿Para qué? Que el servicio pida "los documentos activos de la finca que
           coinciden con esta búsqueda" sin escribir consultas.
¿Impacto? Toda consulta filtra por farm_id y por is_active=True: un documento
          eliminado (borrado lógico) desaparece de listados y descargas.
"""

import uuid
from collections.abc import Sequence

from sqlalchemy import Select, and_, func, or_, select
from sqlalchemy.orm import Session

from app.modules.documents.models import Document


class DocumentRepository:
    """Repositorio de metadatos de documentos sobre una sesión de SQLAlchemy."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def get_active_in_farm(self, farm_id: uuid.UUID, document_id: uuid.UUID) -> Document | None:
        stmt = select(Document).where(
            Document.id == document_id,
            Document.farm_id == farm_id,
            Document.is_active.is_(True),
        )
        return self._db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def _apply_filters(
        stmt: Select,
        association_type: str | None,
        associated_entity_id: uuid.UUID | None,
        search: str | None,
    ) -> Select:
        if association_type:
            stmt = stmt.where(Document.association_type == association_type)
        if associated_entity_id:
            stmt = stmt.where(Document.associated_entity_id == associated_entity_id)
        if search:
            search_pattern = f"%{search}%"
            stmt = stmt.where(
                or_(
                    func.lower(Document.original_filename).like(func.lower(search_pattern)),
                    func.lower(Document.description or "").like(func.lower(search_pattern)),
                )
            )
        return stmt

    def list_active(
        self,
        farm_id: uuid.UUID,
        *,
        association_type: str | None = None,
        associated_entity_id: uuid.UUID | None = None,
        search: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[Sequence[Document], int]:
        """Una página de documentos activos (más recientes primero) y el total sin paginar."""
        filters = (association_type, associated_entity_id, search)
        count_stmt = select(func.count()).select_from(Document).where(
            and_(Document.farm_id == farm_id, Document.is_active.is_(True))
        )
        total = self._db.execute(self._apply_filters(count_stmt, *filters)).scalar() or 0

        stmt = select(Document).where(Document.farm_id == farm_id, Document.is_active.is_(True))
        stmt = self._apply_filters(stmt, *filters).order_by(Document.uploaded_at.desc()).offset(skip).limit(limit)
        return self._db.execute(stmt).scalars().all(), total

    def add(self, document: Document) -> None:
        self._db.add(document)

    def flush(self) -> None:
        """Envía los cambios a la BD sin confirmar (p. ej. para obtener el id)."""
        self._db.flush()

    def commit(self) -> None:
        self._db.commit()

    def rollback(self) -> None:
        self._db.rollback()

    def refresh(self, document: Document) -> None:
        self._db.refresh(document)
