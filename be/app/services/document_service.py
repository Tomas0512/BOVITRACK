"""
╔════════════════════════════════════════════════════════════════════════════╗
║ SERVICIO: app/services/document_service.py                                ║
║ PROPÓSITO: Lógica de negocio para gestión de documentos (HU012)           ║
║                                                                            ║
║ ¿QUÉ?                                                                      ║
║   Funciones para:                                                          ║
║   - Guardar archivos en filesystem                                         ║
║   - Crear registros en BD                                                  ║
║   - Listar/buscar documentos                                              ║
║   - Descargar documentos                                                   ║
║   - Eliminar documentos (soft delete)                                     ║
║   - Validar tipos de archivo                                              ║
║                                                                            ║
║ ¿PARA QUÉ?                                                                ║
║   HU012 Tasks 12.1-12.3: Upload, list, download, delete, asociación      ║
║                                                                            ║
║ ¿IMPACTO?                                                                 ║
║   Todo sube a storage/ (filesystem local)                                 ║
║   Metadatos se guardan en BD para trazabilidad                            ║
╚════════════════════════════════════════════════════════════════════════════╝
"""

import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence

from fastapi import HTTPException, status
from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session

from app.models.document import Document
from app.schemas.document import DocumentUploadRequest
from app.services.audit_service import add_audit_log


# ═══════════════════════════════════════════════════════════════════════════
# 🔧 CONFIGURACIÓN DE ALMACENAMIENTO
# ═══════════════════════════════════════════════════════════════════════════

# Directorio de almacenamiento de documentos
STORAGE_DIR = Path("storage/documents")

# Crear directorio si no existe
STORAGE_DIR.mkdir(parents=True, exist_ok=True)


def get_file_extension(mime_type: str) -> str:
    """
    ¿Qué? Obtiene la extensión desde el MIME type.
    ¿Para qué? Guardar archivos con extensión correcta.
    """
    mime_to_ext = {
        "application/pdf": "pdf",
        "image/jpeg": "jpg",
        "image/png": "png",
        "image/gif": "gif",
        "application/msword": "doc",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
        "application/vnd.ms-excel": "xls",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "xlsx",
        "text/plain": "txt",
        "text/csv": "csv",
    }
    return mime_to_ext.get(mime_type, "bin")


# ═══════════════════════════════════════════════════════════════════════════
# 💾 FUNCIONES DE ALMACENAMIENTO
# ═══════════════════════════════════════════════════════════════════════════

def save_document_file(file_content: bytes, mime_type: str) -> str:
    """
    ¿Qué? Guarda el contenido del archivo en el filesystem.

    ¿Para qué?
      - HU012 Task 12.1: Almacenamiento de documentos
      - Mantener archivos separados de la BD

    ¿Parámetros?
      file_content: Bytes del archivo
      mime_type: Tipo MIME para determinar extensión

    ¿Retorna?
      stored_filename: Nombre sanitizado para recuperar después

    ¿Impacto?
      CRÍTICO: Almacena en storage/documents/{timestamp}_{uuid}.{ext}
      Usa UUID para evitar colisiones de nombres
    """

    # Generar nombre sanitizado
    # Formato: {uuid}_{timestamp}.{ext}
    document_id = uuid.uuid4()
    timestamp = int(datetime.now(timezone.utc).timestamp())
    extension = get_file_extension(mime_type)
    stored_filename = f"{document_id}_{timestamp}.{extension}"

    # Ruta completa del archivo
    file_path = STORAGE_DIR / stored_filename

    # Guardar el archivo
    try:
        with open(file_path, "wb") as f:
            f.write(file_content)
    except IOError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al guardar archivo: {str(e)}"
        )

    return stored_filename


