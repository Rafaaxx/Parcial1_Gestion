## Verification Report: Change 01 — Auth JWT + RBAC

**Change**: change-01-auth-jwt-rbac
**Mode**: Strict TDD
**Date**: 2026-05-08

---

### Status: WARNING

### Executive Summary

Se verificaron 17/17 tareas completadas. Todos los tests auth pasan (14 unit security + 14 unit service + 18 integration = **46 tests auth verdes**). El diseño general es sólido y cumple con 4 de 5 ADRs. Se identificó una **desviación de diseño significativa**: `require_role` lee roles desde la BD (relación cargada) en lugar de desde los claims del JWT como especifica ADR-4 y REQ-RBAC-07. Hay 7 tests preexistentes rotos en `test_rate_limiter.py` (no relacionados con este cambio). Faltan 2 escenarios de spec sin cobertura: LOG-05 (rate limit) y LOGOUT-02 (token ya revocado en integración).

---

### Completeness

| Metric | Value |
|--------|-------|
| Tasks total | 17 |
| Tasks complete | 17 |
| Tasks incomplete | 0 |

All 17 tasks are marked [x] in `tasks.md`. No incomplete tasks.

---

### Test Results

| Metric | Value |
|--------|-------|
| Total tests | 93 collected |
| Passed | **85** |
| Failed | **1** (pre-existing, not related to change) |
| Errors | **7** (pre-existing, not related to change) |
| Auth tests (unit security) | **14/14 passed** ✅ |
| Auth tests (unit service) | **14/14 passed** ✅ |
| Auth tests (integration) | **18/18 passed** ✅ |
| Auth total | **46/46 passed** ✅ |

**Pre-existing failures** (all in `tests/unit/middleware/test_rate_limiter.py`, NOT part of Change 01):
- `test_rate_limiter_initialization` — FAILED: `Limiter` object has no attribute `key_func`
- 7 tests — ERROR at setup: slowapi `@limiter.limit` requires `request` argument on decorated function

**Skipped tests**: 0

---

### TDD Compliance

| Check | Result | Details |
|-------|--------|---------|
| TDD Evidence reported | ❌ Not found | No `apply-progress` artifact exists in `openspec/changes/` — TDD Cycle Evidence table not available for verification |
| All tasks have tests | ✅ Yes | All 17 production code tasks have corresponding test coverage |
| RED confirmed (tests exist) | ✅ Verified | All test files exist: `test_security.py`, `test_auth_service.py`, `test_auth_api.py` |
| GREEN confirmed (tests pass) | ✅ Verified | All 46 auth tests pass on execution |
| Triangulation adequate | ✅ Yes | Multiple scenarios have both unit AND integration tests |
| Safety Net for modified files | ⚠️ Cannot verify | No apply-progress artifact with Safety Net data |

**TDD Compliance**: 4/6 checks passed (2 not verifiable due to missing apply-progress artifact)

---

### Test Layer Distribution

| Layer | Tests | Files | Tools |
|-------|-------|-------|-------|
| Unit | 28 | 2 | pytest + unittest.mock |
| Integration | 18 | 1 | pytest + httpx.AsyncClient + SQLite in-memory |
| E2E | 0 | 0 | Not applicable |
| **Total (auth)** | **46** | **3** | |

---

### Spec Compliance Matrix

