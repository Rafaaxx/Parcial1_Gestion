# Proposal: CHANGE-00d — Seed Data + Tests Base

## Intent

The app has infrastructure (FastAPI, UoW, BaseRepository, Alembic) but **zero models, zero seed data, and zero real migrations**. Without this change, no feature (auth, products, orders) can function — seed data is mandatory per Integrador.txt §10.2. We create the domain models, the idempotent seed script, the first real migration, and the base tests that prove the patterns work.

## Scope

### In Scope
1. **SQLModel entities** in `backend\app\models\`: Rol, EstadoPedido, FormaPago, Usuario, UsuarioRol
2. **Alembic migration** `002_add_seed_models.py` — creates all 5 tables with constraints, FK, PK semantics
3. **Seed script** `backend\app\db\seed.py` — idempotent (`INSERT ... ON CONFLICT DO NOTHING`), invoked via `python -m app.db.seed`
4. **Seed data**: 4 Roles, 6 EstadoPedido (with `es_terminal`), 3 FormaPago (habilitados), 1 admin user (bcrypt-hashed)
5. **Unit tests** for BaseRepository CRUD operations (create, find, list_all, update, soft_delete)
6. **Integration test** for seed script idempotency (running twice produces same state)

### Out of Scope
- Feature-specific endpoints (auth, products, orders — deferred to CHANGE-01+)
- Feature-specific repositories (RolRepository, etc. — BaseRepository[T] suffices for seed)
- Frontend changes
- Alembic autogenerate workflow (migration is handwritten)
- CI/CD pipeline

## Capabilities

### New Capabilities
- `backend-models`: SQLModel entity definitions (Rol, Usuario, EstadoPedido, FormaPago, UsuarioRol) with PK semantics, FK constraints, and mixin usage
- `seed-data`: Idempotent seed script (`python -m app.db.seed`) that loads mandatory catalog data
- `database-migrations`: Version-controlled Alembic migration creating the first real tables
- `backend-test-base`: Shared test fixtures (test models, seed-data assertions) and infrastructure tests for BaseRepository[T]

### Modified Capabilities
- None

## Approach

**Model creation order** (bottom-up, respecting FK dependencies):
1. `Rol` — PK is `codigo: str` (semantic), no FK deps
2. `EstadoPedido` — PK is `codigo: str`, `es_terminal: bool`
3. `FormaPago` — PK is `codigo: str`, `habilitado: bool`
4. `Usuario` — PK is `id: int` (autoincrement), `email: str` UQ, `password_hash: str`, extends `BaseModel` (timestamps + soft delete)
5. `UsuarioRol` — composite PK (`usuario_id`, `rol_codigo`), FK to Usuario and Rol

All models use `table=True`. Rol, EstadoPedido, FormaPago use `codigo` as PK (semantic). Usuario uses autoincrement `id` + `BaseModel` mixin. UsuarioRol is a pure pivot.

**Seed idempotency**: Use raw SQL `INSERT INTO ... ON CONFLICT (pk) DO NOTHING` via `conn.execute()` within an async context. Password hashing with passlib bcrypt (cost=12).

**Migration**: Handwritten `002_add_seed_models.py` referencing `sa.Table(...)` — one `op.create_table()` per entity, `op.create_foreign_key()` for UsuarioRol, `op.create_index()` for email UQ. Revises `001_initial`.

**Tests**: Use the existing SQLite `:memory:` conftest fixtures. Add a "test models" module with minimal SQLModel subclasses for test isolation. Unit tests for BaseRepository CRUD. Integration test runs seed twice and asserts row counts match.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `backend\app\models\rol.py` | New | SQLModel for Rol entity |
| `backend\app\models\estado_pedido.py` | New | SQLModel for EstadoPedido |
| `backend\app\models\forma_pago.py` | New | SQLModel for FormaPago |
| `backend\app\models\usuario.py` | New | SQLModel for Usuario (extends BaseModel) |
| `backend\app\models\usuario_rol.py` | New | SQLModel pivot UsuarioRol |
| `backend\app\models\__init__.py` | Modified | Export all new models |
| `backend\app\db\seed.py` | New | Idempotent seed script |
| `backend\app\db\__init__.py` | New | Package init |
| `backend\migrations\versions\002_add_seed_models.py` | New | Real migration creating 5 tables |
| `backend\tests\unit\test_repository.py` | New | Unit tests for BaseRepository CRUD |
| `backend\tests\integration\test_seed.py` | New | Integration test for seed idempotency |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Password hash mismatch in test assertions | Low | Test seed by login attempt (bcrypt verify) |
| Migration conflicts with placeholder 001 | Low | 002 explicitly revises `001_initial` |
| ON CONFLICT DO NOTHING syntax varies by DB | Low | We target PostgreSQL; SQLite `:memory:` tests use different syntax — handle in seed with dialect detection |

## Rollback Plan

1. Drop migration: `alembic downgrade 001_initial`
2. Delete seed data rows manually: `DELETE FROM usuario_rol; DELETE FROM usuario; DELETE FROM forma_pago; DELETE FROM estado_pedido; DELETE FROM rol;`
3. Or reset: `alembic downgrade base && alembic upgrade 002_add_seed_models`

## Dependencies

- **CHANGE-00a**: Infrastructure already in place (BaseRepository[T], UnitOfWork, Base model mixins, async engine, Alembic setup, conftest fixtures)

## Success Criteria

- [ ] `alembic upgrade head` creates all 5 tables with correct schema (PKs, FKs, constraints)
- [ ] `python -m app.db.seed` executes without error
- [ ] Running seed twice produces same data (idempotent — no duplicate errors)
- [ ] Admin user `admin@foodstore.com` can be verified (password hash matches `Admin1234!`)
- [ ] `pytest tests/unit/test_repository.py` — all CRUD tests pass
- [ ] `pytest tests/integration/test_seed.py` — seed idempotency test passes
- [ ] All 4 Rol records, 6 EstadoPedido records, 3 FormaPago records, 1 Usuario, 1 UsuarioRol present after seed
