"""Tests for Request ID middleware"""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.middleware.request_id import (
    RequestIDMiddleware,
    get_request_id,
    request_id_var,
    set_request_id,
)


class TestRequestIDMiddleware:
    """Tests for RequestIDMiddleware"""

    @pytest.mark.asyncio
    async def test_request_id_in_response_header(self):
        """Response should include X-Request-ID header"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/health")

        assert "x-request-id" in response.headers
        assert response.headers["x-request-id"] is not None

    @pytest.mark.asyncio
    async def test_request_id_is_uuid(self):
        """Request ID should be a valid UUID"""
        import uuid

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/health")

        request_id = response.headers["x-request-id"]

        # Should be valid UUID
        try:
            uuid.UUID(request_id)
        except ValueError:
            pytest.fail(f"Request ID {request_id} is not a valid UUID")

    @pytest.mark.asyncio
    async def test_different_requests_have_different_ids(self):
        """Each request should get a unique ID"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response1 = await client.get("/health")
            response2 = await client.get("/health")

        id1 = response1.headers["x-request-id"]
        id2 = response2.headers["x-request-id"]

        assert id1 != id2


class TestRequestIDContextVar:
    """Tests for request ID context variable"""

    def test_get_request_id_when_not_set(self):
        """Should return empty string when not set"""
        # Reset context
        request_id_var.set("")

        result = get_request_id()
        assert result == ""

    def test_set_and_get_request_id(self):
        """Should be able to set and get request ID"""
        test_id = "test-123-uuid"
        set_request_id(test_id)

        result = get_request_id()
        assert result == test_id

        # Cleanup
        request_id_var.set("")


class TestRequestIDInErrorResponses:
    """Tests for request ID in error responses"""

    @pytest.mark.asyncio
    async def test_error_response_contains_request_id_in_header(self):
        """Error responses should include request ID in header"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/nonexistent-endpoint-12345")

        # Should have request ID in header
        assert "x-request-id" in response.headers

    @pytest.mark.asyncio
    async def test_validation_error_has_request_id(self):
        """Validation errors should include requestId"""
        # Use an endpoint that triggers validation
        from app.exceptions import ValidationError

        @app.get("/test-validation-inline")
        async def test_validation_inline():
            raise ValidationError(
                "Test validation", detail={"errors": [{"field": "test", "message": "error"}]}
            )

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/test-validation-inline")

        assert response.status_code == 422
        data = response.json()

        assert "requestId" in data
        assert data["requestId"] is not None
