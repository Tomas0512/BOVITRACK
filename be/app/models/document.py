"""
╔════════════════════════════════════════════════════════════════════════════╗
║ MODELO: app/models/document.py                                            ║
║ PROPÓSITO: Modelo ORM para gestión de documentos en BoviTrack             ║
║                                                                            ║
║ ¿QUÉ?                                                                      ║
║   Tabla para almacenar metadatos de documentos (PDF, imágenes, etc)       ║
║   y sus asociaciones a:                                                    ║
║   - Fincas (Farm)                                                          ║
║   - Bovinos (Bovine)                                                       ║
║   - Eventos reproductivos (ReproductiveEvent)                             ║
║   - Tratamientos (Treatment)                                              ║
║   - Planes sanitarios (SanitaryPlan)                                       ║
║                                                                            ║
║ ¿PARA QUÉ?                                                                ║
║   HU012: Subir y gestionar documentos                                     ║
║   Permitir que usuarios adjunten archivos a diferentes entidades          ║
║                                                                            ║
║ ¿IMPACTO?                                                                 ║
║   Los documentos se guardan en filesystem local (storage/)                ║
║   Los metadatos se almacenan en BD para trazabilidad y búsqueda           ║
╚════════════════════════════════════════════════════════════════════════════╝
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
    ¿Qué? Tipos de documentos permitidos en el sistema.
    ¿Para qué? Validar que solo se suban archivos de tipos específicos.
    ¿Impacto? Limita extensiones a tipos seguros (no .exe, .sh, etc).
    """
    PDF = "pdf"
    IMAGE = "image"  # jpg, png, etc
    WORD = "word"    # docx, doc
    EXCEL = "excel"  # xlsx, xls
    TEXT = "text"    # txt, csv


class DocumentAssociation(str, Enum):
    """
    ¿Qué? Tipos de entidades a las que se puede asociar un documento.
    ¿Para qué? HU012 Task 12.3: Asociación a finca/bovino/evento.
    ¿Impacto? Define dónde se puede "adjuntar" un documento.
    """
    FARM = "farm"                          # Documentos generales de finca
    BOVINE = "bovine"                      # Ficha, fotos, genealogía
    REPRODUCTIVE_EVENT = "reproductive_event"  # Diagnósticos, partos
    TREATMENT = "treatment"                # Recetas, laboratorio
    SANITARY_PLAN = "sanitary_plan"        # Calendarios, instructivos


class Document(Base):
    """
    ¿Qué? Modelo para almacenar metadatos de documentos.
    ¿Para qué? Rastrear archivos subidos, quién los subió, cuándo, etc.
    ¿Impacto? No almacena el contenido (va en filesystem), solo metadatos.
    """
    __tablename__ = "document"

    # ═══════════════════════════════════════════════════════════════════
    # 🔑 IDENTIFICACIÓN
    # ═══════════════════════════════════════════════════════════════════

    # UUID único del documento
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    # Referencia a la finca (requerida - multitenancy)
    farm_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("farm.id", ondelete="CASCADE"),
        nullable=False
    )

    # ═══════════════════════════════════════════════════════════════════
    # 📄 METADATOS DEL ARCHIVO
    # ═══════════════════════════════════════════════════════════════════

    # Nombre original del archivo (ej: "Diagnóstico_Vaca_001.pdf")
    original_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    # Nombre sanitizado para guardar en filesystem
    # ¿Para qué? Prevenir ataques de path traversal
    # Formato: {uuid}_{timestamp}.{ext}
    stored_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True
    )

    # Tamaño del archivo en bytes
    file_size: Mapped[int] = mapped_column(
        nullable=False
    )

    # Tipo MIME (ej: "application/pdf", "image/jpeg")
    mime_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    # Clasificación del documento
    document_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False
        # Valores: pdf, image, word, excel, text
    )

    # ═══════════════════════════════════════════════════════════════════
    # 🔗 ASOCIACIONES (HU012 Task 12.3)
    # ═══════════════════════════════════════════════════════════════════

    # Tipo de entidad a la que está asociado
    # ej: "farm", "bovine", "reproductive_event"
    association_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False
    )

    # ID de la entidad asociada (UUID)
    # Ejemplo: si association_type="bovine", esto es el bovine_id
    associated_entity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False
    )

    # ═══════════════════════════════════════════════════════════════════
    # 📝 DESCRIPCIÓN Y AUDITORÍA
    # ═══════════════════════════════════════════════════════════════════

    # Descripción del documento (ej: "Diagnóstico de preñez - Ecografía")
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    # Quién subió el documento
    uploaded_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False
    )

    # Fecha de carga del documento
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # ¿Es activo o fue eliminado lógicamente?
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    # Fecha de eliminación lógica (soft delete)
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    # Quién lo eliminó
    deleted_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )

    # ═══════════════════════════════════════════════════════════════════
    # 🔍 RELACIONES ORM
    # ═══════════════════════════════════════════════════════════════════

    # ¿Qué? Relación a la finca
    farm: Mapped["Farm"] = relationship()

    # ¿Qué? Relación al usuario que lo subió
    uploader: Mapped["User"] = relationship(foreign_keys=[uploaded_by])

    # ¿Qué? Relación al usuario que lo eliminó
    deleter: Mapped["User | None"] = relationship(foreign_keys=[deleted_by])

    def __repr__(self) -> str:
        return f"Document(id={self.id}, filename={self.original_filename}, type={self.document_type})"
