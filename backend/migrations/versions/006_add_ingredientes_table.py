"""Add ingredientes table with allergen flag and soft delete support

Revision ID: 006_add_ingredientes_table
Revises: 005_fix_cat_unique_constraint
Create Date: 2026-05-11 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "006_add_ingredientes_table"
down_revision: Union[str, None] = "005_fix_cat_unique_constraint"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create ingredientes table with allergen flag, soft delete, and partial unique constraint."""
    op.create_table(
        "ingredientes",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("nombre", sa.String(length=255), nullable=False),
        sa.Column("es_alergeno", sa.Boolean(), server_default="false", nullable=False),
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
        sa.PrimaryKeyConstraint("id"),
    )
    
    # Create partial unique constraint: UNIQUE (nombre) WHERE deleted_at IS NULL
    # This allows reusing ingredient names after soft-delete
    op.create_index(
        "uq_ingredientes_nombre",
        "ingredientes",
        ["nombre"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )
    
    # Create indexes for query performance
    op.create_index(
        op.f("ix_ingredientes_nombre"),
        "ingredientes",
        ["nombre"],
    )
    op.create_index(
        op.f("ix_ingredientes_es_alergeno"),
        "ingredientes",
        ["es_alergeno"],
    )


def downgrade() -> None:
    """Drop ingredientes table and indexes."""
    op.drop_index(op.f("ix_ingredientes_es_alergeno"), table_name="ingredientes")
    op.drop_index(op.f("ix_ingredientes_nombre"), table_name="ingredientes")
    op.drop_index("uq_ingredientes_nombre", table_name="ingredientes")
    op.drop_table("ingredientes")
