"""Integration tests for productos API endpoints — full stack with SQLite in-memory.

Covers CRUD operations, soft-delete, stock management, associations, pagination, RBAC.
Uses httpx AsyncClient against the actual FastAPI app with overridden DB.

Test scenarios (task 6.1-6.6):
  6.1: Create test_productos_api.py fixture
  6.2: Test POST/PUT/DELETE /api/v1/productos
  6.3: Test GET /api/v1/productos with filters and pagination
  6.4: Test stock management (PATCH /stock, PATCH /disponibilidad)
  6.5: Test category/ingredient associations
  6.6: Test RBAC (permissions by role)
"""
import pytest
from decimal import Decimal
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.main import app
from app.database import Base, get_db
from app.models.rol import Rol
from app.models.usuario import Usuario
from app.models.usuario_rol import UsuarioRol
from app.models.categoria import Categoria
from app.models.ingrediente import Ingrediente
from app.models.producto import Producto
from app.security import create_access_token

pytestmark = pytest.mark.asyncio

# Counter for unique user/email generation
_user_counter = 0


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture
async def test_engine():
    """Create SQLite in-memory engine with all tables. Function scope for isolation."""
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
    """Fresh session per test."""
    async_session = async_sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session


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


async def _create_user_with_role(db_session, role_code: str, prefix: str) -> tuple[str, int]:
    """Helper: create user with role and return (token, user_id)."""
    global _user_counter
    _user_counter += 1
    
    stmt = select(Rol).where(Rol.codigo == role_code)
    result = await db_session.execute(stmt)
    role = result.scalars().first()
    
    if not role:
        role = Rol(codigo=role_code, descripcion=role_code)
        db_session.add(role)
        await db_session.flush()
    
    user = Usuario(
        nombre=prefix.title(),
        apellido="Test",
        email=f"{prefix.lower()}{_user_counter}@t.co",
        password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.G7xJBbJE8YxBm",  # Test1234!
    )
    db_session.add(user)
    await db_session.flush()
    
    user_role = UsuarioRol(usuario_id=user.id, rol_codigo=role.codigo)
    db_session.add(user_role)
    await db_session.commit()
    
    token = create_access_token({
        "sub": str(user.id),
        "email": user.email,
        "roles": [role_code],
    })
    return token, user.id


@pytest.fixture
async def admin_token(db_session) -> str:
    """Create admin user and return access token."""
    token, _ = await _create_user_with_role(db_session, "ADMIN", "Admin")
    return token


@pytest.fixture
async def stock_token(db_session) -> str:
    """Create stock user and return access token."""
    token, _ = await _create_user_with_role(db_session, "STOCK", "Stock")
    return token


@pytest.fixture
async def client_token(db_session) -> str:
    """Create client user and return access token."""
    token, _ = await _create_user_with_role(db_session, "CLIENT", "Client")
    return token


@pytest.fixture
async def pedidos_token(db_session) -> str:
    """Create pedidos user and return access token."""
    token, _ = await _create_user_with_role(db_session, "PEDIDOS", "Pedidos")
    return token


# ── Helper to create test data ─────────────────────────────────────────────────

async def create_test_producto(client, token, nombre="Pizza Margherita", precio=Decimal("150.00")) -> dict:
    """Create a test producto and return the response data."""
    payload = {
        "nombre": nombre,
        "descripcion": "Pizza clásica italiana",
        "precio_base": str(precio),
        "stock_cantidad": 50,
        "disponible": True,
    }
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.post("/api/v1/productos", json=payload, headers=headers)
    return response.json()


# ── Task 6.2: CRUD Tests ──────────────────────────────────────────────────────

