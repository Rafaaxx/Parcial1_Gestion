"""FastAPI router for Pedido endpoints"""
import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_uow, get_current_user
from app.uow import UnitOfWork
from app.modules.pedidos.schemas import (
    CrearPedidoRequest,
    PedidoRead,
    PedidoDetail,
    PedidoListResponse,
    DetallePedidoRead,
    HistorialEstadoPedidoRead,
)
from app.modules.pedidos.service import PedidoService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/pedidos", tags=["pedidos"])


async def get_uow() -> UnitOfWork:
    """
    Dependency that provides a UnitOfWork instance.

    Creates a new database session and wraps it in UnitOfWork.
    The UoW context manager handles commit/rollback automatically.
    """
    async for session in get_db():
        yield UnitOfWork(session)


@router.post("", response_model=PedidoRead, status_code=201)
async def crear_pedido(
    body: CrearPedidoRequest,
    current_user = Depends(get_current_user),
    uow: UnitOfWork = Depends(get_uow),
):
    """
    Create a new order from cart items.

    Atomic transaction: all-or-nothing.
    Validates address ownership, payment method, and stock (SELECT FOR UPDATE)
    before committing.

    Requires roles: CLIENT, ADMIN

    Returns:
        201 PedidoRead on success
        404 if address not found/not owned
        422 if payment method invalid or stock insufficient
    """
    service = PedidoService(uow)
    try:
        pedido = await service.crear_pedido(
            usuario_id=current_user.id,
            body=body,
        )
        return PedidoRead.model_validate(pedido)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating order: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error interno al crear el pedido")


def _check_pedidos_role(
    current_user = Depends(get_current_user),
) -> dict:
    """Allow CLIENT, ADMIN, or PEDIDOS to access orders."""
    from app.models.usuario_rol import UsuarioRol
    allowed_roles = {"CLIENT", "ADMIN", "PEDIDOS"}
    user_roles = {ur.rol_codigo for ur in (current_user.usuario_roles or [])}
    if not user_roles.intersection(allowed_roles):
        raise HTTPException(
            status_code=403,
            detail={
                "detail": "No tienes permisos para acceder a este recurso",
                "code": "FORBIDDEN",
            },
        )
    return {
        "id": current_user.id,
        "email": current_user.email,
        "roles": list(user_roles),
    }


@router.get("", response_model=PedidoListResponse)
async def listar_pedidos(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    current_user: dict = Depends(_check_pedidos_role),
    uow: UnitOfWork = Depends(get_uow),
):
    """
    List orders.

    CLIENT role: only returns orders owned by the current user.
    ADMIN/PEDIDOS roles: returns all orders in the system.

    Supports pagination with skip and limit query parameters.
    """
    service = PedidoService(uow)
    pedidos, total = await service.listar_pedidos(
        usuario_id=current_user["id"],
        roles=current_user["roles"],
        skip=skip,
        limit=limit,
    )
    return PedidoListResponse(
        items=[PedidoRead.model_validate(p) for p in pedidos],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{pedido_id}", response_model=PedidoDetail)
async def obtener_pedido(
    pedido_id: int,
    current_user: dict = Depends(_check_pedidos_role),
    uow: UnitOfWork = Depends(get_uow),
):
    """
    Get order detail with line items and state history.

    CLIENT can only see their own orders.
    ADMIN/PEDIDOS can see any order.

    Returns:
        200 PedidoDetail on success
        404 if order not found or not accessible to user
    """
    service = PedidoService(uow)
    pedido = await service.obtener_detalle(
        pedido_id=pedido_id,
        usuario_id=current_user["id"],
        roles=current_user["roles"],
    )
    if pedido is None:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    detalles = [
        DetallePedidoRead.model_validate(d) for d in pedido.detalles
    ]
    historial = [
        HistorialEstadoPedidoRead.model_validate(h) for h in sorted(
            pedido.historial, key=lambda x: x.created_at
        )
    ]

    return PedidoDetail(
        id=pedido.id,
        usuario_id=pedido.usuario_id,
        estado_codigo=pedido.estado_codigo,
        total=pedido.total,
        costo_envio=pedido.costo_envio,
        forma_pago_codigo=pedido.forma_pago_codigo,
        direccion_id=pedido.direccion_id,
        notas=pedido.notas,
        detalles=detalles,
        historial=historial,
        created_at=pedido.created_at,
        updated_at=pedido.updated_at,
    )


@router.get("/{pedido_id}/historial", response_model=List[HistorialEstadoPedidoRead])
async def obtener_historial(
    pedido_id: int,
    current_user: dict = Depends(_check_pedidos_role),
    uow: UnitOfWork = Depends(get_uow),
):
    """
    Get state transition history for an order.

    Returns the audit trail of state changes ordered chronologically.
    The first record always has estado_desde=NULL (initial transition).

    CLIENT can only access their own orders' history.
    ADMIN/PEDIDOS can access any order's history.

    Returns:
        200 List[HistorialEstadoPedidoRead] on success
        404 if order not found or not accessible
    """
    service = PedidoService(uow)
    pedido = await service.obtener_detalle(
        pedido_id=pedido_id,
        usuario_id=current_user["id"],
        roles=current_user["roles"],
    )
    if pedido is None:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    historial = await service.obtener_historial(pedido_id)
    return [HistorialEstadoPedidoRead.model_validate(h) for h in historial]
