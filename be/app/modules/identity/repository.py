"""
Módulo: modules/identity/repository.py (acceso a datos de identity)
¿Qué? Las consultas de usuarios, tokens de un solo uso, roles, permisos y membresías.
¿Para qué? Que los servicios no escriban SQL: piden "el usuario con este correo" o
           "el permiso del rol en este módulo" y no saben cómo se consulta.
¿Impacto? Las consultas de require_permission conservan su forma (membresía ->
          rol -> permiso), así que la regla de acceso no cambió al mudarse aquí.
"""

import uuid
from datetime import datetime

from collections.abc import Iterable
from typing import Any

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session, joinedload

from app.modules.identity.models import (
    EmailVerificationToken,
    PasswordResetToken,
    Permission,
    Role,
    User,
    UserFarm,
)

ADMIN_ROLE_NAME = "Administrador"


class UserRepository:
    """Usuarios y sus tokens de un solo uso (recuperación y verificación de correo)."""

    def __init__(self, db: Session) -> None:
        self._db = db

    # ── Usuarios
    def get(self, user_id: uuid.UUID) -> User | None:
        return self._db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()

    def get_by_email(self, email: str) -> User | None:
        return self._db.execute(select(User).where(User.email == email)).scalar_one_or_none()

    def get_by_document(self, document_number: str) -> User | None:
        return self._db.execute(select(User).where(User.document_number == document_number)).scalar_one_or_none()

    def email_of(self, user_id: uuid.UUID) -> str | None:
        """UserEmailLookup: correo del usuario, o None."""
        user = self._db.get(User, user_id)
        return user.email if user and user.email else None

    def add(self, user: User) -> None:
        self._db.add(user)

    # ── Tokens de un solo uso
    def add_password_reset_token(self, user_id: uuid.UUID, token: str, expires_at: datetime) -> None:
        self._db.add(PasswordResetToken(user_id=user_id, token=token, expires_at=expires_at))

    def get_password_reset_token(self, token: str) -> PasswordResetToken | None:
        stmt = select(PasswordResetToken).where(PasswordResetToken.token == token)
        return self._db.execute(stmt).scalar_one_or_none()

    def add_email_verification_token(self, user_id: uuid.UUID, token: str, expires_at: datetime) -> None:
        self._db.add(EmailVerificationToken(user_id=user_id, token=token, expires_at=expires_at))

    def get_email_verification_token(self, token: str) -> EmailVerificationToken | None:
        stmt = select(EmailVerificationToken).where(EmailVerificationToken.token == token)
        return self._db.execute(stmt).scalar_one_or_none()

    # ── Transacción
    def flush(self) -> None:
        self._db.flush()

    def commit(self) -> None:
        self._db.commit()

    def refresh(self, user: User) -> None:
        self._db.refresh(user)


