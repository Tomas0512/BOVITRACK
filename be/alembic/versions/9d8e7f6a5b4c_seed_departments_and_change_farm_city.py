"""seed departments and switch farm city to free text

Revision ID: 9d8e7f6a5b4c
Revises: a1b2c3d4e5f6
Create Date: 2026-03-25 22:10:00.000000
"""

from __future__ import annotations

import uuid
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "9d8e7f6a5b4c"
down_revision: Union[str, None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _seed_departments() -> None:
    bind = op.get_bind()
    departments = [
        ("Amazonas", "91"),
        ("Antioquia", "05"),
        ("Arauca", "81"),
        ("Atlántico", "08"),
        ("Bogotá D.C.", "11"),
        ("Bolívar", "13"),
        ("Boyacá", "15"),
        ("Caldas", "17"),
        ("Caquetá", "18"),
        ("Casanare", "85"),
        ("Cauca", "19"),
        ("Cesar", "20"),
        ("Chocó", "27"),
        ("Córdoba", "23"),
        ("Cundinamarca", "25"),
        ("Guainía", "94"),
        ("Guaviare", "95"),
        ("Huila", "41"),
        ("La Guajira", "44"),
        ("Magdalena", "47"),
        ("Meta", "50"),
        ("Nariño", "52"),
        ("Norte de Santander", "54"),
        ("Putumayo", "86"),
        ("Quindío", "63"),
        ("Risaralda", "66"),
        ("San Andrés y Providencia", "88"),
        ("Santander", "68"),
        ("Sucre", "70"),
        ("Tolima", "73"),
        ("Valle del Cauca", "76"),
        ("Vaupés", "97"),
        ("Vichada", "99"),
    ]

    for name, code in departments:
        bind.execute(
            sa.text(
                """
                INSERT INTO department (id, name, code)
                VALUES (:id, :name, :code)
                ON CONFLICT (name) DO UPDATE
                SET code = EXCLUDED.code
                """
            ),
            {"id": str(uuid.uuid4()), "name": name, "code": code},
        )


def _seed_purposes() -> None:
    bind = op.get_bind()
    purposes = [
        ("Leche", "Producción de leche"),
        ("Carne", "Producción de carne"),
        ("Doble propósito", "Producción de leche y carne"),
        ("Cría", "Cría de bovinos"),
        ("Levante", "Levante y ceba"),
    ]

    for name, description in purposes:
        bind.execute(
            sa.text(
                """
                INSERT INTO purpose (id, name, description)
                VALUES (:id, :name, :description)
                ON CONFLICT (name) DO UPDATE
                SET description = EXCLUDED.description
                """
            ),
            {
                "id": str(uuid.uuid4()),
                "name": name,
                "description": description,
            },
        )


def upgrade() -> None:
    _seed_departments()
    _seed_purposes()

    op.drop_constraint("uq_farm_name_location", "farm", type_="unique")
    op.drop_constraint("farm_city_id_fkey", "farm", type_="foreignkey")
    op.drop_column("farm", "city_id")

    op.add_column(
        "farm",
        sa.Column("city_municipality", sa.String(length=120), nullable=False, server_default=""),
    )
    op.alter_column("farm", "city_municipality", server_default=None)
    op.create_unique_constraint(
        "uq_farm_name_location",
        "farm",
        ["name", "department_id", "city_municipality"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_farm_name_location", "farm", type_="unique")
    op.drop_column("farm", "city_municipality")

    op.add_column("farm", sa.Column("city_id", sa.UUID(), nullable=True))
    op.create_foreign_key(
        "farm_city_id_fkey",
        "farm",
        "city",
        ["city_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_unique_constraint(
        "uq_farm_name_location",
        "farm",
        ["name", "department_id", "city_id"],
    )
