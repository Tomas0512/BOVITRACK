"""create_reproductive_event_table

Revision ID: j1k2l3m4n5o6
Revises: i1j2k3l4m5n6
Create Date: 2026-06-08 00:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "j1k2l3m4n5o6"
down_revision: Union[str, None] = "i1j2k3l4m5n6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "reproductive_event",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("farm_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("bovine_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_type", sa.String(30), nullable=False),
        sa.Column("event_date", sa.Date(), nullable=False),
        sa.Column("result", sa.String(50), nullable=True),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("bull_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("calf_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("observations", sa.Text(), nullable=True),
        sa.Column("registered_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["farm_id"], ["farm.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["bovine_id"], ["bovine.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["bull_id"], ["bovine.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["calf_id"], ["bovine.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["registered_by"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_reproductive_event_farm_id", "reproductive_event", ["farm_id"])
    op.create_index("ix_reproductive_event_bovine_id", "reproductive_event", ["bovine_id"])
    op.create_index("ix_reproductive_event_event_type", "reproductive_event", ["event_type"])


def downgrade() -> None:
    op.drop_index("ix_reproductive_event_event_type", table_name="reproductive_event")
    op.drop_index("ix_reproductive_event_bovine_id", table_name="reproductive_event")
    op.drop_index("ix_reproductive_event_farm_id", table_name="reproductive_event")
    op.drop_table("reproductive_event")
