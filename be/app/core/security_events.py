"""
Módulo: core/security_events.py (antes utils/audit_log.py)
¿Qué? Registro estructurado (JSON) de eventos de seguridad: logins exitosos y
      fallidos, cambio y recuperación de contraseña. Enmascara el correo.
¿Para qué? Dejar rastro en los logs para detectar abuso (fuerza bruta, robo de
           cuentas) sin exponer datos personales.
¿Impacto? Es distinto de la auditoría de negocio (tabla audit_log, módulo de
          auditoría): esto va a logs del servidor, aquella a la base de datos.
          Se renombró para no confundir ambas responsabilidades.

Nota: hoy ningún endpoint llama a estas funciones. Se conectan al flujo de
login en la Parte 6 (seguridad).
"""

import json
import logging
from datetime import datetime, timezone

audit_logger = logging.getLogger("security.audit")
audit_logger.setLevel(logging.WARNING)


def _redact_email(email: str) -> str:
    local, domain = email.split("@")
    return f"{local[0]}***@{domain}" if local else f"***@{domain}"


def _audit(event: str, **kwargs: object) -> None:
    entry = {"ts": datetime.now(timezone.utc).isoformat(), "event": event, **kwargs}
    audit_logger.warning(json.dumps(entry, default=str))


def log_login_success(email: str, ip: str) -> None:
    _audit("login_success", email=_redact_email(email), ip=ip)


def log_login_failed(email: str, reason: str, ip: str) -> None:
    _audit("login_failed", email=_redact_email(email), reason=reason, ip=ip)


def log_password_changed(user_id: str, ip: str) -> None:
    _audit("password_changed", user_id=user_id, ip=ip)


def log_password_reset_requested(ip: str) -> None:
    _audit("password_reset_requested", ip=ip)
