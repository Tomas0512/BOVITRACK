"""
Módulo: modules/documents/dependencies.py (composición del módulo)
¿Qué? Arma un DocumentService por request: repositorio, almacenamiento en disco,
      búsqueda de bovinos (ganado) y auditoría.
¿Para qué? Decidir AQUÍ, y solo aquí, qué implementación concreta se usa:
           cambiar a almacenamiento en la nube es cambiar una línea de este archivo.
¿Impacto? Cuando ganado y auditoría migren (Partes 3d y 3e), solo cambian esos imports.
"""

from functools import partial

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.modules import livestock
from app.modules.documents.repository import DocumentRepository
from app.modules.documents.service import DocumentService
from app.modules.documents.storage import LocalDocumentStorage

# Rastro de auditoría: infraestructura de core (no es otro módulo).
from app.core.audit_trail import add_audit_log

# Guards de identity (su API pública). Los routers de este módulo los importan
# desde aquí, para que solo este archivo conozca a otro módulo.
from app.modules.identity import get_current_user as get_current_user
from app.modules.identity import require_permission as require_permission


def get_document_storage() -> LocalDocumentStorage:
    """El almacenamiento activo. Se puede reemplazar en pruebas con dependency_overrides."""
    return LocalDocumentStorage(settings.DOCUMENTS_STORAGE_DIR)


def get_document_service(
    db: Session = Depends(get_db),
    storage: LocalDocumentStorage = Depends(get_document_storage),
) -> DocumentService:
    """Dependencia de FastAPI: un DocumentService por request."""
    return DocumentService(
        repository=DocumentRepository(db),
        storage=storage,
        find_bovine=livestock.build_bovine_lookup(db),
        record_audit=partial(add_audit_log, db),
    )
