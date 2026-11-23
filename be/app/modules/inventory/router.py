"""
Módulo: modules/inventory/router.py (frontera HTTP del módulo)
¿Qué? Router de FastAPI para el CRUD de alimentos (inventario) y consumos.
¿Para qué? Gestionar el catálogo de insumos alimentarios de cada finca
           y registrar el consumo con descuento automático de stock.
¿Impacto? El inventario alimenta la vista v_low_stock_alerts para
          alertas de desabastecimiento. Los consumos permiten trazabilidad
          de qué se alimentó a quién y cuándo.
"""

import uuid

from fastapi import APIRouter, Body, Depends, Path, Query, Request, status


from app.core.limiter import limiter
from app.modules.inventory.dependencies import (
    get_calf_feeding_service,
    get_current_user,
    get_inventory_service,
    require_permission,
)

from app.modules.inventory.schemas import (
    CalfFeedingPlanCreate,
    ConsumptionCreate,
    ConsumptionResponse,
    FoodCreate,
    FoodResponse,
    FoodUpdate,
    PurchaseCreate,
    StockAdjustmentCreate,
    StockMovementResponse,
)
from app.modules.inventory.service import CalfFeedingService, InventoryService
from app.shared.ports import CurrentUser

router = APIRouter(prefix="/api/v1/farms/{farm_id}/food", tags=["Alimentos e Inventario"])


# ═══════════════════════════════════════════════════════
# 📦 Alimentos — catálogo de insumos de la finca
# ═══════════════════════════════════════════════════════

