"""Unit tests for AuthService — register, login, refresh, logout, get_me.

Uses mocked UoW and repositories to test business logic in isolation.
"""

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, PropertyMock, patch

import pytest

from app.exceptions import (
    ConflictError,
    UnauthorizedError,
)
from app.modules.auth.schemas import LoginRequest, RegisterRequest
from app.modules.auth.service import AuthService
from app.security import create_access_token, hash_password, verify_password

# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture
def mock_uow():
    """Create a mock UnitOfWork with a mock session."""
    uow = MagicMock()
    uow.session = AsyncMock()
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=None)
    return uow


@pytest.fixture
def mock_auth_repo():
    """Create a mock AuthRepository."""
    repo = AsyncMock()
    repo.find_by_email = AsyncMock()
    repo.create_with_roles = AsyncMock()
    repo.find = AsyncMock()
    return repo


@pytest.fixture
def mock_refresh_service():
    """Create a mock RefreshTokenService."""
    svc = MagicMock()
    svc.create_token = AsyncMock(return_value="new-uuid-token")
    svc.validate_and_rotate = AsyncMock(return_value=("rotated-uuid-token", 1))
    svc.revoke_token = AsyncMock()
    return svc


@pytest.fixture
def auth_service(mock_refresh_service):
    """Create an AuthService with a mocked refresh service."""
    return AuthService(refresh_token_service=mock_refresh_service)


def make_user(
    id=1,
    email="test@example.com",
    password="HashedPass1!",
    nombre="Test",
    apellido="User",
    activo=True,
):
    """Helper to create a mock Usuario with roles."""
    from unittest.mock import MagicMock

    user = MagicMock()
    user.id = id
    user.email = email
    user.password_hash = hash_password(password)
    user.nombre = nombre
    user.apellido = apellido
    user.activo = activo
    user.telefono = None

    # Simulate roles relationship
    role_mock = MagicMock()
    role_mock.rol_codigo = "CLIENT"
    user.usuario_roles = [role_mock]
    return user


# ── Register Tests ────────────────────────────────────────────────────────────


class TestRegister:
    """REG-01 and REG-02: Register creates user with CLIENT role."""

    async def test_register_success(
        self, auth_service, mock_uow, mock_auth_repo, mock_refresh_service
    ):
        """Valid registration creates user with CLIENT role and returns TokenResponse."""
        mock_auth_repo.find_by_email.return_value = None

        new_user = make_user(id=1)
        mock_auth_repo.create_with_roles.return_value = new_user
        mock_refresh_service.create_token.return_value = "refresh-uuid"

        request = RegisterRequest(
            nombre="Test",
            apellido="User",
            email="test@example.com",
            password="Test1234!",
        )

        result = await auth_service.register(
            request=request,
            uow=mock_uow,
            auth_repo=mock_auth_repo,
        )

        # Verify TokenResponse returned
        assert "access_token" in result
        assert result["refresh_token"] == "refresh-uuid"
        assert result["token_type"] == "bearer"
        assert result["expires_in"] == 1800

        # Verify user was created with CLIENT role
        mock_auth_repo.create_with_roles.assert_called_once()
        _call_kwargs = mock_auth_repo.create_with_roles.call_args[1]
        _call_user = _call_kwargs["usuario"]
        assert _call_user.email == "test@example.com"
        assert _call_user.nombre == "Test"
        assert _call_user.apellido == "User"
        assert _call_kwargs["roles"] == ["CLIENT"]

        # Verify refresh token was created
        mock_refresh_service.create_token.assert_called_once_with(usuario_id=1, uow=mock_uow)

    async def test_register_duplicate_email(
        self, auth_service, mock_uow, mock_auth_repo, mock_refresh_service
    ):
        """Register with existing email raises ConflictError."""
        existing_user = make_user(id=1)
        mock_auth_repo.find_by_email.return_value = existing_user

        request = RegisterRequest(
            nombre="Test",
            apellido="User",
            email="test@example.com",
            password="Test1234!",
        )

        with pytest.raises(ConflictError) as exc:
            await auth_service.register(
                request=request,
                uow=mock_uow,
                auth_repo=mock_auth_repo,
            )

        assert "El email ya está registrado" in str(exc.value.message)

        # Ensure no user was created
        mock_auth_repo.create_with_roles.assert_not_called()

    async def test_register_password_too_short_via_pydantic(self):
        """Password < 8 chars is rejected by Pydantic validation (422)."""
        with pytest.raises(Exception):
            RegisterRequest(
                nombre="Test",
                apellido="User",
                email="test@example.com",
                password="Short1!",
            )


