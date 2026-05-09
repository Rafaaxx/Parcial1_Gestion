"""Auth Pydantic schemas for request/response validation."""

from pydantic import BaseModel, Field, EmailStr


class LoginRequest(BaseModel):
    """Login credentials payload."""

    email: EmailStr
    password: str = Field(min_length=8)


class RegisterRequest(BaseModel):
    """New user registration payload."""

    nombre: str = Field(min_length=2, max_length=80)
    apellido: str = Field(min_length=2, max_length=80)
    email: EmailStr
    password: str = Field(min_length=8)


class TokenResponse(BaseModel):
    """JWT token pair response."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 1800  # 30 minutes in seconds


class RefreshRequest(BaseModel):
    """Refresh token request payload."""

    refresh_token: str


class UserResponse(BaseModel):
    """Authenticated user data — NEVER includes password_hash."""

    id: int
    nombre: str
    apellido: str
    email: EmailStr
    roles: list[str]
    activo: bool
