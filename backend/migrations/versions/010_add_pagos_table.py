"""Add pagos table for MercadoPago integration

Revision ID: 010_add_pagos_table
Revises: 009_merge_pedidos_products
Create Date: 2026-05-12

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "010_add_pagos_table"
down_revision: Union[str, None] = "009_merge_pedidos_products"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create pagos table for MercadoPago integration."""

    # ── Tabla: pagos ──────────────────────────────────────────────────────────

    op.create_table(
        "pagos",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("pedido_id", sa.BigInteger(), nullable=False),
        sa.Column("mp_payment_id", sa.BigInteger(), nullable=True, unique=True),
        sa.Column(
            "mp_status",
            sa.String(length=30),
            nullable=False,
            server_default="pending",
        ),
        sa.Column(
            "mp_status_detail",
            sa.String(length=200),
            nullable=True,
        ),
        sa.Column(
            "external_reference",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "idempotency_key",
            sa.String(length=100),
            nullable=False,
            unique=True,
        ),
        sa.Column(
            "monto",
            sa.Numeric(precision=10, scale=2),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index("ix_pagos_pedido_id", "pagos", ["pedido_id"])
    op.create_index("ix_pagos_mp_status", "pagos", ["mp_status"])
    op.create_index("ix_pagos_external_reference", "pagos", ["external_reference"])

    op.create_foreign_key(
        "fk_pagos_pedido_id",
        "pagos",
        "pedidos",
        ["pedido_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    """Drop pagos table."""
    op.drop_table("pagos")