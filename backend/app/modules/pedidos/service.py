"""Business logic service for Pedido creation and retrieval with atomic UoW semantics"""
import logging
from typing import Optional, List, Tuple
from decimal import Decimal
from fastapi import HTTPException
from sqlalchemy import select

from app.uow import UnitOfWork
from app.models.pedido import Pedido, DetallePedido, HistorialEstadoPedido
from app.models.usuario import Usuario
from app.modules.pedidos.schemas import (
    CrearPedidoRequest,
    PedidoRead,
    PedidoDetail,
    DetallePedidoRead,
    HistorialEstadoPedidoRead,
)

logger = logging.getLogger(__name__)


class StockInsufficientError(HTTPException):
    """Raised when product stock is insufficient for the requested quantity."""

    def __init__(self, producto_id: int, solicitado: int, disponible: int):
        detail = (
            f"Stock insuficiente para producto ID {producto_id}: "
            f"solicitado {solicitado}, disponible {disponible}"
        )
        super().__init__(
            status_code=422,
            detail=detail,
        )


class PaymentMethodNotFoundError(HTTPException):
    """Raised when payment method code is invalid or disabled."""

    def __init__(self, codigo: str):
        detail = f"Forma de pago '{codigo}' no existe o esta deshabilitada"
        super().__init__(
            status_code=422,
            detail=detail,
        )


