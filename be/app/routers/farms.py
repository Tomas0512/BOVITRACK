import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.permissions import require_permission
from app.models.department import Department
from app.models.purpose import Purpose
from app.models.user import User
from app.schemas.farm import (
    DepartmentOption,
    FarmBulkCreateRequest,
    FarmCreate,
    FarmResponse,
    FarmUpdate,
    PurposeOption,
)
from app.services import farm_service

router = APIRouter(prefix="/api/v1/farms", tags=["Fincas"])


@router.get(
    "/departments",
    response_model=list[DepartmentOption],
    summary="Listar departamentos",
)
def list_departments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[DepartmentOption]:
    """Retorna catálogo de departamentos para formularios."""
    _ = current_user
    departments = db.execute(select(Department).order_by(Department.name.asc())).scalars().all()
    return [DepartmentOption.model_validate(d) for d in departments]


@router.get(
    "/purposes",
    response_model=list[PurposeOption],
    summary="Listar propósitos de finca",
)
def list_purposes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[PurposeOption]:
    """Retorna catálogo de propósitos de finca."""
    _ = current_user
    purposes = db.execute(select(Purpose).order_by(Purpose.name.asc())).scalars().all()
    return [PurposeOption.model_validate(p) for p in purposes]


@router.post(
    "",
    response_model=FarmResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una finca",
)
def create_farm(
    farm_data: FarmCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FarmResponse:
    """Crea una nueva finca asignada al usuario autenticado."""
    farm = farm_service.create_farm(db, farm_data, current_user.id)
    return FarmResponse.model_validate(farm)


@router.post(
    "/bulk",
    response_model=list[FarmResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Crear múltiples fincas",
)
def create_farms_bulk(
    payload: FarmBulkCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[FarmResponse]:
    """¿Qué? Crea varias fincas en una sola petición.
    ¿Para qué? Carga masiva — requisito de la rúbrica.
    ¿Impacto? Retorna 201 Created con la lista de fincas creadas.
    """
    farms = farm_service.create_farms_bulk(db, payload.items, current_user.id)
    return [FarmResponse.model_validate(f) for f in farms]


@router.get(
    "",
    response_model=list[FarmResponse],
    summary="Listar fincas del usuario",
)
def list_farms(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[FarmResponse]:
    """Retorna las fincas activas del usuario autenticado."""
    farms = farm_service.get_farms_by_owner(db, current_user.id)
    return [FarmResponse.model_validate(f) for f in farms]


@router.get(
    "/{farm_id}",
    response_model=FarmResponse,
    summary="Obtener detalle de una finca",
    dependencies=[Depends(require_permission("fincas", "can_read"))]
)
def get_farm(
    farm_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FarmResponse:
    """Retorna el detalle de una finca del usuario autenticado."""
    farm = farm_service.get_farm_by_id(db, farm_id, current_user.id)
    return FarmResponse.model_validate(farm)


@router.put(
    "/{farm_id}",
    response_model=FarmResponse,
    summary="Actualizar una finca",
    dependencies=[Depends(require_permission("fincas", "can_update"))]
)
def update_farm(
    farm_id: uuid.UUID,
    farm_data: FarmUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FarmResponse:
    """¿Qué? Actualiza parcialmente una finca del usuario autenticado.
    ¿Para qué? Modificar nombre, municipio o propósito sin recrear la finca.
    ¿Impacto? Solo se actualizan los campos enviados (exclude_unset).
    """
    farm = farm_service.update_farm(db, farm_id, current_user.id, farm_data)
    return FarmResponse.model_validate(farm)


@router.delete(
    "/{farm_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar una finca (soft delete)",
    dependencies=[Depends(require_permission("fincas", "can_delete"))]
)
def delete_farm(
    farm_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """¿Qué? Desactiva una finca del usuario autenticado (soft delete).
    ¿Para qué? No eliminar físicamente para conservar bovinos y registros.
    ¿Impacto? Retorna 204 No Content. La finca deja de aparecer en listados.
    """
    farm_service.delete_farm(db, farm_id, current_user.id)
