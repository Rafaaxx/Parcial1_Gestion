## Why

Food Store requires a solid backend foundation to support all 16 changes that follow. Without a properly configured FastAPI server, database schema, ORM setup, and architectural patterns (Unit of Work, BaseRepository, dependency injection), all subsequent features would be built on unstable ground. This change establishes the critical infrastructure: database connection pool, SQLModel ORM initialization, the generic BaseRepository[T] pattern for all CRUD operations, the Unit of Work context manager for atomic transactions, and the foundational async/await pipeline that all other services will depend on.

## What Changes

- **FastAPI application** scaffold with Uvicorn server
- **PostgreSQL database** with connection pooling (asyncpg via SQLAlchemy 2.0)
- **SQLModel** ORM initialization with core mixins (timestamps, soft delete flags)
- **BaseRepository[T]** generic class for common CRUD patterns (find, create, update, delete, soft delete)
- **UnitOfWork** context manager pattern for atomic multi-entity transactions
- **Alembic migrations** system setup (initial migration with empty tables)
- **Pydantic settings** for environment config (DB URL, DEBUG, JWT secret)
- **Swagger/OpenAPI** documentation at `/docs` and `/redoc`
- **Logger** configuration (structured logging, rotation)
- **Async database session** lifecycle management with dependency injection

## Capabilities

### New Capabilities

- `backend-fastapi-scaffold`: Core FastAPI application, routing, middleware, exception handlers
- `database-postgres-async`: PostgreSQL connection pool, asyncpg driver, session lifecycle
- `orm-sqlmodel`: SQLModel ORM initialization, base models, common mixins (created_at, updated_at, deleted_at)
- `generic-repository-pattern`: BaseRepository[T] for CRUD, soft delete, query builders
- `unit-of-work-pattern`: Transaction context manager, rollback/commit semantics, multi-entity atomicity
- `alembic-migrations`: Database versioning system, initial migration structure, CLI commands
- `config-environment`: Pydantic settings, env file support, validation

### Modified Capabilities

(None — this is greenfield infrastructure)

## Impact

- **Database schema**: PostgreSQL with 0 initial tables (schema created via migrations)
- **Backend codebase**: `backend/` directory created with app/, models/, repositories/, services/, schemas/ structure
- **Configuration**: `.env.example` file with required environment variables
- **Dependencies**: FastAPI, SQLAlchemy 2.0, SQLModel, asyncpg, Alembic, Pydantic, python-dotenv
- **Development**: PostgreSQL database must be running locally (or Docker container)
