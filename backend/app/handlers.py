"""Exception handlers for RFC 7807 Problem Details format"""

import logging
import traceback
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import settings
from app.exceptions import (
    AppException,
    ConflictError,
    ForbiddenError,
    NotFoundError,
    RateLimitError,
    UnauthorizedError,
    ValidationError,
)

logger = logging.getLogger(__name__)

# Base URL for error type URIs
BASE_ERROR_URL = "https://api.foodstore.com/errors"


def get_request_id(request: Request) -> str:
    """Extract request ID from state or generate new one"""
    return getattr(request.state, "request_id", str(uuid.uuid4()))


def format_rfc7807_error(
    title: str,
    status: int,
    detail: str,
    errors: Optional[List[Dict[str, str]]] = None,
    request: Optional[Request] = None,
    request_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Format error response according to RFC 7807"""
    # Handle case where title or detail might be a dict (from FastAPI/Starlette)
    if isinstance(title, dict):
        title_str = title.get("detail", title.get("code", "Error"))
    else:
        title_str = str(title) if title else "Error"

    # Handle detail that might also be a dict
    if isinstance(detail, dict):
        detail_str = detail.get("detail", str(detail))
    else:
        detail_str = str(detail) if detail else f"HTTP {status}"

    error_type = f"{BASE_ERROR_URL}/{title_str.lower().replace(' ', '-')}"

    response = {
        "type": error_type,
        "title": title_str,
        "status": status,
        "detail": detail_str,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "instance": str(request.url.path) if request else None,
    }

    if errors:
        response["errors"] = errors

    if request_id:
        response["requestId"] = request_id

    return response


async def validation_error_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """Handler for ValidationError (HTTP 422)"""
    errors = exc.detail.get("errors") if exc.detail else None
    request_id = get_request_id(request)

    logger.warning(
        f"Validation error: {exc.message}",
        extra={"request_id": request_id, "errors": errors},
    )

    return JSONResponse(
        status_code=422,
        content=format_rfc7807_error(
            title="Validation Error",
            status=422,
            detail=exc.message,
            errors=errors,
            request=request,
            request_id=request_id,
        ),
    )


async def unauthorized_error_handler(request: Request, exc: UnauthorizedError) -> JSONResponse:
    """Handler for UnauthorizedError (HTTP 401)"""
    request_id = get_request_id(request)

    logger.warning(
        f"Unauthorized: {exc.message}",
        extra={"request_id": request_id},
    )

    return JSONResponse(
        status_code=401,
        content=format_rfc7807_error(
            title="Unauthorized",
            status=401,
            detail=exc.message,
            request=request,
            request_id=request_id,
        ),
    )


async def forbidden_error_handler(request: Request, exc: ForbiddenError) -> JSONResponse:
    """Handler for ForbiddenError (HTTP 403)"""
    request_id = get_request_id(request)

    logger.warning(
        f"Forbidden: {exc.message}",
        extra={"request_id": request_id},
    )

    return JSONResponse(
        status_code=403,
        content=format_rfc7807_error(
            title="Forbidden",
            status=403,
            detail=exc.message,
            request=request,
            request_id=request_id,
        ),
    )


async def not_found_error_handler(request: Request, exc: NotFoundError) -> JSONResponse:
    """Handler for NotFoundError (HTTP 404)"""
    request_id = get_request_id(request)
    resource = exc.detail.get("resource", "Resource") if exc.detail else "Resource"

    logger.warning(
        f"Not found: {exc.message} ({resource})",
        extra={"request_id": request_id, "resource": resource},
    )

    return JSONResponse(
        status_code=404,
        content=format_rfc7807_error(
            title="Not Found",
            status=404,
            detail=exc.message,
            request=request,
            request_id=request_id,
        ),
    )


async def conflict_error_handler(request: Request, exc: ConflictError) -> JSONResponse:
    """Handler for ConflictError (HTTP 409)"""
    request_id = get_request_id(request)

    logger.warning(
        f"Conflict: {exc.message}",
        extra={"request_id": request_id},
    )

    return JSONResponse(
        status_code=409,
        content=format_rfc7807_error(
            title="Conflict",
            status=409,
            detail=exc.message,
            request=request,
            request_id=request_id,
        ),
    )


async def rate_limit_error_handler_new(request: Request, exc: RateLimitError) -> JSONResponse:
    """Handler for RateLimitError (HTTP 429)"""
    request_id = get_request_id(request)
    retry_after = exc.detail.get("retry_after") if exc.detail else None

    logger.warning(
        f"Rate limit exceeded: {exc.message}",
        extra={"request_id": request_id, "retry_after": retry_after},
    )

    response_content = format_rfc7807_error(
        title="Too Many Requests",
        status=429,
        detail=exc.message,
        request=request,
        request_id=request_id,
    )

    headers = {}
    if retry_after:
        headers["Retry-After"] = str(retry_after)

    return JSONResponse(
        status_code=429,
        content=response_content,
        headers=headers,
    )


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handler for generic AppException"""
    request_id = get_request_id(request)

    logger.error(
        f"AppException: {exc.message}",
        extra={"request_id": request_id, "error_code": exc.error_code},
        exc_info=exc,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=format_rfc7807_error(
            title="Error",
            status=exc.status_code,
            detail=exc.message,
            request=request,
            request_id=request_id,
        ),
    )


async def request_validation_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handler for Pydantic request validation errors (HTTP 422)"""
    request_id = get_request_id(request)

    # Convert Pydantic errors to RFC 7807 format
    errors = []
    for error in exc.errors():
        loc = error.get("loc", [])
        field = ".".join(str(l) for l in loc[1:] if l != "body") or "body"
        errors.append(
            {
                "field": field,
                "message": error.get("msg", "Validation error"),
            }
        )

    logger.warning(
        f"Request validation error: {len(errors)} errors",
        extra={"request_id": request_id, "errors": errors},
    )

    return JSONResponse(
        status_code=422,
        content=format_rfc7807_error(
            title="Validation Error",
            status=422,
            detail="Error de validación en los datos ingresados",
            errors=errors,
            request=request,
            request_id=request_id,
        ),
    )


async def starlette_http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    """Handler for Starlette native HTTP exceptions"""
    request_id = get_request_id(request)

    # Sanitize exc.detail: can be str or dict (e.g. {"code": "UNAUTHORIZED", "detail": "..."})
    raw_detail = exc.detail
    if isinstance(raw_detail, dict):
        title = raw_detail.get("detail", str(raw_detail))
        detail = raw_detail.get("detail", str(raw_detail))
    else:
        title = raw_detail or "Error"
        detail = raw_detail or f"HTTP {exc.status_code}"

    logger.warning(
        f"HTTP exception: {exc.status_code} - {detail}",
        extra={"request_id": request_id, "status_code": exc.status_code},
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=format_rfc7807_error(
            title=title,
            status=exc.status_code,
            detail=detail,
            request=request,
            request_id=request_id,
        ),
    )


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handler for uncaught exceptions (HTTP 500)"""
    request_id = get_request_id(request)

    # Log full traceback
    tb_str = traceback.format_exc()
    logger.error(
        f"Unhandled exception: {str(exc)}",
        extra={
            "request_id": request_id,
            "path": request.url.path,
            "method": request.method,
        },
        exc_info=exc,
    )

    # In production, hide details
    if not settings.debug:
        return JSONResponse(
            status_code=500,
            content=format_rfc7807_error(
                title="Internal Server Error",
                status=500,
                detail="An internal error occurred. Please try again later.",
                request=request,
                request_id=request_id,
            ),
        )

    # In development, show more details
    return JSONResponse(
        status_code=500,
        content=format_rfc7807_error(
            title="Internal Server Error",
            status=500,
            detail=str(exc),
            errors=[{"field": "traceback", "message": tb_str}],
            request=request,
            request_id=request_id,
        ),
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers with the FastAPI app"""
    app.add_exception_handler(ValidationError, validation_error_handler)
    app.add_exception_handler(UnauthorizedError, unauthorized_error_handler)
    app.add_exception_handler(ForbiddenError, forbidden_error_handler)
    app.add_exception_handler(NotFoundError, not_found_error_handler)
    app.add_exception_handler(ConflictError, conflict_error_handler)
    app.add_exception_handler(RateLimitError, rate_limit_error_handler_new)
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(RequestValidationError, request_validation_handler)
    app.add_exception_handler(StarletteHTTPException, starlette_http_exception_handler)
    app.add_exception_handler(Exception, global_exception_handler)

    logger.info("RFC 7807 exception handlers registered")
