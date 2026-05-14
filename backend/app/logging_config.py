"""Logging configuration for the application with structured logging"""

import json
import logging
import logging.handlers
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from app.config import settings


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""

    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add extra fields
        if hasattr(record, "request_id") and record.request_id:
            log_data["request_id"] = record.request_id

        if hasattr(record, "user_id") and record.user_id:
            log_data["user_id"] = record.user_id

        if hasattr(record, "path") and record.path:
            log_data["path"] = record.path

        if hasattr(record, "method") and record.method:
            log_data["method"] = record.method

        # Add extra context
        if hasattr(record, "extra") and record.extra:
            for key, value in record.extra.items():
                if key not in ["request_id", "user_id", "path", "method"]:
                    # Filter sensitive data
                    if not _is_sensitive_key(key):
                        log_data[key] = value

        # Add exception info for errors
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add function and line for debugging
        if record.levelno >= logging.DEBUG and settings.debug:
            log_data["function"] = record.funcName
            log_data["line"] = record.lineno

        return json.dumps(log_data)


def _is_sensitive_key(key: str) -> bool:
    """Check if a log key contains sensitive data"""
    sensitive_patterns = [
        "password",
        "token",
        "secret",
        "key",
        "authorization",
        "access_token",
        "refresh_token",
        "card_number",
        "credit_card",
        "cvv",
    ]
    key_lower = key.lower()
    return any(pattern in key_lower for pattern in sensitive_patterns)


class SensitiveDataFilter(logging.Filter):
    """Filter to exclude sensitive data from logs"""

    def filter(self, record: logging.LogRecord) -> bool:
        # Check message for sensitive patterns
        msg = record.getMessage().lower()
        sensitive_patterns = [
            "password=",
            "token=",
            "authorization=",
            "secret=",
        ]

        for pattern in sensitive_patterns:
            if pattern in msg:
                # Mask the sensitive part
                idx = msg.find(pattern)
                record.msg = record.msg[: idx + len(pattern)] + "***MASKED***"

        return True


def setup_logging():
    """Configure application-wide logging with rotation and structured output"""

    # Create logs directory if it doesn't exist
    log_dir = Path(settings.log_file).parent
    log_dir.mkdir(parents=True, exist_ok=True)

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(settings.log_level)

    # Remove existing handlers to avoid duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Console handler - human readable in development
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if settings.debug else logging.INFO)

    if settings.debug:
        # In debug mode, use readable format
        console_formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    else:
        # In production, use JSON
        console_formatter = JSONFormatter()

    console_handler.setFormatter(console_formatter)
    console_handler.addFilter(SensitiveDataFilter())
    root_logger.addHandler(console_handler)

    # File handler with rotation (all levels in JSON format)
    file_handler = logging.handlers.RotatingFileHandler(
        filename=settings.log_file,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,  # Keep 5 backup files
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(JSONFormatter())
    file_handler.addFilter(SensitiveDataFilter())
    root_logger.addHandler(file_handler)

    # Suppress verbose logs from third-party libraries
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.WARNING)

    root_logger.info(f"Logging configured: {settings.log_level} level (debug={settings.debug})")
    return root_logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the given name"""
    return logging.getLogger(name)
