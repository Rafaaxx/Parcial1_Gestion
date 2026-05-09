# Testing Capabilities

**Topic Key**: sdd/food-store/testing-capabilities
**Type**: config
**Project**: food-store
**Date**: 2026-05-08

**Strict TDD Mode**: enabled
**Detected**: 2026-05-08

## Test Runner
- **Framework**: pytest
- **Command**: `pytest`
- **Config**: `backend/pytest.ini` (asyncio_mode = auto, testpaths = tests)

## Test Layers

| Layer | Available | Tool |
|-------|-----------|------|
| Unit | ✅ | pytest + pytest-asyncio |
| Integration | ✅ | pytest + httpx (AsyncClient) + SQLite in-memory |
| E2E | ❌ | Not installed |

## Coverage
- **Available**: ❌ (pytest-cov not installed)
- **Potential**: `pytest --cov=app tests/` after installing pytest-cov

## Quality Tools

| Tool | Available | Command |
|------|-----------|---------|
| Linter (Backend) | ✅ | `flake8` (or `ruff`) |
| Linter (Frontend) | ✅ | `eslint` |
| Type Checker (Backend) | ✅ | `mypy` |
| Type Checker (Frontend) | ✅ | `tsc --noEmit` (via `npm run build`) |
| Formatter (Backend) | ✅ | `black`, `isort` |
| Formatter (Frontend) | ✅ | `prettier` |

## Notes
- Integration tests use **SQLite in-memory** for fast, isolated execution
- No dedicated test database URL configured (all in-memory)
- Frontend lacks any test framework — vitest or jest should be added for frontend TDD
- pytest-cov coverage not yet installed; run `pip install pytest-cov` to enable
- Existing tests: 18 tests total (unit: repository, uow, middleware; integration: seed, health, cors-rate-limiting)
