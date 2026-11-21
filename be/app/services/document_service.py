"""
Module: app/services/document_service.py
Purpose: Business logic for document management (HU012)

What?
  Functions for:
  - Save files to filesystem
  - Create DB records
  - List/search documents
  - Download documents
  - Delete documents (soft delete)
  - Validate file types

Why?
  HU012 Tasks 12.1-12.3: Upload, list, download, delete, association

Impact?
  Everything goes to storage/ (local filesystem)
  Metadata stored in DB for traceability
"""

import io
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence

from fastapi import HTTPException, status
from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.bovine import Bovine
from app.schemas.document import DocumentUploadRequest, MAX_DOCUMENT_SIZE
from app.services.audit_service import add_audit_log


# ── Storage configuration ─────────────────────────────────

# Document storage directory
STORAGE_DIR = Path("storage/documents")

# Create directory if it doesn't exist
STORAGE_DIR.mkdir(parents=True, exist_ok=True)


def sanitize_original_filename(filename: str | None) -> str:
    """Strip path components and control characters from client-provided names."""
    candidate = (filename or "document").replace("\\", "/").split("/")[-1]
    candidate = "".join(char for char in candidate if char.isprintable()).strip(" .")
    return (candidate or "document")[:255]


def detect_mime_type(file_content: bytes, declared_mime: str = "") -> str:
    """Identify supported formats from their content, not from the HTTP header."""
    if len(file_content) > MAX_DOCUMENT_SIZE or not file_content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tamaño de archivo no permitido",
        )

    if file_content.startswith(b"%PDF-"):
        return "application/pdf"
    if file_content.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if file_content.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if file_content.startswith((b"GIF87a", b"GIF89a")):
        return "image/gif"

    if file_content.startswith(b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"):
        legacy_mime = declared_mime.split(";", 1)[0].strip().lower()
        if legacy_mime in {"application/msword", "application/vnd.ms-excel"}:
            return legacy_mime
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se pudo determinar si el archivo Office es Word o Excel",
        )

    if zipfile.is_zipfile(io.BytesIO(file_content)):
        try:
            with zipfile.ZipFile(io.BytesIO(file_content)) as archive:
                entries = archive.infolist()
                names = {entry.filename for entry in entries}
                uncompressed_size = sum(entry.file_size for entry in entries)
                if len(entries) > 1000 or uncompressed_size > 100 * 1024 * 1024:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="El paquete Office tiene una estructura no permitida",
                    )
                if "word/document.xml" in names and "[Content_Types].xml" in names:
                    if any(name.endswith("vbaProject.bin") for name in names):
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="No se permiten documentos Office con macros",
                        )
                    return (
                        "application/vnd.openxmlformats-officedocument."
                        "wordprocessingml.document"
                    )
                if "xl/workbook.xml" in names and "[Content_Types].xml" in names:
                    if any(name.endswith("vbaProject.bin") for name in names):
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="No se permiten documentos Office con macros",
                        )
                    return (
                        "application/vnd.openxmlformats-officedocument."
                        "spreadsheetml.sheet"
                    )
        except zipfile.BadZipFile:
            pass

    try:
        decoded = file_content.decode("utf-8-sig")
    except UnicodeDecodeError:
        decoded = ""
    if decoded and all(
        character.isprintable() or character in "\t\n\r\f" for character in decoded
    ):
        if declared_mime.split(";", 1)[0].strip().lower() == "text/csv":
            return "text/csv"
        return "text/plain"

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Formato de archivo no permitido o contenido no reconocido",
    )


def validate_file_extension(filename: str, mime_type: str) -> None:
    """Reject misleading names whose suffix contradicts the detected content."""
    allowed_extensions = {
        "application/pdf": {".pdf"},
        "image/jpeg": {".jpg", ".jpeg"},
        "image/png": {".png"},
        "image/gif": {".gif"},
        "application/msword": {".doc"},
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": {
            ".docx"
        },
        "application/vnd.ms-excel": {".xls"},
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": {
            ".xlsx"
        },
        "text/plain": {".txt"},
        "text/csv": {".csv"},
    }
    if Path(filename).suffix.lower() not in allowed_extensions.get(mime_type, set()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La extensión del archivo no coincide con su contenido",
        )


