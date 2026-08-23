"""create_notification_tables

Revision ID: o1p2q3r4s5t6
Revises: n1o2p3q4r5s6
Create Date: 2026-08-22 00:00:00.000000

¿Qué? Crea las tablas user_notification_pref y notification_log para HU014.
¿Para qué? Guardar las preferencias de notificación por usuario/finca y el
           historial de notificaciones enviadas (email/in_app).
¿Impacto? Dos tablas nuevas con relaciones a users y farm.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "o1p2q3r4s5t6"
down_revision: Union[str, None] = "n1o2p3q4r5s6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Guardas idempotentes: c9ff44fd3509 (create_all con los modelos
    # registrados en app.models) ya crea ambas tablas porque los modelos
    # NotificationLog y UserNotificationPref existen hoy. Sin la guarda,
    # la cadena completa se revierte por fallar en una sola transacción.
    insp = sa.inspect(op.get_bind())

    if not insp.has_table("user_notification_pref"):
        op.create_table(
            "user_notification_pref",
            sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("farm_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("channel", sa.String(20), nullable=False),
            sa.Column("notify_sanitary", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column("notify_low_stock", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column("notify_reproductive", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column("notify_birth", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column("frequency", sa.String(20), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["farm_id"], ["farm.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("user_id", "farm_id", name="uq_user_notification_pref"),
        )
        op.create_index(
            op.f("ix_user_notification_pref_user_id"), "user_notification_pref", ["user_id"]
        )
        op.create_index(
            op.f("ix_user_notification_pref_farm_id"), "user_notification_pref", ["farm_id"]
        )

    if not insp.has_table("notification_log"):
        op.create_table(
            "notification_log",
            sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("farm_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column("type", sa.String(30), nullable=False),
            sa.Column("title", sa.String(255), nullable=False),
            sa.Column("message", sa.Text(), nullable=True),
            sa.Column("channel", sa.String(20), nullable=False),
            sa.Column("status", sa.String(20), nullable=False),
            sa.Column("reference_id", sa.String(100), nullable=True),
            sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.ForeignKeyConstraint(["farm_id"], ["farm.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_notification_log_farm_id"), "notification_log", ["farm_id"])
        op.create_index(op.f("ix_notification_log_user_id"), "notification_log", ["user_id"])
        op.create_index(op.f("ix_notification_log_type"), "notification_log", ["type"])
        op.create_index(op.f("ix_notification_log_reference_id"), "notification_log", ["reference_id"])
        op.create_index(op.f("ix_notification_log_created_at"), "notification_log", ["created_at"])


def downgrade() -> None:
    insp = sa.inspect(op.get_bind())

    if insp.has_table("notification_log"):
        op.drop_index(op.f("ix_notification_log_created_at"), table_name="notification_log")
        op.drop_index(op.f("ix_notification_log_reference_id"), table_name="notification_log")
        op.drop_index(op.f("ix_notification_log_type"), table_name="notification_log")
        op.drop_index(op.f("ix_notification_log_user_id"), table_name="notification_log")
        op.drop_index(op.f("ix_notification_log_farm_id"), table_name="notification_log")
        op.drop_table("notification_log")

    if insp.has_table("user_notification_pref"):
        op.drop_index(op.f("ix_user_notification_pref_farm_id"), table_name="user_notification_pref")
        op.drop_index(op.f("ix_user_notification_pref_user_id"), table_name="user_notification_pref")
        op.drop_table("user_notification_pref")
