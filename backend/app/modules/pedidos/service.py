"""Business logic service for Pedido creation and retrieval with atomic UoW semantics"""
import logging
from typing import Optional, List, Tuple
from decimal import Decimal
from fastapi import HTTPException
from sqlalchemy import select

from app.uow import UnitOfWork
from app.models.pedido import Pedido, DetallePedido, HistorialEstadoPedido
from app.models.usuario import Usuario
from app.models.producto import Producto
from app.modules.pedidos.schemas import (
    CrearPedidoRequest,
    PedidoRead,
    PedidoDetail,
    DetallePedidoRead,
    HistorialEstadoPedidoRead,
)
from app.modules.pedidos.fsm import (
    FSM_TRANSITION_MAP,
    Transition,
    es_estado_terminal,
    is_valid_state,
    get_valid_transitions,
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

    # ── FSM State Transition Methods ─────────────────────────────────────────────

    async def transicionar_estado(
        self,
        pedido_id: int,
        nuevo_estado: str,
        usuario_id: int,
        roles: List[str],
        motivo: Optional[str] = None,
    ) -> Pedido:
        """
        Transition an order to a new state following FSM rules.

        Args:
            pedido_id: Order ID to transition
            nuevo_estado: Target state code
            usuario_id: User triggering the transition
            roles: List of user roles
            motivo: Optional explanation (required for CANCELADO)

        Returns:
            Updated Pedido with new state

        Raises:
            HTTPException 404: Order not found
            HTTPException 422: Invalid transition
            HTTPException 403: Role not allowed
        """
        async with self.uow:
            # Get current order
            pedido = await self.uow.pedidos.find(pedido_id)
            if pedido is None or pedido.deleted_at is not None:
                raise HTTPException(
                    status_code=404,
                    detail="Pedido no encontrado",
                )

            # Validate transition
            is_valid, error_msg = self._validar_transicion(
                estado_actual=pedido.estado_codigo,
                nuevo_estado=nuevo_estado,
                roles=roles,
                motivo=motivo,
            )
            if not is_valid:
                raise HTTPException(
                    status_code=422,
                    detail=error_msg,
                )

            # Handle stock operations
            if nuevo_estado == "CONFIRMADO":
                await self._decrementar_stock_en_pedido(pedido_id)
            elif nuevo_estado == "CANCELADO" and pedido.estado_codigo in ("CONFIRMADO", "EN_PREP"):
                await self._restaurar_stock_en_pedido(pedido_id)

            # Update order state
            old_estado = pedido.estado_codigo
            pedido.estado_codigo = nuevo_estado

            # Create history record
            historial = HistorialEstadoPedido(
                pedido_id=pedido_id,
                estado_desde=old_estado,
                estado_hacia=nuevo_estado,
                observacion=motivo,
                usuario_id=usuario_id,
            )
            self.uow.session.add(historial)

            logger.info(
                f"Pedido {pedido_id} transitioned from {old_estado} to {nuevo_estado} "
                f"by user {usuario_id}"
            )
            return pedido

    def _validar_transicion(
        self,
        estado_actual: str,
        nuevo_estado: str,
        roles: List[str],
        motivo: Optional[str] = None,
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate if a state transition is allowed.

        Args:
            estado_actual: Current state code
            nuevo_estado: Target state code
            roles: User roles
            motivo: Optional explanation for CANCELADO

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check if current state exists in FSM
        if not is_valid_state(estado_actual):
            return False, f"Estado actual inválido: {estado_actual}"

        # Check if target state exists
        if not is_valid_state(nuevo_estado):
            return False, f"Estado destino inválido: {nuevo_estado}"

        # Check terminal state (FSM-TRANS-02)
        if es_estado_terminal(estado_actual):
            return False, f"Estado terminal '{estado_actual}': no se permiten transiciones"

        # Get valid transitions for current state
        valid_transitions = get_valid_transitions(estado_actual)

        # Find matching transition
        matching_transition: Optional[Transition] = None
        for transition in valid_transitions:
            if transition.target == nuevo_estado:
                matching_transition = transition
                break

        if matching_transition is None:
            return False, f"Transición no válida: {estado_actual} → {nuevo_estado}"

        # Check role permissions (FSM-TRANS-03)
        role_set = set(roles)
        allowed_set = set(matching_transition.allowed_roles)
        if not role_set.intersection(allowed_set):
            return False, "No tienes permisos para esta transición"

        # Check motivo requirement for CANCELADO
        if matching_transition.requires_motivo and not motivo:
            return False, "El motivo es obligatorio para cancelar"

        return True, None

    def _es_estado_terminal(self, estado: str) -> bool:
        """
        Check if a state is terminal (ENTREGADO or CANCELADO).

        Args:
            estado: State code to check

        Returns:
            True if terminal, False otherwise
        """
        return es_estado_terminal(estado)

    async def _decrementar_stock_en_pedido(self, pedido_id: int) -> None:
        """
        Decrement stock for all items in an order using SELECT FOR UPDATE.

        Called when transitioning to CONFIRMADO state.
        Uses SELECT FOR UPDATE to prevent race conditions.

        Args:
            pedido_id: Order ID to decrement stock for

        Raises:
            HTTPException 422: If insufficient stock
        """
        # Get all details with product lock
        detalles = await self.uow.detalles_pedido.list_by_pedido(pedido_id)

        for detalle in detalles:
            producto = await self.uow.productos.get_for_update(detalle.producto_id)
            if producto is None:
                raise HTTPException(
                    status_code=422,
                    detail=f"Producto ID {detalle.producto_id} no encontrado",
                )

            # Check stock availability
            if producto.stock_cantidad < detalle.cantidad:
                raise HTTPException(
                    status_code=422,
                    detail=(
                        f"Stock insuficiente para producto '{producto.nombre}': "
                        f"solicitado {detalle.cantidad}, disponible {producto.stock_cantidad}"
                    ),
                )

            # Decrement stock
            producto.stock_cantidad -= detalle.cantidad
            logger.info(
                f"Decremented stock for producto {producto.id} by {detalle.cantidad}, "
                f"new stock: {producto.stock_cantidad}"
            )

    async def _restaurar_stock_en_pedido(self, pedido_id: int) -> None:
        """
        Restore stock for all items in an order.

        Called when transitioning to CANCELADO from CONFIRMADO or EN_PREP.
        No-op for PENDIENTE → CANCELADO (stock never decremented).

        Args:
            pedido_id: Order ID to restore stock for
        """
        # Get all details
        detalles = await self.uow.detalles_pedido.list_by_pedido(pedido_id)

        for detalle in detalles:
            producto = await self.uow.productos.get_for_update(detalle.producto_id)
            if producto is None:
                logger.warning(
                    f"Producto ID {detalle.producto_id} not found when restoring stock "
                    f"for pedido {pedido_id}"
                )
                continue

            # Restore stock
            producto.stock_cantidad += detalle.cantidad
            logger.info(
                f"Restored stock for producto {producto.id} by {detalle.cantidad}, "
                f"new stock: {producto.stock_cantidad}"
            )
