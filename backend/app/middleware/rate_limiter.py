"""Rate limiting middleware using slowapi"""

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

# Initialize limiter with in-memory storage
limiter = Limiter(key_func=get_remote_address, default_limits=["10/10 seconds"])


async def rate_limit_error_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """
    Custom exception handler for rate limit exceeded errors.
    Returns RFC 7807 formatted error response with 429 status.
    """
    # Extract rate limit info from slowapi
    limit_string = exc.detail  # e.g., "10 per 10 seconds"
    
    # Parse retry-after from the limit string (crude but effective)
    retry_after = 10  # default to 10 seconds
    if "15 minute" in limit_string.lower():
        retry_after = 900  # 15 minutes in seconds
    elif "1 minute" in limit_string.lower():
        retry_after = 60
    elif "10 second" in limit_string.lower():
        retry_after = 10
    
    error_detail = {
        "type": "https://api.foodstore.com/errors/rate-limit-exceeded",
        "title": "Too Many Requests",
        "status": 429,
        "detail": f"Rate limit exceeded. Retry after {retry_after} seconds.",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "instance": str(request.url),
        "retry_after": retry_after,
    }
    
    logger.warning(f"Rate limit exceeded for {get_remote_address(request)}")
    
    return JSONResponse(
        status_code=429,
        content=error_detail,
        headers={
            "Retry-After": str(retry_after),
            "X-RateLimit-Limit": exc.detail.split()[0] if exc.detail else "unknown",
        }
    )
