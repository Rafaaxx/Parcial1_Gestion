"""Fix categorias unique constraint to partial index for soft-delete support

Revision ID: 005_fix_categorias_unique_constraint
Revises: 004_add_categorias_table
Create Date: 2026-05-09 00:00:00.000000

Problem: UNIQUE(nombre) prevents reusing category names after soft-delete.
Solution: Replace with partial unique index WHERE deleted_at IS NULL.

This allows:
- After deleting "Comidas", creating "Comidas" again
- Soft-deleted categories don't block new ones with same name
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "005_fix_cat_unique_constraint"
down_revision: Union[str, None] = "004_add_categorias_table"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Replace UNIQUE constraint with partial index on non-deleted categories."""
    # Drop the global UNIQUE constraint
    op.drop_constraint("uq_categorias_nombre", "categorias", type_="unique")
    
    # Create partial unique index: only enforce uniqueness for non-soft-deleted rows
    op.create_index(
        "uq_categorias_nombre_not_deleted",
        "categorias",
        ["nombre"],
        postgresql_where="deleted_at IS NULL",
        unique=True,
    )


def downgrade() -> None:
    """Restore the global UNIQUE constraint."""
    # Drop partial index
    op.drop_index("uq_categorias_nombre_not_deleted", table_name="categorias")
    
    # Restore UNIQUE constraint
    op.create_unique_constraint(
        "uq_categorias_nombre",
        "categorias",
        ["nombre"],
    )
