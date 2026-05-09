"""CORS middleware configuration using FastAPI/Starlette"""

from fastapi.middleware.cors import CORSMiddleware
from typing import List
import logging

logger = logging.getLogger(__name__)


def setup_cors_middleware(app, settings) -> None:
    """
    Configure CORS middleware for the FastAPI application.
    
    Args:
        app: FastAPI application instance
        settings: Application settings containing CORS configuration
    """
    
    # Parse CORS_ORIGINS from settings
    cors_origins = settings.cors_origins
    
    # Validate CORS configuration in production
    if settings.environment == "production":
        if not cors_origins:
            logger.warning(
                "CORS_ORIGINS is empty in production. "
                "This may cause CORS errors for frontend applications. "
                "Please set CORS_ORIGINS environment variable."
            )
        if "*" in cors_origins:
            logger.warning(
                "CORS wildcard (*) is enabled in production. "
                "This is a security risk. "
                "Please specify explicit origins in CORS_ORIGINS."
            )
    
    logger.info(f"Setting up CORS middleware with origins: {cors_origins}")
    
    # Add CORSMiddleware to the app
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins if cors_origins else ["*"],
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers=[
            "Content-Type",
            "Authorization",
            "Accept",
            "Origin",
            "User-Agent",
            "DNT",
            "Cache-Control",
            "X-Requested-With",
        ],
        expose_headers=settings.cors_expose_headers,
        max_age=3600,  # 1 hour
    )
    
    logger.info("CORS middleware configured successfully")
