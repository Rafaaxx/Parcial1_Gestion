"""Business logic service for Producto management"""

import logging
from decimal import Decimal
from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.producto import Producto, ProductoCategoria, ProductoIngrediente
from app.modules.productos.schemas import (
    CategoriaBasica,
    DisponibilidadUpdate,
    IngredienteBasico,
    ProductoCategoriaCreate,
    ProductoCategoriaRead,
    ProductoCreate,
    ProductoDetail,
    ProductoIngredienteCreate,
    ProductoIngredienteRead,
    ProductoListItem,
    ProductoListResponse,
    ProductoRead,
    ProductoUpdate,
    StockUpdate,
)
from app.repositories.producto_repository import ProductoRepository

logger = logging.getLogger(__name__)


class ProductoService:
    """
    Service for product business logic.

    Validates business rules:
    - Product name uniqueness (case-sensitive, active only)
    - Stock cannot be negative
    - Price precision (max 2 decimal places)
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = ProductoRepository(session)

    # --- CRUD Operations ---

    async def create_producto(self, data: ProductoCreate) -> ProductoRead:
        """
        Create a new product after validating uniqueness.

        Args:
            data: ProductoCreate schema with validated fields

        Returns:
            ProductoRead with created product

        Raises:
            ValueError: If product name already exists
        """
        # Check name uniqueness (case-sensitive)
        existing = await self.repository.find_by_nombre(data.nombre)
        if existing:
            raise ValueError(f"Ya existe un producto con el nombre '{data.nombre}'")

        # Create product
        producto = Producto(
            nombre=data.nombre,
            descripcion=data.descripcion,
            precio_base=round(data.precio_base, 2),
            stock_cantidad=data.stock_cantidad,
            disponible=data.disponible,
            imagen=data.imagen,
        )

        self.session.add(producto)
        await self.session.flush()
        await self.session.refresh(producto)

        # Associate category if provided
        if data.categoria_id:
            try:
                await self.repository.add_categoria(producto.id, data.categoria_id, True)
            except ValueError:
                # Category doesn't exist, ignore
                pass

        logger.info(f"Created producto id={producto.id} nombre='{producto.nombre}'")
        return ProductoRead.model_validate(producto)

    async def get_producto_by_id(
        self, producto_id: int, include_stock: bool = False
    ) -> ProductoDetail:
        """
        Get product detail by ID.

        Args:
            producto_id: Product ID
            include_stock: If True, includes stock_cantidad in response.
                           If False (public), hides stock (per spec).

        Returns:
            ProductoDetail with full info

        Raises:
            ValueError: If product not found or soft-deleted
        """
        producto = await self.repository.find_with_associations(producto_id)
        if not producto:
            raise ValueError(f"Producto with id {producto_id} not found")

        return self._build_producto_detail(producto, include_stock=include_stock)

    async def list_productos(
        self,
        skip: int = 0,
        limit: int = 20,
        categoria_id: Optional[int] = None,
        disponible: Optional[bool] = None,
        busqueda: Optional[str] = None,
        precio_desde: Optional[Decimal] = None,
        precio_hasta: Optional[Decimal] = None,
        allergen_ids: Optional[List[int]] = None,
        include_stock: bool = False,
    ) -> ProductoListResponse:
        """
        List products with filtering and pagination.

        Args:
            skip: Pagination offset
            limit: Max results per page
            categoria_id: Filter by category
            disponible: Filter by availability
            busqueda: Search by name (case-insensitive)
            precio_desde: Minimum price
            precio_hasta: Maximum price
            allergen_ids: List of ingredient IDs to exclude (allergens)
            include_stock: If True, includes stock_cantidad in response

        Returns:
            ProductoListResponse with items and pagination metadata
        """
        productos, total = await self.repository.list_with_filters(
            skip=skip,
            limit=limit,
            categoria_id=categoria_id,
            disponible=disponible,
            busqueda=busqueda,
            precio_desde=precio_desde,
            precio_hasta=precio_hasta,
            allergen_ids=allergen_ids or [],
        )

        items = [self._build_producto_list_item(p, include_stock=include_stock) for p in productos]

        return ProductoListResponse(
            items=items,
            total=total,
            skip=skip,
            limit=limit,
        )

    async def update_producto(self, producto_id: int, data: ProductoUpdate) -> ProductoRead:
        """
        Update an existing product.

        Args:
            producto_id: Product ID
            data: ProductoUpdate schema with fields to update

        Returns:
            ProductoRead with updated product

        Raises:
            ValueError: If product not found, soft-deleted, or name conflicts
        """
        producto = await self.repository.find(producto_id)
        if not producto:
            raise ValueError(f"Producto with id {producto_id} not found")

        # If name is being updated, check uniqueness
        update_data = data.model_dump(exclude_unset=True)
        
        # Handle categoria_id separately (can be set to null to clear, or to a specific category)
        categoria_id = update_data.pop("categoria_id", None)
        
        if "nombre" in update_data and update_data["nombre"]:
            new_name = update_data["nombre"]
            if new_name != producto.nombre:
                existing = await self.repository.find_by_nombre(new_name)
                if existing and existing.id != producto_id:
                    raise ValueError(f"Ya existe un producto con el nombre '{new_name}'")

        # Apply updates
        if "precio_base" in update_data and update_data["precio_base"] is not None:
            update_data["precio_base"] = round(update_data["precio_base"], 2)

        for key, value in update_data.items():
            if value is not None and hasattr(producto, key):
                setattr(producto, key, value)

        self.session.add(producto)
        await self.session.flush()
        await self.session.refresh(producto)

        # Handle category association
        if categoria_id is not None:
            if categoria_id > 0:
                # Set as principal category
                try:
                    await self.repository.add_categoria(producto_id, categoria_id, True)
                except ValueError:
                    # Category doesn't exist, ignore
                    pass

        logger.info(f"Updated producto id={producto_id}")
        return ProductoRead.model_validate(producto)

    async def delete_producto(self, producto_id: int) -> None:
        """
        Soft delete a product.

        Args:
            producto_id: Product ID

        Raises:
            ValueError: If product not found or already deleted
        """
        producto = await self.repository.soft_delete(producto_id)
        if not producto:
            raise ValueError(f"Producto with id {producto_id} not found")

        logger.info(f"Soft deleted producto id={producto_id}")

    # --- Stock Management ---

    async def update_stock(self, producto_id: int, data: StockUpdate) -> ProductoDetail:
        """
        Update product stock atomically.

        Args:
            producto_id: Product ID
            data: StockUpdate with new stock value (must be >= 0)

        Returns:
            ProductoDetail with updated stock

        Raises:
            ValueError: If product not found or stock < 0
        """
        if data.stock_cantidad < 0:
            raise ValueError("El stock no puede ser negativo")

        producto = await self.repository.update_stock_atomic(producto_id, data.stock_cantidad)
        if not producto:
            raise ValueError(f"Producto with id {producto_id} not found")

        # Reload with associations for response
        producto = await self.repository.find_with_associations(producto_id)

        logger.info(f"Updated stock for producto id={producto_id} to {data.stock_cantidad}")
        return self._build_producto_detail(producto, include_stock=True)

    async def toggle_disponibilidad(
        self, producto_id: int, data: DisponibilidadUpdate
    ) -> ProductoDetail:
        """
        Toggle product availability.

        Args:
            producto_id: Product ID
            data: DisponibilidadUpdate with new disponible value

        Returns:
            ProductoDetail with updated availability
        """
        producto = await self.repository.toggle_disponibilidad(producto_id, data.disponible)
        if not producto:
            raise ValueError(f"Producto with id {producto_id} not found")

        # Reload with associations for response
        producto = await self.repository.find_with_associations(producto_id)

        logger.info(f"Toggled disponibilidad for producto id={producto_id} to {data.disponible}")
        return self._build_producto_detail(producto, include_stock=True)

    # --- Category Associations ---

    async def add_categoria(
        self, producto_id: int, data: ProductoCategoriaCreate
    ) -> ProductoCategoriaRead:
        """
        Associate a product with a category.

        Args:
            producto_id: Product ID
            data: ProductoCategoriaCreate with category info

        Returns:
            ProductoCategoriaRead with created association

        Raises:
            ValueError: If product/category not found, or already associated
        """
        try:
            association = await self.repository.add_categoria(
                producto_id, data.categoria_id, data.es_principal
            )
            # Build response without requiring nested categoria (avoid extra query)
            return ProductoCategoriaRead(
                id=association.id,
                categoria_id=association.categoria_id,
                es_principal=association.es_principal,
                categoria=None,  # Optional, avoids extra DB query for simple association
            )
        except ValueError as e:
            raise

    async def remove_categoria(self, producto_id: int, categoria_id: int) -> None:
        """
        Remove a category association from a product.

        Args:
            producto_id: Product ID
            categoria_id: Category ID to remove

        Raises:
            ValueError: If association not found
        """
        deleted = await self.repository.remove_categoria(producto_id, categoria_id)
        if not deleted:
            raise ValueError(
                f"Asociación entre producto {producto_id} y categoría {categoria_id} no encontrada"
            )

        logger.info(f"Removed categoria_id={categoria_id} from producto_id={producto_id}")

    # --- Ingredient Associations ---

    async def add_ingrediente(
        self, producto_id: int, data: ProductoIngredienteCreate
    ) -> ProductoIngredienteRead:
        """
        Associate a product with an ingredient.

        Args:
            producto_id: Product ID
            data: ProductoIngredienteCreate with ingredient info

        Returns:
            ProductoIngredienteRead with created association

        Raises:
            ValueError: If product/ingredient not found, or already associated
        """
        try:
            association = await self.repository.add_ingrediente(
                producto_id, data.ingrediente_id, data.es_removible
            )

            # Load ingredient details for response
            from app.models.ingrediente import Ingrediente

            ing_query = select(Ingrediente).where(Ingrediente.id == data.ingrediente_id)
            ing_result = await self.session.execute(ing_query)
            ingrediente = ing_result.scalar_one()

            return ProductoIngredienteRead(
                id=association.id,
                ingrediente_id=association.ingrediente_id,
                es_removible=association.es_removible,
                ingrediente=IngredienteBasico(
                    id=ingrediente.id,
                    nombre=ingrediente.nombre,
                    es_alergeno=ingrediente.es_alergeno,
                ),
            )
        except ValueError:
            raise

    async def remove_ingrediente(self, producto_id: int, ingrediente_id: int) -> None:
        """
        Remove an ingredient association from a product.

        Args:
            producto_id: Product ID
            ingrediente_id: Ingredient ID to remove

        Raises:
            ValueError: If association not found
        """
        deleted = await self.repository.remove_ingrediente(producto_id, ingrediente_id)
        if not deleted:
            raise ValueError(
                f"Asociación entre producto {producto_id} e ingrediente {ingrediente_id} no encontrada"
            )

        logger.info(f"Removed ingrediente_id={ingrediente_id} from producto_id={producto_id}")

    async def list_ingredientes(self, producto_id: int) -> List[ProductoIngredienteRead]:
        """
        List all ingredients for a product.

        Args:
            producto_id: Product ID

        Returns:
            List of ProductoIngredienteRead with ingredient details
        """
        associations = await self.repository.list_ingredientes(producto_id)
        return [
            ProductoIngredienteRead(
                id=a.id,
                ingrediente_id=a.ingrediente_id,
                es_removible=a.es_removible,
                ingrediente=(
                    IngredienteBasico(
                        id=a.ingrediente.id,
                        nombre=a.ingrediente.nombre,
                        es_alergeno=a.ingrediente.es_alergeno,
                    )
                    if a.ingrediente
                    else None
                ),
            )
            for a in associations
        ]

    # --- Helper methods ---

    def _build_producto_detail(
        self, producto: Producto, include_stock: bool = True
    ) -> ProductoDetail:
        """Build ProductoDetail from Producto entity"""
        return ProductoDetail(
            id=producto.id,
            nombre=producto.nombre,
            descripcion=producto.descripcion,
            precio_base=producto.precio_base,
            disponible=producto.disponible,
            stock_cantidad=producto.stock_cantidad if include_stock else 0,
            imagen=producto.imagen,
            created_at=producto.created_at,
            updated_at=producto.updated_at,
            categorias=[
                ProductoCategoriaRead(
                    id=pc.id,
                    categoria_id=pc.categoria_id,
                    es_principal=pc.es_principal,
                    categoria=(
                        CategoriaBasica(id=pc.categoria.id, nombre=pc.categoria.nombre)
                        if pc.categoria
                        else None
                    ),
                )
                for pc in producto.categorias
            ],
            ingredientes=[
                ProductoIngredienteRead(
                    id=pi.id,
                    ingrediente_id=pi.ingrediente_id,
                    es_removible=pi.es_removible,
                    ingrediente=(
                        IngredienteBasico(
                            id=pi.ingrediente.id,
                            nombre=pi.ingrediente.nombre,
                            es_alergeno=pi.ingrediente.es_alergeno,
                        )
                        if pi.ingrediente
                        else None
                    ),
                )
                for pi in producto.ingredientes
            ],
        )

    def _build_producto_list_item(
        self, producto: Producto, include_stock: bool = False
    ) -> ProductoListItem:
        """Build ProductoListItem from Producto entity"""
        # Get categories (only if already loaded via eager loading)
        categorias = []
        try:
            if producto.categorias:
                categorias = [
                    CategoriaBasica(
                        id=pc.categoria_id if hasattr(pc, "categoria_id") else pc.id,
                        nombre=pc.categoria.nombre if pc.categoria else "",
                    )
                    for pc in producto.categorias
                    if pc.categoria
                ]
        except Exception:
            # Relationships not loaded (lazy load would fail in sync context)
            pass

        # Get ingredients (only if already loaded via eager loading)
        ingredientes = []
        try:
            if producto.ingredientes:
                ingredientes = [
                    IngredienteBasico(
                        id=(pi.ingrediente_id if hasattr(pi, "ingrediente_id") else pi.id),
                        nombre=pi.ingrediente.nombre if pi.ingrediente else "",
                        es_alergeno=(pi.ingrediente.es_alergeno if pi.ingrediente else False),
                    )
                    for pi in producto.ingredientes
                    if pi.ingrediente
                ]
        except Exception:
            # Relationships not loaded (lazy load would fail in sync context)
            pass

        return ProductoListItem(
            id=producto.id,
            nombre=producto.nombre,
            descripcion=producto.descripcion,
            precio_base=producto.precio_base,
            stock_cantidad=producto.stock_cantidad if include_stock else None,
            disponible=producto.disponible,
            imagen=producto.imagen,
            categorias=categorias,
            ingredientes=ingredientes,
        )
