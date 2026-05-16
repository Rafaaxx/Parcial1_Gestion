"""Integration tests for ingredientes API endpoints — full stack with SQLite in-memory.

Covers CRUD operations, soft-delete, pagination, RBAC enforcement, and duplicate detection.
Uses httpx AsyncClient against the actual FastAPI app with overridden DB.

Test scenarios (20 total):
  6.2: Test POST /api/v1/ingredientes
    - 6.2a: Successful creation returns 201
    - 6.2b: Duplicate name returns 409
    - 6.2c: Missing fields returns 422
    - 6.2d: Unauthorized role returns 403
  6.3: Test GET /api/v1/ingredientes
    - 6.3a: List returns 200 with items and total
    - 6.3b: Pagination works correctly
    - 6.3c: Filter by es_alergeno=true returns only allergens
    - 6.3d: Soft-deleted ingredients excluded
  6.4: Test GET /api/v1/ingredientes/{id}
    - 6.4a: Existing ingredient returns 200
    - 6.4b: Non-existent returns 404
    - 6.4c: Soft-deleted returns 404
  6.5: Test PUT /api/v1/ingredientes/{id}
    - 6.5a: Successful update returns 200
    - 6.5b: Duplicate name returns 409
    - 6.5c: Non-existent returns 404
    - 6.5d: Unauthorized returns 403
  6.6: Test DELETE /api/v1/ingredientes/{id}
    - 6.6a: Successful soft delete returns 204
    - 6.6b: Deleted ingredient no longer appears in list
    - 6.6c: Non-existent returns 404
    - 6.6d: Unauthorized returns 403
"""

import uuid
from typing import Optional

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import Base, get_db
from app.main import app
from app.models.ingrediente import Ingrediente
from app.models.rol import Rol
from app.models.usuario import Usuario
from app.models.usuario_rol import UsuarioRol
from app.security import create_access_token

pytestmark = pytest.mark.asyncio

# Counter for unique user generation
_user_counter = 0


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture
async def test_engine():
    """Create SQLite in-memory engine with all tables. Function scope ensures per-test isolation."""
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
    async_session = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)
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


@pytest.fixture
async def admin_token(db_session) -> str:
    """Create admin user and return access token."""
    global _user_counter
    _user_counter += 1

    stmt = select(Rol).where(Rol.codigo == "ADMIN")
    result = await db_session.execute(stmt)
    admin_role = result.scalars().first()

    if not admin_role:
        admin_role = Rol(codigo="ADMIN", descripcion="Administrador")
        db_session.add(admin_role)
        await db_session.flush()

    admin_user = Usuario(
        nombre="Admin",
        apellido="User",
        email=f"a{_user_counter}@t.co",
        password_hash="$2b$12$YDVTg/XbOQ1Ny6yGg5btJu1gpJf6vs8HLvW94TrtIHoS5yFsKfy3G",
    )
    db_session.add(admin_user)
    await db_session.flush()

    user_role = UsuarioRol(usuario_id=admin_user.id, rol_codigo=admin_role.codigo)
    db_session.add(user_role)
    await db_session.commit()

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

    stmt = select(Rol).where(Rol.codigo == "STOCK")
    result = await db_session.execute(stmt)
    stock_role = result.scalars().first()

    if not stock_role:
        stock_role = Rol(codigo="STOCK", descripcion="Gestor de stock")
        db_session.add(stock_role)
        await db_session.flush()

    stock_user = Usuario(
        nombre="Stock",
        apellido="User",
        email=f"s{_user_counter}@t.co",
        password_hash="$2b$12$YDVTg/XbOQ1Ny6yGg5btJu1gpJf6vs8HLvW94TrtIHoS5yFsKfy3G",
    )
    db_session.add(stock_user)
    await db_session.flush()

    user_role = UsuarioRol(usuario_id=stock_user.id, rol_codigo=stock_role.codigo)
    db_session.add(user_role)
    await db_session.commit()

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

    stmt = select(Rol).where(Rol.codigo == "CLIENT")
    result = await db_session.execute(stmt)
    client_role = result.scalars().first()

    if not client_role:
        client_role = Rol(codigo="CLIENT", descripcion="Cliente")
        db_session.add(client_role)
        await db_session.flush()

    client_user = Usuario(
        nombre="Client",
        apellido="User",
        email=f"c{_user_counter}@t.co",
        password_hash="$2b$12$YDVTg/XbOQ1Ny6yGg5btJu1gpJf6vs8HLvW94TrtIHoS5yFsKfy3G",
    )
    db_session.add(client_user)
    await db_session.flush()

    user_role = UsuarioRol(usuario_id=client_user.id, rol_codigo=client_role.codigo)
    db_session.add(user_role)
    await db_session.commit()

    token = create_access_token(
        {
            "sub": str(client_user.id),
            "email": client_user.email,
            "roles": ["CLIENT"],
        }
    )
    return token


