"""Add categorias table for hierarchical product categories

Revision ID: 004_add_categorias_table
Revises: 003_add_refresh_token
Create Date: 2026-05-09 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "004_add_categorias_table"
down_revision: Union[str, None] = "003_add_refresh_token"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create categorias table with self-referential FK for hierarchical categories."""
    op.create_table(
        "categorias",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("nombre", sa.String(length=100), nullable=False),
        sa.Column("descripcion", sa.Text(), nullable=True),
        sa.Column("parent_id", sa.Integer(), nullable=True),
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
            ["parent_id"],
            ["categorias.id"],
            name="fk_categorias_parent",
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("nombre", name="uq_categorias_nombre"),
    )
    
    # Create indexes for performance: parent_id for FK traversal, (parent_id, deleted_at) for tree queries
    op.create_index(
        op.f("ix_categorias_parent_id"),
        "categorias",
        ["parent_id"],
    )
    op.create_index(
        "ix_categorias_parent_deleted",
        "categorias",
        ["parent_id", "deleted_at"],
    )
    
    # Seed root categories
    op.execute(
        "INSERT INTO categorias (nombre, descripcion, parent_id, created_at, updated_at) "
        "VALUES ('Comidas', 'Categoría raíz de alimentos', NULL, NOW(), NOW())"
    )


def downgrade() -> None:
    """Drop categorias table and indexes."""
    op.drop_index("ix_categorias_parent_deleted", table_name="categorias")
    op.drop_index(op.f("ix_categorias_parent_id"), table_name="categorias")
    op.drop_table("categorias")
