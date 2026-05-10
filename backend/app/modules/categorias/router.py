"""FastAPI router for hierarchical category management (CRUD endpoints).

Implements 5 endpoints following REST conventions:
  - POST /api/v1/categorias — Create (requires ADMIN/STOCK)
  - GET /api/v1/categorias — List tree (public)
  - GET /api/v1/categorias/{id} — Get single (public)
  - PUT /api/v1/categorias/{id} — Update (requires ADMIN/STOCK)
  - DELETE /api/v1/categorias/{id} — Soft-delete (requires ADMIN)

All endpoints:
  - Use UnitOfWork dependency (get_uow) for database access
  - Return appropriate HTTP status codes (201, 200, 204, 404, 409, 422, 403)
  - Use role-based access control (require_role dependency)
  - Include OpenAPI documentation with docstrings and response models
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app.modules.categorias.schemas import (
    CategoriaCreate, CategoriaUpdate, CategoriaRead, CategoriaTreeNode
)
from app.modules.categorias.service import CategoriaService
from app.uow import UnitOfWork
from app.dependencies import get_uow, require_role
from app.exceptions import AppException, ValidationError

# Create router with prefix and tag for Swagger grouping
router = APIRouter(prefix="/api/v1/categorias", tags=["categorias"])


@router.post(
    "",
    response_model=CategoriaRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new category",
    responses={
        201: {"description": "Category created successfully"},
        400: {"description": "Invalid parent or self-reference detected"},
        404: {"description": "Parent category not found"},
        422: {"description": "Cycle detected or validation error"},
        403: {"description": "Insufficient permissions (ADMIN/STOCK required)"},
    },
)
async def create_categoria(
    data: CategoriaCreate,
    uow: UnitOfWork = Depends(get_uow),
    _: None = Depends(require_role(["ADMIN", "STOCK"])),
) -> CategoriaRead:
    """
    Create a new category (root or subcategory).
    
    **Requires**: ADMIN or STOCK role
    
    **Business Logic**:
    - Root categories have `parent_id = None`
    - Subcategories must have a valid parent_id
    - Self-reference prevention: cannot set `parent_id == id`
    - Cycle detection: recursive hierarchy limited to 20 levels
    
    **Parameters**:
    - `nombre` (required): Category name (max 100 chars)
    - `descripcion` (optional): Category description
    - `parent_id` (optional): Parent category ID (None for root)
    
    **Responses**:
    - 201: Category created (returns CategoriaRead)
    - 400: Self-reference or invalid parent
    - 404: Parent category not found
    - 422: Cycle detected
    - 403: Insufficient permissions
    """
    try:
        service = CategoriaService(uow)
        result = await service.create_categoria(data)
        return result
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "",
    response_model=List[CategoriaTreeNode],
    summary="Get all categories as nested tree",
    responses={
        200: {"description": "List of root categories with descendants"},
    },
)
async def get_categorias_tree(
    uow: UnitOfWork = Depends(get_uow),
) -> List[CategoriaTreeNode]:
    """
    Retrieve all categories organized as a nested tree.
    
    **Access**: Public (no authentication required)
    
    **Returns**: List of root categories with all descendants populated recursively.
    Automatically excludes soft-deleted categories.
    
    **Business Logic**:
    - Only root categories (parent_id IS NULL) appear at top level
    - Each category includes its children in `subcategorias` array
    - Soft-deleted categories (deleted_at IS NOT NULL) are excluded
    - Empty response if no categories exist
    
    **Response Format**:
    ```json
    [
      {
        "id": 1,
        "nombre": "Bebidas",
        "parent_id": null,
        "subcategorias": [
          {
            "id": 2,
            "nombre": "Alcohólicas",
            "parent_id": 1,
            "subcategorias": []
          }
        ]
      }
    ]
    ```
    """
    try:
        service = CategoriaService(uow)
        result = await service.get_tree()
        return result
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/{categoria_id}",
    response_model=CategoriaRead,
    summary="Get single category by ID",
    responses={
        200: {"description": "Category found"},
        404: {"description": "Category not found or is soft-deleted"},
    },
)
async def get_categoria(
    categoria_id: int,
    uow: UnitOfWork = Depends(get_uow),
) -> CategoriaRead:
    """
    Retrieve a single category by ID.
    
    **Access**: Public (no authentication required)
    
    **Parameters**:
    - `categoria_id`: Category ID (path parameter)
    
    **Returns**: Category details (CategoriaRead)
    
    **Business Logic**:
    - Soft-deleted categories return 404
    - Only active (non-deleted) categories are returned
    
    **Response Example**:
    ```json
    {
      "id": 1,
      "nombre": "Bebidas",
      "descripcion": "Bebidas variadas",
      "parent_id": null,
      "created_at": "2024-05-09T10:00:00Z",
      "updated_at": "2024-05-09T10:00:00Z",
      "deleted_at": null
    }
    ```
    """
    try:
        service = CategoriaService(uow)
        result = await service.get_categoria(categoria_id)
        return result
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put(
    "/{categoria_id}",
    response_model=CategoriaRead,
    summary="Update category",
    responses={
        200: {"description": "Category updated successfully"},
        400: {"description": "Self-reference or invalid parent"},
        404: {"description": "Category not found"},
        422: {"description": "Cycle detected"},
        403: {"description": "Insufficient permissions (ADMIN/STOCK required)"},
    },
)
async def update_categoria(
    categoria_id: int,
    data: CategoriaUpdate,
    uow: UnitOfWork = Depends(get_uow),
    _: None = Depends(require_role(["ADMIN", "STOCK"])),
) -> CategoriaRead:
    """
    Update an existing category.
    
    **Requires**: ADMIN or STOCK role
    
    **Parameters**:
    - `categoria_id`: Category ID to update (path parameter)
    - `nombre` (optional): New category name
    - `descripcion` (optional): New description
    - `parent_id` (optional): New parent category ID
    
    **Business Logic**:
    - Cannot set `parent_id` to self (self-reference prevention)
    - Cannot set `parent_id` to a descendant (cycle prevention)
    - Only provided fields are updated
    - All validation rules from create apply here
    
    **Responses**:
    - 200: Category updated (returns updated CategoriaRead)
    - 400: Self-reference detected
    - 404: Category not found
    - 422: Cycle detected or validation error
    - 403: Insufficient permissions
    """
    try:
        service = CategoriaService(uow)
        result = await service.update_categoria(categoria_id, data)
        return result
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete(
    "/{categoria_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete (soft-delete) a category",
    responses={
        204: {"description": "Category deleted successfully"},
        404: {"description": "Category not found"},
        409: {"description": "Category has children (cannot delete)"},
        403: {"description": "Insufficient permissions (ADMIN required)"},
    },
)
async def delete_categoria(
    categoria_id: int,
    uow: UnitOfWork = Depends(get_uow),
    _: None = Depends(require_role(["ADMIN"])),
) -> None:
    """
    Soft-delete a category (set deleted_at timestamp).
    
    **Requires**: ADMIN role (more restrictive than create/update)
    
    **Parameters**:
    - `categoria_id`: Category ID to delete (path parameter)
    
    **Business Logic**:
    - Soft-delete pattern: sets `deleted_at` timestamp instead of hard delete
    - Cannot delete if category has children (returns 409 Conflict)
    - Cannot delete if category has products (future validation)
    - Preserves audit trail and enables recovery
    
    **Responses**:
    - 204: Category deleted successfully (no response body)
    - 404: Category not found
    - 409: Category has children (cannot delete leaf categories only)
    - 403: Insufficient permissions (ADMIN only)
    
    **Note**: Returns 204 No Content on success (empty body per HTTP standard).
    """
    try:
        service = CategoriaService(uow)
        await service.delete_categoria(categoria_id)
        # 204 No Content — no return value
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except ValidationError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
