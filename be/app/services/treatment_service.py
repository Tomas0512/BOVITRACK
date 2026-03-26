"""
Módulo: services/treatment_service.py
¿Qué? Capa de servicio para el módulo de tratamientos sanitarios.
¿Para qué? Gestionar el registro y consulta de tratamientos aplicados
           a bovinos o potreros completos.
¿Impacto? La trazabilidad sanitaria es obligatoria para el ICA.
          Sin este servicio, no habría forma de registrar vacunaciones,
          desparasitaciones ni tratamientos veterinarios.
"""

import uuid
from typing import Sequence

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.treatment import Treatment
from app.schemas.treatment import TreatmentCreate


def create_treatment(db: Session, farm_id: uuid.UUID, data: TreatmentCreate, user_id: uuid.UUID) -> Treatment:
    """¿Qué? Registra un nuevo tratamiento sanitario.
    ¿Para qué? Vincular un tratamiento a la finca y al usuario que lo aplicó.
    ¿Impacto? applied_by permite auditar quién realizó cada tratamiento.
    """
    treatment = Treatment(
        farm_id=farm_id,
        applied_by=user_id,
        **data.model_dump(),
    )
    db.add(treatment)
    db.commit()
    db.refresh(treatment)
    return treatment


def list_treatments(db: Session, farm_id: uuid.UUID, bovine_id: uuid.UUID | None = None) -> Sequence[Treatment]:
    """¿Qué? Lista los tratamientos de una finca, con filtro opcional por bovino.
    ¿Para qué? Consultar el historial sanitario completo o de un animal específico.
    ¿Impacto? Ordenados por fecha de aplicación descendente (más reciente primero).
    """
    stmt = select(Treatment).where(Treatment.farm_id == farm_id)
    if bovine_id:
        stmt = stmt.where(Treatment.bovine_id == bovine_id)
    stmt = stmt.order_by(Treatment.application_date.desc())
    return db.execute(stmt).scalars().all()


def get_treatment(db: Session, farm_id: uuid.UUID, treatment_id: uuid.UUID) -> Treatment:
    """¿Qué? Obtiene un tratamiento por ID dentro de una finca.
    ¿Para qué? Consultar detalle o validar existencia antes de eliminar.
    ¿Impacto? Filtra por farm_id para evitar acceso cruzado entre fincas.
    """
    stmt = select(Treatment).where(Treatment.id == treatment_id, Treatment.farm_id == farm_id)
    treatment = db.execute(stmt).scalar_one_or_none()
    if not treatment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tratamiento no encontrado")
    return treatment


def delete_treatment(db: Session, farm_id: uuid.UUID, treatment_id: uuid.UUID) -> None:
    """¿Qué? Elimina físicamente un tratamiento de la base de datos.
    ¿Para qué? En caso de registro erróneo. No usa soft delete porque
              los tratamientos no tienen dependencias como los bovinos.
    ¿Impacto? La eliminación es permanente — no se puede deshacer.
    """
    treatment = get_treatment(db, farm_id, treatment_id)
    db.delete(treatment)
    db.commit()
