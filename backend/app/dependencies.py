"""FastAPI dependency injection setup

Exports:
  - get_uow: Injects a UnitOfWork for database access.
  - get_current_user: Extracts Bearer token, decodes JWT, loads Usuario.
  - require_role: Factory for role-based access control.
"""

import logging
from typing import AsyncGenerator, Callable, List

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.database import async_session_factory, get_db
from app.uow import UnitOfWork
from app.security import decode_access_token
from app.modules.auth.repository import AuthRepository
from app.models.usuario import Usuario
from app.exceptions import AppException, app_exception_to_http_exception

logger = logging.getLogger(__name__)

# OAuth2 scheme for Swagger UI — tokenUrl points to our login endpoint
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_uow(session: AsyncSession = Depends(get_db)) -> AsyncGenerator[UnitOfWork, None]:
    """
    Dependency for FastAPI to inject Unit of Work

    Usage in an endpoint:
        @app.post("/orders")
        async def create_order(order_data: CreateOrderRequest, uow: UnitOfWork = Depends(get_uow)):
            async with uow:
                order = await uow.get_repository(Order).create(order_data)

    Args:
        session: AsyncSession from get_db dependency

    Yields:
        UnitOfWork instance
    """
    uow = UnitOfWork(session)
    try:
        yield uow
    finally:
        logger.debug("UnitOfWork dependency cleanup")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    uow: UnitOfWork = Depends(get_uow),
) -> Usuario:
    """Extract Bearer token, decode JWT, load Usuario from DB.

    Validates:
      - Token presence and format (``Authorization: Bearer <token>``)
      - JWT signature and expiration (via ``decode_access_token``)
      - User exists in DB and is active

    Args:
        token: Bearer token from Authorization header.
        uow: Active UnitOfWork.

    Returns:
        Usuario instance (fresh from database).

    Raises:
        HTTPException 401: If token is missing, invalid, expired,
            or user not found/disabled.
    """
    try:
        payload = decode_access_token(token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "detail": "Token inválido o expirado",
                "code": "UNAUTHORIZED",
            },
        )

    user_id_str = payload.get("sub")
    if user_id_str is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "detail": "Token inválido",
                "code": "UNAUTHORIZED",
            },
        )

    try:
        user_id = int(user_id_str)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "detail": "Token inválido",
                "code": "UNAUTHORIZED",
            },
        )

    # Load user from DB with roles eagerly loaded
    repo = AuthRepository(uow.session, Usuario)
    usuario = await repo.find_with_roles(user_id)

    if usuario is None or not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "detail": "Usuario no encontrado o deshabilitado",
                "code": "UNAUTHORIZED",
            },
        )

    return usuario


def require_role(roles: List[str]) -> Callable:
    """Factory that returns a FastAPI dependency for role-based access control.

    Reads the roles from the JWT payload (not from database) for performance — ADR-4.
    The dependency runs after ``get_current_user`` and checks that the user's
    roles intersect with the required roles (OR logic).

    Args:
        roles: List of role codes that are allowed (e.g. ["ADMIN", "STOCK"]).

    Returns:
        A dependency function that returns None (pass) or raises
        HTTPException 403.
    """
    async def _role_checker(
        current_user: Usuario = Depends(get_current_user),
        token: str = Depends(oauth2_scheme),
    ) -> None:
        # Read roles from JWT payload (not from BD) — ADR-4 compliance
        try:
            payload = decode_access_token(token)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "detail": "Token inválido o expirado",
                    "code": "UNAUTHORIZED",
                },
            )

        user_roles = set(payload.get("roles", []))
        if not user_roles.intersection(set(roles)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "detail": "No tienes permisos para acceder a este recurso",
                    "code": "FORBIDDEN",
                },
            )
        return None

    return _role_checker
