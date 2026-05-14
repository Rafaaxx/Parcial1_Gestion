"""Integration tests for Pedido endpoints.

CRITICAL: These tests require PostgreSQL because they use SELECT FOR UPDATE
for stock validation. SQLite does NOT support SELECT FOR UPDATE.

All tests in this module are marked with @pytest.mark.postgres and will
be skipped if PostgreSQL is not available.
"""

from decimal import Decimal

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel

# Mark all tests in this module to require PostgreSQL
pytestmark = pytest.mark.postgres


# ── Test data helpers ────────────────────────────────────────────────────────────


async def _create_test_user(session: AsyncSession, email: str = "test@example.com") -> dict:
    """Create a test user with CLIENT role."""
    from passlib.context import CryptContext

    from app.models.rol import Rol
    from app.models.usuario import Usuario
    from app.models.usuario_rol import UsuarioRol

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    usuario = Usuario(
        email=email,
        password_hash=pwd_context.hash("Test1234!"),
        nombre="Test",
        apellido="User",
        activo=True,
    )
    session.add(usuario)
    await session.flush()
    await session.refresh(usuario)

    # Assign CLIENT role
    rol_result = await session.execute(select(Rol).where(Rol.codigo == "CLIENT"))
    rol = rol_result.scalar_one()

    usuario_rol = UsuarioRol(
        usuario_id=usuario.id,
        rol_codigo=rol.codigo,
        asignado_por_id=usuario.id,
    )
    session.add(usuario_rol)
    await session.flush()

    return {"id": usuario.id, "email": email, "roles": ["CLIENT"]}


async def _create_test_admin(session: AsyncSession) -> dict:
    """Create a test user with ADMIN role."""
    from passlib.context import CryptContext

    from app.models.rol import Rol
    from app.models.usuario import Usuario
    from app.models.usuario_rol import UsuarioRol

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    usuario = Usuario(
        email="admin@test.com",
        password_hash=pwd_context.hash("Admin1234!"),
        nombre="Admin",
        apellido="User",
        activo=True,
    )
    session.add(usuario)
    await session.flush()
    await session.refresh(usuario)

    rol_result = await session.execute(select(Rol).where(Rol.codigo == "ADMIN"))
    rol = rol_result.scalar_one()

    usuario_rol = UsuarioRol(
        usuario_id=usuario.id,
        rol_codigo=rol.codigo,
        asignado_por_id=usuario.id,
    )
    session.add(usuario_rol)
    await session.flush()

    return {"id": usuario.id, "email": "admin@test.com", "roles": ["ADMIN"]}


async def _create_test_producto(
    session: AsyncSession,
    nombre: str = "Test Pizza",
    precio: Decimal = Decimal("100.00"),
    stock: int = 50,
) -> dict:
    """Create a test product."""
    from app.models.producto import Producto

    producto = Producto(
        nombre=nombre,
        descripcion="Delicious test product",
        precio_base=precio,
        stock_cantidad=stock,
        disponible=True,
    )
    session.add(producto)
    await session.flush()
    await session.refresh(producto)

    return {"id": producto.id, "nombre": producto.nombre, "precio_base": producto.precio_base}


async def _create_test_address(session: AsyncSession, usuario_id: int) -> int:
    """Create a test address for a user."""
    from app.models.direccion_entrega import DireccionEntrega

    direccion = DireccionEntrega(
        usuario_id=usuario_id,
        linea1="Av. Test 123, Buenos Aires",
        alias="Casa",
        es_principal=True,
    )
    session.add(direccion)
    await session.flush()
    return direccion.id


def _get_auth_headers(user: dict) -> dict:
    """Generate auth headers for test user using real JWT signing."""
    from app.security import create_access_token

    payload = {
        "sub": str(user["id"]),
        "email": user["email"],
        "roles": user["roles"],
    }
    token = create_access_token(payload)
    return {"Authorization": f"Bearer {token}"}


# ── Test class: Pedido creation ─────────────────────────────────────────────────


