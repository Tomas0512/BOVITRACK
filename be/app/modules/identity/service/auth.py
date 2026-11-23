"""
Módulo: modules/identity/service/auth.py (casos de uso de autenticación)
¿Qué? Registro, login con bloqueo por intentos, renovación de tokens, recuperación
      de contraseña, verificación de correo, cierre de todas las sesiones y la
      validación del access token que usa get_current_user.
¿Para qué? Que las reglas de autenticación vivan en un solo lugar, sin HTTP ni SQL:
           lanza errores de dominio (AuthenticationError -> 401, etc.) y la frontera
           HTTP los traduce.
¿Impacto? El correo, la auditoría, el registro de eventos de seguridad y dónde se
          guardan los intentos de login llegan inyectados (puertos), así que el
          servicio se prueba sin servidor SMTP ni base de datos.
"""

import hashlib
import uuid
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Protocol

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.modules.identity.models import User
from app.modules.identity.schemas import ResetPasswordRequest, TokenResponse, UserCreate, UserLogin
from app.shared.exceptions import AuthenticationError, BusinessRuleError, PermissionDeniedError, TooManyAttemptsError
from app.shared.ports import AuditRecorder

# ── Mensajes del contrato (los mismos que recibía el frontend)
EMAIL_TAKEN = "El email ya está registrado"
DOCUMENT_TAKEN = "El número de documento ya está registrado"
INVALID_CREDENTIALS = "Credenciales inválidas"
ACCOUNT_DISABLED_LOGIN = "Cuenta desactivada. Contacte al administrador."
ACCOUNT_DISABLED = "Cuenta desactivada"
COULD_NOT_VALIDATE = "No se pudieron validar las credenciales"
INVALID_REFRESH = "Refresh token inválido o expirado"
TOKEN_WITHOUT_USER = "Token sin identificador de usuario"
USER_GONE = "Usuario no encontrado o cuenta desactivada"
RESET_TOKEN_INVALID = "Token de recuperación inválido"
RESET_TOKEN_USED = "Este token de recuperación ya fue utilizado"
RESET_TOKEN_EXPIRED = "El token de recuperación ha expirado. Solicite uno nuevo."
USER_NOT_FOUND = "Usuario no encontrado"
VERIFY_TOKEN_INVALID = "Token de verificación inválido"
VERIFY_TOKEN_EXPIRED = "Token de verificación expirado"

PASSWORD_RESET_TTL = timedelta(minutes=20)
EMAIL_VERIFICATION_TTL = timedelta(hours=24)

# Envía un correo con un token: (email, token). Implementación: app.core.email.
SendTokenEmail = Callable[[str, str], Awaitable[None]]


class UserStore(Protocol):
    """Lo que el servicio necesita del repositorio de usuarios."""

    def get(self, user_id: uuid.UUID) -> User | None: ...
    def get_by_email(self, email: str) -> User | None: ...
    def get_by_document(self, document_number: str) -> User | None: ...
    def add(self, user: User) -> None: ...
    def add_password_reset_token(self, user_id: uuid.UUID, token: str, expires_at: datetime) -> None: ...
    def get_password_reset_token(self, token: str) -> Any: ...
    def add_email_verification_token(self, user_id: uuid.UUID, token: str, expires_at: datetime) -> None: ...
    def get_email_verification_token(self, token: str) -> Any: ...
    def flush(self) -> None: ...
    def commit(self) -> None: ...
    def refresh(self, user: User) -> None: ...


def _now() -> datetime:
    return datetime.now(timezone.utc)


class AttemptStore(Protocol):
    """Dónde se guardan los intentos fallidos (llave = hash del correo).

    Implementación real: identity.repository.LoginAttemptRepository (tabla
    login_attempt, compartida por todos los procesos). En pruebas: MemoryAttemptStore.
    """

    def locked_until(self, key: str) -> datetime | None: ...
    def add_failure(self, key: str, now: datetime, window_start: datetime) -> int: ...
    def lock(self, key: str, until: datetime) -> None: ...
    def clear(self, key: str) -> None: ...


@dataclass
class _Attempts:
    failed: int = 0
    last_failed_at: datetime | None = None
    locked_until: datetime | None = None


class MemoryAttemptStore:
    """AttemptStore en memoria (pruebas): misma semántica que la tabla."""

    def __init__(self) -> None:
        self._rows: dict[str, _Attempts] = {}

    def locked_until(self, key: str) -> datetime | None:
        row = self._rows.get(key)
        return row.locked_until if row else None

    def add_failure(self, key: str, now: datetime, window_start: datetime) -> int:
        row = self._rows.setdefault(key, _Attempts())
        row.failed = 1 if row.last_failed_at is None or row.last_failed_at < window_start else row.failed + 1
        row.last_failed_at = now
        return row.failed

    def lock(self, key: str, until: datetime) -> None:
        row = self._rows.get(key)
        if row:
            row.locked_until, row.failed = until, 0

    def clear(self, key: str) -> None:
        self._rows.pop(key, None)