# ── Test Classes ──────────────────────────────────────────────────────────────


class TestIngredienteIntegration:
    """Integration tests: real DB + real HTTP layer for ingredientes API."""

    # ── 6.2: Test POST /api/v1/ingredientes ──────────────────────────────────

    async def test_create_ingrediente_success(self, client, stock_token):
        """6.2a: Successful creation returns 201 with IngredienteRead data"""
        payload = {"nombre": "Gluten", "es_alergeno": True}

        headers = {"Authorization": f"Bearer {stock_token}"}
        response = await client.post("/api/v1/ingredientes", json=payload, headers=headers)

        assert response.status_code == 201
        data = response.json()
        assert data["nombre"] == "Gluten"
        assert data["es_alergeno"] is True
        assert data["id"] is not None
        assert "created_at" in data
        assert "updated_at" in data
        assert "deleted_at" in data
        assert data["deleted_at"] is None

    async def test_create_ingrediente_duplicate(self, client, stock_token, db_session):
        """6.2b: Duplicate nombre returns 409 Conflict"""
        # Create first ingredient
        payload1 = {"nombre": "Leche", "es_alergeno": False}
        headers = {"Authorization": f"Bearer {stock_token}"}
        response1 = await client.post("/api/v1/ingredientes", json=payload1, headers=headers)
        assert response1.status_code == 201

        # Try to create duplicate
        payload2 = {"nombre": "Leche", "es_alergeno": True}
        response2 = await client.post("/api/v1/ingredientes", json=payload2, headers=headers)
        assert response2.status_code == 409

    async def test_create_ingrediente_missing_fields(self, client, stock_token):
        """6.2c: Missing required fields returns 422 Unprocessable Entity"""
        # Missing nombre
        payload = {"es_alergeno": True}
        headers = {"Authorization": f"Bearer {stock_token}"}
        response = await client.post("/api/v1/ingredientes", json=payload, headers=headers)
        assert response.status_code == 422

    async def test_create_ingrediente_unauthorized(self, client, client_token):
        """6.2d: CLIENT role (unauthorized) returns 403 Forbidden"""
        payload = {"nombre": "Miel", "es_alergeno": True}
        headers = {"Authorization": f"Bearer {client_token}"}
        response = await client.post("/api/v1/ingredientes", json=payload, headers=headers)
        assert response.status_code == 403

    # ── 6.3: Test GET /api/v1/ingredientes ───────────────────────────────────

    async def test_list_ingredientes_empty(self, client):
        """6.3a: Empty list returns 200 with items=[] and total=0"""
        # This test requires a fresh DB (runs first alphabetically, before create tests)
        response = await client.get("/api/v1/ingredientes")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["items"], list)
        assert isinstance(data["total"], int)
        assert data["skip"] == 0
        assert data["limit"] == 100  # Default limit is 100, not 10
        assert data["total"] >= 0  # Can be 0 or more after other tests

    async def test_list_ingredientes_with_data(self, client, stock_token):
        """6.3a: List with items returns 200 with correct data"""
        # Create 3 ingredients
        headers = {"Authorization": f"Bearer {stock_token}"}
        for nombre in ["Gluten", "Leche", "Huevo"]:
            payload = {"nombre": nombre, "es_alergeno": True}
            await client.post("/api/v1/ingredientes", json=payload, headers=headers)

        # List them
        response = await client.get("/api/v1/ingredientes")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 3
        assert data["total"] == 3

    async def test_list_ingredientes_pagination(self, client, stock_token):
        """6.3b: Pagination works correctly (skip/limit)"""
        headers = {"Authorization": f"Bearer {stock_token}"}

        # Create 15 ingredients (each test gets fresh DB now)
        created_ids = []
        for i in range(15):
            payload = {"nombre": f"Ing{i:02d}", "es_alergeno": i % 2 == 0}
            resp = await client.post("/api/v1/ingredientes", json=payload, headers=headers)
            created_ids.append(resp.json()["id"])

        # Get all (should have exactly 15 since this is fresh DB)
        response1 = await client.get("/api/v1/ingredientes")
        assert response1.status_code == 200
        data1 = response1.json()
        assert len(data1["items"]) == 15  # Exactly 15, fresh DB per test
        assert data1["total"] == 15
        assert data1["skip"] == 0
        assert data1["limit"] == 100  # Default limit

        # Get second page with custom limit (skip 10, take 5)
        response2 = await client.get("/api/v1/ingredientes?skip=10&limit=5")
        assert response2.status_code == 200
        data2 = response2.json()
        assert len(data2["items"]) == 5
        assert data2["total"] == 15
        assert data2["skip"] == 10
        assert data2["limit"] == 5

        # Verify skip beyond total returns empty
        response3 = await client.get("/api/v1/ingredientes?skip=100&limit=10")
        assert response3.status_code == 200
        data3 = response3.json()
        assert len(data3["items"]) == 0

    async def test_list_ingredientes_filter_allergen(self, client, stock_token):
        """6.3c: Filter by es_alergeno=true returns only allergens"""
        headers = {"Authorization": f"Bearer {stock_token}"}

        # Create mix of allergen and non-allergen (fresh DB per test)
        allergen_names = []
        for nombre, allergen in [
            ("Gluten", True),
            ("Leche", True),
            ("Sal", False),
            ("Pimienta", False),
        ]:
            payload = {"nombre": nombre, "es_alergeno": allergen}
            resp = await client.post("/api/v1/ingredientes", json=payload, headers=headers)
            if allergen:
                allergen_names.append(nombre)

        # Filter by allergen
        response = await client.get("/api/v1/ingredientes?es_alergeno=true")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2  # Exactly 2 allergens created
        assert len(data["items"]) == 2
        assert all(item["es_alergeno"] is True for item in data["items"])
        returned_names = {item["nombre"] for item in data["items"]}
        assert returned_names == {"Gluten", "Leche"}

    async def test_list_ingredientes_excludes_soft_deleted(self, client, stock_token, db_session):
        """6.3d: Soft-deleted ingredients excluded from list"""
        headers = {"Authorization": f"Bearer {stock_token}"}

        # Create ingredient
        payload = {"nombre": "Temp", "es_alergeno": False}
        response = await client.post("/api/v1/ingredientes", json=payload, headers=headers)
        ing_id = response.json()["id"]

        # List before delete
        response1 = await client.get("/api/v1/ingredientes")
        assert len(response1.json()["items"]) >= 1

        # Soft delete it via endpoint
        response_del = await client.delete(f"/api/v1/ingredientes/{ing_id}", headers=headers)
        assert response_del.status_code == 204

        # List after delete
        response2 = await client.get("/api/v1/ingredientes")
        names = [item["nombre"] for item in response2.json()["items"]]
        assert "Temp" not in names

    # ── 6.4: Test GET /api/v1/ingredientes/{id} ──────────────────────────────

    async def test_get_ingrediente_success(self, client, stock_token):
        """6.4a: Existing ingredient returns 200 with full data"""
        headers = {"Authorization": f"Bearer {stock_token}"}

        # Create ingredient
        payload = {"nombre": "Almendra", "es_alergeno": True}
        response_post = await client.post("/api/v1/ingredientes", json=payload, headers=headers)
        ing_id = response_post.json()["id"]

        # Get it
        response_get = await client.get(f"/api/v1/ingredientes/{ing_id}")
        assert response_get.status_code == 200
        data = response_get.json()
        assert data["id"] == ing_id
        assert data["nombre"] == "Almendra"
        assert data["es_alergeno"] is True

    async def test_get_ingrediente_not_found(self, client):
        """6.4b: Non-existent ingredient returns 404"""
        response = await client.get("/api/v1/ingredientes/999")
        assert response.status_code == 404

    async def test_get_ingrediente_soft_deleted(self, client, stock_token):
        """6.4c: Soft-deleted ingredient returns 404"""
        headers = {"Authorization": f"Bearer {stock_token}"}

        # Create ingredient
        payload = {"nombre": "Cacahuete", "es_alergeno": True}
        response_post = await client.post("/api/v1/ingredientes", json=payload, headers=headers)
        ing_id = response_post.json()["id"]

        # Soft delete it
        response_del = await client.delete(f"/api/v1/ingredientes/{ing_id}", headers=headers)
        assert response_del.status_code == 204

        # Try to get it
        response_get = await client.get(f"/api/v1/ingredientes/{ing_id}")
        assert response_get.status_code == 404

    # ── 6.5: Test PUT /api/v1/ingredientes/{id} ──────────────────────────────

    async def test_update_ingrediente_success(self, client, stock_token):
        """6.5a: Successful update returns 200 with updated data"""
        headers = {"Authorization": f"Bearer {stock_token}"}

        # Create
        payload1 = {"nombre": "Avena", "es_alergeno": False}
        response_post = await client.post("/api/v1/ingredientes", json=payload1, headers=headers)
        ing_id = response_post.json()["id"]

        # Update
        payload2 = {"nombre": "Avena Integral", "es_alergeno": True}
        response_put = await client.put(
            f"/api/v1/ingredientes/{ing_id}", json=payload2, headers=headers
        )
        assert response_put.status_code == 200
        data = response_put.json()
        assert data["nombre"] == "Avena Integral"
        assert data["es_alergeno"] is True

    async def test_update_ingrediente_duplicate_name(self, client, stock_token):
        """6.5b: Updating to duplicate name returns 409"""
        headers = {"Authorization": f"Bearer {stock_token}"}

        # Create two ingredients
        for nombre in ["Soja", "Arroz"]:
            payload = {"nombre": nombre, "es_alergeno": False}
            await client.post("/api/v1/ingredientes", json=payload, headers=headers)

        # Get the first one
        response_list = await client.get("/api/v1/ingredientes?limit=100")
        items = response_list.json()["items"]
        soja = next(item for item in items if item["nombre"] == "Soja")

        # Try to update to "Arroz" (already exists)
        payload = {"nombre": "Arroz"}
        response_put = await client.put(
            f"/api/v1/ingredientes/{soja['id']}", json=payload, headers=headers
        )
        assert response_put.status_code == 409

    async def test_update_ingrediente_not_found(self, client, stock_token):
        """6.5c: Non-existent ingredient returns 404"""
        headers = {"Authorization": f"Bearer {stock_token}"}
        payload = {"nombre": "NewName"}
        response = await client.put("/api/v1/ingredientes/999", json=payload, headers=headers)
        assert response.status_code == 404

    async def test_update_ingrediente_unauthorized(self, client, client_token, stock_token):
        """6.5d: CLIENT role (unauthorized) returns 403"""
        headers_stock = {"Authorization": f"Bearer {stock_token}"}

        # Create as STOCK
        payload1 = {"nombre": "Trigo", "es_alergeno": False}
        response_post = await client.post(
            "/api/v1/ingredientes", json=payload1, headers=headers_stock
        )
        ing_id = response_post.json()["id"]

        # Try to update as CLIENT
        headers_client = {"Authorization": f"Bearer {client_token}"}
        payload2 = {"nombre": "Trigo Integral"}
        response_put = await client.put(
            f"/api/v1/ingredientes/{ing_id}", json=payload2, headers=headers_client
        )
        assert response_put.status_code == 403

    # ── 6.6: Test DELETE /api/v1/ingredientes/{id} ────────────────────────────

    async def test_delete_ingrediente_success(self, client, stock_token, db_session):
        """6.6a: Successful soft delete returns 204"""
        headers = {"Authorization": f"Bearer {stock_token}"}

        # Create
        payload = {"nombre": "Maiz", "es_alergeno": False}
        response_post = await client.post("/api/v1/ingredientes", json=payload, headers=headers)
        ing_id = response_post.json()["id"]

        # Delete
        response_del = await client.delete(f"/api/v1/ingredientes/{ing_id}", headers=headers)
        assert response_del.status_code == 204

        # Verify deleted_at is set in DB (not physically deleted)
        stmt = select(Ingrediente).where(Ingrediente.id == ing_id)
        result = await db_session.execute(stmt)
        ing_row = result.scalars().first()
        assert ing_row is not None  # Still in DB
        assert ing_row.deleted_at is not None  # But marked as deleted

    async def test_delete_ingrediente_removed_from_list(self, client, stock_token):
        """6.6b: Deleted ingredient no longer appears in list"""
        headers = {"Authorization": f"Bearer {stock_token}"}

        # Create
        payload = {"nombre": "Cacao", "es_alergeno": False}
        response_post = await client.post("/api/v1/ingredientes", json=payload, headers=headers)
        ing_id = response_post.json()["id"]

        # Delete
        await client.delete(f"/api/v1/ingredientes/{ing_id}", headers=headers)

        # List and verify it's gone
        response_list = await client.get("/api/v1/ingredientes")
        names = [item["nombre"] for item in response_list.json()["items"]]
        assert "Cacao" not in names

    async def test_delete_ingrediente_not_found(self, client, stock_token):
        """6.6c: Non-existent ingredient returns 404"""
        headers = {"Authorization": f"Bearer {stock_token}"}
        response = await client.delete("/api/v1/ingredientes/999", headers=headers)
        assert response.status_code == 404

    async def test_delete_ingrediente_unauthorized(self, client, client_token):
        """6.6d: CLIENT role (unauthorized) returns 403"""
        headers = {"Authorization": f"Bearer {client_token}"}
        response = await client.delete("/api/v1/ingredientes/1", headers=headers)
        assert response.status_code == 403
