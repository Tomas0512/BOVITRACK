"""
╔════════════════════════════════════════════════════════════════════════════╗
║ SCHEMAS: app/schemas/document.py                                          ║
║ PROPÓSITO: Validación Pydantic para documentos (HU012)                    ║
║                                                                            ║
║ ¿QUÉ?                                                                      ║
║   Modelos Pydantic para validar:                                           ║
║   - Upload de documentos                                                   ║
║   - Parámetros de listado/búsqueda                                        ║
║   - Respuestas al cliente                                                  ║
║                                                                            ║
║ ¿PARA QUÉ?                                                                ║
║   FastAPI retorna 422 si datos no cumplen estos esquemas                  ║
║   Documentación automática en Swagger                                      ║
║   Type-safety en el código                                                 ║
╚════════════════════════════════════════════════════════════════════════════╝
"""

import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, field_validator


# ═══════════════════════════════════════════════════════════════════════════
# 📋 ENUMS
# ═══════════════════════════════════════════════════════════════════════════

class DocumentTypeEnum(str, Enum):
    """Tipos de documentos permitidos"""
    PDF = "pdf"
    IMAGE = "image"
    WORD = "word"
    EXCEL = "excel"
    TEXT = "text"


class DocumentAssociationEnum(str, Enum):
    """Tipos de entidades a asociar"""
    FARM = "farm"
    BOVINE = "bovine"
    REPRODUCTIVE_EVENT = "reproductive_event"
    TREATMENT = "treatment"
    SANITARY_PLAN = "sanitary_plan"


# ═══════════════════════════════════════════════════════════════════════════
# 📥 SCHEMAS DE ENTRADA (REQUEST)
# ═══════════════════════════════════════════════════════════════════════════

class DocumentUploadRequest(BaseModel):
    """
    ¿Qué? Datos requeridos para subir un documento.
    ¿Para qué? Validar que el cliente envía metadatos correctos.

    ¿Campos?
      - document_type: Tipo del documento (pdf, image, etc)
      - file_size: Tamaño en bytes (validar límite)
      - mime_type: Tipo MIME (application/pdf, image/jpeg, etc)
      - association_type: Con qué entidad se asocia
      - associated_entity_id: UUID de la entidad
      - description: Descripción opcional
    """

    # Tipo de documento
    document_type: DocumentTypeEnum = Field(
        ...,
        description="Tipo de documento"
    )

    # Tamaño del archivo (bytes)
    file_size: int = Field(
        ...,
        gt=0,  # Greater than 0
        le=52428800,  # 50MB máximo
        description="Tamaño en bytes (máximo 50MB)"
    )

    # Tipo MIME
    mime_type: str = Field(
        ...,
        description="application/pdf, image/jpeg, etc"
    )

    # Tipo de asociación
    association_type: DocumentAssociationEnum = Field(
        ...,
        description="farm, bovine, reproductive_event, etc"
    )

    # ID de la entidad asociada
    associated_entity_id: uuid.UUID = Field(
        ...,
        description="UUID de la finca/bovino/evento"
    )

    # Descripción
    description: str | None = Field(
        None,
        max_length=500,
        description="Descripción del documento"
    )

    @field_validator("mime_type")
    @classmethod
    def validate_mime_type(cls, v: str) -> str:
        """
        ¿Qué? Valida que el MIME type sea seguro.
        ¿Para qué? Prevenir upload de ejecutables disfrazados.
        """
        # Whitelist de tipos MIME permitidos
        allowed_types = {
            "application/pdf",
            "image/jpeg",
            "image/png",
            "image/gif",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/vnd.ms-excel",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "text/plain",
            "text/csv",
        }

        if v not in allowed_types:
            raise ValueError(f"MIME type no permitido: {v}")

        return v


class DocumentListRequest(BaseModel):
    """
    ¿Qué? Parámetros para listar documentos.
    ¿Para qué? HU012 Task 12.4: Repositorio documental con búsqueda.
    """

    # Filtro por tipo de asociación
    association_type: DocumentAssociationEnum | None = Field(
        None,
        description="Filtrar por tipo (farm, bovine, etc)"
    )

    # Filtro por entidad específica
    associated_entity_id: uuid.UUID | None = Field(
        None,
        description="Filtrar por entidad"
    )

    # Búsqueda en nombre
    search: str | None = Field(
        None,
        max_length=100,
        description="Buscar en nombre o descripción"
    )

    # Ordenamiento
    order_by: str = Field(
        "uploaded_at",
        pattern="^(uploaded_at|filename)$",
        description="uploaded_at o filename"
    )

    # Dirección
    order_direction: str = Field(
        "desc",
        pattern="^(asc|desc)$",
        description="asc o desc"
    )


# ═══════════════════════════════════════════════════════════════════════════
# 📤 SCHEMAS DE SALIDA (RESPONSE)
# ═══════════════════════════════════════════════════════════════════════════

class DocumentResponse(BaseModel):
    """
    ¿Qué? Información de un documento para retornar al cliente.
    ¿Para qué? Serializar documento a JSON.
    """

    id: uuid.UUID = Field(..., description="ID único")

    original_filename: str = Field(..., description="Nombre original del archivo")

    file_size: int = Field(..., description="Tamaño en bytes")

    mime_type: str = Field(..., description="Tipo MIME")

    document_type: str = Field(..., description="Tipo de documento")

    association_type: str = Field(..., description="Tipo de asociación")

    associated_entity_id: uuid.UUID = Field(..., description="ID de la entidad")

    description: str | None = Field(None, description="Descripción")

    uploaded_by: uuid.UUID = Field(..., description="Quién lo subió")

    uploaded_at: datetime = Field(..., description="Fecha de carga")

    is_active: bool = Field(..., description="¿Está activo?")

    class ConfigDict:
        from_attributes = True


class DocumentListResponse(BaseModel):
    """
    ¿Qué? Lista de documentos con metadatos.
    ¿Para qué? Retornar resultados del repositorio.
    """

    documents: list[DocumentResponse] = Field(..., description="Array de documentos")

    total: int = Field(..., description="Total de documentos")

    page: int = Field(..., description="Página actual")

    page_size: int = Field(..., description="Documentos por página")


class DocumentDeleteResponse(BaseModel):
    """
    ¿Qué? Confirmación de eliminación.
    ¿Para qué? Soft delete de documentos.
    """

    message: str = Field(..., description="Mensaje de confirmación")

    document_id: uuid.UUID = Field(..., description="ID del documento")

    deleted_at: datetime = Field(..., description="Fecha de eliminación")
