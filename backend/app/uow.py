"""Unit of Work pattern implementation for atomic transactions"""

import logging
from typing import Type, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.base import BaseRepository
from app.repositories.categoria_repository import CategoriaRepository
from app.repositories.direccion_repository import DireccionRepository

logger = logging.getLogger(__name__)


class UnitOfWork:
    """
    Unit of Work pattern - manages atomic transactions across multiple repositories.
    Ensures all-or-nothing semantics: either all changes commit or all rollback.
    """
    
    def __init__(self, session: AsyncSession):
        """
        Initialize Unit of Work with database session
        
        Args:
            session: AsyncSession instance for database operations
        """
        self.session = session
        self._repositories: dict[Type, BaseRepository] = {}
        self._categorias: Optional[CategoriaRepository] = None
        self._direcciones: Optional[DireccionRepository] = None
        self.logger = logging.getLogger(f"{__name__}.UnitOfWork")
    
    def get_repository(self, model: Type) -> BaseRepository:
        """
        Get or create a repository for the given model
        
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
        """
        Get or create CategoriaRepository instance.
        
        Returns:
            CategoriaRepository for managing categories
        """
        if self._categorias is None:
            self._categorias = CategoriaRepository(self.session)
        return self._categorias

    @property
    def direcciones(self) -> DireccionRepository:
        """
        Get or create DireccionRepository instance.
        
        Returns:
            DireccionRepository for managing delivery addresses
        """
        if self._direcciones is None:
            self._direcciones = DireccionRepository(self.session)
        return self._direcciones
    
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
        Exit context manager - handles commit/rollback based on exceptions
        
        Args:
            exc_type: Exception type if any occurred
            exc_val: Exception value if any occurred
            exc_tb: Exception traceback if any occurred
        """
        if exc_type is not None:
            # An exception occurred, rollback the transaction
            await self.rollback()
            self.logger.warning(
                f"UnitOfWork: Exception occurred, automatic rollback triggered. "
                f"Error: {exc_type.__name__}: {exc_val}"
            )
        else:
            # No exception, commit the transaction
            try:
                await self.commit()
            except Exception as e:
                self.logger.error(f"UnitOfWork: Error during commit: {str(e)}")
                raise
        
        # Close session
        await self.session.close()
    
    def __repr__(self) -> str:
        return f"<UnitOfWork session={id(self.session)}, repositories={len(self._repositories)}>"