class SecurityLog(Protocol):
    """Registro de eventos de seguridad (logs del servidor). Implementación: app.core.security_events."""

    def log_login_success(self, email: str, ip: str) -> None: ...
    def log_login_failed(self, email: str, reason: str, ip: str) -> None: ...
    def log_login_locked(self, email: str, ip: str) -> None: ...
    def log_password_changed(self, user_id: str, ip: str) -> None: ...
    def log_password_reset_requested(self, ip: str) -> None: ...
    def log_sessions_revoked(self, user_id: str) -> None: ...


class _NoSecurityLog:
    """SecurityLog que no registra nada (pruebas que no lo necesitan)."""

    def __getattr__(self, _name: str) -> Callable[..., None]:
        return lambda *args, **kwargs: None


UNKNOWN_IP = "desconocida"


class LoginThrottle:
    """Bloqueo temporal por intentos fallidos de login, por correo.

    max_attempts fallos dentro de la ventana (lockout_minutes) bloquean ese correo
    lockout_minutes; un login correcto limpia la cuenta. Los intentos se guardan en
    el AttemptStore inyectado: con la tabla login_attempt el bloqueo sobrevive a
    reinicios y es el mismo para todos los procesos de la API.
    """

    def __init__(
        self,
        max_attempts: int = 5,
        lockout_minutes: int = 15,
        clock: Callable[[], datetime] = _now,
        store: AttemptStore | None = None,
    ) -> None:
        self.max_attempts = max_attempts
        self.lockout = timedelta(minutes=lockout_minutes)
        self._clock = clock
        self._store: AttemptStore = store if store is not None else MemoryAttemptStore()

    @staticmethod
    def key(email: str) -> str:
        """El correo nunca se guarda: solo su SHA-256."""
        return hashlib.sha256(email.lower().strip().encode()).hexdigest()

    def ensure_not_locked(self, email: str) -> None:
        now = self._clock()
        locked_until = self._store.locked_until(self.key(email))
        if locked_until and locked_until > now:
            remaining = int((locked_until - now).total_seconds() // 60) + 1
            raise TooManyAttemptsError(f"Demasiados intentos fallidos. Intente de nuevo en {remaining} minuto(s).")

    def register_failure(self, email: str) -> bool:
        """Cuenta un fallo. Devuelve True si con este fallo el correo quedó bloqueado."""
        now = self._clock()
        key = self.key(email)
        failed = self._store.add_failure(key, now, window_start=now - self.lockout)
        if failed >= self.max_attempts:
            self._store.lock(key, now + self.lockout)
            return True
        return False

    def reset(self, email: str) -> None:
        self._store.clear(self.key(email))


class AuthService:
    def __init__(
        self,
        users: UserStore,
        *,
        throttle: LoginThrottle,
        record_audit: AuditRecorder,
        send_password_reset: SendTokenEmail,
        send_email_verification: SendTokenEmail,
        security_log: SecurityLog | None = None,
    ) -> None:
        self._users = users
        self._security: SecurityLog = security_log if security_log is not None else _NoSecurityLog()
        self._throttle = throttle
        self._record_audit = record_audit
        self._send_password_reset = send_password_reset
        self._send_email_verification = send_email_verification

    # ── Registro y verificación de correo
    def register(self, data: UserCreate) -> User:
        """Crea la cuenta. Email y documento deben ser únicos; la contraseña se guarda hasheada."""
        email = data.email.lower().strip()
        if self._users.get_by_email(email):
            raise BusinessRuleError(EMAIL_TAKEN)
        if self._users.get_by_document(data.document_number.strip()):
            raise BusinessRuleError(DOCUMENT_TAKEN)

        now = _now()
        user = User(
            email=email,
            first_name=data.first_name.strip(),
            last_name=data.last_name.strip(),
            document_type=data.document_type.value,
            document_number=data.document_number.strip(),
            phone=data.phone.strip(),
            hashed_password=hash_password(data.password),
            accepted_terms=data.accept_terms,
            accepted_data_policy=data.accept_data_policy,
            accepted_terms_at=now if data.accept_terms else None,
            accepted_data_policy_at=now if data.accept_data_policy else None,
        )
        self._users.add(user)
        self._users.flush()  # inserta el usuario: la auditoría apunta a su id (FK)
        self._record_audit(user_id=str(user.id), action="register", entity="user",
                           entity_id=str(user.id), details={"email": user.email})
        self._users.commit()  # usuario + auditoría: una sola transacción
        self._users.refresh(user)
        return user

    async def send_verification_email(self, user_id: uuid.UUID) -> None:
        """Crea el token de verificación (24 h) y lo envía. Un usuario inexistente se ignora."""
        user = self._users.get(user_id)
        if not user:
            return
        token = str(uuid.uuid4())
        self._users.add_email_verification_token(user.id, token, _now() + EMAIL_VERIFICATION_TTL)
        self._users.commit()
        await self._send_email_verification(user.email, token)

    def verify_email(self, token: str) -> None:
        row = self._users.get_email_verification_token(token)
        if not row or row.used:
            raise BusinessRuleError(VERIFY_TOKEN_INVALID)
        if row.expires_at < _now():
            raise BusinessRuleError(VERIFY_TOKEN_EXPIRED)
        user = self._users.get(row.user_id)
        if not user:
            raise BusinessRuleError(USER_NOT_FOUND)
        user.email_verified = True
        row.used = True
        self._record_audit(user_id=str(user.id), action="email_verified", entity="user", entity_id=str(user.id))
        self._users.commit()

    # ── Sesión
    def login(self, credentials: UserLogin, ip: str = UNKNOWN_IP) -> TokenResponse:
        """Valida email y contraseña. 5 fallos en 15 minutos bloquean ese correo 15 minutos."""
        email = credentials.email.lower().strip()
        try:
            self._throttle.ensure_not_locked(email)
        except TooManyAttemptsError:
            self._security.log_login_failed(email, "locked", ip)
            raise

        user = self._users.get_by_email(email)
        if not user or not verify_password(credentials.password, user.hashed_password):
            self._security.log_login_failed(email, "invalid_credentials", ip)
            if self._throttle.register_failure(email):
                self._security.log_login_locked(email, ip)
            raise AuthenticationError(INVALID_CREDENTIALS)

        self._throttle.reset(email)
        if not user.is_active:
            self._security.log_login_failed(email, "account_disabled", ip)
            raise PermissionDeniedError(ACCOUNT_DISABLED_LOGIN)
        self._security.log_login_success(email, ip)
        return self._issue_tokens(user)

    def refresh(self, refresh_token: str) -> TokenResponse:
        """Nuevo par de tokens a partir de un refresh token vigente (misma versión de sesión)."""
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise AuthenticationError(INVALID_REFRESH)
        user_id = payload.get("sub")
        if not user_id:
            raise AuthenticationError(TOKEN_WITHOUT_USER)
        user = self._user_from_subject(user_id)
        if not user or not user.is_active:
            raise AuthenticationError(USER_GONE)
        version = payload.get("ver")
        if version is None or int(version) != int(user.token_version):
            raise AuthenticationError(INVALID_REFRESH)
        return self._issue_tokens(user)

    def authenticate(self, access_token: str) -> User:
        """Usuario dueño del access token (lo usa get_current_user en cada request)."""
        payload = decode_token(access_token)
        if not payload or payload.get("type") != "access":
            raise AuthenticationError(COULD_NOT_VALIDATE)
        user_id = payload.get("sub")
        version = payload.get("ver")
        if not user_id or version is None:
            raise AuthenticationError(COULD_NOT_VALIDATE)
        user = self._user_from_subject(user_id)
        if not user or int(version) != int(user.token_version):
            raise AuthenticationError(COULD_NOT_VALIDATE)
        if not user.is_active:
            raise PermissionDeniedError(ACCOUNT_DISABLED)
        return user

    def logout_all(self, user: User) -> None:
        """Invalida TODOS los tokens emitidos: sube la versión de sesión del usuario."""
        user.token_version += 1
        self._record_audit(user_id=str(user.id), action="logout_all_sessions", entity="user", entity_id=str(user.id))
        self._users.commit()
        self._security.log_sessions_revoked(str(user.id))

    # ── Recuperación de contraseña
    async def request_password_reset(self, email: str, ip: str = UNKNOWN_IP) -> None:
        """Siempre "funciona", exista o no el correo: así no se revela quién está registrado."""
        self._security.log_password_reset_requested(ip)
        user = self._users.get_by_email(email.lower().strip())
        if not user:
            return
        token = str(uuid.uuid4())
        self._users.add_password_reset_token(user.id, token, _now() + PASSWORD_RESET_TTL)
        self._users.commit()
        await self._send_password_reset(user.email, token)

    def reset_password(self, data: ResetPasswordRequest, ip: str = UNKNOWN_IP) -> None:
        record = self._users.get_password_reset_token(data.token)
        if not record:
            raise BusinessRuleError(RESET_TOKEN_INVALID)
        if record.used:
            raise BusinessRuleError(RESET_TOKEN_USED)
        if record.expires_at < _now():
            raise BusinessRuleError(RESET_TOKEN_EXPIRED)
        user = self._users.get(record.user_id)
        if not user:
            raise BusinessRuleError(USER_NOT_FOUND)
        user.hashed_password = hash_password(data.new_password)
        record.used = True
        self._record_audit(user_id=str(user.id), action="password_reset", entity="user", entity_id=str(user.id))
        self._users.commit()
        self._security.log_password_changed(str(user.id), ip)

    # ── Internos
    def _user_from_subject(self, subject: str) -> User | None:
        try:
            return self._users.get(uuid.UUID(subject))
        except ValueError:  # un "sub" que no es UUID: el token no lo emitimos nosotros
            return None

    @staticmethod
    def _issue_tokens(user: User) -> TokenResponse:
        claims = {"sub": str(user.id), "ver": user.token_version}
        return TokenResponse(access_token=create_access_token(data=claims), refresh_token=create_refresh_token(data=claims))
