"""
Módulo: modules/livestock/service/calves.py
HU007 - Desarrollo de terneros
¿Qué? Casos de uso de los terneros (bovinos de hasta 365 días): listado por
      edad, ficha con métricas de crecimiento, curva de peso, registro de
      pesajes y resumen de la finca. (El plan de alimentación vive en el
      módulo inventory: valida un alimento, y así ganado no depende de inventario.)
¿Para qué? Detectar a tiempo terneros que crecen por debajo de lo esperado
           para su raza y edad.
¿Impacto? Las tablas de referencia (peso esperado por raza y plan por edad) son
          funciones puras de este archivo. La fecha de "hoy" se inyecta para
          poder probar los cálculos de edad con una fecha fija.
"""

import uuid
from collections.abc import Callable, Sequence
from datetime import date, timedelta
from decimal import Decimal
from typing import Any

from app.modules.livestock.models import Bovine, Weight
from app.modules.livestock.repository import BovineRepository, WeightRepository
from app.shared.exceptions import BusinessRuleError, NotFoundError
from app.shared.ports import AuditRecorder

CALF_NOT_FOUND = "Ternero no encontrado"
NOT_A_CALF_ANYMORE = "Este bovino ya no es considerado ternero (>365 días)"
MEASURED_BEFORE_BIRTH = "La fecha de medición no puede ser anterior al nacimiento"
WEIGHT_ALREADY_ON_DATE = "Ya existe un pesaje registrado para esta fecha"


# ═══════════════════════════════════════════════════════════════════════════
# 📋 MÉTRICAS Y TABLAS DE REFERENCIA (funciones puras)
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


def calculate_growth_metrics(bovine: Bovine, today: date) -> CalfGrowthMetrics:
    """Edad, ganancia diaria promedio desde el nacimiento, peso esperado y % de cumplimiento."""
    days_old = (today - bovine.birth_date).days
    current_weight = bovine.current_weight or Decimal("0")
    daily_gain = None
    if bovine.birth_weight and days_old > 0:
        total_gain = current_weight - bovine.birth_weight
        daily_gain = total_gain / Decimal(str(days_old))
    expected_weight = _get_expected_weight(bovine.breed or "Desconocida", days_old)
    if expected_weight > 0:
        growth_percentage = (current_weight / expected_weight) * 100
    else:
        growth_percentage = Decimal("0")
    return CalfGrowthMetrics(
        current_weight_kg=current_weight,
        birth_weight_kg=bovine.birth_weight,
        days_old=days_old,
        daily_gain_kg=daily_gain,
        expected_weight_kg=expected_weight,
        growth_percentage=growth_percentage,
        feeding_plan=_get_feeding_plan_by_age(days_old),
    )


# ═══════════════════════════════════════════════════════════════════════════
# 🐄 CASOS DE USO
# ═══════════════════════════════════════════════════════════════════════════


