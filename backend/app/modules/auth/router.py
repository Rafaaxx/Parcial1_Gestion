"""Auth router — 5 endpoints for authentication and token management."""

from fastapi import APIRouter, Depends, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.config import settings
from app.dependencies import get_current_user, get_uow
from app.middleware.rate_limiter import limiter
from app.models.usuario import Usuario
from app.modules.auth.repository import AuthRepository
from app.modules.auth.schemas import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.modules.auth.service import AuthService
from app.uow import UnitOfWork

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])


def _get_auth_service() -> AuthService:
    """Factory for AuthService (stateless, can be reused)."""
    return AuthService()


def _get_auth_repo(uow: UnitOfWork = Depends(get_uow)) -> AuthRepository:
    """Factory for AuthRepository bound to the current UoW."""
    return AuthRepository(uow.session, Usuario)


# ── POST /register ───────────────────────────────────────────────────────────


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    request: RegisterRequest,
    uow: UnitOfWork = Depends(get_uow),
    auth_repo: AuthRepository = Depends(_get_auth_repo),
    auth_service: AuthService = Depends(_get_auth_service),
):
    """Register a new user with CLIENT role and return tokens."""
    async with uow:
        result = await auth_service.register(request=request, uow=uow, auth_repo=auth_repo)
    return result


# ── POST /login ──────────────────────────────────────────────────────────────


@router.post(
    "/login",
    response_model=TokenResponse,
)
@limiter.limit(settings.rate_limit_auth_limit)
async def login(
    request: Request,
    login_data: LoginRequest,
    uow: UnitOfWork = Depends(get_uow),
    auth_repo: AuthRepository = Depends(_get_auth_repo),
    auth_service: AuthService = Depends(_get_auth_service),
):
    """Authenticate user and return tokens. Rate limited."""
    async with uow:
        result = await auth_service.login(request=login_data, uow=uow, auth_repo=auth_repo)
    return result


# ── POST /refresh ────────────────────────────────────────────────────────────


@router.post(
    "/refresh",
    response_model=TokenResponse,
)
@limiter.limit(settings.rate_limit_refresh_limit)
async def refresh(
    request: Request,
    refresh_data: RefreshRequest,
    uow: UnitOfWork = Depends(get_uow),
    auth_repo: AuthRepository = Depends(_get_auth_repo),
    auth_service: AuthService = Depends(_get_auth_service),
):
    """Rotate a refresh token. Rate limited."""
    async with uow:
        result = await auth_service.refresh(
            refresh_token=refresh_data.refresh_token,
            uow=uow,
            auth_repo=auth_repo,
        )
    return result


# ── POST /logout ─────────────────────────────────────────────────────────────


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def logout(
    request: RefreshRequest,
    current_user: Usuario = Depends(get_current_user),
    uow: UnitOfWork = Depends(get_uow),
    auth_service: AuthService = Depends(_get_auth_service),
):
    """Revoke a refresh token (requires Bearer token)."""
    async with uow:
        await auth_service.logout(
            refresh_token=request.refresh_token,
            current_user=current_user,
            uow=uow,
        )


# ── GET /me ──────────────────────────────────────────────────────────────────


@router.get(
    "/me",
    response_model=UserResponse,
)
async def get_me(
    current_user: Usuario = Depends(get_current_user),
    auth_service: AuthService = Depends(_get_auth_service),
):
    """Return authenticated user data."""
    return await auth_service.get_me(current_user=current_user)
