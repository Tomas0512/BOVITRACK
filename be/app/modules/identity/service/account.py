"""
Módulo: modules/identity/service/account.py (casos de uso de la cuenta propia)
¿Qué? El perfil del usuario autenticado (con su rol más reciente) y la baja de su cuenta.
¿Para qué? Antes era lógica escrita dentro del router de usuarios; ahora son reglas
           de negocio con nombre y con pruebas propias.
¿Impacto? "Eliminar" una cuenta es desactivarla (no se borra) e invalidar sus tokens.
          Nadie puede irse si deja una finca sin administrador.
"""

import uuid
from typing import Protocol

from app.modules.identity.models import User
from app.modules.identity.schemas import UserResponse
from app.shared.exceptions import BusinessRuleError
from app.shared.ports import AuditRecorder

DELETE_CONFIRMATION_WORD = "ELIMINAR"
MUST_CONFIRM = "Debe confirmar escribiendo ELIMINAR"
LAST_ADMIN = (
    "No puedes eliminar tu cuenta: eres el último administrador activo de una finca. "
    "Asigna otro administrador primero."
)


class AccountStore(Protocol):
    """Lo que el servicio necesita de las membresías."""

    def latest_role_name(self, user_id: uuid.UUID) -> str | None: ...
    def farms_where_last_admin(self, user_id: uuid.UUID) -> list[uuid.UUID]: ...
    def commit(self) -> None: ...


class AccountService:
    def __init__(self, memberships: AccountStore, *, record_audit: AuditRecorder) -> None:
        self._memberships = memberships
        self._record_audit = record_audit

    def profile(self, user: User) -> UserResponse:
        """Datos del usuario más el nombre del rol de su membresía activa más reciente."""
        payload = UserResponse.model_validate(user).model_dump()
        payload["role_name"] = self._memberships.latest_role_name(user.id)
        return UserResponse(**payload)

    def delete_account(self, user: User, confirmation_text: str) -> None:
        """Desactiva la cuenta propia. Exige escribir ELIMINAR y no ser el último admin de una finca."""
        if confirmation_text.strip().upper() != DELETE_CONFIRMATION_WORD:
            raise BusinessRuleError(MUST_CONFIRM)
        if self._memberships.farms_where_last_admin(user.id):
            raise BusinessRuleError(LAST_ADMIN)

        self._record_audit(user_id=str(user.id), action="delete_account", entity="user", entity_id=str(user.id))
        user.is_active = False
        user.token_version += 1  # cierra todas sus sesiones
        self._memberships.commit()