class CalfService:
    """Casos de uso del módulo de terneros (HU007)."""

    def __init__(
        self,
        bovines: BovineRepository,
        weights: WeightRepository,
        record_audit: AuditRecorder,
        today: Callable[[], date] = date.today,
    ) -> None:
        self._bovines = bovines
        self._weights = weights
        self._record_audit = record_audit
        self._today = today

    def list_calves(
        self,
        farm_id: uuid.UUID,
        *,
        max_age_days: int = 365,
        min_age_days: int = 0,
        status_filter: str | None = None,
    ) -> Sequence[Bovine]:
        """Activos con edad entre min_age_days y max_age_days, los más jóvenes primero."""
        today = self._today()
        return self._bovines.list_active_born_between(
            farm_id,
            born_after=today - timedelta(days=max_age_days),
            born_on_or_before=today - timedelta(days=min_age_days),
            status=status_filter,
        )

    def get_calf_details(self, farm_id: uuid.UUID, bovine_id: uuid.UUID) -> tuple[Bovine, CalfGrowthMetrics]:
        bovine = self._bovines.get_active_in_farm(farm_id, bovine_id)
        if bovine is None:
            raise NotFoundError(CALF_NOT_FOUND)
        today = self._today()
        if (today - bovine.birth_date).days > 365:
            raise BusinessRuleError(NOT_A_CALF_ANYMORE)
        return bovine, calculate_growth_metrics(bovine, today)

    def get_calf_weight_history(
        self, farm_id: uuid.UUID, bovine_id: uuid.UUID, days_back: int = 365
    ) -> list[dict[str, Any]]:
        """Curva de peso (del más antiguo al más reciente) para graficar.

        El modelo guarda la ganancia en `daily_gain`; la respuesta la expone como
        `daily_gain_kg`. (Antes se leía weight.daily_gain_kg y respondía 500.)
        Cada punto lleva el `id` del pesaje, que WeightRecordResponse exige (bug #23:
        sin él, la ruta seguía en 500 con cualquier animal que tuviera pesajes).
        """
        start_date = self._today() - timedelta(days=days_back)
        return [
            {
                "id": weight.id,
                "date": weight.measured_at.isoformat(),
                "weight_kg": float(weight.weight_kg),
                "daily_gain_kg": float(weight.daily_gain) if weight.daily_gain is not None else None,
            }
            for weight in self._weights.list_for_bovine(farm_id, bovine_id, since=start_date)
        ]

    def record_calf_weight(
        self,
        farm_id: uuid.UUID,
        bovine_id: uuid.UUID,
        weight_kg: Decimal,
        measured_date: date,
        body_condition: int | None = None,
        observations: str | None = None,
        user_id: uuid.UUID | None = None,
    ) -> Weight:
        """Registra un pesaje del ternero, calcula su ganancia diaria y actualiza su peso actual."""
        bovine = self._bovines.get_active_in_farm(farm_id, bovine_id)
        if bovine is None:
            raise NotFoundError(CALF_NOT_FOUND)
        if measured_date < bovine.birth_date:
            raise BusinessRuleError(MEASURED_BEFORE_BIRTH)
        if self._weights.exists_on_date(bovine_id, measured_date):
            raise BusinessRuleError(WEIGHT_ALREADY_ON_DATE)

        previous = self._weights.previous_before(bovine_id, measured_date)
        daily_gain = None
        if previous:
            weight_diff = float(weight_kg - previous.weight_kg)
            days_elapsed = (measured_date - previous.measured_at).days
            if days_elapsed > 0:
                daily_gain = Decimal(str(weight_diff / days_elapsed))

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
        self._weights.add(new_weight)
        self._weights.flush()
        latest = self._weights.latest_measured_at(bovine_id)
        if latest is None or measured_date >= latest:
            bovine.current_weight = weight_kg
            self._weights.flush()
        if user_id:
            self._record_audit(
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
        self._weights.commit()
        self._weights.refresh(new_weight)
        return new_weight

    def get_calf_summary_by_farm(self, farm_id: uuid.UUID) -> dict[str, Any]:
        """Totales por rango de edad, peso promedio y ganancia diaria promedio (últimos 30 días)."""
        today = self._today()
        cutoff_30 = today - timedelta(days=30)
        cutoff_90 = today - timedelta(days=90)
        cutoff_365 = today - timedelta(days=365)

        avg_weight_result = self._bovines.avg_current_weight_born_after(farm_id, cutoff_365)
        avg_gain_result = self._weights.avg_daily_gain_of_calves(farm_id, cutoff_365, today - timedelta(days=30))
        return {
            "total_calves": int(self._bovines.count_active_born(farm_id, cutoff_365)),
            "calves_0_30_days": int(self._bovines.count_active_born(farm_id, cutoff_30)),
            "calves_31_90_days": int(self._bovines.count_active_born(farm_id, cutoff_90, cutoff_30)),
            "calves_91_365_days": int(self._bovines.count_active_born(farm_id, cutoff_365, cutoff_90)),
            "average_weight_kg": float(avg_weight_result) if avg_weight_result else 0,
            "average_daily_gain": float(avg_gain_result) if avg_gain_result else 0,
        }
