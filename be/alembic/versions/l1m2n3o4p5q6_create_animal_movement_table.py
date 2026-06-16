"""create_animal_movement_table

Revision ID: l1m2n3o4p5q6
Revises: k1l2m3n4o5p6
Create Date: 2026-06-15 19:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "l1m2n3o4p5q6"
down_revision: Union[str, None] = "k1l2m3n4o5p6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "animal_movement",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("farm_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("bovine_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("movement_type", sa.String(20), nullable=False),
        sa.Column("movement_date", sa.Date(), nullable=False),
        sa.Column("price", sa.Numeric(12, 2), nullable=True),
        sa.Column("counterparty_name", sa.String(200), nullable=True),
        sa.Column("counterparty_document", sa.String(50), nullable=True),
        sa.Column("counterparty_phone", sa.String(20), nullable=True),
        sa.Column("origin_farm_name", sa.String(200), nullable=True),
        sa.Column("destination_farm_name", sa.String(200), nullable=True),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("observations", sa.Text(), nullable=True),
        sa.Column("registered_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["farm_id"], ["farm.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["bovine_id"], ["bovine.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["registered_by"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_animal_movement_farm_id", "animal_movement", ["farm_id"])
    op.create_index("ix_animal_movement_bovine_id", "animal_movement", ["bovine_id"])
    op.create_index("ix_animal_movement_movement_type", "animal_movement", ["movement_type"])
    op.create_index("ix_animal_movement_movement_date", "animal_movement", ["movement_date"])


def downgrade() -> None:
    op.drop_index("ix_animal_movement_movement_date", table_name="animal_movement")
    op.drop_index("ix_animal_movement_movement_type", table_name="animal_movement")
    op.drop_index("ix_animal_movement_bovine_id", table_name="animal_movement")
    op.drop_index("ix_animal_movement_farm_id", table_name="animal_movement")
    op.drop_table("animal_movement")
