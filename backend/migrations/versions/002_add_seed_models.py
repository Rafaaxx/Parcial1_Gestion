"""Add seed models: roles, estados_pedido, formas_pago, usuarios, usuarios_roles

Revision ID: 002_add_seed_models
Revises: 001_initial
Create Date: 2026-05-08 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "002_add_seed_models"
down_revision: Union[str, None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create tables for seed data models."""

    # ── roles ────────────────────────────────────────────────────────────────
    op.create_table(
        "roles",
        sa.Column("codigo", sa.String(20), primary_key=True),
        sa.Column("descripcion", sa.String(100), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    # ── estados_pedido ───────────────────────────────────────────────────────
    op.create_table(
        "estados_pedido",
        sa.Column("codigo", sa.String(20), primary_key=True),
        sa.Column("descripcion", sa.String(100), nullable=False),
        sa.Column("orden", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("es_terminal", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    # ── formas_pago ──────────────────────────────────────────────────────────
    op.create_table(
        "formas_pago",
        sa.Column("codigo", sa.String(20), primary_key=True),
        sa.Column("descripcion", sa.String(100), nullable=False),
        sa.Column("habilitado", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    # ── usuarios ─────────────────────────────────────────────────────────────
    op.create_table(
        "usuarios",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("email", sa.String(254), unique=True, nullable=False),
        sa.Column("password_hash", sa.String(60), nullable=False),
        sa.Column("nombre", sa.String(100), nullable=False),
        sa.Column("apellido", sa.String(100), nullable=False),
        sa.Column("telefono", sa.String(20), nullable=True),
        sa.Column("activo", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "deleted_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

    # Index on email for fast lookups
    op.create_index("ix_usuarios_email", "usuarios", ["email"])
    # Index on soft-delete column
    op.create_index("ix_usuarios_deleted_at", "usuarios", ["deleted_at"])

    # ── usuarios_roles ───────────────────────────────────────────────────────
    op.create_table(
        "usuarios_roles",
        sa.Column("usuario_id", sa.BigInteger(), primary_key=True, nullable=False),
        sa.Column("rol_codigo", sa.String(20), primary_key=True, nullable=False),
        sa.Column("asignado_por_id", sa.BigInteger(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["usuario_id"],
            ["usuarios.id"],
            name="fk_usuarios_roles_usuario",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["rol_codigo"],
            ["roles.codigo"],
            name="fk_usuarios_roles_rol",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["asignado_por_id"],
            ["usuarios.id"],
            name="fk_usuarios_roles_asignado_por",
            ondelete="SET NULL",
        ),
    )

    op.create_index("ix_usuarios_roles_usuario", "usuarios_roles", ["usuario_id"])
    op.create_index("ix_usuarios_roles_rol", "usuarios_roles", ["rol_codigo"])


def downgrade() -> None:
    """Drop all seed tables in reverse dependency order."""
    op.drop_table("usuarios_roles")
    op.drop_table("usuarios")
    op.drop_table("formas_pago")
    op.drop_table("estados_pedido")
    op.drop_table("roles")
