"""
Módulo: services/food_service.py
¿Qué? Capa de servicio para el módulo de alimentos (inventario) y consumos.
¿Para qué? Gestionar el catálogo de insumos alimentarios de cada finca,
           registrar consumos y descontar automáticamente el stock.
¿Impacto? El control de inventario es clave para evitar desabastecimiento.
          La vista v_low_stock_alerts depende de estos datos para las alertas.
"""

import uuid
from typing import Sequence

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.food import Consumption, Food
from app.schemas.food import ConsumptionCreate, FoodCreate, FoodUpdate


def create_food(db: Session, farm_id: uuid.UUID, data: FoodCreate) -> Food:
    """¿Qué? Registra un nuevo alimento en el inventario de la finca.
    ¿Para qué? Mantener un catálogo de insumos con stock, precio y proveedor.
    ¿Impacto? El alimento queda disponible para registrar consumos.
    """
    food = Food(farm_id=farm_id, **data.model_dump())
    db.add(food)
    db.commit()
    db.refresh(food)
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


def update_food(db: Session, farm_id: uuid.UUID, food_id: uuid.UUID, data: FoodUpdate) -> Food:
    """¿Qué? Actualiza los campos enviados de un alimento.
    ¿Para qué? Modificar precio, stock, proveedor, etc. sin reenviar todo.
    ¿Impacto? exclude_unset=True asegura actualización parcial segura.
    """
    food = get_food(db, farm_id, food_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(food, field, value)
    db.commit()
    db.refresh(food)
    return food


def delete_food(db: Session, farm_id: uuid.UUID, food_id: uuid.UUID) -> None:
    """¿Qué? Desactiva un alimento del inventario (soft delete).
    ¿Para qué? No eliminar físicamente para conservar el historial de consumos.
    ¿Impacto? El alimento deja de aparecer en listados pero sus consumos
              asociados se mantienen para auditoría.
    """
    food = get_food(db, farm_id, food_id)
    food.is_active = False
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
    if food.current_stock < data.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Stock insuficiente. Disponible: {food.current_stock} {food.unit_of_measure}",
        )

    # ¿Qué? Descontar la cantidad consumida del stock.
    # ¿Impacto? Si la transacción falla, el rollback restaura el stock original.
    food.current_stock -= data.quantity

    consumption = Consumption(
        farm_id=farm_id,
        registered_by=user_id,
        **data.model_dump(),
    )
    db.add(consumption)
    db.commit()
    db.refresh(consumption)
    return consumption


def list_consumptions(db: Session, farm_id: uuid.UUID, food_id: uuid.UUID | None = None) -> Sequence[Consumption]:
    """¿Qué? Lista los consumos registrados de una finca.
    ¿Para qué? Consultar el historial de alimentación, filtrable por alimento.
    ¿Impacto? Ordenados por fecha descendente para ver los más recientes primero.
    """
    stmt = select(Consumption).where(Consumption.farm_id == farm_id)
    if food_id:
        stmt = stmt.where(Consumption.food_id == food_id)
    stmt = stmt.order_by(Consumption.feeding_date.desc())
    return db.execute(stmt).scalars().all()
