"""FastAPI router for producto management (CRUD endpoints).

Implements 10+ REST endpoints:
  - POST /api/v1/productos — Create (requires ADMIN/STOCK)
  - GET /api/v1/productos — List with filters, pagination (public)
  - GET /api/v1/productos/{id} — Get single (public)
  - PUT /api/v1/productos/{id} — Update (requires ADMIN/STOCK)
  - DELETE /api/v1/productos/{id} — Soft delete (requires ADMIN)
  - PATCH /api/v1/productos/{id}/stock — Update stock (requires ADMIN/STOCK)
  - PATCH /api/v1/productos/{id}/disponibilidad — Toggle availability (requires ADMIN/STOCK)
  - POST /api/v1/productos/{id}/categorias — Add category (requires ADMIN/STOCK)
  - DELETE /api/v1/productos/{id}/categorias/{cat_id} — Remove category (requires ADMIN/STOCK)
  - GET /api/v1/productos/{id}/ingredientes — List ingredients (public)
  - POST /api/v1/productos/{id}/ingredientes — Add ingredient (requires ADMIN)
  - DELETE /api/v1/productos/{id}/ingredientes/{ing_id} — Remove ingredient (requires ADMIN)

All endpoints:
  - Use UnitOfWork dependency (get_uow) for database access
  - Return appropriate HTTP status codes (201, 200, 204, 404, 409, 422, 403)
  - Use role-based access control (require_role dependency)
  - Include OpenAPI documentation with docstrings and response models
"""
from decimal import Decimal
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.modules.productos.schemas import (
    ProductoCreate,
    ProductoUpdate,
    ProductoRead,
    ProductoDetail,
    ProductoListResponse,
    StockUpdate,
    DisponibilidadUpdate,
    ProductoCategoriaCreate,
    ProductoCategoriaRead,
    ProductoIngredienteCreate,
    ProductoIngredienteRead,
)
from app.modules.productos.service import ProductoService
from app.uow import UnitOfWork
from app.dependencies import get_uow, require_role

# Create router with prefix and tag for Swagger grouping
router = APIRouter(prefix="/api/v1/productos", tags=["productos"])


# ============================================================================
# CRUD Endpoints
# ============================================================================

@router.post(
    "",
    response_model=ProductoRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new product",
    responses={
        201: {"description": "Product created successfully"},
        409: {"description": "Product with same name already exists"},
        422: {"description": "Validation error (negative price, etc.)"},
        403: {"description": "Insufficient permissions (ADMIN/STOCK required)"},
    },
)
async def create_producto(
    data: ProductoCreate,
    uow: UnitOfWork = Depends(get_uow),
    _: None = Depends(require_role(["ADMIN", "STOCK"])),
) -> ProductoRead:
    """
    Create a new product.
    
    **Requires**: ADMIN or STOCK role
    
    **Parameters**:
    - `nombre` (required): Product name (max 200 chars, unique among active)
    - `descripcion` (optional): Product description
    - `precio_base` (required): Base price (>= 0, max 2 decimal places)
    - `stock_cantidad` (optional): Initial stock (default: 0, >= 0)
    - `disponible` (optional): Availability flag (default: true)
    - `imagen` (optional): Image URL (max 500 chars)
    
    **Responses**:
    - 201: Product created (returns ProductoRead)
    - 409: Duplicate name
    - 422: Validation error
    - 403: Insufficient permissions
    """
    try:
        service = ProductoService(uow.session)
        result = await service.create_producto(data)
        await uow.commit()
        return result
    except ValueError as e:
        err_lower = str(e).lower()
        if "ya existe" in err_lower or "already exists" in err_lower:
            raise HTTPException(status_code=409, detail=str(e))
        raise HTTPException(status_code=422, detail=str(e))


