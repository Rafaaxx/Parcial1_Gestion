"""Add direcciones_entrega table with FK to usuarios, partial unique index for default address

Revision ID: 007_add_direcciones_table
Revises: 006_add_ingredientes_table
Create Date: 2026-05-11 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "007_add_direcciones_table"
down_revision: Union[str, None] = "006_add_ingredientes_table"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create direcciones_entrega table with FK, indexes, and partial unique constraint."""
    op.create_table(
        "direcciones_entrega",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("usuario_id", sa.Integer(), nullable=False),
        sa.Column("alias", sa.String(length=50), nullable=True),
        sa.Column("linea1", sa.String(length=500), nullable=False),
        sa.Column(
            "es_principal",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
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
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["usuario_id"],
            ["usuarios.id"],
            name="fk_direcciones_usuario",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Index for listing addresses of a user
    op.create_index(
        "idx_direcciones_usuario",
        "direcciones_entrega",
        ["usuario_id"],
    )

    # Partial unique index: at most one es_principal=true per user (non-deleted)
    op.execute(
        "CREATE UNIQUE INDEX idx_direccion_principal_unico "
        "ON direcciones_entrega (usuario_id) "
        "WHERE es_principal = true AND deleted_at IS NULL"
    )

    # Partial index for listing only active (non-deleted) addresses
    op.execute(
        "CREATE INDEX idx_direcciones_usuario_activas "
        "ON direcciones_entrega (usuario_id) "
        "WHERE deleted_at IS NULL"
    )


def downgrade() -> None:
    """Drop direcciones_entrega table and indexes."""
    op.execute("DROP INDEX IF EXISTS idx_direccion_principal_unico")
    op.execute("DROP INDEX IF EXISTS idx_direcciones_usuario_activas")
    op.drop_index("idx_direcciones_usuario", table_name="direcciones_entrega")
    op.drop_table("direcciones_entrega")
