"""
Módulo: core/config.py
Descripción: Configuración centralizada del backend usando Pydantic Settings.
¿Para qué? Cargar y validar TODAS las variables de entorno necesarias al iniciar la app.
           Si falta alguna variable o tiene un formato inválido, la app no arranca y muestra
           un error claro indicando cuál es el problema.
¿Impacto? Sin este módulo, las variables de entorno se leerían con os.getenv() sin validación,
          lo que podría causar errores silenciosos en tiempo de ejecución.
"""

from typing import Literal

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración de la aplicación cargada desde variables de entorno (.env)."""

    # 🗄️ Base de datos
    DATABASE_URL: str

    # 🔐 JWT y Seguridad
    SECRET_KEY: str = Field(min_length=32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # 📧 Email — Backend de entrega seleccionable
    # Valores: smtp | resend | log
    #   smtp    → Correo real vía SMTP (Gmail u otro proveedor).
    #   resend  → Correo real vía Resend API.
    #   log     → Solo imprime el enlace/correo en consola (sin envío).
    EMAIL_BACKEND: str = "smtp"

    # 📧 Email — Resend API (correo real vía API)
    RESEND_API_KEY: str = ""
    RESEND_FROM_EMAIL: str = "noreply@bovitrack.com"
    RESEND_FROM_NAME: str = "BoviTrack"

    # 📧 Email — SMTP (Gmail u otro proveedor en desarrollo/producción)
    MAIL_FROM: str = "noreply@bovitrack.com"
    MAIL_FROM_NAME: str = "BoviTrack"
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_USE_TLS: bool = True

    # 🌐 URL del frontend (para CORS y enlaces en emails)
    FRONTEND_URL: str = "http://localhost:5173"

    # 🌍 Entorno. En "production": sin /docs, CORS solo FRONTEND_URL, sin --reload
    # y la configuración se valida (ver _production_must_be_safe).
    ENVIRONMENT: Literal["development", "test", "staging", "production"] = "development"

    # 🚦 Rate limiting (slowapi)
    # True (default) aplica los límites de auth (5/min login, 3/min recuperación).
    # Se puede desactivar SOLO en desarrollo/QA local para que la suite E2E
    # pueda ejecutar los ~15 inicios de sesión de la corrida completa sin
    # recibir 429. Nunca desactivar en producción.
    RATE_LIMIT_ENABLED: bool = True

    # 📁 Almacenamiento de documentos (módulo documents)
    # Directorio donde se guardan los archivos subidos. Relativo al directorio de
    # trabajo del backend (/app en Docker). En producción conviene montarlo como
    # volumen persistente para no perder archivos al recrear el contenedor.
    DOCUMENTS_STORAGE_DIR: str = "storage/documents"

    # 🔔 Motor de notificaciones (módulo notifications)
    # Cada cuántos minutos se revisan las alertas de todas las fincas y se
    # envían las notificaciones pendientes. 0 = desactivado (útil en pruebas).
    # El motor es idempotente: no repite una alerta al mismo usuario en 24 h.
    NOTIFICATIONS_INTERVAL_MINUTES: int = 15

    @model_validator(mode="after")
    def _production_must_be_safe(self) -> "Settings":
        """¿Qué? En producción, la app NO arranca con una configuración insegura.
        ¿Para qué? Que un error de configuración se vea al desplegar, no después:
           - sin rate limiting, el login queda abierto a fuerza bruta;
           - con EMAIL_BACKEND=log, los enlaces de recuperación de contraseña
             quedarían escritos en los logs, y nadie recibiría los correos.
        """
        if self.ENVIRONMENT != "production":
            return self
        problems: list[str] = []
        if not self.RATE_LIMIT_ENABLED:
            problems.append("RATE_LIMIT_ENABLED debe ser true")
        backend = self.EMAIL_BACKEND.lower()
        if backend not in ("smtp", "resend"):
            problems.append(f"EMAIL_BACKEND={self.EMAIL_BACKEND!r} no entrega correos reales (usa smtp o resend)")
        elif backend == "smtp" and not self.SMTP_HOST:
            problems.append("EMAIL_BACKEND=smtp necesita SMTP_HOST")
        elif backend == "resend" and not self.RESEND_API_KEY:
            problems.append("EMAIL_BACKEND=resend necesita RESEND_API_KEY")
        if problems:
            raise ValueError("Configuración insegura para producción: " + "; ".join(problems))
        return self

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


# Instancia singleton — se crea al importar y valida todas las variables.
settings = Settings()
