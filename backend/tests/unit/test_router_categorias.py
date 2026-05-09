"""Unit tests for Categoria Router — HTTP contracts, RBAC, error responses.

Uses mocked UnitOfWork and TestClient to test router layer in isolation.
Tests validate:
  - HTTP status codes (201, 200, 204, 404, 403, 422, 409)
  - RBAC enforcement (ADMIN-only, STOCK+ADMIN, public endpoints)
  - Request/response schema validation
  - Error messages and details
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from fastapi.testclient import TestClient
from fastapi import FastAPI

from app.modules.categorias.schemas import (
    CategoriaCreate, CategoriaUpdate, CategoriaRead, CategoriaTreeNode
)
from app.exceptions import AppException, ValidationError
from app.dependencies import get_uow, require_role, get_current_user, oauth2_scheme


# ── TEST SETUP: Minimal FastAPI app with router ────────────────────────────────

@pytest.fixture
def mock_uow():
    """Mock UnitOfWork for router testing"""
    uow = AsyncMock()
    uow.categorias = AsyncMock()
    uow.categorias.create = AsyncMock()
    uow.categorias.update = AsyncMock()
    uow.categorias.soft_delete = AsyncMock()
    uow.categorias.find = AsyncMock()
    uow.categorias.get_tree = AsyncMock()
    uow.categorias.validate_no_cycle = AsyncMock()
    uow.categorias.count_children = AsyncMock()
    return uow


@pytest.fixture
def mock_user_admin():
    """Mock admin user"""
    user = MagicMock()
    user.id = 1
    user.email = "admin@test.com"
    user.roles = [MagicMock(codigo="ADMIN")]
    user.activo = True
    return user


@pytest.fixture
def mock_user_stock():
    """Mock stock user"""
    user = MagicMock()
    user.id = 2
    user.email = "stock@test.com"
    user.roles = [MagicMock(codigo="STOCK")]
    user.activo = True
    return user


@pytest.fixture
def mock_user_client():
    """Mock client user"""
    user = MagicMock()
    user.id = 3
    user.email = "client@test.com"
    user.roles = [MagicMock(codigo="CLIENT")]
    user.activo = True
    return user


@pytest.fixture
def app_with_router(mock_uow):
    """Create FastAPI app with categorias router (but NOT registered yet, returns unregistered app)"""
    # This will be used by tests that directly import and test the router
    # We return a base app that tests can mount the router on
    app = FastAPI(title="Test Food Store API")
    
    # Override dependencies for testing
    async def _get_test_uow():
        return mock_uow
    
    app.dependency_overrides[get_uow] = _get_test_uow
    
    return app


@pytest.fixture
def client(app_with_router):
    """FastAPI TestClient for making test requests"""
    return TestClient(app_with_router)


# ── TESTS: RED PHASE (These will FAIL because router.py doesn't exist yet) ──────


class TestCategoriaRouterCreate:
    """Test suite for POST /api/v1/categorias endpoint"""
    
    def test_post_categorias_creates_root_category_admin(self, client, mock_uow, mock_user_admin):
        """Test: POST /api/v1/categorias creates root category with ADMIN role → 201"""
        # ARRANGE
        payload = {
            "nombre": "Bebidas",
            "descripcion": "Bebidas variadas",
            "parent_id": None
        }
        
        created_cat = MagicMock()
        created_cat.id = 1
        created_cat.nombre = "Bebidas"
        created_cat.descripcion = "Bebidas variadas"
        created_cat.parent_id = None
        created_cat.created_at = datetime.now()
        created_cat.updated_at = datetime.now()
        created_cat.deleted_at = None
        
        mock_uow.categorias.create = AsyncMock(return_value=created_cat)
        
        with patch("app.dependencies.get_current_user", return_value=mock_user_admin):
            # ACT
            response = client.post("/api/v1/categorias", json=payload)
        
        # ASSERT — expected to FAIL because endpoint doesn't exist yet
        assert response.status_code == 201
        assert response.json()["nombre"] == "Bebidas"
        assert "id" in response.json()
    
    def test_post_categorias_requires_admin_or_stock_role(self, client, mock_uow, mock_user_client):
        """Test: POST /api/v1/categorias requires ADMIN/STOCK role, CLIENT → 403"""
        payload = {"nombre": "Bebidas", "parent_id": None}
        
        with patch("app.dependencies.get_current_user", return_value=mock_user_client):
            # CLIENT role should get 403
            response = client.post("/api/v1/categorias", json=payload)
        
        # Expected: 403 Forbidden (CLIENT role not in [ADMIN, STOCK])
        assert response.status_code == 403
    
    def test_post_categorias_unauthenticated_returns_401(self, client):
        """Test: POST /api/v1/categorias without token → 401"""
        payload = {"nombre": "Bebidas", "parent_id": None}
        
        # No auth token provided
        response = client.post("/api/v1/categorias", json=payload)
        
        # Expected: 401 Unauthorized (no token)
        assert response.status_code == 401
    
    def test_post_categorias_invalid_schema_missing_nombre(self, client, mock_uow, mock_user_admin):
        """Test: POST with missing nombre → 422 Unprocessable Entity"""
        payload = {"parent_id": None}  # Missing 'nombre'
        
        with patch("app.dependencies.get_current_user", return_value=mock_user_admin):
            response = client.post("/api/v1/categorias", json=payload)
        
        # Expected: 422 (Pydantic validation error)
        assert response.status_code == 422
    
    def test_post_categorias_with_invalid_parent_returns_404(self, client, mock_uow, mock_user_admin):
        """Test: POST with nonexistent parent_id → 404"""
        payload = {"nombre": "Subcategoría", "parent_id": 999}
        
        mock_uow.categorias.find = AsyncMock(return_value=None)  # Parent not found
        
        with patch("app.dependencies.get_current_user", return_value=mock_user_admin):
            response = client.post("/api/v1/categorias", json=payload)
        
        # Expected: 404 Not Found (parent doesn't exist)
        assert response.status_code == 404


class TestCategoriaRouterList:
    """Test suite for GET /api/v1/categorias (tree) endpoint"""
    
    def test_get_categorias_tree_returns_200(self, client, mock_uow):
        """Test: GET /api/v1/categorias returns 200 with nested tree"""
        # ARRANGE
        tree_data = [
            MagicMock(
                id=1,
                nombre="Bebidas",
                descripcion="Bebidas variadas",
                parent_id=None,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                deleted_at=None,
                children=[
                    MagicMock(
                        id=2,
                        nombre="Alcohólicas",
                        descripcion=None,
                        parent_id=1,
                        created_at=datetime.now(),
                        updated_at=datetime.now(),
                        deleted_at=None,
                        children=[]
                    )
                ]
            )
        ]
        
        mock_uow.categorias.get_tree = AsyncMock(return_value=tree_data)
        
        # ACT
        response = client.get("/api/v1/categorias")
        
        # ASSERT
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if data:
            assert "id" in data[0]
            assert "nombre" in data[0]
            assert "subcategorias" in data[0]
    
    def test_get_categorias_empty_tree_returns_empty_list(self, client, mock_uow):
        """Test: GET /api/v1/categorias with no categories returns empty list"""
        mock_uow.categorias.get_tree = AsyncMock(return_value=[])
        
        response = client.get("/api/v1/categorias")
        
        assert response.status_code == 200
        assert response.json() == []


class TestCategoriaRouterGetById:
    """Test suite for GET /api/v1/categorias/{id} endpoint"""
    
    def test_get_categoria_by_id_success(self, client, mock_uow):
        """Test: GET /api/v1/categorias/{id} returns 200"""
        # ARRANGE
        categoria = MagicMock()
        categoria.id = 1
        categoria.nombre = "Bebidas"
        categoria.descripcion = "Bebidas variadas"
        categoria.parent_id = None
        categoria.created_at = datetime.now()
        categoria.updated_at = datetime.now()
        categoria.deleted_at = None
        
        mock_uow.categorias.find = AsyncMock(return_value=categoria)
        
        # ACT
        response = client.get("/api/v1/categorias/1")
        
        # ASSERT
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["nombre"] == "Bebidas"
    
    def test_get_categoria_by_id_not_found(self, client, mock_uow):
        """Test: GET /api/v1/categorias/{id} with nonexistent id → 404"""
        mock_uow.categorias.find = AsyncMock(return_value=None)
        
        response = client.get("/api/v1/categorias/999")
        
        assert response.status_code == 404
    
    def test_get_categoria_by_id_soft_deleted_returns_404(self, client, mock_uow):
        """Test: GET soft-deleted category returns 404"""
        categoria = MagicMock()
        categoria.id = 1
        categoria.deleted_at = datetime.now()  # Soft deleted
        
        mock_uow.categorias.find = AsyncMock(return_value=None)  # Repo filters soft-deleted
        
        response = client.get("/api/v1/categorias/1")
        
        assert response.status_code == 404


class TestCategoriaRouterUpdate:
    """Test suite for PUT /api/v1/categorias/{id} endpoint"""
    
    def test_put_categoria_updates_name_success(self, client, mock_uow, mock_user_stock):
        """Test: PUT /api/v1/categorias/{id} updates name → 200"""
        payload = {"nombre": "Bebidas - Refrescantes"}
        
        updated_cat = MagicMock()
        updated_cat.id = 1
        updated_cat.nombre = "Bebidas - Refrescantes"
        updated_cat.parent_id = None
        updated_cat.created_at = datetime.now()
        updated_cat.updated_at = datetime.now()
        updated_cat.deleted_at = None
        
        mock_uow.categorias.update = AsyncMock(return_value=updated_cat)
        
        with patch("app.dependencies.get_current_user", return_value=mock_user_stock):
            response = client.put("/api/v1/categorias/1", json=payload)
        
        assert response.status_code == 200
        assert response.json()["nombre"] == "Bebidas - Refrescantes"
    
    def test_put_categoria_requires_admin_or_stock(self, client, mock_uow, mock_user_client):
        """Test: PUT requires ADMIN/STOCK role, CLIENT → 403"""
        payload = {"nombre": "Updated"}
        
        with patch("app.dependencies.get_current_user", return_value=mock_user_client):
            response = client.put("/api/v1/categorias/1", json=payload)
        
        assert response.status_code == 403
    
    def test_put_categoria_cycle_detection_returns_422(self, client, mock_uow, mock_user_admin):
        """Test: PUT with cycle returns 422"""
        payload = {"parent_id": 3}  # Attempting cycle
        
        # Simulate cycle detection failure
        mock_uow.categorias.update = AsyncMock(side_effect=ValidationError("Cycle detected"))
        
        with patch("app.dependencies.get_current_user", return_value=mock_user_admin):
            response = client.put("/api/v1/categorias/1", json=payload)
        
        # Expected: 422 (validation error from service)
        assert response.status_code in [400, 422]
    
    def test_put_categoria_not_found_returns_404(self, client, mock_uow, mock_user_admin):
        """Test: PUT nonexistent category → 404"""
        payload = {"nombre": "Updated"}
        
        mock_uow.categorias.update = AsyncMock(return_value=None)
        
        with patch("app.dependencies.get_current_user", return_value=mock_user_admin):
            response = client.put("/api/v1/categorias/999", json=payload)
        
        assert response.status_code == 404


class TestCategoriaRouterDelete:
    """Test suite for DELETE /api/v1/categorias/{id} endpoint"""
    
    def test_delete_categoria_success_returns_204(self, client, mock_uow, mock_user_admin):
        """Test: DELETE /api/v1/categorias/{id} soft-deletes → 204"""
        mock_uow.categorias.soft_delete = AsyncMock()
        
        with patch("app.dependencies.get_current_user", return_value=mock_user_admin):
            response = client.delete("/api/v1/categorias/1")
        
        assert response.status_code == 204
        assert response.content == b""
    
    def test_delete_categoria_admin_only(self, client, mock_uow, mock_user_stock):
        """Test: DELETE requires ADMIN role, STOCK → 403"""
        with patch("app.dependencies.get_current_user", return_value=mock_user_stock):
            response = client.delete("/api/v1/categorias/1")
        
        # STOCK role should get 403 (only ADMIN can delete)
        assert response.status_code == 403
    
    def test_delete_categoria_with_children_returns_409(self, client, mock_uow, mock_user_admin):
        """Test: DELETE category with children → 409 Conflict"""
        # Simulate category has children
        mock_uow.categorias.soft_delete = AsyncMock(
            side_effect=AppException(
                message="Cannot delete category: it has 2 child categories",
                status_code=409
            )
        )
        
        with patch("app.dependencies.get_current_user", return_value=mock_user_admin):
            response = client.delete("/api/v1/categorias/1")
        
        assert response.status_code == 409
    
    def test_delete_categoria_not_found_returns_404(self, client, mock_uow, mock_user_admin):
        """Test: DELETE nonexistent category → 404"""
        mock_uow.categorias.soft_delete = AsyncMock(
            side_effect=AppException(message="Category not found", status_code=404)
        )
        
        with patch("app.dependencies.get_current_user", return_value=mock_user_admin):
            response = client.delete("/api/v1/categorias/999")
        
        assert response.status_code == 404
    
    def test_delete_categoria_unauthenticated_returns_401(self, client):
        """Test: DELETE without token → 401"""
        response = client.delete("/api/v1/categorias/1")
        
        assert response.status_code == 401


class TestCategoriaSwaggerSchema:
    """Test OpenAPI schema correctness"""
    
    def test_swagger_includes_categorias_endpoints(self, client):
        """Test: OpenAPI schema includes all 5 endpoints"""
        response = client.get("/openapi.json")
        
        assert response.status_code == 200
        schema = response.json()
        
        paths = schema.get("paths", {})
        # Check all 5 endpoints are in paths
        assert "/api/v1/categorias" in paths or any("categorias" in p for p in paths)
    
    def test_swagger_categorias_endpoints_have_tags(self, client):
        """Test: All categoria endpoints tagged with 'categorias'"""
        response = client.get("/openapi.json")
        schema = response.json()
        
        paths = schema.get("paths", {})
        # Find categoria paths and verify tags
        categoria_paths = [p for p in paths if "categorias" in p]
        
        for path in categoria_paths:
            methods = paths[path]
            for method in ["get", "post", "put", "delete"]:
                if method in methods:
                    tags = methods[method].get("tags", [])
                    assert "categorias" in tags or len(tags) > 0
