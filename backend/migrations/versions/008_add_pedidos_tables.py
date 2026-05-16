"""Add pedidos, detalles_pedido, historial_estado_pedido tables

Revision ID: 008_add_pedidos_tables
Revises: 007_add_direcciones_table
Create Date: 2026-05-12

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "008_add_pedidos_tables"
down_revision: Union[str, None] = "007_add_direcciones_table"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create pedidos, detalles_pedido, historial_estado_pedido tables."""

    # ── Tabla: pedidos ──────────────────────────────────────────────────────────

    op.create_table(
        "pedidos",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("usuario_id", sa.BigInteger(), nullable=False),
        sa.Column("estado_codigo", sa.String(length=20), nullable=False),
        sa.Column(
            "total",
            sa.Numeric(precision=10, scale=2),
            nullable=False,
            server_default="0.00",
        ),
        sa.Column(
            "costo_envio",
            sa.Numeric(precision=10, scale=2),
            nullable=False,
            server_default="50.00",
        ),
        sa.Column("forma_pago_codigo", sa.String(length=20), nullable=False),
        sa.Column("direccion_id", sa.BigInteger(), nullable=True),
        sa.Column("notas", sa.Text(), nullable=True),
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

    op.create_index("ix_pedidos_usuario_id", "pedidos", ["usuario_id"])
    op.create_index("ix_pedidos_estado_codigo", "pedidos", ["estado_codigo"])

    op.create_foreign_key(
        "fk_pedidos_usuario_id",
        "pedidos",
        "usuarios",
        ["usuario_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "fk_pedidos_estado_codigo",
        "pedidos",
        "estados_pedido",
        ["estado_codigo"],
        ["codigo"],
    )
    op.create_foreign_key(
        "fk_pedidos_forma_pago_codigo",
        "pedidos",
        "formas_pago",
        ["forma_pago_codigo"],
        ["codigo"],
    )
    op.create_foreign_key(
        "fk_pedidos_direccion_id",
        "pedidos",
        "direcciones_entrega",
        ["direccion_id"],
        ["id"],
        ondelete="SET NULL",
    )

    # ── Tabla: detalles_pedido ─────────────────────────────────────────────────

    op.create_table(
        "detalles_pedido",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("pedido_id", sa.BigInteger(), nullable=False),
        sa.Column("producto_id", sa.BigInteger(), nullable=False),
        sa.Column("nombre_snapshot", sa.String(length=200), nullable=False),
        sa.Column(
            "precio_snapshot",
            sa.Numeric(precision=10, scale=2),
            nullable=False,
        ),
        sa.Column("cantidad", sa.Integer(), nullable=False, server_default="1"),
        sa.Column(
            "personalizacion",
            postgresql.JSON(),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index("ix_detalles_pedido_pedido_id", "detalles_pedido", ["pedido_id"])
    op.create_index("ix_detalles_pedido_producto_id", "detalles_pedido", ["producto_id"])

    op.create_foreign_key(
        "fk_detalles_pedido_pedido_id",
        "detalles_pedido",
        "pedidos",
        ["pedido_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "fk_detalles_pedido_producto_id",
        "detalles_pedido",
        "productos",
        ["producto_id"],
        ["id"],
        ondelete="CASCADE",
    )

    # ── Tabla: historial_estado_pedido (append-only audit trail) ───────────────

    op.create_table(
        "historial_estado_pedido",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("pedido_id", sa.BigInteger(), nullable=False),
        sa.Column("estado_desde", sa.String(length=20), nullable=True),
        sa.Column("estado_hacia", sa.String(length=20), nullable=False),
        sa.Column("observacion", sa.Text(), nullable=True),
        sa.Column("usuario_id", sa.BigInteger(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_historial_estado_pedido_pedido_id",
        "historial_estado_pedido",
        ["pedido_id"],
    )

    op.create_foreign_key(
        "fk_historial_pedido_pedido_id",
        "historial_estado_pedido",
        "pedidos",
        ["pedido_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "fk_historial_estado_desde",
        "historial_estado_pedido",
        "estados_pedido",
        ["estado_desde"],
        ["codigo"],
    )
    op.create_foreign_key(
        "fk_historial_estado_hacia",
        "historial_estado_pedido",
        "estados_pedido",
        ["estado_hacia"],
        ["codigo"],
    )


def downgrade() -> None:
    """Drop pedidos tables in reverse dependency order."""

    op.drop_table("historial_estado_pedido")
    op.drop_table("detalles_pedido")
    op.drop_table("pedidos")
