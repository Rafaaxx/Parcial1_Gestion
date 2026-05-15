"""Integration tests for Perfil API endpoints — full stack with SQLite in-memory.

Covers:
  - GET  /api/v1/perfil   → View profile (US-061)
  - PUT  /api/v1/perfil   → Update profile (US-062)
  - PUT  /api/v1/perfil/password → Change password (US-063)
"""
import uuid
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.main import app
from app.database import Base, get_db
from app.security import hash_password, verify_password, create_access_token
from app.models.rol import Rol
from app.models.usuario import Usuario
from app.models.usuario_rol import UsuarioRol
from app.modules.refreshtokens.model import RefreshToken

pytestmark = pytest.mark.asyncio

# ── URLs ────────────────────────────────────────────────────────────────────

PERFIL_URL = "/api/v1/perfil"
PASSWORD_URL = "/api/v1/perfil/password"
REGISTER_URL = "/api/v1/auth/register"
DEFAULT_PASSWORD = "Test1234!"


# ── Fixtures ────────────────────────────────────────────────────────────────


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
    async_session = async_sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
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
    return f"perfil-test-{uid}@example.com"


@pytest.fixture
async def created_user(db_session, unique_email):
    """Create a test user and return (user, access_token)."""
    password_hash = hash_password(DEFAULT_PASSWORD)
    user = Usuario(
        email=unique_email,
        password_hash=password_hash,
        nombre="Juan",
        apellido="Pérez",
        telefono="+541112345678",
        activo=True,
    )
    db_session.add(user)
    await db_session.flush()

    # Assign CLIENT role
    user_role = UsuarioRol(
        usuario_id=user.id,
        rol_codigo="CLIENT",
        asignado_por_id=None,
    )
    db_session.add(user_role)
    await db_session.commit()
    await db_session.refresh(user)

    # Create access token
    token = create_access_token({
        "sub": str(user.id),
        "email": user.email,
        "roles": ["CLIENT"],
    })
    return user, token


@pytest.fixture
def auth_header(created_user):
    """Authorization header with Bearer token."""
    _, token = created_user
    return {"Authorization": f"Bearer {token}"}


# ═══════════════════════════════════════════════════════════════════════════
# Tests: GET /api/v1/perfil
# ═══════════════════════════════════════════════════════════════════════════


class TestGetPerfil:
    """US-061: Ver perfil propio."""

    async def test_get_perfil_success(self, client, auth_header, created_user):
        """GIVEN un cliente autenticado, WHEN accede a su perfil,
        THEN ve: nombre, email, teléfono, fecha de registro."""
        user, _ = created_user
        resp = await client.get(PERFIL_URL, headers=auth_header)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

        body = resp.json()
        assert body["id"] == user.id
        assert body["nombre"] == "Juan"
        assert body["apellido"] == "Pérez"
        assert body["email"] == user.email
        assert body["telefono"] == "+541112345678"
        assert "roles" in body
        assert "CLIENT" in body["roles"]
        assert "fecha_registro" in body

    async def test_get_perfil_no_auth(self, client):
        """THEN no autenticado recibe 403 (HTTPBearer default)."""
        resp = await client.get(PERFIL_URL)
        assert resp.status_code == 403

    async def test_get_perfil_wrong_token(self, client):
        """GIVEN un token inválido, WHEN accede, THEN 401."""
        headers = {"Authorization": "Bearer invalidtoken123"}
        resp = await client.get(PERFIL_URL, headers=headers)
        assert resp.status_code == 401


# ═══════════════════════════════════════════════════════════════════════════
# Tests: PUT /api/v1/perfil
# ═══════════════════════════════════════════════════════════════════════════


