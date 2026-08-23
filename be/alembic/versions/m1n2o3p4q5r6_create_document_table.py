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
    # ¿Por qué la guarda? La migración previa c9ff44fd3509 usa
    # Base.metadata.create_all(checkfirst=True), que ya crea `document`
    # porque el modelo Document está registrado en app.models. Sin esta
    # guarda, la cadena completa falla y Alembic revierte TODO (incluidas
    # las migraciones i1..l1) al ejecutarse en una sola transacción.
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
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("TRUE"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(["farm_id"], ["farm.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["uploaded_by"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["deleted_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("stored_filename"),
    )
    op.create_index("ix_document_farm_id", "document", ["farm_id"])
    op.create_index("ix_document_association_type", "document", ["association_type"])
    op.create_index("ix_document_associated_entity_id", "document", ["associated_entity_id"])
    op.create_index("ix_document_uploaded_at", "document", ["uploaded_at"])


def downgrade() -> None:
    conn = op.get_bind()
    if not sa.inspect(conn).has_table("document"):
        return

    op.drop_index("ix_document_uploaded_at", table_name="document")
    op.drop_index("ix_document_associated_entity_id", table_name="document")
    op.drop_index("ix_document_association_type", table_name="document")
    op.drop_index("ix_document_farm_id", table_name="document")
    op.drop_table("document")