@router.get(
    "",
    response_model=ProductoListResponse,
    status_code=status.HTTP_200_OK,
    summary="List products with filters and pagination",
    responses={
        200: {"description": "List of products returned"},
    },
    tags=["products"],
)
async def list_productos(
    skip: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(20, ge=1, le=100, description="Pagination limit"),
    categoria_id: Optional[int] = Query(None, description="Filter by category ID"),
    disponible: Optional[bool] = Query(None, description="Filter by availability"),
    busqueda: Optional[str] = Query(None, description="Search by name (case-insensitive)"),
    precio_desde: Optional[Decimal] = Query(None, ge=0, description="Minimum price"),
    precio_hasta: Optional[Decimal] = Query(None, ge=0, description="Maximum price"),
    excluirAlergenos: Optional[str] = Query(None, description="Exclude products with allergen IDs (comma-separated, e.g. 1,3,7)"),
    uow: UnitOfWork = Depends(get_uow),
) -> ProductoListResponse:
    """
    List all active products with optional filters and pagination.
    
    **Public endpoint** — no authentication required.
    
    **Query Parameters**:
    - `skip` (optional): Offset for pagination (default: 0)
    - `limit` (optional): Max items per page (default: 20, max: 100)
    - `categoria_id` (optional): Filter by category
    - `disponible` (optional): Filter by availability (true/false)
    - `busqueda` (optional): Search by name (case-insensitive, ILIKE)
    - `precio_desde` (optional): Minimum price filter
    - `precio_hasta` (optional): Maximum price filter
    - `excluirAlergenos` (optional): Exclude products with specific ingredient IDs (comma-separated)
    
    **Note**: Public endpoint hides stock_cantidad (per spec: "No revelar stock exacto")
    
    **Allergen Exclusion**:
    - Format: `excluirAlergenos=5` or `excluirAlergenos=1,3,7`
    - Products containing ANY of these ingredient IDs are excluded
    - Invalid IDs are silently ignored
    
    **Responses**:
    - 200: Returns ProductoListResponse with items, total, pagination
    """
    # Parse allergen IDs from comma-separated string
    allergen_ids = []
    if excluirAlergenos:
        try:
            allergen_ids = [int(id_str.strip()) for id_str in excluirAlergenos.split(",") if id_str.strip()]
        except ValueError:
            # Silently ignore invalid IDs
            allergen_ids = []
    
    try:
        service = ProductoService(uow.session)
        return await service.list_productos(
            skip=skip,
            limit=limit,
            categoria_id=categoria_id,
            disponible=disponible,
            busqueda=busqueda,
            precio_desde=precio_desde,
            precio_hasta=precio_hasta,
            allergen_ids=allergen_ids,
            include_stock=False,  # Public endpoint hides stock
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{producto_id}",
    response_model=ProductoDetail,
    status_code=status.HTTP_200_OK,
    summary="Get a single product by ID",
    responses={
        200: {"description": "Product found"},
        404: {"description": "Product not found or soft-deleted"},
    },
    tags=["products"],
)
async def get_producto(
    producto_id: int,
    uow: UnitOfWork = Depends(get_uow),
) -> ProductoDetail:
    """
    Get a single active product by ID.
    
    **Public endpoint** — no authentication required.
    Shows stock_cantidad for transparency.
    
    **Path Parameters**:
    - `producto_id`: Product ID
    
    **Responses**:
    - 200: Product found (returns ProductoDetail with categories & ingredients)
    - 404: Product not found or soft-deleted
    """
    try:
        service = ProductoService(uow.session)
        return await service.get_producto_by_id(producto_id, include_stock=True)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put(
    "/{producto_id}",
    response_model=ProductoRead,
    status_code=status.HTTP_200_OK,
    summary="Update a product",
    responses={
        200: {"description": "Product updated successfully"},
        404: {"description": "Product not found or soft-deleted"},
        409: {"description": "New name already exists"},
        422: {"description": "Validation error"},
        403: {"description": "Insufficient permissions (ADMIN/STOCK required)"},
    },
)
async def update_producto(
    producto_id: int,
    data: ProductoUpdate,
    uow: UnitOfWork = Depends(get_uow),
    _: None = Depends(require_role(["ADMIN", "STOCK"])),
) -> ProductoRead:
    """
    Update an active product (ADMIN/STOCK only).
    
    **Requires**: ADMIN or STOCK role
    
    **Path Parameters**:
    - `producto_id`: Product ID
    
    **Request Body** (all fields optional):
    - `nombre`: New product name
    - `descripcion`: New description
    - `precio_base`: New base price (>= 0)
    - `disponible`: New availability flag
    - `imagen`: New image URL
    
    **Responses**:
    - 200: Product updated (returns ProductoRead)
    - 404: Product not found or soft-deleted
    - 409: Duplicate name
    - 422: Validation error
    - 403: Insufficient permissions
    """
    try:
        service = ProductoService(uow.session)
        result = await service.update_producto(producto_id, data)
        await uow.commit()
        return result
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        if "already exists" in str(e).lower():
            raise HTTPException(status_code=409, detail=str(e))
        raise HTTPException(status_code=422, detail=str(e))


@router.delete(
    "/{producto_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Soft delete a product",
    responses={
        204: {"description": "Product soft-deleted successfully"},
        404: {"description": "Product not found or already deleted"},
        403: {"description": "Insufficient permissions (ADMIN required)"},
    },
)
async def delete_producto(
    producto_id: int,
    uow: UnitOfWork = Depends(get_uow),
    _: None = Depends(require_role(["ADMIN"])),
) -> None:
    """
    Soft delete a product (ADMIN only).
    
    **Requires**: ADMIN role
    
    **Business Logic**:
    - Sets `deleted_at` timestamp instead of physical deletion
    - Product no longer appears in list queries
    - Historical associations with categories/ingredients preserved
    
    **Path Parameters**:
    - `producto_id`: Product ID
    
    **Responses**:
    - 204: Product soft-deleted (no response body)
    - 404: Product not found or already deleted
    - 403: Insufficient permissions
    """
    try:
        service = ProductoService(uow.session)
        await service.delete_producto(producto_id)
        await uow.commit()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ============================================================================
