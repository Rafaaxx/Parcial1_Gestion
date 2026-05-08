# Food Store Backend — FastAPI + PostgreSQL

Backend for Food Store, a comprehensive e-commerce platform for food products.

## Stack

- **Framework**: FastAPI 0.111+ (async, modern Python)
- **ORM**: SQLModel 0.0.16 (SQLAlchemy 2.0 + Pydantic)
- **Database**: PostgreSQL 15+ with asyncpg driver
- **Migrations**: Alembic 1.13+ (schema versioning)
- **Authentication**: JWT (python-jose)
- **Testing**: pytest + pytest-asyncio
- **Dev Server**: Uvicorn with auto-reload

## Quick Start

### 1. Prerequisites

- Python 3.10+
- PostgreSQL 15+ running locally (or Docker)
- pip and virtual environment

### 2. Installation

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (Windows)
python -m venv venv
venv\Scripts\activate.bat

# Or on Linux/macOS:
python -m venv venv
source venv/bin/activate

# Upgrade pip
python -m pip install --upgrade pip setuptools wheel

# Install dependencies
pip install -r requirements.txt
```

**Note**: On Windows, you can run the provided `install.bat` script instead:

```bash
cd backend
install.bat
```

### 3. Environment Configuration

Create `.env` file (copy from `.env.example`):

```bash
cp .env.example .env
```

Edit `.env` with your actual values:

```env
# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/food_store_db

# JWT
JWT_SECRET_KEY=your-super-secret-key-min-32-chars-required
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Environment
DEBUG=True
ENVIRONMENT=development

# CORS
CORS_ORIGINS=["http://localhost:5173", "http://localhost:3000"]

# Mercado Pago (Sandbox)
MP_ACCESS_TOKEN=TEST-xxxx
MP_PUBLIC_KEY=TEST-xxxx
```

### 4. Database Setup

#### Option A: PostgreSQL via Docker (Recommended for dev)

```bash
# In the project root, run:
docker-compose up -d

# This creates a PostgreSQL container with the food_store_db database
# PostgreSQL will be accessible at localhost:5432
```

#### Option B: Local PostgreSQL

Ensure PostgreSQL is running and create the database:

```sql
CREATE DATABASE food_store_db;
```

### 5. Run Migrations

```bash
# From backend/ directory with venv activated:
alembic upgrade head
```

This creates all necessary tables in the database.

### 6. Start Development Server

```bash
uvicorn app.main:app --reload
```

Server will start at `http://localhost:8000`

**Auto-reload is enabled** — changes to Python files will restart the server automatically.

### 7. Verify Installation