def retrieve_document_file(stored_filename: str) -> bytes:
    """
    ¿Qué? Recupera el contenido del archivo del filesystem.

    ¿Para qué?
      - HU012 Task 12.2: Download de documentos
      - Retornar archivo al cliente

    ¿Parámetros?
      stored_filename: Nombre sanitizado (de BD)

    ¿Retorna?
      bytes: Contenido del archivo

    ¿Impacto?
      Lanza 404 si archivo no existe
    """

    file_path = STORAGE_DIR / stored_filename

    # Validar que el archivo existe
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Archivo no encontrado"
        )

    # Leer el archivo
    try:
        with open(file_path, "rb") as f:
            return f.read()
    except IOError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al leer archivo: {str(e)}"
        )


def delete_document_file(stored_filename: str) -> None:
    """
    ¿Qué? Elimina físicamente el archivo del filesystem.

    ¿Para qué?
      - Limpiar archivos cuando se eliminan documentos
      - Liberar espacio en disco

    ¿Impacto?
      Elimina archivo físicamente (no es soft delete)
      Se hace DESPUÉS de soft delete en BD
    """

    file_path = STORAGE_DIR / stored_filename

    if file_path.exists():
        try:
            file_path.unlink()  # Eliminar archivo
        except OSError as e:
            # Log pero no fallar - ya está en BD como deleted
            print(f"Error al eliminar archivo físico: {str(e)}")


# ═══════════════════════════════════════════════════════════════════════════
# 📝 FUNCIONES DE BASE DE DATOS
# ═══════════════════════════════════════════════════════════════════════════

def create_document(
    db: Session,
    farm_id: uuid.UUID,
    file_content: bytes,
    original_filename: str,
    request_data: DocumentUploadRequest,
    user_id: uuid.UUID,
) -> Document:
    """
    ¿Qué? Crea un documento (guarda archivo + metadatos en BD).

    ¿Para qué?
      - HU012 Task 12.1: Crear registro de documento
      - HU012 Task 12.3: Asociar a entidad

    ¿Pasos?
      1. Guardar archivo en filesystem
      2. Crear registro en BD
      3. Registrar en auditoría

    ¿Impacto?
      Si falla el guardado del archivo, la BD queda consistente
      porque se guarda PRIMERO, registra DESPUÉS
    """

    # 1. Guardar archivo en filesystem
    stored_filename = save_document_file(file_content, request_data.mime_type)

    # 2. Crear documento en BD
    document = Document(
        farm_id=farm_id,
        original_filename=original_filename,
        stored_filename=stored_filename,
        file_size=request_data.file_size,
        mime_type=request_data.mime_type,
        document_type=request_data.document_type.value,
        association_type=request_data.association_type.value,
        associated_entity_id=request_data.associated_entity_id,
        description=request_data.description,
        uploaded_by=user_id,
    )

    db.add(document)
    db.flush()  # Obtener el ID

    # 3. Registrar en auditoría
    add_audit_log(
        db,
        user_id=str(user_id),
        farm_id=str(farm_id),
        action="create",
        entity="document",
        entity_id=str(document.id),
        details={
            "filename": original_filename,
            "size": request_data.file_size,
            "type": request_data.document_type.value,
            "associated_to": f"{request_data.association_type.value}:{request_data.associated_entity_id}",
        },
    )

    db.commit()
    db.refresh(document)

    return document


