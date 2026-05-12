"""merge branches: pedidos tables merged with existing product branches

Revision ID: 009_merge_pedidos_products
Revises: 008_add_pedidos_tables, 35014a9f706a
Create Date: 2026-05-12
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "009_merge_pedidos_products"
down_revision: Union[str, None] = ("008_add_pedidos_tables", "35014a9f706a")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """No-op merge — just joins the two branches."""
    pass


def downgrade() -> None:
    """No-op merge."""
    pass
