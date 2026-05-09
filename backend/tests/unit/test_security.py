"""Tests for app.security pure functions — hashing, JWT, refresh token."""
import pytest
import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, ANY

from app.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
    generate_refresh_token,
    hash_refresh_token,
)
from app.config import settings


# ── Helpers ───────────────────────────────────────────────────────────────────

def _future_exp(minutes: int = 30) -> datetime:
    return datetime.now(timezone.utc) + timedelta(minutes=minutes)


def _past_exp(minutes: int = 30) -> datetime:
    return datetime.now(timezone.utc) - timedelta(minutes=minutes)


# ── Hashing ───────────────────────────────────────────────────────────────────


class TestHashPassword:
    """SEC-01: hash_password produces valid bcrypt hashes."""

    def test_hash_password_returns_60_chars(self):
        """hash of valid password returns 60-char bcrypt string."""
        hashed = hash_password("Test1234!")
        assert isinstance(hashed, str)
        assert len(hashed) == 60

    def test_hash_different_salts(self):
        """same password produces different hashes (automatic salt)."""
        h1 = hash_password("Test1234!")
        h2 = hash_password("Test1234!")
        assert h1 != h2


class TestVerifyPassword:
    """SEC-01 / SEC-02: verify_password matches bcrypt hashes."""

    def test_verify_password_correct(self):
        """correct password returns True."""
        hashed = hash_password("Test1234!")
        assert verify_password("Test1234!", hashed) is True

    def test_verify_password_incorrect(self):
        """wrong password returns False."""
        hashed = hash_password("Test1234!")
        assert verify_password("WrongPass1!", hashed) is False


# ── JWT ───────────────────────────────────────────────────────────────────────


class TestCreateDecodeAccessToken:
    """SEC-03 / SEC-04: JWT create and decode round-trip."""

    def test_create_and_decode_token(self):
        """payload round-trips with exp and iat"""
        payload = {"sub": "1", "email": "a@b.com", "roles": ["CLIENT"]}
        token = create_access_token(payload)
        decoded = decode_access_token(token)

        assert decoded["sub"] == payload["sub"]
        assert decoded["email"] == payload["email"]
        assert decoded["roles"] == payload["roles"]
        assert "exp" in decoded
        assert "iat" in decoded

    def test_token_contains_required_claims(self):
        """access token has all required claims: sub, email, roles, exp, iat."""
        payload = {"sub": "42", "email": "user@example.com", "roles": ["ADMIN", "CLIENT"]}
        token = create_access_token(payload)
        decoded = decode_access_token(token)

        assert decoded["sub"] == "42"
        assert decoded["email"] == "user@example.com"
        assert decoded["roles"] == ["ADMIN", "CLIENT"]
        # exp should be ~30 min from now
        exp_dt = datetime.fromtimestamp(decoded["exp"], tz=timezone.utc)
        assert _future_exp(25) <= exp_dt <= _future_exp(35)

    def test_decode_tampered_token(self):
        """modified token raises JWTError (SEC-04)."""
        from jose import JWTError

        payload = {"sub": "1", "email": "a@b.com", "roles": ["CLIENT"]}
        token = create_access_token(payload)
        # Tamper with the payload portion
        parts = token.split(".")
        tampered = parts[0] + "." + parts[1] + "modified" + "." + parts[2]
        with pytest.raises(JWTError):
            decode_access_token(tampered)

    def test_decode_expired_token(self):
        """expired JWT raises JWTError (SEC-05)."""
        from jose import JWTError
        from jose import jwt as jose_jwt

        payload = {
            "sub": "1",
            "email": "a@b.com",
            "roles": ["CLIENT"],
            "exp": int((datetime.now(timezone.utc) - timedelta(hours=1)).timestamp()),
            "iat": int((datetime.now(timezone.utc) - timedelta(hours=2)).timestamp()),
        }
        # Manually create an expired token
        token = jose_jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
        with pytest.raises(JWTError):
            decode_access_token(token)


# ── Refresh Token ─────────────────────────────────────────────────────────────


class TestGenerateRefreshToken:
    """SEC-05: generate_refresh_token returns UUID v4."""

    def test_generate_refresh_token_returns_uuid_v4(self):
        """generated token is a valid UUID v4 string."""
        token = generate_refresh_token()
        parsed = uuid.UUID(token)
        assert parsed.version == 4

    def test_generate_refresh_token_unique(self):
        """consecutive calls produce different tokens."""
        t1 = generate_refresh_token()
        t2 = generate_refresh_token()
        assert t1 != t2


class TestHashRefreshToken:
    """SEC-06: hash_refresh_token produces SHA-256 hex digest."""

    def test_hash_refresh_token_returns_64_chars(self):
        """SHA-256 hex digest is 64 characters."""
        token = generate_refresh_token()
        hashed = hash_refresh_token(token)
        assert isinstance(hashed, str)
        assert len(hashed) == 64

    def test_hash_is_deterministic(self):
        """same UUID produces same hash."""
        token = "550e8400-e29b-41d4-a716-446655440000"
        assert hash_refresh_token(token) == hash_refresh_token(token)

    def test_different_tokens_different_hashes(self):
        """different UUIDs produce different hashes."""
        assert hash_refresh_token("a") != hash_refresh_token("b")

    def test_hash_is_hex(self):
        """hash contains only hex characters."""
        token = generate_refresh_token()
        hashed = hash_refresh_token(token)
        int(hashed, 16)  # should not raise
