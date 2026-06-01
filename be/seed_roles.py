"""
Seed: Roles, permisos y reparación de UserFarm para fincas existentes.
Uso: docker compose exec be python seed_roles.py
"""
import uuid
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

DATABASE_URL = os.environ["DATABASE_URL"]
engine = create_engine(DATABASE_URL)

# Módulos del sistema (extraídos de todos los routers)
ALL_MODULES = [
    "fincas",
    "bovinos",
    "usuarios",
    "potreros",
    "produccion_leche",
    "alimentacion",
    "tratamientos",
    "reproduccion",
    "reportes",
]

# Roles: (nombre, descripción, permisos por módulo)
# permisos: (can_create, can_read, can_update, can_delete)
ROLES = [
    (
        "Administrador",
        "Acceso total a todos los módulos de la finca",
        {m: (True, True, True, True) for m in ALL_MODULES},
    ),
    (
        "Operario",
        "Registro y consulta de operaciones diarias",
        {
            "fincas":           (False, True,  False, False),
            "bovinos":          (True,  True,  True,  False),
            "potreros":         (False, True,  False, False),
            "produccion_leche": (True,  True,  False, False),
            "alimentacion":     (True,  True,  False, False),
            "tratamientos":     (True,  True,  False, False),
            "reproduccion":     (True,  True,  False, False),
            "usuarios":         (False, False, False, False),
            "reportes":         (False, True,  False, False),
        },
    ),
    (
        "Veterinario",
        "Gestión sanitaria y reproductiva",
        {
            "fincas":           (False, True,  False, False),
            "bovinos":          (False, True,  True,  False),
            "potreros":         (False, True,  False, False),
            "produccion_leche": (False, True,  False, False),
            "alimentacion":     (False, True,  False, False),
            "tratamientos":     (True,  True,  True,  True),
            "reproduccion":     (True,  True,  True,  True),
            "usuarios":         (False, False, False, False),
            "reportes":         (False, True,  False, False),
        },
    ),
    (
        "Auditor",
        "Solo lectura de todos los módulos",
        {m: (False, True, False, False) for m in ALL_MODULES},
    ),
]


def seed():
    with Session(engine) as session:
        # ── 1. Insertar roles y permisos ──────────────────────────────────
        existing_roles = session.execute(text("SELECT COUNT(*) FROM role")).scalar()
        role_ids = {}

        if existing_roles and existing_roles > 0:
            print(f"Ya existen {existing_roles} roles — omitiendo inserción de roles.")
            # Cargar los IDs existentes
            rows = session.execute(text("SELECT id, name FROM role")).fetchall()
            for row in rows:
                role_ids[row[1]] = row[0]
        else:
            for role_name, role_desc, perms in ROLES:
                role_id = str(uuid.uuid4())
                session.execute(
                    text("INSERT INTO role (id, name, description, is_active) VALUES (:id, :name, :desc, true)"),
                    {"id": role_id, "name": role_name, "desc": role_desc},
                )
                role_ids[role_name] = role_id

                for module, (cc, cr, cu, cd) in perms.items():
                    session.execute(
                        text("""INSERT INTO permission
                            (id, role_id, module, can_create, can_read, can_update, can_delete)
                            VALUES (:id, :role_id, :module, :cc, :cr, :cu, :cd)"""),
                        {
                            "id": str(uuid.uuid4()),
                            "role_id": role_id,
                            "module": module,
                            "cc": cc, "cr": cr, "cu": cu, "cd": cd,
                        },
                    )

            session.commit()
            print(f"✓ {len(ROLES)} roles insertados con sus permisos.")

        # ── 2. Reparar UserFarm de fincas existentes sin vínculo ─────────
        admin_role_id = role_ids.get("Administrador")
        if not admin_role_id:
            print("No se encontró el rol Administrador. Abortando reparación.")
            return

        # Buscar fincas cuyo owner_id no tiene un UserFarm activo
        orphan_farms = session.execute(text("""
            SELECT f.id, f.owner_id
            FROM farm f
            WHERE NOT EXISTS (
                SELECT 1 FROM user_farm uf
                WHERE uf.farm_id = f.id AND uf.user_id = f.owner_id AND uf.is_active = true
            )
        """)).fetchall()

        if not orphan_farms:
            print("✓ Todas las fincas ya tienen su vínculo de acceso correcto.")
            return

        repaired = 0
        for farm_id, owner_id in orphan_farms:
            session.execute(
                text("""INSERT INTO user_farm
                    (id, user_id, farm_id, role_id, assigned_by, is_active)
                    VALUES (:id, :user_id, :farm_id, :role_id, :assigned_by, true)"""),
                {
                    "id": str(uuid.uuid4()),
                    "user_id": str(owner_id),
                    "farm_id": str(farm_id),
                    "role_id": str(admin_role_id),
                    "assigned_by": str(owner_id),
                },
            )
            repaired += 1

        session.commit()
        print(f"✓ {repaired} finca(s) reparada(s): vínculo Administrador creado para el propietario.")


if __name__ == "__main__":
    seed()
