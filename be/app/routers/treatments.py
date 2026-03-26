"""
Módulo: routers/treatments.py
¿Qué? Router de FastAPI para el CRUD de tratamientos sanitarios.
¿Para qué? Permitir registrar vacunaciones, desparasitaciones y
           tratamientos veterinarios asociados a bovinos o potreros.
¿Impacto? La trazabilidad sanitaria es obligatoria para el ICA.
          Cada endpoint requiere autenticación JWT.
"""

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.permissions import require_permission

from app.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.treatment import TreatmentCreate, TreatmentResponse
from app.services import treatment_service

router = APIRouter(prefix="/api/v1/farms/{farm_id}/treatments", tags=["Tratamientos"])


@router.post("", response_model=TreatmentResponse, status_code=status.HTTP_201_CREATED, summary="Registrar tratamiento", dependencies=[Depends(require_permission("tratamientos", "can_create"))])
def create(
    farm_id: uuid.UUID,
    data: TreatmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TreatmentResponse:
    """¿Qué? Registra un tratamiento sanitario en la finca.
    ¿Para qué? Vincular el tratamiento al usuario que lo aplicó (applied_by).
    ¿Impacto? Retorna 201 Created con el tratamiento completo.
    """
    treatment = treatment_service.create_treatment(db, farm_id, data, current_user.id)
    return TreatmentResponse.model_validate(treatment)


@router.get("", response_model=list[TreatmentResponse], summary="Listar tratamientos", dependencies=[Depends(require_permission("tratamientos", "can_read"))])
def list_all(
    farm_id: uuid.UUID,
    bovine_id: uuid.UUID | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[TreatmentResponse]:
    """¿Qué? Lista tratamientos de la finca con filtro opcional por bovino.
    ¿Para qué? Consultar historial sanitario completo o de un animal específico.
    ¿Impacto? bovine_id como query parameter permite filtrar desde el frontend.
    """
    _ = current_user
    treatments = treatment_service.list_treatments(db, farm_id, bovine_id)
    return [TreatmentResponse.model_validate(t) for t in treatments]


@router.get("/{treatment_id}", response_model=TreatmentResponse, summary="Obtener tratamiento por ID", dependencies=[Depends(require_permission("tratamientos", "can_read"))])
def get_one(
    farm_id: uuid.UUID,
    treatment_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TreatmentResponse:
    """¿Qué? Retorna el detalle de un tratamiento específico.
    ¿Para qué? Ver dosis, vía, diagnóstico y observaciones del tratamiento.
    ¿Impacto? Retorna 404 si no existe o no pertenece a la finca.
    """
    _ = current_user
    treatment = treatment_service.get_treatment(db, farm_id, treatment_id)
    return TreatmentResponse.model_validate(treatment)


@router.delete("/{treatment_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar tratamiento", dependencies=[Depends(require_permission("tratamientos", "can_delete"))])
def delete(
    farm_id: uuid.UUID,
    treatment_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """¿Qué? Elimina permanentemente un tratamiento registrado por error.
    ¿Para qué? Corrección de datos. No es soft delete porque no tiene dependencias.
    ¿Impacto? Retorna 204 No Content. La eliminación es irreversible.
    """
    _ = current_user
    treatment_service.delete_treatment(db, farm_id, treatment_id)