class MembershipRepository:
    """Membresías usuario-finca, roles y la matriz de permisos."""

    def __init__(self, db: Session) -> None:
        self._db = db

    # ── Control de acceso (require_permission)
    def active_membership(self, user_id: uuid.UUID, farm_id: uuid.UUID) -> UserFarm | None:
        stmt = select(UserFarm).where(
            UserFarm.user_id == user_id,
            UserFarm.farm_id == farm_id,
            UserFarm.is_active.is_(True),
        )
        return self._db.execute(stmt).scalar_one_or_none()

    def role(self, role_id: uuid.UUID) -> Role | None:
        return self._db.get(Role, role_id)

    def permission(self, role_id: uuid.UUID, module: str) -> Permission | None:
        stmt = select(Permission).where(Permission.role_id == role_id, Permission.module == module)
        return self._db.execute(stmt).scalar_one_or_none()

    def has_permission_anywhere(self, user_id: uuid.UUID, module: str, action: str) -> bool:
        """¿Tiene el permiso en AL MENOS una finca donde es miembro activo?"""
        stmt = (
            select(Permission.id)
            .join(UserFarm, UserFarm.role_id == Permission.role_id)
            .where(
                UserFarm.user_id == user_id,
                UserFarm.is_active.is_(True),
                Permission.module == module,
                getattr(Permission, action).is_(True),
            )
            .limit(1)
        )
        return self._db.execute(stmt).scalar_one_or_none() is not None

    # ── Perfil y baja de cuenta
    def latest_role_name(self, user_id: uuid.UUID) -> str | None:
        """Nombre del rol de la membresía activa más reciente (rol activo)."""
        stmt = (
            select(Role.name)
            .join(UserFarm, UserFarm.role_id == Role.id)
            .where(UserFarm.user_id == user_id, UserFarm.is_active.is_(True), Role.is_active.is_(True))
            .order_by(UserFarm.assigned_at.desc())
            .limit(1)
        )
        return self._db.execute(stmt).scalar_one_or_none()

    def farms_where_last_admin(self, user_id: uuid.UUID) -> list[uuid.UUID]:
        """Fincas donde el usuario es el ÚNICO administrador activo."""
        admin_role = self._db.execute(select(Role).where(Role.name == ADMIN_ROLE_NAME)).scalar_one_or_none()
        if admin_role is None:
            return []
        my_admin_farms = self._db.execute(
            select(UserFarm.farm_id).where(
                UserFarm.user_id == user_id,
                UserFarm.role_id == admin_role.id,
                UserFarm.is_active.is_(True),
            )
        ).scalars().all()
        alone: list[uuid.UUID] = []
        for farm_id in my_admin_farms:
            other_admin = self._db.execute(
                select(UserFarm.id).where(
                    UserFarm.farm_id == farm_id,
                    UserFarm.role_id == admin_role.id,
                    UserFarm.is_active.is_(True),
                    UserFarm.user_id != user_id,
                )
            ).scalars().first()
            if other_admin is None:
                alone.append(farm_id)
        return alone

    # ── Puertos para otros módulos
    def grant_admin(self, user_id: uuid.UUID, farm_id: uuid.UUID) -> None:
        """MembershipGranter (farms): el creador de la finca queda como Administrador. Sin commit."""
        admin_role = self._db.execute(select(Role).where(Role.name == ADMIN_ROLE_NAME)).scalar_one_or_none()
        if admin_role is None:  # BD sin roles sembrados: igual que antes, no se asigna nada
            return
        self._db.add(UserFarm(user_id=user_id, farm_id=farm_id, role_id=admin_role.id, assigned_by=user_id))

    def active_farm_ids(self, user_id: uuid.UUID) -> list[uuid.UUID]:
        """MemberFarmIds (farms): fincas donde el usuario tiene membresía activa."""
        stmt = select(UserFarm.farm_id).where(UserFarm.user_id == user_id, UserFarm.is_active.is_(True))
        return list(self._db.execute(stmt).scalars().all())

    def is_member(self, farm_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """FarmMembershipCheck: ¿el usuario tiene una membresía ACTIVA en la finca?

        Un empleado desactivado en la finca no cuenta: no podría entrar a ella
        (require_permission le da 403), así que tampoco puede recibir tareas.
        """
        stmt = select(UserFarm.id).where(
            UserFarm.farm_id == farm_id,
            UserFarm.user_id == user_id,
            UserFarm.is_active.is_(True),
        )
        return self._db.execute(stmt).scalar_one_or_none() is not None

    def active_member_ids(self, farm_id: uuid.UUID) -> list[uuid.UUID]:
        """FarmMemberLookup: usuarios con membresía activa en la finca."""
        stmt = select(UserFarm.user_id).where(UserFarm.farm_id == farm_id, UserFarm.is_active.is_(True))
        return list(self._db.execute(stmt).scalars().all())

    def commit(self) -> None:
        self._db.commit()


class MembershipDirectory:
    """Lo que el módulo team necesita de identity para gestionar el equipo de una finca.

    team decide las REGLAS (último administrador, invitaciones, alcance del revisor);
    identity guarda y consulta los DATOS (usuarios, roles y membresías). Así team no
    escribe SQL sobre tablas ajenas. Ninguna operación hace commit: lo hace el caso
    de uso, sobre la misma sesión.
    """

    def __init__(self, db: Session) -> None:
        self._db = db

    # ── Usuarios
    def get_user(self, user_id: uuid.UUID) -> User | None:
        return self._db.get(User, user_id)

    def user_by_email(self, email: str) -> User | None:
        return self._db.execute(select(User).where(User.email == email)).scalar_one_or_none()

    def document_taken(self, document_number: str) -> bool:
        stmt = select(User.id).where(User.document_number == document_number)
        return self._db.execute(stmt).scalar_one_or_none() is not None

    def users_by_ids(self, user_ids: Iterable[uuid.UUID]) -> dict[uuid.UUID, User]:
        ids = list(user_ids)
        if not ids:
            return {}
        return {u.id: u for u in self._db.execute(select(User).where(User.id.in_(ids))).scalars().all()}

    def create_user(self, **fields: Any) -> User:
        """Crea el usuario (contraseña ya hasheada) y lo inserta para obtener su id."""
        user = User(**fields)
        self._db.add(user)
        self._db.flush()
        return user

    def set_account_active(self, user: User, active: bool) -> None:
        """Abre o cierra la cuenta. Cerrarla anula también las sesiones abiertas."""
        user.is_active = active
        if not active:
            user.token_version += 1

    # ── Roles
    def active_roles(self) -> list[Role]:
        stmt = select(Role).where(Role.is_active.is_(True)).order_by(Role.name.asc())
        return list(self._db.execute(stmt).scalars().all())

    def get_role(self, role_id: uuid.UUID) -> Role | None:
        return self._db.execute(select(Role).where(Role.id == role_id)).scalar_one_or_none()

    def admin_role_id(self) -> uuid.UUID | None:
        return self._db.execute(select(Role.id).where(Role.name == ADMIN_ROLE_NAME)).scalar_one_or_none()

    # ── Membresías
    def members(self, farm_id: uuid.UUID, *, is_active: bool | None = None) -> list[UserFarm]:
        """Membresías de la finca con su usuario y su rol cargados, las más recientes primero."""
        stmt = self._loaded().where(UserFarm.farm_id == farm_id)
        if is_active is not None:
            stmt = stmt.where(UserFarm.is_active.is_(is_active))
        return list(self._db.execute(stmt.order_by(UserFarm.assigned_at.desc())).scalars().all())

    def member(self, farm_id: uuid.UUID, user_id: uuid.UUID) -> UserFarm | None:
        """La membresía (activa o no) del usuario en la finca, con usuario y rol cargados."""
        stmt = self._loaded().where(UserFarm.user_id == user_id, UserFarm.farm_id == farm_id)
        return self._db.execute(stmt).scalar_one_or_none()

    def add_member(self, user_id: uuid.UUID, farm_id: uuid.UUID, role_id: uuid.UUID, assigned_by: uuid.UUID | None) -> None:
        self._db.add(UserFarm(user_id=user_id, farm_id=farm_id, role_id=role_id, assigned_by=assigned_by, is_active=True))

    def change_member(self, membership: UserFarm, *, role_id: uuid.UUID | None = None, is_active: bool | None = None) -> None:
        if role_id is not None:
            membership.role_id = role_id
        if is_active is not None:
            membership.is_active = is_active

    def remove_member(self, membership: UserFarm) -> None:
        self._db.delete(membership)

    def reload_member(self, membership: UserFarm) -> UserFarm:
        """Vuelve a leer la membresía (tras un commit) con su usuario y su rol actualizados."""
        return self._db.execute(self._loaded().where(UserFarm.id == membership.id)).scalar_one()

    def role_name_in_farm(self, user_id: uuid.UUID, farm_id: uuid.UUID) -> str | None:
        """Nombre del rol de la membresía ACTIVA del usuario en la finca."""
        stmt = (
            select(Role.name)
            .join(UserFarm, UserFarm.role_id == Role.id)
            .where(UserFarm.user_id == user_id, UserFarm.farm_id == farm_id, UserFarm.is_active.is_(True))
        )
        return self._db.execute(stmt).scalar_one_or_none()

    def count_other_active_admins(self, farm_id: uuid.UUID, admin_role_id: uuid.UUID, exclude_user_id: uuid.UUID) -> int:
        stmt = select(func.count()).select_from(UserFarm).where(
            UserFarm.farm_id == farm_id,
            UserFarm.role_id == admin_role_id,
            UserFarm.is_active.is_(True),
            UserFarm.user_id != exclude_user_id,
        )
        return int(self._db.execute(stmt).scalar_one())

    def count_other_active_farms(self, user_id: uuid.UUID, farm_id: uuid.UUID) -> int:
        """En cuántas OTRAS fincas tiene membresía activa (para advertir antes de cerrar su cuenta)."""
        stmt = select(func.count()).select_from(UserFarm).where(
            UserFarm.user_id == user_id, UserFarm.farm_id != farm_id, UserFarm.is_active.is_(True)
        )
        return int(self._db.execute(stmt).scalar_one())

    def administered_farm_ids(self, user_id: uuid.UUID) -> list[uuid.UUID]:
        """Fincas donde es Administrador con membresía activa y rol activo."""
        stmt = (
            select(UserFarm.farm_id)
            .join(Role, Role.id == UserFarm.role_id)
            .where(
                UserFarm.user_id == user_id,
                UserFarm.is_active.is_(True),
                Role.name == ADMIN_ROLE_NAME,
                Role.is_active.is_(True),
            )
        )
        return list(self._db.execute(stmt).scalars().all())

    def users_ever_in_farms(self, farm_ids: Iterable[uuid.UUID]) -> set[uuid.UUID]:
        """Usuarios con membresía (activa o no) en alguna de esas fincas."""
        ids = list(farm_ids)
        if not ids:
            return set()
        stmt = select(UserFarm.user_id).where(UserFarm.farm_id.in_(ids))
        return set(self._db.execute(stmt).scalars().all())

    def _loaded(self) -> Select[tuple[UserFarm]]:
        """Consulta base de membresías con usuario y rol cargados (sin N+1)."""
        return select(UserFarm).options(joinedload(UserFarm.user), joinedload(UserFarm.role))
