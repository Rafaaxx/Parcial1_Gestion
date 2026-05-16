"""FastAPI router for delivery address management (CRUD + default address endpoints).

Implements 5 endpoints following REST conventions:
  - POST /api/v1/direcciones — Create address (requires CLIENT/ADMIN)
  - GET /api/v1/direcciones — List own addresses (requires CLIENT/ADMIN)
  - PUT /api/v1/direcciones/{id} — Update address (requires CLIENT/ADMIN)
  - DELETE /api/v1/direcciones/{id} — Soft-delete address (requires CLIENT/ADMIN)
  - PATCH /api/v1/direcciones/{id}/predeterminada — Set as default (requires CLIENT/ADMIN)

All endpoints:
  - Use UnitOfWork dependency (get_uow) for database access
  - Require authentication + CLIENT or ADMIN role
  - Use current_user from JWT for ownership validation
  - Return appropriate HTTP status codes (201, 200, 204, 404, 409, 422)
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError

from app.dependencies import get_current_user, get_uow, require_role
from app.exceptions import AppException, ConflictError
from app.models.usuario import Usuario
from app.modules.direcciones.schemas import (
    DireccionCreate,
    DireccionListResponse,
    DireccionRead,
    DireccionUpdate,
)
from app.modules.direcciones.service import DireccionService
from app.uow import UnitOfWork

logger = logging.getLogger(__name__)

# Create router with prefix and tag for Swagger grouping
router = APIRouter(prefix="/api/v1/direcciones", tags=["direcciones"])


@router.post(
    "",
    response_model=DireccionRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear dirección de entrega",
    responses={
        201: {"description": "Dirección creada exitosamente"},
        401: {"description": "No autenticado"},
        403: {"description": "Permisos insuficientes (CLIENT/ADMIN requerido)"},
        422: {"description": "Error de validación (linea1 vacío, alias muy largo)"},
    },
)
async def create_direccion(
    data: DireccionCreate,
    uow: UnitOfWork = Depends(get_uow),
    _: None = Depends(require_role(["CLIENT", "ADMIN"])),
    current_user: Usuario = Depends(get_current_user),
) -> DireccionRead:
    """
    Crear una nueva dirección de entrega.

    **Requiere**: CLIENT o ADMIN role

    **Reglas de negocio**:
    - La primera dirección del usuario se marca como predeterminada automáticamente
    - El alias es opcional (max 50 caracteres)
    - linea1 es requerido (min 1, max 500 caracteres)

    **Responses**:
    - 201: Dirección creada exitosamente
    - 422: Error de validación
    - 403: Permisos insuficientes
    """
    try:
        service = DireccionService(uow)
        result = await service.create_direccion(current_user.id, data)
        await uow.commit()
        return result
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        await uow.rollback()
        logger.error(f"POST /direcciones failed: {type(e).__name__}: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.get(
    "",
    response_model=DireccionListResponse,
    summary="Listar direcciones del usuario autenticado",
    responses={
        200: {"description": "Lista de direcciones del usuario"},
        401: {"description": "No autenticado"},
        403: {"description": "Permisos insuficientes"},
    },
)
async def list_direcciones(
    skip: int = Query(0, ge=0, description="Cantidad de registros a omitir"),
    limit: int = Query(100, ge=1, le=100, description="Cantidad de registros a devolver"),
    uow: UnitOfWork = Depends(get_uow),
    _: None = Depends(require_role(["CLIENT", "ADMIN"])),
    current_user: Usuario = Depends(get_current_user),
) -> DireccionListResponse:
    """
    Listar direcciones del usuario autenticado.

    **Requiere**: CLIENT o ADMIN role

    **Parámetros de consulta**:
    - `skip` (opcional, default 0): Registros a omitir (paginación)
    - `limit` (opcional, default 100): Registros por página (max 100)

    **Reglas de negocio**:
    - Solo devuelve direcciones del usuario autenticado
    - Excluye direcciones soft-deleted
    - Ordena por created_at DESC (más reciente primero)
    """
    try:
        service = DireccionService(uow)
        result = await service.list_direcciones(current_user.id, skip, limit)
        return result
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"GET /direcciones failed: {type(e).__name__}: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.put(
    "/{direccion_id}",
    response_model=DireccionRead,
    summary="Actualizar dirección de entrega",
    responses={
        200: {"description": "Dirección actualizada exitosamente"},
        401: {"description": "No autenticado"},
        403: {"description": "Permisos insuficientes"},
        404: {"description": "Dirección no encontrada"},
        422: {"description": "Error de validación"},
    },
)
async def update_direccion(
    direccion_id: int,
    data: DireccionUpdate,
    uow: UnitOfWork = Depends(get_uow),
    _: None = Depends(require_role(["CLIENT", "ADMIN"])),
    current_user: Usuario = Depends(get_current_user),
) -> DireccionRead:
    """
    Actualizar una dirección de entrega existente.

    **Requiere**: CLIENT o ADMIN role

    **Parámetros**:
    - `direccion_id`: ID de la dirección a actualizar (path)
    - `alias` (opcional): Nuevo alias
    - `linea1` (opcional): Nueva dirección

    **Reglas de negocio**:
    - Validación de ownership: 404 si la dirección no pertenece al usuario
    - Solo alias y linea1 pueden actualizarse (no es_principal)
    - Actualización parcial: solo los campos provistos se actualizan
    - Si no se proveen campos → 422
    """
    try:
        service = DireccionService(uow)
        result = await service.update_direccion(direccion_id, current_user.id, data)
        await uow.commit()
        return result
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        await uow.rollback()
        logger.error(f"PUT /direcciones/{direccion_id} failed: {type(e).__name__}: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.delete(
    "/{direccion_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar dirección de entrega (soft delete)",
    responses={
        204: {"description": "Dirección eliminada exitosamente"},
        401: {"description": "No autenticado"},
        403: {"description": "Permisos insuficientes"},
        404: {"description": "Dirección no encontrada"},
    },
)
async def delete_direccion(
    direccion_id: int,
    uow: UnitOfWork = Depends(get_uow),
    _: None = Depends(require_role(["CLIENT", "ADMIN"])),
    current_user: Usuario = Depends(get_current_user),
) -> None:
    """
    Eliminar (soft delete) una dirección de entrega.

    **Requiere**: CLIENT o ADMIN role

    **Parámetros**:
    - `direccion_id`: ID de la dirección a eliminar (path)

    **Reglas de negocio**:
    - Soft delete: marca deleted_at, no borra físicamente
    - Validación de ownership: 404 si no pertenece al usuario
    - Si se elimina la predeterminada, se reasigna a la más reciente
    """
    try:
        service = DireccionService(uow)
        await service.delete_direccion(direccion_id, current_user.id)
        await uow.commit()
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        await uow.rollback()
        logger.error(f"DELETE /direcciones/{direccion_id} failed: {type(e).__name__}: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.patch(
    "/{direccion_id}/predeterminada",
    response_model=DireccionRead,
    summary="Establecer dirección como predeterminada",
    responses={
        200: {"description": "Dirección establecida como predeterminada"},
        401: {"description": "No autenticado"},
        403: {"description": "Permisos insuficientes"},
        404: {"description": "Dirección no encontrada"},
        409: {"description": "Conflicto: ya existe una dirección predeterminada"},
    },
)
async def set_predeterminada(
    direccion_id: int,
    uow: UnitOfWork = Depends(get_uow),
    _: None = Depends(require_role(["CLIENT", "ADMIN"])),
    current_user: Usuario = Depends(get_current_user),
) -> DireccionRead:
    """
    Establecer una dirección como predeterminada.

    **Requiere**: CLIENT o ADMIN role

    **Parámetros**:
    - `direccion_id`: ID de la dirección a establecer como predeterminada (path)

    **Reglas de negocio**:
    - Operación atómica: desmarca la anterior y marca la nueva en la misma transacción
    - Idempotente: si ya es la predeterminada, devuelve 200 sin cambios
    - Validación de ownership: 404 si no pertenece al usuario
    - Si hay race condition, el índice único parcial garantiza integridad (409)
    """
    try:
        service = DireccionService(uow)
        result = await service.set_predeterminada(direccion_id, current_user.id)
        await uow.commit()
        return result
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except ConflictError as e:
        raise HTTPException(status_code=409, detail=e.message)
    except IntegrityError:
        await uow.rollback()
        raise HTTPException(
            status_code=409,
            detail="Ya existe una dirección predeterminada",
        )
    except Exception as e:
        await uow.rollback()
        logger.error(
            f"PATCH /direcciones/{direccion_id}/predeterminada failed: " f"{type(e).__name__}: {e}"
        )
        raise HTTPException(status_code=500, detail="Error interno del servidor")
