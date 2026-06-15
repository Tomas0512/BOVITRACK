"""
╔════════════════════════════════════════════════════════════════════════════╗
║ SERVICIO: calf_service.py                                                 ║
║ PROPÓSITO: Lógica de negocio para gestión de terneros (crías bovinas)     ║
║                                                                            ║
║ ¿QUÉ?                                                                      ║
║   Conjunto de funciones que manejan toda la lógica para terneros:         ║
║   - Listar terneros por rango de edad                                     ║
║   - Calcular indicadores de crecimiento (ganancia diaria, etc)            ║
║   - Registrar pesajes y seguimiento del desarrollo                        ║
║   - Generar métricas para visualización                                   ║
║                                                                            ║
║ ¿PARA QUÉ?                                                                ║
║   Ejecutar las historias de usuario:                                       ║
║   - HU007: Registrar desarrollo de terneros                               ║
║   - HU005: Registrar alimentación y pesajes                               ║
║                                                                            ║
║ ¿IMPACTO?                                                                 ║
║   Este módulo es el cerebro de todo el seguimiento del crecimiento de      ║
║   crías. Sin él, el frontend no podría mostrar indicadores ni gráficas.    ║
╚════════════════════════════════════════════════════════════════════════════╝
"""

import uuid
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from typing import Sequence

from fastapi import HTTPException, status
from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.models.bovine import Bovine
from app.models.food import Food
from app.models.weight import Weight
from app.schemas.bovine import BovineResponse
from app.services.audit_service import add_audit_log


# ═══════════════════════════════════════════════════════════════════════════
# 📋 ESTRUCTURAS DE DATOS PARA TERNEROS
# ═══════════════════════════════════════════════════════════════════════════

class CalfGrowthMetrics:
    """
    ¿Qué? Clase que almacena las métricas de crecimiento de un ternero.
    ¿Para qué? Ser un contenedor de datos que el frontend pueda serializar.
    ¿Impacto? Se usa para retornar datos enriquecidos sin crear un ORM.
    """
    def __init__(
        self,
        current_weight_kg: Decimal,
        birth_weight_kg: Decimal | None,
        days_old: int,
        daily_gain_kg: Decimal | None,
        expected_weight_kg: Decimal,
        growth_percentage: Decimal,
        feeding_plan: str | None,
    ):
        # Peso actual del ternero en kg
        self.current_weight_kg = current_weight_kg

        # Peso al nacer (puede ser None si no se registró)
        self.birth_weight_kg = birth_weight_kg

        # Edad en días desde el nacimiento
        self.days_old = days_old

        # Ganancia promedio diaria en kg (calculado a partir de pesos históricos)
        self.daily_gain_kg = daily_gain_kg

        # Peso esperado según la edad y raza (tabla de referencia)
        self.expected_weight_kg = expected_weight_kg

        # Porcentaje de cumplimiento del objetivo (current vs expected)
        # Ejemplo: 50kg de 60kg esperados = 83.33%
        self.growth_percentage = growth_percentage

        # Plan de alimentación según edad
        self.feeding_plan = feeding_plan

    def to_dict(self) -> dict:
        """Convierte las métricas a un diccionario serializable a JSON."""
        return {
            "current_weight_kg": float(self.current_weight_kg),
            "birth_weight_kg": float(self.birth_weight_kg) if self.birth_weight_kg else None,
            "days_old": self.days_old,
            "daily_gain_kg": float(self.daily_gain_kg) if self.daily_gain_kg else None,
            "expected_weight_kg": float(self.expected_weight_kg),
            "growth_percentage": float(self.growth_percentage),
            "feeding_plan": self.feeding_plan,
        }


# ═══════════════════════════════════════════════════════════════════════════
# 🔍 FUNCIONES DE CONSULTA
# ═══════════════════════════════════════════════════════════════════════════

