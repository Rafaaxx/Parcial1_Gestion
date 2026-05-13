"""FastAPI router for Pedido endpoints"""
import logging
from typing import List, Optional
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
    AvanzarEstadoRequest,
    TransicionResponse,
    ClienteInfo,
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
    estado: Optional[str] = Query(default=None, description="Filter by state code (e.g., PENDIENTE, CONFIRMADO, EN_PREP, EN_CAMINO, ENTREGADO, CANCELADO)"),
    desde: Optional[str] = Query(default=None, description="Filter by creation date (start) - YYYY-MM-DD"),
    hasta: Optional[str] = Query(default=None, description="Filter by creation date (end) - YYYY-MM-DD"),
    busqueda: Optional[str] = Query(default=None, description="Search by order ID or customer name/email"),
    current_user: dict = Depends(_check_pedidos_role),
    uow: UnitOfWork = Depends(get_uow),
):
    """
    List orders.

    CLIENT role: only returns orders owned by the current user.
    ADMIN/PEDIDOS roles: returns all orders in the system.

    Supports:
    - Pagination with skip and limit query parameters
    - Filter by state (estado)
    - Filter by date range (desde, hasta)
    - Search by order ID or customer name/email (busqueda)
    """
    service = PedidoService(uow)
    filtros = {
        "estado": estado,
        "desde": desde,
        "hasta": hasta,
        "busqueda": busqueda,
    }
    pedidos, total = await service.listar_pedidos(
        usuario_id=current_user["id"],
        roles=current_user["roles"],
        skip=skip,
        limit=limit,
        filtros=filtros,
    )
    # Build response with client info
    items = []
    for p in pedidos:
        cliente = None
        if p.usuario:
            cliente = ClienteInfo(
                id=p.usuario.id,
                nombre=f"{p.usuario.nombre} {p.usuario.apellido}".strip() or None,
                email=p.usuario.email,
            )
        pedido_read = PedidoRead(
            id=p.id,
            usuario_id=p.usuario_id,
            estado_codigo=p.estado_codigo,
            total=p.total,
            costo_envio=p.costo_envio,
            created_at=p.created_at,
            cliente=cliente,
        )
        items.append(pedido_read)
    
    return PedidoListResponse(
        items=items,
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

    # Build client info
    cliente = None
    if pedido.usuario:
        cliente = ClienteInfo(
            id=pedido.usuario.id,
            nombre=f"{pedido.usuario.nombre} {pedido.usuario.apellido}".strip() or None,
            email=pedido.usuario.email,
        )

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
        cliente=cliente,
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


@router.patch("/{pedido_id}/estado", response_model=TransicionResponse)
async def avanzar_estado(
    pedido_id: int,
    body: AvanzarEstadoRequest,
    current_user: dict = Depends(_check_pedidos_role),
    uow: UnitOfWork = Depends(get_uow),
):
    """
    Transition an order to a new state.

    Validates the transition against the FSM rules (state machine):
    - PENDIENTE → CONFIRMADO (only SISTEMA role)
    - PENDIENTE → CANCELADO (CLIENT, ADMIN, PEDIDOS with motivo)
    - CONFIRMADO → EN_PREP (ADMIN, PEDIDOS)
    - CONFIRMADO → CANCELADO (ADMIN, PEDIDOS with motivo)
    - EN_PREP → EN_CAMINO (ADMIN, PEDIDOS)
    - EN_PREP → CANCELADO (ADMIN with motivo)
    - EN_CAMINO → ENTREGADO (ADMIN, PEDIDOS)

    Stock is decremented on CONFIRMADO and restored on CANCELADO (from CONFIRMADO/EN_PREP).

    Returns:
        200 TransicionResponse on success
        404 if order not found
        422 if transition invalid
        403 if role not allowed
    """
    service = PedidoService(uow)
    try:
        pedido = await service.transicionar_estado(
            pedido_id=pedido_id,
            nuevo_estado=body.nuevo_estado,
            usuario_id=current_user["id"],
            roles=current_user["roles"],
            motivo=body.motivo,
        )
        return TransicionResponse(
            id=pedido.id,
            estado_codigo=pedido.estado_codigo,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error transitioning order state: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error interno al cambiar estado del pedido")


@router.delete("/{pedido_id}", response_model=TransicionResponse)
async def cancelar_pedido(
    pedido_id: int,
    motivo: Optional[str] = Query(
        default=None,
        description="Reason for cancellation (required for CANCELADO)",
    ),
    current_user: dict = Depends(get_current_user),
    uow: UnitOfWork = Depends(get_uow),
):
    """
    Cancel an order (convenience endpoint).

    CLIENT can only cancel their own PENDIENTE orders.
    ADMIN/PEDIDOS can cancel PENDIENTE or CONFIRMADO orders.

    Stock is restored if the order was CONFIRMADO (stock was decremented).

    Returns:
        200 TransicionResponse with estado_codigo=CANCELADO on success
        404 if order not found
        422 if cancellation not allowed
        403 if role not allowed or not own order (CLIENT)
    """
    # Get user roles
    user_roles = set()
    if hasattr(current_user, 'usuario_roles') and current_user.usuario_roles:
        user_roles = {ur.rol_codigo for ur in current_user.usuario_roles}

    service = PedidoService(uow)
    try:
        # Get current order state to determine allowed transitions
        pedido = await service.obtener_detalle(
            pedido_id=pedido_id,
            usuario_id=current_user.id,
            roles=list(user_roles),
        )

        if pedido is None:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")

        # Determine target state based on role and current state
        if "CLIENT" in user_roles:
            # CLIENT can only cancel their own PENDIENTE orders
            if pedido.estado_codigo != "PENDIENTE":
                raise HTTPException(
                    status_code=403,
                    detail="Solo puedes cancelar pedidos en estado PENDIENTE",
                )
            if pedido.usuario_id != current_user.id:
                raise HTTPException(
                    status_code=403,
                    detail="No puedes cancelar pedidos de otros usuarios",
                )
            # CLIENT can transition to CANCELADO from PENDIENTE
            nuevo_estado = "CANCELADO"
        elif "ADMIN" in user_roles or "PEDIDOS" in user_roles:
            # ADMIN/PEDIDOS can cancel PENDIENTE or CONFIRMADO
            if pedido.estado_codigo not in ("PENDIENTE", "CONFIRMADO"):
                raise HTTPException(
                    status_code=422,
                    detail=f"No se puede cancelar un pedido en estado {pedido.estado_codigo}",
                )
            nuevo_estado = "CANCELADO"
        else:
            raise HTTPException(
                status_code=403,
                detail="No tienes permisos para cancelar pedidos",
            )

        # Require motivo for cancellation
        if not motivo:
            raise HTTPException(
                status_code=422,
                detail="El motivo es obligatorio para cancelar",
            )

        # Execute transition
        pedido = await service.transicionar_estado(
            pedido_id=pedido_id,
            nuevo_estado=nuevo_estado,
            usuario_id=current_user.id,
            roles=list(user_roles),
            motivo=motivo,
        )

        return TransicionResponse(
            id=pedido.id,
            estado_codigo=pedido.estado_codigo,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling order: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error interno al cancelar el pedido")
