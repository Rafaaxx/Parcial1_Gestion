"""PagoRepository — CRUD operations for MercadoPago payments"""

import logging
from typing import Optional

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.pagos.model import Pago
from app.repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class PagoRepository(BaseRepository[Pago]):
    """
    Repository for Pago entity with MercadoPago-specific queries.

    Provides methods for:
    - Creating payments
    - Finding by pedido_id, idempotency_key, or mp_payment_id
    - Updating payment status
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session, Pago)

    async def get_by_pedido_id(self, pedido_id: int) -> Optional[Pago]:
        """
        Get payment by order ID.

        Args:
            pedido_id: Order ID to search for

        Returns:
            Pago instance or None if not found
        """
        query = select(Pago).where(
            and_(
                Pago.pedido_id == pedido_id,
                Pago.deleted_at.is_(None),
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_idempotency_key(self, idempotency_key: str) -> Optional[Pago]:
        """
        Get payment by idempotency key (for duplicate prevention).

        Args:
            idempotency_key: Unique key to search for

        Returns:
            Pago instance or None if not found
        """
        query = select(Pago).where(
            and_(
                Pago.idempotency_key == idempotency_key,
                Pago.deleted_at.is_(None),
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_mp_payment_id(self, mp_payment_id: int) -> Optional[Pago]:
        """
        Get payment by MercadoPago payment ID.

        Args:
            mp_payment_id: MP payment ID to search for

        Returns:
            Pago instance or None if not found
        """
        query = select(Pago).where(
            and_(
                Pago.mp_payment_id == mp_payment_id,
                Pago.deleted_at.is_(None),
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def update_status(
        self,
        pago_id: int,
        mp_status: str,
        mp_status_detail: Optional[str] = None,
        mp_payment_id: Optional[int] = None,
    ) -> Optional[Pago]:
        """
        Update payment status from webhook or API response.

        Args:
            pago_id: Payment ID to update
            mp_status: New MP status
            mp_status_detail: Optional detail from MP
            mp_payment_id: Optional MP payment ID

        Returns:
            Updated Pago or None if not found
        """
        from datetime import datetime, timezone

        update_data = {
            "mp_status": mp_status,
            "mp_status_detail": mp_status_detail,
        }
        if mp_payment_id:
            update_data["mp_payment_id"] = mp_payment_id

        return await self.update(pago_id, update_data)

    async def create_with_idempotency(
        self,
        pedido_id: int,
        external_reference: str,
        idempotency_key: str,
        monto: float,
    ) -> Pago:
        """
        Create payment record with idempotency key before calling MP API.

        This ensures we have a record even if the API call fails,
        and prevents duplicate charges.

        Args:
            pedido_id: Order ID
            external_reference: UUID for MP reference
            idempotency_key: Unique key for idempotency
            monto: Payment amount

        Returns:
            Created Pago instance
        """
        pago = Pago(
            pedido_id=pedido_id,
            external_reference=external_reference,
            idempotency_key=idempotency_key,
            monto=monto,
            mp_status="pending",
        )
        return await self.create(pago)