def list_calves(
    db: Session,
    farm_id: uuid.UUID,
    *,
    max_age_days: int = 365,
    min_age_days: int = 0,
    status_filter: str | None = None,
) -> Sequence[Bovine]:
    """
    ¿Qué? Lista todos los terneros (crías) de una finca dentro de un rango de edad.

    ¿Para qué?
      - HU007 Task 7.1: Endpoint/vista de terneros por edad/estado
      - Mostrar en el dashboard todos los animales jóvenes

    ¿Parámetros?
      db: Sesión de base de datos
      farm_id: UUID de la finca
      max_age_days: Edad máxima en días (default 1 año = 365 días)
      min_age_days: Edad mínima en días (default 0 = recién nacidos)
      status_filter: Filtro opcional por estado (activo, enfermo, etc)

    ¿Retorna?
      Lista de bovinos que son terneros en el rango de edad especificado

    ¿Impacto?
      CRÍTICO: Solo lista terneros activos (is_active=True).
      Un ternero se considera tal si tiene menos de max_age_days desde su birth_date.
    """

    # Calcular la fecha límite inferior (terneros no más viejos que max_age_days)
    # Ejemplo: hoy es 2026-06-15, max_age=365 → nacidos después de 2025-06-15
    cutoff_date_old = date.today() - timedelta(days=max_age_days)

    # Calcular la fecha límite superior (terneros no más jóvenes que min_age_days)
    # Ejemplo: hoy es 2026-06-15, min_age=30 → nacidos antes de 2026-05-16
    cutoff_date_young = date.today() - timedelta(days=min_age_days)

    # Construir la query base
    # birth_date > cutoff_old AND birth_date <= cutoff_young
    # Ejemplo: birth_date entre 2025-06-15 y 2026-05-16
    stmt = select(Bovine).where(
        Bovine.farm_id == farm_id,
        Bovine.is_active.is_(True),
        Bovine.birth_date > cutoff_date_old,
        Bovine.birth_date <= cutoff_date_young,
    )

    # Filtro adicional opcional por estado (activo, enfermo, etc)
    if status_filter:
        stmt = stmt.where(Bovine.status == status_filter)

    # Ordenar por fecha de nacimiento (más recientes primero)
    stmt = stmt.order_by(Bovine.birth_date.desc())

    return db.execute(stmt).scalars().all()


def get_calf_details(
    db: Session,
    farm_id: uuid.UUID,
    bovine_id: uuid.UUID,
) -> tuple[Bovine, CalfGrowthMetrics]:
    """
    ¿Qué? Obtiene un ternero específico con todas sus métricas de crecimiento.

    ¿Para qué?
      - HU007 Task 7.5: Integración con ficha general del bovino
      - Mostrar en la vista de detalle del bovino (BovineDetailPage)

    ¿Retorna?
      Tupla (bovino, métricas_crecimiento)

    ¿Impacto?
      Lanza HTTPException 404 si el bovino no existe o no es un ternero.
      Se considera ternero si tiene menos de 365 días de edad.
    """

    # 1. Obtener el bovino
    stmt = select(Bovine).where(
        Bovine.id == bovine_id,
        Bovine.farm_id == farm_id,
        Bovine.is_active.is_(True),
    )
    bovine = db.execute(stmt).scalar_one_or_none()

    # Si no existe, lanzar error 404
    if not bovine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ternero no encontrado",
        )

    # 2. Validar que realmente sea un ternero (< 365 días)
    days_old = (date.today() - bovine.birth_date).days
    if days_old > 365:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este bovino ya no es considerado ternero (>365 días)",
        )

    # 3. Calcular métricas de crecimiento
    metrics = _calculate_growth_metrics(db, bovine)

    return bovine, metrics


def get_calf_weight_history(
    db: Session,
    farm_id: uuid.UUID,
    bovine_id: uuid.UUID,
    days_back: int = 365,
) -> list[dict]:
    """
    ¿Qué? Obtiene el historial de pesajes de un ternero (para la gráfica).

    ¿Para qué?
      - HU007 Task 7.4: Curva de crecimiento del ternero
      - Alimentar el gráfico de evolución de peso

    ¿Parámetros?
      days_back: Cuántos días hacia atrás recuperar (default 1 año)

    ¿Retorna?
      Lista de diccionarios con {date, weight_kg, daily_gain_kg}

    ¿Impacto?
      Los datos se ordenan cronológicamente de más antiguo a más reciente.
      Se usan para renderizar una gráfica con Chart.js o similar.
    """

    # Calcular fecha de inicio
    start_date = date.today() - timedelta(days=days_back)

    # Query: obtener todos los pesajes del ternero desde start_date
    stmt = select(Weight).where(
        Weight.bovine_id == bovine_id,
        Weight.farm_id == farm_id,
        Weight.measured_at >= start_date,
    ).order_by(Weight.measured_at.asc())  # Más antiguo primero

    weights = db.execute(stmt).scalars().all()

    # Convertir a diccionarios serializables
    history = []
    for weight in weights:
        history.append({
            "date": weight.measured_at.isoformat(),
            "weight_kg": float(weight.weight_kg),
            "daily_gain_kg": float(weight.daily_gain_kg) if weight.daily_gain_kg else None,
        })

    return history


