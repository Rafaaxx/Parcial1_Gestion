"""PedidoRepository — repository for Pedido model with user-scoped and admin queries"""
import logging
from typing import Optional, List, Tuple
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.pedido import Pedido, DetallePedido, HistorialEstadoPedido
from app.repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class PedidoRepository(BaseRepository[Pedido]):
    """
    Repository for Pedido with custom queries.

    Methods:
    - get_for_user(): orders owned by a specific user (CLIENT role)
    - get_all_paginated(): all orders (ADMIN/PEDIDOS roles)
    - get_detail(): order with detalles and historial eagerly loaded
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session, Pedido)

    async def get_for_user(
        self, usuario_id: int, skip: int = 0, limit: int = 20
    ) -> Tuple[List[Pedido], int]:
        """
        Get orders for a specific user (CLIENT role).

        Args:
            usuario_id: ID of the user who owns the orders
            skip: Pagination offset
            limit: Max results per page

        Returns:
            Tuple of (list of Pedido, total count)
        """
        query = (
            select(Pedido)
            .where(Pedido.usuario_id == usuario_id)
            .where(Pedido.deleted_at.is_(None))
            .order_by(Pedido.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(query)
        pedidos = list(result.scalars().all())

        # Count total for pagination
        count_query = (
            select(func.count())
            .select_from(Pedido)
            .where(Pedido.usuario_id == usuario_id)
            .where(Pedido.deleted_at.is_(None))
        )
        count_result = await self.session.execute(count_query)
        total = count_result.scalar() or 0

        return pedidos, total

    async def get_all_paginated(
        self, skip: int = 0, limit: int = 20
    ) -> Tuple[List[Pedido], int]:
        """
        Get all orders (ADMIN/PEDIDOS roles).

        Args:
            skip: Pagination offset
            limit: Max results per page

        Returns:
            Tuple of (list of Pedido, total count)
        """
        query = (
            select(Pedido)
            .where(Pedido.deleted_at.is_(None))
            .order_by(Pedido.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(query)
        pedidos = list(result.scalars().all())

        count_query = (
            select(func.count())
            .select_from(Pedido)
            .where(Pedido.deleted_at.is_(None))
        )
        count_result = await self.session.execute(count_query)
        total = count_result.scalar() or 0

        return pedidos, total

    async def get_detail(self, pedido_id: int) -> Optional[Pedido]:
        """
        Get order with detalles and historial eagerly loaded.

        Args:
            pedido_id: Order ID

        Returns:
            Pedido with relaciones cargadas, or None if not found
        """
        query = (
            select(Pedido)
            .options(
                selectinload(Pedido.detalles),
                selectinload(Pedido.historial),
            )
            .where(Pedido.id == pedido_id)
            .where(Pedido.deleted_at.is_(None))
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()


class DetallePedidoRepository(BaseRepository[DetallePedido]):
    """
    Repository for order line items (DetallePedido).

    Methods:
    - list_by_pedido(): all line items for an order
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session, DetallePedido)

    async def list_by_pedido(self, pedido_id: int) -> List[DetallePedido]:
        """
        Get all line items for an order.

        Args:
            pedido_id: Order ID

        Returns:
            List of DetallePedido ordered by id
        """
        query = (
            select(DetallePedido)
            .where(DetallePedido.pedido_id == pedido_id)
            .order_by(DetallePedido.id)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())