# ── Login Tests ──────────────────────────────────────────────────────────────


class TestLogin:
    """LOG-01 to LOG-04: Login verifies credentials and returns tokens."""

    async def test_login_success(
        self, auth_service, mock_uow, mock_auth_repo, mock_refresh_service
    ):
        """Valid credentials return TokenResponse."""
        user = make_user(id=1, email="test@example.com", password="Test1234!")
        mock_auth_repo.find_by_email.return_value = user
        mock_refresh_service.create_token.return_value = "refresh-uuid"

        request = LoginRequest(email="test@example.com", password="Test1234!")
        result = await auth_service.login(request=request, uow=mock_uow, auth_repo=mock_auth_repo)

        assert "access_token" in result
        assert result["refresh_token"] == "refresh-uuid"
        assert result["token_type"] == "bearer"
        assert result["expires_in"] == 1800

        mock_auth_repo.find_by_email.assert_called_once_with("test@example.com")

    async def test_login_email_not_found(self, auth_service, mock_uow, mock_auth_repo):
        """Non-existent email returns generic error (LOG-02)."""
        mock_auth_repo.find_by_email.return_value = None

        request = LoginRequest(email="notfound@example.com", password="Test1234!")
        with pytest.raises(UnauthorizedError) as exc:
            await auth_service.login(request=request, uow=mock_uow, auth_repo=mock_auth_repo)

        assert "Email o contraseña incorrectos" in str(exc.value.message)

    async def test_login_wrong_password(self, auth_service, mock_uow, mock_auth_repo):
        """Wrong password returns same generic error (LOG-03)."""
        user = make_user(id=1, email="test@example.com", password="Correct1!")
        mock_auth_repo.find_by_email.return_value = user

        request = LoginRequest(email="test@example.com", password="Wrong1!!!")
        with pytest.raises(UnauthorizedError) as exc:
            await auth_service.login(request=request, uow=mock_uow, auth_repo=mock_auth_repo)

        # Must be the SAME message as email not found
        assert "Email o contraseña incorrectos" in str(exc.value.message)

    async def test_login_inactive_account(self, auth_service, mock_uow, mock_auth_repo):
        """Inactive account returns specific error (LOG-04)."""
        user = make_user(id=1, email="test@example.com", password="Test1234!", activo=False)
        mock_auth_repo.find_by_email.return_value = user

        request = LoginRequest(email="test@example.com", password="Test1234!")
        with pytest.raises(UnauthorizedError) as exc:
            await auth_service.login(request=request, uow=mock_uow, auth_repo=mock_auth_repo)

        assert "Cuenta deshabilitada" in str(exc.value.message)


# ── Refresh Tests ─────────────────────────────────────────────────────────────


