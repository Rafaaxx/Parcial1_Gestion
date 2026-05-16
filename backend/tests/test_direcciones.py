"""Integration tests for delivery address endpoints (US-024 to US-028).

Covers all 5 endpoints:
  - POST /api/v1/direcciones     — Crear dirección
  - GET  /api/v1/direcciones     — Listar direcciones
  - PUT  /api/v1/direcciones/{id} — Editar dirección
  - DELETE /api/v1/direcciones/{id} — Eliminar dirección (soft delete)
  - PATCH /api/v1/direcciones/{id}/predeterminada — Establecer predeterminada

Auth strategy:
  - auth_client: overrides get_uow, auth via real JWT in Authorization header
  - unauth_client: overrides get_uow + oauth2_scheme → returns None (triggers 401)
  - Original get_current_user runs in auth_client, loading user from DB each time
"""

from datetime import datetime, timedelta, timezone

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel

from app.dependencies import get_current_user, get_uow, oauth2_scheme
from app.main import app
from app.models import DireccionEntrega, Usuario
from app.modules.direcciones.schemas import (
    DireccionCreate,
    DireccionListResponse,
    DireccionRead,
)
from app.security import create_access_token
from app.uow import UnitOfWork

# ═══════════════════════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════════════════════


@pytest_asyncio.fixture(scope="function")
async def test_db():
    """Create in-memory SQLite test database with all tables."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def test_session(test_db):
    """Create test database session."""
    async with AsyncSession(test_db, expire_on_commit=False) as session:
        yield session


@pytest_asyncio.fixture
def test_uow(test_session):
    """Create test UnitOfWork."""
    return UnitOfWork(test_session)


# ── User Fixtures ─────────────────────────────────────────────────────────────


@pytest_asyncio.fixture
async def usuario_cliente(test_session):
    """Create a CLIENT test user in the database."""
    user = Usuario(
        email="cliente@test.com",
        password_hash="fake_hash",
        nombre="Test",
        apellido="User",
        activo=True,
    )
    test_session.add(user)
    await test_session.flush()
    await test_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def otro_usuario(test_session):
    """Create another user for ownership tests."""
    user = Usuario(
        email="otro@test.com",
        password_hash="fake_hash",
        nombre="Otro",
        apellido="User",
        activo=True,
    )
    test_session.add(user)
    await test_session.flush()
    await test_session.refresh(user)
    return user


# ── Token Fixtures ────────────────────────────────────────────────────────────


@pytest_asyncio.fixture
def token_cliente(usuario_cliente):
    """Create a valid JWT for usuario_cliente with CLIENT role."""
    return create_access_token(
        {
            "sub": str(usuario_cliente.id),
            "email": usuario_cliente.email,
            "roles": ["CLIENT"],
        }
    )


@pytest_asyncio.fixture
def token_otro(otro_usuario):
    """Create a valid JWT for otro_usuario with CLIENT role."""
    return create_access_token(
        {
            "sub": str(otro_usuario.id),
            "email": otro_usuario.email,
            "roles": ["CLIENT"],
        }
    )


# ── HTTP Client Fixtures ──────────────────────────────────────────────────────


@pytest_asyncio.fixture
async def auth_client(test_uow):
    """HTTP client with get_uow overridden.

    Auth flows through real JWT in Authorization header.
    Original get_current_user loads user from DB each request.
    """
    app.dependency_overrides[get_uow] = lambda: test_uow
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def unauth_client(test_uow):
    """HTTP client with get_uow overridden + oauth2_scheme returns None.

    This triggers get_current_user to raise 401 because credentials=None.
    """
    app.dependency_overrides[get_uow] = lambda: test_uow

    async def _no_auth():
        return None

    app.dependency_overrides[oauth2_scheme] = _no_auth
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


# ── Address Fixture Helpers ───────────────────────────────────────────────────


async def _create_direccion_en_db(
    session,
    usuario_id: int,
    linea1: str,
    alias: str | None = None,
    es_principal: bool = False,
    **kwargs,
) -> DireccionEntrega:
    """Helper to create a DireccionEntrega directly in the database."""
    direccion = DireccionEntrega(
        usuario_id=usuario_id,
        linea1=linea1,
        alias=alias,
        es_principal=es_principal,
        **kwargs,
    )
    session.add(direccion)
    await session.flush()
    await session.refresh(direccion)
    return direccion


async def _crear_direccion_via_api(
    client: AsyncClient,
    token: str,
    linea1: str,
    alias: str | None = None,
) -> dict:
    """Helper to create an address via the API and return the response JSON."""
    payload = {"linea1": linea1}
    if alias is not None:
        payload["alias"] = alias
    response = await client.post(
        "/api/v1/direcciones",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert (
        response.status_code == 201
    ), f"Failed to create address: {response.status_code} {response.text}"
    return response.json()


# ═══════════════════════════════════════════════════════════════════════════════
# US-024: Crear dirección de entrega
# ═══════════════════════════════════════════════════════════════════════════════


class TestCrearDireccion:
    """POST /api/v1/direcciones — Crear dirección de entrega"""

    @pytest.mark.asyncio
    async def test_create_direccion_success(self, auth_client, token_cliente):
        """POST con alias y linea1 → 201 + es_principal true (1ra dirección)."""
        response = await auth_client.post(
            "/api/v1/direcciones",
            json={"alias": "Casa", "linea1": "Av. Siempre Viva 123, CABA"},
            headers={"Authorization": f"Bearer {token_cliente}"},
        )
        assert response.status_code == 201, f"Expected 201, got {response.text}"
        data = response.json()
        assert data["linea1"] == "Av. Siempre Viva 123, CABA"
        assert data["alias"] == "Casa"
        assert data["es_principal"] is True
        assert "id" in data
        assert data["usuario_id"] is not None

    @pytest.mark.asyncio
    async def test_create_direccion_first_is_principal(self, auth_client, token_cliente):
        """Primera dirección creada debe tener es_principal=true."""
        response = await auth_client.post(
            "/api/v1/direcciones",
            json={"linea1": "Av. Siempre Viva 123, CABA"},
            headers={"Authorization": f"Bearer {token_cliente}"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["es_principal"] is True, "La primera dirección debe ser la predeterminada"

    @pytest.mark.asyncio
    async def test_create_direccion_second_not_principal(self, auth_client, token_cliente):
        """Segunda dirección NO debe ser predeterminada."""
        # Create first address
        await _crear_direccion_via_api(
            auth_client, token_cliente, linea1="Primera dirección", alias="Casa"
        )

        # Create second address
        response = await auth_client.post(
            "/api/v1/direcciones",
            json={"linea1": "Segunda dirección"},
            headers={"Authorization": f"Bearer {token_cliente}"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["es_principal"] is False, "La segunda dirección NO debe ser predeterminada"

    @pytest.mark.asyncio
    async def test_create_direccion_empty_linea1(self, auth_client, token_cliente):
        """POST con linea1 vacío → 422."""
        response = await auth_client.post(
            "/api/v1/direcciones",
            json={"linea1": ""},
            headers={"Authorization": f"Bearer {token_cliente}"},
        )
        # 422 can come from either Pydantic validation (fastapi) or service layer
        assert response.status_code == 422, f"Expected 422, got {response.text}"

    @pytest.mark.asyncio
    async def test_create_direccion_alias_too_long(self, auth_client, token_cliente):
        """POST con alias de 51 caracteres → 422."""
        response = await auth_client.post(
            "/api/v1/direcciones",
            json={"linea1": "Dirección válida", "alias": "a" * 51},
            headers={"Authorization": f"Bearer {token_cliente}"},
        )
        assert response.status_code == 422, f"Expected 422, got {response.text}"

    @pytest.mark.asyncio
    async def test_create_direccion_unauthorized(self, unauth_client):
        """POST sin autenticación → 401."""
        response = await unauth_client.post(
            "/api/v1/direcciones",
            json={"linea1": "Av. Siempre Viva 123, CABA"},
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"


# ═══════════════════════════════════════════════════════════════════════════════
# US-025: Listar direcciones del cliente
# ═══════════════════════════════════════════════════════════════════════════════


class TestListarDirecciones:
    """GET /api/v1/direcciones — Listar direcciones del usuario autenticado"""

    @pytest.mark.asyncio
    async def test_list_direcciones_empty(self, auth_client, token_cliente):
        """GET sin direcciones → items vacío, total 0."""
        response = await auth_client.get(
            "/api/v1/direcciones",
            headers={"Authorization": f"Bearer {token_cliente}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    @pytest.mark.asyncio
    async def test_list_direcciones_with_data(self, auth_client, token_cliente):
        """Crear 2 direcciones, listar → 2 items."""
        await _crear_direccion_via_api(auth_client, token_cliente, linea1="Dir 1", alias="Casa")
        await _crear_direccion_via_api(auth_client, token_cliente, linea1="Dir 2", alias="Trabajo")

        response = await auth_client.get(
            "/api/v1/direcciones",
            headers={"Authorization": f"Bearer {token_cliente}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 2

    @pytest.mark.asyncio
    async def test_list_direcciones_pagination(self, auth_client, token_cliente):
        """Crear 3, limit=2 → 2 items, total=3."""
        for i in range(3):
            await _crear_direccion_via_api(auth_client, token_cliente, linea1=f"Dir {i + 1}")

        response = await auth_client.get(
            "/api/v1/direcciones?skip=0&limit=2",
            headers={"Authorization": f"Bearer {token_cliente}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 3
        assert data["skip"] == 0
        assert data["limit"] == 2

    @pytest.mark.asyncio
    async def test_list_direcciones_other_user(self, auth_client, token_cliente, token_otro):
        """Crear como user A, listar como user B → vacío."""
        await _crear_direccion_via_api(auth_client, token_cliente, linea1="Dir de usuario A")

        response = await auth_client.get(
            "/api/v1/direcciones",
            headers={"Authorization": f"Bearer {token_otro}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    @pytest.mark.asyncio
    async def test_list_direcciones_unauthorized(self, unauth_client):
        """GET sin autenticación → 401."""
        response = await unauth_client.get("/api/v1/direcciones")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"


# ═══════════════════════════════════════════════════════════════════════════════
# US-026: Editar dirección de entrega
# ═══════════════════════════════════════════════════════════════════════════════


class TestEditarDireccion:
    """PUT /api/v1/direcciones/{id} — Editar dirección"""

    @pytest.mark.asyncio
    async def test_update_direccion_alias(self, auth_client, token_cliente):
        """Cambiar alias → 200 + alias actualizado."""
        created = await _crear_direccion_via_api(
            auth_client, token_cliente, linea1="Original", alias="Casa"
        )

        response = await auth_client.put(
            f"/api/v1/direcciones/{created['id']}",
            json={"alias": "Trabajo"},
            headers={"Authorization": f"Bearer {token_cliente}"},
        )
        assert response.status_code == 200, f"Expected 200, got {response.text}"
        data = response.json()
        assert data["alias"] == "Trabajo"
        assert data["linea1"] == "Original"  # unchanged

    @pytest.mark.asyncio
    async def test_update_direccion_linea1(self, auth_client, token_cliente):
        """Cambiar linea1 → 200 + linea1 actualizado."""
        created = await _crear_direccion_via_api(
            auth_client, token_cliente, linea1="Dirección anterior", alias="Casa"
        )

        response = await auth_client.put(
            f"/api/v1/direcciones/{created['id']}",
            json={"linea1": "Nueva dirección"},
            headers={"Authorization": f"Bearer {token_cliente}"},
        )
        assert response.status_code == 200, f"Expected 200, got {response.text}"
        data = response.json()
        assert data["linea1"] == "Nueva dirección"
        assert data["alias"] == "Casa"  # unchanged

    @pytest.mark.asyncio
    async def test_update_direccion_not_owner(self, auth_client, token_cliente, token_otro):
        """User A edita dirección de user B → 404."""
        # Create address as user A
        created = await _crear_direccion_via_api(
            auth_client, token_cliente, linea1="Dirección de A"
        )

        # Try to update as user B
        response = await auth_client.put(
            f"/api/v1/direcciones/{created['id']}",
            json={"alias": "Hacked"},
            headers={"Authorization": f"Bearer {token_otro}"},
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"

    @pytest.mark.asyncio
    async def test_update_direccion_not_found(self, auth_client, token_cliente):
        """PUT con id inexistente → 404."""
        response = await auth_client.put(
            "/api/v1/direcciones/99999",
            json={"alias": "Nuevo"},
            headers={"Authorization": f"Bearer {token_cliente}"},
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"

    @pytest.mark.asyncio
    async def test_update_direccion_unauthorized(self, unauth_client):
        """PUT sin autenticación → 401."""
        response = await unauth_client.put(
            "/api/v1/direcciones/1",
            json={"alias": "Nuevo"},
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"


# ═══════════════════════════════════════════════════════════════════════════════
# US-027: Eliminar dirección de entrega
# ═══════════════════════════════════════════════════════════════════════════════


class TestEliminarDireccion:
    """DELETE /api/v1/direcciones/{id} — Eliminar dirección (soft delete)"""

    @pytest.mark.asyncio
    async def test_delete_direccion_success(self, auth_client, token_cliente):
        """Eliminar → 204."""
        created = await _crear_direccion_via_api(auth_client, token_cliente, linea1="A eliminar")

        response = await auth_client.delete(
            f"/api/v1/direcciones/{created['id']}",
            headers={"Authorization": f"Bearer {token_cliente}"},
        )
        assert response.status_code == 204, f"Expected 204, got {response.status_code}"

        # Verify soft-deleted: should not appear in list
        list_resp = await auth_client.get(
            "/api/v1/direcciones",
            headers={"Authorization": f"Bearer {token_cliente}"},
        )
        assert list_resp.json()["total"] == 0

    @pytest.mark.asyncio
    async def test_delete_direccion_not_owner(self, auth_client, token_cliente, token_otro):
        """User A elimina dirección de user B → 404."""
        created = await _crear_direccion_via_api(
            auth_client, token_cliente, linea1="Dirección de A"
        )

        response = await auth_client.delete(
            f"/api/v1/direcciones/{created['id']}",
            headers={"Authorization": f"Bearer {token_otro}"},
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"

    @pytest.mark.asyncio
    async def test_delete_direccion_not_found(self, auth_client, token_cliente):
        """DELETE con id inexistente → 404."""
        response = await auth_client.delete(
            "/api/v1/direcciones/99999",
            headers={"Authorization": f"Bearer {token_cliente}"},
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"

    @pytest.mark.asyncio
    async def test_delete_direccion_unauthorized(self, unauth_client):
        """DELETE sin autenticación → 401."""
        response = await unauth_client.delete("/api/v1/direcciones/1")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"

    @pytest.mark.asyncio
    async def test_delete_principal_reassigns(
        self, auth_client, test_session, test_uow, token_cliente
    ):
        """Eliminar predeterminada → siguiente más reciente se vuelve predeterminada."""
        # We need the test user's ID to create addresses directly in DB
        # First get the user ID by creating an address via API
        resp1 = await auth_client.post(
            "/api/v1/direcciones",
            json={"linea1": "Dir 1", "alias": "Más antigua"},
            headers={"Authorization": f"Bearer {token_cliente}"},
        )
        assert resp1.status_code == 201
        dir1_id = resp1.json()["id"]
        assert resp1.json()["es_principal"] is True  # first = default

        # Create 2 more addresses (second and third won't be default)
        resp2 = await auth_client.post(
            "/api/v1/direcciones",
            json={"linea1": "Dir 2"},
            headers={"Authorization": f"Bearer {token_cliente}"},
        )
        assert resp2.status_code == 201
        dir2_id = resp2.json()["id"]
        assert resp2.json()["es_principal"] is False

        resp3 = await auth_client.post(
            "/api/v1/direcciones",
            json={"linea1": "Dir 3"},
            headers={"Authorization": f"Bearer {token_cliente}"},
        )
        assert resp3.status_code == 201
        dir3_id = resp3.json()["id"]
        assert resp3.json()["es_principal"] is False

        # Now delete the default (dir1)
        response = await auth_client.delete(
            f"/api/v1/direcciones/{dir1_id}",
            headers={"Authorization": f"Bearer {token_cliente}"},
        )
        assert response.status_code == 204

        # The most recent address (dir3) should now be the default
        list_resp = await auth_client.get(
            "/api/v1/direcciones",
            headers={"Authorization": f"Bearer {token_cliente}"},
        )
        data = list_resp.json()
        assert data["total"] == 2

        # Find which one is now principal
        dirs = {d["id"]: d for d in data["items"]}
        assert dirs[dir2_id]["es_principal"] is False
        assert dirs[dir3_id]["es_principal"] is True, (
            "La dirección más reciente debe volverse predeterminada " "tras eliminar la anterior"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# US-028: Establecer dirección predeterminada
# ═══════════════════════════════════════════════════════════════════════════════


class TestSetPredeterminada:
    """PATCH /api/v1/direcciones/{id}/predeterminada — Establecer como predeterminada"""

    @pytest.mark.asyncio
    async def test_set_predeterminada_success(self, auth_client, token_cliente):
        """PATCH → 200 + es_principal=true."""
        # Create 2 addresses
        dir1 = await _crear_direccion_via_api(
            auth_client, token_cliente, linea1="Dir 1", alias="Casa"
        )
        dir2 = await _crear_direccion_via_api(
            auth_client, token_cliente, linea1="Dir 2", alias="Trabajo"
        )

        # Set dir2 as predeterminada
        response = await auth_client.patch(
            f"/api/v1/direcciones/{dir2['id']}/predeterminada",
            headers={"Authorization": f"Bearer {token_cliente}"},
        )
        assert response.status_code == 200, f"Expected 200, got {response.text}"
        data = response.json()
        assert data["es_principal"] is True
        assert data["alias"] == "Trabajo"

    @pytest.mark.asyncio
    async def test_set_predeterminada_switches_previous(self, auth_client, token_cliente):
        """A es principal, PATCH B → A ya no es principal, B sí."""
        dir1 = await _crear_direccion_via_api(
            auth_client, token_cliente, linea1="Dir 1", alias="Casa"
        )
        dir2 = await _crear_direccion_via_api(
            auth_client, token_cliente, linea1="Dir 2", alias="Trabajo"
        )

        # Set dir2 as predeterminada
        await auth_client.patch(
            f"/api/v1/direcciones/{dir2['id']}/predeterminada",
            headers={"Authorization": f"Bearer {token_cliente}"},
        )

        # Verify: dir1 is no longer principal, dir2 is
        list_resp = await auth_client.get(
            "/api/v1/direcciones",
            headers={"Authorization": f"Bearer {token_cliente}"},
        )
        data = list_resp.json()
        dirs = {d["id"]: d for d in data["items"]}
        assert dirs[dir1["id"]]["es_principal"] is False
        assert dirs[dir2["id"]]["es_principal"] is True

    @pytest.mark.asyncio
    async def test_set_predeterminada_idempotent(self, auth_client, token_cliente):
        """PATCH sobre la misma dirección ya predeterminada → 200 sin error."""
        # First address is auto-set as default
        dir1 = await _crear_direccion_via_api(auth_client, token_cliente, linea1="Dir 1")
        assert dir1["es_principal"] is True

        # PATCH the same address as predeterminada (already is)
        response = await auth_client.patch(
            f"/api/v1/direcciones/{dir1['id']}/predeterminada",
            headers={"Authorization": f"Bearer {token_cliente}"},
        )
        assert response.status_code == 200, f"Expected 200, got {response.text}"
        data = response.json()
        assert data["es_principal"] is True
        assert data["id"] == dir1["id"]

    @pytest.mark.asyncio
    async def test_set_predeterminada_not_owner(self, auth_client, token_cliente, token_otro):
        """User A PATCH la dirección de user B → 404."""
        created = await _crear_direccion_via_api(
            auth_client, token_cliente, linea1="Dirección de A"
        )

        response = await auth_client.patch(
            f"/api/v1/direcciones/{created['id']}/predeterminada",
            headers={"Authorization": f"Bearer {token_otro}"},
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"

    @pytest.mark.asyncio
    async def test_set_predeterminada_not_found(self, auth_client, token_cliente):
        """PATCH con id inexistente → 404."""
        response = await auth_client.patch(
            "/api/v1/direcciones/99999/predeterminada",
            headers={"Authorization": f"Bearer {token_cliente}"},
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"

    @pytest.mark.asyncio
    async def test_set_predeterminada_unauthorized(self, unauth_client):
        """PATCH sin autenticación → 401."""
        response = await unauth_client.patch(
            "/api/v1/direcciones/1/predeterminada",
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"


# ═══════════════════════════════════════════════════════════════════════════════
# Edge Cases
# ═══════════════════════════════════════════════════════════════════════════════


class TestEdgeCases:
    """Edge case tests for delivery addresses"""

    @pytest.mark.asyncio
    async def test_create_direccion_trim_whitespace(self, auth_client, token_cliente):
        """Alias con espacios se trimea."""
        response = await auth_client.post(
            "/api/v1/direcciones",
            json={"alias": "   Casa   ", "linea1": "  Av. Siempre Viva 123  "},
            headers={"Authorization": f"Bearer {token_cliente}"},
        )
        assert response.status_code == 201, f"Expected 201, got {response.text}"
        data = response.json()
        assert data["alias"] == "Casa"  # trimmed
        assert data["linea1"] == "Av. Siempre Viva 123"  # trimmed

    @pytest.mark.asyncio
    async def test_soft_deleted_not_in_list(self, auth_client, token_cliente):
        """Dirección eliminada no aparece en GET."""
        # Create 2 addresses
        d1 = await _crear_direccion_via_api(auth_client, token_cliente, linea1="Dir 1")
        await _crear_direccion_via_api(auth_client, token_cliente, linea1="Dir 2")

        # Delete one
        await auth_client.delete(
            f"/api/v1/direcciones/{d1['id']}",
            headers={"Authorization": f"Bearer {token_cliente}"},
        )

        # List should show only 1
        list_resp = await auth_client.get(
            "/api/v1/direcciones",
            headers={"Authorization": f"Bearer {token_cliente}"},
        )
        data = list_resp.json()
        assert data["total"] == 1
        assert all(
            d["id"] != d1["id"] for d in data["items"]
        ), "Soft-deleted address must not appear in list"

    @pytest.mark.asyncio
    async def test_list_direcciones_ordered_by_created_at_desc(self, auth_client, token_cliente):
        """Listado ordenado por created_at DESC (más reciente primero)."""
        d1 = await _crear_direccion_via_api(auth_client, token_cliente, linea1="Primera")
        d2 = await _crear_direccion_via_api(auth_client, token_cliente, linea1="Segunda")
        d3 = await _crear_direccion_via_api(auth_client, token_cliente, linea1="Tercera")

        list_resp = await auth_client.get(
            "/api/v1/direcciones",
            headers={"Authorization": f"Bearer {token_cliente}"},
        )
        data = list_resp.json()
        assert data["total"] == 3
        ids = [d["id"] for d in data["items"]]
        # Most recent first: d3, d2, d1
        assert ids == [
            d3["id"],
            d2["id"],
            d1["id"],
        ], f"Expected order [{d3['id']}, {d2['id']}, {d1['id']}], got {ids}"
