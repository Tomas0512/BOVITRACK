"""
Módulo: utils/email.py
Descripción: Envío de correos transaccionales vía SMTP (Mailpit en Docker, Gmail en producción).
¿Para qué? Enviar correos de recuperación de contraseña, verificación de cuenta e invitaciones.
¿Impacto? Sin esto, el flujo de "Olvidé mi contraseña" no puede notificar al usuario.

Prioridad de backend:
  1. SMTP_HOST configurado → usa smtplib (stdlib, sin dependencias extra)
  2. Ninguno → simula en consola (el enlace aparece en los logs del servidor)

Mailpit (desarrollo local):
  Web UI: http://localhost:8025 — todos los correos aparecen en tiempo real.
"""

import asyncio
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.config import settings

logger = logging.getLogger(__name__)


def _send_email_smtp(to_email: str, subject: str, html: str) -> None:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{settings.MAIL_FROM_NAME} <{settings.MAIL_FROM}>"
    msg["To"] = to_email
    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        if settings.SMTP_USERNAME:
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        server.send_message(msg)


def _build_html(body_html: str, cta_url: str, cta_text: str) -> str:
    return f"""
    <html>
    <body style="font-family: system-ui, -apple-system, sans-serif;
                 max-width: 600px; margin: 0 auto; padding: 24px; color: #111827;">
        {body_html}
        <p style="margin: 32px 0;">
            <a href="{cta_url}"
               style="background-color: #2D6A4F; color: white; padding: 12px 28px;
                      text-decoration: none; border-radius: 6px; font-weight: 500;
                      font-size: 15px;">
                {cta_text}
            </a>
        </p>
        <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 24px 0;">
        <p style="color: #6b7280; font-size: 13px;">
            Si el botón no funciona, copia este enlace en tu navegador:<br>
            <a href="{cta_url}" style="color: #2D6A4F;">{cta_url}</a>
        </p>
    </body>
    </html>
    """


async def send_password_reset_email(email: str, token: str) -> None:
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
    subject = "BoviTrack — Recuperación de contraseña"
    html_content = _build_html(
        body_html="""
        <h2 style="color: #2D6A4F; margin-bottom: 8px;">
            Recuperación de contraseña — BoviTrack
        </h2>
        <p style="color: #374151;">
            Recibimos una solicitud para restablecer la contraseña de tu cuenta.
        </p>
        <p style="color: #6b7280; font-size: 14px;">
            El enlace es válido por <strong>1 hora</strong>.
            Si no lo solicitaste, ignora este email.
        </p>
        """,
        cta_url=reset_url,
        cta_text="Restablecer contraseña",
    )
    await _dispatch_email(email, subject, html_content, "RECUPERACIÓN", reset_url)


async def send_email_verification(email: str, token: str) -> None:
    verify_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"
    subject = "BoviTrack — Verifica tu cuenta"
    html_content = _build_html(
        body_html="""
        <h2 style="color: #2D6A4F; margin-bottom: 8px;">
            Verifica tu cuenta — BoviTrack
        </h2>
        <p style="color: #374151;">
            ¡Bienvenido! Para activar tu cuenta y poder iniciar sesión,
            haz clic en el botón de abajo.
        </p>
        <p style="color: #6b7280; font-size: 14px;">
            El enlace es válido por <strong>24 horas</strong>.
        </p>
        """,
        cta_url=verify_url,
        cta_text="Verificar mi cuenta",
    )
    await _dispatch_email(email, subject, html_content, "VERIFICACIÓN", verify_url)


async def send_farm_invitation_email(email: str, token: str, farm_name: str) -> None:
    invitation_url = f"{settings.FRONTEND_URL}/register/invitation?token={token}"
    subject = f"BoviTrack — Has sido invitado a {farm_name}"
    html_content = _build_html(
        body_html=f"""
        <h2 style="color: #2D6A4F; margin-bottom: 8px;">
            Invitación a finca — BoviTrack
        </h2>
        <p style="color: #374151;">
            Has sido invitado a unirte a la finca <strong>{farm_name}</strong>.
        </p>
        <p style="color: #6b7280; font-size: 14px;">
            El enlace es válido por <strong>72 horas</strong>.
        </p>
        """,
        cta_url=invitation_url,
        cta_text="Aceptar invitación",
    )
    await _dispatch_email(email, subject, html_content, "INVITACIÓN", invitation_url)


async def _dispatch_email(email: str, subject: str, html: str, label: str, link: str) -> None:
    if not settings.SMTP_HOST:
        _log_fallback(label, email, link)
        return

    try:
        await asyncio.to_thread(_send_email_smtp, email, subject, html)
        logger.info("✅ Email de %s enviado vía SMTP a %s", label, email)
    except Exception as exc:
        logger.error("❌ Error enviando email de %s vía SMTP a %s: %s", label, email, exc)
        _log_fallback(label, email, link)


def _log_fallback(label: str, email: str, link: str) -> None:
    logger.info(
        "\n%s\n"
        "📧 EMAIL DE %s (sin SMTP — copiar enlace del log)\n"
        "   Para: %s\n"
        "   Enlace: %s\n"
        "%s",
        "=" * 60,
        label,
        email,
        link,
        "=" * 60,
    )
