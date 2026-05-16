"""Pedido module — order creation with Unit of Work atomicity"""

from app.modules.pedidos.fsm import EstadoPedido, es_estado_terminal, is_valid_state
from app.modules.pedidos.schemas import (
    AvanzarEstadoRequest,
    CrearPedidoRequest,
    DetallePedidoRead,
    HistorialEstadoPedidoRead,
    ItemPedidoRequest,
    PedidoDetail,
    PedidoListResponse,
    PedidoRead,
    TransicionResponse,
)
from app.modules.pedidos.service import (
    PaymentMethodNotFoundError,
    PedidoService,
    StockInsufficientError,
)

__all__ = [
    "CrearPedidoRequest",
    "ItemPedidoRequest",
    "DetallePedidoRead",
    "HistorialEstadoPedidoRead",
    "PedidoRead",
    "PedidoDetail",
    "PedidoListResponse",
    "AvanzarEstadoRequest",
    "TransicionResponse",
    "PedidoService",
    "StockInsufficientError",
    "PaymentMethodNotFoundError",
    "EstadoPedido",
    "es_estado_terminal",
    "is_valid_state",
]
