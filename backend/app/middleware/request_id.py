"""Request ID middleware for tracing and correlation"""

import uuid
from contextvars import ContextVar
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

# Context variable to store request ID globally within a request
request_id_var: ContextVar[str] = ContextVar("request_id", default="")


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware that generates and tracks a unique request ID for each request"""
    
    async def dispatch(self, request: Request, call_next) -> Response:
        # Generate UUID for this request
        request_id = str(uuid.uuid4())
        
        # Store in context variable for global access
        request_id_var.set(request_id)
        
        # Store in request state for easy access
        request.state.request_id = request_id
        
        # Process request
        response = await call_next(request)
        
        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        
        return response


def get_request_id() -> str:
    """Get the current request ID from context"""
    return request_id_var.get("")


def set_request_id(request_id: str) -> None:
    """Set the request ID in context"""
    request_id_var.set(request_id)