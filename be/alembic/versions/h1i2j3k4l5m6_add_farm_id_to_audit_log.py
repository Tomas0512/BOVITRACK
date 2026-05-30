"""add farm_id to audit_log

Revision ID: h1i2j3k4l5m6
Revises: g1h2i3j4k5l6
Create Date: 2026-05-30 00:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "h1i2j3k4l5m6"
down_revision: Union[str, None] = "g1h2i3j4k5l6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "audit_log",
        sa.Column("farm_id", sa.UUID(), nullable=True),
    )
    op.create_foreign_key(
        "fk_audit_log_farm_id",
        "audit_log",
        "farm",
        ["farm_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_audit_log_farm_id", "audit_log", ["farm_id"])


def downgrade() -> None:
    op.drop_index("ix_audit_log_farm_id", table_name="audit_log")
    op.drop_constraint("fk_audit_log_farm_id", "audit_log", type_="foreignkey")
    op.drop_column("audit_log", "farm_id")
