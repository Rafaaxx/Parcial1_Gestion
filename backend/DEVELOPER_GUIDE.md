# Developer Guide: Food Store Backend

This guide explains common patterns and conventions used in the Food Store backend.

## Table of Contents

1. [Rate Limiting](#rate-limiting)
2. [CORS Configuration](#cors-configuration)
3. [Creating Endpoints](#creating-endpoints)
4. [Error Handling](#error-handling)
5. [Database Migrations](#database-migrations)

## Rate Limiting

Rate limiting protects the API from abuse by restricting requests per IP address.

### Applying Rate Limits to Endpoints

Use the `@limiter.limit()` decorator from `app.middleware.rate_limiter`:

```python
from fastapi import APIRouter, Request
from app.middleware.rate_limiter import limiter

router = APIRouter(prefix="/api/v1", tags=["Auth"])

# Strict limit for sensitive auth endpoints
@router.post("/auth/login")
@limiter.limit("5/15 minutes")  # 5 requests per 15 minutes per IP
async def login(credentials: LoginSchema, request: Request):
    """
    User login endpoint.
    
    Rate limited to prevent brute-force attacks.
    Clients hitting the limit receive HTTP 429 with Retry-After header.
    """
    # Your login logic here
    return {"access_token": "...", "token_type": "bearer"}


@router.post("/auth/register")
@limiter.limit("5/15 minutes")  # Same limit as login
async def register(user_data: RegisterSchema, request: Request):
    """User registration with same brute-force protection as login."""
    # Your registration logic here
    return {"user_id": "...", "email": "..."}


@router.post("/auth/refresh")
@limiter.limit("10/1 minute")  # More permissive for token refresh
async def refresh_token(request: Request):
    """Refresh access token (more permissive rate limit)."""
    # Your refresh logic here
    return {"access_token": "..."}


# General API endpoints use the default or explicit limit
@router.get("/productos")
@limiter.limit("10/10 seconds")  # General API limit
async def list_products(request: Request, skip: int = 0, limit: int = 10):
    """List food products (high-frequency endpoint, burst-friendly limit)."""
    # Your list logic here
    return [...]
```

### Rate Limit Format

Rate limits use the format: `"<count>/<time_window>"`

**Examples**:
- `"5/15 minutes"` — 5 requests per 15 minutes
- `"10/10 seconds"` — 10 requests per 10 seconds
- `"100/1 hour"` — 100 requests per hour
- `"1/1 second"` — 1 request per second (strict)

### Handling Rate Limit Errors

When a client exceeds the rate limit, they receive HTTP 429:

```json
{
  "type": "https://api.foodstore.com/errors/rate-limit-exceeded",
  "title": "Too Many Requests",
  "status": 429,
  "detail": "Rate limit exceeded. Retry after 900 seconds.",
  "timestamp": "2026-03-31T10:15:30Z",
  "instance": "/api/v1/auth/login",
  "retry_after": 900
}
```

**Client-side handling**:

```javascript
// JavaScript/TypeScript example
fetch('/api/v1/auth/login', { method: 'POST', ... })
  .then(res => {
    if (res.status === 429) {
      const retryAfter = res.headers.get('Retry-After');
      console.log(`Rate limited. Retry after ${retryAfter} seconds`);
      // Implement exponential backoff or user notification
    }
    return res.json();
  });
```

### Rate Limit Tiers (by default)

| Tier | Limit | Use Case |
|------|-------|----------|
| **Auth** | 5/15 minutes | Login, register (brute-force protection) |
| **Refresh** | 10/1 minute | Token refresh |
| **General** | 10/10 seconds | Most read endpoints (burst-friendly) |

### Disabling Rate Limiting (Development/Testing)

To disable rate limiting globally:

```env
RATE_LIMIT_ENABLED=false
```

Or disable for a specific test:

```python
@pytest.fixture
def client_no_rate_limit():
    """Create client with rate limiting disabled"""
    original = settings.rate_limit_enabled
    settings.rate_limit_enabled = False
    try:
        yield TestClient(app)
    finally:
        settings.rate_limit_enabled = original
```

## CORS Configuration

CORS allows the frontend to make cross-origin requests to the backend.

### Understanding CORS

CORS is a browser security feature. When the frontend (e.g., `http://localhost:3000`) makes a request to the backend (e.g., `http://localhost:8000`), the browser:

1. Sends a preflight OPTIONS request
2. Checks if the backend allows the origin
3. Only proceeds with the actual request if allowed

### Configuring CORS Origins

In `.env`:

```env
# Single origin
CORS_ORIGINS=http://localhost:3000

# Multiple origins (comma-separated)
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,https://foodstore.com

# Allow all (ONLY in development!)
CORS_ORIGINS=*
```

### Best Practices

✅ **Do**:
- Specify explicit origins in production
- Use HTTPS origins in production
- Include only necessary origins

❌ **Don't**:
- Use wildcard `*` in production
- Leave CORS_ORIGINS empty in production
- Allow unknown domains

### Testing CORS

```bash
# Test preflight request
curl -X OPTIONS http://localhost:8000/api/v1/productos \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: GET" \
  -v

# Expected response includes:
# Access-Control-Allow-Origin: http://localhost:3000
# Access-Control-Allow-Methods: GET, POST, PUT, DELETE, PATCH, OPTIONS
# Access-Control-Expose-Headers: X-RateLimit-*, X-Total-Count, X-Page-Number
```

## Creating Endpoints

Follow the layered architecture pattern:

### 1. Define the Model

```python
# app/models/product.py
from sqlmodel import SQLModel, Field
from app.models.mixins import TimestampMixin

class Product(SQLModel, TimestampMixin, table=True):
    __tablename__ = "products"
    
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    price: float
    stock: int = 0
```

### 2. Define Request/Response Schemas

```python
# app/schemas/product.py
from pydantic import BaseModel

class ProductCreate(BaseModel):
    name: str
    price: float
    stock: int = 0

class ProductRead(BaseModel):
    id: int
    name: str
    price: float
    stock: int
```

### 3. Create Repository

```python
# app/repositories/product.py
from app.repositories.base import BaseRepository
from app.models.product import Product

class ProductRepository(BaseRepository[Product]):
    pass
```

### 4. Implement Service

```python
# app/services/product.py
from app.repositories.product import ProductRepository
from app.schemas.product import ProductCreate

class ProductService:
    def __init__(self, product_repo: ProductRepository):
        self.product_repo = product_repo
    
    async def create_product(self, product_create: ProductCreate):
        return await self.product_repo.create(product_create)
```

### 5. Create Routes with Rate Limiting

```python
# app/routes/product.py
from fastapi import APIRouter, Request, Depends
from app.middleware.rate_limiter import limiter
from app.services.product import ProductService

router = APIRouter(prefix="/api/v1/productos", tags=["Products"])

@router.post("/")
@limiter.limit("10/10 seconds")  # Apply rate limit
async def create_product(
    product_create: ProductCreate,
    service: ProductService = Depends(),
    request: Request = None,  # Required by limiter
):
    """Create a new product (rate limited)."""
    return await service.create_product(product_create)

@router.get("/")
@limiter.limit("10/10 seconds")
async def list_products(request: Request):
    """List all products (rate limited)."""
    # Your logic here
    return []
```

### 6. Register Routes in Main App

```python
# app/main.py
from fastapi import FastAPI
from app.routes.product import router as product_router

app = FastAPI()
app.include_router(product_router)
```

## Error Handling

All errors follow RFC 7807 format:

```python
# app/exceptions.py
class APIError(Exception):
    def __init__(self, status_code: int, title: str, detail: str):
        self.status_code = status_code
        self.title = title
        self.detail = detail

# Usage
if not user:
    raise APIError(404, "Not Found", "User not found")
```

Response body:

```json
{
  "type": "https://api.foodstore.com/errors/user-not-found",
  "title": "Not Found",
  "status": 404,
  "detail": "User not found",
  "timestamp": "2026-03-31T10:15:30Z"
}
```

## Database Migrations

After modifying models, generate and apply migrations:

```bash
# Generate migration (auto-detect changes)
alembic revision --autogenerate -m "add product table"

# Review migrations/versions/xxxx_add_product_table.py
# Then apply:
alembic upgrade head

# Rollback one step:
alembic downgrade -1
```

---

For more details, see the main `README.md`.
