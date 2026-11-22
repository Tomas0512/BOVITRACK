"""
Módulo: modules/team/service/employees.py (casos de uso: empleados de una finca)
¿Qué? Listar roles y empleados, cambiar el rol o el estado de un empleado en la
      finca, cerrar o abrir su CUENTA, y desvincularlo.
¿Para qué? Reglas del equipo sin HTTP ni SQL. La más importante: una finca nunca
           se queda sin un Administrador activo.
¿Impacto? Los datos (usuarios, roles, membresías) los guarda identity; este
          servicio los pide por el puerto TeamDirectory y decide qué se permite.
"""

import uuid
from typing import Any, Protocol

from app.modules.team.schemas import EmployeeResponse, EmployeeUpdate
from app.shared.exceptions import BusinessRuleError, NotFoundError, PermissionDeniedError
from app.shared.ports import AuditRecorder

ADMIN_ROLE_NAME = "Administrador"
EMPLOYEE_NOT_FOUND = "Empleado no encontrado en esta finca"
ROLE_NOT_FOUND = "Rol no encontrado"
LAST_ADMIN = "No se puede desvincular al último administrador activo de la finca. Asigne otro administrador primero."
LAST_ADMIN_ROLE = "No se puede quitar el rol Administrador al último administrador activo de la finca. Asigne otro administrador primero."
ONLY_ADMIN_CLOSES_ACCOUNTS = "Solo un administrador de la finca puede cambiar el estado de una cuenta."
OWN_ACCOUNT = "No puede desactivar su propia cuenta desde aquí. Use la opción de su perfil."


class TeamDirectory(Protocol):
    """Puerto hacia identity: usuarios, roles y membresías (implementación: identity.MembershipDirectory)."""

    def active_roles(self) -> list[Any]: ...
    def get_role(self, role_id: uuid.UUID) -> Any: ...
    def admin_role_id(self) -> uuid.UUID | None: ...
    def members(self, farm_id: uuid.UUID, *, is_active: bool | None = None) -> list[Any]: ...
    def member(self, farm_id: uuid.UUID, user_id: uuid.UUID) -> Any: ...
    def change_member(self, membership: Any, *, role_id: uuid.UUID | None = None, is_active: bool | None = None) -> None: ...
    def remove_member(self, membership: Any) -> None: ...
    def reload_member(self, membership: Any) -> Any: ...
    def role_name_in_farm(self, user_id: uuid.UUID, farm_id: uuid.UUID) -> str | None: ...
    def count_other_active_admins(self, farm_id: uuid.UUID, admin_role_id: uuid.UUID, exclude_user_id: uuid.UUID) -> int: ...
    def count_other_active_farms(self, user_id: uuid.UUID, farm_id: uuid.UUID) -> int: ...
    def set_account_active(self, user: Any, active: bool) -> None: ...


class Committer(Protocol):
    def commit(self) -> None: ...


