"""
Módulo: modules/farms/router/farms.py (frontera HTTP: fincas y catálogos)
¿Qué? /api/v1/farms: catálogos del formulario, crear (una o varias), listar,
      consultar, actualizar y desactivar fincas.
¿Para qué? Traducir HTTP <-> casos de uso. Las reglas están en FarmService.
¿Impacto? Rutas, nombres de función (operationId) y docstrings iguales a los de
          antes del refactor.
"""

import uuid

from fastapi import APIRouter, Depends, status

from app.modules.farms.dependencies import (
    get_catalog_service,
    get_current_user,
    get_farm_service,
    require_permission,
)
from app.modules.farms.schemas import (
    CityOption,
    DepartmentOption,
    FarmBulkCreateRequest,
    FarmBulkCreateResult,
    FarmCreate,
    FarmResponse,
    FarmUpdate,
    PurposeOption,
)
from app.modules.farms.service import CatalogService, FarmService
from app.shared.ports import CurrentUser

router = APIRouter(prefix="/api/v1/farms", tags=["Fincas"])


@router.get(
    "/departments",
    response_model=list[DepartmentOption],
    summary="Listar departamentos",
)
def list_departments(
    service: CatalogService = Depends(get_catalog_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> list[DepartmentOption]:
    """Retorna catálogo de departamentos para formularios."""
    _ = current_user
    return [DepartmentOption.model_validate(d) for d in service.departments()]


@router.get(
    "/departments/{department_id}/cities",
    response_model=list[CityOption],
    summary="Listar ciudades de un departamento",
)
def list_cities(
    department_id: uuid.UUID,
    service: CatalogService = Depends(get_catalog_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> list[CityOption]:
    """Retorna catálogo de ciudades de un departamento para formularios."""
    _ = current_user
    return [CityOption.model_validate(c) for c in service.cities(department_id)]


@router.get(
    "/purposes",
    response_model=list[PurposeOption],
    summary="Listar propósitos de finca",
)
def list_purposes(
    service: CatalogService = Depends(get_catalog_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> list[PurposeOption]:
    """Retorna catálogo de propósitos de finca."""
    _ = current_user
    return [PurposeOption.model_validate(p) for p in service.purposes()]


@router.post(
    "",
    response_model=FarmResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una finca",
)
def create_farm(
    farm_data: FarmCreate,
    service: FarmService = Depends(get_farm_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> FarmResponse:
    """Crea una nueva finca asignada al usuario autenticado."""
    return FarmResponse.model_validate(service.create(farm_data, current_user.id))


@router.post(
    "/bulk",
    response_model=FarmBulkCreateResult,
    summary="Crear múltiples fincas",
)
def create_farms_bulk(
    payload: FarmBulkCreateRequest,
    service: FarmService = Depends(get_farm_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> FarmBulkCreateResult:
    """¿Qué? Crea varias fincas en una sola petición y reporta el resultado fila por fila.
    ¿Para qué? Carga masiva — requisito de la rúbrica. Una finca con error (p. ej.
               identificador repetido) no impide que se creen las demás.
    ¿Impacto? Retorna 200 con total, creadas, fallidas, las fincas creadas y los
              errores (fila, identificador y motivo). Un campo con formato inválido
              rechaza la petición completa con 422, indicando la fila (items.N).
    """
    return service.create_many(payload.items, current_user.id)


@router.get(
    "",
    response_model=list[FarmResponse],
    summary="Listar fincas del usuario",
)
def list_farms(
    service: FarmService = Depends(get_farm_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> list[FarmResponse]:
    """Retorna las fincas activas del usuario autenticado."""
    return [FarmResponse.model_validate(f) for f in service.list_for_user(current_user.id)]


@router.get(
    "/{farm_id}",
    response_model=FarmResponse,
    summary="Obtener detalle de una finca",
    dependencies=[Depends(require_permission("fincas", "can_read"))]
)
def get_farm(
    farm_id: uuid.UUID,
    service: FarmService = Depends(get_farm_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> FarmResponse:
    """Retorna el detalle de una finca del usuario autenticado."""
    return FarmResponse.model_validate(service.get_for_user(farm_id, current_user.id))


@router.put(
    "/{farm_id}",
    response_model=FarmResponse,
    summary="Actualizar una finca",
    dependencies=[Depends(require_permission("fincas", "can_update"))]
)
def update_farm(
    farm_id: uuid.UUID,
    farm_data: FarmUpdate,
    service: FarmService = Depends(get_farm_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> FarmResponse:
    """¿Qué? Actualiza parcialmente una finca del usuario autenticado.
    ¿Para qué? Modificar nombre, municipio o propósito sin recrear la finca.
    ¿Impacto? Solo se actualizan los campos enviados (exclude_unset).
    """
    return FarmResponse.model_validate(service.update(farm_id, current_user.id, farm_data))


@router.delete(
    "/{farm_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar una finca (soft delete)",
    dependencies=[Depends(require_permission("fincas", "can_delete"))]
)
def delete_farm(
    farm_id: uuid.UUID,
    service: FarmService = Depends(get_farm_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> None:
    """¿Qué? Desactiva una finca del usuario autenticado (soft delete).
    ¿Para qué? No eliminar físicamente para conservar bovinos y registros.
    ¿Impacto? Retorna 204 No Content. La finca deja de aparecer en listados.
    """
    service.deactivate(farm_id, current_user.id)
