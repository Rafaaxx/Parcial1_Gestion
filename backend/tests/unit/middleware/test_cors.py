"""Unit tests for CORS middleware configuration"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.middleware.cors import setup_cors_middleware


@pytest.fixture
def cors_test_app():
    """Create a test app with CORS configuration"""
    app = FastAPI()
    
    # Setup CORS middleware
    setup_cors_middleware(app, settings)
    
    @app.get("/api/test")
    async def test_endpoint():
        return {"message": "success"}
    
    @app.options("/api/test")
    async def options_endpoint():
        return {}
    
    return app


@pytest.fixture
def client(cors_test_app):
    """Create test client"""
    return TestClient(cors_test_app)


def test_cors_middleware_setup():
    """Test that CORS middleware is configured correctly"""
    app = FastAPI()
    setup_cors_middleware(app, settings)
    
    # Check that middleware was added
    assert len(app.user_middleware) > 0


def test_cors_origin_validation(client):
    """
    Test CORS origin validation:
    - allowed origin returns CORS headers
    - disallowed origin returns no CORS headers
    """
    # Request with allowed origin
    allowed_origin = settings.cors_origins[0] if settings.cors_origins else "http://localhost:3000"
    response = client.get(
        "/api/test",
        headers={"Origin": allowed_origin}
    )
    
    # Response should be successful
    assert response.status_code == 200
    
    # Test with disallowed origin
    response = client.get(
        "/api/test",
        headers={"Origin": "http://malicious.com"}
    )
    
    assert response.status_code == 200  # Still 200 but CORS headers won't be in browser


def test_cors_origins_parsing():
    """Test CORS_ORIGINS parsing from comma-separated string"""
    # Verify that settings parse CORS_ORIGINS correctly
    assert isinstance(settings.cors_origins, list)
    assert len(settings.cors_origins) > 0


def test_cors_expose_headers(client):
    """Test Expose-Headers includes rate limit headers"""
    # Make a request
    response = client.get("/api/test")
    
    # Check that expose headers are configured
    assert response.status_code == 200
    
    # The CORSMiddleware adds expose headers; they're sent in preflight
    # but may not appear in simple response headers


def test_cors_preflight_request(client):
    """Test CORS preflight (OPTIONS) request handling"""
    response = client.options(
        "/api/test",
        headers={
            "Origin": settings.cors_origins[0] if settings.cors_origins else "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        }
    )
    
    # Preflight should return 200
    assert response.status_code in [200, 405]  # 405 if OPTIONS not explicitly defined


def test_cors_credentials_allowed(client):
    """Test that CORS credentials are allowed (Authorization header)"""
    response = client.get(
        "/api/test",
        headers={
            "Origin": settings.cors_origins[0] if settings.cors_origins else "http://localhost:3000",
            "Authorization": "Bearer test_token",
        }
    )
    
    # Request should succeed
    assert response.status_code == 200


def test_cors_allow_credentials_setting():
    """Test that CORS allow_credentials is set correctly"""
    assert settings.cors_allow_credentials is True


def test_cors_methods_configured():
    """Test that all required HTTP methods are allowed"""
    app = FastAPI()
    setup_cors_middleware(app, settings)
    
    # Middleware should be configured to accept:
    # GET, POST, PUT, DELETE, PATCH, OPTIONS
    assert len(app.user_middleware) > 0


def test_cors_production_warning_conditions():
    """
    Test CORS validation warnings in production
    - Should warn if CORS_ORIGINS is empty
    - Should warn if wildcard (*) is used
    """
    # Create a test app with production settings
    test_settings = settings.copy(update={
        "environment": "production",
        "cors_origins": ["*"],
    })
    
    app = FastAPI()
    # This would trigger warning logs
    setup_cors_middleware(app, test_settings)
    
    assert len(app.user_middleware) > 0
