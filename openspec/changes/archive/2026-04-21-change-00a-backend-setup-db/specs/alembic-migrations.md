## ADDED Requirements

### Requirement: Alembic manages database schema versions
The system SHALL use Alembic to track and apply database migrations, allowing reproducible schema changes and easy rollback.

#### Scenario: Initial migration is generated
- **WHEN** developer runs `alembic revision --autogenerate -m "initial schema"`
- **THEN** system creates a migration file in `migrations/versions/` with CREATE TABLE statements for all models

#### Scenario: Migration is applied to database
- **WHEN** developer (or CI/CD) runs `alembic upgrade head`
- **THEN** system applies all pending migrations in order and updates the alembic_version table

#### Scenario: Migration can be rolled back
- **WHEN** developer runs `alembic downgrade -1`
- **THEN** system reverts the last migration (DROP TABLE, etc.)

#### Scenario: Migration history is tracked
- **WHEN** developer runs `alembic current`
- **THEN** system displays the current schema version; running `alembic history` shows all applied migrations

---

### Requirement: Migrations are auto-generated from model changes
The system SHALL configure Alembic's autogenerate feature to detect model changes (new columns, new tables, renamed columns) and generate migration scripts.

#### Scenario: New column is detected
- **WHEN** a model adds a new column and `alembic revision --autogenerate` is run
- **THEN** system generates an ALTER TABLE ADD COLUMN statement

#### Scenario: New table is detected
- **WHEN** a new model is added and `alembic revision --autogenerate` is run
- **THEN** system generates a CREATE TABLE statement

---

### Requirement: Migrations can be manually edited for complex changes
The system SHALL allow developers to manually edit generated migration files for complex operations (data transformations, custom SQL).

#### Scenario: Migration file is editable
- **WHEN** a developer opens `migrations/versions/XXXX_*.py`
- **THEN** the file can be edited to add custom SQL or Python logic before running `alembic upgrade`

---

### Requirement: Database is initialized with Alembic on first deploy
The system SHALL support fresh database initialization via Alembic (no manual schema creation).

#### Scenario: Fresh database setup
- **WHEN** developer runs `alembic upgrade head` on a new database
- **THEN** system applies all migrations in order, resulting in a fully-formed schema

---
