"""
Seed: Comprehensive test data for BoviTrack presentation.
Usage: docker compose exec be python seed_test_data.py

Creates:
  1. Demo user: admin@bovitrack.com / Demo1234!
  2. Farm "Hacienda El Porvenir" with 5 land plots, 8 paddocks
  3. 30 bovines with weights, reproductive events, treatments, milk records
  4. 8 food items with stock movements
  5. 15+ economic records (income & expenses)
  6. 5 animal movements
  7. 6 sanitary plans
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
from app.models.weight import Weight
from app.models.food import Food, StockMovement
from app.models.reproductive_event import ReproductiveEvent
from app.models.treatment import Treatment
from app.models.milk_production import MilkProduction
from app.models.economics import EconomicRecord
from app.models.movement import AnimalMovement
from app.models.sanitary_plan import SanitaryPlan
from app.services.audit_service import add_audit_log

DATABASE_URL = os.environ["DATABASE_URL"]
engine = create_engine(DATABASE_URL)


def get_or_create_role(db: Session, name: str) -> Role:
    role = db.query(Role).where(Role.name == name).first()
    if not role:
        role = Role(id=uuid.uuid4(), name=name, description=name, is_active=True)
        db.add(role)
        db.flush()
        print(f"  + Role '{name}' created")
    return role


def get_or_create_purpose(db: Session, name: str) -> Purpose:
    purpose = db.query(Purpose).where(Purpose.name == name).first()
    if not purpose:
        purpose = Purpose(id=uuid.uuid4(), name=name, description=name)
        db.add(purpose)
        db.flush()
    return purpose


# ── Bovine data ────────────────────────────────────────────────────────────
# We define 30 bovines with structure for parent references
# (id_num, name, sex, breed, color, birth_date_offset_days, birth_weight, purpose, entry_type)
BOVINE_TEMPLATES = [
    # Females — Holstein (dairy)
    ("BOV-001", "Lucero",     "hembra", "Holstein", "Blanco y negro",  2200, 38, "leche", "nacimiento"),
    ("BOV-005", "Margarita",  "hembra", "Holstein", "Blanco y negro",  1800, 36, "leche", "nacimiento"),
    ("BOV-009", "Clavel",     "hembra", "Holstein", "Blanco y negro",  1500, 37, "leche", "nacimiento"),
    ("BOV-013", "Rosa",       "hembra", "Holstein", "Blanco y negro",  1200, 35, "leche", "nacimiento"),
    ("BOV-017", "Azucena",    "hembra", "Holstein", "Blanco y negro",   800, 39, "leche", "nacimiento"),
    ("BOV-021", "Tulipán",    "hembra", "Holstein", "Blanco y negro",   400, 34, "leche", "nacimiento"),
    # Females — Normando (dual purpose)
    ("BOV-002", "Estrella",   "hembra", "Normando", "Rojo",            2100, 36, "doble_proposito", "nacimiento"),
    ("BOV-010", "Luna",       "hembra", "Normando", "Rojo oscuro",     1400, 37, "doble_proposito", "nacimiento"),
    ("BOV-018", "Sol",        "hembra", "Normando", "Rojo claro",       700, 35, "doble_proposito", "nacimiento"),
    # Females — Brahmán (beef)
    ("BOV-006", "Morena",     "hembra", "Brahman",  "Gris claro",      1900, 40, "carne", "nacimiento"),
    ("BOV-014", "Paloma",     "hembra", "Brahman",  "Gris oscuro",     1100, 42, "carne", "nacimiento"),
    ("BOV-022", "Candela",    "hembra", "Brahman",  "Gris",             500, 38, "carne", "nacimiento"),
    # Females — Gyr (dairy)
    ("BOV-003", "Jade",       "hembra", "Gyr",      "Rojo jaspeado",   2000, 34, "leche", "nacimiento"),
    ("BOV-011", "Perla",      "hembra", "Gyr",      "Rojo",            1300, 35, "leche", "nacimiento"),
    # Female — Cebú (beef)
    ("BOV-015", "Nube",       "hembra", "Cebu",     "Blanco",          1000, 39, "carne", "nacimiento"),

    # Males — Holstein
    ("BOV-007", "Tormenta",   "macho",  "Holstein", "Blanco y negro",  1700, 44, "cria", "nacimiento"),
    ("BOV-019", "Relámpago",  "macho",  "Holstein", "Blanco y negro",   600, 42, "cria", "nacimiento"),
    # Males — Brahmán
    ("BOV-004", "Torito",     "macho",  "Brahman",  "Gris",            1500, 42, "carne", "compra"),
    ("BOV-012", "Furia",      "macho",  "Brahman",  "Gris oscuro",     1250, 45, "carne", "nacimiento"),
    ("BOV-020", "Trueno",     "macho",  "Brahman",  "Gris claro",       550, 41, "cria", "nacimiento"),
    # Males — Cebú
    ("BOV-008", "Rayo",       "macho",  "Cebu",     "Blanco",          1600, 40, "cria", "nacimiento"),
    ("BOV-016", "Centella",   "macho",  "Cebu",     "Blanco crema",     900, 43, "carne", "nacimiento"),
    ("BOV-023", "Volcán",     "macho",  "Cebu",     "Blanco",           300, 39, "cria", "nacimiento"),
    # Males — Normando
    ("BOV-024", "Bronco",     "macho",  "Normando", "Rojo",             200, 41, "carne", "nacimiento"),
    ("BOV-027", "Fiero",      "macho",  "Normando", "Rojo oscuro",      100, 40, "cria", "nacimiento"),
    # Males — Gyr
    ("BOV-025", "Indio",      "macho",  "Gyr",      "Rojo jaspeado",   250, 38, "cria", "nacimiento"),
    ("BOV-028", "Rajá",       "macho",  "Gyr",      "Rojo",             50,  37, "cria", "nacimiento"),

    # Some sold/dead animals for variety
    ("BOV-026", "Viejo Matías","macho", "Brahman",  "Gris",           2500, 46, "carne", "compra"),   # sold, old
    ("BOV-029", "Pintita",    "hembra", "Holstein", "Blanco y negro",  2800, 36, "leche", "nacimiento"), # dead
    ("BOV-030", "Chaparro",   "macho",  "Cebu",     "Blanco",          50,  38, "cria", "nacimiento"), # very young
]

# Parent assignments (father_id, mother_id) by child id_num
FAMILY_TREE = {
    # child: (father_id_num, mother_id_num)
    "BOV-005": ("BOV-004", "BOV-001"),
    "BOV-006": ("BOV-004", "BOV-002"),
    "BOV-009": ("BOV-007", "BOV-005"),
    "BOV-010": ("BOV-004", "BOV-002"),
    "BOV-013": ("BOV-007", "BOV-009"),
    "BOV-014": ("BOV-012", "BOV-006"),
    "BOV-017": ("BOV-008", "BOV-013"),
    "BOV-018": ("BOV-012", "BOV-010"),
    "BOV-021": ("BOV-019", "BOV-017"),
    "BOV-022": ("BOV-012", "BOV-014"),
    "BOV-024": ("BOV-012", "BOV-002"),
    "BOV-027": ("BOV-020", "BOV-018"),
    "BOV-028": ("BOV-025", "BOV-011"),
    "BOV-030": ("BOV-023", "BOV-015"),
}

# Treat some as sold/dead
SOLD_BOVINES = {"BOV-026"}
DEAD_BOVINES = {"BOV-029"}

# Weight data: each bovine gets 4 weight records at different ages
# weight_at = (days_after_birth, weight_multiplier_of_birth)
WEIGHT_PROGRESSION = [
    (60, 1.8),    # ~2 months
    (180, 3.5),   # ~6 months
    (365, 6.0),   # ~1 year
]

# Females eligible for reproduction (older than 18 months)
REPRODUCTIVE_FEMALES = [
    "BOV-001", "BOV-002", "BOV-003", "BOV-005", "BOV-006",
    "BOV-009", "BOV-010", "BOV-011", "BOV-013", "BOV-014",
    "BOV-015", "BOV-017", "BOV-018", "BOV-022",
]

# Dairy females (for milk production)
DAIRY_FEMALES = ["BOV-001", "BOV-005", "BOV-009", "BOV-013", "BOV-017", "BOV-021"]


def main():
    with Session(engine) as db:
        now = datetime.utcnow()

        # 1. Ensure roles exist
        admin_role = get_or_create_role(db, "Administrador")
        operario_role = get_or_create_role(db, "Operario")
        if not admin_role:
            print("Please run: docker compose exec be python seed_roles.py")
            return

        purpose = get_or_create_purpose(db, "Ganadería de cría")

        # 2. Demo user
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
                email_verified=True,
                accepted_terms=True,
                accepted_data_policy=True,
            )
            db.add(user)
            db.flush()
            db.commit()
            db.refresh(user)
            print("✓ Demo user created: admin@bovitrack.com / Demo1234!")
        else:
            print("→ Demo user already exists")

        # 2b. Usuario desactivado — necesario para probar el flujo público
        # de "solicitar reactivación" (el endpoint rechaza con 400 a
        # cuentas activas, así que la suite E2E necesita una cuenta off).
        inactive_user = db.query(User).where(User.email == "exempleado@bovitrack.com").first()
        if not inactive_user:
            from passlib.context import CryptContext
            pwd = CryptContext(schemes=["bcrypt"])
            inactive_user = User(
                id=uuid.uuid4(),
                email="exempleado@bovitrack.com",
                first_name="Ex",
                last_name="Empleado",
                document_type="CC",
                document_number="987654322",
                phone="+57 300 123 4568",
                hashed_password=pwd.hash("Demo1234!"),
                is_active=False,
                accepted_terms=True,
                accepted_data_policy=True,
            )
            db.add(inactive_user)
            db.flush()
            db.commit()
            db.refresh(inactive_user)
            print("✓ Inactive user created: exempleado@bovitrack.com (para QA de reactivación)")
        else:
            print("→ Inactive user already exists")

        # 3. Demo farm
        farm = db.query(Farm).where(Farm.farm_identifier == "FIN-DEMO-001").first()
        if not farm:
            first_dept = db.query(Department).order_by(Department.name.asc()).first()
            if first_dept:
                dept_id = first_dept.id
            else:
                dept = Department(id=uuid.uuid4(), name="Antioquia", code="05")
                db.add(dept)
                db.flush()
                dept_id = dept.id
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

            uf = UserFarm(
                id=uuid.uuid4(),
                user_id=user.id,
                farm_id=farm.id,
                role_id=admin_role.id,
                assigned_by=user.id,
                is_active=True,
            )
            db.add(uf)
            db.flush()
            add_audit_log(db, user_id=str(user.id), farm_id=str(farm.id), action="create", entity="farm", entity_id=str(farm.id))
            db.commit()
            print("✓ Farm created: Hacienda El Porvenir")
        else:
            print("→ Farm already exists")

        farm_id = farm.id

        # ── Helper: create only if table is empty for this farm ─────────────
        def needs_seed(model, farm_fk="farm_id"):
            return db.query(model).filter(getattr(model, farm_fk) == farm_id).count() == 0

        # ── 4. Land plots ───────────────────────────────────────────────
        if needs_seed(LandPlot):
            plots_data = [
                ("Lote Norte", Decimal("35.00"), "pastoreo", 60),
                ("Lote Sur", Decimal("30.00"), "pastoreo", 50),
                ("Lote Este", Decimal("25.00"), "pastoreo", 45),
                ("Lote Oeste", Decimal("30.00"), "pastoreo", 50),
                ("Lote de Cultivo", Decimal("30.00"), "cultivo", 0),
            ]
            plots = []
            for name, area, usage, cap in plots_data:
                p = LandPlot(
                    id=uuid.uuid4(), farm_id=farm_id, name=name,
                    area=area, area_unit="hectareas", usage_type=usage,
                    max_capacity=cap, is_active=True,
                )
                db.add(p)
                plots.append(p)
            db.flush()
            add_audit_log(db, user_id=str(user.id), farm_id=str(farm_id), action="seed", entity="land_plot", entity_id=str(farm_id), details={"count": len(plots_data)})
            print(f"✓ {len(plots_data)} land plots created")
        else:
            plots = db.query(LandPlot).where(LandPlot.farm_id == farm_id).all()
            print("→ Land plots already exist")

        plot_ids = [p.id for p in plots if p.usage_type == "pastoreo"]

        # ── 5. Paddocks ─────────────────────────────────────────────────
        if needs_seed(Paddock):
            from datetime import date as dt_date
            paddocks_data = [
                ("Potrero La Pradera", Decimal("8.00"), 20, "bueno", "kikuyo", "libre", None, None),
                ("Potrero El Manantial", Decimal("6.00"), 15, "bueno", "brachiaria", "ocupado", None, None),
                ("Potrero La Colina", Decimal("5.00"), 12, "regular", "estrella", "ocupado", None, None),
                ("Potrero El Valle", Decimal("7.00"), 18, "bueno", "kikuyo", "ocupado", None, None),
                ("Potrero La Loma", Decimal("4.50"), 10, "bueno", "ryegrass", "libre", None, None),
                ("Potrero El Bosque", Decimal("6.50"), 16, "regular", "brachiaria", "en_descanso",
                 dt_date.today() - timedelta(days=20), dt_date.today() + timedelta(days=10)),
                ("Potrero La Vega", Decimal("5.00"), 14, "bueno", "kikuyo", "en_descanso",
                 dt_date.today() - timedelta(days=30), dt_date.today() + timedelta(days=5)),
                ("Potrero El Mirador", Decimal("4.00"), 10, "bueno", "estrella", "libre", None, None),
            ]
            paddocks = []
            src_plots = plot_ids or [p.id for p in plots]
            for i, (name, area, cap, cover, pasture, status, rest_start, rest_end) in enumerate(paddocks_data):
                p = Paddock(
                    id=uuid.uuid4(), farm_id=farm_id, name=name,
                    land_plot_id=src_plots[i % len(src_plots)] if src_plots else None,
                    area_hectares=area, max_capacity=cap, coverage_status=cover,
                    pasture_type=pasture, status=status,
                    rest_start_date=rest_start, rest_end_date=rest_end,
                )
                db.add(p)
                paddocks.append(p)
            db.flush()
            print(f"✓ {len(paddocks_data)} paddocks created")

        # ── 6. Bovines ──────────────────────────────────────────────────
        if needs_seed(Bovine):
            ref_date = dt_date.today()
            bovine_map = {}  # id_num -> Bovine object
            bovines_list = []

            # First pass: create all bovines
            for id_num, name, sex, breed, color, days_old, birth_w, purpose, entry_type in BOVINE_TEMPLATES:
                birth_date = ref_date - timedelta(days=days_old)
                age_days = days_old
                # Estimate current weight based on breed and age
                # Mature weight estimates: Holstein ~650, Brahmán ~700, Normando ~600, Cebú ~650, Gyr ~500
                mature_weight = {
                    "Holstein": 650, "Brahman": 700, "Normando": 600,
                    "Cebu": 650, "Gyr": 500,
                }.get(breed, 600)
                # Simple growth curve: weight = mature * (1 - exp(-0.003 * days)) + birth_weight * exp(-0.003 * days)
                import math
                growth_rate = 0.003
                growth_factor = 1 - math.exp(-growth_rate * age_days)
                current_w = round(float(birth_w) * (1 - growth_factor) + mature_weight * growth_factor, 1)

                entry_date = birth_date
                status = "activo"
                exit_date = None
                exit_reason = None
                is_active = True

                if id_num in SOLD_BOVINES:
                    status = "vendido"
                    exit_date = ref_date - timedelta(days=30)
                    exit_reason = "venta"
                    is_active = False
                elif id_num in DEAD_BOVINES:
                    status = "muerto"
                    exit_date = ref_date - timedelta(days=60)
                    exit_reason = "muerte"
                    is_active = False

                # Assign to a random plot
                import random
                plot_id = random.choice(plot_ids) if plot_ids and status == "activo" else None

                bovine = Bovine(
                    id=uuid.uuid4(), farm_id=farm_id,
                    identification_number=id_num, name=name,
                    sex=sex, breed=breed, color=color,
                    birth_date=birth_date, birth_weight=Decimal(str(birth_w)),
                    current_weight=Decimal(str(current_w)),
                    purpose=purpose, status=status,
                    entry_type=entry_type, entry_date=entry_date,
                    exit_date=exit_date, exit_reason=exit_reason,
                    is_active=is_active,
                    land_plot_id=plot_id,
                    registered_by=user.id,
                )
                db.add(bovine)
                db.flush()
                bovine_map[id_num] = bovine
                bovines_list.append(bovine)

            # Second pass: set parent relationships
            for child_id, (father_id, mother_id) in FAMILY_TREE.items():
                child = bovine_map.get(child_id)
                father = bovine_map.get(father_id)
                mother = bovine_map.get(mother_id)
                if child and father:
                    child.father_id = father.id
                if child and mother:
                    child.mother_id = mother.id

            db.flush()
            print(f"✓ {len(bovines_list)} bovines created (with family tree)")
        else:
            bovine_map = {}
            bovines_list = db.query(Bovine).where(Bovine.farm_id == farm_id).all()
            for b in bovines_list:
                bovine_map[b.identification_number] = b
            print("→ Bovines already exist")

        # ── 7. Weight records ───────────────────────────────────────────
        if needs_seed(Weight):
            import math, random
            weight_records = []
            for b in bovines_list:
                if not b.birth_weight or not b.current_weight:
                    continue
                age_days = (ref_date - b.birth_date).days
                birth_w = float(b.birth_weight)
                current_w = float(b.current_weight)
                # Create 4 records: at ~20%, 40%, 60%, 80% of current age
                for frac in [0.2, 0.4, 0.6, 0.8]:
                    measure_age = int(age_days * frac)
                    if measure_age < 14:
                        continue
                    measure_date = b.birth_date + timedelta(days=measure_age)
                    # Interpolate weight using same growth curve
                    growth_rate = 0.003
                    growth_factor = 1 - math.exp(-growth_rate * measure_age)
                    weight = round(birth_w * (1 - growth_factor) + current_w * growth_factor, 1)
                    # Add some noise
                    weight += round(random.uniform(-5, 5), 1)
                    w = Weight(
                        id=uuid.uuid4(), farm_id=farm_id,
                        bovine_id=b.id, weight_kg=Decimal(str(max(weight, 1))),
                        measured_at=measure_date,
                        body_condition=random.choice([3, 3, 3, 4, 4, 5]),
                        observations="Registro histórico de peso",
                        registered_by=user.id,
                    )
                    db.add(w)
                    weight_records.append(w)
            db.flush()
            print(f"✓ {len(weight_records)} weight records created")

        # ── 8. Reproductive events ──────────────────────────────────────
        if needs_seed(ReproductiveEvent):
            repro_events = []
            for b in bovines_list:
                if b.identification_number not in REPRODUCTIVE_FEMALES:
                    continue
                # Only for females that are active and older than 18 months
                age_days = (ref_date - b.birth_date).days
                if age_days < 540:
                    continue

                # First heat / insemination at ~18 months
                heat_date = b.birth_date + timedelta(days=550)
                if heat_date > ref_date:
                    continue

                # 1. Heat event
                e1 = ReproductiveEvent(
                    id=uuid.uuid4(), farm_id=farm_id, bovine_id=b.id,
                    event_type="calor", event_date=heat_date,
                    observations="Primer celo detectado",
                    registered_by=user.id,
                )
                db.add(e1)
                repro_events.append(e1)

                # 2. Insemination if enough time passed
                insem_date = heat_date + timedelta(days=1)
                if insem_date > ref_date:
                    continue

                # Find a bull
                bulls = [x for x in bovines_list if x.sex == "macho" and x.is_active and x.id != b.id]
                bull_id = bulls[0].id if bulls else None

                # Some get pregnant, some don't
                is_pregnant = b.identification_number in ["BOV-001", "BOV-002", "BOV-005", "BOV-009", "BOV-010", "BOV-013"]
                e2 = ReproductiveEvent(
                    id=uuid.uuid4(), farm_id=farm_id, bovine_id=b.id,
                    event_type="inseminacion", event_date=insem_date,
                    bull_id=bull_id,
                    result="positivo" if is_pregnant else "negativo",
                    observations="Inseminación artificial" if is_pregnant else "Inseminación sin éxito",
                    registered_by=user.id,
                )
                db.add(e2)
                repro_events.append(e2)

                if not is_pregnant:
                    continue

                # 3. Pregnancy check at 60 days
                preg_check = insem_date + timedelta(days=60)
                if preg_check > ref_date:
                    continue
                e3 = ReproductiveEvent(
                    id=uuid.uuid4(), farm_id=farm_id, bovine_id=b.id,
                    event_type="diagnostico_gestacion", event_date=preg_check,
                    result="positivo",
                    observations="Gestación confirmada por ecografía",
                    registered_by=user.id,
                )
                db.add(e3)
                repro_events.append(e3)

                # 4. Calving at ~285 days from insemination
                calving_date = insem_date + timedelta(days=285)
                if calving_date > ref_date:
                    continue
                # Find a calf that has this mother in its family tree
                calves = [x for x in bovines_list if
                          x.identification_number in FAMILY_TREE and
                          FAMILY_TREE[x.identification_number][1] == b.identification_number]
                calf_id = calves[0].id if calves else None
                due_date = calving_date - timedelta(days=5)
                e4 = ReproductiveEvent(
                    id=uuid.uuid4(), farm_id=farm_id, bovine_id=b.id,
                    event_type="parto", event_date=calving_date,
                    due_date=due_date,
                    calf_id=calf_id,
                    result="normal",
                    observations="Parto sin complicaciones. Cría saludable.",
                    registered_by=user.id,
                )
                db.add(e4)
                repro_events.append(e4)

            db.flush()
            print(f"✓ {len(repro_events)} reproductive events created")

        # ── 9. Treatments ──────────────────────────────────────────────
        if needs_seed(Treatment):
            treatments = []
            active_bovines = [b for b in bovines_list if b.is_active]
            treatment_templates = [
                ("vacuna", "Fiebre Aftosa", "2 mL", "intramuscular", "Vacunación semestral"),
                ("vacuna", "Brucelosis", "1 mL", "subcutánea", "Vacunación anual"),
                ("desparasitacion", "Ivermectina 1%", "3 mL", "subcutánea", "Desparasitación trimestral"),
                ("vitamina", "Vitaminas ADE", "5 mL", "intramuscular", "Suplementación vitamínica"),
                ("desparasitacion", "Fenbendazol", "10 mL", "oral", "Desparasitación interna"),
            ]

            import random
            for i, b in enumerate(active_bovines[:20]):  # 20 treated bovines
                t_type, product, dose, route, obs = random.choice(treatment_templates)
                app_date = ref_date - timedelta(days=random.randint(15, 180))
                t = Treatment(
                    id=uuid.uuid4(), farm_id=farm_id, bovine_id=b.id,
                    treatment_type=t_type, product_name=product,
                    dose=dose, administration_route=route,
                    application_date=datetime.combine(app_date, datetime.min.time()),
                    diagnosis=None, observations=obs,
                    applied_by=user.id,
                )
                db.add(t)
                treatments.append(t)

            db.flush()
            print(f"✓ {len(treatments)} treatments created")

        # ── 10. Milk production ────────────────────────────────────────
        if needs_seed(MilkProduction):
            import random
            milk_records = []
            dairy_bovines = [b for b in bovines_list if b.identification_number in DAIRY_FEMALES and b.is_active]

            for b in dairy_bovines:
                for day_offset in range(1, 31):  # Last 30 days
                    m_date = ref_date - timedelta(days=day_offset)
                    # Morning milking: 8-12 liters
                    am_liters = round(random.uniform(8.0, 12.0), 1)
                    m1 = MilkProduction(
                        id=uuid.uuid4(), farm_id=farm_id, bovine_id=b.id,
                        milking_date=datetime.combine(m_date, datetime.min.time()),
                        quantity_liters=Decimal(str(am_liters)),
                        milking_type="manual",
                        milking_session="mañana",
                        registered_by=user.id,
                    )
                    db.add(m1)
                    milk_records.append(m1)

                    # Afternoon milking: 6-9 liters
                    pm_liters = round(random.uniform(6.0, 9.0), 1)
                    m2 = MilkProduction(
                        id=uuid.uuid4(), farm_id=farm_id, bovine_id=b.id,
                        milking_date=datetime.combine(m_date, datetime.min.time()),
                        quantity_liters=Decimal(str(pm_liters)),
                        milking_type="manual",
                        milking_session="tarde",
                        registered_by=user.id,
                    )
                    db.add(m2)
                    milk_records.append(m2)

            db.flush()
            print(f"✓ {len(milk_records)} milk production records created")

        # ── 11. Food items ─────────────────────────────────────────────
        if needs_seed(Food):
            foods_data = [
                ("Concentrado Premium Lechero", "concentrado", "kg", Decimal("800.00"), Decimal("150.00"), Decimal("2500.00"),
                 ref_date + timedelta(days=180), "Distribuidora XYZ"),
                ("Concentrado Engorde Brahmán", "concentrado", "kg", Decimal("600.00"), Decimal("100.00"), Decimal("2200.00"),
                 ref_date + timedelta(days=150), "NutriAnimal SA"),
                ("Concentrado Iniciación Terneros", "concentrado", "kg", Decimal("200.00"), Decimal("50.00"), Decimal("3500.00"),
                 ref_date + timedelta(days=120), "AgroVet SAS"),
                ("Sal Mineralizada 6%", "suplementos", "kg", Decimal("100.00"), Decimal("20.00"), Decimal("1200.00"),
                 ref_date + timedelta(days=365), "Minerales SA"),
                ("Sal Mineralizada 12%", "suplementos", "kg", Decimal("60.00"), Decimal("20.00"), Decimal("1800.00"),
                 ref_date + timedelta(days=300), "Minerales SA"),
                ("Vitamina ADE Inyectable", "vitaminas", "litros", Decimal("8.00"), Decimal("3.00"), Decimal("35000.00"),
                 ref_date + timedelta(days=200), "VetFarma"),
                ("Complejo B", "vitaminas", "litros", Decimal("5.00"), Decimal("2.00"), Decimal("28000.00"),
                 ref_date + timedelta(days=250), "VetFarma"),
                ("Antibiótico Penicilina", "medicamentos", "litros", Decimal("3.00"), Decimal("1.00"), Decimal("45000.00"),
                 ref_date + timedelta(days=90), "Laboratorios Vetco"),
            ]
            foods = []
            for name, cat, unit, stock, min_s, cost, exp, supp in foods_data:
                f = Food(
                    id=uuid.uuid4(), farm_id=farm_id, name=name,
                    category=cat, unit_of_measure=unit,
                    current_stock=stock, min_stock_alert=min_s,
                    cost_per_unit=cost, expiration_date=exp,
                    supplier=supp,
                )
                db.add(f)
                foods.append(f)
            db.flush()
            print(f"✓ {len(foods_data)} food items created")
        else:
            foods = db.query(Food).where(Food.farm_id == farm_id).all()
            print("→ Food items already exist")

        # ── 12. Stock movements ────────────────────────────────────────
        if needs_seed(StockMovement):
            import random
            movements = []
            for f in foods:
                # Initial purchase
                qty = float(f.current_stock)
                m1 = StockMovement(
                    id=uuid.uuid4(), farm_id=farm_id, food_id=f.id,
                    movement_type="purchase",
                    quantity=Decimal(str(qty)),
                    unit_cost=f.cost_per_unit,
                    total_cost=Decimal(str(round(qty * float(f.cost_per_unit if f.cost_per_unit else 0), 2))),
                    stock_before=Decimal("0"),
                    stock_after=f.current_stock,
                    movement_date=ref_date - timedelta(days=random.randint(30, 90)),
                    registered_by=user.id,
                    notes=f"Compra inicial de {f.name}",
                )
                db.add(m1)
                movements.append(m1)

                # Some consumption/usage
                if float(f.current_stock) > 20:
                    used = round(float(f.current_stock) * random.uniform(0.1, 0.3), 2)
                    before = f.current_stock
                    after = Decimal(str(round(float(before) - used, 2)))
                    m2 = StockMovement(
                        id=uuid.uuid4(), farm_id=farm_id, food_id=f.id,
                        movement_type="adjustment",
                        quantity=Decimal(str(-used)),
                        stock_before=before,
                        stock_after=after,
                        movement_date=ref_date - timedelta(days=random.randint(1, 15)),
                        registered_by=user.id,
                        notes=f"Consumo de {f.name}",
                    )
                    db.add(m2)
                    movements.append(m2)

            db.flush()
            print(f"✓ {len(movements)} stock movements created")

        # ── 13. Economic records ───────────────────────────────────────
        if needs_seed(EconomicRecord):
            import random
            economic_records = []

            # Income from milk sales
            for month in range(6):
                inc_date = ref_date - timedelta(days=month * 30)
                inc = EconomicRecord(
                    id=uuid.uuid4(), farm_id=farm_id,
                    record_type="ingreso",
                    category="venta_leche",
                    amount=Decimal(str(round(random.uniform(800000, 1200000), 0))),
                    record_date=inc_date,
                    description="Venta de leche semanal — 120 litros/día",
                    registered_by=user.id,
                )
                db.add(inc)
                economic_records.append(inc)

            # Income from cattle sales
            for month in [2, 5]:
                inc_date = ref_date - timedelta(days=month * 30)
                inc = EconomicRecord(
                    id=uuid.uuid4(), farm_id=farm_id,
                    record_type="ingreso",
                    category="venta_animal",
                    amount=Decimal(str(round(random.uniform(2500000, 4000000), 0))),
                    record_date=inc_date,
                    description="Venta de bovino para engorde",
                    registered_by=user.id,
                )
                db.add(inc)
                economic_records.append(inc)

            # Expenses
            expense_categories = [
                ("compra_insumo", "Compra de concentrado y sales minerales", random.uniform(500000, 1500000)),
                ("servicio_veterinario", "Servicio veterinario — vacunación y revisión", random.uniform(200000, 600000)),
                ("transporte", "Transporte de insumos", random.uniform(100000, 300000)),
                ("personal", "Pago de nómina empleados", random.uniform(1800000, 2500000)),
                ("mantenimiento", "Mantenimiento de cercas y bebederos", random.uniform(300000, 800000)),
                ("compra_insumo", "Compra de vitaminas y medicamentos", random.uniform(200000, 500000)),
                ("personal", "Pago de nómina empleados", random.uniform(1800000, 2500000)),
            ]
            for cat, desc, amount in expense_categories:
                exp_date = ref_date - timedelta(days=random.randint(5, 60))
                exp = EconomicRecord(
                    id=uuid.uuid4(), farm_id=farm_id,
                    record_type="gasto",
                    category=cat,
                    amount=Decimal(str(round(amount, 0))),
                    record_date=exp_date,
                    description=desc,
                    registered_by=user.id,
                )
                db.add(exp)
                economic_records.append(exp)

            db.flush()
            print(f"✓ {len(economic_records)} economic records created")

        # ── 14. Animal movements ───────────────────────────────────────
        if needs_seed(AnimalMovement):
            import random
            movements = []
            movement_templates = [
                ("compra", "BOV-004", Decimal("3500000"), "Ganadería El Bosque", "CC", "123456789", "+57 310 111 2233"),
                ("compra", "BOV-007", Decimal("2800000"), "Finca San José", "CC", "987654321", "+57 320 222 3344"),
                ("venta", "BOV-026", Decimal("4200000"), "Ceba La Ponderosa", "NIT", "900123456-7", "+57 300 333 4455"),
                ("traslado", None, None, "Finca La Esperanza (socío)", None, None, None),
                ("nacimiento", "BOV-030", None, None, None, None, None),
            ]
            for m_type, bovine_id_num, price, counterparty, cp_doc_type, cp_doc, cp_phone in movement_templates:
                b_id = bovine_map[bovine_id_num].id if bovine_id_num and bovine_id_num in bovine_map else None
                m = AnimalMovement(
                    id=uuid.uuid4(), farm_id=farm_id, bovine_id=b_id,
                    movement_type=m_type,
                    movement_date=ref_date - timedelta(days=random.randint(30, 180)),
                    price=price,
                    counterparty_name=counterparty,
                    counterparty_document=cp_doc,
                    counterparty_phone=cp_phone,
                    observations=f"Movimiento tipo {m_type} registrado",
                    registered_by=user.id,
                )
                db.add(m)
                movements.append(m)

            db.flush()
            print(f"✓ {len(movements)} animal movements created")

        # ── 15. Sanitary plans ─────────────────────────────────────────
        if needs_seed(SanitaryPlan):
            plans = []
            # Individual plans for specific bovines
            target_bovines = [b for b in bovines_list if b.is_active][:3]
            for b in target_bovines:
                p = SanitaryPlan(
                    id=uuid.uuid4(), farm_id=farm_id, bovine_id=b.id,
                    vaccine_or_treatment_name="Fiebre Aftosa",
                    treatment_type="vacuna",
                    administration_route="intramuscular",
                    dose="2 mL",
                    frequency_days=180,
                    last_applied_date=ref_date - timedelta(days=random.randint(30, 100)),
                    next_scheduled_date=ref_date + timedelta(days=random.randint(80, 150)),
                    observations="Plan sanitario individual",
                    created_by=user.id,
                )
                db.add(p)
                plans.append(p)

            # Lot-based plans
            for i, plot_id in enumerate(plot_ids[:3]):
                p = SanitaryPlan(
                    id=uuid.uuid4(), farm_id=farm_id, land_plot_id=plot_id,
                    vaccine_or_treatment_name=["Desparasitación", "Vitaminas ADE", "Brucelosis"][i],
                    treatment_type=["desparasitacion", "vitamina", "vacuna"][i],
                    administration_route=["subcutánea", "intramuscular", "subcutánea"][i],
                    dose=["3 mL", "5 mL", "1 mL"][i],
                    frequency_days=[90, 30, 365][i],
                    last_applied_date=ref_date - timedelta(days=[20, 15, 60][i]),
                    next_scheduled_date=ref_date + timedelta(days=[70, 15, 305][i]),
                    observations=f"Plan sanitario para lote {plots[i].name}",
                    created_by=user.id,
                )
                db.add(p)
                plans.append(p)

            db.flush()
            print(f"✓ {len(plans)} sanitary plans created")

        # ── Commit everything ──────────────────────────────────────────
        add_audit_log(db, user_id=str(user.id), farm_id=str(farm_id), action="seed", entity="farm", entity_id=str(farm_id), details={"message": "Datos de prueba generados (30 bovinos, registros de peso, leche, economía, etc.)"})
        db.commit()
        print("\n" + "=" * 60)
        print("✅ TEST DATA SEEDING COMPLETE!")
        print("=" * 60)
        print("   Login: admin@bovitrack.com / Demo1234!")
        print(f"   Farm:  Hacienda El Porvenir (30 bovines)")
        print("\n   To verify email invitations:")
        print("   1. Login at http://localhost:5173")
        print("   2. Go to Farm > Empleados > + Asignar empleado")
        print("   3. Enter an email and select a role")
        print("   4. Check http://localhost:8025 (Mailpit) for the email")


if __name__ == "__main__":
    main()
