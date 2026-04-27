"""Custom exception classes for the application"""

from typing import Optional, Any, Dict
from fastapi import HTTPException, status


class AppException(Exception):
    """Base exception for the application"""
    
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        error_code: Optional[str] = None,
        detail: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.detail = detail or {}
        super().__init__(self.message)


class ValidationError(AppException):
    """Raised when input validation fails"""
    
    def __init__(self, message: str, detail: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="VALIDATION_ERROR",
            detail=detail,
        )


class NotFoundError(AppException):
    """Raised when a resource is not found"""
    
    def __init__(self, message: str, resource: str = "Resource"):
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="NOT_FOUND",
            detail={"resource": resource},
        )


class ConflictError(AppException):
    """Raised when there's a conflict (e.g., duplicate unique field)"""
    
    def __init__(self, message: str, detail: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            error_code="CONFLICT",
            detail=detail,
        )


class UnauthorizedError(AppException):
    """Raised when authentication fails"""
    
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="UNAUTHORIZED",
        )


class ForbiddenError(AppException):
    """Raised when user lacks permissions"""
    
    def __init__(self, message: str = "Forbidden"):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="FORBIDDEN",
        )


class DatabaseError(AppException):
    """Raised when a database operation fails"""
    
    def __init__(self, message: str, detail: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="DATABASE_ERROR",
            detail=detail,
        )


class RateLimitError(AppException):
    """Raised when rate limit is exceeded"""
    
    def __init__(self, message: str = "Too many requests", retry_after: Optional[int] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code="RATE_LIMIT_EXCEEDED",
            detail={"retry_after": retry_after} if retry_after else {},
        )


def app_exception_to_http_exception(exc: AppException) -> HTTPException:
    """Convert AppException to HTTPException for FastAPI"""
    return HTTPException(
        status_code=exc.status_code,
        detail={
            "detail": exc.message,
            "code": exc.error_code,
            **(exc.detail or {}),
        },
    )
