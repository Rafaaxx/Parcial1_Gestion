"""FastAPI router for ingredient management (CRUD endpoints).

Implements 5 REST endpoints for ingredient operations:
  - POST /api/v1/ingredientes — Create (requires STOCK/ADMIN)
  - GET /api/v1/ingredientes — List with pagination (public)
  - GET /api/v1/ingredientes/{id} — Get single (public)
  - PUT /api/v1/ingredientes/{id} — Update (requires STOCK/ADMIN)
  - DELETE /api/v1/ingredientes/{id} — Soft-delete (requires STOCK/ADMIN)

All endpoints use soft-delete pattern and return RFC 7807 error responses.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional

from app.modules.ingredientes.schemas import (
    IngredienteCreate,
    IngredienteUpdate,
    IngredienteRead,
    IngredienteListResponse,
)
from app.modules.ingredientes.service import IngredienteService
from app.uow import UnitOfWork
from app.dependencies import get_uow, require_role

# Create router with prefix and tag for Swagger grouping
router = APIRouter(prefix="/api/v1/ingredientes", tags=["ingredientes"])


@router.post(
    "",
    response_model=IngredienteRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new ingredient",
    responses={
        201: {"description": "Ingredient created successfully"},
        409: {"description": "Ingredient with same nombre already exists"},
        422: {"description": "Validation error (empty nombre, etc.)"},
        403: {"description": "Insufficient permissions (STOCK/ADMIN required)"},
    },
)
async def create_ingrediente(
    data: IngredienteCreate,
    uow: UnitOfWork = Depends(get_uow),
    _: None = Depends(require_role(["STOCK", "ADMIN"])),
) -> IngredienteRead:
    """
    Create a new ingredient.
    
    **Requires**: STOCK or ADMIN role
    
    **Parameters**:
    - `nombre` (required): Ingredient name (max 255 chars, unique among active ingredients)
    - `es_alergeno` (optional): Boolean flag indicating allergen status (default: false)
    
    **Responses**:
    - 201: Ingredient created (returns IngredienteRead)
    - 409: Duplicate nombre
    - 422: Validation error
    - 403: Insufficient permissions
    """
    try:
        service = IngredienteService(uow.session)
        result = await service.create_ingrediente(data)
        await service.commit()
        return result
    except ValueError as e:
        if "already exists" in str(e):
            raise HTTPException(status_code=409, detail=str(e))
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "",
    response_model=IngredienteListResponse,
    status_code=status.HTTP_200_OK,
    summary="List all active ingredients with optional filters",
    responses={
        200: {"description": "List of ingredients returned"},
    },
)
async def list_ingredientes(
    skip: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(100, ge=1, le=1000, description="Pagination limit"),
    es_alergeno: Optional[bool] = Query(None, description="Filter by allergen status (optional)"),
    uow: UnitOfWork = Depends(get_uow),
) -> IngredienteListResponse:
    """
    List all active ingredients with pagination and optional allergen filter.
    
    **No authentication required** — allergen information is public metadata.
    
    **Query Parameters**:
    - `skip` (optional): Offset for pagination (default: 0)
    - `limit` (optional): Max items per page (default: 100, max: 1000)
    - `es_alergeno` (optional): Filter by allergen flag (true/false/null)
    
    **Responses**:
    - 200: Returns IngredienteListResponse with items and total count
    """
    try:
        service = IngredienteService(uow.session)
        return await service.list_ingredientes(
            skip=skip,
            limit=limit,
            es_alergeno=es_alergeno,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/{id}",
    response_model=IngredienteRead,
    status_code=status.HTTP_200_OK,
    summary="Get a single ingredient by ID",
    responses={
        200: {"description": "Ingredient found"},
        404: {"description": "Ingredient not found or soft-deleted"},
    },
)
async def get_ingrediente(
    id: int,
    uow: UnitOfWork = Depends(get_uow),
) -> IngredienteRead:
    """
    Get a single active ingredient by ID.
    
    **No authentication required** — allergen information is public metadata.
    
    **Path Parameters**:
    - `id`: Ingredient ID
    
    **Responses**:
    - 200: Ingredient found (returns IngredienteRead)
    - 404: Ingredient not found or soft-deleted
    """
    try:
        service = IngredienteService(uow.session)
        return await service.get_ingrediente_by_id(id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put(
    "/{id}",
    response_model=IngredienteRead,
    status_code=status.HTTP_200_OK,
    summary="Update an ingredient",
    responses={
        200: {"description": "Ingredient updated successfully"},
        404: {"description": "Ingredient not found or soft-deleted"},
        409: {"description": "New nombre already exists"},
        422: {"description": "Validation error"},
        403: {"description": "Insufficient permissions (STOCK/ADMIN required)"},
    },
)
async def update_ingrediente(
    id: int,
    data: IngredienteUpdate,
    uow: UnitOfWork = Depends(get_uow),
    _: None = Depends(require_role(["STOCK", "ADMIN"])),
) -> IngredienteRead:
    """
    Update an active ingredient (STOCK/ADMIN only).
    
    **Requires**: STOCK or ADMIN role
    
    **Path Parameters**:
    - `id`: Ingredient ID
    
    **Request Body** (all fields optional):
    - `nombre` (optional): New ingredient name
    - `es_alergeno` (optional): New allergen flag
    
    **Responses**:
    - 200: Ingredient updated (returns IngredienteRead)
    - 404: Ingredient not found or soft-deleted
    - 409: Duplicate nombre
    - 422: Validation error
    - 403: Insufficient permissions
    """
    try:
        service = IngredienteService(uow.session)
        result = await service.update_ingrediente(id, data)
        await service.commit()
        return result
    except ValueError as e:
        if "already exists" in str(e):
            raise HTTPException(status_code=409, detail=str(e))
        elif "not found" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Soft delete an ingredient",
    responses={
        204: {"description": "Ingredient soft-deleted successfully"},
        404: {"description": "Ingredient not found or already deleted"},
        403: {"description": "Insufficient permissions (STOCK/ADMIN required)"},
    },
)
async def delete_ingrediente(
    id: int,
    uow: UnitOfWork = Depends(get_uow),
    _: None = Depends(require_role(["STOCK", "ADMIN"])),
) -> None:
    """
    Soft delete an ingredient (STOCK/ADMIN only).
    
    **Requires**: STOCK or ADMIN role
    
    **Business Logic**:
    - Sets `deleted_at` timestamp instead of physical deletion
    - Ingredient no longer appears in list queries
    - Historical product-ingredient associations are preserved
    
    **Path Parameters**:
    - `id`: Ingredient ID
    
    **Responses**:
    - 204: Ingredient soft-deleted (no response body)
    - 404: Ingredient not found or already deleted
    - 403: Insufficient permissions
    """
    try:
        service = IngredienteService(uow.session)
        await service.delete_ingrediente(id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
