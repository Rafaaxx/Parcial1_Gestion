"""Admin router — metrics endpoints and user management.

All endpoints require ADMIN role.
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.dependencies import get_current_user, get_uow, require_role
from app.exceptions import AppException, ConflictError, NotFoundError
from app.models.usuario import Usuario
from app.modules.admin.repository import AdminRepository
from app.modules.admin.schemas import (
    PedidoEstadoRead,
    ProductoTopRead,
    ResumenMetricasRead,
    UsuarioAdminListResponse,
    UsuarioAdminRead,
    UsuarioAdminUpdate,
    UsuarioEstadoUpdate,
    VentaPeriodoRead,
)
from app.modules.admin.service import AdminService
from app.uow import UnitOfWork

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/admin",
    tags=["Admin"],
    dependencies=[Depends(require_role(["ADMIN"]))],
)


def _get_admin_service() -> AdminService:
    """Factory for AdminService (stateless)."""
    return AdminService()


def _get_admin_repo(uow: UnitOfWork = Depends(get_uow)) -> AdminRepository:
    """Factory for AdminRepository bound to the current UoW."""
    return AdminRepository(uow.session)


# ═══════════════════════════════════════════════════════════════════════════════
# Metrics Endpoints
# ═══════════════════════════════════════════════════════════════════════════════


@router.get("/metricas/resumen", response_model=ResumenMetricasRead)
async def get_resumen(
    desde: Optional[str] = Query(default=None, description="Fecha inicio (YYYY-MM-DD)"),
    hasta: Optional[str] = Query(default=None, description="Fecha fin (YYYY-MM-DD)"),
    uow: UnitOfWork = Depends(get_uow),
    repo: AdminRepository = Depends(_get_admin_repo),
    service: AdminService = Depends(_get_admin_service),
):
    """Get dashboard metrics summary (sales, orders, users, top products)."""
    async with uow:
        result = await service.get_resumen(uow=uow, repo=repo, desde=desde, hasta=hasta)
    return result


@router.get("/metricas/ventas", response_model=list[VentaPeriodoRead])
async def get_ventas(
    granularidad: str = Query(default="dia", description="Granularidad: dia, semana, mes"),
    desde: Optional[str] = Query(default=None, description="Fecha inicio (YYYY-MM-DD)"),
    hasta: Optional[str] = Query(default=None, description="Fecha fin (YYYY-MM-DD)"),
    uow: UnitOfWork = Depends(get_uow),
    repo: AdminRepository = Depends(_get_admin_repo),
    service: AdminService = Depends(_get_admin_service),
):
    """Get sales by period with granularity."""
    if granularidad not in ("dia", "semana", "mes"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "detail": "Granularidad inválida. Use: dia, semana o mes",
                "code": "VALIDATION_ERROR",
            },
        )
    async with uow:
        result = await service.get_ventas(
            uow=uow, repo=repo, granularidad=granularidad, desde=desde, hasta=hasta
        )
    return result


@router.get("/metricas/productos-top", response_model=list[ProductoTopRead])
async def get_productos_top(
    top: int = Query(default=10, ge=1, le=50, description="Cantidad de productos (max 50)"),
    desde: Optional[str] = Query(default=None, description="Fecha inicio (YYYY-MM-DD)"),
    hasta: Optional[str] = Query(default=None, description="Fecha fin (YYYY-MM-DD)"),
    uow: UnitOfWork = Depends(get_uow),
    repo: AdminRepository = Depends(_get_admin_repo),
    service: AdminService = Depends(_get_admin_service),
):
    """Get top selling products."""
    async with uow:
        result = await service.get_productos_top(
            uow=uow, repo=repo, top=top, desde=desde, hasta=hasta
        )
    return result


@router.get("/metricas/pedidos-por-estado", response_model=list[PedidoEstadoRead])
async def get_pedidos_por_estado(
    desde: Optional[str] = Query(default=None, description="Fecha inicio (YYYY-MM-DD)"),
    hasta: Optional[str] = Query(default=None, description="Fecha fin (YYYY-MM-DD)"),
    uow: UnitOfWork = Depends(get_uow),
    repo: AdminRepository = Depends(_get_admin_repo),
    service: AdminService = Depends(_get_admin_service),
):
    """Get order distribution by state with percentages."""
    async with uow:
        result = await service.get_pedidos_por_estado(uow=uow, repo=repo, desde=desde, hasta=hasta)
    return result


# ═══════════════════════════════════════════════════════════════════════════════
# Admin User Management Endpoints
# ═══════════════════════════════════════════════════════════════════════════════


@router.get("/usuarios", response_model=UsuarioAdminListResponse)
async def list_usuarios(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    busqueda: Optional[str] = Query(default=None, description="Búsqueda por nombre o email"),
    rol: Optional[str] = Query(
        default=None,
        description="Filtrar por código de rol (ADMIN, STOCK, PEDIDOS, CLIENT)",
    ),
    activo: Optional[bool] = Query(default=None, description="Filtrar por estado activo/inactivo"),
    uow: UnitOfWork = Depends(get_uow),
    repo: AdminRepository = Depends(_get_admin_repo),
    service: AdminService = Depends(_get_admin_service),
):
    """List users with pagination, search, and filters."""
    async with uow:
        result = await service.list_usuarios(
            repo=repo,
            skip=skip,
            limit=limit,
            busqueda=busqueda,
            rol=rol,
            activo=activo,
        )
    return result


@router.put("/usuarios/{usuario_id}", response_model=UsuarioAdminRead)
async def update_usuario(
    usuario_id: int,
    body: UsuarioAdminUpdate,
    current_user: Usuario = Depends(get_current_user),
    uow: UnitOfWork = Depends(get_uow),
    repo: AdminRepository = Depends(_get_admin_repo),
    service: AdminService = Depends(_get_admin_service),
):
    """Update user data and/or roles.

    Validates:
      - User exists (404)
      - Cannot remove ADMIN from the last admin (409)
    """
    async with uow:
        try:
            result = await service.update_usuario(
                repo=repo,
                usuario_id=usuario_id,
                nombre=body.nombre,
                email=str(body.email) if body.email else None,
                roles_codes=body.roles_codes,
            )
        except (NotFoundError, ConflictError) as e:
            raise HTTPException(
                status_code=e.status_code,
                detail={
                    "detail": e.message,
                    "code": e.error_code,
                },
            )
    return result


@router.patch("/usuarios/{usuario_id}/estado", response_model=UsuarioAdminRead)
async def update_usuario_estado(
    usuario_id: int,
    body: UsuarioEstadoUpdate,
    current_user: Usuario = Depends(get_current_user),
    uow: UnitOfWork = Depends(get_uow),
    repo: AdminRepository = Depends(_get_admin_repo),
    service: AdminService = Depends(_get_admin_service),
):
    """Activate or deactivate a user.

    Validates:
      - Cannot deactivate yourself (409)
      - User exists (404)
    """
    async with uow:
        try:
            result = await service.update_usuario_estado(
                repo=repo,
                target_usuario_id=usuario_id,
                current_usuario_id=current_user.id,
                activo=body.activo,
            )
        except (NotFoundError, ConflictError) as e:
            raise HTTPException(
                status_code=e.status_code,
                detail={
                    "detail": e.message,
                    "code": e.error_code,
                },
            )
    return result