@router.post("", response_model=FoodResponse, status_code=status.HTTP_201_CREATED, summary="Registrar alimento", dependencies=[Depends(require_permission("alimentos", "can_create"))])
def create_food(
    farm_id: uuid.UUID,
    data: FoodCreate,
    service: InventoryService = Depends(get_inventory_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> FoodResponse:
    """¿Qué? Registra un nuevo alimento en el inventario de la finca.
    ¿Para qué? Mantener un catálogo con stock, precio y proveedor.
    ¿Impacto? Retorna 201 Created. El alimento queda disponible para consumos.
    """
    _ = current_user
    food = service.create_food(farm_id, data, current_user.id)
    return FoodResponse.model_validate(food)


@router.get("", response_model=list[FoodResponse], summary="Listar alimentos", dependencies=[Depends(require_permission("alimentos", "can_read"))])
def list_foods(
    farm_id: uuid.UUID,
    service: InventoryService = Depends(get_inventory_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> list[FoodResponse]:
    """¿Qué? Lista los alimentos activos del inventario.
    ¿Para qué? Mostrar el catálogo al usuario con stock actual.
    ¿Impacto? Solo retorna alimentos activos, ordenados alfabéticamente.
    """
    _ = current_user
    foods = service.list_foods(farm_id)
    return [FoodResponse.model_validate(f) for f in foods]


@router.put("/{food_id}", response_model=FoodResponse, summary="Actualizar alimento", dependencies=[Depends(require_permission("alimentos", "can_update"))])
def update_food(
    farm_id: uuid.UUID,
    food_id: uuid.UUID,
    data: FoodUpdate,
    service: InventoryService = Depends(get_inventory_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> FoodResponse:
    """¿Qué? Actualiza parcialmente un alimento (solo los campos enviados).
    ¿Para qué? Modificar precio, stock, proveedor sin reenviar todo.
    ¿Impacto? Retorna 404 si no existe.
    """
    _ = current_user
    food = service.update_food(farm_id, food_id, data, current_user.id)
    return FoodResponse.model_validate(food)


@router.delete("/{food_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar alimento (soft delete)", dependencies=[Depends(require_permission("alimentos", "can_delete"))])
def delete_food(
    farm_id: uuid.UUID,
    food_id: uuid.UUID,
    service: InventoryService = Depends(get_inventory_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> None:
    """¿Qué? Desactiva un alimento del inventario (soft delete).
    ¿Para qué? Conservar el historial de consumos asociados.
    ¿Impacto? El alimento deja de aparecer en listados pero no se pierde.
    """
    _ = current_user
    service.delete_food(farm_id, food_id, current_user.id)


# ═══════════════════════════════════════════════════════
# 🍽️ Consumos — registro de alimentación
# ═══════════════════════════════════════════════════════

@router.post("/consumptions", response_model=ConsumptionResponse, status_code=status.HTTP_201_CREATED, summary="Registrar consumo", dependencies=[Depends(require_permission("alimentos", "can_create"))])
def create_consumption(
    farm_id: uuid.UUID,
    data: ConsumptionCreate,
    service: InventoryService = Depends(get_inventory_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> ConsumptionResponse:
    """¿Qué? Registra un consumo de alimento y descuenta stock automáticamente.
    ¿Para qué? Trazabilidad de alimentación por bovino/potrero.
    ¿Impacto? VALIDA stock antes de descontar. Si no hay suficiente,
              retorna 400 Bad Request con el stock disponible.
    """
    consumption = service.create_consumption(farm_id, data, current_user.id)
    return ConsumptionResponse.model_validate(consumption)


@router.get("/consumptions", response_model=list[ConsumptionResponse], summary="Listar consumos", dependencies=[Depends(require_permission("alimentos", "can_read"))])
def list_consumptions(
    farm_id: uuid.UUID,
    food_id: uuid.UUID | None = Query(None),
    bovine_id: uuid.UUID | None = Query(None),
    service: InventoryService = Depends(get_inventory_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> list[ConsumptionResponse]:
    """¿Qué? Lista los consumos registrados con filtro opcional por alimento o bovino.
    ¿Para qué? Consultar historial de alimentación de la finca o de un animal específico.
    ¿Impacto? Ordenados por fecha descendente (más recientes primero).
    """
    _ = current_user
    consumptions = service.list_consumptions(farm_id, food_id, bovine_id)
    return [ConsumptionResponse.model_validate(c) for c in consumptions]


# ═══════════════════════════════════════════════════════
# 📦 Compras y Movimientos de Stock (HU011)
# ═══════════════════════════════════════════════════════


@router.post("/purchases", response_model=dict, status_code=status.HTTP_201_CREATED, summary="Registrar compra de insumo", dependencies=[Depends(require_permission("alimentos", "can_create"))])
def record_purchase(
    farm_id: uuid.UUID,
    data: PurchaseCreate,
    service: InventoryService = Depends(get_inventory_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> dict:
    """Record a purchase of a food item. Increases stock and logs cost.
    Why? Track both inventory levels and purchase costs (HU011).
    """
    food, movement = service.record_purchase(
        farm_id, data.food_id, data.quantity,
        data.unit_cost, current_user.id, data.movement_date, data.notes,
    )
    return {
        "food": FoodResponse.model_validate(food).model_dump(),
        "movement": StockMovementResponse.model_validate(movement).model_dump(),
    }


@router.post("/adjust-stock", response_model=dict, status_code=status.HTTP_201_CREATED, summary="Ajustar stock manualmente", dependencies=[Depends(require_permission("alimentos", "can_update"))])
def adjust_stock(
    farm_id: uuid.UUID,
    data: StockAdjustmentCreate,
    service: InventoryService = Depends(get_inventory_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> dict:
    """Manually adjust stock level for inventory corrections (HU011).
    positive quantity = increase stock, negative = decrease.
    """
    food, movement = service.record_stock_adjustment(
        farm_id, data.food_id, data.quantity,
        data.reason, current_user.id, data.movement_date,
    )
    return {
        "food": FoodResponse.model_validate(food).model_dump(),
        "movement": StockMovementResponse.model_validate(movement).model_dump(),
    }


@router.get("/movements", response_model=list[StockMovementResponse], summary="Historial de movimientos de stock", dependencies=[Depends(require_permission("alimentos", "can_read"))])
def list_stock_movements(
    farm_id: uuid.UUID,
    food_id: uuid.UUID | None = Query(None),
    movement_type: str | None = Query(None),
    limit: int = Query(100, ge=1, le=500),
    service: InventoryService = Depends(get_inventory_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> list[StockMovementResponse]:
    """Get full stock movement history for traceability (HU011.2).
    Filterable by food_id and movement_type. Newest first.
    """
    _ = current_user
    movements = service.get_stock_movements(farm_id, food_id, movement_type, limit)
    return [StockMovementResponse.model_validate(m) for m in movements]


@router.get("/low-stock", response_model=list[FoodResponse], summary="Alertas de stock bajo", dependencies=[Depends(require_permission("alimentos", "can_read"))])
def low_stock_alerts(
    farm_id: uuid.UUID,
    service: InventoryService = Depends(get_inventory_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> list[FoodResponse]:
    """Get all food items below minimum stock threshold (HU011.3).
    Why? Frontend can show reorder alerts.
    """
    _ = current_user
    foods = service.get_low_stock_foods(farm_id)
    return [FoodResponse.model_validate(f) for f in foods]


# ⚠️ Ruta paramétrica se registra AL FINAL para no tapar a las estáticas
# (GET /movements, /consumptions, /low-stock). FastAPI empareja en orden.
@router.get("/{food_id}", response_model=FoodResponse, summary="Obtener alimento por ID", dependencies=[Depends(require_permission("alimentos", "can_read"))])
def get_food(
    farm_id: uuid.UUID,
    food_id: uuid.UUID,
    service: InventoryService = Depends(get_inventory_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> FoodResponse:
    """¿Qué? Retorna el detalle de un alimento del inventario.
    ¿Para qué? Ver stock actual, precio, proveedor y fecha de vencimiento.
    ¿Impacto? Retorna 404 si no existe o no pertenece a la finca.
    """
    _ = current_user
    food = service.get_food(farm_id, food_id)
    return FoodResponse.model_validate(food)


# ═══════════════════════════════════════════════════════
# 🍼 Plan de alimentación de terneros (HU007)
# ═══════════════════════════════════════════════════════
# Vive en inventario porque lo que valida es un alimento de la finca. La ruta,
# la etiqueta y el operationId son los mismos que tenía en el router de terneros.

calf_feeding_router = APIRouter(
    prefix="/api/v1/farms/{farm_id}/calves",
    tags=["Terneros (HU007)"],
)


@calf_feeding_router.post(
    "/{bovine_id}/feeding-plan",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Actualizar plan de alimentación",
    description="""
    ¿Qué? Registra o actualiza el plan de alimentación de un ternero.

    ¿Cuerpo?
      {
        "food_id": "uuid-del-alimento",
        "quantity_kg_per_day": 2.5,
        "start_date": "2026-06-15",
        "end_date": "2026-07-15",
        "notes": "Introducir concentrado gradualmente"
      }

    ¿Para qué?
      - Seguimiento del crecimiento (HU007)
      - Registrar costos de alimentación (HU010)

    ¿Correspondencia HU?
      HU007 Task 7.2: Registro de alimentación
      HU010: Registrar información económica
    """,
    dependencies=[Depends(require_permission("bovinos", "can_create"))],
)
@limiter.limit("5/minute")
def update_calf_feeding_plan(
    request: Request,
    farm_id: uuid.UUID = Path(...),
    bovine_id: uuid.UUID = Path(...),
    feeding_data: CalfFeedingPlanCreate = Body(...),
    service: CalfFeedingService = Depends(get_calf_feeding_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> dict:
    """
    ¿QUÉ PASA AQUÍ?

    1. Se recibe el plan de alimentación
    2. Se valida que el ternero y alimento existen
    3. Se guarda el plan
    4. Se retorna el plan guardado

    NOTA: En una implementación completa, habría una tabla FeedingPlan en BD.
    Por ahora, retornamos un diccionario que el frontend puede almacenar.
    """

    plan = service.update_calf_feeding_plan(
        farm_id=farm_id,
        bovine_id=bovine_id,
        food_id=feeding_data.food_id,
        quantity_kg_per_day=feeding_data.quantity_kg_per_day,
        start_date=feeding_data.start_date,
        end_date=feeding_data.end_date,
        notes=feeding_data.notes,
    )

    return plan


# Router del módulo: inventario + plan de alimentación de terneros.
module_router = APIRouter()
module_router.include_router(router)
module_router.include_router(calf_feeding_router)
