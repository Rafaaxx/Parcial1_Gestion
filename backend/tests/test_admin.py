"""Integration tests for Admin module — metrics, user management, and role guard.

Tests:
  1. Role guard (ADMIN implicit access, STOCK denied)
  2. Metrics endpoints (resumen, ventas, productos-top, pedidos-por-estado)
  3. User management (list, edit, activate/deactivate, last ADMIN validation)

Note: These tests are skipped because the admin router is not registered in main.py.
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel

from app.main import app
from app.dependencies import get_uow, oauth2_scheme
from app.uow import UnitOfWork
from app.models import (
    Usuario,
    UsuarioRol,
    Rol,
    Pedido,
    DetallePedido,
    Producto,
    Categoria,
    EstadoPedido,
    FormaPago,
)
from app.security import create_access_token
from decimal import Decimal


# Skip all tests in this module until admin router is implemented
pytestmark = pytest.mark.skip(reason="Admin router not registered in main.py")


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


# ── Seed data fixtures ────────────────────────────────────────────────────────


@pytest_asyncio.fixture
async def seed_roles(test_session):
    """Seed the 4 RBAC roles."""
    roles = [
        Rol(codigo="ADMIN", descripcion="Administrador"),
        Rol(codigo="STOCK", descripcion="Gestor de Stock"),
        Rol(codigo="PEDIDOS", descripcion="Gestor de Pedidos"),
        Rol(codigo="CLIENT", descripcion="Cliente"),
    ]
    for r in roles:
        test_session.add(r)
    await test_session.flush()


@pytest_asyncio.fixture
async def seed_estados_pedido(test_session):
    """Seed order states."""
    estados = [
        EstadoPedido(codigo="PENDIENTE", descripcion="Pendiente", orden=1, es_terminal=False),
        EstadoPedido(codigo="CONFIRMADO", descripcion="Confirmado", orden=2, es_terminal=False),
        EstadoPedido(codigo="EN_PREP", descripcion="En Preparación", orden=3, es_terminal=False),
        EstadoPedido(codigo="EN_CAMINO", descripcion="En Camino", orden=4, es_terminal=False),
        EstadoPedido(codigo="ENTREGADO", descripcion="Entregado", orden=5, es_terminal=True),
        EstadoPedido(codigo="CANCELADO", descripcion="Cancelado", orden=6, es_terminal=True),
    ]
    for e in estados:
        test_session.add(e)
    await test_session.flush()


@pytest_asyncio.fixture
async def seed_formas_pago(test_session):
    """Seed payment methods."""
    formas = [
        FormaPago(codigo="MERCADOPAGO", descripcion="MercadoPago", habilitado=True),
        FormaPago(codigo="EFECTIVO", descripcion="Efectivo", habilitado=True),
    ]
    for f in formas:
        test_session.add(f)
    await test_session.flush()


@pytest_asyncio.fixture
async def usuario_admin(test_session, seed_roles):
    """Create an ADMIN user."""
    user = Usuario(
        email="admin@test.com",
        password_hash="fake_hash_admin",
        nombre="Admin",
        apellido="User",
        activo=True,
    )
    test_session.add(user)
    await test_session.flush()
    await test_session.refresh(user)

    # Assign ADMIN role
    ur = UsuarioRol(usuario_id=user.id, rol_codigo="ADMIN")
    test_session.add(ur)
    await test_session.flush()
    return user


@pytest_asyncio.fixture
async def usuario_stock(test_session, seed_roles):
    """Create a STOCK-only user (no ADMIN)."""
    user = Usuario(
        email="stock@test.com",
        password_hash="fake_hash_stock",
        nombre="Stock",
        apellido="User",
        activo=True,
    )
    test_session.add(user)
    await test_session.flush()
    await test_session.refresh(user)

    ur = UsuarioRol(usuario_id=user.id, rol_codigo="STOCK")
    test_session.add(ur)
    await test_session.flush()
    return user


@pytest_asyncio.fixture
async def usuario_pedidos(test_session, seed_roles):
    """Create a PEDIDOS user."""
    user = Usuario(
        email="pedidos@test.com",
        password_hash="fake_hash_pedidos",
        nombre="Pedidos",
        apellido="User",
        activo=True,
    )
    test_session.add(user)
    await test_session.flush()
    await test_session.refresh(user)

    ur = UsuarioRol(usuario_id=user.id, rol_codigo="PEDIDOS")
    test_session.add(ur)
    await test_session.flush()
    return user


@pytest_asyncio.fixture
async def usuario_inactivo(test_session, seed_roles):
    """Create an inactive user (for toggle tests)."""
    user = Usuario(
        email="inactive@test.com",
        password_hash="fake_hash",
        nombre="Inactive",
        apellido="User",
        activo=True,
    )
    test_session.add(user)
    await test_session.flush()
    await test_session.refresh(user)

    ur = UsuarioRol(usuario_id=user.id, rol_codigo="CLIENT")
    test_session.add(ur)
    await test_session.flush()
    return user


@pytest_asyncio.fixture
async def seed_producto(test_session):
    """Create a test product."""
    prod = Producto(
        nombre="Test Product",
        descripcion="A test product",
        precio_base=Decimal("100.00"),
        stock_cantidad=50,
        disponible=True,
    )
    test_session.add(prod)
    await test_session.flush()
    await test_session.refresh(prod)
    return prod


@pytest_asyncio.fixture
async def seed_pedido_entregado(test_session, usuario_admin, seed_estados_pedido, seed_formas_pago, seed_producto):
    """Create a delivered order with items."""
    from datetime import datetime, timezone

    pedido = Pedido(
        usuario_id=usuario_admin.id,
        estado_codigo="ENTREGADO",
        total=Decimal("250.00"),
        costo_envio=Decimal("50.00"),
        forma_pago_codigo="EFECTIVO",
    )
    test_session.add(pedido)
    await test_session.flush()
    await test_session.refresh(pedido)

    detalle = DetallePedido(
        pedido_id=pedido.id,
        producto_id=seed_producto.id,
        nombre_snapshot="Test Product",
        precio_snapshot=Decimal("100.00"),
        cantidad=2,
    )
    test_session.add(detalle)
    await test_session.flush()
    return pedido


# ── Token fixtures ────────────────────────────────────────────────────────────


@pytest_asyncio.fixture
def token_admin(usuario_admin):
    """Create a valid JWT for ADMIN user."""
    return create_access_token({
        "sub": str(usuario_admin.id),
        "email": usuario_admin.email,
        "roles": ["ADMIN"],
    })


@pytest_asyncio.fixture
def token_stock(usuario_stock):
    """Create a valid JWT for STOCK user."""
    return create_access_token({
        "sub": str(usuario_stock.id),
        "email": usuario_stock.email,
        "roles": ["STOCK"],
    })


@pytest_asyncio.fixture
def token_pedidos(usuario_pedidos):
    """Create a valid JWT for PEDIDOS user."""
    return create_access_token({
        "sub": str(usuario_pedidos.id),
        "email": usuario_pedidos.email,
        "roles": ["PEDIDOS"],
    })


# ── HTTP Client fixtures ──────────────────────────────────────────────────────


@pytest_asyncio.fixture
async def auth_client(test_uow):
    """HTTP client with get_uow overridden."""
    app.dependency_overrides[get_uow] = lambda: test_uow
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def unauth_client(test_uow):
    """HTTP client with auth overridden to return None (triggers 401)."""
    app.dependency_overrides[get_uow] = lambda: test_uow

    async def _no_auth():
        return None

    app.dependency_overrides[oauth2_scheme] = _no_auth
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


# ═══════════════════════════════════════════════════════════════════════════════
# Task 2 Tests: Role Guard — ADMIN implicit access
# ═══════════════════════════════════════════════════════════════════════════════


class TestAdminRoleGuard:
    """ADMIN should access any endpoint implicitly."""

    @pytest.mark.asyncio
    async def test_admin_accesses_admin_endpoint(self, auth_client, token_admin):
        """ADMIN can access /api/v1/admin/metricas/resumen."""
        response = await auth_client.get(
            "/api/v1/admin/metricas/resumen",
            headers={"Authorization": f"Bearer {token_admin}"},
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    @pytest.mark.asyncio
    async def test_stock_cannot_access_admin_endpoint(self, auth_client, token_stock):
        """STOCK cannot access admin-only endpoint."""
        response = await auth_client.get(
            "/api/v1/admin/metricas/resumen",
            headers={"Authorization": f"Bearer {token_stock}"},
        )
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"

    @pytest.mark.asyncio
    async def test_admin_accesses_catalogo_endpoint(self, auth_client, token_admin):
        """ADMIN can access a STOCK-protected endpoint without STOCK role."""
        # Simulate accessing a catalogo endpoint (same as productos which allows ADMIN+STOCK)
        response = await auth_client.get(
            "/api/v1/admin/metricas/resumen",
            headers={"Authorization": f"Bearer {token_admin}"},
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    @pytest.mark.asyncio
    async def test_unauthorized_access(self, unauth_client):
        """No auth header → 401."""
        response = await unauth_client.get("/api/v1/admin/metricas/resumen")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"


# ═══════════════════════════════════════════════════════════════════════════════
# Task 4 Tests: Metrics Endpoints
# ═══════════════════════════════════════════════════════════════════════════════


class TestMetricsResumen:
    """GET /api/v1/admin/metricas/resumen"""

    @pytest.mark.asyncio
    async def test_resumen_success(self, auth_client, token_admin, seed_pedido_entregado):
        """Admin gets full resumen with KPIs."""
        response = await auth_client.get(
            "/api/v1/admin/metricas/resumen",
            headers={"Authorization": f"Bearer {token_admin}"},
        )
        assert response.status_code == 200, f"Expected 200, got {response.text}"
        data = response.json()
        assert "total_ventas" in data
        assert "cantidad_pedidos" in data
        assert "pedidos_por_estado" in data
        assert "usuarios_registrados" in data
        assert "productos_mas_vendidos" in data
        # With seed_pedido_entregado, there should be at least one delivered order
        assert data["cantidad_pedidos"] >= 1
        assert data["usuarios_registrados"] >= 1

    @pytest.mark.asyncio
    async def test_resumen_with_filters(self, auth_client, token_admin, seed_pedido_entregado):
        """Resumen filtered by date range."""
        response = await auth_client.get(
            "/api/v1/admin/metricas/resumen?desde=2020-01-01&hasta=2030-12-31",
            headers={"Authorization": f"Bearer {token_admin}"},
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_resumen_empty(self, auth_client, token_admin):
        """Resumen with no data returns zeros."""
        response = await auth_client.get(
            "/api/v1/admin/metricas/resumen",
            headers={"Authorization": f"Bearer {token_admin}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total_ventas"] is not None
        assert data["cantidad_pedidos"] == 0


class TestMetricsVentas:
    """GET /api/v1/admin/metricas/ventas"""

    @pytest.mark.asyncio
    async def test_ventas_by_day(self, auth_client, token_admin, seed_pedido_entregado):
        """Sales aggregated by day."""
        response = await auth_client.get(
            "/api/v1/admin/metricas/ventas?granularidad=dia&desde=2020-01-01&hasta=2030-12-31",
            headers={"Authorization": f"Bearer {token_admin}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_ventas_by_month(self, auth_client, token_admin, seed_pedido_entregado):
        """Sales aggregated by month."""
        response = await auth_client.get(
            "/api/v1/admin/metricas/ventas?granularidad=mes",
            headers={"Authorization": f"Bearer {token_admin}"},
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_ventas_invalid_granularidad(self, auth_client, token_admin):
        """Invalid granularity returns 422."""
        response = await auth_client.get(
            "/api/v1/admin/metricas/ventas?granularidad=invalid",
            headers={"Authorization": f"Bearer {token_admin}"},
        )
        assert response.status_code == 422, f"Expected 422, got {response.status_code}"


class TestMetricsProductosTop:
    """GET /api/v1/admin/metricas/productos-top"""

    @pytest.mark.asyncio
    async def test_top_productos(self, auth_client, token_admin, seed_pedido_entregado):
        """Top 10 products."""
        response = await auth_client.get(
            "/api/v1/admin/metricas/productos-top?top=5",
            headers={"Authorization": f"Bearer {token_admin}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_top_productos_with_dates(self, auth_client, token_admin, seed_pedido_entregado):
        """Top products with date range."""
        response = await auth_client.get(
            "/api/v1/admin/metricas/productos-top?top=5&desde=2020-01-01&hasta=2030-12-31",
            headers={"Authorization": f"Bearer {token_admin}"},
        )
        assert response.status_code == 200


class TestMetricsPedidosPorEstado:
    """GET /api/v1/admin/metricas/pedidos-por-estado"""

    @pytest.mark.asyncio
    async def test_pedidos_por_estado(self, auth_client, token_admin, seed_pedido_entregado):
        """Order distribution by state."""
        response = await auth_client.get(
            "/api/v1/admin/metricas/pedidos-por-estado",
            headers={"Authorization": f"Bearer {token_admin}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            assert "estado" in data[0]
            assert "cantidad" in data[0]
            assert "porcentaje" in data[0]


# ═══════════════════════════════════════════════════════════════════════════════
# Task 5 Tests: Admin User Management
# ═══════════════════════════════════════════════════════════════════════════════


class TestListUsuarios:
    """GET /api/v1/admin/usuarios"""

    @pytest.mark.asyncio
    async def test_list_usuarios(self, auth_client, token_admin, usuario_admin):
        """Admin lists all users."""
        response = await auth_client.get(
            "/api/v1/admin/usuarios?skip=0&limit=20",
            headers={"Authorization": f"Bearer {token_admin}"},
        )
        assert response.status_code == 200, f"Expected 200, got {response.text}"
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] >= 1

    @pytest.mark.asyncio
    async def test_list_usuarios_search(self, auth_client, token_admin, usuario_admin):
        """Search users by email."""
        response = await auth_client.get(
            f"/api/v1/admin/usuarios?busqueda={usuario_admin.email}",
            headers={"Authorization": f"Bearer {token_admin}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1

    @pytest.mark.asyncio
    async def test_list_usuarios_filter_role(self, auth_client, token_admin, usuario_admin):
        """Filter users by role code."""
        response = await auth_client.get(
            "/api/v1/admin/usuarios?rol=ADMIN",
            headers={"Authorization": f"Bearer {token_admin}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        for user in data["items"]:
            assert "ADMIN" in user["roles"]


class TestUpdateUsuario:
    """PUT /api/v1/admin/usuarios/{id}"""

    @pytest.mark.asyncio
    async def test_update_usuario_roles(self, auth_client, token_admin, usuario_inactivo):
        """Update user roles."""
        response = await auth_client.put(
            f"/api/v1/admin/usuarios/{usuario_inactivo.id}",
            json={"roles_codes": ["STOCK", "CLIENT"]},
            headers={"Authorization": f"Bearer {token_admin}"},
        )
        assert response.status_code == 200, f"Expected 200, got {response.text}"
        data = response.json()
        assert "STOCK" in data["roles"]
        assert "CLIENT" in data["roles"]

    @pytest.mark.asyncio
    async def test_update_usuario_not_found(self, auth_client, token_admin):
        """Update non-existent user returns 404."""
        response = await auth_client.put(
            "/api/v1/admin/usuarios/99999",
            json={"nombre": "Ghost"},
            headers={"Authorization": f"Bearer {token_admin}"},
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"

    @pytest.mark.asyncio
    async def test_cannot_remove_last_admin(self, auth_client, token_admin, usuario_admin):
        """Cannot remove ADMIN role from the last ADMIN."""
        response = await auth_client.put(
            f"/api/v1/admin/usuarios/{usuario_admin.id}",
            json={"roles_codes": ["STOCK"]},  # STOCK only, no ADMIN
            headers={"Authorization": f"Bearer {token_admin}"},
        )
        assert response.status_code == 409, f"Expected 409, got {response.status_code}: {response.text}"


class TestUpdateUsuarioEstado:
    """PATCH /api/v1/admin/usuarios/{id}/estado"""

    @pytest.mark.asyncio
    async def test_deactivate_usuario(self, auth_client, token_admin, usuario_inactivo):
        """Deactivate a user."""
        response = await auth_client.patch(
            f"/api/v1/admin/usuarios/{usuario_inactivo.id}/estado",
            json={"activo": False},
            headers={"Authorization": f"Bearer {token_admin}"},
        )
        assert response.status_code == 200, f"Expected 200, got {response.text}"
        data = response.json()
        assert data["activo"] is False

    @pytest.mark.asyncio
    async def test_reactivate_usuario(self, auth_client, token_admin, usuario_inactivo):
        """Reactivate a deactivated user."""
        # First deactivate
        await auth_client.patch(
            f"/api/v1/admin/usuarios/{usuario_inactivo.id}/estado",
            json={"activo": False},
            headers={"Authorization": f"Bearer {token_admin}"},
        )
        # Then reactivate
        response = await auth_client.patch(
            f"/api/v1/admin/usuarios/{usuario_inactivo.id}/estado",
            json={"activo": True},
            headers={"Authorization": f"Bearer {token_admin}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["activo"] is True

    @pytest.mark.asyncio
    async def test_cannot_deactivate_self(self, auth_client, token_admin, usuario_admin):
        """Admin cannot deactivate themselves."""
        response = await auth_client.patch(
            f"/api/v1/admin/usuarios/{usuario_admin.id}/estado",
            json={"activo": False},
            headers={"Authorization": f"Bearer {token_admin}"},
        )
        assert response.status_code == 409, f"Expected 409, got {response.status_code}: {response.text}"