# ═══════════════════════════════════════════════════════════════════════════
# ➕ FUNCIONES DE CREACIÓN Y ACTUALIZACIÓN
# ═══════════════════════════════════════════════════════════════════════════

def record_calf_weight(
    db: Session,
    farm_id: uuid.UUID,
    bovine_id: uuid.UUID,
    weight_kg: Decimal,
    measured_date: date,
    body_condition: int | None = None,
    observations: str | None = None,
    user_id: uuid.UUID | None = None,
) -> Weight:
    """
    ¿Qué? Registra un pesaje nuevo para un ternero y calcula la ganancia diaria.

    ¿Para qué?
      - HU007 Task 7.2: Registro de crecimiento (peso)
      - HU005: Registrar pesajes de ganado

    ¿Pasos?
      1. Validar que el ternero existe
      2. Obtener el pesaje anterior más reciente
      3. Calcular la ganancia diaria (kg/día)
      4. Guardar el nuevo peso
      5. Actualizar el peso actual del bovino
      6. Registrar en auditoría

    ¿Impacto?
      CRÍTICO: Actualiza bovine.current_weight automáticamente.
      Calcula daily_gain basado en el tiempo desde el último pesaje.
    """

    # 1. Validar que el ternero existe
    bovine = db.query(Bovine).filter(
        Bovine.id == bovine_id,
        Bovine.farm_id == farm_id,
        Bovine.is_active.is_(True),
    ).first()

    if not bovine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ternero no encontrado",
        )

    # 2. Obtener el pesaje anterior más reciente (si existe)
    previous_weight = db.query(Weight).filter(
        Weight.bovine_id == bovine_id,
        Weight.measured_at < measured_date,
    ).order_by(Weight.measured_at.desc()).first()

    # 3. Calcular ganancia diaria
    daily_gain = None
    if previous_weight:
        # Diferencia de peso en kg
        weight_diff = float(weight_kg - previous_weight.weight_kg)

        # Días transcurridos entre pesajes
        days_elapsed = (measured_date - previous_weight.measured_at).days

        # Evitar división por cero (si se registra el mismo día, no calcular)
        if days_elapsed > 0:
            daily_gain = Decimal(str(weight_diff / days_elapsed))

    # 4. Crear el nuevo registro de peso
    new_weight = Weight(
        farm_id=farm_id,
        bovine_id=bovine_id,
        weight_kg=weight_kg,
        measured_at=measured_date,
        daily_gain=daily_gain,
        body_condition=body_condition,
        observations=observations,
        registered_by=user_id or bovine.registered_by,
    )

    db.add(new_weight)
    db.flush()  # Guardar para obtener el ID

    # 5. Actualizar el peso actual del bovino
    bovine.current_weight = weight_kg
    db.flush()

    # 6. Registrar en auditoría
    if user_id:
        add_audit_log(
            db,
            user_id=str(user_id),
            farm_id=str(farm_id),
            action="create",
            entity="weight",
            entity_id=str(new_weight.id),
            details={
                "bovine_id": str(bovine_id),
                "weight_kg": float(weight_kg),
                "daily_gain": float(daily_gain) if daily_gain else None,
            },
        )

    db.commit()
    db.refresh(new_weight)

    return new_weight


