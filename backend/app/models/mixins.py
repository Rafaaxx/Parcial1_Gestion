"""SQLModel mixins for common patterns (timestamps, soft delete)"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, DateTime, func
from sqlmodel import SQLModel, Field


class TimestampMixin(SQLModel):
    """Mixin that adds created_at and updated_at timestamps to models"""
    
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False),
        description="Record creation timestamp (UTC)"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False),
        description="Record last update timestamp (UTC)"
    )


class SoftDeleteMixin(SQLModel):
    """Mixin that adds soft delete capability (deleted_at field)"""
    
    deleted_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
        description="Soft delete timestamp - NULL if not deleted"
    )
    
    def is_deleted(self) -> bool:
        """Check if record is soft-deleted"""
        return self.deleted_at is not None


class BaseModel(TimestampMixin, SoftDeleteMixin):
    """Base model combining both timestamp and soft delete mixins"""
    pass
