"""
Módulo: config.py
Descripción: Configuración centralizada del backend usando Pydantic Settings.
¿Para qué? Cargar y validar TODAS las variables de entorno necesarias al iniciar la app.
           Si falta alguna variable o tiene un formato inválido, la app no arranca y muestra
           un error claro indicando cuál es el problema.
¿Impacto? Sin este módulo, las variables de entorno se leerían con os.getenv() sin validación,
          lo que podría causar errores silenciosos en tiempo de ejecución.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración de la aplicación cargada desde variables de entorno (.env)."""

    # 🗄️ Base de datos
    DATABASE_URL: str

    # 🔐 JWT y Seguridad
    SECRET_KEY: str
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

    # 🌍 Entorno (development / production)
    ENVIRONMENT: str = "development"

    # 🚦 Rate limiting (slowapi)
    # True (default) aplica los límites de auth (5/min login, 3/min recuperación).
    # Se puede desactivar SOLO en desarrollo/QA local para que la suite E2E
    # pueda ejecutar los ~15 inicios de sesión de la corrida completa sin
    # recibir 429. Nunca desactivar en producción.
    RATE_LIMIT_ENABLED: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


# Instancia singleton — se crea al importar y valida todas las variables.
settings = Settings()
