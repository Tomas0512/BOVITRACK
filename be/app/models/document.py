"""
Module: app/models/document.py
Purpose: ORM model for document management in BoviTrack

What?
  Table to store document metadata (PDF, images, etc)
  and their associations to:
  - Farms
  - Bovines
  - Reproductive Events
  - Treatments
  - Sanitary Plans

Why?
  HU012: Upload and manage documents
  Allow users to attach files to different entities

Impact?
  Documents are saved in local filesystem (storage/)
  Metadata is stored in DB for traceability and search
"""

import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import (
    Boolean, DateTime, ForeignKey, String, Text, func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class DocumentType(str, Enum):
    """
    What? Allowed document types in the system.
    Why? Validate that only specific file types are uploaded.
    Impact? Limits extensions to safe types (no .exe, .sh, etc).
    """
    PDF = "pdf"
    IMAGE = "image"  # jpg, png, etc
    WORD = "word"    # docx, doc
    EXCEL = "excel"  # xlsx, xls
    TEXT = "text"    # txt, csv


class DocumentAssociation(str, Enum):
    """
    What? Entity types a document can be associated with.
    Why? HU012 Task 12.3: Association to farm/bovine/event.
    Impact? Defines where a document can be "attached".
    """
    FARM = "farm"                          # Documentos generales de finca
    BOVINE = "bovine"                      # Ficha, fotos, genealogía
    REPRODUCTIVE_EVENT = "reproductive_event"  # Diagnósticos, partos
    TREATMENT = "treatment"                # Recetas, laboratorio
    SANITARY_PLAN = "sanitary_plan"        # Calendarios, instructivos


class Document(Base):
    """
    What? Model to store document metadata.
    Why? Track uploaded files, who uploaded them, when, etc.
    Impact? Does not store content (goes to filesystem), only metadata.
    """
    __tablename__ = "document"

    # ── Identification ─────────────────────────────────────

    # Document UUID
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    # Farm reference (required - multitenancy)
    farm_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("farm.id", ondelete="CASCADE"),
        nullable=False
    )

    # ── File Metadata ──────────────────────────────────────

    # Original filename (e.g. "Diagnostico_Vaca_001.pdf")
    original_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    # Sanitized filename for filesystem storage
    # Why? Prevent path traversal attacks
    # Format: {uuid}_{timestamp}.{ext}
    stored_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True
    )

    # File size in bytes
    file_size: Mapped[int] = mapped_column(
        nullable=False
    )

    # MIME type (e.g. "application/pdf", "image/jpeg")
    mime_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    # Document classification
    document_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False
        # Values: pdf, image, word, excel, text
    )

    # ── Associations (HU012 Task 12.3) ─────────────────────

    # Entity type this document is associated with
    # e.g. "farm", "bovine", "reproductive_event"
    association_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False
    )

    # Associated entity ID (UUID)
    # Example: if association_type="bovine", this is the bovine_id
    associated_entity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False
    )

    # ── Description & Audit ─────────────────────────────────

    # Document description (e.g. "Pregnancy diagnosis - Ultrasound")
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    # Who uploaded the document
    uploaded_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False
    )

    # Upload date
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Is active or soft-deleted?
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    # Soft delete date
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    # Who deleted it
    deleted_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )

    # ── ORM Relationships ───────────────────────────────────

    # What? Farm relationship
    farm: Mapped["Farm"] = relationship()

    # What? Uploader user relationship
    uploader: Mapped["User"] = relationship(foreign_keys=[uploaded_by])

    # What? Deleter user relationship
    deleter: Mapped["User | None"] = relationship(foreign_keys=[deleted_by])

    def __repr__(self) -> str:
        return f"Document(id={self.id}, filename={self.original_filename}, type={self.document_type})"
