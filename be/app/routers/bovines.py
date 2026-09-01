"""
Módulo: routers/bovines.py
¿Qué? Router de FastAPI para el CRUD de bovinos dentro de una finca.
¿Para qué? Exponer endpoints REST para crear, listar, consultar, actualizar
           y retirar bovinos desde el frontend o Swagger.
¿Impacto? Cada endpoint está protegido por get_current_user (JWT).
          Las rutas son anidadas bajo /farms/{farm_id}/bovines para
          asegurar que cada operación se haga dentro de la finca correcta.
"""

import csv
import io
import uuid
from decimal import Decimal

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from pydantic import ValidationError
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.permissions import require_permission

from app.dependencies import get_current_user, get_db
from app.models.farm import LandPlot
from app.models.paddock import Paddock
from app.models.user import User
from app.schemas.bovine import BovineCreate, BovineResponse, BovineUpdate
from app.services import bovine_service

router = APIRouter(prefix="/api/v1/farms/{farm_id}/bovines", tags=["Bovinos"])


@router.post("", response_model=BovineResponse, status_code=status.HTTP_201_CREATED, summary="Registrar bovino", dependencies=[Depends(require_permission("bovinos", "can_create"))])
def create(
    farm_id: uuid.UUID,
    data: BovineCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BovineResponse:
    """¿Qué? Registra un nuevo bovino en la finca.
    ¿Para qué? El registered_by se asigna automáticamente al usuario autenticado.
    ¿Impacto? Retorna 201 Created con el bovino completo.
    """
    bovine = bovine_service.create_bovine(db, farm_id, data, current_user.id)
    return BovineResponse.model_validate(bovine)


def _resolve_by_name(db: Session, farm_id: uuid.UUID, name: str | None, model) -> uuid.UUID | None:
    """¿Qué? Resuelve el id de un lote/potrero por nombre dentro de la finca.
    ¿Para qué? Permitir indicar 'land_plot' y 'paddock' por nombre en el CSV.
    ¿Impacto? Si el nombre no existe, se retorna None (la fila se valida luego).
    """
    if not name:
        return None
    row = db.execute(
        select(model.id).where(model.farm_id == farm_id, func.lower(model.name) == name.strip().lower())
    ).scalar_one_or_none()
    return row if row else None


@router.post(
    "/import",
    summary="Importar bovinos en lote (CSV)",
    description="Carga masiva de bovinos desde un archivo CSV. Columnas obligatorias: "
    "identification_number, sex, birth_date, entry_type, entry_date. Opcionales: name, breed, "
    "color, birth_weight, current_weight, purpose, land_plot, paddock.",
    dependencies=[Depends(require_permission("bovinos", "can_create"))],
)
def import_csv(
    farm_id: uuid.UUID,
    file: UploadFile = File(..., description="Archivo CSV (UTF-8)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """¿Qué? Lee un CSV, valida cada fila e importa los bovinos válidos.
    ¿Para qué? Cubrir el requisito de cargas masivas desde el desarrollo web.
    ¿Impacto? Retorna el resumen: importados, fallidos y errores por fila.
    """
    content = file.file.read().decode("utf-8-sig", errors="replace")
    reader = csv.DictReader(io.StringIO(content))
    if not reader.fieldnames:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El CSV no tiene cabeceras")
    headers = {h.strip().lower(): h for h in reader.fieldnames}

    rows: list[BovineCreate] = []
    raw_errors: list[dict] = []
    for idx, raw in enumerate(reader, start=2):
        get = lambda *names: next((raw[headers[n]].strip() for n in names if n in headers and (raw.get(headers[n]) or "")), "")  # noqa: E731
        try:
            payload = {
                "identification_number": get("identification_number", "id"),
                "sex": (get("sex") or "").lower(),
                "birth_date": get("birth_date", "birthdate"),
                "entry_type": (get("entry_type", "entrytype") or "").lower(),
                "entry_date": get("entry_date", "entrydate"),
            }
            opt_num = lambda col: (  # noqa: E731
                Decimal(get(col).replace(",", ".")) if get(col) else None
            )
            for field, col in (("name", "name"), ("breed", "breed"), ("color", "color"), ("purpose", "purpose"), ("observations", "observations")):
                v = get(col)
                if v:
                    payload[field] = v
            for field, col in (("birth_weight", "birth_weight"), ("current_weight", "current_weight")):
                v = get(col)
                if v:
                    payload[field] = opt_num(col)
            land_plot = get("land_plot", "landplot", "lote")
            paddock = get("paddock", "potrero")
            payload["land_plot_id"] = _resolve_by_name(db, farm_id, land_plot, LandPlot)
            payload["paddock_id"] = _resolve_by_name(db, farm_id, paddock, Paddock)
            rows.append(BovineCreate(**payload))
        except ValidationError as exc:
            raw_errors.append({"row": idx, "error": "; ".join(e["msg"] for e in exc.errors())[:200]})
        except Exception as exc:  # noqa: BLE001
            raw_errors.append({"row": idx, "error": f"Fila no válida: {exc}"})

    result = bovine_service.import_bovines(db, farm_id, rows, current_user.id)
    return {"total": len(rows), "imported": result["imported"], "failed": result["failed"], "errors": raw_errors + result["errors"]}



@router.get("", response_model=list[BovineResponse], summary="Listar bovinos de la finca", dependencies=[Depends(require_permission("bovinos", "can_read"))])
def list_all(
    farm_id: uuid.UUID,
    sex: str | None = Query(None),
    status_filter: str | None = Query(None, alias="status"),
    purpose: str | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[BovineResponse]:
    """¿Qué? Lista los bovinos activos con filtros opcionales por query string.
    ¿Para qué? Permitir al frontend filtrar por sexo, estado o propósito.
    ¿Impacto? El alias 'status' evita conflicto con la palabra reservada de Python.
    """
    _ = current_user
    bovines = bovine_service.list_bovines(db, farm_id, sex=sex, status_filter=status_filter, purpose=purpose)
    return [BovineResponse.model_validate(b) for b in bovines]


@router.get("/{bovine_id}", response_model=BovineResponse, summary="Obtener bovino por ID", dependencies=[Depends(require_permission("bovinos", "can_read"))])
def get_one(
    farm_id: uuid.UUID,
    bovine_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BovineResponse:
    """¿Qué? Retorna el detalle de un bovino específico.
    ¿Para qué? Ver ficha completa del animal, incluyendo genealogía y estado.
    ¿Impacto? Retorna 404 si el bovino no existe o no pertenece a la finca.
    """
    _ = current_user
    bovine = bovine_service.get_bovine(db, farm_id, bovine_id)
    return BovineResponse.model_validate(bovine)


@router.put("/{bovine_id}", response_model=BovineResponse, summary="Actualizar bovino", dependencies=[Depends(require_permission("bovinos", "can_update"))])
def update(
    farm_id: uuid.UUID,
    bovine_id: uuid.UUID,
    data: BovineUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BovineResponse:
    """¿Qué? Actualiza parcialmente un bovino (solo los campos enviados).
    ¿Para qué? Modificar peso, potrero, observaciones sin reenviar todo.
    ¿Impacto? Retorna 404 si el bovino no existe.
    """
    _ = current_user
    bovine = bovine_service.update_bovine(db, farm_id, bovine_id, data, current_user.id)
    return BovineResponse.model_validate(bovine)


@router.delete("/{bovine_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Retirar bovino (soft delete)", dependencies=[Depends(require_permission("bovinos", "can_delete"))])
def delete(
    farm_id: uuid.UUID,
    bovine_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """¿Qué? Desactiva un bovino y lo marca como 'retirado'.
    ¿Para qué? Mantener historial sin eliminar físicamente.
    ¿Impacto? Retorna 204 No Content. El bovino ya no aparece en listados.
    """
    _ = current_user
    bovine_service.delete_bovine(db, farm_id, bovine_id, current_user.id)