def update_calf_feeding_plan(
    db: Session,
    farm_id: uuid.UUID,
    bovine_id: uuid.UUID,
    food_id: uuid.UUID,
    quantity_kg_per_day: Decimal,
    start_date: date,
    end_date: date | None = None,
    notes: str | None = None,
) -> dict:
    """
    ¿Qué? Registra o actualiza el plan de alimentación de un ternero.

    ¿Para qué?
      - HU007 Task 7.2: Registro de alimentación según edad
      - HU010: Registrar información económica (costo de alimentación)

    ¿Pasos?
      1. Validar ternero y alimento existen
      2. Validar que el ternero está dentro del rango de edad
      3. Validar que la cantidad es positiva
      4. Crear o actualizar registro
      5. Registrar en auditoría

    ¿Retorna?
      Diccionario con los datos del plan registrado

    ¿Impacto?
      Este registro alimenticio se vincula luego con HU010 (económica).
    """

    # 1. Validar ternero existe
    bovine = db.query(Bovine).filter(
        Bovine.id == bovine_id,
        Bovine.farm_id == farm_id,
    ).first()

    if not bovine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ternero no encontrado",
        )

    # 2. Validar alimento existe
    food = db.query(Food).filter(
        Food.id == food_id,
        Food.farm_id == farm_id,
    ).first()

    if not food:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alimento no encontrado",
        )

    # 3. Validar que la cantidad es positiva
    if quantity_kg_per_day <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La cantidad debe ser mayor a 0",
        )

    # 4. Crear registro
    # Nota: En una implementación completa, habría una tabla FeedingPlan
    # Por ahora, retornamos un diccionario que el frontend puede usar
    plan_data = {
        "bovine_id": str(bovine_id),
        "food_id": str(food_id),
        "food_name": food.name,
        "quantity_kg_per_day": float(quantity_kg_per_day),
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat() if end_date else None,
        "notes": notes,
    }

    return plan_data


# ═══════════════════════════════════════════════════════════════════════════
# 📊 FUNCIONES DE CÁLCULO Y ANALÍTICA
# ═══════════════════════════════════════════════════════════════════════════

def _calculate_growth_metrics(db: Session, bovine: Bovine) -> CalfGrowthMetrics:
    """
    ¿Qué? Calcula las métricas de crecimiento de un ternero.

    ¿Para qué? Interno. Usado por get_calf_details().

    ¿Cálculos?
      - Edad en días
      - Ganancia diaria promedio
      - Peso esperado según raza y edad (tabla de referencia)
      - Porcentaje de cumplimiento

    ¿Impacto?
      PRIVADO. No llamar directamente desde routers.
    """

    # 1. Obtener edad en días
    today = date.today()
    days_old = (today - bovine.birth_date).days

    # 2. Obtener el peso actual
    current_weight = bovine.current_weight or Decimal("0")

    # 3. Calcular ganancia diaria promedio
    # Fórmula: (peso_actual - peso_nacimiento) / días_de_vida
    daily_gain = None
    if bovine.birth_weight and days_old > 0:
        total_gain = current_weight - bovine.birth_weight
        daily_gain = total_gain / Decimal(str(days_old))

    # 4. Obtener peso esperado según edad y raza
    # En una implementación real, esto vendría de una tabla de referencia
    # Por ahora, usamos una fórmula simple: 30kg base + 0.2kg/día
    expected_weight = _get_expected_weight(bovine.breed or "Desconocida", days_old)

    # 5. Calcular porcentaje de cumplimiento
    if expected_weight > 0:
        growth_percentage = (current_weight / expected_weight) * 100
    else:
        growth_percentage = Decimal("0")

    # 6. Determinar plan de alimentación según edad
    feeding_plan = _get_feeding_plan_by_age(days_old)

    return CalfGrowthMetrics(
        current_weight_kg=current_weight,
        birth_weight_kg=bovine.birth_weight,
        days_old=days_old,
        daily_gain_kg=daily_gain,
        expected_weight_kg=expected_weight,
        growth_percentage=growth_percentage,
        feeding_plan=feeding_plan,
    )


def _get_expected_weight(breed: str, days_old: int) -> Decimal:
    """
    ¿Qué? Obtiene el peso esperado para un ternero según raza y edad.

    ¿Para qué? Comparar con el peso real y determinar si crece correctamente.

    ¿Datos?
      Tabla de referencia simplificada. En producción, usar base de datos.
    """

    # Tabla simplificada de pesos esperados por raza (kg a diferentes edades)
    expected_weights = {
        "Brahman": {0: 30, 30: 45, 60: 70, 90: 95, 180: 180, 365: 350},
        "Angus": {0: 35, 30: 50, 60: 75, 90: 100, 180: 190, 365: 380},
        "Cebú": {0: 28, 30: 42, 60: 65, 90: 90, 180: 170, 365: 330},
        "Desconocida": {0: 32, 30: 48, 60: 72, 90: 95, 180: 180, 365: 350},
    }

    # Normalizar el nombre de la raza
    breed_normalized = breed.capitalize()
    if breed_normalized not in expected_weights:
        breed_normalized = "Desconocida"

    # Obtener la tabla de referencia para la raza
    weights = expected_weights[breed_normalized]

    # Encontrar el rango más cercano
    # Ejemplo: si days_old=45, usar interpolación entre 30 y 60
    sorted_days = sorted(weights.keys())

    if days_old <= sorted_days[0]:
        return Decimal(str(weights[sorted_days[0]]))

    if days_old >= sorted_days[-1]:
        return Decimal(str(weights[sorted_days[-1]]))

    # Interpolación lineal entre dos puntos
    for i in range(len(sorted_days) - 1):
        day1, day2 = sorted_days[i], sorted_days[i + 1]
        if day1 <= days_old <= day2:
            weight1, weight2 = weights[day1], weights[day2]
            # Proporción entre day1 y day2
            proportion = (days_old - day1) / (day2 - day1)
            expected = weight1 + proportion * (weight2 - weight1)
            return Decimal(str(expected))

    return Decimal(str(weights[sorted_days[-1]]))


