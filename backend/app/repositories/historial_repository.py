"""HistorialEstadoPedidoRepository — APPEND-ONLY repository for order state audit trail.

This repository intentionally exposes ONLY find() and create() methods.
NO update() or delete() methods are implemented.
This enforces the append-only semantics (RN-03) at the repository layer.
"""

import logging
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.pedido import HistorialEstadoPedido
from app.repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class HistorialEstadoPedidoRepository(BaseRepository[HistorialEstadoPedido]):
    """
    Repository for order state history audit trail.

    IMPORTANT: This repository is APPEND-ONLY.
    Only find() and create() are implemented.
    update() and delete() are intentionally NOT implemented.

    Business rule enforced:
    - RN-03: HistorialEstadoPedido is append-only. No UPDATE or DELETE.

    Methods:
    - find(): get by ID (excluded soft-deleted — not applicable here)
    - list_by_pedido(): get history for an order ordered by created_at ASC
    - create(): add new history record
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session, HistorialEstadoPedido)

    async def list_by_pedido(self, pedido_id: int) -> List[HistorialEstadoPedido]:
        """
        Get state transition history for an order ordered by created_at ASC.

        Args:
            pedido_id: Order ID

        Returns:
            List of HistorialEstadoPedido records ordered chronologically
        """
        query = (
            select(HistorialEstadoPedido)
            .where(HistorialEstadoPedido.pedido_id == pedido_id)
            .order_by(HistorialEstadoPedido.created_at.asc())
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())