def list_documents(
    db: Session,
    farm_id: uuid.UUID,
    *,
    association_type: str | None = None,
    associated_entity_id: uuid.UUID | None = None,
    search: str | None = None,
    skip: int = 0,
    limit: int = 50,
) -> tuple[Sequence[Document], int]:
    """
    ¿Qué? Lista documentos de una finca con filtros.

    ¿Para qué?
      - HU012 Task 12.4: Repositorio documental
      - Permitir búsqueda y filtrado

    ¿Parámetros?
      association_type: Filtro por tipo (farm, bovine, etc)
      associated_entity_id: Filtro por entidad específica
      search: Búsqueda en nombre o descripción

    ¿Retorna?
      (documentos, total_count)

    ¿Impacto?
      Solo retorna documentos activos (is_active=True)
    """

    # Query base: solo documentos activos
    stmt = select(Document).where(
        Document.farm_id == farm_id,
        Document.is_active.is_(True),
    )

    # Filtros opcionales
    if association_type:
        stmt = stmt.where(Document.association_type == association_type)

    if associated_entity_id:
        stmt = stmt.where(Document.associated_entity_id == associated_entity_id)

    if search:
        # Búsqueda en nombre o descripción (case-insensitive)
        search_pattern = f"%{search}%"
        stmt = stmt.where(
            or_(
                func.lower(Document.original_filename).like(func.lower(search_pattern)),
                func.lower(Document.description or "").like(func.lower(search_pattern)),
            )
        )

    # Contar total
    count_stmt = select(func.count()).select_from(Document).where(
        and_(
            Document.farm_id == farm_id,
            Document.is_active.is_(True),
        )
    )
    if association_type:
        count_stmt = count_stmt.where(Document.association_type == association_type)
    if associated_entity_id:
        count_stmt = count_stmt.where(Document.associated_entity_id == associated_entity_id)
    if search:
        search_pattern = f"%{search}%"
        count_stmt = count_stmt.where(
            or_(
                func.lower(Document.original_filename).like(func.lower(search_pattern)),
                func.lower(Document.description or "").like(func.lower(search_pattern)),
            )
        )

    total = db.execute(count_stmt).scalar() or 0

    # Ordenamiento y paginación
    stmt = stmt.order_by(Document.uploaded_at.desc())
    stmt = stmt.offset(skip).limit(limit)

    documents = db.execute(stmt).scalars().all()

    return documents, total


def get_document(
    db: Session,
    farm_id: uuid.UUID,
    document_id: uuid.UUID,
) -> Document:
    """
    ¿Qué? Obtiene un documento específico.

    ¿Para qué?
      - Validar que existe antes de descargar
      - Verificar que pertenece a la finca (multitenancy)

    ¿Retorna?
      Document

    ¿Impacto?
      Lanza 404 si no existe
    """

    stmt = select(Document).where(
        Document.id == document_id,
        Document.farm_id == farm_id,
        Document.is_active.is_(True),
    )

    document = db.execute(stmt).scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Documento no encontrado"
        )

    return document


def delete_document(
    db: Session,
    farm_id: uuid.UUID,
    document_id: uuid.UUID,
    user_id: uuid.UUID,
) -> Document:
    """
    ¿Qué? Soft delete de un documento.

    ¿Para qué?
      - HU012 Task 12.2: Delete endpoint
      - Mantener auditoría (no elimina BD)
      - Elimina archivo del filesystem

    ¿Pasos?
      1. Marcar como inactivo en BD
      2. Eliminar archivo físico
      3. Registrar en auditoría

    ¿Impacto?
      Documento desaparece de listados (is_active=False)
      Archivo se elimina del filesystem
      Historial se mantiene para auditoría
    """

    # 1. Obtener documento
    document = get_document(db, farm_id, document_id)

    # 2. Marcar como eliminado en BD
    document.is_active = False
    document.deleted_at = datetime.now(timezone.utc)
    document.deleted_by = user_id

    # 3. Eliminar archivo físico
    delete_document_file(document.stored_filename)

    # 4. Registrar en auditoría
    add_audit_log(
        db,
        user_id=str(user_id),
        farm_id=str(farm_id),
        action="delete",
        entity="document",
        entity_id=str(document.id),
        details={"filename": document.original_filename},
    )

    db.commit()
    db.refresh(document)

    return document


def get_document_for_download(
    db: Session,
    farm_id: uuid.UUID,
    document_id: uuid.UUID,
) -> tuple[bytes, str, str]:
    """
    ¿Qué? Obtiene el archivo + metadatos para descargar.

    ¿Para qué?
      - HU012 Task 12.2: Download endpoint
      - Retornar archivo con headers correctos

    ¿Retorna?
      (file_content, original_filename, mime_type)

    ¿Impacto?
      El cliente recibe el archivo con nombre original
    """

    # Obtener metadatos
    document = get_document(db, farm_id, document_id)

    # Obtener contenido del archivo
    file_content = retrieve_document_file(document.stored_filename)

    return file_content, document.original_filename, document.mime_type
