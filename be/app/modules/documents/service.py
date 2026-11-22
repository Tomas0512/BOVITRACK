"""
Módulo: modules/documents/service.py
¿Qué? Casos de uso de la gestión documental (HU012): subir, listar, buscar,
      descargar y eliminar documentos asociados a la finca o a un bovino.
¿Para qué? Guardar la evidencia de la finca (certificados, facturas, registros
           sanitarios) de forma segura y trazable.
¿Impacto? Garantiza que:
          - solo se aceptan formatos permitidos, verificados por su contenido
            (file_rules.py), nunca por lo que declara el cliente;
          - el documento se asocia a esta finca o a un bovino de esta finca;
          - si falla la BD después de guardar el archivo, el archivo se borra
            (no quedan huérfanos en disco);
          - eliminar es lógico: el registro se conserva para la auditoría.
          No conoce HTTP, SQLAlchemy ni el disco: usa el repositorio y un
          DocumentStorage inyectado.
"""

import uuid
from collections.abc import Sequence
from datetime import datetime, timezone
from typing import Protocol

from app.modules.documents.file_rules import (
    detect_mime_type,
    ensure_mime_matches_document_type,
    get_file_extension,
    sanitize_original_filename,
    validate_file_extension,
)
from app.modules.documents.models import Document
from app.modules.documents.repository import DocumentRepository
from app.modules.documents.schemas import (
    DocumentAssociationEnum,
    DocumentTypeEnum,
    DocumentUploadRequest,
)
from app.shared.exceptions import BusinessRuleError, NotFoundError
from app.shared.ports import AuditRecorder, BovineLookup

DOCUMENT_NOT_FOUND = "Document not found"
EMPTY_FILE = "El archivo está vacío"
FARM_MISMATCH = "La finca asociada no coincide"
BOVINE_NOT_IN_FARM = "El bovino asociado no existe en esta finca"
MIME_MISMATCH = "El MIME registrado no coincide con el contenido del archivo"


class DocumentStorage(Protocol):
    """Dónde se guardan los bytes. Implementación actual: storage.LocalDocumentStorage."""

    def save(self, content: bytes, extension: str) -> str: ...

    def read(self, stored_filename: str) -> bytes: ...

    def delete(self, stored_filename: str) -> None: ...


class DocumentService:
    """Casos de uso del módulo de documentos."""

    def __init__(
        self,
        repository: DocumentRepository,
        storage: DocumentStorage,
        find_bovine: BovineLookup,
        record_audit: AuditRecorder,
    ) -> None:
        self._repo = repository
        self._storage = storage
        self._find_bovine = find_bovine
        self._record_audit = record_audit

    def upload_document(
        self,
        farm_id: uuid.UUID,
        *,
        file_content: bytes,
        declared_mime: str,
        filename: str | None,
        document_type: DocumentTypeEnum,
        association_type: DocumentAssociationEnum,
        associated_entity_id: uuid.UUID,
        description: str | None,
        user_id: uuid.UUID,
    ) -> Document:
        """Valida el archivo recibido y lo registra.

        Orden de validación (igual que antes del refactor): vacío -> formato real
        -> tipo declarado -> extensión -> asociación a la finca.
        """
        if not file_content:
            raise BusinessRuleError(EMPTY_FILE)
        detected_mime = detect_mime_type(file_content, declared_mime)
        ensure_mime_matches_document_type(detected_mime, document_type.value)
        original_filename = sanitize_original_filename(filename)
        validate_file_extension(original_filename, detected_mime)

        request_data = DocumentUploadRequest(
            document_type=document_type,
            file_size=len(file_content),
            mime_type=detected_mime,
            association_type=association_type,
            associated_entity_id=associated_entity_id,
            description=description,
        )
        return self.create_document(farm_id, file_content, original_filename, request_data, user_id)

    def create_document(
        self,
        farm_id: uuid.UUID,
        file_content: bytes,
        original_filename: str,
        request_data: DocumentUploadRequest,
        user_id: uuid.UUID,
    ) -> Document:
        """Guarda el archivo y luego su registro; si la BD falla, borra el archivo."""
        association_type = request_data.association_type.value
        entity_id = request_data.associated_entity_id
        if association_type == "farm":
            if entity_id != farm_id:
                raise BusinessRuleError(FARM_MISMATCH)
        elif association_type == "bovine":
            if self._find_bovine(farm_id, entity_id) is None:
                raise BusinessRuleError(BOVINE_NOT_IN_FARM)

        detected_mime = detect_mime_type(file_content, request_data.mime_type)
        if detected_mime != request_data.mime_type:
            raise BusinessRuleError(MIME_MISMATCH)
        original_filename = sanitize_original_filename(original_filename)
        validate_file_extension(original_filename, detected_mime)
        stored_filename = self._storage.save(file_content, get_file_extension(detected_mime))

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
            self._repo.add(document)
            self._repo.flush()
            self._record_audit(
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
            self._repo.commit()
            self._repo.refresh(document)
        except Exception:
            self._repo.rollback()
            self._storage.delete(stored_filename)
            raise
        return document

    def list_documents(
        self,
        farm_id: uuid.UUID,
        *,
        association_type: str | None = None,
        associated_entity_id: uuid.UUID | None = None,
        search: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[Sequence[Document], int]:
        """Página de documentos activos y total, con filtros y búsqueda por nombre o descripción."""
        return self._repo.list_active(
            farm_id,
            association_type=association_type,
            associated_entity_id=associated_entity_id,
            search=search,
            skip=skip,
            limit=limit,
        )

    def get_document(self, farm_id: uuid.UUID, document_id: uuid.UUID) -> Document:
        document = self._repo.get_active_in_farm(farm_id, document_id)
        if document is None:
            raise NotFoundError(DOCUMENT_NOT_FOUND)
        return document

    def delete_document(self, farm_id: uuid.UUID, document_id: uuid.UUID, user_id: uuid.UUID) -> Document:
        """Borrado lógico en BD + auditoría, y DESPUÉS el borrado físico del archivo.

        El orden importa: si el commit falla, el documento sigue activo y su
        archivo intacto. (Antes el archivo se borraba primero: un commit fallido
        dejaba un documento activo cuya descarga respondía 404.)
        """
        document = self.get_document(farm_id, document_id)
        document.is_active = False
        document.deleted_at = datetime.now(timezone.utc)
        document.deleted_by = user_id
        self._record_audit(
            user_id=str(user_id),
            farm_id=str(farm_id),
            action="delete",
            entity="document",
            entity_id=str(document.id),
            details={"filename": document.original_filename},
        )
        self._repo.commit()
        self._storage.delete(document.stored_filename)
        self._repo.refresh(document)
        return document

    def get_document_for_download(self, farm_id: uuid.UUID, document_id: uuid.UUID) -> tuple[bytes, str, str]:
        """(bytes, nombre original, MIME) para devolver el archivo con su nombre real."""
        document = self.get_document(farm_id, document_id)
        return self._storage.read(document.stored_filename), document.original_filename, document.mime_type
