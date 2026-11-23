"""
Módulo: core/security_events.py (antes utils/audit_log.py)
¿Qué? Registro estructurado (JSON, una línea por evento) de eventos de seguridad:
      logins exitosos y fallidos (con el motivo), bloqueos por intentos, solicitud
      y cambio de contraseña y cierre de todas las sesiones. Enmascara el correo.
¿Para qué? Dejar rastro en los logs del servidor para detectar abuso (fuerza bruta,
           robo de cuentas) sin exponer datos personales. Ejemplo:
           docker compose logs be | grep '"event": "login_failed"'
¿Impacto? Es distinto de la auditoría de negocio (tabla audit_log, módulo de
          auditoría): esto va a los logs, aquella a la base de datos.
          Lo usa identity (AuthService) a través del puerto SecurityLog.
"""

import json
import logging
import sys
from datetime import datetime, timezone

audit_logger = logging.getLogger("security.audit")
audit_logger.setLevel(logging.INFO)
# Uvicorn no configura el logger raíz: sin un handler propio estos eventos no
# saldrían en `docker compose logs`. propagate=True deja que pytest (caplog) los vea.
if not audit_logger.handlers:
    _handler = logging.StreamHandler(sys.stderr)
    _handler.setFormatter(logging.Formatter("SECURITY %(message)s"))
    audit_logger.addHandler(_handler)


def _redact_email(email: str) -> str:
    local, _, domain = email.partition("@")
    return f"{local[0]}***@{domain}" if local else f"***@{domain}"


def _audit(event: str, **kwargs: object) -> None:
    entry = {"ts": datetime.now(timezone.utc).isoformat(), "event": event, **kwargs}
    audit_logger.info(json.dumps(entry, default=str))


def log_login_success(email: str, ip: str) -> None:
    _audit("login_success", email=_redact_email(email), ip=ip)


def log_login_failed(email: str, reason: str, ip: str) -> None:
    """reason: invalid_credentials | locked | account_disabled."""
    _audit("login_failed", email=_redact_email(email), reason=reason, ip=ip)


def log_login_locked(email: str, ip: str) -> None:
    _audit("login_locked", email=_redact_email(email), ip=ip)


def log_password_changed(user_id: str, ip: str) -> None:
    _audit("password_changed", user_id=user_id, ip=ip)


def log_password_reset_requested(ip: str) -> None:
    _audit("password_reset_requested", ip=ip)


def log_sessions_revoked(user_id: str) -> None:
    _audit("sessions_revoked", user_id=user_id)
