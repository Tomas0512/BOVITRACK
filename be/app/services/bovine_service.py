"""
Módulo: services/bovine_service.py
¿Qué? Capa de servicio (lógica de negocio) para el módulo de bovinos.
¿Para qué? Separar la lógica de acceso a datos del router, facilitando
           testing y reutilización desde otros módulos.
¿Impacto? Toda operación CRUD de bovinos pasa por aquí antes de tocar la BD.
"""

import uuid
from typing import Sequence

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.bovine import Bovine
from app.schemas.bovine import BovineCreate, BovineUpdate


def create_bovine(db: Session, farm_id: uuid.UUID, data: BovineCreate, user_id: uuid.UUID) -> Bovine:
    """¿Qué? Crea un nuevo bovino asociado a una finca.
    ¿Para qué? Registrar un animal con todos sus datos de ingreso.
    ¿Impacto? registered_by se asigna automáticamente al usuario autenticado
              para mantener la trazabilidad.
    """
    bovine = Bovine(
        farm_id=farm_id,
        registered_by=user_id,
        **data.model_dump(),
    )
    db.add(bovine)
    db.commit()
    db.refresh(bovine)
    return bovine


def list_bovines(
    db: Session,
    farm_id: uuid.UUID,
    *,
    sex: str | None = None,
    status_filter: str | None = None,
    purpose: str | None = None,
) -> Sequence[Bovine]:
    """¿Qué? Lista los bovinos activos de una finca con filtros opcionales.
    ¿Para qué? Permitir al frontend filtrar por sexo, estado o propósito.
    ¿Impacto? Solo retorna bovinos activos (is_active=True) para excluir retirados.
    """
    stmt = select(Bovine).where(Bovine.farm_id == farm_id, Bovine.is_active.is_(True))
    if sex:
        stmt = stmt.where(Bovine.sex == sex)
    if status_filter:
        stmt = stmt.where(Bovine.status == status_filter)
    if purpose:
        stmt = stmt.where(Bovine.purpose == purpose)
    stmt = stmt.order_by(Bovine.created_at.desc())
    return db.execute(stmt).scalars().all()


def get_bovine(db: Session, farm_id: uuid.UUID, bovine_id: uuid.UUID) -> Bovine:
    """¿Qué? Obtiene un bovino por ID dentro de una finca específica.
    ¿Para qué? Consultar el detalle de un animal o validar que existe antes de operar.
    ¿Impacto? Lanza 404 si el bovino no existe o no pertenece a la finca,
              evitando acceso cruzado entre fincas.
    """
    stmt = select(Bovine).where(Bovine.id == bovine_id, Bovine.farm_id == farm_id)
    bovine = db.execute(stmt).scalar_one_or_none()
    if not bovine:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bovino no encontrado")
    return bovine


def update_bovine(db: Session, farm_id: uuid.UUID, bovine_id: uuid.UUID, data: BovineUpdate) -> Bovine:
    """¿Qué? Actualiza los campos enviados de un bovino (actualización parcial).
    ¿Para qué? Modificar peso, estado, potrero u observaciones sin reenviar todo.
    ¿Impacto? exclude_unset=True asegura que solo se modifiquen los campos presentes
              en la petición, sin sobrescribir los demás con None.
    """
    bovine = get_bovine(db, farm_id, bovine_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(bovine, field, value)
    db.commit()
    db.refresh(bovine)
    return bovine


def delete_bovine(db: Session, farm_id: uuid.UUID, bovine_id: uuid.UUID) -> None:
    """¿Qué? Desactiva un bovino (soft delete) y lo marca como 'retirado'.
    ¿Para qué? No eliminar físicamente para mantener el historial y auditoría.
    ¿Impacto? El bovino deja de aparecer en listados pero sus registros de
              tratamientos y producción se conservan.
    """
    bovine = get_bovine(db, farm_id, bovine_id)
    bovine.is_active = False
    bovine.status = "retirado"
    db.commit()
