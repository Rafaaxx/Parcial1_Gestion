"""SQLModel mixins for common patterns (timestamps, soft delete)

NOTE: We use ``sa_type`` + ``sa_column_kwargs`` instead of ``sa_column``
because ``sa_column=Column(...)`` creates a SINGLE Column object shared
across ALL subclasses, causing ``ArgumentError: Column object '...' already
assigned to Table '...'`` when multiple models inherit the same mixin.
Using ``sa_column_kwargs`` lets SQLModel create a fresh Column per subclass.
"""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, func
from sqlmodel import Field, SQLModel


def _utcnow() -> datetime:
    """Return current UTC datetime as timezone-aware.

    Replacement for deprecated datetime.utcnow().
    Always returns datetime with timezone.utc info.
    """
    return datetime.now(timezone.utc)


class TimestampMixin(SQLModel):
    """Mixin that adds created_at and updated_at timestamps to models"""

    created_at: datetime = Field(
        default_factory=_utcnow,
        sa_type=DateTime(timezone=True),
        sa_column_kwargs={"server_default": func.now(), "nullable": False},
        description="Record creation timestamp (UTC)",
    )
    updated_at: datetime = Field(
        default_factory=_utcnow,
        sa_type=DateTime(timezone=True),
        sa_column_kwargs={
            "server_default": func.now(),
            "onupdate": func.now(),
            "nullable": False,
        },
        description="Record last update timestamp (UTC)",
    )


class SoftDeleteMixin(SQLModel):
    """Mixin that adds soft delete capability (deleted_at field)"""

    deleted_at: Optional[datetime] = Field(
        default=None,
        sa_type=DateTime(timezone=True),
        sa_column_kwargs={"nullable": True},
        description="Soft delete timestamp - NULL if not deleted",
    )

    def is_deleted(self) -> bool:
        """Check if record is soft-deleted"""
        return self.deleted_at is not None


class BaseModel(TimestampMixin, SoftDeleteMixin):
    """Base model combining both timestamp and soft delete mixins"""

    pass
