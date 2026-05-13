"""FastAPI router for Pagos endpoints — MercadoPago integration"""
import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.uow import UnitOfWork
from app.models.usuario import Usuario
from app.modules.pagos.schemas import (
    PagoCreate,
    PagoCreateResponse,
    PagoResponse,
    WebhookPayload,
    WebhookResponse,
)
from app.modules.pagos.service import PagoService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/pagos", tags=["pagos"])


async def get_uow() -> UnitOfWork:
    """
    Dependency that provides a UnitOfWork instance.

    Creates a new database session and wraps it in UnitOfWork.
    The UoW context manager handles commit/rollback automatically.
    """
    async for session in get_db():
        yield UnitOfWork(session)


@router.post("/crear", response_model=PagoCreateResponse, status_code=201)
async def crear_pago(
    body: PagoCreate,
    current_user: Usuario = Depends(get_current_user),
    uow: UnitOfWork = Depends(get_uow),
):
    """
    Create a MercadoPago payment for an order.

    - Validates order exists and belongs to user
    - Validates order is in PENDIENTE state
    - Creates payment record with idempotency key
    - Calls MP API to create payment preference
    - Returns init_point for redirect to MP checkout

    Requires roles: CLIENT, ADMIN
    """
    service = PagoService(uow)
    return await service.crear_pago(usuario_id=current_user.id, body=body)


@router.get("/{pedido_id}", response_model=PagoResponse)
async def get_pago(
    pedido_id: int,
    current_user: Usuario = Depends(get_current_user),
    uow: UnitOfWork = Depends(get_uow),
):
    """
    Get payment details for an order.

    - Returns payment info if exists
    - 404 if no payment found for the order

    Requires roles: CLIENT (only own orders), ADMIN (all orders)
    """
    service = PagoService(uow)
    pago = await service.get_payment_by_pedido(pedido_id)

    if not pago:
        raise HTTPException(status_code=404, detail="No se encontró pago para este pedido")

    # Authorization: CLIENT can only see their own, ADMIN can see all
    # Note: We need to fetch the pedido to check ownership
    pedido = await uow.pedidos.find(pedido_id)
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    if current_user.id != pedido.usuario_id and current_user.rol != "ADMIN":
        raise HTTPException(status_code=403, detail="No tienes permiso para ver este pago")

    return PagoResponse(
        id=pago.id,
        pedido_id=pago.pedido_id,
        mp_payment_id=pago.mp_payment_id,
        mp_status=pago.mp_status,
        mp_status_detail=pago.mp_status_detail,
        external_reference=pago.external_reference,
        idempotency_key=pago.idempotency_key,
        monto=pago.monto,
        created_at=pago.created_at,
        updated_at=pago.updated_at,
        deleted_at=pago.deleted_at,
    )


@router.post("/webhook", response_model=WebhookResponse)
async def webhook(
    topic: str = Query(..., description="Webhook topic from MP"),
    id: str = Query(..., description="MP payment ID"),
    uow: UnitOfWork = Depends(get_uow),
):
    """
    MercadoPago webhook endpoint (IPN - Instant Payment Notification).

    IMPORTANT:
    - This endpoint is PUBLIC (no auth) - MP sends the webhook
    - We ALWAYS validate against MP API, never trust webhook payload alone
    - Idempotency: duplicate webhooks are ignored

    Query params come from MP:
    - topic: "payment"
    - id: MP payment ID

    Returns:
        HTTP 200 with processing result
    """
    logger.info(f"Received webhook: topic={topic}, id={id}")

    service = PagoService(uow)
    result = await service.procesar_webhook(topic=topic, resource_id=id)

    return WebhookResponse(
        message=result.get("message", "Processed"),
        processed=result.get("processed", False),
    )