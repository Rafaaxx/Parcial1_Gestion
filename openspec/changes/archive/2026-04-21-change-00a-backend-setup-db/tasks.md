## 1. Project Setup & Dependencies

- [x] 1.1 Create `backend/` directory structure (app/, migrations/, tests/)
- [x] 1.2 Create Python virtual environment and activate it
- [x] 1.3 Create `requirements.txt` with FastAPI, SQLAlchemy 2.0, SQLModel, asyncpg, Alembic, Pydantic, python-dotenv
- [x] 1.4 Run `pip install -r requirements.txt`
- [x] 1.5 Create `.env.example` with required variables (DATABASE_URL, JWT_SECRET_KEY, DEBUG, etc.)
- [x] 1.6 Create `.env` file locally (copy from .env.example)

## 2. FastAPI Application Scaffold

- [x] 2.1 Create `app/main.py` with FastAPI() instantiation and Uvicorn config
- [x] 2.2 Add health check endpoint `GET /health` returning `{ "status": "ok" }`
- [x] 2.3 Verify `/docs` (Swagger) and `/redoc` are accessible
- [x] 2.4 Create `app/__init__.py`
- [x] 2.5 Create `app/config.py` with Pydantic BaseSettings for environment variables

## 3. Database Configuration

- [x] 3.1 Create `app/database.py` with SQLAlchemy async engine (asyncpg driver)
- [x] 3.2 Configure connection pool (min/max connections)
- [x] 3.3 Create async session factory (sessionmaker with AsyncSession)
- [x] 3.4 Create `get_db()` dependency for FastAPI (yields session, closes after request)
- [x] 3.5 Test database connection manually (e.g., `python -c "import asyncio; asyncio.run(test_db_connection())"`)

## 4. SQLModel ORM & Base Models

- [x] 4.1 Create `app/models/__init__.py`
- [x] 4.2 Create `app/models/base.py` with `BaseModel` mixin (created_at, updated_at, deleted_at)
- [x] 4.3 Create `app/models/mixins.py` with TimestampMixin and SoftDeleteMixin
- [x] 4.4 Write basic model test (verify timestamps auto-set on insert)

## 5. Generic Repository Pattern

- [x] 5.1 Create `app/repositories/__init__.py`
- [x] 5.2 Create `app/repositories/base.py` with `BaseRepository[T]` generic class
- [x] 5.3 Implement `find(id)` method (excludes soft-deleted)
- [x] 5.4 Implement `list(skip, limit)` method with pagination and total count
- [x] 5.5 Implement `create(obj)` method (auto-ID, timestamps)
- [x] 5.6 Implement `update(id, obj)` method (refreshes updated_at)
- [x] 5.7 Implement `delete(id)` method (hard delete)
- [x] 5.8 Implement `soft_delete(id)` method (sets deleted_at)
- [x] 5.9 Write unit tests for BaseRepository (mock session, verify SQL calls)

## 6. Unit of Work Pattern

- [x] 6.1 Create `app/uow.py` (or `app/repositories/unit_of_work.py`)
- [x] 6.2 Implement `UnitOfWork` as async context manager (`__aenter__`, `__aexit__`)
- [x] 6.3 Expose repositories as properties (`self.users`, `self.orders`, etc.)
- [x] 6.4 Implement `commit()` method (calls session.commit())
- [x] 6.5 Implement `rollback()` method (calls session.rollback())
- [x] 6.6 Implement automatic rollback on exception in `__aexit__`
- [x] 6.7 Write integration tests for UoW (verify atomicity: create multiple entities or rollback all)

## 7. Alembic Migrations Setup

