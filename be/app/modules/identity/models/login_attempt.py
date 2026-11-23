"""
Módulo: modules/identity/models/login_attempt.py
¿Qué? Tabla `login_attempt`: intentos fallidos de login por correo y, si aplica,
      hasta cuándo está bloqueado ese correo.
¿Para qué? Que el bloqueo tras 5 intentos fallidos sobreviva a reinicios y sea el
           MISMO para todos los procesos de la API (WEB_CONCURRENCY > 1). Antes
           vivía en la memoria de cada proceso.
¿Impacto? El correo no se guarda: la llave es su SHA-256 (también se cuentan
          intentos contra correos que no existen, y no queremos una lista de
          correos que alguien probó). Las filas viejas se limpian solas.
"""

from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class LoginAttempt(Base):
    __tablename__ = "login_attempt"

    # SHA-256 (hex) del correo normalizado (minúsculas, sin espacios).
    email_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    failed_count: Mapped[int] = mapped_column(Integer, nullable=False)
    last_failed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    locked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        return f"LoginAttempt(failed={self.failed_count}, locked_until={self.locked_until})"
