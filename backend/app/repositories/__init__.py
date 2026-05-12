"""Repository pattern implementation for data access"""

from app.repositories.base import BaseRepository
from app.repositories.producto_repository import ProductoRepository
from app.repositories.pedido_repository import PedidoRepository, DetallePedidoRepository
from app.repositories.historial_repository import HistorialEstadoPedidoRepository

__all__ = [
    "BaseRepository",
    "ProductoRepository",
    "PedidoRepository",
    "DetallePedidoRepository",
    "HistorialEstadoPedidoRepository",
]
