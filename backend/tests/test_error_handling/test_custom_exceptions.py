"""Tests for custom exception classes"""

import pytest
from fastapi import status

from app.exceptions import (
    AppException,
    ConflictError,
    ForbiddenError,
    NotFoundError,
    RateLimitError,
    UnauthorizedError,
    ValidationError,
)


class TestAppException:
    """Tests for base AppException class"""

    def test_default_status_code(self):
        """Default status code should be 400"""
        exc = AppException("Test error")
        assert exc.status_code == status.HTTP_400_BAD_REQUEST

    def test_custom_status_code(self):
        """Should accept custom status code"""
        exc = AppException("Test error", status_code=418)
        assert exc.status_code == 418

    def test_error_code(self):
        """Should store error code"""
        exc = AppException("Test error", error_code="TEST_ERROR")
        assert exc.error_code == "TEST_ERROR"

    def test_detail_dict(self):
        """Should store detail dictionary"""
        exc = AppException("Test error", detail={"field": "value"})
        assert exc.detail == {"field": "value"}


class TestValidationError:
    """Tests for ValidationError exception"""

    def test_status_code_422(self):
        """Should map to HTTP 422"""
        exc = ValidationError("Validation failed")
        assert exc.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_error_code(self):
        """Should have correct error code"""
        exc = ValidationError("Validation failed")
        assert exc.error_code == "VALIDATION_ERROR"

    def test_with_field_errors(self):
        """Should accept field errors in detail"""
        errors = [{"field": "email", "message": "Invalid format"}]
        exc = ValidationError("Validation failed", detail={"errors": errors})
        assert exc.detail["errors"] == errors


class TestUnauthorizedError:
    """Tests for UnauthorizedError exception"""

    def test_status_code_401(self):
        """Should map to HTTP 401"""
        exc = UnauthorizedError()
        assert exc.status_code == status.HTTP_401_UNAUTHORIZED

    def test_default_message(self):
        """Should have default message"""
        exc = UnauthorizedError()
        assert exc.message == "Unauthorized"

    def test_custom_message(self):
        """Should accept custom message"""
        exc = UnauthorizedError("Token expired")
        assert exc.message == "Token expired"


class TestForbiddenError:
    """Tests for ForbiddenError exception"""

    def test_status_code_403(self):
        """Should map to HTTP 403"""
        exc = ForbiddenError()
        assert exc.status_code == status.HTTP_403_FORBIDDEN

    def test_default_message(self):
        """Should have default message"""
        exc = ForbiddenError()
        assert exc.message == "Forbidden"


class TestNotFoundError:
    """Tests for NotFoundError exception"""

    def test_status_code_404(self):
        """Should map to HTTP 404"""
        exc = NotFoundError("Not found")
        assert exc.status_code == status.HTTP_404_NOT_FOUND

    def test_default_resource(self):
        """Should have default resource type"""
        exc = NotFoundError("Not found")
        assert exc.detail["resource"] == "Resource"

    def test_custom_resource(self):
        """Should accept custom resource type"""
        exc = NotFoundError("Not found", resource="product")
        assert exc.detail["resource"] == "product"


class TestConflictError:
    """Tests for ConflictError exception"""

    def test_status_code_409(self):
        """Should map to HTTP 409"""
        exc = ConflictError("Conflict")
        assert exc.status_code == status.HTTP_409_CONFLICT

    def test_error_code(self):
        """Should have correct error code"""
        exc = ConflictError("Conflict")
        assert exc.error_code == "CONFLICT"


class TestRateLimitError:
    """Tests for RateLimitError exception"""

    def test_status_code_429(self):
        """Should map to HTTP 429"""
        exc = RateLimitError()
        assert exc.status_code == status.HTTP_429_TOO_MANY_REQUESTS

    def test_retry_after(self):
        """Should store retry_after in detail"""
        exc = RateLimitError("Rate limited", retry_after=60)
        assert exc.detail["retry_after"] == 60

    def test_no_retry_after(self):
        """Should not have retry_after when not specified"""
        exc = RateLimitError("Rate limited")
        assert "retry_after" not in exc.detail or exc.detail.get("retry_after") is None