| Capability | Scenario | Test(s) | Result |
|------------|----------|---------|--------|
| **security-utils** | SEC-01: Hash y verify exitoso | `test_security.py::TestHashPassword::test_hash_password_returns_60_chars` + `test_verify_password_correct` | ✅ COMPLIANT |
| security-utils | SEC-02: Verify con password incorrecto | `test_security.py::TestVerifyPassword::test_verify_password_incorrect` | ✅ COMPLIANT |
| security-utils | SEC-03: JWT create y decode | `test_security.py::TestCreateDecodeAccessToken::test_create_and_decode_token` | ✅ COMPLIANT |
| security-utils | SEC-04: Token manipulado | `test_security.py::TestCreateDecodeAccessToken::test_decode_tampered_token` | ✅ COMPLIANT |
| security-utils | SEC-05: Token expirado | `test_security.py::TestCreateDecodeAccessToken::test_decode_expired_token` | ✅ COMPLIANT |
| **auth-register** | REG-01: Registro exitoso | `test_auth_service.py::TestRegister::test_register_success` + `test_auth_api.py::TestRegister::test_register_full_flow` | ✅ COMPLIANT |
| auth-register | REG-02: Email duplicado | `test_auth_service.py::TestRegister::test_register_duplicate_email` + `test_auth_api.py::TestRegister::test_register_duplicate_email` | ✅ COMPLIANT |
| auth-register | REG-03: Password débil | `test_auth_service.py::TestRegister::test_register_password_too_short_via_pydantic` + `test_auth_api.py::TestRegister::test_register_weak_password` | ✅ COMPLIANT |
| auth-register | REG-04: Campos faltantes | `test_auth_api.py::TestRegister::test_register_missing_fields` | ✅ COMPLIANT |
| **auth-login** | LOG-01: Login exitoso | `test_auth_service.py::TestLogin::test_login_success` + `test_auth_api.py::TestLogin::test_login_full_flow` | ✅ COMPLIANT |
| auth-login | LOG-02: Email inexistente | `test_auth_service.py::TestLogin::test_login_email_not_found` + `test_auth_api.py::TestLogin::test_login_email_not_found` | ✅ COMPLIANT |
| auth-login | LOG-03: Password incorrecto | `test_auth_service.py::TestLogin::test_login_wrong_password` + `test_auth_api.py::TestLogin::test_login_wrong_password` | ✅ COMPLIANT |
| auth-login | LOG-04: Cuenta deshabilitada | `test_auth_service.py::TestLogin::test_login_inactive_account` + `test_auth_api.py::TestLogin::test_login_inactive_account` | ✅ COMPLIANT |
| auth-login | LOG-05: Rate limit excedido | **No test found** — rate limiting is disabled in test config (`settings.rate_limit_enabled = False`) | ❌ UNTESTED |
| **auth-refresh** | REF-01: Refresh exitoso con rotación | `test_auth_service.py::TestRefresh::test_refresh_success` + `test_auth_api.py::TestRefresh::test_refresh_rotation` | ✅ COMPLIANT |
| auth-refresh | REF-02: Token expirado | `test_auth_service.py::TestRefresh::test_refresh_expired_token` | ✅ COMPLIANT (unit only) |
| auth-refresh | REF-03: Replay attack detectado | `test_auth_service.py::TestRefresh::test_refresh_replay_detection` + `test_auth_api.py::TestRefresh::test_refresh_replay_attack` | ✅ COMPLIANT |
| auth-refresh | REF-04: Token inexistente | `test_auth_service.py::TestRefresh::test_refresh_token_not_found` + `test_auth_api.py::TestRefresh::test_refresh_token_not_found` | ✅ COMPLIANT |
| **auth-logout** | LOGOUT-01: Logout exitoso | `test_auth_service.py::TestLogout::test_logout_success` + `test_auth_api.py::TestLogout::test_logout_flow` | ✅ COMPLIANT |
| auth-logout | LOGOUT-02: Token ya revocado | `test_auth_service.py::TestLogout::test_logout_token_not_found` | ⚠️ PARTIAL — unit test covers "not found" path, but the "already revoked" path has no dedicated integration test. The error message tested is "Token inválido" (not found), not "Token ya revocado" (already revoked) |
| auth-logout | LOGOUT-03: Sin autenticación | `test_auth_api.py::TestLogout::test_logout_no_auth` | ✅ COMPLIANT |
| **auth-me** | ME-01: Usuario autenticado | `test_auth_service.py::TestGetMe::test_get_me_success` + `test_auth_api.py::TestMe::test_me_authenticated` | ✅ COMPLIANT |
| auth-me | ME-02: Sin token | `test_auth_api.py::TestMe::test_me_no_token` | ✅ COMPLIANT |
| auth-me | ME-03: Token expirado | `test_auth_api.py::TestMe::test_me_expired_token` | ✅ COMPLIANT |
| **rbac-authorization** | RBAC-01: Token válido devuelve usuario | (no explicit test) | ⚠️ PARTIAL — covered indirectly by every authenticated test (e.g., `test_me_authenticated`), but no test isolates `get_current_user` behavior |
| rbac-authorization | RBAC-02: Token faltante | `test_auth_api.py::TestLogout::test_logout_no_auth` + `test_auth_api.py::TestMe::test_me_no_token` | ✅ COMPLIANT |
| rbac-authorization | RBAC-03: Token expirado | `test_auth_api.py::TestMe::test_me_expired_token` | ✅ COMPLIANT |
| rbac-authorization | RBAC-04: Rol suficiente pasa | `test_auth_api.py::TestRBAC::test_admin_role_passes` | ✅ COMPLIANT |
| rbac-authorization | RBAC-05: Rol insuficiente | `test_auth_api.py::TestRBAC::test_client_role_forbidden` | ✅ COMPLIANT |

