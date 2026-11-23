"""
Módulo: modules/farms/router/paddocks.py (frontera HTTP: potreros)
¿Qué? CRUD de potreros de una finca: /api/v1/farms/{farm_id}/paddocks.
¿Para qué? Gestionar la creación, consulta, actualización y desactivación de
           potreros. Las reglas de rotación están en PaddockService.
¿Impacto? Cada respuesta incluye los animales activos del potrero. Antes este
          router consultaba el modelo Bovine (de livestock); ahora el servicio
          los lee con un modelo de lectura y el router no conoce el ganado.
"""

import uuid

from fastapi import APIRouter, Depends, Query, status

from app.modules.farms.dependencies import get_current_user, get_paddock_service, require_permission
from app.modules.farms.schemas import PaddockCreate, PaddockResponse, PaddockUpdate
from app.modules.farms.service import PaddockService
from app.shared.ports import CurrentUser

router = APIRouter(prefix="/api/v1/farms/{farm_id}/paddocks", tags=["Potreros"])


@router.post("", response_model=PaddockResponse, status_code=status.HTTP_201_CREATED, summary="Crear potrero", dependencies=[Depends(require_permission("potreros", "can_create"))])
def create(
    farm_id: uuid.UUID,
    data: PaddockCreate,
    service: PaddockService = Depends(get_paddock_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> PaddockResponse:
    """¿Qué? Registra un nuevo potrero (área de pastoreo) en la finca.
    ¿Para qué? Definir área, capacidad y estado inicial del potrero.
    ¿Impacto? Retorna 201 Created. El potrero queda disponible para rotación.
    """
    paddock = service.create(farm_id, data, current_user.id)
    return service.with_animals([paddock])[0]


@router.get("", response_model=list[PaddockResponse], summary="Listar potreros", dependencies=[Depends(require_permission("potreros", "can_read"))])
def list_all(
    farm_id: uuid.UUID,
    paddock_status: str | None = Query(None, alias="status", description="Filtrar por estado: libre, ocupado, en_descanso"),
    land_plot_id: uuid.UUID | None = Query(None, description="Filtrar por lote al que pertenece"),
    service: PaddockService = Depends(get_paddock_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> list[PaddockResponse]:
    """Lista los potreros activos de la finca, con filtro por estado y por lote."""
    _ = current_user
    return service.with_animals(service.list(farm_id, status=paddock_status, land_plot_id=land_plot_id))


@router.get("/{paddock_id}", response_model=PaddockResponse, summary="Obtener potrero por ID", dependencies=[Depends(require_permission("potreros", "can_read"))])
def get_one(
    farm_id: uuid.UUID,
    paddock_id: uuid.UUID,
    service: PaddockService = Depends(get_paddock_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> PaddockResponse:
    """¿Qué? Retorna el detalle de un potrero específico.
    ¿Para qué? Ver área, capacidad, estado de cobertura y fechas de descanso.
    ¿Impacto? Retorna 404 si no existe o no pertenece a la finca.
    """
    _ = current_user
    return service.with_animals([service.get(farm_id, paddock_id)])[0]


@router.put("/{paddock_id}", response_model=PaddockResponse, summary="Actualizar potrero", dependencies=[Depends(require_permission("potreros", "can_update"))])
def update(
    farm_id: uuid.UUID,
    paddock_id: uuid.UUID,
    data: PaddockUpdate,
    service: PaddockService = Depends(get_paddock_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> PaddockResponse:
    """¿Qué? Actualiza parcialmente un potrero (solo los campos enviados).
    ¿Para qué? Cambiar estado (libre → ocupado → en_descanso), cobertura, fechas.
    ¿Impacto? Clave para la gestión de rotación de potreros.
    """
    paddock = service.update(farm_id, paddock_id, data, current_user.id)
    return service.with_animals([paddock])[0]


@router.delete("/{paddock_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar potrero (soft delete)", dependencies=[Depends(require_permission("potreros", "can_delete"))])
def delete(
    farm_id: uuid.UUID,
    paddock_id: uuid.UUID,
    service: PaddockService = Depends(get_paddock_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> None:
    """¿Qué? Desactiva un potrero (soft delete).
    ¿Para qué? Conservar el historial de rotaciones y bovinos que estuvieron ahí.
    ¿Impacto? Retorna 204 No Content. El potrero ya no aparece en listados activos.
    """
    service.deactivate(farm_id, paddock_id, current_user.id)
