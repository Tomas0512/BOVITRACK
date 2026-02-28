"""
Módulo: utils/email.py
Descripción: Utilidad para envío de correos electrónicos.
¿Para qué? Enviar el enlace de recuperación de contraseña al usuario.
           En modo desarrollo imprime en consola; en producción enviará por SMTP.
¿Impacto? Sin esto, el flujo de "Olvidé mi contraseña" no puede notificar al usuario.
"""

import logging

from app.config import settings

logger = logging.getLogger(__name__)


async def send_password_reset_email(email: str, token: str) -> None:
    """Envía un correo con el enlace para restablecer la contraseña.

    En desarrollo: imprime el enlace en la consola del servidor.
    En producción: se debe integrar con un servicio SMTP real (configurar MAIL_* en .env).

    Args:
        email: Dirección de correo del destinatario.
        token: Token único de recuperación.
    """
    reset_link = f"{settings.FRONTEND_URL}/reset-password?token={token}"

    # ── Modo desarrollo: imprime en consola ──
    logger.info("=" * 60)
    logger.info("📧 CORREO DE RECUPERACIÓN (modo desarrollo)")
    logger.info(f"   Para: {email}")
    logger.info(f"   Enlace: {reset_link}")
    logger.info("=" * 60)

    # ── Modo producción (descomentar cuando se configure SMTP) ──
    # from email.mime.text import MIMEText
    # import aiosmtplib
    #
    # message = MIMEText(
    #     f"Hola,\n\nHaz clic en el siguiente enlace para restablecer tu contraseña:\n\n"
    #     f"{reset_link}\n\nEste enlace expira en 1 hora.\n\nEquipo BoviTrack",
    #     "plain",
    #     "utf-8",
    # )
    # message["From"] = settings.MAIL_FROM
    # message["To"] = email
    # message["Subject"] = "BoviTrack - Restablecer contraseña"
    #
    # await aiosmtplib.send(
    #     message,
    #     hostname=settings.MAIL_SERVER,
    #     port=settings.MAIL_PORT,
    #     username=settings.MAIL_USERNAME,
    #     password=settings.MAIL_PASSWORD,
    #     use_tls=settings.MAIL_USE_TLS,
    # )
