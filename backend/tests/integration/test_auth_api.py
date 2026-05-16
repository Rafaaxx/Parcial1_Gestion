"""Integration tests for auth API endpoints — full stack with SQLite in-memory.

Covers register, login, refresh, logout, me, and RBAC scenarios.
Uses httpx AsyncClient against the actual FastAPI app with overridden DB.
"""

import uuid

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import selectinload

from app.config import settings
from app.database import Base, get_db
from app.main import app
from app.models.rol import Rol
from app.models.usuario import Usuario
from app.models.usuario_rol import UsuarioRol
from app.modules.refreshtokens.model import RefreshToken
from app.security import decode_access_token, hash_refresh_token

pytestmark = pytest.mark.asyncio


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture(scope="module")
async def test_engine():
    """Create SQLite in-memory engine with all tables."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed roles
    async with async_sessionmaker(engine, class_=AsyncSession)() as session:
        roles = [
            Rol(codigo="ADMIN", descripcion="Administrador"),
            Rol(codigo="CLIENT", descripcion="Cliente"),
            Rol(codigo="STOCK", descripcion="Gestor de stock"),
            Rol(codigo="PEDIDOS", descripcion="Gestor de pedidos"),
        ]
        for rol in roles:
            session.add(rol)
        await session.commit()

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def db_session(test_engine):
    """Fresh session per test, rolled back after."""
    async_session = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
def override_get_db(db_session):
    """Override get_db with the test session."""

    async def _override():
        yield db_session

    return _override


@pytest.fixture
async def client(override_get_db):
    """Test client with overridden DB dependency."""
    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture
def unique_email():
    """Generate a unique email per test."""
    uid = uuid.uuid4().hex[:8]
    return f"test-{uid}@example.com"


# ── Constants ─────────────────────────────────────────────────────────────────


REGISTER_URL = "/api/v1/auth/register"
LOGIN_URL = "/api/v1/auth/login"
REFRESH_URL = "/api/v1/auth/refresh"
LOGOUT_URL = "/api/v1/auth/logout"
ME_URL = "/api/v1/auth/me"

DEFAULT_PASSWORD = "Test1234!"


# ── Register Tests ───────────────────────────────────────────────────────────


class TestRegister:
    """REG-01 to REG-04: Registration scenarios."""

    async def test_register_full_flow(self, client, db_session, unique_email):
        """REG-01: Register returns 201 + TokenResponse."""
        data = {
            "nombre": "Test",
            "apellido": "User",
            "email": unique_email,
            "password": DEFAULT_PASSWORD,
        }
        resp = await client.post(REGISTER_URL, json=data)
        assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

        body = resp.json()
        assert "access_token" in body
        assert "refresh_token" in body
        assert body["token_type"] == "bearer"
        assert body["expires_in"] == 1800

        # Verify user exists in DB
        result = await db_session.execute(select(Usuario).where(Usuario.email == unique_email))
        user = result.scalar_one_or_none()
        assert user is not None
        assert user.nombre == "Test"
        assert user.apellido == "User"
        assert user.activo is True

        # Verify CLIENT role
        role_result = await db_session.execute(
            select(UsuarioRol).where(
                UsuarioRol.usuario_id == user.id,
                UsuarioRol.rol_codigo == "CLIENT",
            )
        )
        assert role_result.scalar_one_or_none() is not None

        # Verify password is hashed (not plain text)
        assert user.password_hash != DEFAULT_PASSWORD
        assert len(user.password_hash) == 60

    async def test_register_duplicate_email(self, client, unique_email):
        """REG-02: Duplicate email returns 409."""
        data = {
            "nombre": "Test",
            "apellido": "User",
            "email": unique_email,
            "password": DEFAULT_PASSWORD,
        }
        resp1 = await client.post(REGISTER_URL, json=data)
        assert resp1.status_code == 201

        resp2 = await client.post(REGISTER_URL, json=data)
        assert resp2.status_code == 409

    async def test_register_weak_password(self, client, unique_email):
        """REG-03: Password < 8 chars returns 422."""
        data = {
            "nombre": "Test",
            "apellido": "User",
            "email": unique_email,
            "password": "Ab1",
        }
        resp = await client.post(REGISTER_URL, json=data)
        assert resp.status_code == 422

    async def test_register_missing_fields(self, client, unique_email):
        """REG-04: Missing required field returns 422."""
        data = {
            "apellido": "User",
            "email": unique_email,
            "password": DEFAULT_PASSWORD,
        }
        resp = await client.post(REGISTER_URL, json=data)
        assert resp.status_code == 422


# ── Login Tests ──────────────────────────────────────────────────────────────


async def _register_and_login(client, email, password=DEFAULT_PASSWORD):
    """Helper: register a user and login, returning (access_token, refresh_token, body)."""
    reg_data = {
        "nombre": "Test",
        "apellido": "User",
        "email": email,
        "password": password,
    }
    reg_resp = await client.post(REGISTER_URL, json=reg_data)
    assert reg_resp.status_code == 201, f"Register failed: {reg_resp.text}"

    login_resp = await client.post(LOGIN_URL, json={"email": email, "password": password})
    assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
    body = login_resp.json()
    return body["access_token"], body["refresh_token"], body


class TestLogin:
    """LOG-01 to LOG-05: Login scenarios."""

    async def test_login_full_flow(self, client, db_session, unique_email):
        """LOG-01: Login returns 200 + TokenResponse with tokens."""
        access_token, refresh_token, body = await _register_and_login(client, unique_email)

        assert body["token_type"] == "bearer"
        assert body["expires_in"] == 1800

        # Verify refresh token stored in DB
        token_hash_val = hash_refresh_token(refresh_token)
        result = await db_session.execute(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash_val)
        )
        stored = result.scalar_one_or_none()
        assert stored is not None
        assert stored.revoked_at is None

        # Decode access token to verify claims
        decoded = decode_access_token(access_token)
        assert decoded["email"] == unique_email
        assert "CLIENT" in decoded["roles"]

    async def test_login_email_not_found(self, client):
        """LOG-02: Non-existent email returns 401 with generic message."""
        resp = await client.post(
            LOGIN_URL,
            json={"email": "unknown@example.com", "password": DEFAULT_PASSWORD},
        )
        assert resp.status_code == 401

    async def test_login_wrong_password(self, client, unique_email):
        """LOG-03: Wrong password returns same generic message."""
        await _register_and_login(client, unique_email)
        resp = await client.post(
            LOGIN_URL,
            json={"email": unique_email, "password": "Wrong1!!!"},
        )
        assert resp.status_code == 401

    async def test_login_inactive_account(self, client, db_session, unique_email):
        """LOG-04: Disabled account returns 401."""
        await _register_and_login(client, unique_email)

        # Deactivate the user
        result = await db_session.execute(select(Usuario).where(Usuario.email == unique_email))
        user = result.scalar_one()
        user.activo = False
        await db_session.commit()

        resp = await client.post(
            LOGIN_URL, json={"email": unique_email, "password": DEFAULT_PASSWORD}
        )
        assert resp.status_code == 401


# ── Refresh Tests ────────────────────────────────────────────────────────────


class TestRefresh:
    """REF-01 to REF-04: Token refresh and rotation."""

    async def test_refresh_rotation(self, client, db_session, unique_email):
        """REF-01: Refresh rotates tokens — old one revoked."""
        access_token, refresh_token, _ = await _register_and_login(client, unique_email)

        # Refresh
        resp = await client.post(REFRESH_URL, json={"refresh_token": refresh_token})
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

        body = resp.json()
        assert "access_token" in body
        assert body["refresh_token"] != refresh_token

        # Old token should be revoked in DB
        old_hash = hash_refresh_token(refresh_token)
        result = await db_session.execute(
            select(RefreshToken).where(RefreshToken.token_hash == old_hash)
        )
        stored = result.scalar_one_or_none()
        assert stored is not None
        assert stored.revoked_at is not None

    async def test_refresh_token_not_found(self, client):
        """REF-02/REF-04: Non-existent token returns 401."""
        resp = await client.post(
            REFRESH_URL,
            json={"refresh_token": "00000000-0000-0000-0000-000000000000"},
        )
        assert resp.status_code == 401

    async def test_refresh_replay_attack(self, client, db_session, unique_email):
        """REF-03: Same token used twice triggers replay detection."""
        _, refresh_token, _ = await _register_and_login(client, unique_email)

        # First refresh: should succeed
        resp1 = await client.post(REFRESH_URL, json={"refresh_token": refresh_token})
        assert resp1.status_code == 200

        # Second refresh with same token: replay detection — should return 401
        resp2 = await client.post(REFRESH_URL, json={"refresh_token": refresh_token})
        assert resp2.status_code == 401, f"Expected 401 for replay, got {resp2.status_code}"


# ── Logout Tests ─────────────────────────────────────────────────────────────


class TestLogout:
    """LOGOUT-01 to LOGOUT-03: Logout scenarios."""

    async def test_logout_flow(self, client, db_session, unique_email):
        """LOGOUT-01: Logout returns 204 and revokes token."""
        access_token, refresh_token, _ = await _register_and_login(client, unique_email)

        resp = await client.post(
            LOGOUT_URL,
            json={"refresh_token": refresh_token},
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert resp.status_code == 204, f"Expected 204, got {resp.status_code}"

        # Token should be revoked in DB
        token_hash_val = hash_refresh_token(refresh_token)
        result = await db_session.execute(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash_val)
        )
        stored = result.scalar_one_or_none()
        assert stored is not None
        assert stored.revoked_at is not None

    async def test_logout_already_revoked(self, client, unique_email):
        """LOGOUT-02: Already revoked token returns 401."""
        access_token, refresh_token, _ = await _register_and_login(client, unique_email)

        # First logout — should succeed
        resp1 = await client.post(
            LOGOUT_URL,
            json={"refresh_token": refresh_token},
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert resp1.status_code == 204

        # Second logout with same token — should return 401
        resp2 = await client.post(
            LOGOUT_URL,
            json={"refresh_token": refresh_token},
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert resp2.status_code == 401

    async def test_logout_no_auth(self, client):
        """LOGOUT-03: Without Bearer token returns 401 (no token = unauthorized)."""
        resp = await client.post(LOGOUT_URL, json={"refresh_token": "some-token"})
        assert resp.status_code == 401, f"Expected 401, got {resp.status_code}"


# ── Me Tests ─────────────────────────────────────────────────────────────────


class TestMe:
    """ME-01 to ME-03: Authenticated user data."""

    async def test_me_authenticated(self, client, unique_email):
        """ME-01: Authenticated user returns UserResponse."""
        access_token, _, _ = await _register_and_login(client, unique_email)

        resp = await client.get(
            ME_URL,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

        body = resp.json()
        assert body["email"] == unique_email
        assert body["nombre"] == "Test"
        assert body["apellido"] == "User"
        assert body["activo"] is True
        assert "CLIENT" in body["roles"]
        # Must NEVER expose password_hash
        assert "password_hash" not in body
        assert "password" not in body

    async def test_me_no_token(self, client):
        """ME-02: Without token returns 401 (no token = unauthorized)."""
        resp = await client.get(ME_URL)
        assert resp.status_code == 401, f"Expected 401, got {resp.status_code}"

    async def test_me_expired_token(self, client):
        """ME-03: Expired JWT returns 401."""
        from datetime import datetime, timedelta, timezone

        from jose import jwt

        expired_payload = {
            "sub": "1",
            "email": "test@example.com",
            "roles": ["CLIENT"],
            "exp": int((datetime.now(timezone.utc) - timedelta(hours=1)).timestamp()),
            "iat": int((datetime.now(timezone.utc) - timedelta(hours=2)).timestamp()),
        }
        expired_token = jwt.encode(
            expired_payload,
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm,
        )

        resp = await client.get(
            ME_URL,
            headers={"Authorization": f"Bearer {expired_token}"},
        )
        assert resp.status_code == 401


# ── RBAC Tests ───────────────────────────────────────────────────────────────


class TestRBAC:
    """RBAC-04 to RBAC-05: Role-based access control."""

    async def test_admin_role_passes(self, client, db_session, unique_email):
        """RBAC-04: Admin user passes require_role(['ADMIN'])."""
        # Create admin user via DB
        from passlib.hash import bcrypt

        admin = Usuario(
            email=unique_email,
            password_hash=bcrypt.hash("Admin1234!"),
            nombre="Admin",
            apellido="User",
            activo=True,
        )
        db_session.add(admin)
        await db_session.flush()
        db_session.add(UsuarioRol(usuario_id=admin.id, rol_codigo="ADMIN"))
        await db_session.commit()

        # Login as admin
        resp = await client.post(
            LOGIN_URL,
            json={"email": unique_email, "password": "Admin1234!"},
        )
        assert resp.status_code == 200, f"Admin login failed: {resp.text}"
        admin_token = resp.json()["access_token"]

        # Verify me endpoint returns ADMIN role
        resp = await client.get(
            ME_URL,
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 200
        assert "ADMIN" in resp.json()["roles"]

    async def test_client_role_forbidden(self, client, unique_email):
        """RBAC-05: Client user has CLIENT role (not ADMIN)."""
        access_token, _, _ = await _register_and_login(client, unique_email)
        resp = await client.get(
            ME_URL,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert resp.status_code == 200
        roles = resp.json()["roles"]
        assert "CLIENT" in roles
        assert "ADMIN" not in roles
