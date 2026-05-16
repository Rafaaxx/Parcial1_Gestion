"""Security utilities — password hashing, JWT tokens, refresh token generation.

Pure functions only — no state, no side effects beyond what the functions return.
"""

import hashlib
import uuid
from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt

from app.config import settings


def hash_password(password: str) -> str:
    """Hash a password with bcrypt (cost >= 12).

    Args:
        password: Plain-text password to hash.

    Returns:
        60-character bcrypt hash string.
    """
    # Use bcrypt directly instead of passlib to avoid version conflicts
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode(), salt).decode()


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plain-text password against a bcrypt hash.

    Args:
        plain: Plain-text password to verify.
        hashed: Bcrypt hash to compare against.

    Returns:
        True if the password matches the hash, False otherwise.
    """
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def create_access_token(data: dict) -> str:
    """Create a signed JWT access token (HS256) with standard claims.

    The payload includes:
      - ``sub``: user ID (str)
      - ``email``: user email
      - ``roles``: list of role codes
      - ``exp``: expiration timestamp (30 min from now)
      - ``iat``: issued-at timestamp

    Args:
        data: Dictionary with at least ``sub``, ``email``, ``roles`` keys.

    Returns:
        Encoded JWT string.
    """
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    to_encode.update(
        {
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(minutes=settings.access_token_expire_minutes)).timestamp()),
        }
    )
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict:
    """Decode and verify a JWT access token.

    Validates:
      - Digital signature (HS256 via ``jwt_secret_key``)
      - Expiration time (``exp`` claim)

    Args:
        token: Encoded JWT string.

    Returns:
        Decoded payload dict.

    Raises:
        JWTError: If the token is invalid, tampered with, or expired.
    """
    return jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
    )


def generate_refresh_token() -> str:
    """Generate a cryptographically random refresh token (UUID v4).

    Returns:
        UUID v4 string (e.g. ``550e8400-e29b-41d4-a716-446655440000``).
    """
    return str(uuid.uuid4())


def hash_refresh_token(token: str) -> str:
    """Hash a refresh token with SHA-256 for secure storage.

    Args:
        token: The raw refresh token UUID string.

    Returns:
        64-character lowercase hex digest.
    """
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
