"""AuthService — stateless service for authentication orchestration.

Orchestrates authentication flows (register, login, refresh, logout, get_me)
by delegating to specialized services and repositories.
"""

from typing import TYPE_CHECKING, Optional

from app.exceptions import ConflictError, UnauthorizedError
from app.modules.auth.repository import AuthRepository
from app.modules.auth.schemas import LoginRequest, RegisterRequest
from app.modules.refreshtokens.service import RefreshTokenService
from app.security import create_access_token, hash_password, verify_password
from app.uow import UnitOfWork

if TYPE_CHECKING:
    from app.models.usuario import Usuario


class AuthService:
    """Handles authentication business logic.

    Stateless service — dependencies injected via method parameters.
    """

    def __init__(self, refresh_token_service: Optional[RefreshTokenService] = None):
        self.refresh_token_service = refresh_token_service or RefreshTokenService()

    # ── Register ──────────────────────────────────────────────────────────────

    async def register(
        self,
        request: RegisterRequest,
        uow: UnitOfWork,
        auth_repo: AuthRepository,
    ) -> dict:
        """Register a new user with CLIENT role and return tokens.

        Args:
            request: Validated registration data.
            uow: Active UnitOfWork.
            auth_repo: AuthRepository for user persistence.

        Returns:
            TokenResponse as a dict with access_token, refresh_token,
            token_type, expires_in.

        Raises:
            ConflictError: If the email is already registered.
        """
        # Check email uniqueness
        existing = await auth_repo.find_by_email(request.email)
        if existing is not None:
            raise ConflictError("El email ya está registrado")

        # Hash password and create user
        from app.models.usuario import Usuario

        password_hash = hash_password(request.password)
        usuario = Usuario(
            email=request.email,
            password_hash=password_hash,
            nombre=request.nombre,
            apellido=request.apellido,
            activo=True,
        )

        created = await auth_repo.create_with_roles(
            usuario=usuario,
            roles=["CLIENT"],
            asignado_por_id=None,
        )

        # Generate tokens
        access_token = create_access_token(
            {
                "sub": str(created.id),
                "email": created.email,
                "roles": ["CLIENT"],
            }
        )
        refresh_token = await self.refresh_token_service.create_token(
            usuario_id=created.id,
            uow=uow,
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 1800,
        }

    # ── Login ─────────────────────────────────────────────────────────────────

    async def login(
        self,
        request: LoginRequest,
        uow: UnitOfWork,
        auth_repo: AuthRepository,
    ) -> dict:
        """Authenticate user credentials and return tokens.

        Args:
            request: Login credentials.
            uow: Active UnitOfWork.
            auth_repo: AuthRepository for user lookup.

        Returns:
            TokenResponse as a dict.

        Raises:
            UnauthorizedError: Generic error if credentials are wrong.
            UnauthorizedError: Specific error if account is disabled.
        """
        # Find user by email
        usuario = await auth_repo.find_by_email(request.email)

        # Generic error: email not found
        if usuario is None:
            raise UnauthorizedError("Email o contraseña incorrectos")

        # Generic error: wrong password
        if not verify_password(request.password, usuario.password_hash):
            raise UnauthorizedError("Email o contraseña incorrectos")

        # Specific error: account disabled
        if not usuario.activo:
            raise UnauthorizedError("Cuenta deshabilitada")

        # Build roles list from relationship
        roles = [ur.rol_codigo for ur in (usuario.usuario_roles or [])]

        # Generate tokens
        access_token = create_access_token(
            {
                "sub": str(usuario.id),
                "email": usuario.email,
                "roles": roles,
            }
        )
        refresh_token = await self.refresh_token_service.create_token(
            usuario_id=usuario.id,
            uow=uow,
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 1800,
        }

    # ── Refresh ───────────────────────────────────────────────────────────────

    async def refresh(
        self,
        refresh_token: str,
        uow: UnitOfWork,
        auth_repo: AuthRepository,
    ) -> dict:
        """Validate and rotate a refresh token, return a new token pair.

        Args:
            refresh_token: The raw refresh token UUID to validate.
            uow: Active UnitOfWork.
            auth_repo: AuthRepository for user lookup.

        Returns:
            New TokenResponse as a dict.

        Raises:
            UnauthorizedError: If token is invalid, expired, or replay detected.
        """
        # Delegate rotation to RefreshTokenService — returns (new_token, usuario_id)
        new_token, usuario_id = await self.refresh_token_service.validate_and_rotate(
            token_uuid=refresh_token,
            usuario_id=None,
            uow=uow,
        )

        # Load user from DB for fresh data — eager load roles to avoid MissingGreenlet
        usuario = await auth_repo.find_with_roles(usuario_id)

        # Build roles from relationship
        roles = [ur.rol_codigo for ur in (usuario.usuario_roles or [])]

        # Create new access token
        access_token = create_access_token(
            {
                "sub": str(usuario.id),
                "email": usuario.email,
                "roles": roles,
            }
        )

        return {
            "access_token": access_token,
            "refresh_token": new_token,
            "token_type": "bearer",
            "expires_in": 1800,
        }

    # ── Logout ────────────────────────────────────────────────────────────────

    async def logout(
        self,
        refresh_token: str,
        current_user: "Usuario",
        uow: UnitOfWork,
    ) -> None:
        """Revoke a refresh token (logout).

        Args:
            refresh_token: The raw refresh token UUID to revoke.
            current_user: The authenticated user.
            uow: Active UnitOfWork.

        Raises:
            UnauthorizedError: If token is invalid or already revoked.
        """
        await self.refresh_token_service.revoke_token(
            token_uuid=refresh_token,
            uow=uow,
        )

    # ── Get Me ────────────────────────────────────────────────────────────────

    async def get_me(self, current_user: "Usuario") -> dict:
        """Return authenticated user data (no password_hash).

        Args:
            current_user: The authenticated Usuario instance.

        Returns:
            UserResponse as a dict.
        """
        roles = [ur.rol_codigo for ur in (current_user.usuario_roles or [])]
        return {
            "id": current_user.id,
            "nombre": current_user.nombre,
            "apellido": current_user.apellido,
            "email": current_user.email,
            "roles": roles,
            "activo": current_user.activo,
        }
