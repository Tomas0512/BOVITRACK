"""
Módulo: routers/food.py
¿Qué? Router de FastAPI para el CRUD de alimentos (inventario) y consumos.
¿Para qué? Gestionar el catálogo de insumos alimentarios de cada finca
           y registrar el consumo con descuento automático de stock.
¿Impacto? El inventario alimenta la vista v_low_stock_alerts para
          alertas de desabastecimiento. Los consumos permiten trazabilidad
          de qué se alimentó a quién y cuándo.
"""

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.permissions import require_permission

from app.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.food import (
    ConsumptionCreate,
    ConsumptionResponse,
    FoodCreate,
    FoodResponse,
    FoodUpdate,
)
from app.services import food_service

router = APIRouter(prefix="/api/v1/farms/{farm_id}/food", tags=["Alimentos e Inventario"])


# ═══════════════════════════════════════════════════════
# 📦 Alimentos — catálogo de insumos de la finca
# ═══════════════════════════════════════════════════════

@router.post("", response_model=FoodResponse, status_code=status.HTTP_201_CREATED, summary="Registrar alimento", dependencies=[Depends(require_permission("alimentos", "can_create"))])
def create_food(
    farm_id: uuid.UUID,
    data: FoodCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FoodResponse:
    """¿Qué? Registra un nuevo alimento en el inventario de la finca.
    ¿Para qué? Mantener un catálogo con stock, precio y proveedor.
    ¿Impacto? Retorna 201 Created. El alimento queda disponible para consumos.
    """
    _ = current_user
    food = food_service.create_food(db, farm_id, data)
    return FoodResponse.model_validate(food)


@router.get("", response_model=list[FoodResponse], summary="Listar alimentos", dependencies=[Depends(require_permission("alimentos", "can_read"))])
def list_foods(
    farm_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[FoodResponse]:
    """¿Qué? Lista los alimentos activos del inventario.
    ¿Para qué? Mostrar el catálogo al usuario con stock actual.
    ¿Impacto? Solo retorna alimentos activos, ordenados alfabéticamente.
    """
    _ = current_user
    foods = food_service.list_foods(db, farm_id)
    return [FoodResponse.model_validate(f) for f in foods]


@router.get("/{food_id}", response_model=FoodResponse, summary="Obtener alimento por ID", dependencies=[Depends(require_permission("alimentos", "can_read"))])
def get_food(
    farm_id: uuid.UUID,
    food_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FoodResponse:
    """¿Qué? Retorna el detalle de un alimento del inventario.
    ¿Para qué? Ver stock actual, precio, proveedor y fecha de vencimiento.
    ¿Impacto? Retorna 404 si no existe o no pertenece a la finca.
    """
    _ = current_user
    food = food_service.get_food(db, farm_id, food_id)
    return FoodResponse.model_validate(food)


@router.put("/{food_id}", response_model=FoodResponse, summary="Actualizar alimento", dependencies=[Depends(require_permission("alimentos", "can_update"))])
def update_food(
    farm_id: uuid.UUID,
    food_id: uuid.UUID,
    data: FoodUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FoodResponse:
    """¿Qué? Actualiza parcialmente un alimento (solo los campos enviados).
    ¿Para qué? Modificar precio, stock, proveedor sin reenviar todo.
    ¿Impacto? Retorna 404 si no existe.
    """
    _ = current_user
    food = food_service.update_food(db, farm_id, food_id, data)
    return FoodResponse.model_validate(food)


@router.delete("/{food_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar alimento (soft delete)", dependencies=[Depends(require_permission("alimentos", "can_delete"))])
def delete_food(
    farm_id: uuid.UUID,
    food_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """¿Qué? Desactiva un alimento del inventario (soft delete).
    ¿Para qué? Conservar el historial de consumos asociados.
    ¿Impacto? El alimento deja de aparecer en listados pero no se pierde.
    """
    _ = current_user
    food_service.delete_food(db, farm_id, food_id)


# ═══════════════════════════════════════════════════════
# 🍽️ Consumos — registro de alimentación
# ═══════════════════════════════════════════════════════

@router.post("/consumptions", response_model=ConsumptionResponse, status_code=status.HTTP_201_CREATED, summary="Registrar consumo", dependencies=[Depends(require_permission("alimentos", "can_create"))])
def create_consumption(
    farm_id: uuid.UUID,
    data: ConsumptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ConsumptionResponse:
    """¿Qué? Registra un consumo de alimento y descuenta stock automáticamente.
    ¿Para qué? Trazabilidad de alimentación por bovino/potrero.
    ¿Impacto? VALIDA stock antes de descontar. Si no hay suficiente,
              retorna 400 Bad Request con el stock disponible.
    """
    consumption = food_service.create_consumption(db, farm_id, data, current_user.id)
    return ConsumptionResponse.model_validate(consumption)


@router.get("/consumptions", response_model=list[ConsumptionResponse], summary="Listar consumos", dependencies=[Depends(require_permission("alimentos", "can_read"))])
def list_consumptions(
    farm_id: uuid.UUID,
    food_id: uuid.UUID | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ConsumptionResponse]:
    """¿Qué? Lista los consumos registrados con filtro opcional por alimento.
    ¿Para qué? Consultar historial de alimentación de la finca.
    ¿Impacto? Ordenados por fecha descendente (más recientes primero).
    """
    _ = current_user
    consumptions = food_service.list_consumptions(db, farm_id, food_id)
    return [ConsumptionResponse.model_validate(c) for c in consumptions]
