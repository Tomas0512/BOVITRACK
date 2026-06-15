import uuid
from datetime import date, timedelta
from decimal import Decimal
from typing import Sequence

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.economics import EconomicRecord
from app.schemas.economics import EconomicRecordCreate, EconomicRecordUpdate, EconomicIndicators
from app.services.audit_service import add_audit_log


def create_record(db: Session, farm_id: uuid.UUID, data: EconomicRecordCreate, user_id: uuid.UUID) -> EconomicRecord:
    record = EconomicRecord(
        farm_id=farm_id,
        registered_by=user_id,
        **data.model_dump(),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    add_audit_log(db, user_id=str(user_id), farm_id=str(farm_id), action="create", entity="economic_record", entity_id=str(record.id), details={"type": record.record_type, "amount": str(record.amount), "category": record.category})
    db.commit()
    return record


def list_records(
    db: Session,
    farm_id: uuid.UUID,
    record_type: str | None = None,
    category: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
) -> Sequence[EconomicRecord]:
    stmt = select(EconomicRecord).where(EconomicRecord.farm_id == farm_id)
    if record_type:
        stmt = stmt.where(EconomicRecord.record_type == record_type)
    if category:
        stmt = stmt.where(EconomicRecord.category == category)
    if date_from:
        stmt = stmt.where(EconomicRecord.record_date >= date_from)
    if date_to:
        stmt = stmt.where(EconomicRecord.record_date <= date_to)
    stmt = stmt.order_by(EconomicRecord.record_date.desc())
    return db.execute(stmt).scalars().all()


def get_record(db: Session, farm_id: uuid.UUID, record_id: uuid.UUID) -> EconomicRecord:
    stmt = select(EconomicRecord).where(EconomicRecord.id == record_id, EconomicRecord.farm_id == farm_id)
    record = db.execute(stmt).scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registro economico no encontrado")
    return record


def update_record(db: Session, farm_id: uuid.UUID, record_id: uuid.UUID, data: EconomicRecordUpdate, user_id: uuid.UUID) -> EconomicRecord:
    record = get_record(db, farm_id, record_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(record, field, value)
    db.commit()
    db.refresh(record)
    add_audit_log(db, user_id=str(user_id), farm_id=str(farm_id), action="update", entity="economic_record", entity_id=str(record.id), details={"type": record.record_type, "amount": str(record.amount)})
    db.commit()
    return record


def delete_record(db: Session, farm_id: uuid.UUID, record_id: uuid.UUID, user_id: uuid.UUID) -> None:
    record = get_record(db, farm_id, record_id)
    add_audit_log(db, user_id=str(user_id), farm_id=str(farm_id), action="delete", entity="economic_record", entity_id=str(record.id), details={"type": record.record_type})
    db.delete(record)
    db.commit()


def get_indicators(db: Session, farm_id: uuid.UUID, date_from: date | None = None, date_to: date | None = None) -> EconomicIndicators:
    base = select(EconomicRecord).where(EconomicRecord.farm_id == farm_id)
    if date_from:
        base = base.where(EconomicRecord.record_date >= date_from)
    if date_to:
        base = base.where(EconomicRecord.record_date <= date_to)

    records = db.execute(base).scalars().all()

    total_income = Decimal("0")
    total_expense = Decimal("0")
    income_by_category: dict[str, Decimal] = {}
    expense_by_category: dict[str, Decimal] = {}

    today = date.today()
    first_of_month = today.replace(day=1)
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

    balance = total_income - total_expense
    monthly_balance = monthly_income - monthly_expense

    if date_from and date_to:
        days = (date_to - date_from).days or 1
    else:
        days = 1

    return EconomicIndicators(
        total_income=total_income,
        total_expense=total_expense,
        balance=balance,
        income_by_category=income_by_category,
        expense_by_category=expense_by_category,
        monthly_income=monthly_income,
        monthly_expense=monthly_expense,
        monthly_balance=monthly_balance,
        avg_income_per_day=total_income / Decimal(str(days)) if days > 0 else Decimal("0"),
        avg_expense_per_day=total_expense / Decimal(str(days)) if days > 0 else Decimal("0"),
    )