**Compliance summary**: 25/29 scenarios compliant, 3 partial, 1 untested

---

### Correctness (Static — Structural Evidence)

| Requirement | Status | Notes |
|------------|--------|-------|
| REQ-REG-01: asignar rol CLIENT automáticamente | ✅ Implemented | `create_with_roles(roles=["CLIENT"])` en AuthService.register() |
| REQ-REG-02: verificar unicidad de email | ✅ Implemented | `find_by_email()` check en AuthService.register(), raise ConflictError |
| REQ-REG-03: rechazar password < 8 chars | ✅ Implemented | Pydantic `Field(min_length=8)` en RegisterRequest y LoginRequest |
| REQ-REG-04: rechazar nombre/apellido fuera de rango | ✅ Implemented | Pydantic `Field(min_length=2, max_length=80)` |
| REQ-REG-05: devolver 201 + TokenResponse | ✅ Implemented | Router devuelve `status_code=201` + `response_model=TokenResponse` |
| REQ-REG-06: devolver 409 si email duplicado | ✅ Implemented | ConflictError → handler global → 409 |
| REQ-LOG-01: 200 + TokenResponse | ✅ Implemented | Router + service devuelven TokenResponse |
| REQ-LOG-02: 401 genérico | ✅ Implemented | "Email o contraseña incorrectos" en ambos casos (email not found + wrong password) |
| REQ-LOG-03: 401 si activo=False | ✅ Implemented | `if not usuario.activo: raise UnauthorizedError("Cuenta deshabilitada")` |
| REQ-LOG-04: rate limit 5/15min | ✅ Implemented | `@limiter.limit(settings.rate_limit_auth_limit)` en router.login() |
| REQ-LOG-05: JWT con claims | ✅ Implemented | `create_access_token` con sub, email, roles, exp, iat |
| REQ-LOG-06: refresh UUIDv4 + SHA-256 | ✅ Implemented | `generate_refresh_token()` + `hash_refresh_token()` |
| REQ-REF-01: rotar tokens | ✅ Implemented | `validate_and_rotate()` en RefreshTokenService |
| REQ-REF-02: 401 si expirado | ✅ Implemented | `if stored.is_expired: raise UnauthorizedError("Token expirado")` |
| REQ-REF-03: detectar replay | ✅ Implemented | `if stored.is_revoked: revoke_all_for_user()` |
| REQ-REF-04: 401 si no existe | ✅ Implemented | `if stored is None: raise UnauthorizedError("Token inválido")` |
| REQ-REF-05: refresh expira 7d | ✅ Implemented | `timedelta(days=settings.refresh_token_expire_days)` — default 7 |
| REQ-LOGOUT-01: revocar refresh token | ✅ Implemented | `RefreshTokenService.revoke_token()` → `repo.revoke()` |
| REQ-LOGOUT-02: 204 No Content | ✅ Implemented | Router `status_code=204` |
| REQ-LOGOUT-03: requerir Bearer | ✅ Implemented | `Depends(get_current_user)` en logout endpoint |
| REQ-LOGOUT-04: 401 si no existe/revocado | ✅ Implemented | `RefreshTokenService.revoke_token()` raise UnauthorizedError |
| REQ-ME-01: 200 + UserResponse | ✅ Implemented | Router + `AuthService.get_me()` |
| REQ-ME-02: incluir campos requeridos | ✅ Implemented | `UserResponse` schema con id, nombre, apellido, email, roles, activo |
| REQ-ME-03: NUNCA password_hash | ✅ Implemented | `UserResponse` no tiene campo password_hash; `get_me()` no lo incluye |
| REQ-ME-04: 401 si falta token | ✅ Implemented | `get_current_user` raise 401 |
| REQ-RBAC-01: extraer Bearer token | ✅ Implemented | `OAuth2PasswordBearer` scheme |
| REQ-RBAC-02: decodificar JWT | ✅ Implemented | `decode_access_token()` en `get_current_user` |
| REQ-RBAC-03: cargar usuario fresco de BD | ✅ Implemented | `AuthRepository.find_with_roles()` en `get_current_user` |
| REQ-RBAC-04: 401 si inválido | ✅ Implemented | `get_current_user` raise HTTPException 401 |
| REQ-RBAC-05: 403 si rol insuficiente | ✅ Implemented | `require_role` raise HTTPException 403 |
| REQ-RBAC-06: lista de roles (OR) | ✅ Implemented | `user_roles.intersection(set(roles))` |
| REQ-RBAC-07: roles del JWT (no BD) | ❌ **NOT implemented** | Lee de `current_user.usuario_roles` (cargado de BD), NO del JWT |
| REQ-RBAC-08: exponer en dependencies.py | ✅ Implemented | `get_current_user` y `require_role` exportados en `dependencies.py` |
| REQ-SEC-01: bcrypt cost≥12 | ✅ Implemented | `passlib.hash.bcrypt.hash()` usa default rounds=12 |
| REQ-SEC-02: verify con bcrypt | ✅ Implemented | `bcrypt.verify()` |
| REQ-SEC-03: JWT HS256 con claims | ✅ Implemented | `jwt.encode()` con HS256, sub, email, roles, exp, iat |
| REQ-SEC-04: decodificar JWT | ✅ Implemented | `jwt.decode()` |
| REQ-SEC-05: UUID v4 | ✅ Implemented | `uuid.uuid4()` |
| REQ-SEC-06: SHA-256 | ✅ Implemented | `hashlib.sha256()` |
| REQ-SEC-07: SECRET_KEY de settings | ✅ Implemented | `settings.jwt_secret_key` |

