"""DireccionRepository — repository for delivery addresses with ownership and default address support"""

import logging
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import and_, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.direccion_entrega import DireccionEntrega
from app.repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class DireccionRepository(BaseRepository[DireccionEntrega]):
    """
    Repository for DireccionEntrega with ownership and default address support.

    Inherits from BaseRepository:
    - find(id) → Optional[DireccionEntrega] (excluye soft-deleted)
    - list_all(skip, limit, filters, order_by) → tuple[list, total]
    - count(filters) → int
    - create(obj) → DireccionEntrega
    - update(id, data) → Optional[DireccionEntrega]
    - soft_delete(id) → Optional[DireccionEntrega]
    """

    def __init__(self, session: AsyncSession):
        """Initialize repository with session and DireccionEntrega model."""
        super().__init__(session, DireccionEntrega)

    async def find_by_usuario(
        self, usuario_id: int, skip: int = 0, limit: int = 100
    ) -> tuple[List[DireccionEntrega], int]:
        """
        List active addresses for a user, ordered by created_at DESC.

        Args:
            usuario_id: Owner user ID
            skip: Pagination offset
            limit: Page size

        Returns:
            Tuple of (addresses list, total count)
        """
        return await self.list_all(
            skip=skip,
            limit=limit,
            filters={"usuario_id": usuario_id},
            order_by=DireccionEntrega.created_at.desc(),
        )

    async def find_user_direccion(
        self, direccion_id: int, usuario_id: int
    ) -> Optional[DireccionEntrega]:
        """
        Find a single address with ownership and active check.

        SELECT * FROM direcciones_entrega
        WHERE id = :direccion_id
          AND usuario_id = :usuario_id
          AND deleted_at IS NULL

        Args:
            direccion_id: Address ID
            usuario_id: Owner user ID

        Returns:
            DireccionEntrega or None if not found, not owned, or soft-deleted
        """
        query = select(DireccionEntrega).where(
            and_(
                DireccionEntrega.id == direccion_id,
                DireccionEntrega.usuario_id == usuario_id,
                DireccionEntrega.deleted_at.is_(None),
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def find_principal(self, usuario_id: int) -> Optional[DireccionEntrega]:
        """
        Find the current default address for a user.

        SELECT * FROM direcciones_entrega
        WHERE usuario_id = :usuario_id
          AND es_principal = true
          AND deleted_at IS NULL

        Args:
            usuario_id: Owner user ID

        Returns:
            Default DireccionEntrega or None
        """
        query = select(DireccionEntrega).where(
            and_(
                DireccionEntrega.usuario_id == usuario_id,
                DireccionEntrega.es_principal == True,
                DireccionEntrega.deleted_at.is_(None),
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def count_by_usuario(self, usuario_id: int) -> int:
        """
        Count active addresses for a user.

        Args:
            usuario_id: Owner user ID

        Returns:
            Count of active addresses
        """
        return await self.count(filters={"usuario_id": usuario_id})

    async def unset_previous_default(self, usuario_id: int) -> None:
        """
        Unset es_principal for the current default address.

        UPDATE direcciones_entrega
        SET es_principal = false
        WHERE usuario_id = :usuario_id
          AND es_principal = true
          AND deleted_at IS NULL

        Args:
            usuario_id: Owner user ID
        """
        stmt = (
            update(DireccionEntrega)
            .where(
                and_(
                    DireccionEntrega.usuario_id == usuario_id,
                    DireccionEntrega.es_principal == True,
                    DireccionEntrega.deleted_at.is_(None),
                )
            )
            .values(
                es_principal=False,
                updated_at=datetime.now(timezone.utc),
            )
        )
        await self.session.execute(stmt)

    async def set_es_principal(self, direccion_id: int, value: bool) -> None:
        """
        Set es_principal for a specific address.

        UPDATE direcciones_entrega
        SET es_principal = :value
        WHERE id = :direccion_id AND deleted_at IS NULL

        Args:
            direccion_id: Address ID
            value: True to set as default, False to unset
        """
        stmt = (
            update(DireccionEntrega)
            .where(
                and_(
                    DireccionEntrega.id == direccion_id,
                    DireccionEntrega.deleted_at.is_(None),
                )
            )
            .values(
                es_principal=value,
                updated_at=datetime.now(timezone.utc),
            )
        )
        await self.session.execute(stmt)

    async def find_most_recent_active(
        self, usuario_id: int, exclude_id: Optional[int] = None
    ) -> Optional[DireccionEntrega]:
        """
        Find the most recently created active address for a user.
        Used when reassigning default after deleting the current default.

        SELECT * FROM direcciones_entrega
        WHERE usuario_id = :usuario_id
          AND deleted_at IS NULL
          AND id != :exclude_id
        ORDER BY created_at DESC
        LIMIT 1

        Args:
            usuario_id: Owner user ID
            exclude_id: Address ID to exclude (e.g. the one being deleted)

        Returns:
            Most recent active DireccionEntrega or None
        """
        conditions = [
            DireccionEntrega.usuario_id == usuario_id,
            DireccionEntrega.deleted_at.is_(None),
        ]
        if exclude_id is not None:
            conditions.append(DireccionEntrega.id != exclude_id)

        query = (
            select(DireccionEntrega)
            .where(and_(*conditions))
            .order_by(DireccionEntrega.created_at.desc())
            .limit(1)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
