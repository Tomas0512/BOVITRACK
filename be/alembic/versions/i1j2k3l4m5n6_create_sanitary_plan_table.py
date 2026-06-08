"""create_sanitary_plan_table

Revision ID: i1j2k3l4m5n6
Revises: h1i2j3k4l5m6
Create Date: 2026-06-01 00:00:00.000000

¿Qué? Crea la tabla sanitary_plan para gestionar planes sanitarios.
¿Para qué? Guardar vacunas y tratamientos programados por bovino o lote.
¿Impacto? Nueva tabla con relaciones a bovine, land_plot y farm.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "i1j2k3l4m5n6"
down_revision: Union[str, None] = "h1i2j3k4l5m6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "sanitary_plan",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("farm_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("bovine_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("land_plot_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("vaccine_or_treatment_name", sa.String(255), nullable=False),
        sa.Column("treatment_type", sa.String(50), nullable=False),
        sa.Column("administration_route", sa.String(50), nullable=False),
        sa.Column("dose", sa.String(50), nullable=True),
        sa.Column("frequency_days", sa.Integer(), nullable=False),
        sa.Column("last_applied_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("next_scheduled_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("observations", sa.Text(), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["bovine_id"], ["bovine.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["farm_id"], ["farm.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["land_plot_id"], ["land_plot.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_sanitary_plan_farm_id", "sanitary_plan", ["farm_id"])
    op.create_index("ix_sanitary_plan_bovine_id", "sanitary_plan", ["bovine_id"])
    op.create_index("ix_sanitary_plan_land_plot_id", "sanitary_plan", ["land_plot_id"])
    op.create_index("ix_sanitary_plan_next_scheduled_date", "sanitary_plan", ["next_scheduled_date"])


def downgrade() -> None:
    op.drop_index("ix_sanitary_plan_next_scheduled_date", table_name="sanitary_plan")
    op.drop_index("ix_sanitary_plan_land_plot_id", table_name="sanitary_plan")
    op.drop_index("ix_sanitary_plan_bovine_id", table_name="sanitary_plan")
    op.drop_index("ix_sanitary_plan_farm_id", table_name="sanitary_plan")
    op.drop_table("sanitary_plan")
