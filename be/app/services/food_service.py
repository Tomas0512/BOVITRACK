"""
Módulo: services/food_service.py
¿Qué? Capa de servicio para el módulo de alimentos (inventario) y consumos.
¿Para qué? Gestionar el catálogo de insumos alimentarios de cada finca,
           registrar consumos y descontar automáticamente el stock.
¿Impacto? El control de inventario es clave para evitar desabastecimiento.
          La vista v_low_stock_alerts depende de estos datos para las alertas.
"""

import uuid
from decimal import Decimal
from typing import Sequence

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from datetime import datetime, timezone

from app.models.food import Consumption, Food, StockMovement
from app.models.paddock import Paddock
from app.schemas.food import ConsumptionCreate, FoodCreate, FoodUpdate
from app.services.audit_service import add_audit_log
from app.utils.validators import ensure_farm_scope


def create_food(db: Session, farm_id: uuid.UUID, data: FoodCreate, user_id: uuid.UUID | None = None) -> Food:
    """¿Qué? Registra un nuevo alimento en el inventario de la finca.
    ¿Para qué? Mantener un catálogo de insumos con stock, precio y proveedor.
    ¿Impacto? El alimento queda disponible para registrar consumos.
    """
    food = Food(farm_id=farm_id, **data.model_dump())
    db.add(food)
    db.commit()
    db.refresh(food)
    add_audit_log(db, user_id=str(user_id) if user_id else None, farm_id=str(farm_id), action="create", entity="food", entity_id=str(food.id), details={"name": food.name})
    db.commit()
    return food


def list_foods(db: Session, farm_id: uuid.UUID) -> Sequence[Food]:
    """¿Qué? Lista los alimentos activos del inventario de una finca.
    ¿Para qué? Mostrar el catálogo de insumos disponibles.
    ¿Impacto? Solo retorna alimentos con is_active=True (excluye eliminados).
    """
    stmt = select(Food).where(Food.farm_id == farm_id, Food.is_active.is_(True)).order_by(Food.name.asc())
    return db.execute(stmt).scalars().all()


def get_food(db: Session, farm_id: uuid.UUID, food_id: uuid.UUID) -> Food:
    """¿Qué? Obtiene un alimento por ID dentro de una finca.
    ¿Para qué? Consultar detalle o validar existencia antes de operar.
    ¿Impacto? Filtra por farm_id para evitar acceso cruzado entre fincas.
    """
    stmt = select(Food).where(Food.id == food_id, Food.farm_id == farm_id)
    food = db.execute(stmt).scalar_one_or_none()
    if not food:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alimento no encontrado")
    return food


