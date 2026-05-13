"""PedidoRepository — repository for Pedido model with user-scoped and admin queries"""
import logging
from typing import Optional, List, Tuple, Dict, Any
from datetime import datetime
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from app.models.pedido import Pedido, DetallePedido, HistorialEstadoPedido
from app.models.usuario import Usuario
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

    async def get_for_user_with_filters(
        self,
        usuario_id: int,
        skip: int = 0,
        limit: int = 20,
        filtros: Optional[Dict[str, Any]] = None,
    ) -> Tuple[List[Pedido], int]:
        """
        Get orders for a specific user with optional filters.

        Args:
            usuario_id: ID of the user who owns the orders
            skip: Pagination offset
            limit: Max results per page
            filtros: Optional dict with estado, desde, hasta, busqueda

        Returns:
            Tuple of (list of Pedido with joined user, total count)
        """
        filtros = filtros or {}
        
        # Build base query with user join
        conditions = [
            Pedido.usuario_id == usuario_id,
            Pedido.deleted_at.is_(None),
        ]
        
        # Apply filters
        if filtros.get("estado"):
            conditions.append(Pedido.estado_codigo == filtros["estado"])
        
        if filtros.get("desde"):
            try:
                desde_date = datetime.strptime(filtros["desde"], "%Y-%m-%d")
                conditions.append(Pedido.created_at >= desde_date)
            except ValueError:
                logger.warning(f"Invalid desde date format: {filtros['desde']}")
        
        if filtros.get("hasta"):
            try:
                hasta_date = datetime.strptime(filtros["hasta"], "%Y-%m-%d")
                # Include the entire day
                hasta_date = hasta_date.replace(hour=23, minute=59, second=59)
                conditions.append(Pedido.created_at <= hasta_date)
            except ValueError:
                logger.warning(f"Invalid hasta date format: {filtros['hasta']}")
        
        query = (
            select(Pedido)
            .join(Usuario, Pedido.usuario_id == Usuario.id)
            .options(joinedload(Pedido.usuario))
            .where(and_(*conditions))
            .order_by(Pedido.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(query)
        pedidos = list(result.scalars().unique().all())

        # Count query with filters
        count_conditions = [
            Pedido.usuario_id == usuario_id,
            Pedido.deleted_at.is_(None),
        ]
        if filtros.get("estado"):
            count_conditions.append(Pedido.estado_codigo == filtros["estado"])
        
        count_query = (
            select(func.count())
            .select_from(Pedido)
            .where(and_(*count_conditions))
        )
        count_result = await self.session.execute(count_query)
        total = count_result.scalar() or 0

        return pedidos, total

    async def get_all_with_filters(
        self,
        skip: int = 0,
        limit: int = 20,
        filtros: Optional[Dict[str, Any]] = None,
    ) -> Tuple[List[Pedido], int]:
        """
        Get all orders with optional filters (ADMIN/PEDIDOS roles).

        Args:
            skip: Pagination offset
            limit: Max results per page
            filtros: Optional dict with estado, desde, hasta, busqueda

        Returns:
            Tuple of (list of Pedido with joined user, total count)
        """
        filtros = filtros or {}
        
        # Build conditions
        conditions = [Pedido.deleted_at.is_(None)]
        
        # Apply filters
        if filtros.get("estado"):
            conditions.append(Pedido.estado_codigo == filtros["estado"])
        
        if filtros.get("desde"):
            try:
                desde_date = datetime.strptime(filtros["desde"], "%Y-%m-%d")
                conditions.append(Pedido.created_at >= desde_date)
            except ValueError:
                logger.warning(f"Invalid desde date format: {filtros['desde']}")
        
        if filtros.get("hasta"):
            try:
                hasta_date = datetime.strptime(filtros["hasta"], "%Y-%m-%d")
                hasta_date = hasta_date.replace(hour=23, minute=59, second=59)
                conditions.append(Pedido.created_at <= hasta_date)
            except ValueError:
                logger.warning(f"Invalid hasta date format: {filtros['hasta']}")
        
        # Search by order ID or customer name/email
        busqueda = filtros.get("busqueda")
        if busqueda:
            conditions.append(
                or_(
                    Pedido.id == int(busqueda) if busqueda.isdigit() else False,
                    Usuario.nombre.ilike(f"%{busqueda}%"),
                    Usuario.apellido.ilike(f"%{busqueda}%"),
                    Usuario.email.ilike(f"%{busqueda}%"),
                )
            )
        
        query = (
            select(Pedido)
            .join(Usuario, Pedido.usuario_id == Usuario.id)
            .options(joinedload(Pedido.usuario))
            .where(and_(*conditions))
            .order_by(Pedido.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(query)
        pedidos = list(result.scalars().unique().all())

        # Count query with filters
        count_query = (
            select(func.count())
            .select_from(Pedido)
            .join(Usuario, Pedido.usuario_id == Usuario.id)
            .where(and_(*conditions))
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
