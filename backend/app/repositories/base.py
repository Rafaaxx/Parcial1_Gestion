"""Generic BaseRepository[T] implementation for CRUD operations"""

import logging
from typing import TypeVar, Generic, Optional, List, Type, Any, Dict
from datetime import datetime, timezone

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel

from app.models.mixins import SoftDeleteMixin

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=SQLModel)


class BaseRepository(Generic[T]):
    """Generic repository for common CRUD operations on any SQLModel entity"""
    
    def __init__(self, session: AsyncSession, model: Type[T]):
        """
        Initialize repository with session and model type
        
        Args:
            session: AsyncSession instance
            model: SQLModel type to manage
        """
        self.session = session
        self.model = model
        self.logger = logging.getLogger(f"{__name__}.{model.__name__}")
    
    async def find(self, entity_id: Any) -> Optional[T]:
        """
        Find entity by primary key, excluding soft-deleted records
        
        Args:
            entity_id: Primary key value
            
        Returns:
            Entity instance or None if not found
        """
        query = select(self.model).where(self.model.id == entity_id)
        
        # Exclude soft-deleted if model supports it
        if issubclass(self.model, SoftDeleteMixin):
            query = query.where(self.model.deleted_at.is_(None))
        
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def list_all(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[Any] = None,
    ) -> tuple[List[T], int]:
        """
        List entities with pagination and optional filtering
        
        Args:
            skip: Offset for pagination
            limit: Number of records to return
            filters: Dictionary of column:value filters
            order_by: SQLAlchemy order_by clause
            
        Returns:
            Tuple of (entities list, total count)
        """
        query = select(self.model)
        
        # Exclude soft-deleted records
        if issubclass(self.model, SoftDeleteMixin):
            query = query.where(self.model.deleted_at.is_(None))
        
        # Apply filters
        if filters:
            for column_name, value in filters.items():
                if hasattr(self.model, column_name):
                    query = query.where(getattr(self.model, column_name) == value)
        
        # Get total count before pagination
        count_query = select(func.count()).select_from(self.model)
        if issubclass(self.model, SoftDeleteMixin):
            count_query = count_query.where(self.model.deleted_at.is_(None))
        if filters:
            for column_name, value in filters.items():
                if hasattr(self.model, column_name):
                    count_query = count_query.where(getattr(self.model, column_name) == value)
        
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()
        
        # Apply ordering
        if order_by is not None:
            query = query.order_by(order_by)
        elif hasattr(self.model, 'id'):
            query = query.order_by(self.model.id)
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        result = await self.session.execute(query)
        return result.scalars().all(), total
    
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count entities matching filters (excluding soft-deleted)
        
        Args:
            filters: Optional filters dictionary
            
        Returns:
            Count of matching entities
        """
        query = select(func.count()).select_from(self.model)
        
        # Exclude soft-deleted records
        if issubclass(self.model, SoftDeleteMixin):
            query = query.where(self.model.deleted_at.is_(None))
        
        # Apply filters
        if filters:
            for column_name, value in filters.items():
                if hasattr(self.model, column_name):
                    query = query.where(getattr(self.model, column_name) == value)
        
        result = await self.session.execute(query)
        return result.scalar()
    
    async def create(self, obj: T) -> T:
        """
        Create new entity
        
        Args:
            obj: Entity instance (must not have ID yet)
            
        Returns:
            Created entity with generated ID
        """
        self.session.add(obj)
        await self.session.flush()  # Flush to generate ID without committing
        await self.session.refresh(obj)
        self.logger.debug(f"Created {self.model.__name__} with id={obj.id}")
        return obj
    
    async def update(self, entity_id: Any, update_data: Dict[str, Any]) -> Optional[T]:
        """
        Update entity by ID
        
        Args:
            entity_id: Primary key value
            update_data: Dictionary of fields to update
            
        Returns:
            Updated entity or None if not found
        """
        entity = await self.find(entity_id)
        if not entity:
            return None
        
        # Update fields
        for key, value in update_data.items():
            if hasattr(entity, key):
                setattr(entity, key, value)
        
        # Update timestamp if model has it
        if hasattr(entity, 'updated_at'):
            entity.updated_at = datetime.now(timezone.utc)
        
        self.session.add(entity)
        await self.session.flush()
        await self.session.refresh(entity)
        self.logger.debug(f"Updated {self.model.__name__} with id={entity_id}")
        return entity
    
    async def delete(self, entity_id: Any) -> bool:
        """
        Hard delete entity (physically removes from database)
        
        Args:
            entity_id: Primary key value
            
        Returns:
            True if deleted, False if not found
        """
        entity = await self.session.get(self.model, entity_id)
        if not entity:
            return False
        
        await self.session.delete(entity)
        await self.session.flush()
        self.logger.debug(f"Hard deleted {self.model.__name__} with id={entity_id}")
        return True
    
    async def soft_delete(self, entity_id: Any) -> Optional[T]:
        """
        Soft delete entity (sets deleted_at timestamp)
        
        Args:
            entity_id: Primary key value
            
        Returns:
            Updated entity or None if not found or doesn't support soft delete
        """
        if not issubclass(self.model, SoftDeleteMixin):
            raise ValueError(f"{self.model.__name__} doesn't support soft delete")
        
        entity = await self.session.get(self.model, entity_id)
        if not entity:
            return None
        
        entity.deleted_at = datetime.now(timezone.utc)
        if hasattr(entity, 'updated_at'):
            entity.updated_at = datetime.now(timezone.utc)
        
        self.session.add(entity)
        await self.session.flush()
        await self.session.refresh(entity)
        self.logger.debug(f"Soft deleted {self.model.__name__} with id={entity_id}")
        return entity
    
    async def exists(self, entity_id: Any) -> bool:
        """
        Check if entity exists (excluding soft-deleted)
        
        Args:
            entity_id: Primary key value
            
        Returns:
            True if entity exists and not soft-deleted
        """
        entity = await self.find(entity_id)
        return entity is not None
