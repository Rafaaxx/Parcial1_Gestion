"""Integration tests for categorías API endpoints — full stack with SQLite in-memory.

Covers hierarchical category creation, retrieval, updates, soft-delete, cycle detection,
and RBAC enforcement. Uses httpx AsyncClient against the actual FastAPI app with overridden DB.

Test scenarios (16 total):
  3.1 🔴 RED  — Write 11 integration test scenarios
  3.2 🟢 GREEN — Apply migration, run tests (all should pass)
  3.3 Verify soft-delete: POST → DELETE → GET → 404, check deleted_at
  3.4 Verify RBAC: CLIENTE POST → 403, STOCK DELETE → 403
  3.5 Verify cycle detection: PUT with cycle → 400/422
  3.6 Verify cascade: DELETE with children → 409
"""

import uuid
from typing import Optional

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import Base, get_db
from app.main import app
from app.models.categoria import Categoria
from app.models.rol import Rol
from app.models.usuario import Usuario
from app.models.usuario_rol import UsuarioRol
from app.security import create_access_token

pytestmark = pytest.mark.asyncio

# Counter for unique user generation
_user_counter = 0


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
async def admin_token(db_session) -> str:
    """Create admin user and return access token."""
    global _user_counter
    _user_counter += 1

    # Get or create admin role
    stmt = select(Rol).where(Rol.codigo == "ADMIN")
    result = await db_session.execute(stmt)
    admin_role = result.scalars().first()

    if not admin_role:
        admin_role = Rol(codigo="ADMIN", descripcion="Administrador")
        db_session.add(admin_role)
        await db_session.flush()

    # Create admin user with SHORT email (bcrypt 72-byte limit)
    admin_user = Usuario(
        nombre="Admin",
        apellido="User",
        email=f"a{_user_counter}@t.co",
        password_hash="$2b$12$YDVTg/XbOQ1Ny6yGg5btJu1gpJf6vs8HLvW94TrtIHoS5yFsKfy3G",
    )
    db_session.add(admin_user)
    await db_session.flush()

    # Assign admin role
    user_role = UsuarioRol(usuario_id=admin_user.id, rol_codigo=admin_role.codigo)
    db_session.add(user_role)
    await db_session.commit()

    # Generate token
    token = create_access_token(
        {
            "sub": str(admin_user.id),
            "email": admin_user.email,
            "roles": ["ADMIN"],
        }
    )
    return token


@pytest.fixture
async def stock_token(db_session) -> str:
    """Create stock user and return access token."""
    global _user_counter
    _user_counter += 1

    # Get or create stock role
    stmt = select(Rol).where(Rol.codigo == "STOCK")
    result = await db_session.execute(stmt)
    stock_role = result.scalars().first()

    if not stock_role:
        stock_role = Rol(codigo="STOCK", descripcion="Gestor de stock")
        db_session.add(stock_role)
        await db_session.flush()

    # Create stock user with SHORT email (bcrypt 72-byte limit)
    stock_user = Usuario(
        nombre="Stock",
        apellido="User",
        email=f"s{_user_counter}@t.co",
        password_hash="$2b$12$YDVTg/XbOQ1Ny6yGg5btJu1gpJf6vs8HLvW94TrtIHoS5yFsKfy3G",
    )
    db_session.add(stock_user)
    await db_session.flush()

    # Assign stock role
    user_role = UsuarioRol(usuario_id=stock_user.id, rol_codigo=stock_role.codigo)
    db_session.add(user_role)
    await db_session.commit()

    # Generate token
    token = create_access_token(
        {
            "sub": str(stock_user.id),
            "email": stock_user.email,
            "roles": ["STOCK"],
        }
    )
    return token


@pytest.fixture
async def client_token(db_session) -> str:
    """Create client user and return access token."""
    global _user_counter
    _user_counter += 1

    # Get or create client role
    stmt = select(Rol).where(Rol.codigo == "CLIENT")
    result = await db_session.execute(stmt)
    client_role = result.scalars().first()

    if not client_role:
        client_role = Rol(codigo="CLIENT", descripcion="Cliente")
        db_session.add(client_role)
        await db_session.flush()

    # Create client user with SHORT email (bcrypt 72-byte limit)
    client_user = Usuario(
        nombre="Client",
        apellido="User",
        email=f"c{_user_counter}@t.co",
        password_hash="$2b$12$YDVTg/XbOQ1Ny6yGg5btJu1gpJf6vs8HLvW94TrtIHoS5yFsKfy3G",
    )
    db_session.add(client_user)
    await db_session.flush()

    # Assign client role
    user_role = UsuarioRol(usuario_id=client_user.id, rol_codigo=client_role.codigo)
    db_session.add(user_role)
    await db_session.commit()

    # Generate token
    token = create_access_token(
        {
            "sub": str(client_user.id),
            "email": client_user.email,
            "roles": ["CLIENT"],
        }
    )
    return token


