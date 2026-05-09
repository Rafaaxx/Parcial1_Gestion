# Archive Report: Change 01 — Auth JWT + RBAC

## Change Summary
- **Intent**: Implementar el flujo completo de autenticación (register, login, refresh, logout) con JWT de doble token + RBAC de 4 roles, cumpliendo RN-AU01 a RN-AU10 y RN-RB01 a RN-RB09.
- **Status**: **ARCHIVED** — PASS WITH WARNINGS
- **Archived Date**: 2026-05-08
- **Implementation Date**: 2026-05-08

## Artifacts
| Artifact | Path |
|----------|------|
| proposal | `openspec/changes/archive/2026-05-08-change-01-auth-jwt-rbac/proposal.md` |
| specs | `openspec/changes/archive/2026-05-08-change-01-auth-jwt-rbac/specs/auth-jwt-rbac.spec.md` |
| design | `openspec/changes/archive/2026-05-08-change-01-auth-jwt-rbac/design.md` |
| tasks | `openspec/changes/archive/2026-05-08-change-01-auth-jwt-rbac/tasks.md` |
| verify-report | `openspec/changes/archive/2026-05-08-change-01-auth-jwt-rbac/verify-report.md` |

## Source of Truth Updated
- `openspec/specs/auth-jwt-rbac/spec.md` — Created new spec domain from delta spec (auth-jwt-rbac.spec.md → auth-jwt-rbac/spec.md)

## What Was Built

### New Capabilities
1. **auth-jwt**: Flujo completo de autenticación JWT con register, login, refresh (con rotación), logout, y perfil propio. Incluye detección de replay attack (RN-AU05).
2. **rbac-authorization**: Dependencias `get_current_user` (401 si no autenticado) y `require_role` (403 si rol insuficiente).
3. **refresh-token-storage**: Modelo RefreshToken en BD con SHA-256 del UUID, revoked_at tracking, rotación atómica.
4. **security-utils**: Módulo `security.py` con bcrypt hashing (cost 12), JWT HS256, UUID v4 + SHA-256.

### Files Created (10 new files)
| File | Description |
|------|-------------|
| `backend/app/security.py` | bcrypt hashing, JWT HS256 create/decode, refresh token UUID/SHA-256 |
| `backend/app/modules/auth/schemas.py` | LoginRequest, RegisterRequest, TokenResponse, UserResponse |
| `backend/app/modules/auth/repository.py` | AuthRepository extends BaseRepository[Usuario] |
| `backend/app/modules/auth/service.py` | AuthService: register, login, refresh, logout, get_me |
| `backend/app/modules/auth/router.py` | 5 endpoints con rate limiting |
| `backend/app/modules/refreshtokens/model.py` | RefreshToken (TimestampMixin, no SoftDelete) |
| `backend/app/modules/refreshtokens/repository.py` | RefreshTokenRepository (custom, no BaseRepository) |
| `backend/app/modules/refreshtokens/service.py` | RefreshTokenService: create, validate_and_rotate, replay detection |
| `backend/migrations/versions/003_add_refresh_token.py` | refresh_tokens table with FK, unique hash, index |
| `backend/tests/unit/test_security.py` | 14 tests — hashing, JWT, refresh tokens |
| `backend/tests/unit/test_auth_service.py` | 14 tests — service layer with mocked UoW |
| `backend/tests/integration/test_auth_api.py` | 19 tests — full API integration |

### Files Modified (4 existing files)
| File | Description |
|------|-------------|
| `backend/app/dependencies.py` | Added get_current_user, require_role (JWT-based) |
| `backend/app/models/__init__.py` | Added RefreshToken import |
| `backend/app/models/usuario.py` | Added refresh_tokens relationship |
| `backend/app/main.py` | Registered auth_router |

## Test Results

| Suite | Tests | Status |
|-------|-------|--------|
| Unit — security (`test_security.py`) | 14/14 | ✅ ALL PASS |
| Unit — auth service (`test_auth_service.py`) | 14/14 | ✅ ALL PASS |
| Integration — auth API (`test_auth_api.py`) | 19/19 | ✅ ALL PASS |
| **Auth total** | **47/47** | **✅ ALL PASS** |

## Known Issues (Warnings — not blocking)

### 1. ADR-4/REQ-RBAC-07: `require_role` lee roles de BD en lugar de JWT claims
- **What**: `require_role` lee `current_user.usuario_roles` (de BD) en vez de extraer roles del payload JWT como especifica ADR-4.
- **Impact**: Funcionalmente correcto (el usuario se carga con roles por `get_current_user`). Performance sub-óptima si se optimiza `get_current_user` en el futuro para no cargar roles.
- **Recommended fix**: Extraer roles del payload decodificado del JWT en lugar de cargarlos de BD.

### 2. LOG-05: Rate limit excedido sin cobertura de tests
- **What**: Rate limiting se deshabilita en test config. El decorador `@limiter.limit()` está presente en el router pero no se verifica.
- **Impact**: El escenario 429 no tiene test de integración.

### 3. LOGOUT-02: Cobertura parcial
- **What**: Unit test prueba "Token inválido" (no existe) pero no "Token ya revocado". Integration test `test_logout_already_revoked` cubre el flujo ahora.
- **Note**: Desde la verificación inicial, se agregó `test_logout_already_revoked` en integración, mejorando la cobertura.

### 4. T-4.2: Falta `cascade="all, delete-orphan"` en relación refresh_tokens
- **Impact**: Bajo — la limpieza se maneja por FK cascade en BD.

### 5. Pre-existing: 8 tests rotos en `test_rate_limiter.py`
- **What**: 1 FAILED + 7 ERRORs en tests de rate limiter (slowapi v0.2.x API changes — no relacionados con Change 01).
- **Impact**: Rate limiter unit tests están rotos. Los 47 tests auth pasan sin problemas.

## Verification Summary
- **Tasks**: 17/17 completed ✅
- **Spec compliance**: 25/29 scenarios compliant, 3 partial, 1 untested
- **Architecture decisions**: 4/5 followed (ADR-4 desviado — ver Known Issues)
- **Design**: Feature-first modules, UoW pattern, stateless JWT, refresh rotation with replay detection
- **TDD**: Strict TDD mode — tests exist and pass for all production code
