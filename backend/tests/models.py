"""Test-only SQLModel models for testing infrastructure patterns.

These models are used exclusively in unit tests for the generic
BaseRepository and UnitOfWork. They are NOT part of the application
domain model.
"""

from typing import Optional

from sqlmodel import Field, SQLModel

from app.models.mixins import SoftDeleteMixin, TimestampMixin


class TestModel(TimestampMixin, SoftDeleteMixin, SQLModel, table=True):
    """Model with soft-delete support — used for repository tests."""

    __tablename__ = "test_entities"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    value: int = Field(default=0)


class UoWTestModel(TimestampMixin, SQLModel, table=True):
    """Simple model without soft-delete — used for isolation tests."""

    __tablename__ = "uow_test_entities"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
