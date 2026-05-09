"""RefreshTokenService — stateless service for refresh token lifecycle.

This service encapsulates:
  - Token creation (UUID generation + SHA-256 hashing + persistence)
  - Token validation and rotation (detect replay attacks)
  - Token revocation (explicit logout)

It is stateless: all dependencies are received as arguments.
"""
from datetime import datetime, timedelta, timezone

from app.config import settings
from app.exceptions import UnauthorizedError
from app.security import generate_refresh_token, hash_refresh_token
from app.uow import UnitOfWork
from app.modules.refreshtokens.model import RefreshToken
from app.modules.refreshtokens.repository import RefreshTokenRepository


class RefreshTokenService:
    """Manages the lifecycle of refresh tokens."""

    @staticmethod
    async def create_token(usuario_id: int, uow: UnitOfWork) -> str:
        """Generate, persist, and return a new refresh token UUID.

        The raw UUID is returned (to give to the client). Only the SHA-256
        hash is stored in the database.

        Args:
            usuario_id: The user the token belongs to.
            uow: Active UnitOfWork for transactional persistence.

        Returns:
            The raw UUID string to return to the client.
        """
        repo = RefreshTokenRepository(uow.session)
        raw_token = generate_refresh_token()
        token_hash = hash_refresh_token(raw_token)

        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(days=settings.refresh_token_expire_days)

        token = RefreshToken(
            token_hash=token_hash,
            usuario_id=usuario_id,
            expires_at=expires_at,
        )
        await repo.create(token)
        return raw_token

    @staticmethod
    async def validate_and_rotate(
        token_uuid: str, usuario_id: int | None, uow: UnitOfWork
    ) -> tuple[str, int]:
        """Validate a refresh token and rotate it (revoke old, create new).

        Replay detection: if the token is already revoked, ALL active tokens
        for that user are revoked and an UnauthorizedError is raised.

        Args:
            token_uuid: The raw UUID string from the client.
            usuario_id: Ignored — the user is resolved from the stored token.
            uow: Active UnitOfWork for transactional persistence.

        Returns:
            Tuple of (new_raw_UUID_string, usuario_id) for the caller.

        Raises:
            UnauthorizedError: If token is invalid, expired, or
                a replay attack is detected.
        """
        repo = RefreshTokenRepository(uow.session)
        token_hash = hash_refresh_token(token_uuid)
        stored = await repo.find_by_hash(token_hash)

        # Token not found in DB
        if stored is None:
            raise UnauthorizedError("Token inválido")

        # Token expired
        if stored.is_expired:
            raise UnauthorizedError("Token expirado")

        # Replay attack: token already revoked
        if stored.is_revoked:
            usuario_id_from_token = stored.usuario_id
            await repo.revoke_all_for_user(usuario_id_from_token)
            raise UnauthorizedError(
                "Sesión comprometida — todos los tokens revocados"
            )

        # Valid token: revoke current, create new
        usuario_id_from_token = stored.usuario_id
        await repo.revoke(stored.id)
        new_token = await RefreshTokenService.create_token(usuario_id_from_token, uow)
        return new_token, usuario_id_from_token

    @staticmethod
    async def revoke_token(token_uuid: str, uow: UnitOfWork) -> None:
        """Revoke a specific refresh token by its UUID.

        Args:
            token_uuid: The raw UUID string from the client.
            uow: Active UnitOfWork for transactional persistence.

        Raises:
            UnauthorizedError: If the token does not exist or is
                already revoked.
        """
        repo = RefreshTokenRepository(uow.session)
        token_hash = hash_refresh_token(token_uuid)
        stored = await repo.find_by_hash(token_hash)

        if stored is None:
            raise UnauthorizedError("Token inválido")

        if stored.is_revoked:
            raise UnauthorizedError("Token ya revocado")

        await repo.revoke(stored.id)
