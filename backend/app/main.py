"""FastAPI application entry point"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.database import engine, Base
from app.handlers import register_exception_handlers
from app.logging_config import setup_logging
from app.middleware.cors import setup_cors_middleware
from app.middleware.rate_limiter import limiter, rate_limit_error_handler
from app.middleware.request_id import RequestIDMiddleware
from app.modules.auth.router import router as auth_router
from app.modules.categorias.router import router as categorias_router
from app.modules.ingredientes.router import router as ingredientes_router
from app.modules.productos.router import router as productos_router
from app.modules.direcciones.router import router as router_direcciones
from app.modules.pedidos.router import router as pedidos_router
from app.modules.pagos.router import router as pagos_router
from app.modules.admin.router import router as admin_router
from app.modules.perfil.router import router as perfil_router

# Configure logging
setup_logging()
logger = logging.getLogger(__name__)


# Lifespan events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager"""
    # Startup
    logger.info(f"[STARTUP] {settings.app_name} v{settings.app_version} starting...")
    logger.info(f"[STARTUP] Environment: {settings.environment}")
    logger.info(f"[STARTUP] Debug mode: {settings.debug}")
    
    # Log CORS configuration
    logger.info(f"[STARTUP] CORS origins: {settings.cors_origins}")
    
    # Log rate limiting configuration
    if settings.rate_limit_enabled:
        logger.info(f"[STARTUP] Rate limiting ENABLED")
        logger.info(f"[STARTUP]   - General limit: {settings.rate_limit_general_limit}")
        logger.info(f"[STARTUP]   - Auth limit: {settings.rate_limit_auth_limit}")
        logger.info(f"[STARTUP]   - Refresh limit: {settings.rate_limit_refresh_limit}")
    else:
        logger.info(f"[STARTUP] Rate limiting DISABLED")
    
    yield
    
    # Shutdown
    logger.info("[SHUTDOWN] Application shutting down...")
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

# Add Request ID middleware for tracing
app.add_middleware(RequestIDMiddleware)

# Register rate limit exception handler (for slowapi)
app.add_exception_handler(RateLimitExceeded, rate_limit_error_handler)

# Register RFC 7807 exception handlers
register_exception_handlers(app)


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

# ── Productos Router ───────────────────────────────────────────────────────────
app.include_router(productos_router)

# ── Direcciones Router ────────────────────────────────────────────────────────────
app.include_router(router_direcciones)

# ── Pedidos Router ───────────────────────────────────────────────────────────────
app.include_router(pedidos_router, prefix="/api/v1")

# ── Pagos Router ───────────────────────────────────────────────────────────────
app.include_router(pagos_router, prefix="/api/v1")

# ── Admin Router ───────────────────────────────────────────────────────────────
# Note: admin_router already has prefix="/api/v1/admin" in its definition
app.include_router(admin_router)

# ── Perfil Router ─────────────────────────────────────────────────────────────
app.include_router(perfil_router)


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )