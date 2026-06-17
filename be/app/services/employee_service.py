"""
Módulo: services/employee_service.py
¿Qué? Capa de servicio para el módulo de empleados de una finca.
¿Para qué? Gestionar la asignación, listado, actualización y desvinculación
           de usuarios como empleados en una finca.
¿Impacto? Usa la tabla user_farm como tabla puente; los roles determinan
          qué puede hacer cada usuario dentro de la finca.
"""

import uuid
from typing import Sequence

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.farm import UserFarm
from app.models.role import Role
from app.models.user import User
from app.schemas.employee import EmployeeAssign, EmployeeResponse, EmployeeUpdate
from app.services.audit_service import add_audit_log


def list_roles(db: Session) -> Sequence[Role]:
    """¿Qué? Retorna todos los roles activos disponibles en el sistema.
    ¿Para qué? Poblar el select de roles en el formulario de asignación.
    """
    stmt = select(Role).where(Role.is_active.is_(True)).order_by(Role.name.asc())
    return db.execute(stmt).scalars().all()


def _build_response(uf: UserFarm) -> EmployeeResponse:
    """¿Qué? Construye un EmployeeResponse combinando UserFarm + User + Role.
    ¿Para qué? El schema de respuesta requiere datos de tres modelos distintos.
    """
    return EmployeeResponse(
        id=uf.id,
        user_id=uf.user_id,
        farm_id=uf.farm_id,
        role_id=uf.role_id,
        role_name=uf.role.name,
        is_active=uf.is_active,
        assigned_at=uf.assigned_at,
        first_name=uf.user.first_name,
        last_name=uf.user.last_name,
        email=uf.user.email,
        document_type=uf.user.document_type,
        document_number=uf.user.document_number,
        phone=uf.user.phone,
    )


def assign_employee(
    db: Session,
    farm_id: uuid.UUID,
    data: EmployeeAssign,
    assigned_by: uuid.UUID,
) -> EmployeeResponse:
    """¿Qué? Asigna un usuario (buscado por email) como empleado en la finca.
    ¿Para qué? Vincular un usuario registrado a la finca con un rol específico.
    ¿Impacto? Retorna 404 si el email no existe. Retorna 409 si ya está asignado.
    """
    user = db.execute(select(User).where(User.email == str(data.user_email))).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado con ese correo")

    role = db.execute(select(Role).where(Role.id == data.role_id)).scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rol no encontrado")

    existing = db.execute(
        select(UserFarm).where(UserFarm.user_id == user.id, UserFarm.farm_id == farm_id)
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El usuario ya está asignado a esta finca")

    uf = UserFarm(
        user_id=user.id,
        farm_id=farm_id,
        role_id=data.role_id,
        assigned_by=assigned_by,
        is_active=True,
    )
    db.add(uf)
    db.commit()
    db.refresh(uf)

    uf = db.execute(
        select(UserFarm)
        .options(joinedload(UserFarm.user), joinedload(UserFarm.role))
        .where(UserFarm.id == uf.id)
    ).scalar_one()
    return _build_response(uf)


def list_employees(
    db: Session,
    farm_id: uuid.UUID,
    *,
    is_active: bool | None = None,
) -> list[EmployeeResponse]:
    """¿Qué? Lista los empleados de una finca con filtro opcional de estado.
    ¿Para qué? Mostrar activos e inactivos por separado en la UI.
    ¿Impacto? Ordenados por apellido y nombre para visualización consistente.
    """
    stmt = (
        select(UserFarm)
        .options(joinedload(UserFarm.user), joinedload(UserFarm.role))
        .where(UserFarm.farm_id == farm_id)
    )
    if is_active is not None:
        stmt = stmt.where(UserFarm.is_active.is_(is_active))
    stmt = stmt.order_by(UserFarm.assigned_at.desc())
    user_farms = db.execute(stmt).scalars().all()
    return [_build_response(uf) for uf in user_farms]


def get_employee(db: Session, farm_id: uuid.UUID, user_id: uuid.UUID) -> UserFarm:
    """¿Qué? Obtiene la asignación de un usuario en la finca.
    ¿Para qué? Validar existencia antes de actualizar o eliminar.
    ¿Impacto? Retorna 404 si el usuario no está asignado a la finca.
    """
    stmt = (
        select(UserFarm)
        .options(joinedload(UserFarm.user), joinedload(UserFarm.role))
        .where(UserFarm.user_id == user_id, UserFarm.farm_id == farm_id)
    )
    uf = db.execute(stmt).scalar_one_or_none()
    if not uf:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empleado no encontrado en esta finca")
    return uf


def _last_admin_check(db: Session, farm_id: uuid.UUID, user_id: uuid.UUID) -> None:
    """¿Qué? Verifica que no se esté desactivando/eliminando al último administrador activo.
    ¿Para qué? Evitar que una finca se quede sin administradores.
    ¿Impacto? HTTP 400 si es el último admin activo de la finca.
    """
    admin_role = db.execute(select(Role).where(Role.name == "Administrador")).scalar_one_or_none()
    if not admin_role:
        return

    uf = get_employee(db, farm_id, user_id)
    if uf.role_id != admin_role.id:
        return

    other_admins = db.execute(
        select(UserFarm).where(
            UserFarm.farm_id == farm_id,
            UserFarm.role_id == admin_role.id,
            UserFarm.is_active.is_(True),
            UserFarm.user_id != user_id,
        )
    ).scalars().all()

    if len(other_admins) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede desvincular al último administrador activo de la finca. Asigne otro administrador primero.",
        )


def update_employee(
    db: Session,
    farm_id: uuid.UUID,
    user_id: uuid.UUID,
    data: EmployeeUpdate,
    updated_by: uuid.UUID | None = None,
) -> EmployeeResponse:
    """¿Qué? Actualiza el rol o el estado activo de un empleado en la finca.
    ¿Para qué? Cambiar de rol (ej: Empleado → Capataz) o activar/desactivar.
    ¿Impacto? Solo modifica los campos enviados.
    """
    uf = get_employee(db, farm_id, user_id)
    if data.is_active is not None and not data.is_active:
        _last_admin_check(db, farm_id, user_id)
    if data.role_id is not None:
        role = db.execute(select(Role).where(Role.id == data.role_id)).scalar_one_or_none()
        if not role:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rol no encontrado")
        uf.role_id = data.role_id
    if data.is_active is not None:
        uf.is_active = data.is_active
    db.commit()
    db.refresh(uf)

    uf = db.execute(
        select(UserFarm)
        .options(joinedload(UserFarm.user), joinedload(UserFarm.role))
        .where(UserFarm.id == uf.id)
    ).scalar_one()
    add_audit_log(db, user_id=str(updated_by) if updated_by else None, farm_id=str(farm_id), action="update", entity="employee", entity_id=str(user_id), details={"is_active": uf.is_active})
    db.commit()
    return _build_response(uf)


def remove_employee(db: Session, farm_id: uuid.UUID, user_id: uuid.UUID, removed_by: uuid.UUID | None = None) -> None:
    """¿Qué? Elimina la asignación de un empleado en la finca.
    ¿Para qué? Desvincular permanentemente a un usuario de la finca.
    ¿Impacto? La operación es irreversible. Para desactivar temporalmente usar update_employee.
    """
    _last_admin_check(db, farm_id, user_id)
    uf = get_employee(db, farm_id, user_id)
    add_audit_log(db, user_id=str(removed_by) if removed_by else None, farm_id=str(farm_id), action="remove", entity="employee", entity_id=str(user_id))
    db.delete(uf)
    db.commit()
