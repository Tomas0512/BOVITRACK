"""
Module: app/schemas/document.py
Purpose: Pydantic validation for documents (HU012)

What?
  Pydantic models to validate:
  - Document upload
  - List/search parameters
  - Client responses

Why?
  FastAPI returns 422 if data doesn't match these schemas
  Auto-documentation in Swagger
  Type-safety in code
"""

import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ── Enums ───────────────────────────────────────────────

class DocumentTypeEnum(str, Enum):
    """Allowed document types"""
    PDF = "pdf"
    IMAGE = "image"
    WORD = "word"
    EXCEL = "excel"
    TEXT = "text"


class DocumentAssociationEnum(str, Enum):
    """Entity types to associate"""
    FARM = "farm"
    BOVINE = "bovine"
    REPRODUCTIVE_EVENT = "reproductive_event"
    TREATMENT = "treatment"
    SANITARY_PLAN = "sanitary_plan"


# ── Request schemas ──────────────────────────────────────

class DocumentUploadRequest(BaseModel):
    """
    What? Required data to upload a document.
    Why? Validate that the client sends correct metadata.

    Fields?
      - document_type: Document type (pdf, image, etc)
      - file_size: Size in bytes (validate limit)
      - mime_type: MIME type (application/pdf, image/jpeg, etc)
      - association_type: Which entity it associates with
      - associated_entity_id: Entity UUID
      - description: Optional description
    """

    # Document type
    document_type: DocumentTypeEnum = Field(
        ...,
        description="Document type"
    )

    # File size (bytes)
    file_size: int = Field(
        ...,
        gt=0,
        le=52428800,  # 50MB max
        description="File size in bytes (max 50MB)"
    )

    # MIME type
    mime_type: str = Field(
        ...,
        description="application/pdf, image/jpeg, etc"
    )

    # Association type
    association_type: DocumentAssociationEnum = Field(
        ...,
        description="farm, bovine, reproductive_event, etc"
    )

    # Associated entity ID
    associated_entity_id: uuid.UUID = Field(
        ...,
        description="Entity UUID (farm/bovine/event)"
    )

    # Description
    description: str | None = Field(
        None,
        max_length=500,
        description="Document description"
    )

    @field_validator("mime_type")
    @classmethod
    def validate_mime_type(cls, v: str) -> str:
        """
        What? Validates that the MIME type is safe.
        Why? Prevent disguised executable upload.
        """
        # Whitelist of allowed MIME types
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
            raise ValueError(f"Unallowed MIME type: {v}")

        return v


class DocumentListRequest(BaseModel):
    """
    What? Parameters to list documents.
    Why? HU012 Task 12.4: Document repository with search.
    """

    # Filter by association type
    association_type: DocumentAssociationEnum | None = Field(
        None,
        description="Filter by type (farm, bovine, etc)"
    )

    # Filter by specific entity
    associated_entity_id: uuid.UUID | None = Field(
        None,
        description="Filter by entity"
    )

    # Search in name/description
    search: str | None = Field(
        None,
        max_length=100,
        description="Search in name or description"
    )

    # Ordering
    order_by: str = Field(
        "uploaded_at",
        pattern="^(uploaded_at|filename)$",
        description="uploaded_at or filename"
    )

    # Direction
    order_direction: str = Field(
        "desc",
        pattern="^(asc|desc)$",
        description="asc or desc"
    )


# ── Response schemas ─────────────────────────────────────

class DocumentResponse(BaseModel):
    """
    What? Document information to return to the client.
    Why? Serialize document to JSON.
    """

    id: uuid.UUID = Field(..., description="Unique ID")

    original_filename: str = Field(..., description="Original filename")

    file_size: int = Field(..., description="File size in bytes")

    mime_type: str = Field(..., description="MIME type")

    document_type: str = Field(..., description="Document type")

    association_type: str = Field(..., description="Association type")

    associated_entity_id: uuid.UUID = Field(..., description="Entity ID")

    description: str | None = Field(None, description="Description")

    uploaded_by: uuid.UUID = Field(..., description="Who uploaded it")

    uploaded_at: datetime = Field(..., description="Upload date")

    is_active: bool = Field(..., description="Is active?")

    model_config = ConfigDict(from_attributes=True)


class DocumentListResponse(BaseModel):
    """
    What? Document list with metadata.
    Why? Return repository results.
    """

    documents: list[DocumentResponse] = Field(..., description="Document array")

    total: int = Field(..., description="Total documents")

    page: int = Field(..., description="Current page")

    page_size: int = Field(..., description="Documents per page")


class DocumentDeleteResponse(BaseModel):
    """
    What? Deletion confirmation.
    Why? Soft delete of documents.
    """

    message: str = Field(..., description="Confirmation message")

    document_id: uuid.UUID = Field(..., description="Document ID")

    deleted_at: datetime = Field(..., description="Deletion date")
