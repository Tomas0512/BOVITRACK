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
# require_permission(module, action) en be/app/modules/*/router.
# Historial de corrección (2026-08): 'alimentacion'→'alimentos',
# 'planes_sanitarios'→'sanitario', se agregaron 'economica' y 'tareas';
# se eliminaron 'reproduccion' y 'reportes' (ningún router los exige).
ALL_MODULES = [
    "fincas",
    "bovinos",
    "documentos",
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
#
# Fuente de verdad: las MIGRACIONES de Alembic (que es lo que existe en la BD).
# Antes este archivo sembraba "Operario" y "Auditor", roles que las migraciones
# no crean: ejecutarlo dejaba roles fantasma y no corregía Capataz ni Empleado.
# Corregido en la Parte 3e-4 del refactor para que coincida con la BD.
_NONE = (False, False, False, False)
_READ = (False, True, False, False)
_NO_DELETE = (True, True, True, False)

ROLES = [
    (
        "Administrador",
        "Acceso total al sistema",
        {m: (True, True, True, True) for m in ALL_MODULES},
    ),
    (
        "Capataz",
        "Gestión operativa de la finca",
        {m: _NO_DELETE for m in ALL_MODULES} | {"fincas": _READ, "usuarios": _READ},
    ),
    (
        "Veterinario",
        "Gestión sanitaria y tratamientos",
        {m: _READ for m in ALL_MODULES} | {
            "bovinos":      (False, True, True, False),
            "documentos":   (False, True, True, False),
            "tareas":       (False, True, True, False),
            "tratamientos": _NO_DELETE,
            "reproductivo": _NO_DELETE,
            "sanitario":    _NO_DELETE,
        },
    ),
    (
        "Empleado",
        "Operaciones básicas del día a día",
        {m: _READ for m in ALL_MODULES} | {
            "alimentos":        (True, True, False, False),
            "produccion_leche": (True, True, False, False),
            "tareas":           (False, True, True, False),
            "usuarios":         _NONE,
        },
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

        # El dueño puede no tener vínculo, o tenerlo INACTIVO (o con otro rol). Antes se
        # hacía un INSERT a secas y, en el segundo caso, chocaba con uq_user_farm
        # (user_id, farm_id) y abortaba todo el seed. Ahora es un UPSERT: crea el
        # vínculo o reactiva el existente como Administrador.
        created = reactivated = 0
        for farm_id, owner_id in orphan_farms:
            inserted = session.execute(
                text("""INSERT INTO user_farm
                    (id, user_id, farm_id, role_id, assigned_by, is_active)
                    VALUES (:id, :user_id, :farm_id, :role_id, :assigned_by, true)
                    ON CONFLICT ON CONSTRAINT uq_user_farm
                    DO UPDATE SET is_active = true, role_id = EXCLUDED.role_id
                    RETURNING (xmax = 0) AS inserted"""),
                {
                    "id": str(uuid.uuid4()),
                    "user_id": str(owner_id),
                    "farm_id": str(farm_id),
                    "role_id": str(admin_role_id),
                    "assigned_by": str(owner_id),
                },
            ).scalar_one()
            if inserted:
                created += 1
            else:
                reactivated += 1

        session.commit()
        print(f"✓ {created + reactivated} finca(s) reparada(s): vínculo Administrador del propietario "
              f"creado en {created} y reactivado en {reactivated}.")


if __name__ == "__main__":
    seed()
