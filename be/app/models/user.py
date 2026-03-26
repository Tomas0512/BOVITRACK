"""
Módulo: models/user.py
Descripción: Modelo ORM que representa la tabla `users` en PostgreSQL.
¿Para qué? Definir la estructura de la tabla de usuarios con los campos que
           maneja el formulario de registro de BoviTrack: nombres, apellidos,
           tipo y número de documento, email, teléfono y contraseña hasheada.
¿Impacto? Este modelo es el corazón del sistema de autenticación. Cada registro
          en esta tabla representa un usuario del sistema.
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    """Modelo ORM para la tabla `users`.

    Campos adaptados al formulario de registro de BoviTrack:
    firstName, lastName, documentType, documentNumber, email, phone, password.
    """

    __tablename__ = "users"

    # Identificador único (UUID)
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Nombres del usuario
    first_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # Apellidos del usuario
    last_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # Tipo de documento (CC, CE, TI, PP, NIT)
    document_type: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    # Número de documento
    document_number: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
    )

    # Correo electrónico (único, indexado para búsquedas rápidas en login)
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )

    # Teléfono de contacto
    phone: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    # Hash bcrypt de la contraseña (NUNCA texto plano)
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # ¿Cuenta activa? (permite desactivar sin borrar)
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    # Confirmación de email y control de sesión global
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    token_version: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Consentimientos legales
    accepted_terms: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    accepted_data_policy: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    accepted_terms_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    accepted_data_policy_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Fecha de creación (generada por PostgreSQL)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Fecha de última actualización
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    password_reset_tokens: Mapped[list["PasswordResetToken"]] = relationship(
        back_populates="user", cascade="all, delete-orphan",
    )
    email_verification_tokens: Mapped[list["EmailVerificationToken"]] = relationship(
        back_populates="user", cascade="all, delete-orphan",
    )
    audit_logs: Mapped[list["AuditLog"]] = relationship(back_populates="user")

    def __repr__(self) -> str:
        return f"User(id={self.id}, email={self.email}, is_active={self.is_active})"