```bash
# Health check
curl http://localhost:8000/health

# Expected response:
# {"status": "ok", "app": "Food Store API", "version": "0.1.0"}

# Open API documentation
# Visit http://localhost:8000/docs (Swagger UI)
# Visit http://localhost:8000/redoc (ReDoc)
```

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app, routes, middleware
│   ├── config.py            # Pydantic settings from .env
│   ├── database.py          # SQLAlchemy async engine, session factory
│   ├── dependencies.py      # FastAPI dependency injection
│   ├── exceptions.py        # Custom exception classes
│   ├── logging_config.py    # Logging setup
│   ├── uow.py               # Unit of Work pattern
│   ├── models/              # SQLModel ORM definitions
│   │   ├── __init__.py
│   │   └── mixins.py        # Base mixins (timestamps, soft delete)
│   ├── repositories/        # Data access layer
│   │   ├── __init__.py
│   │   └── base.py          # Generic BaseRepository[T]
│   ├── schemas/             # Pydantic request/response models
│   ├── services/            # Business logic layer
│   ├── routes/              # API endpoints (by feature)
│   ├── middleware/          # Custom middleware
│   ├── exceptions/          # Exception handlers
│   └── utils/               # Utilities, validators, helpers
├── migrations/              # Alembic migration scripts
│   ├── env.py               # Alembic configuration
│   ├── versions/            # Individual migration files
│   └── script.py.mako       # Migration template
├── tests/                   # Test suite
│   ├── unit/                # Unit tests
│   ├── integration/         # Integration tests
│   └── conftest.py          # Pytest fixtures and config
├── .env.example             # Environment template
├── .env                     # Local environment (git-ignored)
├── requirements.txt         # Python dependencies
├── alembic.ini              # Alembic config
├── README.md                # This file
└── install.bat              # Windows installation helper
```

## Architecture

### Layered Architecture

```
┌─────────────────────────────────────────────────────┐
│ HTTP Layer (FastAPI Router)                         │
│ ↓ Validates request, calls Service                  │
├─────────────────────────────────────────────────────┤
│ Service Layer (Business Logic)                      │
│ ↓ Orchestrates repositories, applies rules          │
├─────────────────────────────────────────────────────┤
│ Unit of Work (Transaction Manager)                  │
│ ↓ Manages atomic operations, commit/rollback        │
├─────────────────────────────────────────────────────┤
│ Repository Layer (Data Access)                      │
│ ↓ Abstraction over database queries                 │
├─────────────────────────────────────────────────────┤
│ Model Layer (SQLModel ORM)                          │
│ ↓ Maps to database tables                           │
├─────────────────────────────────────────────────────┤
│ Database (PostgreSQL)                               │
└─────────────────────────────────────────────────────┘
```

### Design Patterns Used

1. **Repository Pattern**: `BaseRepository[T]` for CRUD abstraction
2. **Unit of Work**: Atomic transactions across multiple repositories
3. **Dependency Injection**: FastAPI's `Depends()` for loose coupling
4. **Mixins**: Reusable behavior (timestamps, soft delete)
5. **Async/Await**: All database operations are non-blocking

## Common Tasks

### CORS Configuration

CORS (Cross-Origin Resource Sharing) allows the frontend to make requests to the API from different domains.

**Configure CORS origins** in `.env`:

```env
# Comma-separated list of allowed origins
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,https://foodstore.com
CORS_ALLOW_CREDENTIALS=true
```

- `CORS_ORIGINS`: Comma-separated list of allowed frontend URLs
- `CORS_ALLOW_CREDENTIALS`: Allow cookies and Authorization headers (default: true)

**Exposed Headers**: The API exposes these headers for client consumption:
- `X-RateLimit-Limit`: Max requests allowed in the window
- `X-RateLimit-Remaining`: Requests remaining in current window
- `X-RateLimit-Reset`: Unix timestamp when limit resets
- `X-Total-Count`: Total items in a paginated response
- `X-Page-Number`: Current page number

**Warning**: 
- In production, NEVER use `CORS_ORIGINS=*` (wildcard). Always specify explicit origins.
- Empty `CORS_ORIGINS` in production will log a warning.

### Rate Limiting

Rate limiting protects the API from abuse and brute-force attacks by restricting the number of requests per IP address in a time window.

**Configure rate limiting** in `.env`:

```env
# Enable/disable rate limiting globally
RATE_LIMIT_ENABLED=true

# Rate limit tiers (format: requests/time_window)
RATE_LIMIT_GENERAL_LIMIT=10/10 seconds    # General API endpoints
RATE_LIMIT_AUTH_LIMIT=5/15 minutes        # Auth endpoints (login, register)
RATE_LIMIT_REFRESH_LIMIT=10/1 minute      # Token refresh endpoint

# Storage backend (currently: memory, future: redis)
RATE_LIMIT_STORAGE=memory
```

**Default Limits**:
- **General API**: 10 requests per 10 seconds (per IP)
- **Auth endpoints**: 5 requests per 15 minutes (per IP)
- **Token refresh**: 10 requests per 1 minute (per IP)

**How it works**:
1. Each request increments a counter per IP address
2. When the limit is reached, the API returns HTTP 429 (Too Many Requests)
3. The response includes `Retry-After` header with seconds to wait
4. Window resets after the specified time period

**429 Response Example**:

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

**Response Headers**:
- `Retry-After: 900` — Wait 900 seconds before retrying
- `X-RateLimit-Limit: 5` — Max requests in window
- `X-RateLimit-Remaining: 0` — Requests left
- `X-RateLimit-Reset: 1640000000` — Unix timestamp of reset

**Using Rate Limits in Code**:

When creating new endpoints, apply rate limit decorators:

```python
from app.middleware.rate_limiter import limiter

@router.post("/api/v1/auth/login")
@limiter.limit("5/15 minutes")  # 5 requests per 15 minutes
async def login(credentials: LoginSchema, request: Request):
    # Login logic here
    return {"token": "..."}