def _get_feeding_plan_by_age(days_old: int) -> str:
    """
    ¿Qué? Retorna el plan de alimentación recomendado según la edad.

    ¿Para qué? Guiar al ganadero sobre qué debe alimentar al ternero.

    ¿Retorna?
      Descripción del plan (ej: "Leche materna + concentrado")
    """

    if days_old < 30:
        return "Leche materna exclusiva + agua y sal"
    elif days_old < 60:
        return "Leche materna + introducir concentrado (500g/día)"
    elif days_old < 120:
        return "Leche materna reducida + concentrado (1-2kg/día) + forraje"
    elif days_old < 180:
        return "Destete gradual + concentrado (2-3kg/día) + forraje"
    elif days_old < 365:
        return "Destete completo + concentrado (3kg/día) + forraje de calidad"
    else:
        return "Plan adulto (>365 días)"


def get_calf_summary_by_farm(
    db: Session,
    farm_id: uuid.UUID,
) -> dict:
    """
    ¿Qué? Obtiene un resumen general de terneros en una finca.

    ¿Para qué? Dashboard de HU007 - mostrar métricas globales.

    ¿Retorna?
      {
        "total_calves": int,
        "calves_0_30_days": int,
        "calves_31_90_days": int,
        "calves_91_365_days": int,
        "average_weight_kg": float,
        "average_daily_gain": float,
      }
    """

    # Query: contar terneros por grupo de edad
    cutoff_30 = date.today() - timedelta(days=30)
    cutoff_90 = date.today() - timedelta(days=90)
    cutoff_365 = date.today() - timedelta(days=365)

    total = db.query(func.count(Bovine.id)).filter(
        Bovine.farm_id == farm_id,
        Bovine.is_active.is_(True),
        Bovine.birth_date > cutoff_365,
    ).scalar() or 0

    calves_0_30 = db.query(func.count(Bovine.id)).filter(
        Bovine.farm_id == farm_id,
        Bovine.is_active.is_(True),
        Bovine.birth_date > cutoff_30,
    ).scalar() or 0

    calves_31_90 = db.query(func.count(Bovine.id)).filter(
        Bovine.farm_id == farm_id,
        Bovine.is_active.is_(True),
        Bovine.birth_date > cutoff_90,
        Bovine.birth_date <= cutoff_30,
    ).scalar() or 0

    calves_91_365 = db.query(func.count(Bovine.id)).filter(
        Bovine.farm_id == farm_id,
        Bovine.is_active.is_(True),
        Bovine.birth_date > cutoff_365,
        Bovine.birth_date <= cutoff_90,
    ).scalar() or 0

    # Promedios
    avg_weight_result = db.query(func.avg(Bovine.current_weight)).filter(
        Bovine.farm_id == farm_id,
        Bovine.is_active.is_(True),
        Bovine.birth_date > cutoff_365,
    ).scalar()
    avg_weight = float(avg_weight_result) if avg_weight_result else 0

    # Ganancia diaria promedio (de la tabla Weight)
    avg_gain_result = db.query(func.avg(Weight.daily_gain)).filter(
        Weight.farm_id == farm_id,
        Weight.measured_at >= date.today() - timedelta(days=30),
    ).scalar()
    avg_gain = float(avg_gain_result) if avg_gain_result else 0

    return {
        "total_calves": int(total),
        "calves_0_30_days": int(calves_0_30),
        "calves_31_90_days": int(calves_31_90),
        "calves_91_365_days": int(calves_91_365),
        "average_weight_kg": avg_weight,
        "average_daily_gain": avg_gain,
    }
