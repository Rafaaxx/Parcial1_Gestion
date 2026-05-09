# SDD Init — Project Context

**Topic Key**: sdd-init/food-store
**Type**: architecture
**Project**: food-store
**Date**: 2026-05-08

## Tech Stack

### Backend
- **Runtime**: Python 3.11+
- **Framework**: FastAPI 0.111
- **ORM**: SQLModel 0.0.16 / SQLAlchemy 2.0.32
- **Database**: PostgreSQL 15+ via asyncpg 0.30
- **Migrations**: Alembic 1.13
- **Auth**: JWT (python-jose 3.3, PyJWT 2.8), bcrypt (passlib 1.7)
- **Payments**: MercadoPago SDK 2.3
- **Rate Limiting**: slowapi 0.1.9
- **Validation**: Pydantic 2.6 / Pydantic-Settings 2.1

### Frontend
- **Runtime**: Node 18+, TypeScript 5.3
- **Framework**: React 19 + Vite 5
- **Styling**: Tailwind CSS 3
- **State**: Zustand 4 (cart, auth, UI stores)
- **HTTP**: Axios 1.6
- **Build**: Vite + terser + PostCSS

### Testing (Backend)
- **Framework**: pytest 7.4 + pytest-asyncio 0.23
- **Integration**: httpx 0.26 (AsyncClient)
- **Database**: SQLite in-memory (via aiosqlite)
- **Coverage**: Not installed (pytest-cov missing)
- **Quality**: flake8, mypy, black, isort

### Testing (Frontend)
- **Frontend**: No test framework installed (no vitest/jest/playwright)
- **Linting**: ESLint 9, Prettier 3
- **Type Checking**: tsc --noEmit (via build script)

## Project Structure

```
food-store/
├── backend/
│   ├── app/
│   │   ├── models/          # SQLModel entities (mixins, usuario, rol, etc.)
│   │   ├── repositories/    # BaseRepository (generic CRUD)
│   │   ├── uow.py           # Unit of Work pattern
│   │   ├── dependencies.py  # FastAPI DI (get_uow, etc.)
│   │   ├── middleware/      # CORS, Rate Limiter
│   │   ├── config.py        # Pydantic Settings
│   │   ├── database.py      # Async engine + session factory
│   │   ├── exceptions.py    # Custom exceptions
│   │   ├── db/seed.py       # Idempotent seed data
│   │   └── main.py          # FastAPI app entrypoint
│   ├── migrations/          # Alembic versions (001_initial, 002_seed_models)
│   ├── tests/
│   │   ├── unit/            # Repository, UoW, Middleware tests
│   │   ├── integration/     # Seed data, CORS/Rate limiting, Health
│   │   ├── conftest.py      # Fixtures (SQLite in-memory, AsyncClient)
│   │   └── models.py        # Test models
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/             # App root
│   │   ├── config/          # Environment config
│   │   ├── features/        # Feature modules (auth, cart, ui)
│   │   ├── shared/          # Shared (hooks, http, ui, utils, store)
│   │   └── ...
│   └── package.json
├── docs/                    # Source of truth docs
│   ├── Integrador.txt       # Technical specification
│   ├── Descripcion.txt      # Project description
│   └── Historias_de_usuario.txt  # User stories
├── openspec/                # Existing SDD artifacts (legacy)
│   ├── config.yaml
│   ├── specs/               # Specs (seed-data, zustand-stores, ui-system, etc.)
│   └── changes/archive/     # Archived changes (00a-00d)
├── agents.md                # Agent instructions
└── README.md
```

## Architecture Patterns

1. **Feature-First Modular Backend**: organized by domain feature
2. **Feature-Sliced Frontend**: FSD-like structure with `@features`, `@shared`, `@entities`, `@pages`, `@app` aliases
3. **Unit of Work**: `UoW` class for transactional consistency (`backend/app/uow.py`)
4. **Repository Pattern**: `BaseRepository` with generic CRUD (`backend/app/repositories/base.py`)
5. **Service Layer**: Business logic in services (to be implemented)
6. **Soft Delete**: `SoftDeleteMixin` with `deleted_at` field
7. **Snapshot Pattern**: For order state tracking
8. **FSM (Finite State Machine)**: 6-state order lifecycle with append-only audit trail
9. **RBAC**: 4 roles (ADMIN, STOCK, PEDIDOS, CLIENT)

## Existing Conventions

- **Commits**: Conventional commits (feat, fix, refactor, test, docs)
- **API**: RESTful, OpenAPI at /docs and /redoc
- **Error Handling**: RFC 7807 problem details
- **Testing**: pytest with async auto-mode, SQLite in-memory for isolation
- **Seed Data**: Idempotent (INSERT ... ON CONFLICT DO NOTHING)
- **Config**: Pydantic Settings via .env

## Domains Pending Implementation (per docs)

US-001: Auth JWT + RBAC (login, register, refresh, logout)
US-002: Categorías (hierarchical catalog)
US-003: Productos (CRUD, stock, ingredientes)
US-004: Carrito (client-side with Zustand)
US-005: Pedidos (FSM, audit trail)
US-006: Pagos MercadoPago (checkout, webhooks IPN)
US-007: Admin panel (dashboard, metrics)
US-008: Direcciones de entrega
