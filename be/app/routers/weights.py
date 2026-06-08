"""
Módulo: routers/weights.py
¿Qué? Router de FastAPI para el CRUD de pesajes de bovinos.
¿Para qué? Registrar el historial de pesos por animal y consultar la evolución
           para construir gráficos de crecimiento en el frontend.
¿Impacto? Las rutas están anidadas bajo /farms/{farm_id}/bovines/{bovine_id}/weights
          para asegurar que cada operación se haga en el contexto correcto de finca y animal.
"""

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.models.user import User
from app.permissions import require_permission
from app.schemas.weight import WeightCreate, WeightResponse
from app.services import weight_service

router = APIRouter(
    prefix="/api/v1/farms/{farm_id}/bovines/{bovine_id}/weights",
    tags=["Pesajes"],
)


@router.post(
    "",
    response_model=WeightResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar pesaje",
    dependencies=[Depends(require_permission("bovinos", "can_create"))],
)
def create(
    farm_id: uuid.UUID,
    bovine_id: uuid.UUID,
    data: WeightCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> WeightResponse:
    """¿Qué? Registra un nuevo pesaje para un bovino.
    ¿Para qué? Guardar el historial de pesos y calcular automáticamente
               la ganancia diaria respecto al pesaje anterior.
    ¿Impacto? Retorna 201 Created. Actualiza current_weight del bovino.
    """
    record = weight_service.create_weight(db, farm_id, bovine_id, data, current_user.id)
    return WeightResponse.model_validate(record)


@router.get(
    "",
    response_model=list[WeightResponse],
    summary="Historial de pesajes",
    dependencies=[Depends(require_permission("bovinos", "can_read"))],
)
def list_all(
    farm_id: uuid.UUID,
    bovine_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[WeightResponse]:
    """¿Qué? Lista el historial completo de pesajes de un bovino.
    ¿Para qué? Alimentar la tabla y el gráfico de evolución de peso en el frontend.
    ¿Impacto? Ordenados de más antiguo a más reciente para el gráfico de línea.
    """
    _ = current_user
    records = weight_service.list_weights(db, farm_id, bovine_id)
    return [WeightResponse.model_validate(r) for r in records]


@router.get(
    "/{weight_id}",
    response_model=WeightResponse,
    summary="Obtener pesaje por ID",
    dependencies=[Depends(require_permission("bovinos", "can_read"))],
)
def get_one(
    farm_id: uuid.UUID,
    bovine_id: uuid.UUID,
    weight_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> WeightResponse:
    """¿Qué? Retorna el detalle de un pesaje específico.
    ¿Para qué? Consultar un registro individual.
    ¿Impacto? Retorna 404 si no existe o no pertenece al bovino/finca.
    """
    _ = current_user
    record = weight_service.get_weight(db, farm_id, bovine_id, weight_id)
    return WeightResponse.model_validate(record)


@router.delete(
    "/{weight_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar pesaje",
    dependencies=[Depends(require_permission("bovinos", "can_delete"))],
)
def delete(
    farm_id: uuid.UUID,
    bovine_id: uuid.UUID,
    weight_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """¿Qué? Elimina un pesaje registrado por error.
    ¿Para qué? Corrección de datos incorrectos.
    ¿Impacto? Eliminación permanente. Retorna 204 No Content.
    """
    weight_service.delete_weight(db, farm_id, bovine_id, weight_id, current_user.id)
