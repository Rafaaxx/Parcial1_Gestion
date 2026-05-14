"""merge branches

Revision ID: 35014a9f706a
Revises: 007_add_direcciones_table, 5fb466c177a6
Create Date: 2026-05-12 11:46:21.518802

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "35014a9f706a"
down_revision: Union[str, None] = ("007_add_direcciones_table", "5fb466c177a6")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
