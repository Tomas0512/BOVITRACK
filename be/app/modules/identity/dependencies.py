"""
Módulo: modules/identity/dependencies.py (composición del módulo y guards de la app)
¿Qué? Arma los servicios de identity y define las dos dependencias que protegen
      TODA la API:
        - get_current_user: quién hace la petición (access token -> usuario).
        - require_permission(module, action): si puede hacerla en la finca de la URL.
      También arma los puertos que identity ofrece a otros módulos.
¿Para qué? Los demás módulos toman estos guards por la API pública de identity
           (app.modules.identity), nunca de sus internos.
¿Impacto? identity es la capa base: no importa ningún otro módulo. Solo usa core
          (BD, seguridad, correo, rastro de auditoría) y shared.
"""

import uuid
from collections.abc import Callable
from functools import partial

from fastapi import Depends, Path
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core import security_events
from app.core.audit_trail import add_audit_log
from app.core.database import get_db
from app.core.email import send_email_verification, send_password_reset_email
from app.core.security import hash_password
from app.modules.identity.models import User
from app.modules.identity.repository import (
    LoginAttemptRepository,
    MembershipDirectory,
    MembershipRepository,
    UserRepository,
)
from app.modules.identity.service import AccessService, AccountService, AuthService, LoginThrottle
from app.shared.ports import FarmMemberLookup, FarmMembershipCheck, UserEmailLookup

# Extrae el token del header "Authorization: Bearer <token>".
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# Bloqueo de login: 5 fallos en 15 minutos bloquean ese correo 15 minutos. La cuenta
# vive en la tabla login_attempt, compartida por todos los procesos de la API.
LOGIN_MAX_ATTEMPTS = 5
LOGIN_LOCKOUT_MINUTES = 15


# ── Servicios
def build_auth_service(db: Session) -> AuthService:
    return AuthService(
        UserRepository(db),
        throttle=LoginThrottle(LOGIN_MAX_ATTEMPTS, LOGIN_LOCKOUT_MINUTES, store=LoginAttemptRepository(db)),
        record_audit=partial(add_audit_log, db),
        send_password_reset=send_password_reset_email,
        send_email_verification=send_email_verification,
        security_log=security_events,
    )


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    """Dependencia de FastAPI: un AuthService por request."""
    return build_auth_service(db)


def get_account_service(db: Session = Depends(get_db)) -> AccountService:
    """Dependencia de FastAPI: un AccountService por request."""
    return AccountService(MembershipRepository(db), record_audit=partial(add_audit_log, db))


# ── Guards (los usan TODOS los módulos)
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Usuario autenticado a partir del access token JWT.

    401 si el token es inválido, expiró, es de una sesión cerrada o el usuario no
    existe. 403 si la cuenta está desactivada.
    """
    return build_auth_service(db).authenticate(token)


def require_permission(module: str, action: str) -> Callable[..., User]:
    """Fábrica de dependencias: exige el permiso `action` en `module` para el farm_id de la URL.

    Uso:  @router.post("", dependencies=[Depends(require_permission("bovinos", "can_create"))])
    403 si no es miembro activo de la finca, su rol está desactivado o no tiene el permiso.
    """

    def _check_permission(
        farm_id: uuid.UUID = Path(...),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ) -> User:
        AccessService(MembershipRepository(db)).check_permission(current_user.id, farm_id, module, action)
        return current_user

    return _check_permission


# ── Puertos que identity ofrece a otros módulos
def has_permission_anywhere(db: Session, user_id: uuid.UUID, module: str, action: str) -> bool:
    """¿Tiene el permiso en al menos una finca? (audit: auditoría del sistema)."""
    return AccessService(MembershipRepository(db)).has_permission_anywhere(user_id, module, action)


def build_farm_member_lookup(db: Session) -> FarmMemberLookup:
    """FarmMemberLookup: miembros activos de una finca (notifications)."""
    return MembershipRepository(db).active_member_ids


def build_admin_granter(db: Session) -> Callable[[uuid.UUID, uuid.UUID], None]:
    """MembershipGranter (farms): deja al creador de una finca como Administrador."""
    return MembershipRepository(db).grant_admin


def build_member_farm_ids(db: Session) -> Callable[[uuid.UUID], list[uuid.UUID]]:
    """MemberFarmIds (farms): fincas donde el usuario es miembro activo."""
    return MembershipRepository(db).active_farm_ids


def build_membership_check(db: Session) -> FarmMembershipCheck:
    """FarmMembershipCheck: ¿el usuario es miembro ACTIVO de la finca? (tasks: a quién se asigna)."""
    return MembershipRepository(db).is_member


def build_user_email_lookup(db: Session) -> UserEmailLookup:
    """UserEmailLookup: correo de un usuario (notifications)."""
    return UserRepository(db).email_of


def build_membership_directory(db: Session) -> MembershipDirectory:
    """Usuarios, roles y membresías para gestionar el equipo de una finca (team)."""
    return MembershipDirectory(db)


def build_password_hasher() -> Callable[[str], str]:
    """Hashea una contraseña con el mismo algoritmo del registro (team: registro por invitación)."""
    return hash_password
