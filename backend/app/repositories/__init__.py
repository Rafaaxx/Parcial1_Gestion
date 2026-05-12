"""Repository pattern implementation for data access"""

from app.repositories.base import BaseRepository
from app.repositories.producto_repository import ProductoRepository

__all__ = ["BaseRepository", "ProductoRepository"]
