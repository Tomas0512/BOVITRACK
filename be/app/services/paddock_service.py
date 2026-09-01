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
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.models.farm import LandPlot
from app.models.paddock import Paddock
from app.schemas.paddock import PaddockCreate, PaddockUpdate
from app.services.audit_service import add_audit_log


def _validate_land_plot(db: Session, farm_id: uuid.UUID, land_plot_id: uuid.UUID) -> LandPlot:
    """¿Qué? Comprueba que el lote existe, está activo y pertenece a la finca.
    ¿Para qué? Evitar potreros colgados de un lote de otra finca o inexistente.
    ¿Impacto? 422 si el lote no sirve; retorna el objeto para validar límites.
    """
    plot = db.execute(
        select(LandPlot).where(
            LandPlot.id == land_plot_id,
            LandPlot.farm_id == farm_id,
            LandPlot.is_active.is_(True),
        )
    ).scalar_one_or_none()
    if plot is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="El lote indicado no existe o no pertenece a esta finca.",
        )
    return plot


def _check_limits(plot: LandPlot, max_capacity: int, area_hectares) -> None:
    """¿Qué? Verifica que el potrero no supere la capacidad ni el área del lote.
    ¿Para qué? Evitar sobrepastoreo (más animales/área que el terreno soporta).
    ¿Impacto? 422 si el potrero excede el límite del lote.
    """
    if max_capacity is not None and max_capacity > plot.max_capacity:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"La capacidad del potrero no puede superar la del lote ({plot.max_capacity}).",
        )
    if area_hectares is not None and area_hectares > plot.area:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"El área del potrero no puede superar la del lote ({plot.area} {plot.area_unit}).",
        )


def create_paddock(db: Session, farm_id: uuid.UUID, data: PaddockCreate, user_id: uuid.UUID | None = None) -> Paddock:
    """¿Qué? Crea un nuevo potrero asociado a una finca.
    ¿Para qué? Registrar un área de pastoreo con capacidad y estado.
    ¿Impacto? El potrero estará disponible para asignar bovinos.
    """
    # El potrero pertenece a un lote concreto de ESTA finca (finca > lote > potrero).
    plot = _validate_land_plot(db, farm_id, data.land_plot_id)
    _check_limits(plot, data.max_capacity, data.area_hectares)

    paddock = Paddock(farm_id=farm_id, **data.model_dump())
    db.add(paddock)
    db.commit()
    db.refresh(paddock)
    add_audit_log(db, user_id=str(user_id) if user_id else None, farm_id=str(farm_id), action="create", entity="paddock", entity_id=str(paddock.id), details={"name": paddock.name})
    db.commit()
    return paddock


def list_paddocks(
    db: Session,
    farm_id: uuid.UUID,
    status_filter: str | None = None,
    land_plot_id: uuid.UUID | None = None,
) -> Sequence[Paddock]:
    """Lista los potreros activos de una finca, opcionalmente los de un solo lote.

    Se ordena por lote y luego por nombre para que la UI pueda agruparlos.
    """
    stmt = (
        select(Paddock)
        .options(joinedload(Paddock.land_plot))
        .join(LandPlot, LandPlot.id == Paddock.land_plot_id)
        .where(Paddock.farm_id == farm_id, Paddock.is_active.is_(True))
        .order_by(LandPlot.name.asc(), Paddock.name.asc())
    )
    if status_filter:
        stmt = stmt.where(Paddock.status == status_filter)
    if land_plot_id:
        stmt = stmt.where(Paddock.land_plot_id == land_plot_id)
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


def update_paddock(db: Session, farm_id: uuid.UUID, paddock_id: uuid.UUID, data: PaddockUpdate, user_id: uuid.UUID | None = None) -> Paddock:
    """¿Qué? Actualiza los campos enviados de un potrero.
    ¿Para qué? Cambiar estado (libre → ocupado → en_descanso), cobertura, fechas.
    ¿Impacto? Clave para la gestión de rotación de potreros.
    """
    paddock = get_paddock(db, farm_id, paddock_id)
    cambios = data.model_dump(exclude_unset=True)
    # Mover un potrero de lote es válido, pero el lote destino debe ser de la finca.
    plot_id = cambios.get("land_plot_id", paddock.land_plot_id)
    plot = _validate_land_plot(db, farm_id, plot_id)
    if "max_capacity" in cambios or "area_hectares" in cambios:
        _check_limits(
            plot,
            cambios.get("max_capacity", paddock.max_capacity),
            cambios.get("area_hectares", paddock.area_hectares),
        )
    for field, value in cambios.items():
        setattr(paddock, field, value)
    db.commit()
    db.refresh(paddock)
    add_audit_log(db, user_id=str(user_id) if user_id else None, farm_id=str(farm_id), action="update", entity="paddock", entity_id=str(paddock.id), details={"name": paddock.name, "status": paddock.status})
    db.commit()
    return paddock


def delete_paddock(db: Session, farm_id: uuid.UUID, paddock_id: uuid.UUID, user_id: uuid.UUID | None = None) -> None:
    """¿Qué? Desactiva un potrero (soft delete).
    ¿Para qué? No eliminar físicamente para conservar el historial de rotaciones.
    ¿Impacto? Los bovinos en rotaciones pasadas mantienen la referencia al potrero.
    """
    paddock = get_paddock(db, farm_id, paddock_id)

    # Un lote no puede quedarse sin potreros: es la misma regla que se aplica
    # al crearlo, sostenida en el tiempo.
    hermanos = db.execute(
        select(func.count())
        .select_from(Paddock)
        .where(
            Paddock.land_plot_id == paddock.land_plot_id,
            Paddock.is_active.is_(True),
            Paddock.id != paddock_id,
        )
    ).scalar_one()
    if hermanos == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede eliminar el único potrero del lote. Cree otro potrero primero o elimine el lote completo.",
        )

    paddock.is_active = False
    add_audit_log(db, user_id=str(user_id) if user_id else None, farm_id=str(farm_id), action="delete", entity="paddock", entity_id=str(paddock.id), details={"name": paddock.name})
    db.commit()
