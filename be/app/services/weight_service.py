"""
Módulo: services/weight_service.py
¿Qué? Capa de servicio para el módulo de pesajes de bovinos.
¿Para qué? Registrar pesajes históricos, calcular automáticamente la ganancia
           diaria respecto al pesaje anterior, y actualizar el peso actual del bovino.
¿Impacto? Sin este servicio, el historial de pesos no existiría y el frontend
          no podría graficar la evolución de cada animal.
"""

import uuid
from decimal import Decimal
from typing import Sequence

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.bovine import Bovine
from app.models.weight import Weight
from app.schemas.weight import WeightCreate
from app.services.audit_service import add_audit_log


def _get_bovine_or_404(db: Session, farm_id: uuid.UUID, bovine_id: uuid.UUID) -> Bovine:
    """¿Qué? Busca un bovino validando que pertenezca a la finca.
    ¿Para qué? Evitar que un usuario acceda a bovinos de otras fincas.
    ¿Impacto? Lanza 404 si no existe o no pertenece a la finca indicada.
    """
    stmt = select(Bovine).where(
        Bovine.id == bovine_id,
        Bovine.farm_id == farm_id,
        Bovine.is_active.is_(True),
    )
    bovine = db.execute(stmt).scalar_one_or_none()
    if not bovine:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bovino no encontrado en esta finca.")
    return bovine


def _calculate_daily_gain(
    db: Session,
    bovine_id: uuid.UUID,
    new_weight: Decimal,
    measured_at,
) -> Decimal | None:
    """¿Qué? Calcula la ganancia diaria de peso respecto al pesaje anterior.
    ¿Para qué? Indicador clave de productividad: cuántos kg gana el animal por día.
    ¿Impacto? Si no hay pesaje anterior retorna None. Si los días entre pesajes
              es 0 (misma fecha) retorna None para evitar división por cero.
    Formula: (peso_nuevo - peso_anterior) / días_entre_pesajes
    """
    stmt = (
        select(Weight)
        .where(
            Weight.bovine_id == bovine_id,
            Weight.measured_at < measured_at,
        )
        .order_by(Weight.measured_at.desc())
        .limit(1)
    )
    previous = db.execute(stmt).scalar_one_or_none()
    if not previous:
        return None
    days = (measured_at - previous.measured_at).days
    if days <= 0:
        return None
    return round((new_weight - previous.weight_kg) / Decimal(days), 2)


def create_weight(
    db: Session,
    farm_id: uuid.UUID,
    bovine_id: uuid.UUID,
    data: WeightCreate,
    user_id: uuid.UUID,
) -> Weight:
    """¿Qué? Registra un nuevo pesaje para un bovino.
    ¿Para qué? Guardar el historial de pesos y mantener current_weight actualizado.
    ¿Impacto? Calcula ganancia diaria automáticamente y actualiza el campo
              current_weight del bovino con el nuevo valor registrado.
    """
    bovine = _get_bovine_or_404(db, farm_id, bovine_id)

    daily_gain = _calculate_daily_gain(db, bovine_id, data.weight_kg, data.measured_at)

    record = Weight(
        farm_id=farm_id,
        bovine_id=bovine_id,
        registered_by=user_id,
        daily_gain=daily_gain,
        **data.model_dump(),
    )
    db.add(record)

    # ¿Qué? Actualizar current_weight solo si este pesaje es el más reciente.
    # ¿Para qué? Evitar sobrescribir el peso con un valor atrasado.
    latest_stmt = (
        select(Weight.measured_at)
        .where(Weight.bovine_id == bovine_id)
        .order_by(Weight.measured_at.desc())
        .limit(1)
    )
    latest = db.execute(latest_stmt).scalar_one_or_none()
    if latest is None or data.measured_at >= latest:
        bovine.current_weight = data.weight_kg

    db.commit()
    db.refresh(record)

    add_audit_log(
        db,
        user_id=str(user_id),
        farm_id=str(farm_id),
        action="create",
        entity="weight",
        entity_id=str(record.id),
        details={"bovine_id": str(bovine_id), "weight_kg": str(data.weight_kg)},
    )
    db.commit()
    return record


def list_weights(
    db: Session,
    farm_id: uuid.UUID,
    bovine_id: uuid.UUID,
) -> Sequence[Weight]:
    """¿Qué? Lista el historial completo de pesajes de un bovino.
    ¿Para qué? Permitir al frontend construir la tabla y el gráfico de evolución.
    ¿Impacto? Ordenados de más antiguo a más reciente para que el gráfico
              muestre la línea de tiempo correctamente.
    """
    _get_bovine_or_404(db, farm_id, bovine_id)
    stmt = (
        select(Weight)
        .where(
            Weight.farm_id == farm_id,
            Weight.bovine_id == bovine_id,
        )
        .order_by(Weight.measured_at.asc())
    )
    return db.execute(stmt).scalars().all()


def get_weight(
    db: Session,
    farm_id: uuid.UUID,
    bovine_id: uuid.UUID,
    weight_id: uuid.UUID,
) -> Weight:
    """¿Qué? Obtiene un pesaje específico por ID.
    ¿Para qué? Consultar detalle o validar existencia antes de eliminar.
    ¿Impacto? Filtra por farm_id y bovine_id para seguridad entre fincas.
    """
    stmt = select(Weight).where(
        Weight.id == weight_id,
        Weight.farm_id == farm_id,
        Weight.bovine_id == bovine_id,
    )
    record = db.execute(stmt).scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pesaje no encontrado.")
    return record


def delete_weight(
    db: Session,
    farm_id: uuid.UUID,
    bovine_id: uuid.UUID,
    weight_id: uuid.UUID,
    user_id: uuid.UUID,
) -> None:
    """¿Qué? Elimina un pesaje por ID.
    ¿Para qué? Corregir registros erróneos.
    ¿Impacto? No recalcula current_weight automáticamente — el frontend
              debe notificar al usuario que revise el peso actual del bovino.
    """
    record = get_weight(db, farm_id, bovine_id, weight_id)
    db.delete(record)
    add_audit_log(
        db,
        user_id=str(user_id),
        farm_id=str(farm_id),
        action="delete",
        entity="weight",
        entity_id=str(weight_id),
        details={"bovine_id": str(bovine_id)},
    )
    db.commit()
