"""
Módulo: routers/paddocks.py
¿Qué? Router de FastAPI para el CRUD de potreros.
¿Para qué? Gestionar la creación, consulta, actualización y desactivación
           de potreros dentro de cada finca.
¿Impacto? La rotación de potreros es fundamental para la sostenibilidad
          ganadera. Sin este router, no se podrían gestionar áreas de pastoreo.
"""

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.permissions import require_permission

from app.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.paddock import PaddockCreate, PaddockResponse, PaddockUpdate
from app.services import paddock_service

router = APIRouter(prefix="/api/v1/farms/{farm_id}/paddocks", tags=["Potreros"])


@router.post("", response_model=PaddockResponse, status_code=status.HTTP_201_CREATED, summary="Crear potrero", dependencies=[Depends(require_permission("potreros", "can_create"))])
def create(
    farm_id: uuid.UUID,
    data: PaddockCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PaddockResponse:
    """¿Qué? Registra un nuevo potrero (área de pastoreo) en la finca.
    ¿Para qué? Definir área, capacidad y estado inicial del potrero.
    ¿Impacto? Retorna 201 Created. El potrero queda disponible para rotación.
    """
    _ = current_user
    paddock = paddock_service.create_paddock(db, farm_id, data)
    return PaddockResponse.model_validate(paddock)


@router.get("", response_model=list[PaddockResponse], summary="Listar potreros", dependencies=[Depends(require_permission("potreros", "can_read"))])
def list_all(
    farm_id: uuid.UUID,
    paddock_status: str | None = Query(None, alias="status", description="Filtrar por estado: libre, ocupado, en_descanso"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[PaddockResponse]:
    """Lista los potreros activos de la finca con filtro opcional por estado."""
    _ = current_user
    paddocks = paddock_service.list_paddocks(db, farm_id, status_filter=paddock_status)
    return [PaddockResponse.model_validate(p) for p in paddocks]


@router.get("/{paddock_id}", response_model=PaddockResponse, summary="Obtener potrero por ID", dependencies=[Depends(require_permission("potreros", "can_read"))])
def get_one(
    farm_id: uuid.UUID,
    paddock_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PaddockResponse:
    """¿Qué? Retorna el detalle de un potrero específico.
    ¿Para qué? Ver área, capacidad, estado de cobertura y fechas de descanso.
    ¿Impacto? Retorna 404 si no existe o no pertenece a la finca.
    """
    _ = current_user
    paddock = paddock_service.get_paddock(db, farm_id, paddock_id)
    return PaddockResponse.model_validate(paddock)


@router.put("/{paddock_id}", response_model=PaddockResponse, summary="Actualizar potrero", dependencies=[Depends(require_permission("potreros", "can_update"))])
def update(
    farm_id: uuid.UUID,
    paddock_id: uuid.UUID,
    data: PaddockUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PaddockResponse:
    """¿Qué? Actualiza parcialmente un potrero (solo los campos enviados).
    ¿Para qué? Cambiar estado (libre → ocupado → en_descanso), cobertura, fechas.
    ¿Impacto? Clave para la gestión de rotación de potreros.
    """
    _ = current_user
    paddock = paddock_service.update_paddock(db, farm_id, paddock_id, data)
    return PaddockResponse.model_validate(paddock)


@router.delete("/{paddock_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar potrero (soft delete)", dependencies=[Depends(require_permission("potreros", "can_delete"))])
def delete(
    farm_id: uuid.UUID,
    paddock_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """¿Qué? Desactiva un potrero (soft delete).
    ¿Para qué? Conservar el historial de rotaciones y bovinos que estuvieron ahí.
    ¿Impacto? Retorna 204 No Content. El potrero ya no aparece en listados activos.
    """
    _ = current_user
    paddock_service.delete_paddock(db, farm_id, paddock_id)