# Stock Management Endpoints
# ============================================================================

@router.patch(
    "/{producto_id}/stock",
    response_model=ProductoDetail,
    status_code=status.HTTP_200_OK,
    summary="Update product stock",
    responses={
        200: {"description": "Stock updated successfully"},
        404: {"description": "Product not found"},
        422: {"description": "Stock cannot be negative"},
        403: {"description": "Insufficient permissions (ADMIN/STOCK required)"},
    },
)
async def update_stock(
    producto_id: int,
    data: StockUpdate,
    uow: UnitOfWork = Depends(get_uow),
    _: None = Depends(require_role(["ADMIN", "STOCK"])),
) -> ProductoDetail:
    """
    Update product stock atomically (ADMIN/STOCK only).
    
    **Requires**: ADMIN or STOCK role
    
    **Business Logic**:
    - Uses SELECT FOR UPDATE to prevent race conditions
    - Stock cannot be negative (returns 422 if attempted)
    
    **Path Parameters**:
    - `producto_id`: Product ID
    
    **Request Body**:
    - `stock_cantidad` (required): New stock quantity (>= 0)
    
    **Responses**:
    - 200: Stock updated (returns ProductoDetail)
    - 404: Product not found
    - 422: Stock < 0
    - 403: Insufficient permissions
    """
    try:
        service = ProductoService(uow.session)
        result = await service.update_stock(producto_id, data)
        await uow.commit()
        return result
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        if "negative" in str(e).lower():
            raise HTTPException(status_code=422, detail=str(e))
        raise HTTPException(status_code=422, detail=str(e))


@router.patch(
    "/{producto_id}/disponibilidad",
    response_model=ProductoDetail,
    status_code=status.HTTP_200_OK,
    summary="Toggle product availability",
    responses={
        200: {"description": "Availability toggled successfully"},
        404: {"description": "Product not found"},
        403: {"description": "Insufficient permissions (ADMIN/STOCK required)"},
    },
)
async def toggle_disponibilidad(
    producto_id: int,
    data: DisponibilidadUpdate,
    uow: UnitOfWork = Depends(get_uow),
    _: None = Depends(require_role(["ADMIN", "STOCK"])),
) -> ProductoDetail:
    """
    Toggle product availability (ADMIN/STOCK only).
    
    **Requires**: ADMIN or STOCK role
    
    **Note**: `disponible` is independent of `stock_cantidad`:
    - A product can be disponible=true but stock=0 (out of stock but visible)
    - A product can be disponible=false but stock>0 (hidden from catalog)
    
    **Path Parameters**:
    - `producto_id`: Product ID
    
    **Request Body**:
    - `disponible` (required): New availability value (true/false)
    
    **Responses**:
    - 200: Availability toggled (returns ProductoDetail)
    - 404: Product not found
    - 403: Insufficient permissions
    """
    try:
        service = ProductoService(uow.session)
        result = await service.toggle_disponibilidad(producto_id, data)
        await uow.commit()
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ============================================================================
# Category Association Endpoints
# ============================================================================

@router.post(
    "/{producto_id}/categorias",
    response_model=ProductoCategoriaRead,
    status_code=status.HTTP_201_CREATED,
    summary="Add a category to a product",
    responses={
        201: {"description": "Category associated successfully"},
        404: {"description": "Product or category not found"},
        409: {"description": "Category already associated"},
        403: {"description": "Insufficient permissions (ADMIN/STOCK required)"},
    },
)
async def add_categoria(
    producto_id: int,
    data: ProductoCategoriaCreate,
    uow: UnitOfWork = Depends(get_uow),
    _: None = Depends(require_role(["ADMIN", "STOCK"])),
) -> ProductoCategoriaRead:
    """
    Associate a category with a product (ADMIN/STOCK only).
    
    **Requires**: ADMIN or STOCK role
    
    **Path Parameters**:
    - `producto_id`: Product ID
    
    **Request Body**:
    - `categoria_id` (required): Category ID to associate
    - `es_principal` (optional): Set as main category (default: false)
    
    **Responses**:
    - 201: Association created (returns ProductoCategoriaRead)
    - 404: Product or category not found
    - 409: Category already associated
    - 403: Insufficient permissions
    """
    try:
        service = ProductoService(uow.session)
        result = await service.add_categoria(producto_id, data)
        await uow.commit()
        return result
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        if "already" in str(e).lower():
            raise HTTPException(status_code=409, detail=str(e))
        raise HTTPException(status_code=422, detail=str(e))


