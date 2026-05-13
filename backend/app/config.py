"""Application configuration using Pydantic Settings"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables or .env file"""

    # Application
    app_name: str = "Food Store API"
    app_version: str = "0.1.0"
    debug: bool = False
    environment: str = "development"

    # Database
    database_url: str
    database_pool_size: int = 20
    database_max_overflow: int = 10
    echo_sql: bool = False

    # JWT Authentication
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # CORS — Cross-Origin Resource Sharing
    # Whitelist specific frontend origins to prevent unauthorized cross-origin requests
    cors_origins: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    # Allow credentials (Authorization header, cookies) in CORS requests
    cors_allow_credentials: bool = True
    # Headers exposed to the frontend (must be explicitly listed for CORS)
    # Includes rate limit headers and pagination metadata
    cors_expose_headers: List[str] = [
        "X-RateLimit-Limit", 
        "X-RateLimit-Remaining", 
        "X-RateLimit-Reset", 
        "X-Total-Count", 
        "X-Page-Number"
    ]

    # Mercado Pago Integration
    mp_access_token: str = "TEST-"
    mp_public_key: str = "TEST-"
    mp_notification_url: str = "http://localhost:8000/api/v1/pagos/webhook"

    # Logging Configuration
    log_level: str = "INFO"
    log_file: str = "logs/app.log"

    # Rate Limiting — Protect API from abuse and brute-force attacks
    # Global flag to enable/disable rate limiting
    rate_limit_enabled: bool = True
    # Storage backend: "memory" (in-process) or "redis" (distributed)
    rate_limit_storage: str = "memory"
    # General API rate limit (e.g., "10/10 seconds" = 10 requests per 10 seconds)
    # Applied to most endpoints, allows burst traffic
    rate_limit_general_limit: str = "10/10 seconds"
    # Auth endpoints rate limit (e.g., "5/15 minutes" = 5 attempts per 15 min)
    # More restrictive to prevent brute-force login attempts
    rate_limit_auth_limit: str = "5/15 minutes"
    # Token refresh rate limit (e.g., "10/1 minute")
    # Moderate limit for token refresh operations
    rate_limit_refresh_limit: str = "10/1 minute"

    # Email Configuration (optional, for future notifications)
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from_email: str = "no-reply@foodstore.com"

    frontend_url: str = "http://localhost:5173"

    class Config:
        env_file = ".env"
        case_sensitive = False


# Instantiate settings (loaded once at app startup)
settings = Settings()

