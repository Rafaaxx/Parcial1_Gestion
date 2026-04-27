"""Initial schema setup

Revision ID: 001_initial
Revises: 
Create Date: 2026-04-21 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Create initial schema for Food Store.
    
    This is a placeholder migration. After the app models are finalized,
    generate actual migrations with: alembic revision --autogenerate -m "description"
    """
    pass


def downgrade() -> None:
    """
    Revert initial schema.
    """
    pass