@router.delete(
    "/{producto_id}/categorias/{categoria_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove a category from a product",
    responses={
        204: {"description": "Category disassociated successfully"},
        404: {"description": "Association not found"},
        403: {"description": "Insufficient permissions (ADMIN/STOCK required)"},
    },
)
async def remove_categoria(
    producto_id: int,
    categoria_id: int,
    uow: UnitOfWork = Depends(get_uow),
    _: None = Depends(require_role(["ADMIN", "STOCK"])),
) -> None:
    """
    Remove a category association from a product (ADMIN/STOCK only).
    
    **Requires**: ADMIN or STOCK role
    
    **Path Parameters**:
    - `producto_id`: Product ID
    - `categoria_id`: Category ID to remove
    
    **Responses**:
    - 204: Association removed (no response body)
    - 404: Association not found
    - 403: Insufficient permissions
    """
    try:
        service = ProductoService(uow.session)
        await service.remove_categoria(producto_id, categoria_id)
        await uow.commit()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ============================================================================
# Ingredient Association Endpoints
# ============================================================================

@router.get(
    "/{producto_id}/ingredientes",
    response_model=List[ProductoIngredienteRead],
    status_code=status.HTTP_200_OK,
    summary="List ingredients for a product",
    responses={
        200: {"description": "List of ingredients returned"},
    },
)
async def list_ingredientes(
    producto_id: int,
    uow: UnitOfWork = Depends(get_uow),
) -> List[ProductoIngredienteRead]:
    """
    List all ingredients associated with a product.
    
    **Public endpoint** — no authentication required.
    Useful for displaying allergen information in the catalog.
    
    **Path Parameters**:
    - `producto_id`: Product ID
    
    **Responses**:
    - 200: List of ProductoIngredienteRead with ingredient details
    """
    try:
        service = ProductoService(uow.session)
        return await service.list_ingredientes(producto_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/{producto_id}/ingredientes",
    response_model=ProductoIngredienteRead,
    status_code=status.HTTP_201_CREATED,
    summary="Add an ingredient to a product",
    responses={
        201: {"description": "Ingredient associated successfully"},
        404: {"description": "Product or ingredient not found"},
        409: {"description": "Ingredient already associated"},
        403: {"description": "Insufficient permissions (ADMIN required)"},
    },
)
async def add_ingrediente(
    producto_id: int,
    data: ProductoIngredienteCreate,
    uow: UnitOfWork = Depends(get_uow),
    _: None = Depends(require_role(["ADMIN", "STOCK"])),
) -> ProductoIngredienteRead:
    """
    Associate an ingredient with a product (ADMIN/STOCK only).
    
    **Requires**: ADMIN or STOCK role
    
    **Path Parameters**:
    - `producto_id`: Product ID
    
    **Request Body**:
    - `ingrediente_id` (required): Ingredient ID to associate
    - `es_removible` (optional): Can customer remove from order? (default: true)
    
    **Responses**:
    - 201: Association created (returns ProductoIngredienteRead)
    - 404: Product or ingredient not found
    - 409: Ingredient already associated
    - 403: Insufficient permissions
    """
    try:
        service = ProductoService(uow.session)
        result = await service.add_ingrediente(producto_id, data)
        await uow.commit()
        return result
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        if "already" in str(e).lower():
            raise HTTPException(status_code=409, detail=str(e))
        raise HTTPException(status_code=422, detail=str(e))


@router.delete(
    "/{producto_id}/ingredientes/{ingrediente_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove an ingredient from a product",
    responses={
        204: {"description": "Ingredient disassociated successfully"},
        404: {"description": "Association not found"},
        403: {"description": "Insufficient permissions (ADMIN/STOCK required)"},
    },
)
async def remove_ingrediente(
    producto_id: int,
    ingrediente_id: int,
    uow: UnitOfWork = Depends(get_uow),
    _: None = Depends(require_role(["ADMIN", "STOCK"])),
) -> None:
    """
    Remove an ingredient association from a product (ADMIN/STOCK only).
    
    **Requires**: ADMIN or STOCK role
    
    **Path Parameters**:
    - `producto_id`: Product ID
    - `ingrediente_id`: Ingredient ID to remove
    
    **Responses**:
    - 204: Association removed (no response body)
    - 404: Association not found
    - 403: Insufficient permissions
    """
    try:
        service = ProductoService(uow.session)
        await service.remove_ingrediente(producto_id, ingrediente_id)
        await uow.commit()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))