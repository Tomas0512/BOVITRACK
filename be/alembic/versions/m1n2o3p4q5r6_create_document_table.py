"""create_document_table

Revision ID: m1n2o3p4q5r6
Revises: c9ff44fd3509
Create Date: 2026-06-16 19:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "m1n2o3p4q5r6"
down_revision: Union[str, None] = "c9ff44fd3509"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ¿Por qué la guarda? Las BD creadas cuando c9ff44fd3509 usaba
    # Base.metadata.create_all() ya tienen `document` (creada desde el modelo).
    # En una BD nueva esta migración es la que la crea, con la MISMA forma que
    # dejó create_all (sin índices extra ni server_default), así cualquier BD
    # termina idéntica.
    conn = op.get_bind()
    if sa.inspect(conn).has_table("document"):
        return

    op.create_table(
        "document",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("farm_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("original_filename", sa.String(255), nullable=False),
        sa.Column("stored_filename", sa.String(255), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column("mime_type", sa.String(50), nullable=False),
        sa.Column("document_type", sa.String(20), nullable=False),
        sa.Column("association_type", sa.String(30), nullable=False),
        sa.Column("associated_entity_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("uploaded_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(["farm_id"], ["farm.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["uploaded_by"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["deleted_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("stored_filename"),
    )


def downgrade() -> None:
    # drop_table también borra los índices y FKs de la tabla.
    if sa.inspect(op.get_bind()).has_table("document"):
        op.drop_table("document")
