"""FastAPI application entry point"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.database import engine, Base
from app.exceptions import AppException, app_exception_to_http_exception
from app.middleware.cors import setup_cors_middleware
from app.middleware.rate_limiter import limiter, rate_limit_error_handler
from app.modules.auth.router import router as auth_router
from app.modules.categorias.router import router as categorias_router
from app.modules.ingredientes.router import router as ingredientes_router
from app.modules.direcciones.router import router as router_direcciones

# Configure logging
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)


# Lifespan events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager"""
    # Startup
    logger.info(f"🚀 {settings.app_name} v{settings.app_version} starting...")
    logger.info(f"📊 Environment: {settings.environment}")
    logger.info(f"🔍 Debug mode: {settings.debug}")
    
    # Log CORS configuration
    logger.info(f"🔐 CORS origins: {settings.cors_origins}")
    
    # Log rate limiting configuration
    if settings.rate_limit_enabled:
        logger.info(f"⏱️  Rate limiting ENABLED")
        logger.info(f"   - General limit: {settings.rate_limit_general_limit}")
        logger.info(f"   - Auth limit: {settings.rate_limit_auth_limit}")
        logger.info(f"   - Refresh limit: {settings.rate_limit_refresh_limit}")
    else:
        logger.info(f"⏱️  Rate limiting DISABLED")
    
    yield
    
    # Shutdown
    logger.info("🛑 Application shutting down...")
    await engine.dispose()


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Backend for Food Store - e-commerce platform for food products",
    lifespan=lifespan,
    debug=settings.debug,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Register rate limiter with FastAPI (for dependency injection)
app.state.limiter = limiter

# Setup CORS middleware (must be first in the stack to handle preflight)
setup_cors_middleware(app, settings)

# Register rate limit exception handler
app.add_exception_handler(RateLimitExceeded, rate_limit_error_handler)


# Register exception handlers
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """Handle custom application exceptions"""
    logger.error(f"AppException: {exc.message}", exc_info=exc)
    http_exc = app_exception_to_http_exception(exc)
    return JSONResponse(
        status_code=http_exc.status_code,
        content=http_exc.detail,
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "code": "INTERNAL_SERVER_ERROR"},
    )


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint to verify the API is running"""
    return {"status": "ok", "app": settings.app_name, "version": settings.app_version}


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "documentation": "/docs"
    }


# ── Auth Router ──────────────────────────────────────────────────────────────

app.include_router(auth_router)


# ── Categorias Router ─────────────────────────────────────────────────────────

app.include_router(categorias_router)


# ── Ingredientes Router ───────────────────────────────────────────────────────────

app.include_router(ingredientes_router)


# ── Direcciones Router ────────────────────────────────────────────────────────────

app.include_router(router_direcciones)

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
