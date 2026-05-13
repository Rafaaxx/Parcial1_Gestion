"""Business logic service for MercadoPago payments with idempotency and FSM integration"""
import logging
import os
import uuid
from typing import Optional
from decimal import Decimal

import mercadopago
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings

from app.uow import UnitOfWork
from app.modules.pagos.model import Pago
from app.modules.pagos.repository import PagoRepository
from app.modules.pagos.schemas import (
    PagoCreate,
    PagoCreateResponse,
    PagoResponse,
    WebhookPayload,
)
from app.modules.pedidos.service import PedidoService
from app.models.pedido import Pedido

logger = logging.getLogger(__name__)


class PaymentAlreadyExistsError(HTTPException):
    """Raised when a payment already exists for an order."""

    def __init__(self, pedido_id: int):
        detail = f"Ya existe un pago para el pedido {pedido_id}"
        super().__init__(status_code=409, detail=detail)


class IdempotencyConflictError(HTTPException):
    """Raised when idempotency key already exists."""

    def __init__(self):
        detail = "La clave de idempotencia ya fue utilizada. No se procesará el pago duplicado."
        super().__init__(status_code=409, detail=detail)


class MPConnectionError(HTTPException):
    """Raised when MercadoPago API is unreachable."""

    def __init__(self, detail: str = "Error de conexión con MercadoPago"):
        super().__init__(status_code=503, detail=detail)


