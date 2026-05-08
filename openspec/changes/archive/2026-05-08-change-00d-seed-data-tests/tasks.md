## 1. Database Metadata Fix

- [ ] 1.1 Update `migrations/env.py` to use `SQLModel.metadata` as `target_metadata`
      - Change `from app.database import Base` → `from sqlmodel import SQLModel`
      - Change `target_metadata = Base.metadata` → `target_metadata = SQLModel.metadata`
      - Keep `from app.models import *` for model discovery
- [ ] 1.2 Update `tests/conftest.py` to use `SQLModel.metadata.create_all()` for test table creation
      - Change `await conn.run_sync(Base.metadata.create_all)` → `await conn.run_sync(SQLModel.metadata.create_all)`
      - Change `await conn.run_sync(Base.metadata.drop_all)` → `await conn.run_sync(SQLModel.metadata.drop_all)`
      - Keep `from app.database import Base` import (still needed for `get_db` dependency override), add `from sqlmodel import SQLModel`

## 2. SQLModel Models

- [ ] 2.1 Create `backend/app/models/rol.py` — `Rol` model (table `roles`)
      - Inherits `TimestampMixin` (not `table=True` in mixin)
      - `__tablename__ = "roles"`
      - `codigo: str = Field(max_length=20, primary_key=True)` — semantic PK
      - `descripcion: str = Field(max_length=100, nullable=False)`
      - `table=True` on the class itself
- [ ] 2.2 Create `backend/app/models/estado_pedido.py` — `EstadoPedido` model (table `estados_pedido`)
      - Inherits `TimestampMixin`
      - `__tablename__ = "estados_pedido"`
      - `codigo: str = Field(max_length=20, primary_key=True)` — semantic PK
      - `descripcion: str = Field(max_length=100, nullable=False)`
      - `orden: int = Field(nullable=False)` — FSM ordering
      - `es_terminal: bool = Field(default=False, nullable=False)` — terminal state flag
- [ ] 2.3 Create `backend/app/models/forma_pago.py` — `FormaPago` model (table `formas_pago`)
      - Inherits `TimestampMixin`
      - `__tablename__ = "formas_pago"`
      - `codigo: str = Field(max_length=20, primary_key=True)` — semantic PK
      - `descripcion: str = Field(max_length=100, nullable=False)`
      - `habilitado: bool = Field(default=True, nullable=False)` — can disable without delete
- [ ] 2.4 Create `backend/app/models/usuario.py` — `Usuario` model (table `usuarios`)
      - Inherits `BaseModel` (= `TimestampMixin` + `SoftDeleteMixin`)
      - `__tablename__ = "usuarios"`
      - `id: Optional[int] = Field(default=None, primary_key=True)` — BIGSERIAL autoincrement
      - `email: str = Field(max_length=254, unique=True, nullable=False, index=True)`
      - `password_hash: str = Field(max_length=60, nullable=False)` — bcrypt CHAR(60)
      - `nombre: str = Field(max_length=100, nullable=False)`
      - `apellido: str = Field(max_length=100, nullable=False)`
      - `telefono: Optional[str] = Field(max_length=20, default=None, nullable=True)`
      - `activo: bool = Field(default=True, nullable=False)`
- [ ] 2.5 Create `backend/app/models/usuario_rol.py` — `UsuarioRol` model (table `usuarios_roles`)
      - Inherits `TimestampMixin`
      - `__tablename__ = "usuarios_roles"`
      - `usuario_id: int = Field(foreign_key="usuarios.id", primary_key=True, ondelete="CASCADE")`
      - `rol_codigo: str = Field(max_length=20, foreign_key="roles.codigo", primary_key=True)`
      - `asignado_por_id: Optional[int] = Field(foreign_key="usuarios.id", default=None, nullable=True)`
      - Composite PK via two `primary_key=True` fields
- [ ] 2.6 Update `backend/app/models/__init__.py` to export all 5 new models
      - Add imports: `Rol`, `EstadoPedido`, `FormaPago`, `Usuario`, `UsuarioRol`
      - Update `__all__` to include all 5 models (keep `TimestampMixin`, `SoftDeleteMixin`)

## 3. Alembic Migration

- [ ] 3.1 Create `backend/migrations/versions/002_add_seed_models.py` — handwritten migration
      - Revision ID: `002_add_seed_models`, Revises: `001_initial`
      - `upgrade()`: create tables in dependency order (roles → estados_pedido → formas_pago → usuarios → usuarios_roles)
      - `upgrade()` includes: `op.create_table()`, `op.create_unique_constraint('uq_usuarios_email')`, `op.create_index('ix_usuarios_email')`, `op.create_primary_key()`, `op.create_foreign_key()` (3 FKs for usuarios_roles)
      - `downgrade()`: drop tables in reverse order (usuarios_roles → usuarios → formas_pago → estados_pedido → roles)
      - `downgrade()` includes: `op.drop_constraint('uq_usuarios_email')`, `op.drop_index('ix_usuarios_email')`
      - Column types match the design: `sa.String(20)`, `sa.BigInteger()`, `sa.DateTime(timezone=True)`, `sa.Boolean()` with `server_default`, etc.

## 4. Seed Script

