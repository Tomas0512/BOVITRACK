"""
Seed: Generate test data for final presentation walkthrough.
Usage: docker compose exec be python seed_test_data.py

Creates:
  1. Demo user: admin@bovitrack.com / Demo1234!
  2. Demo farm "Hacienda El Porvenir"
  3. Land plots, paddocks, bovines, food items, stock movements
"""

import os
import uuid
from datetime import date, datetime, timedelta
from decimal import Decimal

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.database import Base
from app.models.user import User
from app.models.farm import Farm, UserFarm, LandPlot
from app.models.role import Role
from app.models.purpose import Purpose
from app.models.department import Department
from app.models.paddock import Paddock
from app.models.bovine import Bovine
from app.models.food import Food, StockMovement

DATABASE_URL = os.environ["DATABASE_URL"]
engine = create_engine(DATABASE_URL)


def get_or_create_role(db: Session, name: str, description: str) -> Role:
    role = db.query(Role).where(Role.name == name).first()
    if not role:
        role = Role(id=uuid.uuid4(), name=name, description=description)
        db.add(role)
        db.flush()
    return role


def get_or_create_purpose(db: Session, name: str, description: str) -> Purpose:
    purpose = db.query(Purpose).where(Purpose.name == name).first()
    if not purpose:
        purpose = Purpose(id=uuid.uuid4(), name=name, description=description)
        db.add(purpose)
        db.flush()
    return purpose