class EmployeeService:
    def __init__(self, directory: TeamDirectory, transaction: Committer, *, record_audit: AuditRecorder) -> None:
        self._dir = directory
        self._tx = transaction
        self._record_audit = record_audit

    def roles(self) -> list[Any]:
        """Roles activos, para el select del formulario."""
        return self._dir.active_roles()

    def list(self, farm_id: uuid.UUID, *, is_active: bool | None = None) -> list[EmployeeResponse]:
        return [self._response(m, farm_id) for m in self._dir.members(farm_id, is_active=is_active)]

    def update(self, farm_id: uuid.UUID, user_id: uuid.UUID, data: EmployeeUpdate, updated_by: uuid.UUID | None = None) -> EmployeeResponse:
        """Cambia el rol o el estado del empleado EN ESTA finca (no toca su cuenta)."""
        membership = self._member(farm_id, user_id)
        if data.is_active is False:
            self._ensure_not_last_admin(farm_id, membership, LAST_ADMIN)
        if data.role_id is not None:
            if not self._dir.get_role(data.role_id):
                raise NotFoundError(ROLE_NOT_FOUND)
            if data.role_id != membership.role_id:  # bug #20: quitarle el rol al último admin
                self._ensure_not_last_admin(farm_id, membership, LAST_ADMIN_ROLE)
        self._dir.change_member(membership, role_id=data.role_id, is_active=data.is_active)
        self._record_audit(user_id=str(updated_by) if updated_by else None, farm_id=str(farm_id), action="update",
                           entity="employee", entity_id=str(user_id), details={"is_active": membership.is_active})
        self._tx.commit()
        return self._response(self._dir.reload_member(membership), farm_id)

    def set_account_status(
        self, farm_id: uuid.UUID, user_id: uuid.UUID, *, is_active: bool, reason: str | None, actor_id: uuid.UUID
    ) -> EmployeeResponse:
        """Abre o cierra la CUENTA (login en TODAS sus fincas). Solo un Administrador de la finca.

        Nadie cierra su propia cuenta por aquí (para eso está DELETE /users/me) ni la
        del último administrador activo de la finca.
        """
        if self._dir.role_name_in_farm(actor_id, farm_id) != ADMIN_ROLE_NAME:
            raise PermissionDeniedError(ONLY_ADMIN_CLOSES_ACCOUNTS)
        membership = self._member(farm_id, user_id)
        if not is_active:
            if membership.user_id == actor_id:
                raise BusinessRuleError(OWN_ACCOUNT)
            self._ensure_not_last_admin(farm_id, membership, LAST_ADMIN)

        user = membership.user
        if user.is_active == is_active:  # ya estaba así: nada que hacer
            return self._response(membership, farm_id)
        self._dir.set_account_active(user, is_active)
        self._record_audit(user_id=str(actor_id), farm_id=str(farm_id),
                           action="activate_account" if is_active else "deactivate_account",
                           entity="user", entity_id=str(user_id), details={"reason": reason} if reason else None)
        self._tx.commit()
        return self._response(self._dir.reload_member(membership), farm_id)

    def remove(self, farm_id: uuid.UUID, user_id: uuid.UUID, removed_by: uuid.UUID | None = None) -> None:
        """Desvincula al empleado de la finca (borra la membresía). Irreversible."""
        membership = self._member(farm_id, user_id)
        self._ensure_not_last_admin(farm_id, membership, LAST_ADMIN)
        self._record_audit(user_id=str(removed_by) if removed_by else None, farm_id=str(farm_id), action="remove",
                           entity="employee", entity_id=str(user_id))
        self._dir.remove_member(membership)
        self._tx.commit()

    # ── Reglas internas
    def _member(self, farm_id: uuid.UUID, user_id: uuid.UUID) -> Any:
        membership = self._dir.member(farm_id, user_id)
        if not membership:
            raise NotFoundError(EMPLOYEE_NOT_FOUND)
        return membership

    def _ensure_not_last_admin(self, farm_id: uuid.UUID, membership: Any, message: str) -> None:
        """Una finca nunca se queda sin Administrador activo."""
        admin_role_id = self._dir.admin_role_id()
        if admin_role_id is None or membership.role_id != admin_role_id:
            return
        if self._dir.count_other_active_admins(farm_id, admin_role_id, membership.user_id) == 0:
            raise BusinessRuleError(message)

    def _response(self, membership: Any, farm_id: uuid.UUID) -> EmployeeResponse:
        """Combina membresía + usuario + rol en la respuesta que muestra la UI."""
        user = membership.user
        return EmployeeResponse(
            id=membership.id,
            user_id=membership.user_id,
            farm_id=membership.farm_id,
            role_id=membership.role_id,
            role_name=membership.role.name,
            is_active=membership.is_active,
            account_active=user.is_active,
            other_farms_count=self._dir.count_other_active_farms(membership.user_id, farm_id),
            assigned_at=membership.assigned_at,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            document_type=user.document_type,
            document_number=user.document_number,
            phone=user.phone,
        )
