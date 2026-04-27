## Context

Food Store is a greenfield project built with FastAPI (async Python backend) and React (frontend). The backend must support:
- Concurrent HTTP requests with async/await
- ACID transactions for critical flows (order creation, payment confirmation)
- Efficient database pooling for production-grade performance
- Pattern reuse: all 16 changes will use the same repository, service, and unit-of-work patterns

This design establishes the foundational layer—everything that comes after depends on it.

## Goals / Non-Goals

**Goals:**
- Establish a production-ready FastAPI application structure with proper async/await patterns
- Configure PostgreSQL with connection pooling for concurrent requests
- Implement generic BaseRepository[T] to eliminate CRUD boilerplate across all services
- Establish Unit of Work (context manager) pattern for atomic multi-entity transactions
- Set up Alembic for database versioning and migrations
- Configure Swagger/OpenAPI documentation at `/docs`
- Provide a clear folder structure that scales to 16+ changes without becoming a mess

**Non-Goals:**
- Authentication, authorization, or JWT (CHANGE-01)
- API endpoint logic beyond scaffolding (that's per-feature change)
- Frontend setup (CHANGE-00b)
- Docker/Kubernetes containerization (out of scope for now)

## Decisions

### 1. **Async FastAPI (not Django or Flask)**
**Decision**: Use FastAPI with Uvicorn for async-first HTTP handling.

**Rationale**: 
- All database calls in CHANGE-09 (order creation) and CHANGE-13 (webhook) must be non-blocking to handle concurrent requests.
- FastAPI is the only major Python web framework with native async/await support.
- Built-in OpenAPI/Swagger reduces documentation debt.

**Alternatives considered**:
- Django + Channels: Adds complexity; Django ORM is sync-first.
- Flask + asyncio: Async support is bolt-on, not native.
- FastAPI wins.

---

### 2. **SQLAlchemy 2.0 + SQLModel ORM (not raw SQL or other ORMs)**
**Decision**: Use SQLModel (Pydantic + SQLAlchemy) for ORM and schema validation.

**Rationale**:
- **Single schema definition**: SQLModel models double as Pydantic schemas (request/response validation) AND database models. Eliminates duplication.
- **Type safety**: Full TypeScript-like IDE support, catch type errors at dev time.
- **Async-first**: SQLAlchemy 2.0 with asyncpg driver supports async/await natively.
- **Migration support**: Alembic handles schema versioning as code.

**Alternatives considered**:
- Raw SQL: Fine for simple queries, but CHANGE-03 (hierarchical categories) needs complex CTEs. An ORM helps.
- Tortoise ORM: Less mature, smaller community.
- SQLAlchemy 1.4: Works but 2.0 is better for async.
- SQLModel wins for elegance + type safety.

---

### 3. **asyncpg as the database driver**
**Decision**: Use asyncpg (PostgreSQL-specific async driver).

**Rationale**:
- asyncpg is 10–20x faster than psycopg3 for reads because it skips network round-trips.
- Works seamlessly with SQLAlchemy 2.0's async API.
- PostgreSQL is ACID-compliant and free; perfect for e-commerce (critical for CHANGE-10's FSM atomicity).

**Alternatives considered**:
- psycopg3: Sync-first, slower.
- MySQL: No async driver as mature as asyncpg.
- SQLite: Not suitable for concurrent writes (food store needs concurrent orders).
- PostgreSQL + asyncpg wins.

---

### 4. **Alembic for database migrations**
**Decision**: Use Alembic (SQLAlchemy's migration tool) to version schema changes.

**Rationale**:
- Migrations are code: reviewable, reversible, part of git history.
- Alembic handles auto-generating migrations from model changes (most of the time).
- Critical for team collaboration: no two developers diverge on schema.

**Alternatives considered**:
- Raw SQL migrations: Hard to track dependencies.
- Directly modifying database: Loses history, can't rollback.
- Alembic wins.

---

### 5. **BaseRepository[T] Generic Pattern**
**Decision**: Implement a generic `BaseRepository[T]` that handles common CRUD for any model.

**Rationale**:
- CHANGE-01 through CHANGE-14 all need repository patterns (find by ID, list, create, update, delete, soft delete).
- Writing the same pattern 14 times = maintenance nightmare.
- `BaseRepository[T]` is written once, inherited by all service-specific repositories.

**Example**:
```python
class BaseRepository(Generic[T]):
    async def find(self, id: int) -> T | None: ...
    async def list(self, skip: int, limit: int) -> list[T]: ...
    async def create(self, obj: T) -> T: ...
    async def update(self, id: int, obj: T) -> T: ...
    async def soft_delete(self, id: int) -> None: ...

class CategoryRepository(BaseRepository[Categoria]):
    # Inherit all CRUD for free
    # Add custom logic (e.g., find_by_parent_id)
```

**Alternatives considered**:
- No base class, duplicate code everywhere: Unmaintainable.
- SQLAlchemy-utils: Too much magic, less control.
- BaseRepository wins.

---

### 6. **Unit of Work (UoW) Pattern**
**Decision**: Implement UoW as a context manager for atomic multi-entity transactions.

**Rationale**:
- CHANGE-09 (order creation) is all-or-nothing: create Pedido + DetallePedidos + HistorialEstadoPedido atomically, or rollback everything.
- A context manager makes this clean: `async with uow: uow.orders.create(...); uow.details.create(...)`
- If ANY operation fails, the context manager rolls back the transaction.

**Example**:
```python
async with UnitOfWork(db_session) as uow:
    pedido = await uow.orders.create(order_data)
    for item in items:
        await uow.details.create(pedido_id=pedido.id, item=item)
    await uow.commit()  # All-or-nothing
```

**Alternatives considered**:
- Service-level transaction handling: Scattered try/except blocks everywhere.
- Database-level triggers: Hard to test, logic hidden in SQL.
- UoW pattern wins for clarity and testability.

---

### 7. **Folder Structure**
**Decision**:
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI app instantiation
│   ├── config.py        # Pydantic settings
│   ├── routes/          # API endpoints (one per feature change)
│   │   ├── __init__.py
│   │   └── auth.py      # (added in CHANGE-01)
│   ├── models/          # SQLModel definitions
│   ├── schemas/         # Pydantic request/response models
│   ├── repositories/    # BaseRepository + concrete implementations
│   ├── services/        # Business logic
│   ├── middleware/      # CORS, error handling, logging
│   ├── exceptions/      # Custom exception classes
│   └── utils/           # Helpers (validators, formatters)
├── migrations/          # Alembic migration scripts
├── tests/               # Unit + integration tests
├── .env.example         # Environment template
├── requirements.txt     # Python dependencies
└── README.md            # Setup + development guide
```

---

### 8. **Environment Configuration**
**Decision**: Use Pydantic settings + `.env` files.

**Rationale**:
- Secrets (DB passwords, JWT keys) should NEVER be in code.
- `.env` is loaded at startup; easily overridable per environment (local, staging, prod).
- Pydantic validates: missing required vars fail loudly at startup.

**Example**:
```python
class Settings(BaseSettings):
    DATABASE_URL: str  # postgres://...
    JWT_SECRET_KEY: str
    DEBUG: bool = False
```

---

## Risks / Trade-offs

| Risk | Mitigation |
|------|-----------|
| **PostgreSQL not installed locally** | Provide `docker-compose.yml` to spin up Postgres + pgAdmin. Dev can run `docker-compose up` once. |
| **asyncpg requires asyncio event loop** | All database code must be `async`. If a dev forgets `async def`, the event loop won't work. Tests + linting catch this. |
| **UoW rollback on exception** | If an exception occurs mid-transaction, UoW auto-rolls back. This is **desired**—catching exceptions in tests ensures atomicity. Trade-off: adds complexity vs. sync code, but necessary for correctness. |
| **Alembic migrations can conflict** | If two devs create migrations simultaneously on different branches, git merge can break the migration order. Mitigation: code review migrations before merge; keep merge conflicts in `__pycache__` files. |
| **BaseRepository is generic** | Python's generics are compile-time only (no runtime type info). If someone passes the wrong type, it fails at runtime. Mitigation: type hints + mypy catch most errors. |

---

## Migration Plan

### Phase 1: Setup (2 hours)
1. Initialize FastAPI app scaffold with main.py, config.py
2. Set up PostgreSQL connection via asyncpg + SQLAlchemy 2.0
3. Create base SQLModel mixins (timestamps, soft delete)

### Phase 2: Patterns (3 hours)
4. Implement BaseRepository[T] with CRUD methods
5. Implement UnitOfWork context manager
6. Set up dependency injection (FastAPI Depends)

### Phase 3: Alembic & Documentation (2 hours)
7. Initialize Alembic and create `env.py`
8. Generate initial migration (empty schema)
9. Document setup + development guide in README.md

### Phase 4: Swagger & Validation (1 hour)
10. Ensure `/docs` is accessible
11. Set up logger configuration

**Rollback**: Each step is independent. If asyncpg fails, revert to step 1 and try psycopg3.

---

## Open Questions

- **Database:** Should we use a managed PostgreSQL (AWS RDS, Render.com) for deployment, or keep it local? → Decision postponed to deployment phase (CHANGE-16).
- **Logging:** JSON structured logs or plain text for dev? → Plain text for now; JSON for prod (via config).
- **Rate limiting**: CHANGE-00c will handle API-level rate limiting; should this change also limit database pool connections? → Covered in CHANGE-00c.
