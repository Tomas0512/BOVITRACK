"""
Módulo: routers/bovines.py
¿Qué? Router de FastAPI para el CRUD de bovinos dentro de una finca.
¿Para qué? Exponer endpoints REST para crear, listar, consultar, actualizar
           y retirar bovinos desde el frontend o Swagger.
¿Impacto? Cada endpoint está protegido por get_current_user (JWT).
          Las rutas son anidadas bajo /farms/{farm_id}/bovines para
          asegurar que cada operación se haga dentro de la finca correcta.
"""

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.permissions import require_permission

from app.dependencies import get_current_user, get_db
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
    bovine = bovine_service.update_bovine(db, farm_id, bovine_id, data)
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
    bovine_service.delete_bovine(db, farm_id, bovine_id)
