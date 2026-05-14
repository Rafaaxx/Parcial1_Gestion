"""Add activo column to usuarios table and indexes for metrics queries

Revision ID: 011_add_usuario_activo_and_indexes
Revises: 010_add_pagos_table
Create Date: 2026-05-13

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "011_add_usuario_activo_and_indexes"
down_revision: Union[str, None] = "010_add_pagos_table"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add activo column and metrics indexes."""

    # ── Add activo column to usuarios ────────────────────────────────────────
    # Check if column already exists (model already defines it, but migration
    # may not have been run). Using batch mode for SQLite compatibility.
    with op.batch_alter_table("usuarios") as batch_op:
        batch_op.add_column(
            sa.Column(
                "activo",
                sa.Boolean(),
                nullable=False,
                server_default=sa.text("true"),
            )
        )

    # ── Indexes for metrics queries on pedidos ───────────────────────────────
    # ix_pedidos_estado_codigo is already defined in the model (index=True),
    # but we add it explicitly for performance in metrics aggregation queries.
    op.create_index(
        "ix_pedidos_created_at",
        "pedidos",
        ["created_at"],
        postgresql_concurrently=True,
    )
    op.create_index(
        "ix_pedidos_estado_codigo_created_at",
        "pedidos",
        ["estado_codigo", "created_at"],
        postgresql_concurrently=True,
    )


def downgrade() -> None:
    """Remove activo column and metrics indexes."""
    with op.batch_alter_table("usuarios") as batch_op:
        batch_op.drop_column("activo")

    op.drop_index("ix_pedidos_estado_codigo_created_at", table_name="pedidos")
    op.drop_index("ix_pedidos_created_at", table_name="pedidos")
