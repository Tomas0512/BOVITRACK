"""
Módulo: models/password_reset_token.py
Descripción: Modelo ORM para la tabla `password_reset_tokens` en PostgreSQL.
¿Para qué? Almacenar tokens temporales de un solo uso que permiten restablecer
           la contraseña de un usuario que olvidó sus credenciales.
¿Impacto? Sin esta tabla, el flujo de "forgot password" no puede funcionar,
          ya que no habría forma de verificar que el enlace de reset es legítimo.
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class PasswordResetToken(Base):
    """Modelo ORM para la tabla `password_reset_tokens`.

    Cada vez que un usuario solicita recuperar su contraseña, se crea un
    registro aquí con un token único y una fecha de expiración (1 hora).
    """

    __tablename__ = "password_reset_tokens"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Referencia al usuario que solicitó el reset
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Token único que se envía en el email de recuperación
    token: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )

    # Fecha y hora en que el token deja de ser válido
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    # ¿Ya fue utilizado? (evita reutilización)
    used: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # Fecha de creación
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relación ORM con User
    user = relationship("User", lazy="selectin")

    def __repr__(self) -> str:
        token_preview = self.token[:8] if self.token else "N/A"
        return (
            f"PasswordResetToken(id={self.id}, user_id={self.user_id}, "
            f"token={token_preview}..., used={self.used})"
        )
