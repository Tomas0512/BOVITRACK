"""
Módulo: modules/economics/service.py
¿Qué? Reglas de negocio de la información económica: registrar, consultar,
      corregir y eliminar ingresos y egresos, y calcular los indicadores
      (balance total y del mes, totales por categoría, promedio diario).
¿Para qué? Que el ganadero sepa si la finca gana o pierde dinero.
¿Impacto? No conoce HTTP ni SQLAlchemy. La auditoría llega como colaborador
          inyectado y la fecha de "hoy" también, para poder probar el cálculo
          mensual con una fecha fija.
"""

import uuid
from collections.abc import Callable, Sequence
from datetime import date
from decimal import Decimal

from app.modules.economics.models import EconomicRecord
from app.modules.economics.repository import EconomicRecordRepository
from app.modules.economics.schemas import EconomicIndicators, EconomicRecordCreate, EconomicRecordUpdate
from app.shared.ports import AuditRecorder
from app.shared.exceptions import NotFoundError

RECORD_NOT_FOUND = "Registro economico no encontrado"


class EconomicsService:
    """Casos de uso del módulo económico."""

    def __init__(
        self,
        repository: EconomicRecordRepository,
        record_audit: AuditRecorder,
        today: Callable[[], date] = date.today,
    ) -> None:
        self._repo = repository
        self._record_audit = record_audit
        self._today = today

    def create_record(self, farm_id: uuid.UUID, data: EconomicRecordCreate, user_id: uuid.UUID) -> EconomicRecord:
        record = EconomicRecord(farm_id=farm_id, registered_by=user_id, **data.model_dump())
        self._repo.add(record)
        self._repo.commit()
        self._repo.refresh(record)
        self._record_audit(
            user_id=str(user_id),
            farm_id=str(farm_id),
            action="create",
            entity="economic_record",
            entity_id=str(record.id),
            details={"type": record.record_type, "amount": str(record.amount), "category": record.category},
        )
        self._repo.commit()
        return record

    def list_records(
        self,
        farm_id: uuid.UUID,
        record_type: str | None = None,
        category: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> Sequence[EconomicRecord]:
        """Movimientos de la finca, los más recientes primero."""
        return self._repo.list_by_farm(
            farm_id, record_type=record_type, category=category, date_from=date_from, date_to=date_to
        )

    def get_record(self, farm_id: uuid.UUID, record_id: uuid.UUID) -> EconomicRecord:
        record = self._repo.get_in_farm(farm_id, record_id)
        if record is None:
            raise NotFoundError(RECORD_NOT_FOUND)
        return record

    def update_record(
        self, farm_id: uuid.UUID, record_id: uuid.UUID, data: EconomicRecordUpdate, user_id: uuid.UUID
    ) -> EconomicRecord:
        record = self.get_record(farm_id, record_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(record, field, value)
        self._repo.commit()
        self._repo.refresh(record)
        self._record_audit(
            user_id=str(user_id),
            farm_id=str(farm_id),
            action="update",
            entity="economic_record",
            entity_id=str(record.id),
            details={"type": record.record_type, "amount": str(record.amount)},
        )
        self._repo.commit()
        return record

    def delete_record(self, farm_id: uuid.UUID, record_id: uuid.UUID, user_id: uuid.UUID) -> None:
        record = self.get_record(farm_id, record_id)
        self._record_audit(
            user_id=str(user_id),
            farm_id=str(farm_id),
            action="delete",
            entity="economic_record",
            entity_id=str(record.id),
            details={"type": record.record_type},
        )
        self._repo.delete(record)
        self._repo.commit()

    def get_indicators(
        self, farm_id: uuid.UUID, date_from: date | None = None, date_to: date | None = None
    ) -> EconomicIndicators:
        """Calcula balance, totales por categoría, mes en curso y promedio diario.

        El promedio diario divide por los días del rango pedido; si no se pidió
        rango, por los días entre el primer y el último movimiento (mínimo 1).
        """
        records = self._repo.list_by_farm(farm_id, date_from=date_from, date_to=date_to, newest_first=False)

        total_income = Decimal("0")
        total_expense = Decimal("0")
        income_by_category: dict[str, Decimal] = {}
        expense_by_category: dict[str, Decimal] = {}

        first_of_month = self._today().replace(day=1)
        monthly_income = Decimal("0")
        monthly_expense = Decimal("0")

        for r in records:
            if r.record_type == "ingreso":
                total_income += r.amount
                income_by_category[r.category] = income_by_category.get(r.category, Decimal("0")) + r.amount
                if r.record_date >= first_of_month:
                    monthly_income += r.amount
            else:
                total_expense += r.amount
                expense_by_category[r.category] = expense_by_category.get(r.category, Decimal("0")) + r.amount
                if r.record_date >= first_of_month:
                    monthly_expense += r.amount

        if date_from and date_to:
            # Rango inclusivo (los filtros usan >= y <=): del 1 al 10 son 10 días, no 9.
            days = (date_to - date_from).days + 1
        elif records:
            dates = [r.record_date for r in records]
            span = (max(dates) - min(dates)).days + 1
            days = span if span > 0 else 1
        else:
            days = 1

        return EconomicIndicators(
            total_income=total_income,
            total_expense=total_expense,
            balance=total_income - total_expense,
            income_by_category=income_by_category,
            expense_by_category=expense_by_category,
            monthly_income=monthly_income,
            monthly_expense=monthly_expense,
            monthly_balance=monthly_income - monthly_expense,
            avg_income_per_day=total_income / Decimal(str(days)) if days > 0 else Decimal("0"),
            avg_expense_per_day=total_expense / Decimal(str(days)) if days > 0 else Decimal("0"),
        )