@router.get("/api/v1/productos")
@limiter.limit("10/10 seconds")  # 10 requests per 10 seconds (general API)
async def list_products(request: Request):
    # List logic here
    return [...]
```

**Disable Rate Limiting** (for testing):

```env
RATE_LIMIT_ENABLED=false
```

**For Load Balancers**:

If behind a load balancer, configure `X-Forwarded-For` header handling to ensure rate limits work correctly with multiple server IPs.

### Create a New API Endpoint

1. Define model in `app/models/<feature>.py`
2. Define schema in `app/schemas/<feature>.py`
3. Create repository in `app/repositories/<feature>.py`
4. Implement business logic in `app/services/<feature>.py`
5. Create routes in `app/routes/<feature>.py`
6. Register routes in `app/main.py`
7. **Apply rate limiting decorators** if needed

### Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=app

# Run specific test file
pytest tests/integration/test_health.py -v

# Run with asyncio output
pytest tests/ -v -s

# Run middleware tests specifically
pytest tests/unit/middleware/ -v
pytest tests/integration/test_cors_rate_limiting.py -v
```

### Generate Database Migration

After modifying models, auto-generate a migration:

```bash
# From backend/ directory:
alembic revision --autogenerate -m "description of changes"

# Review the generated migration in migrations/versions/
# Then apply it:
alembic upgrade head
```

### View Database Migrations History

```bash
# Show current migration revision
alembic current

# Show all revisions
alembic history

# Rollback to previous migration
alembic downgrade -1
```

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | ✅ | - | PostgreSQL connection string |
| `JWT_SECRET_KEY` | ✅ | - | Secret key for signing JWT tokens (min 32 chars) |
| `JWT_ALGORITHM` | ✅ | HS256 | JWT signing algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | ✅ | 30 | Access token expiry in minutes |
| `REFRESH_TOKEN_EXPIRE_DAYS` | ✅ | 7 | Refresh token expiry in days |
| `DEBUG` | ✅ | False | Enable FastAPI debug mode |
| `ENVIRONMENT` | ✅ | development | Environment name (development, production) |
| `CORS_ORIGINS` | ✅ | http://localhost:3000 | Comma-separated CORS allowed origins |
| `CORS_ALLOW_CREDENTIALS` | ❌ | true | Allow credentials (cookies, auth headers) |
| `RATE_LIMIT_ENABLED` | ❌ | true | Enable global rate limiting |
| `RATE_LIMIT_GENERAL_LIMIT` | ❌ | 10/10 seconds | General API rate limit |
| `RATE_LIMIT_AUTH_LIMIT` | ❌ | 5/15 minutes | Auth endpoints rate limit |
| `RATE_LIMIT_REFRESH_LIMIT` | ❌ | 10/1 minute | Token refresh rate limit |
| `RATE_LIMIT_STORAGE` | ❌ | memory | Rate limit storage backend (memory, redis) |
| `MP_ACCESS_TOKEN` | ✅ | - | Mercado Pago access token |
| `MP_PUBLIC_KEY` | ✅ | - | Mercado Pago public key |
| `LOG_LEVEL` | ❌ | INFO | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `LOG_FILE` | ❌ | logs/app.log | Path to log file |

## Troubleshooting

### "database.py connection pool errors"

**Symptom**: `asyncpg.exceptions.TooManyConnectionsError`

**Solution**: Check `DATABASE_URL` is correct and PostgreSQL is running:

```bash
# Test connection
psql -U postgres -h localhost -d food_store_db
```

### "ModuleNotFoundError: No module named 'app'"

**Solution**: Ensure you're running commands from the `backend/` directory with venv activated:

```bash
cd backend
venv\Scripts\activate.bat  # Windows
source venv/bin/activate  # Linux/macOS
```

### Migrations fail with "Alembic not found"

**Solution**: Install requirements:

```bash
pip install -r requirements.txt
```

## Deployment

See `DEPLOYMENT.md` for production setup (environment variables, database configuration, containerization).

## Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make changes following the architecture patterns
3. Write tests for new functionality
4. Run tests: `pytest tests/ -v`
5. Commit with conventional commits: `git commit -m "feat: description"`
6. Push and create a pull request

## License

Proprietary — Food Store Project
