"""FastAPI router for Pagos endpoints — MercadoPago integration with webhook support"""
import asyncio
import logging
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from fastapi.background import BackgroundTasks
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
from app.modules.pagos import mp_client

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


async def _procesar_webhook_background(topic: str, resource_id: str) -> None:
    """
    Background task to process webhook asynchronously.

    This runs after the HTTP 200 response is sent to MercadoPago.
    Uses a separate database session to avoid conflicts.
    """
    logger.info(f"[WEBHOOK BG] Processing background task: topic={topic}, id={resource_id}")

    try:
        async for session in get_db():
            uow = UnitOfWork(session)
            service = PagoService(uow)
            result = await service.procesar_webhook(topic=topic, resource_id=resource_id)
            logger.info(f"[WEBHOOK BG] Result: {result}")
            await session.close()
            return
    except Exception as e:
        logger.error(f"[WEBHOOK BG] Error processing webhook: {e}")


@router.post("/webhook", response_model=WebhookResponse)
async def webhook(
    topic: str = Query(..., description="Webhook topic from MP"),
    id: str = Query(..., description="MP payment ID"),
    background_tasks: BackgroundTasks = None,
    x_signature: str = Query(None, description="X-Signature header from MP"),
    x_request_id: str = Query(None, description="X-Request-Id header from MP"),
):
    """
    MercadoPago webhook endpoint (IPN - Instant Payment Notification).

    CRITICAL FLOW:
    1. Validate X-Signature header (security)
    2. Respond HTTP 200 IMMEDIATELY (before any processing)
    3. Process webhook in background task

    MercadoPago reintenta webhooks if no 200 response within ~30 seconds.
    We respond immediately and process asynchronously.

    Headers from MP:
    - X-Signature: HMAC signature for validation
    - X-Request-Id: Unique request ID

    Query params from MP:
    - topic: "payment"
    - id: MP payment ID

    Returns:
        HTTP 200 with status "ok" immediately (processing happens in background)
    """
    logger.info(f"[WEBHOOK] Received: topic={topic}, id={id}, signature={x_signature[:40] if x_signature else 'None'}...")

    # Validate signature (security)
    if x_signature:
        if not mp_client.validar_firma_webhook(id, x_signature, x_request_id):
            logger.warning(f"[WEBHOOK] Invalid signature for payment {id}")
            raise HTTPException(status_code=403, detail="Invalid webhook signature")

    # Process only payment topics
    if topic != "payment":
        logger.info(f"[WEBHOOK] Ignoring non-payment topic: {topic}")
        return WebhookResponse(message="Ignored (unsupported topic)", processed=False)

    # ⚡ RESPONDER HTTP 200 INMEDIATAMENTE
    # MercadoPago necesita este 200 rápido para no reintentar
    logger.info(f"[WEBHOOK] Sending HTTP 200 immediately for payment {id}")

    # Programar procesamiento en background (después de enviar respuesta)
    if background_tasks:
        background_tasks.add_task(_procesar_webhook_background, topic, id)

    return WebhookResponse(
        message="ok",
        processed=True,
    )


@router.post("/webhook-legacy", response_model=WebhookResponse)
async def webhook_legacy(
    payload: WebhookPayload,
    background_tasks: BackgroundTasks = None,
    x_signature: str = Query(None, description="X-Signature header from MP"),
    x_request_id: str = Query(None, description="X-Request-Id header from MP"),
):
    """
    Legacy webhook endpoint for MercadoPago (form-encoded POST body).

    Same flow as /webhook but accepts JSON body instead of query params.
    """
    topic = payload.topic
    resource_id = payload.action_id or payload.resource or ""

    logger.info(f"[WEBHOOK LEGACY] Received: topic={topic}, id={resource_id}")

    # Validate signature (security)
    if x_signature and resource_id:
        if not mp_client.validar_firma_webhook(resource_id, x_signature, x_request_id):
            logger.warning(f"[WEBHOOK LEGACY] Invalid signature for payment {resource_id}")
            raise HTTPException(status_code=403, detail="Invalid webhook signature")

    # Process only payment topics
    if topic != "payment":
        logger.info(f"[WEBHOOK LEGACY] Ignoring non-payment topic: {topic}")
        return WebhookResponse(message="Ignored (unsupported topic)", processed=False)

    # ⚡ RESPONDER HTTP 200 INMEDIATAMENTE
    logger.info(f"[WEBHOOK LEGACY] Sending HTTP 200 immediately for payment {resource_id}")

    # Programar procesamiento en background (después de enviar respuesta)
    if background_tasks and resource_id:
        background_tasks.add_task(_procesar_webhook_background, topic, resource_id)

    return WebhookResponse(
        message="ok",
        processed=True,
    )