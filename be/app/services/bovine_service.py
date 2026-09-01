"""
Módulo: services/bovine_service.py
¿Qué? Capa de servicio (lógica de negocio) para el módulo de bovinos.
¿Para qué? Separar la lógica de acceso a datos del router, facilitando
           testing y reutilización desde otros módulos.
¿Impacto? Toda operación CRUD de bovinos pasa por aquí antes de tocar la BD.
"""

import uuid
from datetime import date
from typing import Sequence

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.bovine import Bovine
from app.models.farm import LandPlot
from app.models.paddock import Paddock
from app.schemas.bovine import BovineCreate, BovineUpdate
from app.services.audit_service import add_audit_log
from app.utils.validators import ensure_farm_scope


def _validate_paddock(db: Session, farm_id: uuid.UUID, paddock_id: uuid.UUID) -> Paddock:
    """¿Qué? Comprueba que el potrero existe y pertenece a la finca.
    ¿Para qué? Evitar asignar un bovino a un potrero de otra finca.
    ¿Impacto? 400 si el potrero no es válido para esta finca.
    """
    paddock = db.execute(
        select(Paddock).where(
            Paddock.id == paddock_id,
            Paddock.farm_id == farm_id,
            Paddock.is_active.is_(True),
        )
    ).scalar_one_or_none()
    if not paddock:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El potrero indicado no existe en esta finca",
        )
    return paddock


def create_bovine(db: Session, farm_id: uuid.UUID, data: BovineCreate, user_id: uuid.UUID) -> Bovine:
    """¿Qué? Crea un nuevo bovino asociado a una finca.
    ¿Para qué? Registrar un animal con todos sus datos de ingreso.
    ¿Impacto? registered_by se asigna automáticamente al usuario autenticado
              para mantener la trazabilidad.
    """
    # ¿Qué? Validar unicidad del número de identificación dentro de la finca.
    dup = db.execute(
        select(Bovine).where(
            Bovine.farm_id == farm_id,
            Bovine.identification_number == data.identification_number,
        )
    ).scalar_one_or_none()
    if dup:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un bovino con esa identificación en la finca",
        )

    # ¿Qué? Validar que padre/madre pertenezcan a la finca.
    for ref in (data.father_id, data.mother_id):
        if ref:
            ref_bovine = db.execute(
                select(Bovine).where(Bovine.id == ref, Bovine.farm_id == farm_id)
            ).scalar_one_or_none()
            if not ref_bovine:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El bovino padre/madre indicado no existe en esta finca",
                )

    # ¿Qué? Validar que el lote indicado pertenezca a la finca.
    if data.land_plot_id:
        land_plot = db.execute(
            select(LandPlot).where(
                LandPlot.id == data.land_plot_id,
                LandPlot.farm_id == farm_id,
            )
        ).scalar_one_or_none()
        if not land_plot:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El lote indicado no existe en esta finca",
            )

    # ¿Qué? Validar que el potrero indicado pertenezca a la finca y sea coherente con el lote.
    data_dict = data.model_dump()
    if data.paddock_id:
        paddock = _validate_paddock(db, farm_id, data.paddock_id)
        if data.land_plot_id and paddock.land_plot_id != data.land_plot_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El potrero indicado pertenece a otro lote.",
            )
        if not data.land_plot_id:
            data_dict["land_plot_id"] = paddock.land_plot_id

    bovine = Bovine(
        farm_id=farm_id,
        registered_by=user_id,
        **data_dict,
    )
    db.add(bovine)
    db.commit()
    db.refresh(bovine)
    add_audit_log(db, user_id=str(user_id), farm_id=str(farm_id), action="create", entity="bovine", entity_id=str(bovine.id), details={"tag": bovine.identification_number})
    db.commit()
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