# ── Test Classes ──────────────────────────────────────────────────────────────


class TestCategoriaIntegration:
    """Integration tests: real DB + real HTTP layer for categorías API."""

    async def test_create_root_category_success(self, client, admin_token):
        """Test 3.1: Create root category (parent_id=None) → 201, saved to DB"""
        payload = {
            "nombre": "Bebidas",
            "descripcion": "Bebidas frías y calientes",
            "parent_id": None,
        }

        headers = {"Authorization": f"Bearer {admin_token}"}
        response = await client.post("/api/v1/categorias", json=payload, headers=headers)

        assert response.status_code == 201
        data = response.json()
        assert data["nombre"] == "Bebidas"
        assert data["descripcion"] == "Bebidas frías y calientes"
        assert data["parent_id"] is None
        assert data["id"] is not None
        assert "deleted_at" in data
        assert data["deleted_at"] is None

    async def test_create_subcategory_with_parent_success(self, client, admin_token, db_session):
        """Test 3.1: Create subcategory with parent_id → 201, FK verified"""
        # First create parent
        parent_payload = {"nombre": "Bebidas", "parent_id": None}
        headers = {"Authorization": f"Bearer {admin_token}"}
        parent_resp = await client.post("/api/v1/categorias", json=parent_payload, headers=headers)
        parent_id = parent_resp.json()["id"]

        # Create child
        child_payload = {"nombre": "Alcohólicas", "parent_id": parent_id}
        response = await client.post("/api/v1/categorias", json=child_payload, headers=headers)

        assert response.status_code == 201
        data = response.json()
        assert data["parent_id"] == parent_id
        assert data["nombre"] == "Alcohólicas"

        # Verify in DB with FK constraint
        stmt = select(Categoria).where(Categoria.id == parent_id)
        result = await db_session.execute(stmt)
        parent = result.scalars().first()
        assert parent is not None
        assert parent.nombre == "Bebidas"

    async def test_create_nonexistent_parent_fails(self, client, admin_token):
        """Test 3.1: POST with nonexistent parent_id → 400/404"""
        fake_parent = 99999  # Use a large integer that doesn't exist
        payload = {"nombre": "Orphan", "parent_id": fake_parent}
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = await client.post("/api/v1/categorias", json=payload, headers=headers)

        # Service raises AppException → router converts to HTTPException
        assert response.status_code in [400, 404]
        assert "detail" in response.json()

    async def test_get_categories_tree_nested_structure(self, client, admin_token):
        """Test 3.1: GET /api/v1/categorias returns nested tree structure"""
        headers = {"Authorization": f"Bearer {admin_token}"}

        # Create: root → child1, child2
        root_payload = {"nombre": "Comidas", "parent_id": None}
        root_resp = await client.post("/api/v1/categorias", json=root_payload, headers=headers)
        root_id = root_resp.json()["id"]

        child1_payload = {"nombre": "Pizzas", "parent_id": root_id}
        await client.post("/api/v1/categorias", json=child1_payload, headers=headers)

        child2_payload = {"nombre": "Pastas", "parent_id": root_id}
        await client.post("/api/v1/categorias", json=child2_payload, headers=headers)

        # Get tree (public endpoint, no auth required)
        response = await client.get("/api/v1/categorias")

        assert response.status_code == 200
        tree = response.json()
        assert len(tree) > 0

        root = next((cat for cat in tree if cat["nombre"] == "Comidas"), None)
        assert root is not None
        assert root["id"] == root_id
        assert len(root.get("subcategorias", [])) >= 2

    async def test_get_single_category_by_id(self, client, admin_token):
        """Test 3.1: GET /api/v1/categorias/{id} returns single category"""
        headers = {"Authorization": f"Bearer {admin_token}"}

        # Create
        payload = {"nombre": "Bebidas", "parent_id": None}
        create_resp = await client.post("/api/v1/categorias", json=payload, headers=headers)
        categoria_id = create_resp.json()["id"]

        # Get (public endpoint)
        response = await client.get(f"/api/v1/categorias/{categoria_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == categoria_id
        assert data["nombre"] == "Bebidas"

    async def test_get_nonexistent_category_returns_404(self, client):
        """Test 3.1: GET /api/v1/categorias/{nonexistent} → 404"""
        fake_id = 99999  # Use a large integer that doesn't exist
        response = await client.get(f"/api/v1/categorias/{fake_id}")

        assert response.status_code == 404
        assert "detail" in response.json()

    async def test_update_category_name_success(self, client, admin_token):
        """Test 3.1: PUT updates category name → 200"""
        headers = {"Authorization": f"Bearer {admin_token}"}

        # Create
        payload = {"nombre": "Original Name", "parent_id": None}
        create_resp = await client.post("/api/v1/categorias", json=payload, headers=headers)
        categoria_id = create_resp.json()["id"]

        # Update
        update_payload = {"nombre": "Updated Name"}
        response = await client.put(
            f"/api/v1/categorias/{categoria_id}", json=update_payload, headers=headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["nombre"] == "Updated Name"

    async def test_update_category_reparent_success(self, client, admin_token):
        """Test 3.1: PUT changes parent_id → 200"""
        headers = {"Authorization": f"Bearer {admin_token}"}

        # Create parent1, parent2, child
        parent1_resp = await client.post(
            "/api/v1/categorias", json={"nombre": "Parent1", "parent_id": None}, headers=headers
        )
        parent1_id = parent1_resp.json()["id"]

        parent2_resp = await client.post(
            "/api/v1/categorias", json={"nombre": "Parent2", "parent_id": None}, headers=headers
        )
        parent2_id = parent2_resp.json()["id"]

        child_resp = await client.post(
            "/api/v1/categorias", json={"nombre": "Child", "parent_id": parent1_id}, headers=headers
        )
        child_id = child_resp.json()["id"]

        # Reparent child to parent2
        response = await client.put(
            f"/api/v1/categorias/{child_id}", json={"parent_id": parent2_id}, headers=headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["parent_id"] == parent2_id

    async def test_soft_delete_category_without_children(self, client, admin_token, db_session):
        """Test 3.3: DELETE soft-deletes → 204, deleted_at populated, GET returns 404"""
        headers = {"Authorization": f"Bearer {admin_token}"}

        # Create
        payload = {"nombre": "Temporary", "parent_id": None}
        create_resp = await client.post("/api/v1/categorias", json=payload, headers=headers)
        categoria_id = create_resp.json()["id"]

        # Delete
        response = await client.delete(f"/api/v1/categorias/{categoria_id}", headers=headers)
        assert response.status_code == 204

        # Verify GET returns 404 (soft-delete filtering)
        get_response = await client.get(f"/api/v1/categorias/{categoria_id}")
        assert get_response.status_code == 404

        # Verify in DB: deleted_at IS NOT NULL
        stmt = select(Categoria).where(Categoria.id == categoria_id)
        result = await db_session.execute(stmt)
        db_cat = result.scalars().first()
        assert db_cat is not None
        assert db_cat.deleted_at is not None

    async def test_delete_category_with_children_returns_409(self, client, admin_token):
        """Test 3.6: DELETE with children → 409 Conflict"""
        headers = {"Authorization": f"Bearer {admin_token}"}

        # Create parent & child
        parent_resp = await client.post(
            "/api/v1/categorias", json={"nombre": "Parent", "parent_id": None}, headers=headers
        )
        parent_id = parent_resp.json()["id"]

        await client.post(
            "/api/v1/categorias", json={"nombre": "Child", "parent_id": parent_id}, headers=headers
        )

        # Try to delete parent
        response = await client.delete(f"/api/v1/categorias/{parent_id}", headers=headers)

        assert response.status_code == 409
        error_detail = response.json()["detail"].lower()
        assert "children" in error_detail or "conflict" in error_detail

    async def test_cycle_detection_self_reference(self, client, admin_token):
        """Test 3.5: PUT with self-reference → 400"""
        headers = {"Authorization": f"Bearer {admin_token}"}

        # Create
        payload = {"nombre": "Category", "parent_id": None}
        create_resp = await client.post("/api/v1/categorias", json=payload, headers=headers)
        categoria_id = create_resp.json()["id"]

        # Try to set parent to self
        response = await client.put(
            f"/api/v1/categorias/{categoria_id}", json={"parent_id": categoria_id}, headers=headers
        )

        assert response.status_code == 400
        error_detail = response.json()["detail"].lower()
        assert "self" in error_detail or "cannot" in error_detail

    async def test_cycle_detection_indirect_cycle(self, client, admin_token):
        """Test 3.5: PUT creating indirect cycle → 400/422"""
        headers = {"Authorization": f"Bearer {admin_token}"}

        # Create: A → B → C
        a_resp = await client.post(
            "/api/v1/categorias", json={"nombre": "A", "parent_id": None}, headers=headers
        )
        a_id = a_resp.json()["id"]

        b_resp = await client.post(
            "/api/v1/categorias", json={"nombre": "B", "parent_id": a_id}, headers=headers
        )
        b_id = b_resp.json()["id"]

        c_resp = await client.post(
            "/api/v1/categorias", json={"nombre": "C", "parent_id": b_id}, headers=headers
        )
        c_id = c_resp.json()["id"]

        # Try to set A parent to C (cycle: A → B → C → A)
        response = await client.put(
            f"/api/v1/categorias/{a_id}", json={"parent_id": c_id}, headers=headers
        )

        assert response.status_code in [400, 422]
        error_detail = response.json()["detail"].lower()
        assert "cycle" in error_detail or "cannot" in error_detail

    async def test_rbac_client_cannot_create_category(self, client, client_token):
        """Test 3.4: CLIENT role POST → 403"""
        payload = {"nombre": "Test", "parent_id": None}
        headers = {"Authorization": f"Bearer {client_token}"}
        response = await client.post("/api/v1/categorias", json=payload, headers=headers)

        assert response.status_code == 403

    async def test_rbac_stock_cannot_delete(self, client, admin_token, stock_token):
        """Test 3.4: STOCK role DELETE → 403"""
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        stock_headers = {"Authorization": f"Bearer {stock_token}"}

        # Create as admin
        payload = {"nombre": "Category", "parent_id": None}
        create_resp = await client.post("/api/v1/categorias", json=payload, headers=admin_headers)
        categoria_id = create_resp.json()["id"]

        # Try delete as STOCK
        response = await client.delete(f"/api/v1/categorias/{categoria_id}", headers=stock_headers)

        assert response.status_code == 403

    async def test_rbac_stock_can_create_and_update(self, client, stock_token):
        """Test 3.4: STOCK role CAN create and update (not delete)"""
        payload = {"nombre": "StockCategory", "parent_id": None}
        headers = {"Authorization": f"Bearer {stock_token}"}

        # Create
        response = await client.post("/api/v1/categorias", json=payload, headers=headers)
        assert response.status_code == 201
        categoria_id = response.json()["id"]

        # Update
        response = await client.put(
            f"/api/v1/categorias/{categoria_id}", json={"nombre": "Updated"}, headers=headers
        )
        assert response.status_code == 200


# ── Test Unauthenticated Access ───────────────────────────────────────────


class TestCategoriaAuth:
    """Test authentication and authorization for categorías endpoints."""

    async def test_get_public_no_auth_required(self, client):
        """Test: GET /api/v1/categorias is public (no auth required)"""
        response = await client.get("/api/v1/categorias")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    async def test_create_unauthenticated_returns_401(self, client):
        """Test: POST without token → 401"""
        payload = {"nombre": "Test", "parent_id": None}
        response = await client.post("/api/v1/categorias", json=payload)

        # Should be 401 (unauthorized) or 403 (forbidden) depending on implementation
        assert response.status_code in [401, 403]

    async def test_update_unauthenticated_returns_401(self, client, admin_token):
        """Test: PUT without token → 401"""
        admin_headers = {"Authorization": f"Bearer {admin_token}"}

        # Create category first
        payload = {"nombre": "Test", "parent_id": None}
        create_resp = await client.post("/api/v1/categorias", json=payload, headers=admin_headers)
        categoria_id = create_resp.json()["id"]

        # Try update without auth
        response = await client.put(
            f"/api/v1/categorias/{categoria_id}", json={"nombre": "Updated"}
        )

        assert response.status_code in [401, 403]

    async def test_delete_unauthenticated_returns_401(self, client, admin_token):
        """Test: DELETE without token → 401"""
        admin_headers = {"Authorization": f"Bearer {admin_token}"}

        # Create category first
        payload = {"nombre": "Test", "parent_id": None}
        create_resp = await client.post("/api/v1/categorias", json=payload, headers=admin_headers)
        categoria_id = create_resp.json()["id"]

        # Try delete without auth
        response = await client.delete(f"/api/v1/categorias/{categoria_id}")

        assert response.status_code in [401, 403]