class PedidoService:
    """
    Service layer for order operations.

    Stateless. Receives UnitOfWork via constructor.
    Does NOT call session.commit() — the UoW context manager handles it.

    Atomic UoW flow for crear_pedido:
    1. Validate address ownership (404 if not found or not owned)
    2. Validate payment method (422 if invalid or disabled)
    3. Validate stock with SELECT FOR UPDATE per item (422 if insufficient)
    4. Calculate totals (subtotal + costo_envio)
    5. Create Pedido
    6. Create DetallePedido for each item (with snapshots)
    7. Create HistorialEstadoPedido initial record (estado_desde=NULL)
    8. UoW.__aexit__ commits if no exception, otherwise rolls back
    """

    COSTO_ENVIO_DEFAULT = Decimal("50.00")
    ESTADO_INICIAL = "PENDIENTE"

    def __init__(self, uow: UnitOfWork):
        """
        Initialize service with UnitOfWork.

        Args:
            uow: UnitOfWork instance with active database session
        """
        self.uow = uow

    async def crear_pedido(
        self,
        usuario_id: int,
        body: CrearPedidoRequest,
    ) -> Pedido:
        """
        Create an order atomically using Unit of Work.
        # ... (docstrings originales) ...
        """
        # ¡AQUÍ ESTÁ LA MAGIA! Abrimos el bloque del Unit of Work
        async with self.uow:
            await self._validar_direccion(usuario_id, body.direccion_id)

            await self._validar_forma_pago(body.forma_pago_codigo)

            items_validados = await self._validar_stock_items(body.items)

            subtotal = self._calcular_subtotal(items_validados)
            total = subtotal + self.COSTO_ENVIO_DEFAULT

            pedido = await self._crear_pedido_record(
                usuario_id=usuario_id,
                body=body,
                total=total,
            )

            await self._crear_detalles_pedido(pedido.id, items_validados)

            await self._crear_historial_inicial(pedido.id, usuario_id)

            logger.info(
                f"Pedido {pedido.id} created for usuario {usuario_id} "
                f"with total={total}, items={len(items_validados)}"
            )
            return pedido

    async def listar_pedidos(
        self,
        usuario_id: int,
        roles: List[str],
        skip: int,
        limit: int,
    ) -> Tuple[List[Pedido], int]:
        """
        List orders filtered by role.

        CLIENT role: only own orders
        ADMIN/PEDIDOS roles: all orders

        Args:
            usuario_id: Current user ID
            roles: List of role names for the current user
            skip: Pagination offset
            limit: Max results per page

        Returns:
            Tuple of (list of Pedido, total count)
        """
        if "CLIENT" in roles:
            return await self.uow.pedidos.get_for_user(usuario_id, skip, limit)
        return await self.uow.pedidos.get_all_paginated(skip, limit)

    async def obtener_detalle(
        self,
        pedido_id: int,
        usuario_id: int,
        roles: List[str],
    ) -> Optional[Pedido]:
        """
        Get order detail if user has access.

        CLIENT: only own orders
        ADMIN/PEDIDOS: any order

        Args:
            pedido_id: Order ID
            usuario_id: Current user ID
            roles: List of role names

        Returns:
            Pedido with detalles and historial loaded, or None if not found/not owned
        """
        pedido = await self.uow.pedidos.get_detail(pedido_id)
        if pedido is None or pedido.deleted_at is not None:
            return None
        if "CLIENT" in roles and pedido.usuario_id != usuario_id:
            return None
        return pedido

    async def obtener_historial(
        self, pedido_id: int
    ) -> List[HistorialEstadoPedido]:
        """
        Get state transition history for an order.

        Args:
            pedido_id: Order ID

        Returns:
            List of HistorialEstadoPedido ordered by created_at ASC
        """
        return await self.uow.historial_pedido.list_by_pedido(pedido_id)

    # ── Internal helpers ────────────────────────────────────────────────────────

    async def _validar_direccion(
        self, usuario_id: int, direccion_id: Optional[int]
    ) -> None:
        """
        Validate that the address exists, is active, and belongs to the user.

        Raises:
            HTTPException 404: Address not found, soft-deleted, or not owned
        """
        if direccion_id is None:
            return

        from app.models.direccion_entrega import DireccionEntrega
        query = select(DireccionEntrega).where(
            DireccionEntrega.id == direccion_id,
            DireccionEntrega.deleted_at.is_(None),
        )
        result = await self.uow.session.execute(query)
        direccion = result.scalar_one_or_none()

        if direccion is None:
            raise HTTPException(
                status_code=404,
                detail="Direccion no encontrada",
            )
        if direccion.usuario_id != usuario_id:
            raise HTTPException(
                status_code=404,
                detail="Direccion no encontrada",
            )

    async def _validar_forma_pago(self, forma_pago_codigo: str) -> None:
        """
        Validate that the payment method exists and is enabled.

        Raises:
            PaymentMethodNotFoundError: Payment method invalid or disabled
        """
        from app.models.forma_pago import FormaPago
        query = select(FormaPago).where(FormaPago.codigo == forma_pago_codigo)
        result = await self.uow.session.execute(query)
        forma_pago = result.scalar_one_or_none()

        if forma_pago is None or not forma_pago.habilitado:
            raise PaymentMethodNotFoundError(forma_pago_codigo)

    async def _validar_stock_items(
        self, items: List
    ) -> List[Tuple]:
        """
        Validate stock for all items using SELECT FOR UPDATE.

        Each product row is locked during validation to prevent race conditions.

        Raises:
            HTTPException 422: Product not found, not available, or insufficient stock
        """
        items_validados = []
        for item in items:
            producto = await self.uow.productos.get_for_update(item.producto_id)

            if producto is None or producto.deleted_at is not None:
                raise HTTPException(
                    status_code=422,
                    detail=f"Producto ID {item.producto_id} no encontrado",
                )
            if not producto.disponible:
                raise HTTPException(
                    status_code=422,
                    detail=f"Producto '{producto.nombre}' no esta disponible",
                )
            if producto.stock_cantidad < item.cantidad:
                raise StockInsufficientError(
                    producto_id=item.producto_id,
                    solicitado=item.cantidad,
                    disponible=producto.stock_cantidad,
                )
            items_validados.append((item, producto))
        return items_validados

    def _calcular_subtotal(self, items_validados: List[Tuple]) -> Decimal:
        """
        Calculate order subtotal from validated items.

        Args:
            items_validados: List of (ItemPedidoRequest, Producto) tuples

        Returns:
            Subtotal as Decimal
        """
        subtotal = Decimal("0.00")
        for item, producto in items_validados:
            subtotal += producto.precio_base * item.cantidad
        return subtotal

    async def _crear_pedido_record(
        self,
        usuario_id: int,
        body: CrearPedidoRequest,
        total: Decimal,
    ) -> Pedido:
        """
        Create the Pedido record and flush to get the ID.

        Args:
            usuario_id: Owner user ID
            body: Original request
            total: Calculated total (subtotal + costo_envio)

        Returns:
            Created Pedido with ID assigned
        """
        pedido = Pedido(
            usuario_id=usuario_id,
            estado_codigo=self.ESTADO_INICIAL,
            total=total,
            costo_envio=self.COSTO_ENVIO_DEFAULT,
            forma_pago_codigo=body.forma_pago_codigo,
            direccion_id=body.direccion_id,
            notas=body.notas,
        )
        self.uow.session.add(pedido)
        await self.uow.session.flush()
        await self.uow.session.refresh(pedido)
        return pedido

    async def _crear_detalles_pedido(
        self, pedido_id: int, items_validados: List[Tuple]
    ) -> None:
        """
        Create DetallePedido records for each item with snapshots.

        RN-04: Captures nombre and precio at this moment.
        These values are immutable even if the product changes later.

        Args:
            pedido_id: Parent order ID
            items_validados: List of (ItemPedidoRequest, Producto) tuples
        """
        for item, producto in items_validados:
            detalle = DetallePedido(
                pedido_id=pedido_id,
                producto_id=producto.id,
                nombre_snapshot=producto.nombre,
                precio_snapshot=producto.precio_base,
                cantidad=item.cantidad,
                personalizacion=item.personalizacion,
            )
            self.uow.session.add(detalle)

    async def _crear_historial_inicial(
        self, pedido_id: int, usuario_id: int
    ) -> None:
        """
        Create the initial HistorialEstadoPedido record with estado_desde=NULL.

        RN-02: The first history record always has estado_desde = NULL.
        This marks the creation transition from "nothing" to PENDIENTE.

        Args:
            pedido_id: Parent order ID
            usuario_id: User who created the order
        """
        historial = HistorialEstadoPedido(
            pedido_id=pedido_id,
            estado_desde=None,
            estado_hacia=self.ESTADO_INICIAL,
            usuario_id=usuario_id,
        )
        self.uow.session.add(historial)
