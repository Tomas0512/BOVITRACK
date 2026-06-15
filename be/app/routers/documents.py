"""
╔════════════════════════════════════════════════════════════════════════════╗
║ ROUTER: app/routers/documents.py                                          ║
║ PROPÓSITO: Endpoints HTTP para gestión de documentos (HU012)              ║
║                                                                            ║
║ ¿QUÉ?                                                                      ║
║   Rutas HTTP para:                                                         ║
║   - POST /farms/{farm_id}/documents - Upload archivo                      ║
║   - GET /farms/{farm_id}/documents - Listar documentos                    ║
║   - GET /farms/{farm_id}/documents/{document_id} - Descargar              ║
║   - DELETE /farms/{farm_id}/documents/{document_id} - Eliminar            ║
║                                                                            ║
║ ¿PARA QUÉ?                                                                ║
║   HU012 Tasks 12.2-12.4: Upload, download, list, delete                  ║
║                                                                            ║
║ ¿IMPACTO?                                                                 ║
║   Cada endpoint valida JWT + RBAC + pertenencia a finca                   ║
╚════════════════════════════════════════════════════════════════════════════╝
"""

import uuid

from fastapi import APIRouter, Depends, File, Form, Path, Query, Request, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.models.user import User
from app.permissions import require_permission
from app.schemas.document import (
    DocumentAssociationEnum,
    DocumentListRequest,
    DocumentListResponse,
    DocumentResponse,
    DocumentTypeEnum,
    DocumentUploadRequest,
)
from app.services import document_service
from app.utils.limiter import limiter

# ═══════════════════════════════════════════════════════════════════════════
# 🔧 CONFIGURACIÓN DEL ROUTER
# ═══════════════════════════════════════════════════════════════════════════

router = APIRouter(
    prefix="/api/v1/farms/{farm_id}/documents",
    tags=["Documentos (HU012)"],
    dependencies=[Depends(require_permission("bovines", "can_read"))],
)


# ═══════════════════════════════════════════════════════════════════════════
# 📤 UPLOAD
# ═══════════════════════════════════════════════════════════════════════════

@router.post(
    "",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Subir documento",
)
@limiter.limit("5/minute")
async def upload_document(
    request: Request,
    farm_id: uuid.UUID = Path(...),
    file: UploadFile = File(..., description="Archivo a subir (máximo 50MB)"),
    document_type: DocumentTypeEnum = Form(..., description="Tipo: pdf, image, word, excel, text"),
    association_type: DocumentAssociationEnum = Form(..., description="Asociado a: farm, bovine, etc"),
    associated_entity_id: uuid.UUID = Form(..., description="UUID de la entidad"),
    description: str | None = Form(None, max_length=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DocumentResponse:
    """
    ¿QUÉ PASA AQUÍ?

    1. Leer contenido del archivo subido
    2. Validar tamaño y tipo MIME
    3. Crear registro en BD
    4. Retornar metadatos

    ¿IMPACTO CRÍTICO?
      - Archivo se guarda en storage/documents/
      - Metadatos se almacenan en BD
      - Se registra en auditoría quién lo subió
    """

    # 1. Leer contenido del archivo
    file_content = await file.read()

    # 2. Validar tamaño
    if len(file_content) > 52428800:  # 50MB
        raise Exception("Archivo demasiado grande")

    # 3. Crear request data
    request_data = DocumentUploadRequest(
        document_type=document_type,
        file_size=len(file_content),
        mime_type=file.content_type or "application/octet-stream",
        association_type=association_type,
        associated_entity_id=associated_entity_id,
        description=description,
    )

    # 4. Crear documento (guarda archivo + BD)
    document = document_service.create_document(
        db,
        farm_id=farm_id,
        file_content=file_content,
        original_filename=file.filename or "document",
        request_data=request_data,
        user_id=current_user.id,
    )

    return DocumentResponse.model_validate(document)


# ═══════════════════════════════════════════════════════════════════════════
# 📋 LISTADO
# ═══════════════════════════════════════════════════════════════════════════

@router.get(
    "",
    response_model=DocumentListResponse,
    summary="Listar documentos",
)
@limiter.limit("20/minute")
def list_documents(
    request: Request,
    farm_id: uuid.UUID = Path(...),
    association_type: DocumentAssociationEnum | None = Query(None),
    associated_entity_id: uuid.UUID | None = Query(None),
    search: str | None = Query(None, max_length=100),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DocumentListResponse:
    """
    ¿QUÉ PASA AQUÍ?

    1. Listar documentos con filtros
    2. Buscar en nombre/descripción
    3. Paginar resultados
    4. Retornar array con total

    ¿IMPACTO?
      Solo retorna documentos activos (no eliminados)
    """

    documents, total = document_service.list_documents(
        db,
        farm_id=farm_id,
        association_type=association_type.value if association_type else None,
        associated_entity_id=associated_entity_id,
        search=search,
        skip=skip,
        limit=limit,
    )

    return DocumentListResponse(
        documents=[DocumentResponse.model_validate(d) for d in documents],
        total=total,
        page=skip // limit if limit > 0 else 0,
        page_size=limit,
    )


# ═══════════════════════════════════════════════════════════════════════════
# 📥 DESCARGA
# ═══════════════════════════════════════════════════════════════════════════

@router.get(
    "/{document_id}/download",
    summary="Descargar documento",
)
@limiter.limit("20/minute")
def download_document(
    request: Request,
    farm_id: uuid.UUID = Path(...),
    document_id: uuid.UUID = Path(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FileResponse:
    """
    ¿QUÉ PASA AQUÍ?

    1. Obtener metadatos del documento
    2. Leer archivo del filesystem
    3. Retornar con headers correctos

    ¿IMPACTO?
      Cliente descarga el archivo con nombre original
      Header: Content-Disposition: attachment; filename="..."
    """

    file_content, original_filename, mime_type = (
        document_service.get_document_for_download(db, farm_id, document_id)
    )

    return FileResponse(
        content=file_content,
        media_type=mime_type,
        filename=original_filename,
    )


# ═══════════════════════════════════════════════════════════════════════════
# 🗑️ ELIMINACIÓN
# ═══════════════════════════════════════════════════════════════════════════

@router.delete(
    "/{document_id}",
    summary="Eliminar documento",
    status_code=status.HTTP_204_NO_CONTENT,
)
@limiter.limit("5/minute")
def delete_document(
    request: Request,
    farm_id: uuid.UUID = Path(...),
    document_id: uuid.UUID = Path(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """
    ¿QUÉ PASA AQUÍ?

    1. Soft delete en BD (marca como inactivo)
    2. Elimina archivo del filesystem
    3. Registra en auditoría

    ¿IMPACTO?
      - Documento desaparece de listados
      - Archivo se elimina físicamente
      - Historial se mantiene (auditoría)
    """

    document_service.delete_document(
        db,
        farm_id=farm_id,
        document_id=document_id,
        user_id=current_user.id,
    )

    return None
