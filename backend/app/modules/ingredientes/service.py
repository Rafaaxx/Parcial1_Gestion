"""Business logic service for ingredient management"""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.ingrediente_repository import IngredienteRepository
from app.modules.ingredientes.schemas import (
    IngredienteCreate,
    IngredienteUpdate,
    IngredienteRead,
    IngredienteListResponse,
)


class IngredienteService:
    """Service for ingredient business logic"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = IngredienteRepository(session)
    
    async def create_ingrediente(self, data: IngredienteCreate) -> IngredienteRead:
        """
        Create a new ingredient after validating uniqueness.
        
        Args:
            data: IngredienteCreate schema
            
        Returns:
            IngredienteRead with created ingredient
            
        Raises:
            ValueError: If ingredient with same nombre already exists
        """
        # Check if nombre already exists
        existing = await self.repository.find_by_nombre(data.nombre)
        if existing:
            raise ValueError(f"Ingrediente with nombre '{data.nombre}' already exists")
        
        # Create new ingredient
        ingrediente = await self.repository.create(data.model_dump())
        return IngredienteRead.model_validate(ingrediente)
    
    async def list_ingredientes(
        self,
        skip: int = 0,
        limit: int = 100,
        es_alergeno: Optional[bool] = None,
    ) -> IngredienteListResponse:
        """
        List active ingredients with optional allergen filter.
        
        Args:
            skip: Pagination offset
            limit: Pagination limit
            es_alergeno: Optional filter for allergens only
            
        Returns:
            IngredienteListResponse with paginated results
        """
        # Build filters
        filters = {}
        if es_alergeno is not None:
            filters["es_alergeno"] = es_alergeno
        
        # Get list with pagination
        items, total = await self.repository.list_all(
            skip=skip,
            limit=limit,
            filters=filters if filters else None,
            order_by=self.repository.model.nombre,
        )
        
        return IngredienteListResponse(
            items=[IngredienteRead.model_validate(item) for item in items],
            total=total,
            skip=skip,
            limit=limit,
        )
    
    async def get_ingrediente_by_id(self, id: int) -> IngredienteRead:
        """
        Get a single active ingredient by ID.
        
        Args:
            id: Ingredient ID
            
        Returns:
            IngredienteRead
            
        Raises:
            ValueError: If ingredient not found or soft-deleted
        """
        ingrediente = await self.repository.find(id)
        if not ingrediente:
            raise ValueError(f"Ingrediente with id {id} not found")
        return IngredienteRead.model_validate(ingrediente)
    
    async def update_ingrediente(
        self,
        id: int,
        data: IngredienteUpdate,
    ) -> IngredienteRead:
        """
        Update an active ingredient.
        
        Args:
            id: Ingredient ID
            data: IngredienteUpdate schema
            
        Returns:
            IngredienteRead with updated data
            
        Raises:
            ValueError: If ingredient not found, soft-deleted, or nombre not unique
        """
        ingrediente = await self.repository.find(id)
        if not ingrediente:
            raise ValueError(f"Ingrediente with id {id} not found")
        
        # If nombre is being updated, check uniqueness
        if data.nombre and data.nombre != ingrediente.nombre:
            existing = await self.repository.find_by_nombre(data.nombre)
            if existing:
                raise ValueError(f"Ingrediente with nombre '{data.nombre}' already exists")
        
        # Update
        update_data = data.model_dump(exclude_unset=True)
        ingrediente = await self.repository.update(id, update_data)
        return IngredienteRead.model_validate(ingrediente)
    
    async def delete_ingrediente(self, id: int) -> None:
        """
        Soft delete an ingredient.
        
        Args:
            id: Ingredient ID
            
        Raises:
            ValueError: If ingredient not found or already deleted
        """
        await self.repository.soft_delete(id)
        await self.session.commit()
    
    async def commit(self) -> None:
        """Commit pending changes"""
        await self.session.commit()