class TestProductoCRUD:
    """6.2: Tests for CRUD operations on productos."""

    async def test_create_producto_success(self, client, admin_token):
        """6.2a: Successful creation returns 201 with ProductoRead data."""
        payload = {
            "nombre": "Empanada de Carne",
            "descripcion": "Empanada criolla",
            "precio_base": "50.00",
            "stock_cantidad": 100,
            "disponible": True,
        }
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = await client.post("/api/v1/productos", json=payload, headers=headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["nombre"] == "Empanada de Carne"
        assert Decimal(data["precio_base"]) == Decimal("50.00")
        assert data["id"] is not None
        assert "created_at" in data
        assert "updated_at" in data
        assert data["deleted_at"] is None

    async def test_create_producto_duplicate_name(self, client, admin_token):
        """6.2b: Duplicate name returns 409 Conflict."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Create first product
        payload1 = {"nombre": "Taco", "precio_base": "80.00", "stock_cantidad": 20}
        resp1 = await client.post("/api/v1/productos", json=payload1, headers=headers)
        assert resp1.status_code == 201
        
        # Try to create duplicate
        payload2 = {"nombre": "Taco", "precio_base": "90.00"}
        resp2 = await client.post("/api/v1/productos", json=payload2, headers=headers)
        assert resp2.status_code == 409

    async def test_create_producto_negative_price(self, client, admin_token):
        """6.2c: Negative price returns 422."""
        payload = {"nombre": "Test", "precio_base": "-10.00"}
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = await client.post("/api/v1/productos", json=payload, headers=headers)
        assert response.status_code == 422

    async def test_create_producto_unauthorized_role(self, client, client_token):
        """6.2d: CLIENT role (unauthorized) returns 403."""
        payload = {"nombre": "Test", "precio_base": "10.00"}
        headers = {"Authorization": f"Bearer {client_token}"}
        response = await client.post("/api/v1/productos", json=payload, headers=headers)
        assert response.status_code == 403

    async def test_create_producto_stock_role_allowed(self, client, stock_token):
        """6.2d: STOCK role can create products."""
        payload = {"nombre": "Stock Product", "precio_base": "25.00", "stock_cantidad": 10}
        headers = {"Authorization": f"Bearer {stock_token}"}
        response = await client.post("/api/v1/productos", json=payload, headers=headers)
        assert response.status_code == 201

    async def test_get_producto_success(self, client, admin_token):
        """6.2e: Get existing product returns 200 with full detail."""
        producto = await create_test_producto(client, admin_token, "Arepa")
        
        response = await client.get(f"/api/v1/productos/{producto['id']}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == producto["id"]
        assert data["nombre"] == "Arepa"
        assert "stock_cantidad" in data
        assert "categorias" in data
        assert "ingredientes" in data

    async def test_get_producto_not_found(self, client):
        """6.2f: Non-existent product returns 404."""
        response = await client.get("/api/v1/productos/999")
        assert response.status_code == 404

    async def test_update_producto_success(self, client, admin_token):
        """6.2g: Successful update returns 200."""
        producto = await create_test_producto(client, admin_token, "Sushi")
        
        payload = {"nombre": "Sushi Premium", "precio_base": "300.00"}
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = await client.put(
            f"/api/v1/productos/{producto['id']}", 
            json=payload, 
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["nombre"] == "Sushi Premium"
        assert Decimal(data["precio_base"]) == Decimal("300.00")

    async def test_update_producto_not_found(self, client, admin_token):
        """6.2h: Update non-existent returns 404."""
        payload = {"nombre": "Test"}
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = await client.put("/api/v1/productos/999", json=payload, headers=headers)
        assert response.status_code == 404

    async def test_delete_producto_success(self, client, admin_token, db_session):
        """6.2i: Soft delete returns 204 and marks deleted_at."""
        producto = await create_test_producto(client, admin_token, "TempProduct")
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        response_del = await client.delete(
            f"/api/v1/productos/{producto['id']}", 
            headers=headers
        )
        assert response_del.status_code == 204
        
        # Verify in DB
        stmt = select(Producto).where(Producto.id == producto["id"])
        result = await db_session.execute(stmt)
        row = result.scalars().first()
        assert row is not None
        assert row.deleted_at is not None

    async def test_delete_producto_unauthorized(self, client, stock_token):
        """6.2j: STOCK role cannot delete (only ADMIN)."""
        producto = await create_test_producto(client, stock_token, "StockProduct")
        
        # STOCK can create but NOT delete
        headers = {"Authorization": f"Bearer {stock_token}"}
        response = await client.delete(f"/api/v1/productos/{producto['id']}", headers=headers)
        assert response.status_code == 403


# ── Task 6.3: Filters and Pagination Tests ────────────────────────────────────

class TestProductoFiltersPagination:
    """6.3: Tests for filtering and pagination on producto listing."""

    async def test_list_productos_empty(self, client):
        """6.3a: Empty list returns 200 with empty items."""
        response = await client.get("/api/v1/productos")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["skip"] == 0
        assert data["limit"] == 20

    async def test_list_productos_basic(self, client, admin_token):
        """6.3b: List returns products with correct structure."""
        # Create 3 products
        for nombre in ["Hamburguesa", "Hot Dog", "Panchos"]:
            await create_test_producto(client, admin_token, nombre)
        
        response = await client.get("/api/v1/productos")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 3
        # Public endpoint hides stock_cantidad
        assert "stock_cantidad" not in data["items"][0]

    async def test_list_productos_pagination(self, client, admin_token):
        """6.3c: Pagination with skip/limit works correctly."""
        # Create 25 products
        for i in range(25):
            await create_test_producto(client, admin_token, f"Product{i:02d}")
        
        # First page
        response1 = await client.get("/api/v1/productos?skip=0&limit=10")
        assert response1.status_code == 200
        data1 = response1.json()
        assert len(data1["items"]) == 10
        assert data1["total"] >= 25
        assert data1["skip"] == 0
        assert data1["limit"] == 10
        
        # Second page
        response2 = await client.get("/api/v1/productos?skip=10&limit=10")
        assert response2.status_code == 200
        data2 = response2.json()
        assert len(data2["items"]) == 10
        assert data2["skip"] == 10

    async def test_list_productos_filter_disponible(self, client, admin_token):
        """6.3d: Filter by disponible=true/false."""
        # Create available and unavailable products
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Available product
        payload1 = {"nombre": "Available1", "precio_base": "10.00", "disponible": True}
        await client.post("/api/v1/productos", json=payload1, headers=headers)
        
        # Unavailable product
        payload2 = {"nombre": "Unavailable1", "precio_base": "20.00", "disponible": False}
        await client.post("/api/v1/productos", json=payload2, headers=headers)
        
        # Filter only available
        response = await client.get("/api/v1/productos?disponible=true")
        assert response.status_code == 200
        data = response.json()
        assert all(item["disponible"] is True for item in data["items"])

    async def test_list_productos_search(self, client, admin_token):
        """6.3e: Search by name (case-insensitive)."""
        await create_test_producto(client, admin_token, "Pizza Napolitana")
        await create_test_producto(client, admin_token, "Pizzza Carbonara")
        
        response = await client.get("/api/v1/productos?busqueda=pizza")
        assert response.status_code == 200
        data = response.json()
        # Should find "Pizza Napolitana" (case-insensitive match)
        nombres = [item["nombre"] for item in data["items"]]
        assert any("Pizza" in n for n in nombres)

    async def test_list_productos_excludes_soft_deleted(self, client, admin_token):
        """6.3f: Soft-deleted products excluded from listing."""
        producto = await create_test_producto(client, admin_token, "ToDelete")
        
        # Delete it
        headers = {"Authorization": f"Bearer {admin_token}"}
        await client.delete(f"/api/v1/productos/{producto['id']}", headers=headers)
        
        # List and verify it's gone
        response = await client.get("/api/v1/productos")
        names = [item["nombre"] for item in response.json()["items"]]
        assert "ToDelete" not in names


# ── Task 6.4: Stock Management Tests ─────────────────────────────────────────

class TestProductoStock:
    """6.4: Tests for stock management endpoints."""

    async def test_update_stock_success(self, client, stock_token):
        """6.4a: Update stock returns 200 with updated value."""
        producto = await create_test_producto(client, stock_token, "StockTest", Decimal("100.00"))
        
        headers = {"Authorization": f"Bearer {stock_token}"}
        response = await client.patch(
            f"/api/v1/productos/{producto['id']}/stock",
            json={"stock_cantidad": 75},
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["stock_cantidad"] == 75

    async def test_update_stock_negative(self, client, stock_token):
        """6.4b: Negative stock returns 422."""
        producto = await create_test_producto(client, stock_token, "StockTest2")
        
        headers = {"Authorization": f"Bearer {stock_token}"}
        response = await client.patch(
            f"/api/v1/productos/{producto['id']}/stock",
            json={"stock_cantidad": -5},
            headers=headers
        )
        assert response.status_code == 422

    async def test_update_stock_not_found(self, client, stock_token):
        """6.4c: Update stock for non-existent product returns 404."""
        headers = {"Authorization": f"Bearer {stock_token}"}
        response = await client.patch(
            "/api/v1/productos/999/stock",
            json={"stock_cantidad": 10},
            headers=headers
        )
        assert response.status_code == 404

    async def test_toggle_disponibilidad_success(self, client, stock_token):
        """6.4d: Toggle disponibilidad returns 200 with updated value."""
        producto = await create_test_producto(client, stock_token, "AvailTest")
        
        headers = {"Authorization": f"Bearer {stock_token}"}
        
        # Disable
        response1 = await client.patch(
            f"/api/v1/productos/{producto['id']}/disponibilidad",
            json={"disponible": False},
            headers=headers
        )
        assert response1.status_code == 200
        assert response1.json()["disponible"] is False
        
        # Re-enable
        response2 = await client.patch(
            f"/api/v1/productos/{producto['id']}/disponibilidad",
            json={"disponible": True},
            headers=headers
        )
        assert response2.status_code == 200
        assert response2.json()["disponible"] is True

    async def test_toggle_disponibilidad_unauthorized(self, client, client_token):
        """6.4e: CLIENT role cannot toggle disponibilidad."""
        headers = {"Authorization": f"Bearer {client_token}"}
        response = await client.patch(
            "/api/v1/productos/1/disponibilidad",
            json={"disponible": False},
            headers=headers
        )
        assert response.status_code == 403


# ── Task 6.5: Association Tests ───────────────────────────────────────────────

class TestProductoAssociations:
    """6.5: Tests for category and ingredient associations."""

    async def _create_category(self, client, admin_token, nombre="Bebidas") -> int:
        """Helper to create a category and return its ID."""
        payload = {"nombre": nombre}
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = await client.post("/api/v1/categorias", json=payload, headers=headers)
        return response.json()["id"]

    async def _create_ingrediente(self, client, admin_token, nombre="Tomate", es_alergeno=False) -> int:
        """Helper to create an ingrediente and return its ID."""
        payload = {"nombre": nombre, "es_alergeno": es_alergeno}
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = await client.post("/api/v1/ingredientes", json=payload, headers=headers)
        return response.json()["id"]

    async def test_add_categoria_success(self, client, admin_token):
        """6.5a: Add category to product returns 201."""
        producto = await create_test_producto(client, admin_token, "TestProd")
        categoria_id = await self._create_category(client, admin_token, "Comida Italiana")
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = await client.post(
            f"/api/v1/productos/{producto['id']}/categorias",
            json={"categoria_id": categoria_id, "es_principal": True},
            headers=headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["categoria_id"] == categoria_id
        assert data["es_principal"] is True

    async def test_add_categoria_duplicate(self, client, admin_token):
        """6.5b: Duplicate category association returns 409."""
        producto = await create_test_producto(client, admin_token, "TestProd2")
        categoria_id = await self._create_category(client, admin_token, "Comida Rápida")
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # First association
        await client.post(
            f"/api/v1/productos/{producto['id']}/categorias",
            json={"categoria_id": categoria_id},
            headers=headers
        )
        
        # Duplicate
        response2 = await client.post(
            f"/api/v1/productos/{producto['id']}/categorias",
            json={"categoria_id": categoria_id},
            headers=headers
        )
        assert response2.status_code == 409

    async def test_add_categoria_not_found(self, client, admin_token):
        """6.5c: Adding non-existent category returns 404."""
        producto = await create_test_producto(client, admin_token, "TestProd3")
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = await client.post(
            f"/api/v1/productos/{producto['id']}/categorias",
            json={"categoria_id": 999},
            headers=headers
        )
        assert response.status_code == 404

    async def test_remove_categoria_success(self, client, admin_token):
        """6.5d: Remove category returns 204."""
        producto = await create_test_producto(client, admin_token, "TestProd4")
        categoria_id = await self._create_category(client, admin_token, "Postres")
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Add
        await client.post(
            f"/api/v1/productos/{producto['id']}/categorias",
            json={"categoria_id": categoria_id},
            headers=headers
        )
        
        # Remove
        response = await client.delete(
            f"/api/v1/productos/{producto['id']}/categorias/{categoria_id}",
            headers=headers
        )
        assert response.status_code == 204

    async def test_add_ingrediente_success(self, client, admin_token):
        """6.5e: Add ingredient to product returns 201."""
        producto = await create_test_producto(client, admin_token, "TestProd5")
        ingrediente_id = await self._create_ingrediente(client, admin_token, "Queso", True)
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = await client.post(
            f"/api/v1/productos/{producto['id']}/ingredientes",
            json={"ingrediente_id": ingrediente_id, "es_removible": True},
            headers=headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["ingrediente_id"] == ingrediente_id
        assert data["es_removible"] is True

    async def test_add_ingrediente_allergen_display(self, client, admin_token):
        """6.5f: Allergen flag is displayed in ingredient list."""
        producto = await create_test_producto(client, admin_token, "TestProd6")
        ingrediente_id = await self._create_ingrediente(client, admin_token, "Maní", True)
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        await client.post(
            f"/api/v1/productos/{producto['id']}/ingredientes",
            json={"ingrediente_id": ingrediente_id, "es_removible": False},
            headers=headers
        )
        
        # List ingredientes
        response = await client.get(f"/api/v1/productos/{producto['id']}/ingredientes")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["ingrediente"]["es_alergeno"] is True

    async def test_remove_ingrediente_success(self, client, admin_token):
        """6.5g: Remove ingredient returns 204."""
        producto = await create_test_producto(client, admin_token, "TestProd7")
        ingrediente_id = await self._create_ingrediente(client, admin_token, "Cebolla")
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Add
        await client.post(
            f"/api/v1/productos/{producto['id']}/ingredientes",
            json={"ingrediente_id": ingrediente_id},
            headers=headers
        )
        
        # Remove
        response = await client.delete(
            f"/api/v1/productos/{producto['id']}/ingredientes/{ingrediente_id}",
            headers=headers
        )
        assert response.status_code == 204


# ── Task 6.6: RBAC Tests ─────────────────────────────────────────────────────

class TestProductoRBAC:
    """6.6: Tests for role-based access control on productos."""

    async def test_create_requires_auth_or_role(self, client):
        """6.6a: Create without token returns 403/401."""
        payload = {"nombre": "Test", "precio_base": "10.00"}
        response = await client.post("/api/v1/productos", json=payload)
        assert response.status_code in [401, 403]

    async def test_admin_can_create_and_delete(self, client, admin_token):
        """6.6b: ADMIN role can create and delete products."""
        producto = await create_test_producto(client, admin_token, "AdminProd")
        
        # ADMIN can delete
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = await client.delete(f"/api/v1/productos/{producto['id']}", headers=headers)
        assert response.status_code == 204

    async def test_stock_can_create_and_update_stock_but_not_delete(self, client, stock_token, admin_token):
        """6.6c: STOCK can create, update stock, but NOT delete."""
        # Create
        producto = await create_test_producto(client, stock_token, "StockProd")
        
        # Update stock
        headers = {"Authorization": f"Bearer {stock_token}"}
        response = await client.patch(
            f"/api/v1/productos/{producto['id']}/stock",
            json={"stock_cantidad": 25},
            headers=headers
        )
        assert response.status_code == 200
        
        # Cannot delete
        response_del = await client.delete(
            f"/api/v1/productos/{producto['id']}", 
            headers=headers
        )
        assert response_del.status_code == 403

    async def test_client_can_only_read(self, client, client_token):
        """6.6d: CLIENT role can read (public) but not write."""
        # Can read public list
        response_list = await client.get("/api/v1/productos")
        assert response_list.status_code == 200
        
        # Cannot create
        payload = {"nombre": "ClientProduct", "precio_base": "10.00"}
        headers = {"Authorization": f"Bearer {client_token}"}
        response_create = await client.post("/api/v1/productos", json=payload, headers=headers)
        assert response_create.status_code == 403
        
        # Cannot update stock
        response_stock = await client.patch(
            "/api/v1/productos/1/stock",
            json={"stock_cantidad": 10},
            headers=headers
        )
        assert response_stock.status_code == 403

    async def test_pedidos_role_cannot_access_products(self, client, pedidos_token):
        """6.6e: PEDIDOS role has no access to productos."""
        headers = {"Authorization": f"Bearer {pedidos_token}"}
        
        # Cannot create
        response_create = await client.post(
            "/api/v1/productos",
            json={"nombre": "PedidosProduct", "precio_base": "10.00"},
            headers=headers
        )
        assert response_create.status_code == 403
        
        # Cannot update stock
        response_stock = await client.patch(
            "/api/v1/productos/1/stock",
            json={"stock_cantidad": 10},
            headers=headers
        )
        assert response_stock.status_code == 403