def update_bovine(db: Session, farm_id: uuid.UUID, bovine_id: uuid.UUID, data: BovineUpdate, user_id: uuid.UUID | None = None) -> Bovine:
    """¿Qué? Actualiza los campos enviados de un bovino (actualización parcial).
    ¿Para qué? Modificar peso, estado, potrero u observaciones sin reenviar todo.
    ¿Impacto? exclude_unset=True asegura que solo se modifiquen los campos presentes
              en la petición, sin sobrescribir los demás con None.
    """
    bovine = get_bovine(db, farm_id, bovine_id)
    cambios = data.model_dump(exclude_unset=True)

    # ¿Qué? Unicidad del número de identificación dentro de la finca (no 500).
    new_ident = cambios.get("identification_number")
    if new_ident:
        dup = db.execute(
            select(Bovine).where(
                Bovine.farm_id == farm_id,
                Bovine.identification_number == new_ident,
                Bovine.id != bovine_id,
            )
        ).scalar_one_or_none()
        if dup:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe un bovino con esa identificación en la finca",
            )

    # ¿Qué? Validar pertenencia a la finca de las referencias nuevas.
    if cambios.get("land_plot_id") is not None:
        ensure_farm_scope(db, farm_id, land_plot_id=cambios["land_plot_id"])
    if cambios.get("father_id") is not None:
        ensure_farm_scope(db, farm_id, bovine_id=cambios["father_id"])
    if cambios.get("mother_id") is not None:
        ensure_farm_scope(db, farm_id, bovine_id=cambios["mother_id"])

    # ¿Qué? Coherencia jerárquica lote ↔ potrero (finca > lote > potrero).
    final_land = cambios["land_plot_id"] if "land_plot_id" in cambios else bovine.land_plot_id
    final_pad = cambios["paddock_id"] if "paddock_id" in cambios else bovine.paddock_id
    if final_pad:
        paddock = _validate_paddock(db, farm_id, final_pad)
        if final_land is not None and paddock.land_plot_id != final_land:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El potrero indicado pertenece a otro lote.",
            )
        if final_land is None:
            cambios["land_plot_id"] = paddock.land_plot_id

    for field, value in cambios.items():
        setattr(bovine, field, value)
    db.commit()
    db.refresh(bovine)
    add_audit_log(db, user_id=str(user_id) if user_id else None, farm_id=str(farm_id), action="update", entity="bovine", entity_id=str(bovine.id), details={"tag": bovine.identification_number})
    db.commit()
    return bovine


def delete_bovine(db: Session, farm_id: uuid.UUID, bovine_id: uuid.UUID, user_id: uuid.UUID | None = None) -> None:
    """¿Qué? Desactiva un bovino (soft delete) y lo marca como 'retirado'.
    ¿Para qué? No eliminar físicamente para mantener el historial y auditoría.
    ¿Impacto? El bovino deja de aparecer en listados pero sus registros de
              tratamientos y producción se conservan.
    """
    bovine = get_bovine(db, farm_id, bovine_id)
    bovine.is_active = False
    bovine.status = "retirado"
    bovine.exit_date = date.today()
    bovine.exit_reason = "retirado"
    add_audit_log(db, user_id=str(user_id) if user_id else None, farm_id=str(farm_id), action="delete", entity="bovine", entity_id=str(bovine.id), details={"tag": bovine.identification_number})
    db.commit()


def import_bovines(db: Session, farm_id: uuid.UUID, rows: list[BovineCreate], user_id: uuid.UUID) -> dict:
    """¿Qué? Importa en lote varios bovinos reutilizando create_bovine.
    ¿Para qué? Cubrir el requisito de "cargas masivas" (checklist) sin duplicar
               la lógica de validación/auditoría.
    ¿Impacto? Los registros válidos se guardan; los inválidos se reportan con
              su número de fila para que el usuario corrija el CSV. El proceso
              no se aborta por una fila errónea (registro parcial con reporte).
    """
    imported = 0
    errors: list[dict] = []
    for idx, data in enumerate(rows, start=2):
        try:
            create_bovine(db, farm_id, data, user_id)
            imported += 1
        except HTTPException as exc:
            errors.append({"row": idx, "error": str(exc.detail)})
        except Exception as exc:  # noqa: BLE001 - reporte por fila, no abortar
            errors.append({"row": idx, "error": f"Error inesperado: {exc}"})
    return {"imported": imported, "failed": len(errors), "errors": errors}
