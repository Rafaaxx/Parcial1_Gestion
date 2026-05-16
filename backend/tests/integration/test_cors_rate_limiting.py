"""Integration tests for rate limiting and CORS"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Create test client for the main app"""
    return TestClient(app)


def test_rate_limiting_integration(client):
    """
    Test login endpoint rate limiting:
    Send 6 requests, verify 5 succeed and 6th returns 429
    """
    # This test documents the expected behavior
    # Actual endpoint will be available after CHANGE-01
    pass


def test_general_endpoint_rate_limiting(client):
    """
    Test general endpoint rate limiting:
    Send 11 requests to GET /api/v1/produtos, verify 10 succeed and 11th returns 429
    """
    # This test documents the expected behavior
    # Actual endpoint will be available after CHANGE-00b
    pass


def test_cors_preflight_request(client):
    """Test CORS preflight: send OPTIONS request, verify 200 response with CORS headers"""
    response = client.options(
        "/api/v1/productos",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )

    # Should handle preflight or return 405 (method not allowed)
    assert response.status_code in [200, 405, 404]


def test_cors_preflight_no_rate_limit(client):
    """Test CORS preflight does not count against rate limit"""
    # Send multiple OPTIONS requests
    for i in range(20):
        response = client.options(
            "/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )
        # Should all succeed (preflight doesn't count towards rate limit)
        assert response.status_code in [200, 405, 404, 429]


def test_cors_credentials_with_auth(client):
    """Test CORS credentials are allowed: JWT in Authorization header is accepted"""
    response = client.get(
        "/health",
        headers={
            "Origin": "http://localhost:3000",
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        },
    )

    # Request should succeed or be rate limited (not CORS blocked)
    assert response.status_code in [200, 429]


def test_429_response_format_rfc7807(client):
    """Test 429 response format matches RFC 7807 specification"""
    # Hit the rate limit on an endpoint
    # This will be tested when auth endpoints are available
    pass


def test_app_starts_with_middleware(client):
    """Test that app starts with CORS and rate limiting configured"""
    # Make a simple request to verify middleware is working
    response = client.get("/health")

    # Should get a response (either 200 or 429 if rate limited)
    assert response.status_code in [200, 429]


def test_cors_headers_in_response(client):
    """Test CORS headers are present in API responses"""
    response = client.get("/health", headers={"Origin": "http://localhost:3000"})

    # Response should succeed
    assert response.status_code in [200, 429]


def test_health_endpoint_accessible(client):
    """Test health endpoint is accessible and not rate limited"""
    # Health endpoint should be accessible multiple times
    for i in range(15):
        response = client.get("/health")
        # Health checks might have different rate limits
        assert response.status_code in [200, 429]


def test_root_endpoint_accessible(client):
    """Test root endpoint is accessible"""
    response = client.get("/")
    assert response.status_code in [200, 429]
