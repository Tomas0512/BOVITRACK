"""
Module: app/routers/documents.py
Purpose: HTTP endpoints for document management (HU012)

What?
  HTTP routes for:
  - POST /farms/{farm_id}/documents - Upload file
  - GET /farms/{farm_id}/documents - List documents
  - GET /farms/{farm_id}/documents/{document_id} - Download
  - DELETE /farms/{farm_id}/documents/{document_id} - Delete

Why?
  HU012 Tasks 12.2-12.4: Upload, download, list, delete

Impact?
  Each endpoint validates JWT + RBAC + farm ownership
"""

import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, Path, Query, Request, UploadFile, status
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
)


# ═══════════════════════════════════════════════════════════════════════════
# 📤 UPLOAD
# ═══════════════════════════════════════════════════════════════════════════

@router.post(
    "",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Subir documento",
    dependencies=[Depends(require_permission("bovinos", "can_create"))],
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
    What happens here?

    1. Read uploaded file content
    2. Validate size and MIME type
    3. Create DB record
    4. Return metadata

    Critical impact?
      - File saved in storage/documents/
      - Metadata stored in DB
      - Audit log records who uploaded it
    """

    # 1. Read file content
    file_content = await file.read()

    # 2. Validate size
    if len(file_content) > 52428800:  # 50MB
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="El archivo supera el máximo de 50MB",
        )

    # 3. Create request data
    request_data = DocumentUploadRequest(
        document_type=document_type,
        file_size=len(file_content),
        mime_type=file.content_type or "application/octet-stream",
        association_type=association_type,
        associated_entity_id=associated_entity_id,
        description=description,
    )

    # 4. Create document (save file + DB)
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
    dependencies=[Depends(require_permission("bovinos", "can_read"))],
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
    What happens here?

    1. List documents with filters
    2. Search in name/description
    3. Paginate results
    4. Return array with total

    Impact?
      Only returns active documents (not soft-deleted)
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
    dependencies=[Depends(require_permission("bovinos", "can_read"))],
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
    What happens here?

    1. Get document metadata
    2. Read file from filesystem
    3. Return with correct headers

    Impact?
      Client downloads file with original filename
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
    dependencies=[Depends(require_permission("bovinos", "can_delete"))],
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
    What happens here?

    1. Soft delete in DB (mark as inactive)
    2. Delete file from filesystem
    3. Register in audit log

    Impact?
      - Document disappears from listings
      - File is physically deleted
      - History is kept (audit log)
    """

    document_service.delete_document(
        db,
        farm_id=farm_id,
        document_id=document_id,
        user_id=current_user.id,
    )

    return None