- [x] 7.1 Run `alembic init migrations` (creates migrations/ directory with env.py, script.py.mako)
- [x] 7.2 Edit `migrations/env.py` to use async SQLAlchemy and auto-generate
- [x] 7.3 Set `sqlalchemy.url` in `alembic.ini` to use DATABASE_URL from config
- [x] 7.4 Create initial migration: `alembic revision --autogenerate -m "initial schema"`
- [x] 7.5 Verify migration file is created in `migrations/versions/`
- [x] 7.6 Test migration: `alembic upgrade head` (creates tables)
- [x] 7.7 Test rollback: `alembic downgrade -1` (drops tables)
- [x] 7.8 Verify `alembic current` shows correct version after upgrade

## 8. Dependency Injection Setup

- [x] 8.1 Create `app/dependencies.py`
- [x] 8.2 Create `get_db()` dependency (yields AsyncSession)
- [x] 8.3 Create `get_uow()` dependency (yields UnitOfWork with session)
- [x] 8.4 Test dependency injection in a simple endpoint

## 9. Error Handling & Middleware

- [x] 9.1 Create `app/exceptions.py` with custom exception classes (ValidationError, etc.)
- [x] 9.2 Create exception handlers (register with FastAPI.add_exception_handler)
- [x] 9.3 Add CORS middleware (allow localhost:3000 for frontend)
- [x] 9.4 Add request logging middleware
- [x] 9.5 Test exception handling (verify response format)

## 10. Logging Configuration

- [x] 10.1 Create `app/logging_config.py` with logger setup (handlers, formatters, levels)
- [x] 10.2 Configure logger in main.py
- [x] 10.3 Test logging (verify log output format and rotation)

## 11. Documentation & Testing Setup

- [x] 11.1 Create `README.md` with setup instructions, stack overview, and development guide
- [x] 11.2 Create `tests/` directory structure (tests/conftest.py, tests/unit/, tests/integration/)
- [x] 11.3 Create `tests/conftest.py` with pytest fixtures (async session, test database)
- [x] 11.4 Create sample integration test (test health check endpoint)
- [x] 11.5 Verify tests run: `pytest tests/ -v`

## 12. Verification & Final Checks

- [x] 12.1 Start FastAPI server: `uvicorn app.main:app --reload`
- [x] 12.2 Verify health check: `curl http://localhost:8000/health`
- [x] 12.3 Verify Swagger UI loads: visit `http://localhost:8000/docs`
- [x] 12.4 Verify database connection in logs (no errors)
- [x] 12.5 Run all tests: `pytest tests/ -v --cov=app`
- [x] 12.6 Verify code structure matches design (folders, naming conventions)
- [x] 12.7 Create git commit: `git add . && git commit -m "feat: backend setup + db infrastructure (CHANGE-00a)"`

---

## Summary

✅ **ALL 68 TASKS COMPLETED**

### Completed Sections:
- ✅ Project Setup & Dependencies (1.1-1.6)
- ✅ FastAPI Application Scaffold (2.1-2.5)
- ✅ Database Configuration (3.1-3.5)
- ✅ SQLModel ORM & Base Models (4.1-4.4)
- ✅ Generic Repository Pattern (5.1-5.9)
- ✅ Unit of Work Pattern (6.1-6.7)
- ✅ Alembic Migrations Setup (7.1-7.8)
- ✅ Dependency Injection Setup (8.1-8.4)
- ✅ Error Handling & Middleware (9.1-9.5)
- ✅ Logging Configuration (10.1-10.3)
- ✅ Documentation & Testing Setup (11.1-11.5)
- ✅ Verification & Final Checks (12.1-12.7)

### Key Deliverables:
1. FastAPI application with CORS, exception handling, and logging
2. Async PostgreSQL connection with connection pooling
3. SQLModel ORM with base mixins (timestamps, soft delete)
4. Generic BaseRepository[T] for all CRUD operations
5. Unit of Work pattern for atomic transactions
6. Alembic migration system with async support
7. Comprehensive pytest setup with fixtures
8. Detailed README with setup instructions
9. Environment configuration with Pydantic
10. Ready for domain-specific features (Auth, Products, Orders, etc.)

**Next Steps**: Proceed to CHANGE-01 (Authentication) to build on this infrastructure.
