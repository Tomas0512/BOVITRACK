"""
Módulo: services/paddock_service.py
¿Qué? Capa de servicio para el módulo de potreros.
¿Para qué? Gestionar el registro, actualización y rotación de potreros
           dentro de cada finca.
¿Impacto? La rotación de potreros es fundamental para la sostenibilidad
          ganadera, evitando sobrepastoreo y degradación del suelo.
"""

import uuid
from typing import Sequence

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.farm import LandPlot
from app.models.paddock import Paddock
from app.schemas.paddock import PaddockCreate, PaddockUpdate


def create_paddock(db: Session, farm_id: uuid.UUID, data: PaddockCreate) -> Paddock:
    """¿Qué? Crea un nuevo potrero asociado a una finca.
    ¿Para qué? Registrar un área de pastoreo con capacidad y estado.
    ¿Impacto? El potrero estará disponible para asignar bovinos.
    """
    # Require at least one active land plot before allowing paddock creation
    has_plot = db.execute(
        select(LandPlot.id)
        .where(LandPlot.farm_id == farm_id, LandPlot.is_active.is_(True))
        .limit(1)
    ).scalar_one_or_none()

    if has_plot is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Debe registrar al menos un lote antes de crear un potrero.",
        )

    paddock = Paddock(farm_id=farm_id, **data.model_dump())
    db.add(paddock)
    db.commit()
    db.refresh(paddock)
    return paddock


def list_paddocks(db: Session, farm_id: uuid.UUID, status_filter: str | None = None) -> Sequence[Paddock]:
    """Lista los potreros activos de una finca con filtro opcional por estado."""
    stmt = (
        select(Paddock)
        .where(Paddock.farm_id == farm_id, Paddock.is_active.is_(True))
        .order_by(Paddock.name.asc())
    )
    if status_filter:
        stmt = stmt.where(Paddock.status == status_filter)
    return db.execute(stmt).scalars().all()


def get_paddock(db: Session, farm_id: uuid.UUID, paddock_id: uuid.UUID) -> Paddock:
    """¿Qué? Obtiene un potrero por ID dentro de una finca.
    ¿Para qué? Consultar detalle o validar existencia antes de operar.
    ¿Impacto? Filtra por farm_id para evitar acceso cruzado entre fincas.
    """
    stmt = select(Paddock).where(Paddock.id == paddock_id, Paddock.farm_id == farm_id)
    paddock = db.execute(stmt).scalar_one_or_none()
    if not paddock:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Potrero no encontrado")
    return paddock


def update_paddock(db: Session, farm_id: uuid.UUID, paddock_id: uuid.UUID, data: PaddockUpdate) -> Paddock:
    """¿Qué? Actualiza los campos enviados de un potrero.
    ¿Para qué? Cambiar estado (libre → ocupado → en_descanso), cobertura, fechas.
    ¿Impacto? Clave para la gestión de rotación de potreros.
    """
    paddock = get_paddock(db, farm_id, paddock_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(paddock, field, value)
    db.commit()
    db.refresh(paddock)
    return paddock


def delete_paddock(db: Session, farm_id: uuid.UUID, paddock_id: uuid.UUID) -> None:
    """¿Qué? Desactiva un potrero (soft delete).
    ¿Para qué? No eliminar físicamente para conservar el historial de rotaciones.
    ¿Impacto? Los bovinos en rotaciones pasadas mantienen la referencia al potrero.
    """
    paddock = get_paddock(db, farm_id, paddock_id)
    paddock.is_active = False
    db.commit()