def update_food(db: Session, farm_id: uuid.UUID, food_id: uuid.UUID, data: FoodUpdate, user_id: uuid.UUID | None = None) -> Food:
    """¿Qué? Actualiza los campos enviados de un alimento.
    ¿Para qué? Modificar precio, stock, proveedor, etc. sin reenviar todo.
    ¿Impacto? exclude_unset=True asegura actualización parcial segura.
    """
    food = get_food(db, farm_id, food_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(food, field, value)
    db.commit()
    db.refresh(food)
    add_audit_log(db, user_id=str(user_id) if user_id else None, farm_id=str(farm_id), action="update", entity="food", entity_id=str(food.id), details={"name": food.name})
    db.commit()
    return food


def delete_food(db: Session, farm_id: uuid.UUID, food_id: uuid.UUID, user_id: uuid.UUID | None = None) -> None:
    """¿Qué? Desactiva un alimento del inventario (soft delete).
    ¿Para qué? No eliminar físicamente para conservar el historial de consumos.
    ¿Impacto? El alimento deja de aparecer en listados pero sus consumos
              asociados se mantienen para auditoría.
    """
    food = get_food(db, farm_id, food_id)
    food.is_active = False
    add_audit_log(db, user_id=str(user_id) if user_id else None, farm_id=str(farm_id), action="delete", entity="food", entity_id=str(food.id), details={"name": food.name})
    db.commit()


# ── Consumos ──────────────────────────────────────


def create_consumption(db: Session, farm_id: uuid.UUID, data: ConsumptionCreate, user_id: uuid.UUID) -> Consumption:
    """¿Qué? Registra un consumo de alimento y descuenta el stock automáticamente.
    ¿Para qué? Llevar trazabilidad de qué alimento se usó, cuánto y para quién.
    ¿Impacto? VALIDA stock antes de descontar. Si no hay suficiente, retorna
              400 Bad Request con el stock disponible. Esto evita inventario negativo.
    """
    # ¿Qué? Obtener el alimento para verificar stock.
    # ¿Para qué? No se puede consumir más de lo disponible.
    food = get_food(db, farm_id, data.food_id)
    ensure_farm_scope(db, farm_id, bovine_id=data.bovine_id, land_plot_id=data.land_plot_id)

    # ¿Qué? Validar el potrero (pertenece a la finca y es coherente con el lote).
    if data.paddock_id:
        paddock = db.execute(
            select(Paddock).where(
                Paddock.id == data.paddock_id,
                Paddock.farm_id == farm_id,
                Paddock.is_active.is_(True),
            )
        ).scalar_one_or_none()
        if not paddock:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El potrero indicado no existe en esta finca.",
            )
        if data.land_plot_id is not None and paddock.land_plot_id != data.land_plot_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El potrero indicado pertenece a otro lote.",
            )
        if data.land_plot_id is None:
            data.land_plot_id = paddock.land_plot_id
    if food.current_stock < data.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Stock insuficiente. Disponible: {food.current_stock} {food.unit_of_measure}",
        )

    # ¿Qué? Descontar la cantidad consumida del stock.
    # ¿Impacto? Si la transacción falla, el rollback restaura el stock original.
    stock_before = food.current_stock
    food.current_stock -= data.quantity
    _record_stock_movement(
        db,
        farm_id=farm_id,
        food_id=food.id,
        movement_type="consumption",
        quantity=-data.quantity,
        stock_before=stock_before,
        stock_after=food.current_stock,
        registered_by=user_id,
        reference_type="consumption",
        notes=f"Consumo: {data.observations or ''}".strip() or None,
        movement_date=data.feeding_date,
    )

    consumption = Consumption(
        farm_id=farm_id,
        registered_by=user_id,
        **data.model_dump(),
    )
    db.add(consumption)
    db.commit()
    db.refresh(consumption)
    add_audit_log(db, user_id=str(user_id), farm_id=str(farm_id), action="create", entity="consumption", entity_id=str(consumption.id), details={"food_id": str(data.food_id), "quantity": str(data.quantity)})
    db.commit()
    return consumption


def list_consumptions(
    db: Session,
    farm_id: uuid.UUID,
    food_id: uuid.UUID | None = None,
    bovine_id: uuid.UUID | None = None,
) -> Sequence[Consumption]:
    """¿Qué? Lista los consumos registrados de una finca.
    ¿Para qué? Consultar el historial de alimentación, filtrable por alimento o bovino.
    ¿Impacto? Ordenados por fecha descendente para ver los más recientes primero.
    """
    stmt = select(Consumption).where(Consumption.farm_id == farm_id)
    if food_id:
        stmt = stmt.where(Consumption.food_id == food_id)
    if bovine_id:
        stmt = stmt.where(Consumption.bovine_id == bovine_id)
    stmt = stmt.order_by(Consumption.feeding_date.desc())
    return db.execute(stmt).scalars().all()


# ── Stock Movements (HU011) ──────────────────────────


def _record_stock_movement(
    db: Session,
    farm_id: uuid.UUID,
    food_id: uuid.UUID,
    movement_type: str,
    quantity: Decimal,
    stock_before: Decimal,
    stock_after: Decimal,
    registered_by: uuid.UUID,
    unit_cost: Decimal | None = None,
    total_cost: Decimal | None = None,
    reference_type: str | None = None,
    reference_id: uuid.UUID | None = None,
    notes: str | None = None,
    movement_date: datetime | None = None,
) -> StockMovement:
    """Internal helper to record any stock movement with full traceability.
    Why? All stock changes (purchase, consumption, adjustment, return) are
          logged here so the frontend can show a complete audit trail.
    """
    movement = StockMovement(
        farm_id=farm_id,
        food_id=food_id,
        movement_type=movement_type,
        quantity=quantity,
        unit_cost=unit_cost,
        total_cost=total_cost,
        stock_before=stock_before,
        stock_after=stock_after,
        reference_type=reference_type,
        reference_id=reference_id,
        notes=notes,
        registered_by=registered_by,
        movement_date=movement_date or datetime.now(timezone.utc),
    )
    db.add(movement)
    db.flush()
    return movement


