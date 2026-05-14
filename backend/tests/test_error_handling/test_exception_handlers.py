"""Tests for RFC 7807 exception handlers"""

import pytest
from httpx import AsyncClient, ASGITransport

from fastapi import status
from fastapi.testclient import TestClient

# Import app and handlers
from app.main import app
from app.handlers import (
    format_rfc7807_error,
    validation_error_handler,
    not_found_error_handler,
    unauthorized_error_handler,
    conflict_error_handler,
    forbidden_error_handler,
)
from app.exceptions import (
    ValidationError,
    NotFoundError,
    UnauthorizedError,
    ConflictError,
    ForbiddenError,
)


class TestRFC7807Format:
    """Tests for RFC 7807 response format"""
    
    def test_format_includes_required_fields(self):
        """RFC 7807 response must include type, title, status, detail, timestamp"""
        result = format_rfc7807_error(
            title="Test Error",
            status=400,
            detail="Test detail",
        )
        
        assert "type" in result
        assert "title" in result
        assert result["title"] == "Test Error"
        assert result["status"] == 400
        assert result["detail"] == "Test detail"
        assert "timestamp" in result
    
    def test_format_includes_errors_array(self):
        """Should include errors array when provided"""
        errors = [{"field": "email", "message": "Invalid"}]
        result = format_rfc7807_error(
            title="Validation Error",
            status=422,
            detail="Validation failed",
            errors=errors,
        )
        
        assert "errors" in result
        assert result["errors"] == errors
    
    def test_format_includes_instance(self):
        """Should include instance (request path) when request provided"""
        from unittest.mock import MagicMock
        
        mock_request = MagicMock()
        mock_request.url.path = "/api/v1/test"
        
        result = format_rfc7807_error(
            title="Error",
            status=500,
            detail="Error",
            request=mock_request,
        )
        
        assert result["instance"] == "/api/v1/test"
    
    def test_format_includes_request_id(self):
        """Should include requestId when provided"""
        result = format_rfc7807_error(
            title="Error",
            status=500,
            detail="Error",
            request_id="test-123",
        )
        
        assert result["requestId"] == "test-123"
    
    def test_type_is_error_url(self):
        """Type should be a URL based on error title"""
        result = format_rfc7807_error(
            title="Validation Error",
            status=422,
            detail="Error",
        )
        
        assert result["type"].startswith("https://api.foodstore.com/errors/")


class TestExceptionHandlers:
    """Tests for exception handlers returning RFC 7807"""
    
    @pytest.fixture
    def test_client(self):
        """Create test client"""
        transport = ASGITransport(app=app)
        return AsyncClient(transport=transport, base_url="http://test")
    
    @pytest.mark.asyncio
    async def test_not_found_returns_rfc7807(self, test_client):
        """NotFoundError should return RFC 7807 format"""
        # Create a route that raises NotFoundError
        from app.exceptions import NotFoundError
        
        @app.get("/test-not-found")
        async def test_not_found():
            raise NotFoundError("Item not found", resource="product")
        
        response = await test_client.get("/test-not-found")
        
        assert response.status_code == 404
        data = response.json()
        
        # Check RFC 7807 fields
        assert data["type"] == "https://api.foodstore.com/errors/not-found"
        assert data["title"] == "Not Found"
        assert data["status"] == 404
        assert data["detail"] == "Item not found"
        assert "timestamp" in data
        assert "requestId" in data
    
    @pytest.mark.asyncio
    async def test_validation_error_returns_rfc7807(self, test_client):
        """ValidationError should return RFC 7807 format with field errors"""
        from app.exceptions import ValidationError
        
        @app.get("/test-validation")
        async def test_validation():
            raise ValidationError(
                "Validation failed",
                detail={"errors": [{"field": "email", "message": "Invalid"}]}
            )
        
        response = await test_client.get("/test-validation")
        
        assert response.status_code == 422
        data = response.json()
        
        assert data["status"] == 422
        assert "errors" in data
        assert data["errors"][0]["field"] == "email"
    
    @pytest.mark.asyncio
    async def test_conflict_error_returns_rfc7807(self, test_client):
        """ConflictError should return RFC 7807 format"""
        from app.exceptions import ConflictError
        
        @app.get("/test-conflict")
        async def test_conflict():
            raise ConflictError("Email already exists")
        
        response = await test_client.get("/test-conflict")
        
        assert response.status_code == 409
        data = response.json()
        
        assert data["status"] == 409
        assert data["detail"] == "Email already exists"
    
    @pytest.mark.asyncio
    async def test_unauthorized_returns_rfc7807(self, test_client):
        """UnauthorizedError should return RFC 7807 format"""
        from app.exceptions import UnauthorizedError
        
        @app.get("/test-unauthorized")
        async def test_unauthorized():
            raise UnauthorizedError("Invalid token")
        
        response = await test_client.get("/test-unauthorized")
        
        assert response.status_code == 401
        data = response.json()
        
        assert data["status"] == 401
        assert data["detail"] == "Invalid token"
    
    @pytest.mark.asyncio
    async def test_forbidden_returns_rfc7807(self, test_client):
        """ForbiddenError should return RFC 7807 format"""
        from app.exceptions import ForbiddenError
        
        @app.get("/test-forbidden")
        async def test_forbidden():
            raise ForbiddenError("Insufficient permissions")
        
        response = await test_client.get("/test-forbidden")
        
        assert response.status_code == 403
        data = response.json()
        
        assert data["status"] == 403


class TestPydanticValidationHandler:
    """Tests for Pydantic request validation"""
    
    @pytest.mark.asyncio
    async def test_invalid_body_returns_rfc7807(self):
        """Invalid request body should return RFC 7807 format"""
        # This uses a schema that requires 'name' field
        from pydantic import BaseModel
        
        class ItemCreate(BaseModel):
            name: str
            price: float
        
        @app.post("/test-item")
        async def create_item(item: ItemCreate):
            return item
        
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post("/test-item", json={"name": "test"})
        
        assert response.status_code == 422
        data = response.json()
        
        # Should be RFC 7807 format
        assert data["type"] == "https://api.foodstore.com/errors/validation-error"
        assert data["status"] == 422
        assert "errors" in data
    
    @pytest.mark.asyncio
    async def test_invalid_query_param_returns_rfc7807(self):
        """Invalid query parameter should return RFC 7807 format"""
        @app.get("/test-query")
        async def get_items(limit: int = 10):
            return {"limit": limit}
        
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/test-query?limit=abc")
        
        assert response.status_code == 422
        data = response.json()
        
        assert data["status"] == 422
        assert "errors" in data