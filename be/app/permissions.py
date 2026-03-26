"""
Módulo: permissions.py
¿Qué? Dependencia de FastAPI para validar permisos basados en roles (RBAC).
¿Para qué? Verificar que el usuario autenticado tenga permiso para ejecutar
           una operación específica (crear, leer, actualizar, eliminar) en un
           módulo específico (bovinos, tratamientos, etc.) dentro de una finca.
¿Impacto? Sin este módulo, cualquier usuario autenticado podría hacer
          cualquier operación en cualquier finca, sin restricciones de rol.

Uso en routers:
    from app.permissions import require_permission

    @router.post("", dependencies=[Depends(require_permission("bovinos", "can_create"))])
    def create_bovine(...):
        ...
"""

import uuid

from fastapi import Depends, HTTPException, Path, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.models.farm import UserFarm
from app.models.role import Permission
from app.models.user import User


def require_permission(module: str, action: str):
    """¿Qué? Factory que retorna una dependencia de FastAPI para validar permisos.
    ¿Para qué? Verificar que el usuario tenga el permiso 'action' en 'module'
               para la finca indicada en la URL (farm_id).
    ¿Impacto? Si el usuario no tiene permiso, retorna 403 Forbidden.
              Si no pertenece a la finca, retorna 403.

    Args:
        module: Nombre del módulo (ej: 'bovinos', 'tratamientos').
        action: Columna de permiso (ej: 'can_create', 'can_read').
    """

    def _check_permission(
        farm_id: uuid.UUID = Path(...),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ) -> User:
        """¿Qué? Dependency que se ejecuta antes del endpoint.
        ¿Para qué? Buscar la relación UserFarm → Role → Permission y validar.
        ¿Impacto? Retorna el usuario si tiene permiso, o lanza 403 si no.
        """
        # ¿Qué? Buscar la relación del usuario con la finca.
        # ¿Para qué? Un usuario solo puede operar en fincas donde está registrado.
        stmt = select(UserFarm).where(
            UserFarm.user_id == current_user.id,
            UserFarm.farm_id == farm_id,
            UserFarm.is_active.is_(True),
        )
        user_farm = db.execute(stmt).scalar_one_or_none()

        if not user_farm:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes acceso a esta finca",
            )

        # ¿Qué? Buscar el permiso del rol para el módulo solicitado.
        # ¿Para qué? Verificar si el rol tiene la acción habilitada.
        stmt = select(Permission).where(
            Permission.role_id == user_farm.role_id,
            Permission.module == module,
        )
        permission = db.execute(stmt).scalar_one_or_none()

        if not permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Tu rol no tiene permisos para el módulo '{module}'",
            )

        # ¿Qué? Verificar que la acción específica esté habilitada.
        # ¿Impacto? getattr(permission, "can_create") retorna True/False.
        if not getattr(permission, action, False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"No tienes permiso para '{action}' en '{module}'",
            )

        return current_user

    return _check_permission