- [ ] 4.1 Create `backend/app/db/__init__.py` — empty package init
- [ ] 4.2 Create `backend/app/db/seed.py` — async idempotent seed script
      - Read `SEED_ADMIN_PASSWORD` from env (fallback `Admin1234!`)
      - Hash admin password with `passlib.context.CryptContext(schemes=["bcrypt"])`
      - Async seed function using `async_session_factory()` from `app.database`
      - Insert order: Rol → EstadoPedido → FormaPago → Usuario → UsuarioRol
      - Use raw SQL `INSERT INTO ... ON CONFLICT DO NOTHING` via `session.execute()`
      - 4 roles: ADMIN, STOCK, PEDIDOS, CLIENT
      - 6 estados_pedido: PENDIENTE(1), CONFIRMADO(2), EN_PREP(3), EN_CAMINO(4), ENTREGADO(5, terminal), CANCELADO(6, terminal)
      - 3 formas_pago: MERCADOPAGO, EFECTIVO, TRANSFERENCIA (all habilitado=true)
      - 1 admin user: admin@foodstore.com with bcrypt-hashed password, nombre='Admin', apellido='User'
      - 1 usuario_rol: admin user + ADMIN role, asignado_por_id=NULL
      - `if __name__ == "__main__": asyncio.run(main())` for `python -m app.db.seed` invocation
      - Print success with row counts on completion; print error + exit(1) on failure
      - Dialect-aware: use `ON CONFLICT` for PostgreSQL, fallback for SQLite

## 5. Repository & UoW Tests

- [ ] 5.1 Create `backend/tests/unit/test_repository.py` with `TestModel` class and fixtures
      - Define `TestModel(BaseModel, table=True)` with `__tablename__ = "test_models"`, fields: `id` (PK), `name` (str), `value` (str)
      - Add `test_model_repo` fixture: `BaseRepository(test_db_session, TestModel)`
      - Ensure `TestModel` is registered with `SQLModel.metadata` before table creation
- [ ] 5.2 Write core CRUD unit tests (create, find, list_all, update)
      - `test_create_entity` — create returns entity with generated ID, persisted in DB
      - `test_find_entity_by_id` — find returns entity; find(non_existent_id) returns None
      - `test_list_all_entities` — list_all returns all with pagination metadata (total count)
      - `test_update_entity_fields` — update modifies fields, other fields unchanged
- [ ] 5.3 Write edge case repository tests
      - `test_update_nonexistent_entity` — update returns None for invalid ID
      - `test_soft_delete_entity` — soft_delete sets `deleted_at`; find excludes it; row still in DB
      - `test_soft_delete_on_non_soft_model` — soft_delete raises ValueError for models without SoftDeleteMixin
- [ ] 5.4 Write utility repository tests (count, exists, list_all with filters)
      - `test_count_entities` — count returns correct total (excluding soft-deleted)
      - `test_exists_entity` — exists returns True for existing, False for non-existent
      - `test_list_all_with_filters` — list_all(filters={...}) returns only matching entities
- [ ] 5.5 Create `backend/tests/integration/test_uow.py` — UnitOfWork atomicity tests
      - `test_uow_commit_success` — multiple creates inside UoW persist atomically
      - `test_uow_rollback_on_error` — exception inside UoW rolls back ALL changes
      - `test_uow_nested_operations` — mix of create/update inside UoW commits or rolls back as unit

## 6. Seed Integration Tests

- [ ] 6.1 Create `backend/tests/integration/test_seed.py` with seed execution fixture
      - `seed_data` fixture: runs seed logic against test DB session, returns session with seeded data
      - Import seed function (or inline raw SQL) to run within test transaction
- [ ] 6.2 Write seed execution and idempotency tests
      - `test_seed_executes_successfully` — seed runs without error
      - `test_seed_idempotent` — running seed twice produces identical row counts
- [ ] 6.3 Write seed data validation tests
      - `test_seed_admin_user_exists` — admin user exists with valid bcrypt password hash
      - `test_seed_all_roles_present` — all 4 roles exist (ADMIN, STOCK, PEDIDOS, CLIENT)
      - `test_seed_all_estados_present` — all 6 estados_pedido exist with correct `es_terminal` values
      - `test_seed_all_formas_pago_present` — all 3 formas_pago exist with `habilitado = true`
      - `test_seed_admin_has_admin_role` — admin user has ADMIN rol via usuarios_roles

## 7. Verification

- [ ] 7.1 Run `alembic upgrade head` and verify all 5 tables created correctly
      - Inspect schema: check PKs, FKs, constraints, column types match design
      - Verify `alembic history` shows 001_initial → 002_add_seed_models
      - Test `alembic downgrade 001_initial` and `alembic upgrade head` round-trip
- [ ] 7.2 Run seed script: `python -m app.db.seed` and verify output
      - Confirm success message with row counts
      - Verify admin password with a bcrypt verify check
      - Run seed twice to confirm idempotency
- [ ] 7.3 Run full test suite: `pytest tests/ -v`
      - All repository CRUD tests pass (create, find, list_all, update, soft_delete, count, exists)
      - All UoW integration tests pass (commit, rollback, nested)
      - All seed integration tests pass (execution, idempotency, data validation)
      - Existing tests (health, CORS, rate limiting) remain green
- [ ] 7.4 Create git commit with all changes
      - Stage: all new model files, seed script, migration, tests, modified __init__.py, env.py, conftest.py
      - Commit message: `feat: add seed data models, migration, seed script, and tests (CHANGE-00d)`

---

## Summary

| Section | Tasks | Description |
|---------|-------|-------------|
| 1. Database Metadata Fix | 2 | Update env.py and conftest.py to use SQLModel.metadata |
| 2. SQLModel Models | 6 | 5 domain models + __init__.py exports |
| 3. Alembic Migration | 1 | Handwritten migration for 5 tables |
| 4. Seed Script | 2 | db package init + async idempotent seed |
| 5. Repository & UoW Tests | 5 | TestModel fixture, 10 CRUD tests, 3 UoW tests |
| 6. Seed Integration Tests | 3 | Execution, idempotency, and data validation tests |
| 7. Verification | 4 | Migration, seed run, test suite, git commit |
| **Total** | **23** | |