def get_file_extension(mime_type: str) -> str:
    """
    What? Gets file extension from MIME type.
    Why? Save files with correct extension.
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


# ── Storage functions ────────────────────────────────────

def save_document_file(file_content: bytes, mime_type: str) -> str:
    """
    What? Saves file content to the filesystem.

    Why?
      - HU012 Task 12.1: Document storage
      - Keep files separate from DB

    Params?
      file_content: File bytes
      mime_type: MIME type to determine extension

    Returns?
      stored_filename: Sanitized name for later retrieval

    Impact?
      CRITICAL: Saves in storage/documents/{timestamp}_{uuid}.{ext}
      Uses UUID to avoid name collisions
    """

    # Generate sanitized filename
    # Format: {uuid}_{timestamp}.{ext}
    document_id = uuid.uuid4()
    timestamp = int(datetime.now(timezone.utc).timestamp())
    extension = get_file_extension(mime_type)
    stored_filename = f"{document_id}_{timestamp}.{extension}"

    # Full file path
    file_path = STORAGE_DIR / stored_filename

    # Save the file
    try:
        with open(file_path, "wb") as f:
            f.write(file_content)
    except IOError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving file: {str(e)}"
        )

    return stored_filename


def retrieve_document_file(stored_filename: str) -> bytes:
    """
    What? Retrieves file content from the filesystem.

    Why?
      - HU012 Task 12.2: Document download
      - Return file to client

    Params?
      stored_filename: Sanitized name (from DB)

    Returns?
      bytes: File content

    Impact?
      Raises 404 if file doesn't exist
    """

    file_path = STORAGE_DIR / stored_filename

    # Validate the file exists
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )

    # Read the file
    try:
        with open(file_path, "rb") as f:
            return f.read()
    except IOError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error reading file: {str(e)}"
        )


def delete_document_file(stored_filename: str) -> None:
    """
    What? Physically deletes the file from filesystem.

    Why?
      - Clean up files when documents are deleted
      - Free up disk space

    Impact?
      Deletes file physically (not soft delete)
      Done AFTER soft delete in DB
    """

    file_path = STORAGE_DIR / stored_filename

    if file_path.exists():
        try:
            file_path.unlink()  # Delete file
        except OSError as e:
            # Log but don't fail - already marked as deleted in DB
            print(f"Error deleting physical file: {str(e)}")


# ── Database functions ───────────────────────────────────

def create_document(
    db: Session,
    farm_id: uuid.UUID,
    file_content: bytes,
    original_filename: str,
    request_data: DocumentUploadRequest,
    user_id: uuid.UUID,
) -> Document:
    """
    What? Creates a document (save file + metadata in DB).

    Why?
      - HU012 Task 12.1: Create document record
      - HU012 Task 12.3: Associate to entity

    Steps?
      1. Save file to filesystem
      2. Create DB record
      3. Register in audit log

    Impact?
      If file save fails, DB stays consistent
      because save happens FIRST, register AFTER
    """

    # ¿Qué? Validar que la entidad asociada pertenezca a la finca.
    association_type = request_data.association_type.value
    entity_id = request_data.associated_entity_id
    if association_type == "farm":
        if entity_id != farm_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La finca asociada no coincide",
            )
    elif association_type == "bovine":
        bovine = db.execute(
            select(Bovine.id).where(Bovine.id == entity_id, Bovine.farm_id == farm_id)
        ).scalar_one_or_none()
        if not bovine:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El bovino asociado no existe en esta finca",
            )

    # 1. Save file to filesystem
    detected_mime = detect_mime_type(file_content, request_data.mime_type)
    if detected_mime != request_data.mime_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El MIME registrado no coincide con el contenido del archivo",
        )
    original_filename = sanitize_original_filename(original_filename)
    validate_file_extension(original_filename, detected_mime)
    stored_filename = save_document_file(file_content, detected_mime)

    # 2. Create document in DB
    document = Document(
        farm_id=farm_id,
        original_filename=original_filename,
        stored_filename=stored_filename,
        file_size=request_data.file_size,
        mime_type=detected_mime,
        document_type=request_data.document_type.value,
        association_type=request_data.association_type.value,
        associated_entity_id=request_data.associated_entity_id,
        description=request_data.description,
        uploaded_by=user_id,
    )

    try:
        db.add(document)
        db.flush()  # Obtener el ID sin confirmar la transacción.

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
    except Exception:
        db.rollback()
        delete_document_file(stored_filename)
        raise

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
    What? Lists documents for a farm with filters.

    Why?
      - HU012 Task 12.4: Document repository
      - Allow search and filtering

    Params?
      association_type: Filter by type (farm, bovine, etc)
      associated_entity_id: Filter by specific entity
      search: Search in name or description

    Returns?
      (documents, total_count)

    Impact?
      Only returns active documents (is_active=True)
    """

    # Base query: only active documents
    stmt = select(Document).where(
        Document.farm_id == farm_id,
        Document.is_active.is_(True),
    )

    # Optional filters
    if association_type:
        stmt = stmt.where(Document.association_type == association_type)

    if associated_entity_id:
        stmt = stmt.where(Document.associated_entity_id == associated_entity_id)

    if search:
        # Search in name or description (case-insensitive)
        search_pattern = f"%{search}%"
        stmt = stmt.where(
            or_(
                func.lower(Document.original_filename).like(func.lower(search_pattern)),
                func.lower(Document.description or "").like(func.lower(search_pattern)),
            )
        )

    # Count total
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

    # Sorting and pagination
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
    What? Gets a specific document.

    Why?
      - Validate it exists before download
      - Verify it belongs to the farm (multitenancy)

    Returns?
      Document

    Impact?
      Raises 404 if not found
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
            detail="Document not found"
        )

    return document


def delete_document(
    db: Session,
    farm_id: uuid.UUID,
    document_id: uuid.UUID,
    user_id: uuid.UUID,
) -> Document:
    """
    What? Soft delete a document.

    Why?
      - HU012 Task 12.2: Delete endpoint
      - Keep audit trail (doesn't delete from DB)
      - Deletes file from filesystem

    Steps?
      1. Mark as inactive in DB
      2. Delete physical file
      3. Register in audit log

    Impact?
      Document disappears from lists (is_active=False)
      File is deleted from filesystem
      History is kept for audit
    """

    # 1. Get document
    document = get_document(db, farm_id, document_id)

    # 2. Mark as deleted in DB
    document.is_active = False
    document.deleted_at = datetime.now(timezone.utc)
    document.deleted_by = user_id

    # 3. Delete physical file
    delete_document_file(document.stored_filename)

    # 4. Register in audit log
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
    What? Gets file + metadata for download.

    Why?
      - HU012 Task 12.2: Download endpoint
      - Return file with correct headers

    Returns?
      (file_content, original_filename, mime_type)

    Impact?
      Client receives file with original name
    """

    # Get metadata
    document = get_document(db, farm_id, document_id)

    # Get file content
    file_content = retrieve_document_file(document.stored_filename)

    return file_content, document.original_filename, document.mime_type
