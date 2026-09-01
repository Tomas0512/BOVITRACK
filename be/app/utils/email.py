"""
Module: utils/email.py
Description: Transactional email sending (password reset, verification, invitations, notifications).
Purpose: Send emails to the backend chosen via settings.EMAIL_BACKEND.
         Backends: mailpit (SMTP local de desarrollo), smtp (SMTP real),
         resend (Resend API), log (solo consola).
Impact: Without this, users cannot receive password reset or verification emails.

Backend selection (settings.EMAIL_BACKEND):
  - mailpit → smtplib hacia Mailpit (SMTP_HOST). NO entrega real, ideal para dev.
  - smtp    → smtplib hacia un proveedor SMTP real (Gmail, etc.).
  - resend  → Resend API (correo real).
  - log     → simula en consola (el enlace aparece en el log del servidor).
  Si el backend elegido falla, se degrada a log (consola).

Mailpit — test emails locally without an account or domain:
  Web UI: http://localhost:8025 — all sent emails appear in real time.
"""

import asyncio
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import resend

from app.config import settings

logger = logging.getLogger(__name__)


def _send_email_resend(params: resend.Emails.SendParams) -> None:
    resend.api_key = settings.RESEND_API_KEY
    resend.Emails.send(params)


def _send_email_smtp(to_email: str, subject: str, html: str) -> None:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{settings.MAIL_FROM_NAME} <{settings.MAIL_FROM}>"
    msg["To"] = to_email
    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        if settings.SMTP_USE_TLS:
            server.starttls()
        if settings.SMTP_USERNAME:
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        server.send_message(msg)


def _build_html(body_html: str, cta_url: str, cta_text: str) -> str:
    return f"""
    <html>
    <body style="font-family: system-ui, -apple-system, sans-serif;
                 max-width: 600px; margin: 0 auto; padding: 24px; color: #2c1e17;">
        {body_html}
        <p style="margin: 32px 0;">
            <a href="{cta_url}"
               style="background-color: #b3541e; color: white; padding: 12px 28px;
                      text-decoration: none; border-radius: 6px; font-weight: 500;
                      font-size: 15px;">
                {cta_text}
            </a>
        </p>
        <hr style="border: none; border-top: 1px solid #e3dcd1; margin: 24px 0;">
        <p style="color: #6b5a45; font-size: 13px;">
            Si el botón no funciona, copia este enlace en tu navegador:<br>
            <a href="{cta_url}" style="color: #b3541e;">{cta_url}</a>
        </p>
    </body>
    </html>
    """


async def send_password_reset_email(email: str, token: str) -> None:
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
    subject = "BoviTrack — Recuperación de contraseña"
    html_content = _build_html(
        body_html="""
        <h2 style="color: #b3541e; margin-bottom: 8px;">
            Recuperación de contraseña — BoviTrack
        </h2>
        <p style="color: #2c1e17;">
            Recibimos una solicitud para restablecer la contraseña de tu cuenta.
        </p>
        <p style="color: #6b5a45; font-size: 14px;">
            El enlace es válido por <strong>20 minutos</strong>.
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
        <h2 style="color: #b3541e; margin-bottom: 8px;">
            Verifica tu cuenta — BoviTrack
        </h2>
        <p style="color: #2c1e17;">
            ¡Bienvenido! Para activar tu cuenta y poder iniciar sesión,
            haz clic en el botón de abajo.
        </p>
        <p style="color: #6b5a45; font-size: 14px;">
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
        <h2 style="color: #b3541e; margin-bottom: 8px;">
            Invitación a finca — BoviTrack
        </h2>
        <p style="color: #2c1e17;">
            Has sido invitado a unirte a la finca <strong>{farm_name}</strong>.
        </p>
        <p style="color: #6b5a45; font-size: 14px;">
            El enlace es válido por <strong>72 horas</strong>.
        </p>
        """,
        cta_url=invitation_url,
        cta_text="Aceptar invitación",
    )
    await _dispatch_email(email, subject, html_content, "INVITACIÓN", invitation_url)


async def _dispatch_email(email: str, subject: str, html: str, label: str, link: str) -> None:
    """¿Qué? Envía un email al backend configurado en settings.EMAIL_BACKEND.

    ¿Para qué? Centralizar la entrega para que dev y producción usen el canal
               correcto sin tocar el resto del código.
    ¿Impacto? Si el backend elegido falla, se degrada a log en consola.
    """
    backend = (settings.EMAIL_BACKEND or "mailpit").lower()

    if backend in ("mailpit", "smtp"):
        try:
            await asyncio.to_thread(_send_email_smtp, email, subject, html)
            logger.info("✅ Email de %s enviado vía SMTP a %s", label, email)
            return
        except Exception as exc:
            logger.error("❌ Error enviando email de %s vía SMTP a %s: %s", label, email, exc)

    elif backend == "resend":
        if not settings.RESEND_API_KEY:
            logger.error("❌ EMAIL_BACKEND=resend pero RESEND_API_KEY no está configurada")
        else:
            params: resend.Emails.SendParams = {
                "from": f"{settings.RESEND_FROM_NAME} <{settings.RESEND_FROM_EMAIL}>",
                "to": [email],
                "subject": subject,
                "html": html,
            }
            try:
                await asyncio.to_thread(_send_email_resend, params)
                logger.info("✅ Email de %s enviado vía Resend a %s", label, email)
                return
            except Exception as exc:
                logger.error("❌ Error enviando email de %s vía Resend a %s: %s", label, email, exc)

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


async def send_generic_email(
    to_email: str,
    subject: str,
    body_html: str,
    cta_url: str | None = None,
    cta_text: str | None = None,
    label: str = "NOTIFICACIÓN",
) -> None:
    """¿Qué? Envía un email de propósito general (útil para notificaciones HU014).

    ¿Para qué? Reutilizar el mismo pipeline de envío (EMAIL_BACKEND) para
               correos que no son de autenticación, sin escribir HTML a mano.
    ¿Impacto? Si cta_url se provee, se muestra un botón de acción en el cuerpo;
              si no, se envía solo el texto. Se degrada a log si falla el backend.
    """
    html_content = body_html
    if cta_url:
        html_content = _build_html(
            body_html=body_html,
            cta_url=cta_url,
            cta_text=cta_text or "Ver más",
        )
    await _dispatch_email(email=to_email, subject=subject, html=html_content, label=label, link=cta_url or subject)
