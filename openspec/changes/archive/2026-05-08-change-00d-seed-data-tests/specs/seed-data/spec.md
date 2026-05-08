# Seed Data + Test Base Specification

## Purpose

Define the domain models required by Integrador.txt §3 (Rol, EstadoPedido, FormaPago, Usuario, UsuarioRol), the idempotent seed script that loads mandatory catalog data (Integrador.txt §10.2), the Alembic migration that creates these tables, and the base tests that prove the infrastructure patterns (BaseRepository[T], UnitOfWork) work correctly.

## ADDED Requirements

### Requirement: Domain models use SQLModel with consistent base class

The system SHALL define domain models inheriting from `SQLModel` (via the existing `TimestampMixin` / `BaseModel` mixins), and all models SHALL register with `SQLModel.metadata` so that Alembic and test table creation discover them consistently.

#### Scenario: Model metadata consistency

- **GIVEN** models inherit from `TimestampMixin(SQLModel)` or `BaseModel(TimestampMixin, SoftDeleteMixin)`
- **WHEN** Alembic runs `alembic upgrade head`
- **THEN** Alembic SHALL discover all models via `SQLModel.metadata` and apply the correct DDL
- **AND** test table creation SHALL use `SQLModel.metadata.create_all()` for consistency

---

### Requirement: Rol model — catalog of system roles

The system SHALL define a `Rol` model (table `roles`) with a semantic VARCHAR(20) primary key `codigo`, a `descripcion` VARCHAR(100), and timestamp columns from `TimestampMixin`.

#### Scenario: Rol table exists after migration

- **GIVEN** Alembic upgrade has been applied
- **WHEN** inspecting the database schema
- **THEN** a table `roles` exists with columns: `codigo` (VARCHAR(20) PK), `descripcion` (VARCHAR(100)), `created_at`, `updated_at`

#### Scenario: Rol has correct seed data

- **GIVEN** the seed script has been executed
- **WHEN** querying the `roles` table
- **THEN** exactly 4 rows exist: ADMIN, STOCK, PEDIDOS, CLIENT

---

### Requirement: EstadoPedido model — catalog of FSM states

The system SHALL define an `EstadoPedido` model (table `estados_pedido`) with a semantic VARCHAR(20) primary key `codigo`, `descripcion`, `orden` (INTEGER for FSM ordering), `es_terminal` (BOOLEAN default false), and timestamp columns.

#### Scenario: EstadoPedido table exists after migration

- **GIVEN** Alembic upgrade has been applied
- **WHEN** inspecting the database schema
- **THEN** a table `estados_pedido` exists with columns: `codigo` (VARCHAR(20) PK), `descripcion` (VARCHAR(100)), `orden` (INTEGER), `es_terminal` (BOOLEAN), `created_at`, `updated_at`

#### Scenario: EstadoPedido has correct seed data

- **GIVEN** the seed script has been executed
- **WHEN** querying the `estados_pedido` table
- **THEN** exactly 6 rows exist matching the FSM specification (PENDIENTE, CONFIRMADO, EN_PREP, EN_CAMINO, ENTREGADO, CANCELADO)
- **AND** `ENTREGADO` and `CANCELADO` have `es_terminal = true`
- **AND** all other states have `es_terminal = false`
- **AND** `orden` values are sequential (1 through 6)

---

### Requirement: FormaPago model — catalog of payment methods

The system SHALL define a `FormaPago` model (table `formas_pago`) with a semantic VARCHAR(20) primary key `codigo`, `descripcion`, `habilitado` (BOOLEAN default true), and timestamp columns.

#### Scenario: FormaPago table exists after migration

- **GIVEN** Alembic upgrade has been applied
- **WHEN** inspecting the database schema
- **THEN** a table `formas_pago` exists with columns: `codigo` (VARCHAR(20) PK), `descripcion` (VARCHAR(100)), `habilitado` (BOOLEAN), `created_at`, `updated_at`

#### Scenario: FormaPago has correct seed data

- **GIVEN** the seed script has been executed
- **WHEN** querying the `formas_pago` table
- **THEN** exactly 3 rows exist: MERCADOPAGO, EFECTIVO, TRANSFERENCIA
- **AND** all three have `habilitado = true`

---

### Requirement: Usuario model — user accounts with soft delete

The system SHALL define a `Usuario` model (table `usuarios`) with an autoincrement BIGINT primary key `id`, `email` (VARCHAR(254) UNIQUE NOT NULL), `password_hash` (CHAR(60) NOT NULL), `nombre` (VARCHAR(100)), `apellido` (VARCHAR(100)), optional `telefono` (VARCHAR(20)), `activo` (BOOLEAN default true), and columns from `BaseModel` (timestamps + soft delete).

#### Scenario: Usuario table exists after migration

