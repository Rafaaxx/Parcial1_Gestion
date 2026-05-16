"""Unit of Work pattern implementation for atomic transactions"""

import logging
from typing import Optional, Type

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.base import BaseRepository
from app.repositories.categoria_repository import CategoriaRepository
from app.repositories.direccion_repository import DireccionRepository
from app.repositories.historial_repository import HistorialEstadoPedidoRepository
from app.repositories.pedido_repository import DetallePedidoRepository, PedidoRepository
from app.repositories.producto_repository import ProductoRepository

logger = logging.getLogger(__name__)


class UnitOfWork:
    """
    Unit of Work pattern - manages atomic transactions across multiple repositories.
    Ensures all-or-nothing semantics: either all changes commit or all rollback.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize Unit of Work with database session.

        Args:
            session: AsyncSession instance for database operations
        """
        self.session = session
        self._repositories: dict[Type, BaseRepository] = {}
        self._categorias: Optional[CategoriaRepository] = None
        self._direcciones: Optional[DireccionRepository] = None
        self._productos: Optional[ProductoRepository] = None
        self._pedidos: Optional[PedidoRepository] = None
        self._detalles_pedido: Optional[DetallePedidoRepository] = None
        self._historial_pedido: Optional[HistorialEstadoPedidoRepository] = None
        self.logger = logging.getLogger(f"{__name__}.UnitOfWork")

    def get_repository(self, model: Type) -> BaseRepository:
        """
        Get or create a repository for the given model.

        Args:
            model: SQLModel type

        Returns:
            BaseRepository instance for the model
        """
        if model not in self._repositories:
            self._repositories[model] = BaseRepository(self.session, model)
        return self._repositories[model]

    @property
    def categorias(self) -> CategoriaRepository:
        """Get or create CategoriaRepository instance."""
        if self._categorias is None:
            self._categorias = CategoriaRepository(self.session)
        return self._categorias

    @property
    def direcciones(self) -> DireccionRepository:
        """Get or create DireccionRepository instance."""
        if self._direcciones is None:
            self._direcciones = DireccionRepository(self.session)
        return self._direcciones

    @property
    def productos(self) -> ProductoRepository:
        """Get or create ProductoRepository instance."""
        if self._productos is None:
            self._productos = ProductoRepository(self.session)
        return self._productos

    @property
    def pedidos(self) -> PedidoRepository:
        """Get or create PedidoRepository instance."""
        if self._pedidos is None:
            self._pedidos = PedidoRepository(self.session)
        return self._pedidos

    @property
    def detalles_pedido(self) -> DetallePedidoRepository:
        """Get or create DetallePedidoRepository instance."""
        if self._detalles_pedido is None:
            self._detalles_pedido = DetallePedidoRepository(self.session)
        return self._detalles_pedido

    @property
    def historial_pedido(self) -> HistorialEstadoPedidoRepository:
        """Get or create HistorialEstadoPedidoRepository instance."""
        if self._historial_pedido is None:
            self._historial_pedido = HistorialEstadoPedidoRepository(self.session)
        return self._historial_pedido

    async def commit(self):
        """Commit all changes in the current transaction"""
        try:
            await self.session.commit()
            self.logger.debug("UnitOfWork: Transaction committed")
        except Exception as e:
            await self.session.rollback()
            self.logger.error(f"UnitOfWork: Commit failed, rolling back: {str(e)}")
            raise

    async def rollback(self):
        """Rollback all changes in the current transaction"""
        try:
            await self.session.rollback()
            self.logger.debug("UnitOfWork: Transaction rolled back")
        except Exception as e:
            self.logger.error(f"UnitOfWork: Rollback failed: {str(e)}")
            raise

    async def __aenter__(self):
        """Enter context manager"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Exit context manager - handles commit/rollback based on exceptions.

        Args:
            exc_type: Exception type if any occurred
            exc_val: Exception value if any occurred
            exc_tb: Exception traceback if any occurred
        """
        if exc_type is not None:
            await self.rollback()
            self.logger.warning(
                f"UnitOfWork: Exception occurred, automatic rollback triggered. "
                f"Error: {exc_type.__name__}: {exc_val}"
            )
        else:
            try:
                await self.commit()
            except Exception as e:
                self.logger.error(f"UnitOfWork: Error during commit: {str(e)}")
                raise

        await self.session.close()

    def __repr__(self) -> str:
        return f"<UnitOfWork session={id(self.session)}, repositories={len(self._repositories)}>"
