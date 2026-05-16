"""Repository pattern implementation for data access"""

from app.repositories.base import BaseRepository
from app.repositories.historial_repository import HistorialEstadoPedidoRepository
from app.repositories.pedido_repository import DetallePedidoRepository, PedidoRepository
from app.repositories.producto_repository import ProductoRepository

__all__ = [
    "BaseRepository",
    "ProductoRepository",
    "PedidoRepository",
    "DetallePedidoRepository",
    "HistorialEstadoPedidoRepository",
]
