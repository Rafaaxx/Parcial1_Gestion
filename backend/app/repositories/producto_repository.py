"""ProductoRepository — repository for Producto model with filtering and associations"""
import logging
from typing import Optional, List, Dict, Any, Tuple
from decimal import Decimal
from sqlalchemy import select, func, and_, or_, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.producto import Producto, ProductoCategoria, ProductoIngrediente
from app.repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class ProductoRepository(BaseRepository[Producto]):
    """
    Repository for Producto CRUD operations with:
    - Advanced filtering (category, availability, search, price range)
    - Pagination
    - Atomic stock updates (SELECT FOR UPDATE)
    - Association management with categories and ingredients
    """
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, Producto)
    
    async def find_with_associations(self, producto_id: int) -> Optional[Producto]:
        """
        Find a product with its categories and ingredients eagerly loaded.
        
        Args:
            producto_id: Product ID
            
        Returns:
            Producto with relaciones cargadas o None
        """
        query = (
            select(Producto)
            .options(
                selectinload(Producto.categorias).selectinload(ProductoCategoria.categoria),
                selectinload(Producto.ingredientes).selectinload(ProductoIngrediente.ingrediente),
            )
            .where(Producto.id == producto_id)
            .where(Producto.deleted_at.is_(None))
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def list_with_filters(
        self,
        skip: int = 0,
        limit: int = 20,
        categoria_id: Optional[int] = None,
        disponible: Optional[bool] = None,
        busqueda: Optional[str] = None,
        precio_desde: Optional[Decimal] = None,
        precio_hasta: Optional[Decimal] = None,
        allergen_ids: Optional[List[int]] = None,
        order_by: Optional[Any] = None,
    ) -> Tuple[List[Producto], int]:
        """
        List products with advanced filtering and pagination.
        
        Args:
            skip: Pagination offset
            limit: Max results per page
            categoria_id: Filter by category ID (via productos_categorias)
            disponible: Filter by availability flag
            busqueda: Search by name (ILIKE, case-insensitive)
            precio_desde: Minimum price filter
            precio_hasta: Maximum price filter
            allergen_ids: List of ingredient IDs to exclude (NOT EXISTS logic)
            order_by: SQLAlchemy order_by clause
            
        Returns:
            Tuple of (list of products, total count)
        """
        # Build base query with soft-delete filter
        query = select(Producto).where(Producto.deleted_at.is_(None))
        count_query = select(func.count()).select_from(Producto).where(
            Producto.deleted_at.is_(None)
        )
        
        # Apply filters
        conditions = []
        
        # Filter by availability
        if disponible is not None:
            conditions.append(Producto.disponible == disponible)
        
        # Search by name (case-insensitive)
        if busqueda:
            search_pattern = f"%{busqueda}%"
            conditions.append(Producto.nombre.ilike(search_pattern))
        
        # Price range filters
        if precio_desde is not None:
            conditions.append(Producto.precio_base >= precio_desde)
        if precio_hasta is not None:
            conditions.append(Producto.precio_base <= precio_hasta)
        
        # Category filter (join through productos_categorias)
        if categoria_id is not None:
            # Subquery to find products in the category
            subquery = (
                select(ProductoCategoria.producto_id)
                .where(ProductoCategoria.categoria_id == categoria_id)
            )
            conditions.append(Producto.id.in_(subquery))
        
        # Allergen filter (NOT EXISTS logic)
        if allergen_ids:
            # Products that do NOT have any of the specified ingredients
            allergen_subquery = (
                select(ProductoIngrediente.producto_id)
                .where(ProductoIngrediente.ingrediente_id.in_(allergen_ids))
            )
            conditions.append(~Producto.id.in_(allergen_subquery))
        
        # Apply all conditions
        if conditions:
            query = query.where(and_(*conditions))
            count_query = count_query.where(and_(*conditions))
        
        # Get total count
        count_result = await self.session.execute(count_query)
        total = count_result.scalar() or 0
        
        # Apply ordering (default: created_at DESC for newest first)
        if order_by is not None:
            query = query.order_by(order_by)
        else:
            query = query.order_by(Producto.created_at.desc())
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        # Execute with eager loading of associations
        query = query.options(
            selectinload(Producto.categorias).selectinload(ProductoCategoria.categoria),
            selectinload(Producto.ingredientes).selectinload(ProductoIngrediente.ingrediente),
        )
        
        result = await self.session.execute(query)
        return result.scalars().all(), total
    
    async def find_by_nombre(self, nombre: str) -> Optional[Producto]:
        """
        Find an active product by exact name (case-sensitive).
        
        Args:
            nombre: Product name to search
            
        Returns:
            Producto or None if not found or soft-deleted
        """
        query = select(self.model).where(
            self.model.nombre == nombre,
            self.model.deleted_at.is_(None)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def update_stock_atomic(
        self,
        producto_id: int,
        new_stock: int
    ) -> Optional[Producto]:
        """
        Update stock quantity atomically using SELECT FOR UPDATE.
        
        This prevents race conditions when multiple concurrent requests
        try to update stock simultaneously.
        
        Args:
            producto_id: Product ID
            new_stock: New stock quantity (must be >= 0)
            
        Returns:
            Updated Producto or None if not found
            
        Raises:
            ValueError: If new_stock < 0
        """
        if new_stock < 0:
            raise ValueError("Stock cannot be negative")
        
        # Use SELECT FOR UPDATE to lock the row
        query = (
            select(Producto)
            .where(Producto.id == producto_id)
            .where(Producto.deleted_at.is_(None))
            .with_for_update()
        )
        result = await self.session.execute(query)
        producto = result.scalar_one_or_none()
        
        if not producto:
            return None
        
        producto.stock_cantidad = new_stock
        self.session.add(producto)
        await self.session.flush()
        await self.session.refresh(producto)
        
        self.logger.debug(f"Updated stock for producto_id={producto_id} to {new_stock}")
        return producto
    
    async def toggle_disponibilidad(
        self,
        producto_id: int,
        disponible: bool
    ) -> Optional[Producto]:
        """
        Toggle the disponibilidad flag of a product.
        
        Args:
            producto_id: Product ID
            disponible: New disponibilidad value
            
        Returns:
            Updated Producto or None if not found
        """
        producto = await self.find(producto_id)
        if not producto:
            return None
        
        producto.disponible = disponible
        self.session.add(producto)
        await self.session.flush()
        await self.session.refresh(producto)
        
        self.logger.debug(
            f"Toggled disponibilidad for producto_id={producto_id} to {disponible}"
        )
        return producto
    
    # --- Association methods: Categorías ---
    
    async def add_categoria(
        self,
        producto_id: int,
        categoria_id: int,
        es_principal: bool = False
    ) -> Optional[ProductoCategoria]:
        """
        Associate a product with a category.
        
        Args:
            producto_id: Product ID
            categoria_id: Category ID
            es_principal: Whether this is the main category
            
        Returns:
            Created ProductoCategoria association
            
        Raises:
            ValueError: If product or category not found
        """
        # Verify product exists
        producto = await self.find(producto_id)
        if not producto:
            raise ValueError(f"Producto with id {producto_id} not found")
        
        # Verify category exists (import here to avoid circular)
        from app.models.categoria import Categoria
        cat_query = select(Categoria).where(
            Categoria.id == categoria_id,
            Categoria.deleted_at.is_(None)
        )
        cat_result = await self.session.execute(cat_query)
        if not cat_result.scalar_one_or_none():
            raise ValueError(f"Categoria with id {categoria_id} not found")
        
        # Check if association already exists
        existing_query = select(ProductoCategoria).where(
            ProductoCategoria.producto_id == producto_id,
            ProductoCategoria.categoria_id == categoria_id
        )
        existing_result = await self.session.execute(existing_query)
        if existing_result.scalar_one_or_none():
            raise ValueError("Category already associated with product")
        
        # Create association
        association = ProductoCategoria(
            producto_id=producto_id,
            categoria_id=categoria_id,
            es_principal=es_principal
        )
        self.session.add(association)
        await self.session.flush()
        await self.session.refresh(association)
        
        self.logger.debug(
            f"Added categoria_id={categoria_id} to producto_id={producto_id}"
        )
        return association
    
    async def remove_categoria(
        self,
        producto_id: int,
        categoria_id: int
    ) -> bool:
        """
        Remove a category association from a product.
        
        Args:
            producto_id: Product ID
            categoria_id: Category ID
            
        Returns:
            True if association was deleted, False if not found
        """
        query = select(ProductoCategoria).where(
            ProductoCategoria.producto_id == producto_id,
            ProductoCategoria.categoria_id == categoria_id
        )
        result = await self.session.execute(query)
        association = result.scalar_one_or_none()
        
        if not association:
            return False
        
        await self.session.delete(association)
        await self.session.flush()
        
        self.logger.debug(
            f"Removed categoria_id={categoria_id} from producto_id={producto_id}"
        )
        return True
    
    async def set_principal_categoria(
        self,
        producto_id: int,
        categoria_id: int
    ) -> bool:
        """
        Set a category as the principal category for a product.
        
        Unsets es_principal on all other categories for this product.
        
        Args:
            producto_id: Product ID
            categoria_id: Category ID to set as principal
            
        Returns:
            True if successful, False if association not found
        """
        # Unset all principal flags for this product
        unset_query = select(ProductoCategoria).where(
            ProductoCategoria.producto_id == producto_id,
            ProductoCategoria.es_principal == True
        )
        unset_result = await self.session.execute(unset_query)
        for assoc in unset_result.scalars().all():
            assoc.es_principal = False
            self.session.add(assoc)
        
        # Set new principal
        set_query = select(ProductoCategoria).where(
            ProductoCategoria.producto_id == producto_id,
            ProductoCategoria.categoria_id == categoria_id
        )
        set_result = await self.session.execute(set_query)
        association = set_result.scalar_one_or_none()
        
        if not association:
            return False
        
        association.es_principal = True
        self.session.add(association)
        await self.session.flush()
        
        self.logger.debug(
            f"Set categoria_id={categoria_id} as principal for producto_id={producto_id}"
        )
        return True
    
    # --- Association methods: Ingredientes ---
    
    async def add_ingrediente(
        self,
        producto_id: int,
        ingrediente_id: int,
        es_removible: bool = True
    ) -> Optional[ProductoIngrediente]:
        """
        Associate a product with an ingredient.
        
        Args:
            producto_id: Product ID
            ingrediente_id: Ingredient ID
            es_removible: Whether the customer can remove this ingredient
            
        Returns:
            Created ProductoIngrediente association
            
        Raises:
            ValueError: If product or ingredient not found
        """
        # Verify product exists
        producto = await self.find(producto_id)
        if not producto:
            raise ValueError(f"Producto with id {producto_id} not found")
        
        # Verify ingredient exists
        from app.models.ingrediente import Ingrediente
        ing_query = select(Ingrediente).where(
            Ingrediente.id == ingrediente_id,
            Ingrediente.deleted_at.is_(None)
        )
        ing_result = await self.session.execute(ing_query)
        if not ing_result.scalar_one_or_none():
            raise ValueError(f"Ingrediente with id {ingrediente_id} not found")
        
        # Check if association already exists
        existing_query = select(ProductoIngrediente).where(
            ProductoIngrediente.producto_id == producto_id,
            ProductoIngrediente.ingrediente_id == ingrediente_id
        )
        existing_result = await self.session.execute(existing_query)
        if existing_result.scalar_one_or_none():
            raise ValueError("Ingredient already associated with product")
        
        # Create association
        association = ProductoIngrediente(
            producto_id=producto_id,
            ingrediente_id=ingrediente_id,
            es_removible=es_removible
        )
        self.session.add(association)
        await self.session.flush()
        await self.session.refresh(association)
        
        self.logger.debug(
            f"Added ingrediente_id={ingrediente_id} to producto_id={producto_id} "
            f"(es_removible={es_removible})"
        )
        return association
    
    async def remove_ingrediente(
        self,
        producto_id: int,
        ingrediente_id: int
    ) -> bool:
        """
        Remove an ingredient association from a product.
        
        Args:
            producto_id: Product ID
            ingrediente_id: Ingredient ID
            
        Returns:
            True if association was deleted, False if not found
        """
        query = select(ProductoIngrediente).where(
            ProductoIngrediente.producto_id == producto_id,
            ProductoIngrediente.ingrediente_id == ingrediente_id
        )
        result = await self.session.execute(query)
        association = result.scalar_one_or_none()
        
        if not association:
            return False
        
        await self.session.delete(association)
        await self.session.flush()
        
        self.logger.debug(
            f"Removed ingrediente_id={ingrediente_id} from producto_id={producto_id}"
        )
        return True
    
    async def list_ingredientes(self, producto_id: int) -> List[ProductoIngrediente]:
        """
        List all ingredients associated with a product.
        
        Args:
            producto_id: Product ID
            
        Returns:
            List of ProductoIngrediente associations with ingredient details
        """
        query = (
            select(ProductoIngrediente)
            .options(selectinload(ProductoIngrediente.ingrediente))
            .where(ProductoIngrediente.producto_id == producto_id)
            .order_by(ProductoIngrediente.id)
        )
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def list_categorias(self, producto_id: int) -> List[ProductoCategoria]:
        """
        List all categories associated with a product.
        
        Args:
            producto_id: Product ID
            
        Returns:
            List of ProductoCategoria associations with category details
        """
        query = (
            select(ProductoCategoria)
            .options(selectinload(ProductoCategoria.categoria))
            .where(ProductoCategoria.producto_id == producto_id)
            .order_by(ProductoCategoria.es_principal.desc(), ProductoCategoria.id)
        )
        result = await self.session.execute(query)
        return result.scalars().all()