def main():
    with Session(engine) as db:
        # 1. Create demo user
        admin_role = get_or_create_role(db, "Administrador", "Acceso total al sistema")
        purpose = get_or_create_purpose(db, "Ganadería de cría", "Cría y levante de bovinos")

        user = db.query(User).where(User.email == "admin@bovitrack.com").first()
        if not user:
            from passlib.context import CryptContext
            pwd = CryptContext(schemes=["bcrypt"])
            user = User(
                id=uuid.uuid4(),
                email="admin@bovitrack.com",
                first_name="Admin",
                last_name="BoviTrack",
                document_type="CC",
                document_number="987654321",
                phone="+57 300 123 4567",
                hashed_password=pwd.hash("Demo1234!"),
                is_active=True,
                accepted_terms=True,
                accepted_data_policy=True,
            )
            db.add(user)
            db.flush()
            print("✓ Demo user created: admin@bovitrack.com / Demo1234!")

        # 2. Create demo farm
        farm = db.query(Farm).where(Farm.farm_identifier == "FIN-DEMO-001").first()
        if not farm:
            first_dept = db.query(Department).order_by(Department.name.asc()).first()
            dept_id = first_dept.id if first_dept else uuid.uuid4()
            farm = Farm(
                id=uuid.uuid4(),
                owner_id=user.id,
                name="Hacienda El Porvenir",
                address="Vereda La Esperanza, Km 5",
                department_id=dept_id,
                city_municipality="Rionegro",
                total_area=Decimal("150.00"),
                area_unit="hectareas",
                purpose_id=purpose.id,
                farm_identifier="FIN-DEMO-001",
                phone="+57 300 987 6543",
                is_active=True,
            )
            db.add(farm)
            db.flush()
            print(f"✓ Farm created: {farm.name}")

            # Assign admin role to user for this farm
            uf = db.query(UserFarm).where(
                UserFarm.user_id == user.id, UserFarm.farm_id == farm.id
            ).first()
            if not uf:
                uf = UserFarm(
                    id=uuid.uuid4(),
                    user_id=user.id,
                    farm_id=farm.id,
                    role_id=admin_role.id,
                    assigned_by=user.id,
                    is_active=True,
                )
                db.add(uf)
                print("✓ User linked to farm as Administrador")
        else:
            print("→ Farm already exists, skipping")

        # 3. Create land plots
        if farm:
            existing_plots = db.query(LandPlot).where(LandPlot.farm_id == farm.id).count()
            if existing_plots == 0:
                plots = [
                    LandPlot(id=uuid.uuid4(), farm_id=farm.id, name="Lote Norte", area=Decimal("50.00"), area_unit="hectareas", usage_type="pastoreo", max_capacity=80, is_active=True),
                    LandPlot(id=uuid.uuid4(), farm_id=farm.id, name="Lote Sur", area=Decimal("40.00"), area_unit="hectareas", usage_type="pastoreo", max_capacity=60, is_active=True),
                    LandPlot(id=uuid.uuid4(), farm_id=farm.id, name="Lote de Cultivo", area=Decimal("30.00"), area_unit="hectareas", usage_type="cultivo", max_capacity=0, is_active=True),
                ]
                for p in plots:
                    db.add(p)
                db.flush()
                print(f"✓ {len(plots)} land plots created")

        # 4. Create paddocks
            existing_paddocks = db.query(Paddock).where(Paddock.farm_id == farm.id).count()
            if existing_paddocks == 0:
                paddocks = [
                    Paddock(id=uuid.uuid4(), farm_id=farm.id, name="Potrero 1", area_hectares=Decimal("10.00"), max_capacity=25, coverage_status="bueno", pasture_type="kikuyo", status="libre"),
                    Paddock(id=uuid.uuid4(), farm_id=farm.id, name="Potrero 2", area_hectares=Decimal("8.00"), max_capacity=20, coverage_status="bueno", pasture_type="brachiaria", status="ocupado"),
                    Paddock(id=uuid.uuid4(), farm_id=farm.id, name="Potrero 3", area_hectares=Decimal("12.00"), max_capacity=30, coverage_status="regular", pasture_type="estrella", status="en_descanso", rest_start_date=date.today() - timedelta(days=15), rest_end_date=date.today() + timedelta(days=15)),
                ]
                for p in paddocks:
                    db.add(p)
                db.flush()
                print(f"✓ {len(paddocks)} paddocks created")

        # 5. Create bovines
            existing_bovines = db.query(Bovine).where(Bovine.farm_id == farm.id).count()
            if existing_bovines == 0:
                plots = db.query(LandPlot).where(LandPlot.farm_id == farm.id).all()
                plot_id = plots[0].id if plots else None
                bovines = [
                    Bovine(id=uuid.uuid4(), farm_id=farm.id, identification_number="BOV-001", name="Lucero", sex="hembra", breed="Holstein", color="Blanco y negro", birth_date=date(2021, 3, 15), birth_weight=Decimal("38.00"), current_weight=Decimal("520.00"), purpose="leche", status="activo", entry_type="nacimiento", entry_date=date(2021, 3, 15), land_plot_id=plot_id, registered_by=user.id),
                    Bovine(id=uuid.uuid4(), farm_id=farm.id, identification_number="BOV-002", name="Torito", sex="macho", breed="Brahmán", color="Gris", birth_date=date(2022, 7, 1), birth_weight=Decimal("42.00"), current_weight=Decimal("480.00"), purpose="carne", status="activo", entry_type="compra", entry_date=date(2022, 9, 15), land_plot_id=plot_id, registered_by=user.id),
                    Bovine(id=uuid.uuid4(), farm_id=farm.id, identification_number="BOV-003", name="Estrella", sex="hembra", breed="Normando", color="Rojo", birth_date=date(2020, 11, 20), birth_weight=Decimal("36.00"), current_weight=Decimal("550.00"), purpose="leche", status="activo", entry_type="nacimiento", entry_date=date(2020, 11, 20), land_plot_id=plot_id, registered_by=user.id),
                    Bovine(id=uuid.uuid4(), farm_id=farm.id, identification_number="BOV-004", name="Rayo", sex="macho", breed="Cebú", color="Blanco", birth_date=date(2023, 5, 10), birth_weight=Decimal("40.00"), current_weight=Decimal("200.00"), purpose="cria", status="activo", entry_type="nacimiento", entry_date=date(2023, 5, 10), land_plot_id=plot_id, registered_by=user.id),
                ]
                for b in bovines:
                    db.add(b)
                db.flush()
                print(f"✓ {len(bovines)} bovines created")

        # 6. Create food items
            existing_food = db.query(Food).where(Food.farm_id == farm.id).count()
            if existing_food == 0:
                foods = [
                    Food(id=uuid.uuid4(), farm_id=farm.id, name="Concentrado Premium", category="concentrado", unit_of_measure="kg", current_stock=Decimal("500.00"), min_stock_alert=Decimal("100.00"), cost_per_unit=Decimal("2500.00"), expiration_date=date.today() + timedelta(days=180), supplier="Distribuidora XYZ"),
                    Food(id=uuid.uuid4(), farm_id=farm.id, name="Sal Mineralizada", category="suplementos", unit_of_measure="kg", current_stock=Decimal("80.00"), min_stock_alert=Decimal("20.00"), cost_per_unit=Decimal("1200.00"), expiration_date=date.today() + timedelta(days=365), supplier="Minerales SA"),
                    Food(id=uuid.uuid4(), farm_id=farm.id, name="Vitamina ADE", category="vitaminas", unit_of_measure="litros", current_stock=Decimal("15.00"), min_stock_alert=Decimal("5.00"), cost_per_unit=Decimal("35000.00"), supplier="VetFarma"),
                ]
                for f in foods:
                    db.add(f)
                db.flush()
                print(f"✓ {len(foods)} food items created")

        # 7. Create stock movements
                food_ids = [f.id for f in foods]
                existing_movements = db.query(StockMovement).where(StockMovement.farm_id == farm.id).count()
                if existing_movements == 0 and len(food_ids) >= 2:
                    movements = [
                        StockMovement(id=uuid.uuid4(), farm_id=farm.id, food_id=food_ids[0], movement_type="purchase", quantity=Decimal("500.00"), unit_cost=Decimal("2500.00"), stock_before=Decimal("0"), stock_after=Decimal("500.00"), movement_date=datetime.now() - timedelta(days=30), registered_by=user.id, notes="Compra inicial"),
                        StockMovement(id=uuid.uuid4(), farm_id=farm.id, food_id=food_ids[0], movement_type="adjustment", quantity=Decimal("-50.00"), unit_cost=None, stock_before=Decimal("500.00"), stock_after=Decimal("450.00"), movement_date=datetime.now() - timedelta(days=7), registered_by=user.id, notes="Consumo semanal"),
                        StockMovement(id=uuid.uuid4(), farm_id=farm.id, food_id=food_ids[1], movement_type="purchase", quantity=Decimal("100.00"), unit_cost=Decimal("1200.00"), stock_before=Decimal("0"), stock_after=Decimal("100.00"), movement_date=datetime.now() - timedelta(days=15), registered_by=user.id, notes="Compra de sal mineralizada"),
                    ]
                    for m in movements:
                        db.add(m)
                    print(f"✓ {len(movements)} stock movements created")

        db.commit()
        print("\n✅ Test data seeding complete!")
        print("   Login: admin@bovitrack.com / Demo1234!")


if __name__ == "__main__":
    main()
