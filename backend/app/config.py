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

    # CORS
    cors_origins: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    # Mercado Pago
    mp_access_token: str = "TEST-"
    mp_public_key: str = "TEST-"
    mp_notification_url: str = "http://localhost:8000/api/v1/pagos/webhook"

    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/app.log"

    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 5
    rate_limit_period: int = 900  # 15 minutes in seconds

    # Email Configuration (optional)
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from_email: str = "no-reply@foodstore.com"

    class Config:
        env_file = ".env"
        case_sensitive = False


# Instantiate settings
settings = Settings()
