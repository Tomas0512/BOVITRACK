"""add reactivation_request, land_plot.location, paddock.pasture_type

Revision ID: g1h2i3j4k5l6
Revises: f1a2b3c4d5e6
Create Date: 2025-01-01 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision: str = "g1h2i3j4k5l6"
down_revision: Union[str, None] = "f1a2b3c4d5e6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- reactivation_request table ---
    op.create_table(
        "reactivation_request",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("reviewed_by", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
    )

    # --- land_plot.location ---
    op.add_column("land_plot", sa.Column("location", sa.String(255), nullable=True))

    # --- paddock.pasture_type ---
    op.add_column("paddock", sa.Column("pasture_type", sa.String(50), nullable=True))


def downgrade() -> None:
    op.drop_column("paddock", "pasture_type")
    op.drop_column("land_plot", "location")
    op.drop_table("reactivation_request")
