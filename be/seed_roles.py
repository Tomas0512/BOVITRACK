"""
Seed: Roles, permisos y reparación de UserFarm para fincas existentes.
Uso: docker compose exec be python seed_roles.py

Idempotente y AUTO-CORRECTIVO: puede ejecutarse las veces que haga falta.
Si un permiso ya existe, se actualiza con la matriz de este archivo
(la fuente de verdad es el código); si sobra un módulo obsoleto, se elimina.
"""
import uuid
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

DATABASE_URL = os.environ["DATABASE_URL"]
engine = create_engine(DATABASE_URL)

# Módulos del sistema. DEBEN coincidir EXACTAMENTE con las claves que usan
# require_permission(module, action) en be/app/routers/*.py.
# Historial de corrección (2026-08): 'alimentacion'→'alimentos',
# 'planes_sanitarios'→'sanitario', se agregaron 'economica' y 'tareas';
# se eliminaron 'reproduccion' y 'reportes' (ningún router los exige).
ALL_MODULES = [
    "fincas",
    "bovinos",
    "usuarios",
    "potreros",
    "produccion_leche",
    "alimentos",
    "tratamientos",
    "reproductivo",
    "sanitario",
    "tareas",
    "economica",
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
            "alimentos":        (True,  True,  False, False),
            "tratamientos":     (True,  True,  False, False),
            "reproductivo":     (True,  True,  False, False),
            "sanitario":        (True,  True,  False, False),
            "tareas":           (True,  True,  False, False),
            "economica":        (False, True,  False, False),
            "usuarios":         (False, False, False, False),
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
            "alimentos":        (False, True,  False, False),
            "tratamientos":     (True,  True,  True,  True),
            "reproductivo":     (True,  True,  True,  True),
            "sanitario":        (True,  True,  True,  True),
            "tareas":           (True,  True,  True,  True),
            "economica":        (False, True,  False, False),
            "usuarios":         (False, False, False, False),
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
        # ── 1. Asegurar roles (inserta solo los que falten) ──────────────
        role_ids = {}
        rows = session.execute(text("SELECT id, name FROM role")).fetchall()
        for row in rows:
            role_ids[row[1]] = row[0]

        for role_name, role_desc, _perms in ROLES:
            if role_name not in role_ids:
                role_id = str(uuid.uuid4())
                session.execute(
                    text("INSERT INTO role (id, name, description, is_active) VALUES (:id, :name, :desc, true)"),
                    {"id": role_id, "name": role_name, "desc": role_desc},
                )
                role_ids[role_name] = role_id
                print(f"✓ Rol creado: {role_name}")

        # ── 2. Sincronizar permisos de cada rol con la matriz ────────────
        inserted = updated = deleted = 0
        for role_name, _role_desc, perms in ROLES:
            role_id = role_ids[role_name]

            existing = {
                row[0]: row[1]
                for row in session.execute(
                    text("SELECT module, id FROM permission WHERE role_id = :rid"),
                    {"rid": str(role_id)},
                ).fetchall()
            }

            # Eliminar módulos obsoletos que ya ningún router exige
            for module, perm_id in existing.items():
                if module not in ALL_MODULES:
                    session.execute(text("DELETE FROM permission WHERE id = :pid"), {"pid": perm_id})
                    deleted += 1

            for module, (cc, cr, cu, cd) in perms.items():
                if module in existing:
                    session.execute(
                        text("""UPDATE permission
                            SET can_create = :cc, can_read = :cr, can_update = :cu, can_delete = :cd
                            WHERE id = :pid"""),
                        {"cc": cc, "cr": cr, "cu": cu, "cd": cd, "pid": existing[module]},
                    )
                    updated += 1
                else:
                    session.execute(
                        text("""INSERT INTO permission
                            (id, role_id, module, can_create, can_read, can_update, can_delete)
                            VALUES (:id, :role_id, :module, :cc, :cr, :cu, :cd)"""),
                        {
                            "id": str(uuid.uuid4()),
                            "role_id": str(role_id),
                            "module": module,
                            "cc": cc, "cr": cr, "cu": cu, "cd": cd,
                        },
                    )
                    inserted += 1

        session.commit()
        print(f"✓ Permisos sincronizados: {inserted} insertados, {updated} actualizados, {deleted} obsoletos eliminados.")

        # ── 3. Reparar UserFarm de fincas existentes sin vínculo ─────────
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
