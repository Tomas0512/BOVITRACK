"""
Migración: seed_roles_and_permissions
¿Qué? Migración de datos (no de esquema) que inserta los roles y permisos
      iniciales del sistema BoviTrack.
¿Para qué? Sin roles ni permisos, el sistema no puede aplicar control de
           acceso basado en roles (RBAC). Los 4 roles definidos cubren los
           perfiles operativos típicos de una finca ganadera.
¿Impacto? Una vez ejecutada, las tablas role y permission contendrán:
          - Administrador: acceso total (CRUD en todos los módulos)
          - Capataz: gestión operativa (sin eliminar ni gestionar usuarios)
          - Veterinario: foco sanitario (solo lectura en producción/fincas)
          - Empleado: operaciones básicas del día a día (solo lectura, sin usuarios)

Revision ID: e1f2a3b4c5d6
Revises: c1d2e3f4a5b6
Create Date: 2026-03-26 11:20:00.000000
"""

from __future__ import annotations

import uuid
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "e1f2a3b4c5d6"
down_revision: Union[str, None] = "c1d2e3f4a5b6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# ¿Qué? Lista de módulos del sistema que aparecen en la tabla permission.
# ¿Para qué? Cada rol tiene un permiso por módulo con flags can_create/read/update/delete.
# ¿Impacto? Si se agrega un nuevo módulo al sistema, debe añadirse aquí y regenerar la migración.
MODULES = [
    "bovinos",
    "potreros",
    "tratamientos",
    "produccion_leche",
    "alimentos",
    "tareas",
    "fincas",
    "usuarios",
]

# ¿Qué? Definición de los 4 roles con sus permisos por módulo.
# ¿Para qué? Centralizar la configuración para que sea fácil de auditar y modificar.
# ¿Impacto? c=create, r=read, u=update, d=delete. True/False por operación.
ROLES = [
    {
        "name": "Administrador",
        "description": "Acceso total al sistema",
        "permissions": {m: {"c": True, "r": True, "u": True, "d": True} for m in MODULES},
    },
    {
        "name": "Capataz",
        "description": "Gestión operativa de la finca",
        "permissions": {
            "bovinos": {"c": True, "r": True, "u": True, "d": False},
            "potreros": {"c": True, "r": True, "u": True, "d": False},
            "tratamientos": {"c": True, "r": True, "u": True, "d": False},
            "produccion_leche": {"c": True, "r": True, "u": True, "d": False},
            "alimentos": {"c": True, "r": True, "u": True, "d": False},
            "tareas": {"c": True, "r": True, "u": True, "d": False},
            "fincas": {"c": False, "r": True, "u": False, "d": False},
            "usuarios": {"c": False, "r": True, "u": False, "d": False},
        },
    },
    {
        "name": "Veterinario",
        "description": "Gestión sanitaria y tratamientos",
        "permissions": {
            "bovinos": {"c": False, "r": True, "u": True, "d": False},
            "potreros": {"c": False, "r": True, "u": False, "d": False},
            "tratamientos": {"c": True, "r": True, "u": True, "d": False},
            "produccion_leche": {"c": False, "r": True, "u": False, "d": False},
            "alimentos": {"c": False, "r": True, "u": False, "d": False},
            "tareas": {"c": False, "r": True, "u": True, "d": False},
            "fincas": {"c": False, "r": True, "u": False, "d": False},
            "usuarios": {"c": False, "r": True, "u": False, "d": False},
        },
    },
    {
        "name": "Empleado",
        "description": "Operaciones básicas del día a día",
        "permissions": {
            "bovinos": {"c": False, "r": True, "u": False, "d": False},
            "potreros": {"c": False, "r": True, "u": False, "d": False},
            "tratamientos": {"c": False, "r": True, "u": False, "d": False},
            "produccion_leche": {"c": True, "r": True, "u": False, "d": False},
            "alimentos": {"c": True, "r": True, "u": False, "d": False},
            "tareas": {"c": False, "r": True, "u": True, "d": False},
            "fincas": {"c": False, "r": True, "u": False, "d": False},
            "usuarios": {"c": False, "r": False, "u": False, "d": False},
        },
    },
]


def upgrade() -> None:
    """¿Qué? Inserta los roles y permisos en la base de datos.
    ¿Para qué? Poblar las tablas role y permission con los datos iniciales.
    ¿Impacto? Usa ON CONFLICT para ser idempotente — se puede ejecutar
              varias veces sin duplicar datos.
    """
    bind = op.get_bind()
    for role_data in ROLES:
        role_id = str(uuid.uuid4())
        # ¿Qué? INSERT con ON CONFLICT para idempotencia.
        # ¿Para qué? Si ya existe un rol con ese nombre, actualiza la descripción.
        bind.execute(
            sa.text(
                """
                INSERT INTO role (id, name, description, is_active)
                VALUES (:id, :name, :description, true)
                ON CONFLICT (name) DO UPDATE
                SET description = EXCLUDED.description
                RETURNING id
                """
            ),
            {"id": role_id, "name": role_data["name"], "description": role_data["description"]},
        )
        # ¿Qué? Obtener el ID real del rol (puede ser diferente si ya existía).
        result = bind.execute(
            sa.text("SELECT id FROM role WHERE name = :name"),
            {"name": role_data["name"]},
        )
        actual_role_id = str(result.scalar_one())

        # ¿Qué? Insertar un permiso por cada módulo para este rol.
        # ¿Impacto? ON CONFLICT actualiza los flags si el permiso ya existe.
        for module, perms in role_data["permissions"].items():
            bind.execute(
                sa.text(
                    """
                    INSERT INTO permission (id, role_id, module, can_create, can_read, can_update, can_delete)
                    VALUES (:id, :role_id, :module, :can_create, :can_read, :can_update, :can_delete)
                    ON CONFLICT (role_id, module) DO UPDATE
                    SET can_create = EXCLUDED.can_create,
                        can_read = EXCLUDED.can_read,
                        can_update = EXCLUDED.can_update,
                        can_delete = EXCLUDED.can_delete
                    """
                ),
                {
                    "id": str(uuid.uuid4()),
                    "role_id": actual_role_id,
                    "module": module,
                    "can_create": perms["c"],
                    "can_read": perms["r"],
                    "can_update": perms["u"],
                    "can_delete": perms["d"],
                },
            )


def downgrade() -> None:
    """¿Qué? Elimina los roles y permisos insertados por esta migración.
    ¿Para qué? Permitir rollback limpio de la migración.
    ¿Impacto? Elimina primero permisos (por FK) y luego roles.
    """
    bind = op.get_bind()
    for role_data in ROLES:
        bind.execute(
            sa.text("DELETE FROM permission WHERE role_id = (SELECT id FROM role WHERE name = :name)"),
            {"name": role_data["name"]},
        )
        bind.execute(
            sa.text("DELETE FROM role WHERE name = :name"),
            {"name": role_data["name"]},
        )
