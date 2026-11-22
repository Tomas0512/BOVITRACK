"""
Módulo: modules/identity/service/access.py (control de acceso por rol, RBAC)
¿Qué? La regla que aplica require_permission: el usuario debe ser miembro activo
      de la finca, su rol debe estar activo y el rol debe tener la acción
      habilitada (can_create / can_read / can_update / can_delete) en el módulo.
¿Para qué? Que la regla de acceso de TODA la app esté en un solo lugar, sin FastAPI,
           y se pruebe sin levantar la API.
¿Impacto? Cada falla tiene su mensaje (403). Los mensajes son los mismos de antes.
"""

import uuid
from typing import Any, Protocol

from app.shared.exceptions import PermissionDeniedError

NO_FARM_ACCESS = "No tienes acceso a esta finca"
ROLE_DISABLED = "Tu rol está desactivado"


class AccessStore(Protocol):
    """Lo que la regla necesita leer: membresía, rol y permiso."""

    def active_membership(self, user_id: uuid.UUID, farm_id: uuid.UUID) -> Any: ...
    def role(self, role_id: uuid.UUID) -> Any: ...
    def permission(self, role_id: uuid.UUID, module: str) -> Any: ...
    def has_permission_anywhere(self, user_id: uuid.UUID, module: str, action: str) -> bool: ...


class AccessService:
    def __init__(self, store: AccessStore) -> None:
        self._store = store

    def check_permission(self, user_id: uuid.UUID, farm_id: uuid.UUID, module: str, action: str) -> None:
        """No devuelve nada si puede; lanza PermissionDeniedError con el motivo si no."""
        membership = self._store.active_membership(user_id, farm_id)
        if not membership:
            raise PermissionDeniedError(NO_FARM_ACCESS)

        role = self._store.role(membership.role_id)
        if role is None or not role.is_active:
            raise PermissionDeniedError(ROLE_DISABLED)

        permission = self._store.permission(membership.role_id, module)
        if not permission:
            raise PermissionDeniedError(f"Tu rol no tiene permisos para el módulo '{module}'")
        if not getattr(permission, action, False):
            raise PermissionDeniedError(f"No tienes permiso para '{action}' en '{module}'")

    def has_permission_anywhere(self, user_id: uuid.UUID, module: str, action: str) -> bool:
        """¿Tiene el permiso en al menos una de sus fincas? (pantallas sin farm_id, como la auditoría)."""
        return self._store.has_permission_anywhere(user_id, module, action)
