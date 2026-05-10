"""RefreshToken model — persists refresh tokens for secure rotation.

NOTE: This model does NOT inherit from BaseModel (no SoftDeleteMixin).
Refresh tokens use ``revoked_at`` with revokation semantics, not soft-delete.
"""
from typing import Optional, TYPE_CHECKING
from datetime import datetime, timezone

from sqlalchemy import DateTime
from sqlmodel import SQLModel, Field, Relationship

from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.usuario import Usuario


class RefreshToken(TimestampMixin, SQLModel, table=True):
    """Stores a refresh token's SHA-256 hash for secure rotation.

    Each token has:
      - ``token_hash``: SHA-256 hex digest of the raw UUID (never stored raw).
      - ``usuario_id``: FK to the owning user.
      - ``expires_at``: expiration timestamp (7 days from creation).
      - ``revoked_at``: NULL if active, set on revokation/rotation.
    """

    __tablename__ = "refresh_tokens"

    id: Optional[int] = Field(default=None, primary_key=True)
    token_hash: str = Field(max_length=64, unique=True, nullable=False)
    usuario_id: int = Field(foreign_key="usuarios.id", nullable=False)
    expires_at: datetime = Field(
        nullable=False,
        sa_type=DateTime(timezone=True),
        description="Token expiration timestamp (UTC)",
    )
    revoked_at: Optional[datetime] = Field(
        default=None,
        nullable=True,
        sa_type=DateTime(timezone=True),
        description="Token revocation timestamp (UTC) — NULL if active",
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    usuario: Optional["Usuario"] = Relationship(back_populates="refresh_tokens")

    # ── Helpers ───────────────────────────────────────────────────────────────

    @property
    def is_expired(self) -> bool:
        """Check if the token has expired (expires_at past UTC now)."""
        return self.expires_at.replace(tzinfo=timezone.utc) < datetime.now(
            timezone.utc
        )

    @property
    def is_revoked(self) -> bool:
        """Check if the token has been explicitly revoked."""
        return self.revoked_at is not None