- **GIVEN** Alembic upgrade has been applied
- **WHEN** inspecting the database schema
- **THEN** a table `usuarios` exists with columns: `id` (BIGSERIAL PK), `email` (VARCHAR(254) UNIQUE NOT NULL), `password_hash` (CHAR(60) NOT NULL), `nombre` (VARCHAR(100) NOT NULL), `apellido` (VARCHAR(100) NOT NULL), `telefono` (VARCHAR(20) nullable), `activo` (BOOLEAN), `created_at`, `updated_at`, `deleted_at`

#### Scenario: Admin user exists after seed

- **GIVEN** the seed script has been executed
- **WHEN** querying `usuarios` by email `admin@foodstore.com`
- **THEN** the user exists with `nombre = 'Admin'` and `apellido = 'User'`
- **AND** `password_hash` is a valid bcrypt hash (passlib, cost ≥ 12)
- **AND** the hash verifies against the password `Admin1234!`

---

### Requirement: UsuarioRol model — N:M pivot with composite PK

The system SHALL define a `UsuarioRol` model (table `usuarios_roles`) with a composite primary key (`usuario_id`, `rol_codigo`), foreign keys to `usuarios` and `roles`, an optional `asignado_por_id` FK to `usuarios`, and timestamp columns.

#### Scenario: UsuarioRol table exists after migration

- **GIVEN** Alembic upgrade has been applied
- **WHEN** inspecting the database schema
- **THEN** a table `usuarios_roles` exists with columns: `usuario_id` (BIGINT PK, FK → usuarios.id), `rol_codigo` (VARCHAR(20) PK, FK → roles.codigo), `asignado_por_id` (BIGINT, nullable, FK → usuarios.id), `created_at`, `updated_at`

#### Scenario: Admin user has ADMIN role after seed

- **GIVEN** the seed script has been executed
- **WHEN** querying `usuarios_roles` joined with `usuarios` where `email = 'admin@foodstore.com'`
- **THEN** a row exists with `rol_codigo = 'ADMIN'`

---

### Requirement: Seed script is idempotent

The system SHALL provide an idempotent seed script at `app/db/seed.py` invocable via `python -m app.db.seed`. Running the script multiple times SHALL produce the same database state without errors.

#### Scenario: First seed populates all tables

- **GIVEN** an empty database with Alembic migrations applied
- **WHEN** `python -m app.db.seed` is executed
- **THEN** the script completes without errors
- **AND** `roles` has 4 rows, `estados_pedido` has 6 rows, `formas_pago` has 3 rows, `usuarios` has 1 row, `usuarios_roles` has 1 row

#### Scenario: Second seed is a no-op

- **GIVEN** the database already has seed data from a previous run
- **WHEN** `python -m app.db.seed` is executed again
- **THEN** the script completes without errors
- **AND** all row counts remain identical to the first run

---

### Requirement: Admin password is configurable via environment variable

The system SHALL read the admin password from `SEED_ADMIN_PASSWORD` environment variable, falling back to `Admin1234!` if not set.

#### Scenario: Custom admin password

- **GIVEN** `SEED_ADMIN_PASSWORD` is set to a custom value
- **WHEN** the seed script is executed
- **THEN** the admin user's password hash verifies against the custom value

---

### Requirement: BaseRepository CRUD operations work correctly

The system SHALL provide unit tests proving that `BaseRepository[T]` supports: create, find by ID, list with pagination, update fields, soft delete, count, and exists check.

#### Scenario: Create and find entity

- **GIVEN** a test model (minimal SQLModel subclass) with no existing records
- **WHEN** creating an entity via `repository.create()`
- **THEN** the entity is returned with an assigned ID
- **AND** `repository.find(entity.id)` returns the entity

#### Scenario: List all entities with pagination

- **GIVEN** N test entities exist in the database
- **WHEN** calling `repository.list_all(skip=0, limit=10)`
- **THEN** the result contains all N entities and the total count is N

#### Scenario: Update entity fields

- **GIVEN** an existing entity with known field values
- **WHEN** updating a field via `repository.update(entity_id, {field: new_value})`
- **THEN** `repository.find(entity_id).field` equals `new_value`

#### Scenario: Soft delete entity

- **GIVEN** an existing entity that supports soft delete
- **WHEN** calling `repository.soft_delete(entity_id)`
- **THEN** `repository.find(entity_id)` returns `None` (excluded by default filter)
- **AND** the entity still exists with `deleted_at` set (not physically removed)

---

### Requirement: UnitOfWork atomicity is tested

The system SHALL provide tests proving that `UnitOfWork` commits on success and rolls back on failure.

#### Scenario: Successful commit

- **GIVEN** a UnitOfWork context
- **WHEN** multiple operations succeed inside the context
- **THEN** all changes are persisted after the context exits

#### Scenario: Automatic rollback on error

- **GIVEN** a UnitOfWork context
- **WHEN** an exception occurs inside the context
- **THEN** no changes are persisted (rollback)