---

### Coherence (Design)

| Decision | Followed? | Notes |
|----------|-----------|-------|
| ADR-1: RefreshToken sin BaseModel/SoftDeleteMixin | ✅ Yes | Hereda `TimestampMixin + SQLModel`, usa `revoked_at`. No tiene `deleted_at` |
| ADR-2: AuthRepository hereda BaseRepository[Usuario] | ✅ Yes | `AuthRepository(BaseRepository[Usuario])` con `find_by_email()` y `create_with_roles()` |
| ADR-3: RefreshTokenService separado de AuthService | ✅ Yes | Dos servicios independientes: `AuthService` y `RefreshTokenService`. AuthService inyecta RefreshTokenService |
| ADR-4: require_role lee roles del JWT, no BD | ❌ **No** | `require_role` lee roles de `current_user.usuario_roles` que viene de BD (cargado por `get_current_user` via `find_with_roles`). No extrae roles del payload del JWT. Ver detalle en Issues. |
| ADR-5: Login error genérico | ✅ Yes | "Email o contraseña incorrectos" para email no encontrado y password incorrecto por igual. "Cuenta deshabilitada" para cuenta inactiva (caso específico) |

#### Additional Design Notes

- **Design.md dice "Credenciales inválidas"** pero el código usa "Email o contraseña incorrectos" — la spec dice esto último, el código cumple la spec. El design.md quedó desactualizado en ese detalle.
- **T-4.2**: La relación `refresh_tokens` en `Usuario` no incluye `cascade="all, delete-orphan"` como especifica la tarea. El código tiene `back_populates="usuario"` pero sin cascade.
- **proposal.md linea 11**: "require_role(roles) factory (valida contra JWT claims)" — no coincide con la implementación actual.

---

### Files Verified

| Status | File | Notes |
|--------|------|-------|
| ✅ EXISTS | `backend/app/security.py` | Hashing, JWT, refresh token |
| ✅ EXISTS | `backend/app/dependencies.py` | get_current_user + require_role |
| ✅ EXISTS | `backend/app/modules/__init__.py` | Package init |
| ✅ EXISTS | `backend/app/modules/auth/__init__.py` | Package init |
| ✅ EXISTS | `backend/app/modules/auth/schemas.py` | LoginRequest, RegisterRequest, TokenResponse, UserResponse, RefreshRequest |
| ✅ EXISTS | `backend/app/modules/auth/repository.py` | AuthRepository extends BaseRepository[Usuario] |
| ✅ EXISTS | `backend/app/modules/auth/service.py` | AuthService: register, login, refresh, logout, get_me |
| ✅ EXISTS | `backend/app/modules/auth/router.py` | 5 endpoints with rate limiting |
| ✅ EXISTS | `backend/app/modules/refreshtokens/__init__.py` | Package init |
| ✅ EXISTS | `backend/app/modules/refreshtokens/model.py` | RefreshToken con TimestampMixin, sin SoftDeleteMixin |
| ✅ EXISTS | `backend/app/modules/refreshtokens/repository.py` | RefreshTokenRepository custom (no BaseRepository) |
| ✅ EXISTS | `backend/app/modules/refreshtokens/service.py` | RefreshTokenService: create, validate_and_rotate, revoke, replay detection |
| ✅ EXISTS (modified) | `backend/app/models/__init__.py` | Importa RefreshToken |
| ✅ EXISTS (modified) | `backend/app/models/usuario.py` | refresh_tokens relationship |
| ✅ EXISTS (modified) | `backend/app/main.py` | auth_router registrado |
| ✅ EXISTS | `backend/migrations/versions/003_add_refresh_token.py` | Migration with FK, unique, index |
| ✅ EXISTS | `backend/tests/unit/test_security.py` | 14 tests |
| ✅ EXISTS | `backend/tests/unit/test_auth_service.py` | 14 tests |
| ✅ EXISTS | `backend/tests/integration/test_auth_api.py` | 18 tests |