class TestRefresh:
    """REF-01 to REF-04: Token rotation and replay detection."""

    async def test_refresh_success(
        self, auth_service, mock_uow, mock_auth_repo, mock_refresh_service
    ):
        """Valid refresh token rotates to a new pair (REF-01)."""
        user = make_user(id=1)
        mock_auth_repo.find_with_roles.return_value = user
        mock_refresh_service.validate_and_rotate.return_value = ("new-uuid", 1)

        result = await auth_service.refresh(
            refresh_token="old-uuid", uow=mock_uow, auth_repo=mock_auth_repo
        )

        assert "access_token" in result
        assert result["refresh_token"] == "new-uuid"
        assert result["token_type"] == "bearer"

        mock_refresh_service.validate_and_rotate.assert_called_once_with(
            token_uuid="old-uuid", usuario_id=None, uow=mock_uow
        )

    async def test_refresh_expired_token(
        self, auth_service, mock_uow, mock_auth_repo, mock_refresh_service
    ):
        """Expired token raises UnauthorizedError (REF-02)."""
        mock_refresh_service.validate_and_rotate.side_effect = UnauthorizedError("Token expirado")

        user = make_user(id=1)
        mock_auth_repo.find.return_value = user

        with pytest.raises(UnauthorizedError) as exc:
            await auth_service.refresh(
                refresh_token="expired-uuid", uow=mock_uow, auth_repo=mock_auth_repo
            )

        assert "Token expirado" in str(exc.value.message)

    async def test_refresh_replay_detection(
        self, auth_service, mock_uow, mock_auth_repo, mock_refresh_service
    ):
        """Already-revoked token triggers replay protection (REF-03)."""
        mock_refresh_service.validate_and_rotate.side_effect = UnauthorizedError(
            "Sesión comprometida — todos los tokens revocados"
        )

        with pytest.raises(UnauthorizedError) as exc:
            await auth_service.refresh(
                refresh_token="replayed-uuid", uow=mock_uow, auth_repo=mock_auth_repo
            )

        assert "Sesión comprometida" in str(exc.value.message)

    async def test_refresh_token_not_found(
        self, auth_service, mock_uow, mock_auth_repo, mock_refresh_service
    ):
        """Non-existent token raises UnauthorizedError (REF-04)."""
        mock_refresh_service.validate_and_rotate.side_effect = UnauthorizedError("Token inválido")

        with pytest.raises(UnauthorizedError) as exc:
            await auth_service.refresh(
                refresh_token="nonexistent-uuid",
                uow=mock_uow,
                auth_repo=mock_auth_repo,
            )

        assert "Token inválido" in str(exc.value.message)


# ── Logout Tests ──────────────────────────────────────────────────────────────


class TestLogout:
    """LOGOUT-01 and LOGOUT-02: Token revokation."""

    async def test_logout_success(self, auth_service, mock_uow, mock_refresh_service):
        """Valid token is revoked successfully (LOGOUT-01)."""
        user = make_user(id=1)
        mock_refresh_service.revoke_token = AsyncMock()

        await auth_service.logout(refresh_token="valid-uuid", current_user=user, uow=mock_uow)

        mock_refresh_service.revoke_token.assert_called_once_with(
            token_uuid="valid-uuid", uow=mock_uow
        )

    async def test_logout_token_not_found(self, auth_service, mock_uow, mock_refresh_service):
        """Non-existent token raises UnauthorizedError (LOGOUT-02)."""
        mock_refresh_service.revoke_token.side_effect = UnauthorizedError("Token inválido")

        user = make_user(id=1)
        with pytest.raises(UnauthorizedError) as exc:
            await auth_service.logout(refresh_token="invalid-uuid", current_user=user, uow=mock_uow)

        assert "Token inválido" in str(exc.value.message)


# ── Get Me Tests ──────────────────────────────────────────────────────────────


class TestGetMe:
    """ME-01: Authenticated user data."""

    async def test_get_me_success(self, auth_service):
        """Authenticated user returns UserResponse without password_hash."""
        user = make_user(id=1, email="test@example.com")

        result = await auth_service.get_me(current_user=user)

        assert result["id"] == 1
        assert result["email"] == "test@example.com"
        assert result["nombre"] == "Test"
        assert result["apellido"] == "User"
        assert result["activo"] is True
        assert result["roles"] == ["CLIENT"]
        # password_hash must NEVER be exposed
        assert "password_hash" not in result
        assert "password" not in result