class TestUpdatePerfil:
    """US-062: Editar perfil propio."""

    async def test_update_nombre(self, client, auth_header, created_user):
        """GIVEN un cliente autenticado, WHEN modifica su nombre,
        THEN los cambios se persisten."""
        resp = await client.put(
            PERFIL_URL,
            json={"nombre": "Juan Carlos"},
            headers=auth_header,
        )
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        body = resp.json()
        assert body["nombre"] == "Juan Carlos"
        assert body["apellido"] == "Pérez"  # unchanged

    async def test_update_telefono(self, client, auth_header, created_user):
        """GIVEN un cliente autenticado, WHEN modifica su teléfono,
        THEN los cambios se persisten."""
        resp = await client.put(
            PERFIL_URL,
            json={"telefono": "+5491112345678"},
            headers=auth_header,
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["telefono"] == "+5491112345678"

    async def test_update_multiple_fields(self, client, auth_header):
        """GIVEN múltiples campos, WHEN se envían, THEN todos se persisten."""
        resp = await client.put(
            PERFIL_URL,
            json={
                "nombre": "María",
                "apellido": "García",
                "telefono": "+5411555666777",
            },
            headers=auth_header,
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["nombre"] == "María"
        assert body["apellido"] == "García"
        assert body["telefono"] == "+5411555666777"

    async def test_update_no_fields(self, client, auth_header):
        """GIVEN un body vacío, WHEN se envía, THEN 422."""
        resp = await client.put(
            PERFIL_URL,
            json={},
            headers=auth_header,
        )
        assert resp.status_code == 422

    async def test_update_no_auth(self, client):
        """GIVEN no autenticado, WHEN modifica, THEN 403 (HTTPBearer default)."""
        resp = await client.put(
            PERFIL_URL,
            json={"nombre": "Hacker"},
        )
        assert resp.status_code == 403

    async def test_email_not_changeable(self, client, auth_header, created_user):
        """El email NO se puede cambiar (es el identificador)."""
        user, _ = created_user
        resp = await client.put(
            PERFIL_URL,
            json={"nombre": "New Name"},
            headers=auth_header,
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["email"] == user.email  # unchanged


# ═══════════════════════════════════════════════════════════════════════════
# Tests: PUT /api/v1/perfil/password
# ═══════════════════════════════════════════════════════════════════════════


class TestChangePassword:
    """US-063: Cambiar contraseña."""

    async def test_change_password_success(self, client, auth_header, created_user, db_session):
        """GIVEN un cliente autenticado, WHEN envía su contraseña actual y la nueva,
        THEN si la actual es correcta se actualiza la contraseña."""
        user, _ = created_user
        resp = await client.put(
            PASSWORD_URL,
            json={
                "password_actual": DEFAULT_PASSWORD,
                "password_nueva": "NuevaPass789!",
            },
            headers=auth_header,
        )
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        body = resp.json()
        assert "message" in body
        assert body["requires_relogin"] is True

        # Verify password was actually changed
        await db_session.refresh(user)
        assert verify_password("NuevaPass789!", user.password_hash)

    async def test_change_password_wrong_actual(self, client, auth_header):
        """GIVEN contraseña actual incorrecta, WHEN intenta cambiarla,
        THEN se rechaza con error."""
        resp = await client.put(
            PASSWORD_URL,
            json={
                "password_actual": "WrongPass123!",
                "password_nueva": "NuevaPass789!",
            },
            headers=auth_header,
        )
        assert resp.status_code == 401

    async def test_change_password_short_new(self, client, auth_header):
        """La nueva contraseña debe cumplir los mismos requisitos
        que en el registro (mínimo 8 caracteres)."""
        resp = await client.put(
            PASSWORD_URL,
            json={
                "password_actual": DEFAULT_PASSWORD,
                "password_nueva": "corta",
            },
            headers=auth_header,
        )
        assert resp.status_code == 422

    async def test_change_password_revokes_tokens(self, client, auth_header, created_user, db_session):
        """Se invalidan todos los refresh tokens existentes (forzar re-login)."""
        user, _ = created_user

        # Create a refresh token for the user
        from app.security import generate_refresh_token, hash_refresh_token
        raw_token = generate_refresh_token()
        token_hash = hash_refresh_token(raw_token)

        from datetime import datetime, timedelta, timezone
        refresh_token = RefreshToken(
            token_hash=token_hash,
            usuario_id=user.id,
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
        )
        db_session.add(refresh_token)
        await db_session.commit()

        # Change password
        resp = await client.put(
            PASSWORD_URL,
            json={
                "password_actual": DEFAULT_PASSWORD,
                "password_nueva": "NuevaPass789!",
            },
            headers=auth_header,
        )
        assert resp.status_code == 200

        # Verify all tokens were revoked
        result = await db_session.execute(
            select(RefreshToken).where(
                RefreshToken.usuario_id == user.id,
                RefreshToken.revoked_at.is_(None),
            )
        )
        active_tokens = result.scalars().all()
        assert len(active_tokens) == 0, "All tokens should be revoked"

    async def test_change_password_no_auth(self, client):
        """GIVEN no autenticado, WHEN cambia contraseña, THEN 403 (HTTPBearer default)."""
        resp = await client.put(
            PASSWORD_URL,
            json={
                "password_actual": "anything",
                "password_nueva": "NewPass123!",
            },
        )
        assert resp.status_code == 403