class PagoService:
    """
    Service layer for MercadoPago payment operations.

    Stateless. Receives UnitOfWork via constructor.
    Does NOT call session.commit() — the UoW context manager handles it.

    Flow for crear_pago:
    1. Validate order exists and is in PENDIENTE state
    2. Check if payment already exists for this order (409 if exists)
    3. Generate idempotency_key
    4. Create Pago record in DB (for idempotency)
    5. Call MP API with idempotency_key
    6. Update Pago with MP response (payment_id, status, init_point)
    7. Return init_point for redirect or status

    Flow for procesar_webhook:
    1. Extract payment_id from webhook
    2. Query MP API to get real status (NEVER trust webhook payload alone!)
    3. Find Pago by mp_payment_id or external_reference
    4. If already processed, return (idempotency)
    5. Update Pago status
    6. If approved, transition order to CONFIRMADO via FSM
    """

    def __init__(self, uow: UnitOfWork):
        """
        Initialize service with UnitOfWork.

        Args:
            uow: UnitOfWork instance with active database session
        """
        self.uow = uow
        self._mp_client = None

    @property
    def mp_client(self) -> mercadopago.SDK:
        """Lazy initialization of MercadoPago SDK."""
        if self._mp_client is None:
            access_token = settings.mp_access_token
            print("Access_Token: ", access_token)
            if not access_token:
                raise ValueError("MP_ACCESS_TOKEN not configured")
            self._mp_client = mercadopago.SDK(access_token,)
        return self._mp_client

    async def crear_pago(
        self,
        usuario_id: int,
        body: PagoCreate,
    ) -> PagoCreateResponse:
        """
        Create a payment for an order via MercadoPago.

        Args:
            usuario_id: ID of the user creating the payment
            body: Payment creation request

        Returns:
            PagoCreateResponse with init_point or payment details

        Raises:
            HTTPException: 404 if order not found, 409 if payment exists
        """
        # 1. Get order and validate
        pedido = await self.uow.pedidos.find(body.pedido_id)
        if not pedido:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")

        if pedido.usuario_id != usuario_id:
            raise HTTPException(status_code=403, detail="No tienes permiso para pagar este pedido")

        if pedido.estado_codigo != "PENDIENTE":
            raise HTTPException(
                status_code=400,
                detail=f"El pedido no está en estado PENDIENTE (actual: {pedido.estado_codigo})",
            )

        # 2. Check if payment already exists
        repo = PagoRepository(self.uow.session)
        existing_payment = await repo.get_by_pedido_id(body.pedido_id)
        if existing_payment:
            raise PaymentAlreadyExistsError(body.pedido_id)

        # 3. Generate idempotency key
        idempotency_key = str(uuid.uuid4())
        external_reference = str(pedido.id)  # Use pedido ID as reference

        # 4. Create initial payment record (for idempotency)
        pago = await repo.create_with_idempotency(
            pedido_id=pedido.id,
            external_reference=external_reference,
            idempotency_key=idempotency_key,
            monto=float(pedido.total),
        )

        try:
            # 5. Call MP API to create payment
            preference_data = {
                "items": [
                    {
                        "title": f"Pedido #{pedido.id}",
                        "quantity": 1,
                        "unit_price": float(pedido.total),
                        "currency_id": "ARS",
                    }
                ],
                "external_reference": external_reference,
                "notification_url": settings.mp_notification_url,
                "back_urls": {
                    "success": f"{settings.frontend_url}/checkout/success",
                    "pending": f"{settings.frontend_url}/checkout/pending",
                    "failure": f"{settings.frontend_url}/checkout/failure",
                },
            }

            print("Preference Data:", preference_data)

            # Use preference (checkout redirection) instead of direct card payment
            # This is simpler and more common for this use case
            result = self.mp_client.preference().create(preference_data)

            if result["status"] == 201:
                preference = result["response"]
                init_point = preference.get("init_point")

                return PagoCreateResponse(
                    mp_payment_id=None,  # No payment created yet, just preference
                    status="pending",
                    init_point=init_point,
                    external_reference=external_reference,
                    monto=pedido.total,
                )
            else:
                logger.error(f"MP API error: {result}")
                raise MPConnectionError(f"Error al crear preferencia en MP: {result.get('message', 'Unknown')}")

        except Exception as e:
            logger.error(f"Error calling MP API: {e}")
            # Don't delete the payment record - it can be retried
            raise MPConnectionError(f"Error de conexión con MercadoPago: {str(e)}")

    async def get_payment_by_pedido(self, pedido_id: int) -> Optional[Pago]:
        """
        Get payment details for an order.

        Args:
            pedido_id: Order ID to search for

        Returns:
            Pago instance or None if not found
        """
        repo = PagoRepository(self.uow.session)
        return await repo.get_by_pedido_id(pedido_id)

    async def procesar_webhook(self, topic: str, resource_id: str) -> dict:
        """
        Process webhook notification from MercadoPago.

        IMPORTANT: Always validate against MP API - never trust webhook payload alone!

        Args:
            topic: Webhook topic (e.g., "payment")
            resource_id: MP payment ID to look up

        Returns:
            Dict with processing result
        """
        if topic != "payment":
            logger.warning(f"Ignoring webhook with topic: {topic}")
            return {"processed": False, "message": f"Unsupported topic: {topic}"}

        # 1. Query MP API to get REAL status (never trust webhook!)
        try:
            payment_info = self.mp_client.payment().get(resource_id)
            if payment_info["status"] != 200:
                logger.error(f"MP API error: {payment_info}")
                return {"processed": False, "message": "Error fetching payment from MP"}
            
            mp_payment = payment_info["response"]
            mp_status = mp_payment.get("status", "unknown")
            mp_status_detail = mp_payment.get("status_detail", "")
            external_ref = mp_payment.get("external_reference")
        except Exception as e:
            logger.error(f"Error fetching MP payment: {e}")
            return {"processed": False, "message": f"Error connecting to MP: {e}"}

        # 2. Find payment in our DB
        repo = PagoRepository(self.uow.session)
        
        # Try by mp_payment_id first, then by external_reference
        pago = await repo.get_by_mp_payment_id(int(resource_id))
        if not pago and external_ref:
            # Find by external_reference (pedido_id)
            try:
                pedido_id = int(external_ref)
                pago = await repo.get_by_pedido_id(pedido_id)
            except (ValueError, TypeError):
                pass

        if not pago:
            logger.warning(f"Pago not found for MP payment {resource_id}")
            return {"processed": False, "message": "Payment not found in database"}

        # 3. Idempotency: if already processed, skip
        if pago.mp_payment_id and pago.mp_status in ("approved", "rejected", "cancelled", "refunded"):
            logger.info(f"Pago {pago.id} already processed with status {pago.mp_status}")
            return {"processed": True, "message": "Already processed"}

        # 4. Update payment status
        await repo.update_status(
            pago_id=pago.id,
            mp_status=mp_status,
            mp_status_detail=mp_status_detail,
            mp_payment_id=int(resource_id),
        )

        # 5. If approved, transition order to CONFIRMADO
        if mp_status == "approved":
            await self._transition_pedido_to_confirmado(pago.pedido_id)

        return {
            "processed": True,
            "message": f"Payment status updated to {mp_status}",
            "pedido_id": pago.pedido_id,
            "new_status": mp_status,
        }

    async def _transition_pedido_to_confirmado(self, pedido_id: int):
        """
        Transition order to CONFIRMADO state after payment approval.

        This integrates with the FSM via PedidoService.
        """
        try:
            pedido_service = PedidoService(self.uow)
            await pedido_service.cambiar_estado(
                pedido_id=pedido_id,
                nuevo_estado="CONFIRMADO",
                observacion="Pago aprobado via MercadoPago",
                usuario_id=None,  # System transition
            )
            logger.info(f"Pedido {pedido_id} transitioned to CONFIRMADO")
        except Exception as e:
            logger.error(f"Error transitioning pedido {pedido_id} to CONFIRMADO: {e}")
            # Don't raise - payment is already recorded, FSM failure is logged