---

### Issues Found

#### CRITICAL (must fix before archive)

None.

#### WARNING (should fix)

1. **ADR-4/REQ-RBAC-07: `require_role` lee roles de BD en lugar de JWT claims**
   - **File**: `backend/app/dependencies.py:138`
   - **What**: `user_roles = {ur.rol_codigo for ur in (current_user.usuario_roles or [])}` lee roles del objeto Usuario cargado desde BD, no del JWT.
   - **Why**: El diseño (ADR-4) y la spec (REQ-RBAC-07) especifican explícitamente leer roles del JWT para evitar round-trip a BD. El código actual sí va a BD.
   - **Impact**: Funcionalmente correcto (el usuario se carga con roles por `get_current_user` de todas formas), pero la decisión de diseño no se respetó. Performance no óptima si `get_current_user` un día se optimiza para no cargar roles.
   - **Fix**: Extraer roles del payload decodificado del JWT en `get_current_user` y pasarlos a `require_role`, o decodificar el JWT nuevamente en `require_role`.

2. **LOG-05: Rate limit excedido — sin cobertura de tests**
   - **Scenarios**: LOG-05 requiere probar 429 con header Retry-After
   - **What**: Rate limiting se deshabilita en test config (`settings.rate_limit_enabled = False` + `limiter.enabled = False` en `conftest.py`)
   - **Impact**: El escenario de rate limit no tiene test de integración. El decorador `@limiter.limit()` está presente en el router, pero no se verifica su comportamiento.

3. **LOGOUT-02: Refresh token ya revocado — cobertura parcial**
   - **What**: El unit test `test_logout_token_not_found` prueba "Token inválido" (token no existe), pero no "Token ya revocado" (token existe pero ya revocado). No hay test de integración para LOGOUT-02.
   - **Impact**: El flujo de "ya revocado" en logout no se prueba directamente.

4. **T-4.2: Falta `cascade="all, delete-orphan"` en relación refresh_tokens**
   - **File**: `backend/app/models/usuario.py:22-24`
   - **What**: `refresh_tokens: List["RefreshToken"] = Relationship(back_populates="usuario")` no tiene `cascade="all, delete-orphan"` como especifica la tarea.
   - **Impact**: Bajo — la limpieza de refresh tokens al eliminar un usuario no es automática (se maneja por FK cascade en BD).

5. **Pre-existing: 8 tests rotos en `test_rate_limiter.py`**
   - **What**: 1 FAILED + 7 ERRORs en tests de rate limiter (no relacionados con Change 01)
   - **Root cause**: slowapi v0.2.x API changes — `@limiter.limit` requiere argumento `request` en la función decorada, y `Limiter.key_func` no existe.
   - **Impact**: Rate limiter unit tests están rotos. Los tests auth NO se ven afectados (todos pasan).

#### SUGGESTION (nice to have)

1. **bcrypt cost explícito**: `hash_password()` usa `bcrypt.hash(password)` sin especificar rounds. El default de passlib es 12, pero sería más explícito usar `bcrypt.using(rounds=12).hash(password)` o leer de settings.

2. **Test de integración para REF-02 (token expirado)**: El test `test_refresh_token_not_found` usa un UUID inexistente (cubre REF-04), pero el comentario dice "REF-02/REF-04". Sería bueno tener un test dedicado para REF-02 con un token que tenga `expires_at` en pasado.

3. **RBAC-01 sin test aislado**: No hay un test que aísle `get_current_user` devolviendo un usuario — se prueba indirectamente por todos los tests autenticados.

4. **Deprecation warnings**: `datetime.utcnow()` está deprecado en Python 3.13 — se usa en mixins, repositorio base, y varios lugares. Recomendación: migrar a `datetime.now(timezone.utc)`.

---

### Verdict

**PASS WITH WARNINGS**

El cambio está implementado correctamente en su mayoría. 46/46 tests auth pasan. La funcionalidad core (register, login, refresh con rotación, replay detection, logout, get_me, RBAC) funciona y está testeada. La desviación principal es **ADR-4 (require_role desde BD en vez de JWT)**, que aunque funcionalmente correcta, no respeta la decisión de diseño. Se recomienda corregir los WARNINGs antes de archivar, especialmente ADR-4.
