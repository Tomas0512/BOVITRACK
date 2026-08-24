"""create_stock_movement_table

Revision ID: n1o2p3q4r5s6
Revises: m1n2o3p4q5r6
Create Date: 2026-06-27 12:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "n1o2p3q4r5s6"
down_revision: Union[str, None] = "m1n2o3p4q5r6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Guarda idempotente: c9ff44fd3509 (create_all) ya crea `stock_movement`
    # porque el modelo StockMovement está registrado en app.models.
    conn = op.get_bind()
    if sa.inspect(conn).has_table("stock_movement"):
        return

    op.create_table(
        "stock_movement",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("farm_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("farm.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("food_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("food.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("movement_type", sa.String(20), nullable=False),
        sa.Column("quantity", sa.Numeric(12, 2), nullable=False),
        sa.Column("unit_cost", sa.Numeric(12, 2), nullable=True),
        sa.Column("total_cost", sa.Numeric(12, 2), nullable=True),
        sa.Column("stock_before", sa.Numeric(12, 2), nullable=False),
        sa.Column("stock_after", sa.Numeric(12, 2), nullable=False),
        sa.Column("reference_type", sa.String(30), nullable=True),
        sa.Column("reference_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("registered_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("movement_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_stock_movement_farm_id"), "stock_movement", ["farm_id"])
    op.create_index(op.f("ix_stock_movement_food_id"), "stock_movement", ["food_id"])
    op.create_index(op.f("ix_stock_movement_type"), "stock_movement", ["movement_type"])
    op.create_index(op.f("ix_stock_movement_date"), "stock_movement", ["movement_date"])


def downgrade() -> None:
    conn = op.get_bind()
    if not sa.inspect(conn).has_table("stock_movement"):
        return

    op.drop_index(op.f("ix_stock_movement_date"), table_name="stock_movement")
    op.drop_index(op.f("ix_stock_movement_type"), table_name="stock_movement")
    op.drop_index(op.f("ix_stock_movement_food_id"), table_name="stock_movement")
    op.drop_index(op.f("ix_stock_movement_farm_id"), table_name="stock_movement")
    op.drop_table("stock_movement")