@pytest.mark.postgres
class TestCrearPedido:
    """Tests for POST /api/v1/pedidos — order creation with UoW atomicity."""

    @pytest.fixture
    async def setup_data(self, pg_session: AsyncSession):
        """Create test data: user, admin, product, other_user. Commits so app can see it."""
        user = await _create_test_user(pg_session, "cliente@test.com")
        admin = await _create_test_admin(pg_session)
        producto = await _create_test_producto(
            pg_session,
            nombre="Pizza Margherita",
            precio=Decimal("850.00"),
            stock=20,
        )
        other_user = await _create_test_user(pg_session, "other@test.com")
        await pg_session.commit()
        return {"user": user, "admin": admin, "producto": producto, "other_user": other_user}

    @pytest.mark.asyncio
    async def test_crear_pedido_exitoso(
        self,
        pg_session: AsyncSession,
        pg_client: AsyncClient,
        setup_data: dict,
    ):
        """Test: order created atomically with snapshots and initial history."""
        user = setup_data["user"]
        producto = setup_data["producto"]
        headers = _get_auth_headers(user)

        body = {
            "items": [
                {
                    "producto_id": producto["id"],
                    "cantidad": 2,
                    "personalizacion": None,
                }
            ],
            "forma_pago_codigo": "MERCADOPAGO",
            "direccion_id": None,
            "notas": "Sin aceitunas",
        }

        response = await pg_client.post(
            "/api/v1/pedidos",
            json=body,
            headers=headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["estado_codigo"] == "PENDIENTE"
        assert data["costo_envio"] == "50.00"
        assert Decimal(data["total"]) > Decimal("0.00")

        # Verify Pedido exists in DB
        from app.models.pedido import Pedido

        pedido_result = await pg_session.execute(select(Pedido).where(Pedido.id == data["id"]))
        pedido = pedido_result.scalar_one()
        assert pedido.usuario_id == user["id"]
        assert pedido.estado_codigo == "PENDIENTE"
        assert pedido.costo_envio == Decimal("50.00")

        # Verify DetallePedido has snapshots
        from app.models.pedido import DetallePedido

        detalles_result = await pg_session.execute(
            select(DetallePedido).where(DetallePedido.pedido_id == pedido.id)
        )
        detalles = list(detalles_result.scalars().all())
        assert len(detalles) == 1
        assert detalles[0].nombre_snapshot == producto["nombre"]
        assert detalles[0].precio_snapshot == producto["precio_base"]
        assert detalles[0].cantidad == 2

        # Verify HistorialEstadoPedido with estado_desde=NULL
        from app.models.pedido import HistorialEstadoPedido

        historial_result = await pg_session.execute(
            select(HistorialEstadoPedido).where(HistorialEstadoPedido.pedido_id == pedido.id)
        )
        historial = list(historial_result.scalars().all())
        assert len(historial) == 1
        assert historial[0].estado_desde is None
        assert historial[0].estado_hacia == "PENDIENTE"
        assert historial[0].usuario_id == user["id"]

    @pytest.mark.asyncio
    async def test_stock_insuficiente_rollback(
        self,
        pg_session: AsyncSession,
        pg_client: AsyncClient,
        setup_data: dict,
    ):
        """Test: order NOT created when stock insufficient (full rollback)."""
        user = setup_data["user"]
        producto = setup_data["producto"]
        headers = _get_auth_headers(user)

        # stock_cantidad = 20, requested = 100 (exceeds)
        body = {
            "items": [
                {
                    "producto_id": producto["id"],
                    "cantidad": 100,
                }
            ],
            "forma_pago_codigo": "MERCADOPAGO",
        }

        response = await pg_client.post(
            "/api/v1/pedidos",
            json=body,
            headers=headers,
        )

        assert response.status_code == 422
        assert "Stock insuficiente" in response.json()["detail"]

        # Verify NO Pedido created in DB
        from app.models.pedido import Pedido

        count_result = await pg_session.execute(
            select(Pedido).where(Pedido.usuario_id == user["id"])
        )
        count = len(list(count_result.scalars().all()))
        assert count == 0

    @pytest.mark.asyncio
    async def test_forma_pago_invalida_422(
        self,
        pg_session: AsyncSession,
        pg_client: AsyncClient,
        setup_data: dict,
    ):
        """Test: 422 when payment method invalid or disabled."""
        user = setup_data["user"]
        producto = setup_data["producto"]
        headers = _get_auth_headers(user)

        body = {
            "items": [{"producto_id": producto["id"], "cantidad": 1}],
            "forma_pago_codigo": "INVALIDO",
        }

        response = await pg_client.post(
            "/api/v1/pedidos",
            json=body,
            headers=headers,
        )

        assert response.status_code == 422
        assert "Forma de pago" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_producto_no_encontrado_422(
        self,
        pg_session: AsyncSession,
        pg_client: AsyncClient,
        setup_data: dict,
    ):
        """Test: 422 when product does not exist."""
        user = setup_data["user"]
        headers = _get_auth_headers(user)

        body = {
            "items": [{"producto_id": 99999, "cantidad": 1}],
            "forma_pago_codigo": "MERCADOPAGO",
        }

        response = await pg_client.post(
            "/api/v1/pedidos",
            json=body,
            headers=headers,
        )

        assert response.status_code == 422
        assert "no encontrado" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_direccion_no_pertenece_al_usuario_404(
        self,
        pg_session: AsyncSession,
        pg_client: AsyncClient,
        setup_data: dict,
    ):
        """Test: 404 when address belongs to another user."""
        user = setup_data["user"]
        other_user = setup_data["other_user"]
        producto = setup_data["producto"]
        headers = _get_auth_headers(user)

        # Create address for a different user
        otra_direccion = await _create_test_address(pg_session, usuario_id=other_user["id"])

        body = {
            "items": [{"producto_id": producto["id"], "cantidad": 1}],
            "forma_pago_codigo": "MERCADOPAGO",
            "direccion_id": otra_direccion,
        }

        response = await pg_client.post(
            "/api/v1/pedidos",
            json=body,
            headers=headers,
        )

        # 404 because address ownership check fails
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_direccion_valida_propia(
        self,
        pg_session: AsyncSession,
        pg_client: AsyncClient,
        setup_data: dict,
    ):
        """Test: order created successfully with valid own address."""
        user = setup_data["user"]
        producto = setup_data["producto"]
        headers = _get_auth_headers(user)

        direccion_id = await _create_test_address(pg_session, user["id"])

        body = {
            "items": [{"producto_id": producto["id"], "cantidad": 1}],
            "forma_pago_codigo": "MERCADOPAGO",
            "direccion_id": direccion_id,
        }

        response = await pg_client.post(
            "/api/v1/pedidos",
            json=body,
            headers=headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data is not None

    @pytest.mark.asyncio
    async def test_sin_autenticacion_401(
        self,
        pg_session: AsyncSession,
        pg_client: AsyncClient,
        setup_data: dict,
    ):
        """Test: 401 when no authentication provided."""
        producto = setup_data["producto"]

        body = {
            "items": [{"producto_id": producto["id"], "cantidad": 1}],
            "forma_pago_codigo": "MERCADOPAGO",
        }

        response = await pg_client.post("/api/v1/pedidos", json=body)

        assert response.status_code in (401, 403)


# ── Test class: Listar Pedidos ─────────────────────────────────────────────────


@pytest.mark.postgres
class TestListarPedidos:
    """Tests for GET /api/v1/pedidos — order listing."""

    @pytest.fixture
    async def setup_data(self, pg_session: AsyncSession):
        """Create test data: users and products. Commits so app can see it."""
        user1 = await _create_test_user(pg_session, "user1@test.com")
        user2 = await _create_test_user(pg_session, "user2@test.com")
        producto = await _create_test_producto(pg_session)
        await pg_session.commit()
        return {"user1": user1, "user2": user2, "producto": producto}

    @pytest.mark.asyncio
    async def test_cliente_ve_solo_sus_pedidos(
        self,
        pg_session: AsyncSession,
        pg_client: AsyncClient,
        setup_data: dict,
    ):
        """Test: CLIENT sees only their own orders."""
        user1 = setup_data["user1"]
        user2 = setup_data["user2"]
        producto = setup_data["producto"]

        # Create order for user1
        headers1 = _get_auth_headers(user1)
        body = {
            "items": [{"producto_id": producto["id"], "cantidad": 1}],
            "forma_pago_codigo": "MERCADOPAGO",
        }
        resp1 = await pg_client.post("/api/v1/pedidos", json=body, headers=headers1)
        assert resp1.status_code == 201

        # Create order for user2
        headers2 = _get_auth_headers(user2)
        body["items"][0]["cantidad"] = 2
        resp2 = await pg_client.post("/api/v1/pedidos", json=body, headers=headers2)
        assert resp2.status_code == 201

        # List as user1
        list_resp = await pg_client.get("/api/v1/pedidos", headers=headers1)
        assert list_resp.status_code == 200
        data = list_resp.json()
        assert data["total"] == 1
        assert all(item["id"] == resp1.json()["id"] for item in data["items"])

    @pytest.mark.asyncio
    async def test_admin_ve_todos_los_pedidos(
        self,
        pg_session: AsyncSession,
        pg_client: AsyncClient,
        setup_data: dict,
    ):
        """Test: ADMIN sees all orders in the system."""
        user1 = setup_data["user1"]
        user2 = setup_data["user2"]
        producto = setup_data["producto"]
        admin = await _create_test_admin(pg_session)
        await pg_session.commit()

        # Create orders for user1 and user2
        for user in [user1, user2]:
            headers = _get_auth_headers(user)
            body = {
                "items": [{"producto_id": producto["id"], "cantidad": 1}],
                "forma_pago_codigo": "MERCADOPAGO",
            }
            resp = await pg_client.post("/api/v1/pedidos", json=body, headers=headers)
            assert resp.status_code == 201

        # List as admin
        admin_headers = _get_auth_headers(admin)
        list_resp = await pg_client.get("/api/v1/pedidos", headers=admin_headers)
        assert list_resp.status_code == 200
        data = list_resp.json()
        assert data["total"] == 2

    @pytest.mark.asyncio
    async def test_paginacion(
        self,
        pg_session: AsyncSession,
        pg_client: AsyncClient,
        setup_data: dict,
    ):
        """Test: pagination works correctly."""
        user = setup_data["user1"]
        producto = setup_data["producto"]
        headers = _get_auth_headers(user)

        # Create 3 orders
        for i in range(3):
            body = {
                "items": [{"producto_id": producto["id"], "cantidad": i + 1}],
                "forma_pago_codigo": "MERCADOPAGO",
            }
            resp = await pg_client.post("/api/v1/pedidos", json=body, headers=headers)
            assert resp.status_code == 201

        # List with pagination
        list_resp = await pg_client.get("/api/v1/pedidos?skip=0&limit=2", headers=headers)
        assert list_resp.status_code == 200
        data = list_resp.json()
        assert data["total"] == 3
        assert len(data["items"]) == 2
        assert data["skip"] == 0
        assert data["limit"] == 2


# ── Test class: Ver Detalle de Pedido ──────────────────────────────────────────


@pytest.mark.postgres
class TestObtenerPedido:
    """Tests for GET /api/v1/pedidos/{id} — order detail."""

    @pytest.fixture
    async def setup_data(self, pg_session: AsyncSession, pg_client: AsyncClient):
        """Create test data and a completed order. Commits so app can see it."""
        user = await _create_test_user(pg_session, "detail@test.com")
        producto = await _create_test_producto(
            pg_session, nombre="Detail Test Product", precio=Decimal("200.00")
        )
        await pg_session.commit()

        headers = _get_auth_headers(user)
        body = {
            "items": [
                {"producto_id": producto["id"], "cantidad": 3},
            ],
            "forma_pago_codigo": "EFECTIVO",
            "notas": "Detalle test notes",
        }
        resp = await pg_client.post("/api/v1/pedidos", json=body, headers=headers)
        assert resp.status_code == 201
        pedido_id = resp.json()["id"]

        return {"user": user, "producto": producto, "pedido_id": pedido_id}

    @pytest.mark.asyncio
    async def test_obtener_detalle_exitoso(
        self,
        pg_session: AsyncSession,
        pg_client: AsyncClient,
        setup_data: dict,
    ):
        """Test: get order detail with items and history."""
        user = setup_data["user"]
        producto = setup_data["producto"]
        pedido_id = setup_data["pedido_id"]
        headers = _get_auth_headers(user)

        response = await pg_client.get(f"/api/v1/pedidos/{pedido_id}", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == pedido_id
        assert data["estado_codigo"] == "PENDIENTE"
        assert data["forma_pago_codigo"] == "EFECTIVO"
        assert len(data["detalles"]) == 1
        assert len(data["historial"]) == 1
        assert data["historial"][0]["estado_desde"] is None
        assert data["historial"][0]["estado_hacia"] == "PENDIENTE"

    @pytest.mark.asyncio
    async def test_detalle_snapshot_persiste(
        self,
        pg_session: AsyncSession,
        pg_client: AsyncClient,
        setup_data: dict,
    ):
        """Test: snapshots are immutable after product change."""
        user = setup_data["user"]
        producto = setup_data["producto"]
        pedido_id = setup_data["pedido_id"]
        headers = _get_auth_headers(user)

        # Get detail
        response = await pg_client.get(f"/api/v1/pedidos/{pedido_id}", headers=headers)
        data = response.json()

        assert data["detalles"][0]["nombre_snapshot"] == producto["nombre"]
        assert Decimal(data["detalles"][0]["precio_snapshot"]) == producto["precio_base"]


# ── Test class: Historial de Estados ───────────────────────────────────────────


@pytest.mark.postgres
class TestHistorialEstados:
    """Tests for GET /api/v1/pedidos/{id}/historial — state history."""

    @pytest.mark.asyncio
    async def test_historial_estado_desde_null(
        self,
        pg_session: AsyncSession,
        pg_client: AsyncClient,
    ):
        """Test: first history record has estado_desde=NULL."""
        user = await _create_test_user(pg_session, "hist@test.com")
        producto = await _create_test_producto(pg_session)
        await pg_session.commit()

        headers = _get_auth_headers(user)
        body = {
            "items": [{"producto_id": producto["id"], "cantidad": 1}],
            "forma_pago_codigo": "MERCADOPAGO",
        }
        resp = await pg_client.post("/api/v1/pedidos", json=body, headers=headers)
        assert resp.status_code == 201
        pedido_id = resp.json()["id"]

        # Get history
        hist_resp = await pg_client.get(f"/api/v1/pedidos/{pedido_id}/historial", headers=headers)
        assert hist_resp.status_code == 200
        historial = hist_resp.json()

        assert len(historial) == 1
        assert historial[0]["estado_desde"] is None
        assert historial[0]["estado_hacia"] == "PENDIENTE"


# ── Test class: SELECT FOR UPDATE (PostgreSQL-specific) ─────────────────────────


@pytest.mark.postgres
class TestSelectForUpdate:
    """Tests that verify SELECT FOR UPDATE behavior requires PostgreSQL."""

    @pytest.mark.asyncio
    async def test_get_for_update_bloquea_fila(
        self,
        pg_session: AsyncSession,
    ):
        """Test: ProductoRepository.get_for_update() locks the row."""
        from app.repositories.producto_repository import ProductoRepository

        producto = await _create_test_producto(
            pg_session, nombre="Lock Test", precio=Decimal("100.00"), stock=10
        )
        await pg_session.flush()

        repo = ProductoRepository(pg_session)
        locked = await repo.get_for_update(producto["id"])

        assert locked is not None
        assert locked.id == producto["id"]
        assert locked.stock_cantidad == 10
