"""Repository for Ingrediente model — custom CRUD methods for ingredients"""

from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.ingrediente import Ingrediente
from app.repositories.base import BaseRepository


class IngredienteRepository(BaseRepository[Ingrediente]):
    """Custom repository for ingredient operations"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, Ingrediente)
    
    async def find_by_nombre(self, nombre: str) -> Optional[Ingrediente]:
        """
        Find an active ingredient by name (case-sensitive).
        
        Args:
            nombre: Ingredient name to search
            
        Returns:
            Ingrediente or None if not found or soft-deleted
        """
        query = select(self.model).where(
            self.model.nombre == nombre,
            self.model.deleted_at.is_(None)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def list_by_allergen(self, es_alergeno: bool) -> List[Ingrediente]:
        """
        List active ingredients filtered by allergen status.
        
        Args:
            es_alergeno: True to filter for allergens only
            
        Returns:
            List of ingredients matching the allergen filter
        """
        query = select(self.model).where(
            self.model.deleted_at.is_(None),
            self.model.es_alergeno == es_alergeno
        ).order_by(self.model.nombre)
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def soft_delete(self, id: int) -> None:
        """
        Soft delete an ingredient by setting deleted_at timestamp.
        
        Args:
            id: Ingredient ID to delete
            
        Raises:
            ValueError: If ingredient not found or already deleted
        """
        ingrediente = await self.find(id)
        if not ingrediente:
            raise ValueError(f"Ingrediente with id {id} not found or already deleted")
        
        from datetime import datetime, timezone
        ingrediente.deleted_at = datetime.now(timezone.utc)
        self.session.add(ingrediente)
        await self.session.flush()
    
    async def create(self, data: dict) -> Ingrediente:
        """
        Create a new ingredient.
        
        Args:
            data: Dictionary with ingredient fields
            
        Returns:
            Created Ingrediente instance
        """
        ingrediente = self.model(**data)
        self.session.add(ingrediente)
        await self.session.flush()
        await self.session.refresh(ingrediente)
        return ingrediente
    
    async def update(self, id: int, data: dict) -> Ingrediente:
        """
        Update an active ingredient.
        
        Args:
            id: Ingredient ID to update
            data: Dictionary with fields to update
            
        Returns:
            Updated Ingrediente instance
            
        Raises:
            ValueError: If ingredient not found or soft-deleted
        """
        ingrediente = await self.find(id)
        if not ingrediente:
            raise ValueError(f"Ingrediente with id {id} not found or already deleted")
        
        for key, value in data.items():
            if value is not None and hasattr(ingrediente, key):
                setattr(ingrediente, key, value)
        
        self.session.add(ingrediente)
        await self.session.flush()
        await self.session.refresh(ingrediente)
        return ingrediente
