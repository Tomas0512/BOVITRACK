"""Validador de alcance de finca para sub-recursos.

¿Qué? Comprueba que un `bovine_id` y/o `land_plot_id` pertenezcan a la finca.
¿Para qué? Evitar acceso cruzado (IDOR) al crear/actualizar registros que
           apuntan a animales o lotes de otras fincas.
¿Impacto? 400 si el recurso no pertenece a la finca indicada.
"""

import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.bovine import Bovine
from app.models.farm import Farm, LandPlot, UserFarm


def ensure_farm_scope(
    db: Session,
    farm_id: uuid.UUID,
    *,
    bovine_id: uuid.UUID | None = None,
    land_plot_id: uuid.UUID | None = None,
    member_user_id: uuid.UUID | None = None,
) -> None:
    """Valida que los sub-recursos indicados pertenezcan a la finca."""
    if bovine_id is not None:
        exists = db.execute(
            select(Bovine.id).where(Bovine.id == bovine_id, Bovine.farm_id == farm_id)
        ).scalar_one_or_none()
        if not exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El bovino indicado no existe en esta finca.",
            )
    if land_plot_id is not None:
        exists = db.execute(
            select(LandPlot.id).where(LandPlot.id == land_plot_id, LandPlot.farm_id == farm_id)
        ).scalar_one_or_none()
        if not exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El lote indicado no existe en esta finca.",
            )
    if member_user_id is not None and not _is_farm_member(db, farm_id, member_user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario asignado no pertenece a esta finca.",
        )


def _is_farm_member(db: Session, farm_id: uuid.UUID, user_id: uuid.UUID) -> bool:
    """¿El usuario es dueño o miembro de la finca?"""
    member = db.execute(
        select(UserFarm.id).where(UserFarm.farm_id == farm_id, UserFarm.user_id == user_id)
    ).scalar_one_or_none()
    if member:
        return True
    owner: uuid.UUID | None = db.execute(
        select(Farm.owner_id).where(Farm.id == farm_id)
    ).scalar_one_or_none()
    return owner is not None and owner == user_id