def record_purchase(
    db: Session,
    farm_id: uuid.UUID,
    food_id: uuid.UUID,
    quantity: Decimal,
    unit_cost: Decimal,
    user_id: uuid.UUID,
    movement_date: datetime | None = None,
    notes: str | None = None,
) -> tuple[Food, StockMovement]:
    """Record a purchase of a food item — increases stock and logs cost.
    Why? Track both inventory levels and purchase costs for HU011.
    Impact? Updates Food.current_stock, creates StockMovement + EconomicRecord.
    """
    food = get_food(db, farm_id, food_id)
    stock_before = food.current_stock
    total_cost = quantity * unit_cost

    food.current_stock += quantity
    food.cost_per_unit = unit_cost
    food.supplier = notes if notes and not food.supplier else food.supplier
    db.flush()

    movement = _record_stock_movement(
        db=db, farm_id=farm_id, food_id=food_id,
        movement_type="purchase",
        quantity=quantity,
        stock_before=stock_before,
        stock_after=food.current_stock,
        registered_by=user_id,
        unit_cost=unit_cost,
        total_cost=total_cost,
        notes=notes,
        movement_date=movement_date,
    )

    db.commit()
    db.refresh(food)

    add_audit_log(
        db, user_id=str(user_id), farm_id=str(farm_id),
        action="create", entity="stock_movement",
        entity_id=str(movement.id),
        details={"food_id": str(food_id), "type": "purchase",
                 "quantity": str(quantity), "total_cost": str(total_cost)},
    )
    db.commit()
    return food, movement


def record_stock_adjustment(
    db: Session,
    farm_id: uuid.UUID,
    food_id: uuid.UUID,
    quantity: Decimal,
    reason: str,
    user_id: uuid.UUID,
    movement_date: datetime | None = None,
) -> tuple[Food, StockMovement]:
    """Manually adjust stock (e.g. for inventory corrections).
    Why? Physical counts may differ from system stock.
    Impact: positive quantity = increase, negative = decrease.
    """
    food = get_food(db, farm_id, food_id)
    stock_before = food.current_stock

    new_stock = food.current_stock + quantity
    if new_stock < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot reduce stock below 0. Current: {food.current_stock}",
        )
    food.current_stock = new_stock
    db.flush()

    movement = _record_stock_movement(
        db=db, farm_id=farm_id, food_id=food_id,
        movement_type="adjustment",
        quantity=quantity,
        stock_before=stock_before,
        stock_after=food.current_stock,
        registered_by=user_id,
        notes=reason,
        movement_date=movement_date,
    )

    db.commit()
    db.refresh(food)

    add_audit_log(
        db, user_id=str(user_id), farm_id=str(farm_id),
        action="create", entity="stock_movement",
        entity_id=str(movement.id),
        details={"food_id": str(food_id), "type": "adjustment",
                 "quantity": str(quantity), "reason": reason},
    )
    db.commit()
    return food, movement


def get_stock_movements(
    db: Session,
    farm_id: uuid.UUID,
    food_id: uuid.UUID | None = None,
    movement_type: str | None = None,
    limit: int = 100,
) -> Sequence[StockMovement]:
    """Get stock movement history for a farm, optionally filtered.
    Why? Provide full traceability of all inventory changes (HU011.2).
    Impact: Ordered by movement_date descending (newest first).
    """
    stmt = select(StockMovement).where(StockMovement.farm_id == farm_id)
    if food_id:
        stmt = stmt.where(StockMovement.food_id == food_id)
    if movement_type:
        stmt = stmt.where(StockMovement.movement_type == movement_type)
    stmt = stmt.order_by(StockMovement.movement_date.desc()).limit(limit)
    return db.execute(stmt).scalars().all()


def get_low_stock_foods(db: Session, farm_id: uuid.UUID) -> Sequence[Food]:
    """Get all food items where current_stock <= min_stock_alert.
    Why? Trigger alerts for reordering (HU011.3).
    """
    stmt = select(Food).where(
        Food.farm_id == farm_id,
        Food.is_active.is_(True),
        Food.min_stock_alert.isnot(None),
        Food.current_stock <= Food.min_stock_alert,
    ).order_by(
        (Food.current_stock / func.nullif(Food.min_stock_alert, 0)).asc()
    )
    return db.execute(stmt).scalars().all()
