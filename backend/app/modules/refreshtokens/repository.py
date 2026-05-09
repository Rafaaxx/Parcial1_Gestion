"""RefreshTokenRepository — custom repository for refresh token persistence.

Does NOT inherit from BaseRepository because RefreshToken does not use
SoftDeleteMixin. The queries use direct SELECT with no ``deleted_at`` filter.
"""
from typing import Optional
from datetime import datetime, timezone

from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.refreshtokens.model import RefreshToken


class RefreshTokenRepository:
    """Repository for RefreshToken persistence.

    Operates directly on the session without the BaseRepository generic
    since RefreshToken uses ``revoked_at`` (not ``deleted_at``) semantics.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, token: RefreshToken) -> RefreshToken:
        """Persist a new refresh token.

        Args:
            token: Unsaved RefreshToken instance.

        Returns:
            The same instance with generated id populated.
        """
        self.session.add(token)
        await self.session.flush()
        await self.session.refresh(token)
        return token

    async def find_by_hash(self, token_hash: str) -> Optional[RefreshToken]:
        """Find a refresh token by its SHA-256 hash.

        This is a direct query with no ``deleted_at`` filter —
        RefreshToken does not have SoftDeleteMixin.

        Args:
            token_hash: The SHA-256 hex digest to look up.

        Returns:
            RefreshToken instance or None if not found.
        """
        query = select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def revoke(self, token_id: int) -> None:
        """Mark a refresh token as revoked (sets revoked_at).

        Args:
            token_id: Primary key of the token to revoke.
        """
        now = datetime.now(timezone.utc)
        stmt = (
            update(RefreshToken)
            .where(RefreshToken.id == token_id)
            .values(revoked_at=now)
        )
        await self.session.execute(stmt)
        await self.session.flush()

    async def revoke_all_for_user(self, usuario_id: int) -> int:
        """Revoke all ACTIVE (not expired, not revoked) tokens for a user.

        Args:
            usuario_id: The user whose tokens should be revoked.

        Returns:
            Number of tokens revoked.
        """
        now = datetime.now(timezone.utc)
        # Count affected rows first
        count_stmt = select(func.count()).where(
            RefreshToken.usuario_id == usuario_id,
            RefreshToken.revoked_at.is_(None),
            RefreshToken.expires_at > now,
        )
        count_result = await self.session.execute(count_stmt)
        count = count_result.scalar() or 0

        # Revoke them
        stmt = (
            update(RefreshToken)
            .where(
                RefreshToken.usuario_id == usuario_id,
                RefreshToken.revoked_at.is_(None),
                RefreshToken.expires_at > now,
            )
            .values(revoked_at=now)
        )
        await self.session.execute(stmt)
        await self.session.flush()
        return count
