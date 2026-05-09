# Tasks: Change 01 — Auth JWT + RBAC

> **Change**: `change-01-auth-jwt-rbac`
> **Generated**: 2026-05-08
> **Total Tasks**: 17 — 5 Infrastructure, 3 RefreshToken Module, 4 Auth Module, 3 Integration, 3 Tests

---

## Phase 1: Infrastructure

**Goal**: Crear los bloques fundamentales que el resto del sistema consume: utilidades de seguridad (hashing, JWT, refresh tokens) y la tabla en base de datos para almacenar refresh tokens.

---

### T-1.1: Create `app/security.py` — password hashing + JWT utils + refresh token generation

- **Files**: `backend/app/security.py` (CREATE)
- **Depends on**: None (module sin dependencias internas)
- **Acceptance**:
  - `hash_password(password)` retorna string bcrypt de 60 caracteres con cost≥12 (REQ-SEC-01, RN-AU01)
  - `verify_password(plain, hashed)` retorna `True` si coincide, `False` si no (REQ-SEC-02)
  - `create_access_token(data)` crea JWT HS256 con sub, email, roles, exp (30min), iat (REQ-SEC-03, RN-AU02)
  - `decode_access_token(token)` verifica firma + exp, retorna payload o lanza `jwt.PyJWTError` (REQ-SEC-04)
  - `generate_refresh_token()` retorna UUID v4 string (REQ-SEC-05, RN-AU03)
  - `hash_refresh_token(token)` retorna SHA-256 hex digest de 64 chars (REQ-SEC-06, RN-AU03)
  - Usa `settings.jwt_secret_key` y `settings.jwt_algorithm` de `config.py` (REQ-SEC-07)
- **Scenarios que cubre**: SEC-01, SEC-02, SEC-03, SEC-04, SEC-05
- **Effort**: Small (< 30 min)
- [x] T-1.1 implemented

---

### T-1.2: Create migration `003_add_refresh_token.py`

- **Files**: `backend/migrations/versions/003_add_refresh_token.py` (CREATE)
- **Depends on**: None (migración autónoma)
- **Acceptance**:
  - Crea tabla `refresh_tokens` con columnas: `id` (BIGSERIAL PK), `token_hash` (CHAR(64), UNIQUE, NOT NULL), `usuario_id` (BIGINT, FK → usuarios.id, ON DELETE CASCADE), `expires_at` (TIMESTAMPTZ, NOT NULL), `revoked_at` (TIMESTAMPTZ, NULL), `created_at` (TIMESTAMPTZ, server_default=func.now(), NOT NULL), `updated_at` (TIMESTAMPTZ, server_default=func.now(), NOT NULL)
  - Unique constraint `uq_refresh_token_hash` sobre `token_hash`
  - Index sobre `usuario_id`
  - Downgrade: dropea index + tabla sin errores
- **Effort**: Small (< 30 min)
- [x] T-1.2 implemented — migration created at `backend/migrations/versions/003_add_refresh_token.py`

---

## Phase 2: RefreshToken Module

**Goal**: Modelo, repositorio y servicio para la gestión de refresh tokens en BD. Este módulo NO hereda de `SoftDeleteMixin` porque usa `revoked_at` con semántica de revocación, no soft-delete.

---

### T-2.1: Create `modules/refreshtokens/` — model

- **Files**:
  - `backend/app/modules/__init__.py` (CREATE)
  - `backend/app/modules/auth/__init__.py` (CREATE)
  - `backend/app/modules/refreshtokens/__init__.py` (CREATE)
  - `backend/app/modules/refreshtokens/model.py` (CREATE)
- **Depends on**: T-1.2 (misma tabla)
- **Acceptance**:
  - `RefreshToken` hereda de `TimestampMixin` y `SQLModel` (NO de `BaseModel` ni `SoftDeleteMixin`)
  - `__tablename__ = "refresh_tokens"`
  - Columnas: `id` (Optional[int], PK auto), `token_hash` (str, max_length=64, unique), `usuario_id` (int, FK → usuarios.id), `expires_at` (datetime), `revoked_at` (Optional[datetime], default=None), `created_at`, `updated_at` (de TimestampMixin)
  - Relación `usuario: Usuario` con `back_populates="refresh_tokens"`
  - Helper property `is_expired()` que compara `expires_at` contra UTC now
  - Helper property `is_revoked()` que chequea `revoked_at is not None`
- **Effort**: Small (< 30 min)
- [x] T-2.1 implemented — RefreshToken model, module __init__ files created

---

### T-2.2: Create `modules/refreshtokens/repository.py`

- **Files**: `backend/app/modules/refreshtokens/repository.py` (CREATE)
- **Depends on**: T-2.1 (modelo RefreshToken)
- **Acceptance**:
  - `RefreshTokenRepository` NO hereda de `BaseRepository` (RefreshToken no tiene SoftDeleteMixin)
  - Constructor recibe `session: AsyncSession`
  - `async create(token: RefreshToken) -> RefreshToken`: agrega y hace flush
  - `async find_by_hash(token_hash: str) -> Optional[RefreshToken]`: busca por token_hash exacto, sin filtrar por deleted_at (crítico — consulta directa)
  - `async revoke(token_id: int) -> None`: setea `revoked_at = datetime.utcnow()` y hace flush
  - `async revoke_all_for_user(usuario_id: int) -> int`: revoca todos los refresh tokens activos (revoked_at IS NULL AND expires_at > now) de un usuario, retorna count de filas afectadas
- **Effort**: Small (30 min)
- [x] T-2.2 implemented — RefreshTokenRepository with find_by_hash, revoke, revoke_all_for_user

---

### T-2.3: Create `modules/refreshtokens/service.py`

- **Files**: `backend/app/modules/refreshtokens/service.py` (CREATE)
- **Depends on**: T-2.2 (repository), T-1.1 (security utils)
- **Acceptance**:
  - `RefreshTokenService` recibe `uow: UnitOfWork` en métodos (stateless service)
  - `async create_token(usuario_id: int) -> str`:
    - Genera UUID v4 via `generate_refresh_token()`
    - Calcula SHA-256 via `hash_refresh_token()`
    - Crea `RefreshToken` con `expires_at = utcnow + 7d`
    - Persiste vía repositorio
    - Retorna el UUID original (no el hash) para devolver al cliente
  - `async validate_and_rotate(token_uuid: str, usuario_id: int) -> str`:
    - Hashea con SHA-256
    - Busca por hash en BD
    - Si no existe → raise `UnauthorizedError` ("Token inválido")
    - Si existe y `is_expired()` → raise `UnauthorizedError` ("Token expirado")
    - Si existe y `is_revoked()` → **detección de replay**: llama a `revoke_all_for_user()` y raise `UnauthorizedError` ("Sesión comprometida — todos los tokens revocados") — REQ-REF-03, RN-AU05
    - Si válido → revoca el actual, crea y persiste nuevo token, retorna nuevo UUID
  - `async revoke_token(token_uuid: str) -> None`:
    - Busca por hash, si existe lo revoca
    - Si no existe o ya revocado → raise `UnauthorizedError`
- **Scenarios que cubre**: REF-01, REF-02, REF-03, REF-04
- **Effort**: Medium (30-60 min)
- [x] T-2.3 implemented — RefreshTokenService with create_token, validate_and_rotate, replay detection

---

## Phase 3: Auth Module

**Goal**: Schemas, repositorio, servicio y router de autenticación. Este es el módulo expuesto al mundo exterior.

---

### T-3.1: Create `modules/auth/schemas.py`

- **Files**: `backend/app/modules/auth/schemas.py` (CREATE)
- **Depends on**: None (schemas Pydantic puros)
- **Acceptance**:
  - `LoginRequest(BaseModel)`:
    - `email: EmailStr` (validación de email)
    - `password: str = Field(min_length=8)` (requerido, ≥8 chars, REQ-LOG-01, REQ-REG-03)
  - `RegisterRequest(BaseModel)`:
    - `nombre: str = Field(min_length=2, max_length=80)` (REQ-REG-04)
    - `apellido: str = Field(min_length=2, max_length=80)` (REQ-REG-04)
    - `email: EmailStr`
    - `password: str = Field(min_length=8)` (REQ-REG-03)
  - `TokenResponse(BaseModel)`:
    - `access_token: str`
    - `refresh_token: str`
    - `token_type: str = "bearer"`
    - `expires_in: int = 1800` (30 min en segundos)
  - `UserResponse(BaseModel)`:
    - `id: int, nombre: str, apellido: str, email: EmailStr, roles: list[str], activo: bool`
    - NUNCA incluye `password_hash` (REQ-ME-03)
- **Effort**: Small (< 30 min)
- [x] T-3.1 implemented — LoginRequest, RegisterRequest, TokenResponse, UserResponse schemas

---

### T-3.2: Create `modules/auth/repository.py`

- **Files**: `backend/app/modules/auth/repository.py` (CREATE)
- **Depends on**: Existing `Usuario` model + `BaseRepository[Usuario]`
- **Acceptance**:
  - `AuthRepository(BaseRepository[Usuario])` hereda `find()`, `create()`, `update()`, `list_all()`, etc. del genérico
  - `async find_by_email(email: str) -> Optional[Usuario]`: busca por email exacto (unicidad, RN-DA04)
  - `async create_with_roles(usuario: Usuario, roles: list[str], asignado_por_id: Optional[int] = None) -> Usuario`:
    - Crea el usuario vía `BaseRepository.create()`
    - Crea registros `UsuarioRol` para cada código de rol (REQ-REG-01, RN-AU07)
    - Usa `asignado_por_id` nulo (registro propio)
    - Todo en la misma sesión (misma transacción)
- **Effort**: Small (30 min)
- [x] T-3.2 implemented — AuthRepository extends BaseRepository[Usuario] with find_by_email, create_with_roles

---

### T-3.3: Create `modules/auth/service.py`

- **Files**: `backend/app/modules/auth/service.py` (CREATE)
- **Depends on**: T-3.2 (AuthRepository), T-2.3 (RefreshTokenService), T-1.1 (security utils), T-3.1 (schemas)
- **Acceptance**:

  **`async register(request: RegisterRequest, uow: UnitOfWork) -> dict`**:
  - Verifica que email no exista via `find_by_email()` → si existe, raise `ConflictError("El email ya está registrado")` (REQ-REG-02 → REG-02)
  - Hashea password con `hash_password()` con cost≥12 (REQ-REG-01 → REG-01, RN-AU01)
  - Valida password ≥8 chars, nombre/apellido 2-80 chars (validación Pydantic → 422 automático)
  - Crea usuario vía `create_with_roles()` con rol `["CLIENT"]` (RN-AU07)
  - Crea access token JWT con `create_access_token()` (sub=str(user.id), email, roles=["CLIENT"])
  - Crea refresh token vía `RefreshTokenService.create_token()`
  - Retorna dict con `TokenResponse` (REQ-REG-05 → REG-01)
  - **201 Created** (no 200)

  **`async login(request: LoginRequest, uow: UnitOfWork) -> dict`**:
  - Busca usuario por email via `find_by_email()` (REQ-LOG-01 → LOG-01)
  - Si no encuentra → raise `UnauthorizedError("Email o contraseña incorrectos")` (REQ-LOG-02, RN-AU08 → LOG-02)
  - Verifica password con `verify_password()` → si falla → mismo error genérico (LOG-03)
  - Si `not usuario.activo` → raise `UnauthorizedError("Cuenta deshabilitada")` (REQ-LOG-03 → LOG-04)
  - Construye `roles` list desde UsuarioRol (consulta activa o relacion cargada)
  - Crea access token JWT con sub=str(user.id), email, roles (REQ-LOG-05, RN-AU02)
  - Crea refresh token (REQ-LOG-06, RN-AU03)
  - Retorna dict con `TokenResponse`

  **`async refresh(refresh_token: str, uow: UnitOfWork) -> dict`**:
  - Delega a `RefreshTokenService.validate_and_rotate()` (REQ-REF-01)
  - Obtiene `usuario_id` del token rotado válido
  - Busca usuario fresco de BD
  - Crea nuevo access token JWT
  - Retorna dict con `TokenResponse`
  - Maneja: token expirado (REF-02), replay attack (REF-03), token inexistente (REF-04) → todas 401

  **`async logout(refresh_token: str, current_user: Usuario, uow: UnitOfWork) -> None`**:
  - Delega a `RefreshTokenService.revoke_token()` (REQ-LOGOUT-01 → LOGOUT-01)
  - Si token no existe o ya revocado → raise `UnauthorizedError` (REQ-LOGOUT-04 → LOGOUT-02)
  - Retorna None (→ 204 No Content, REQ-LOGOUT-02)

  **`async get_me(current_user: Usuario) -> dict`**:
  - Retorna `UserResponse` construido desde `current_user` (sin password_hash) (REQ-ME-01, REQ-ME-02, REQ-ME-03 → ME-01)

- **Scenarios que cubre**: REG-01, REG-02, REG-03, REG-04, LOG-01, LOG-02, LOG-03, LOG-04, REF-01, REF-02, REF-03, REF-04, LOGOUT-01, LOGOUT-02, ME-01
- **Effort**: Large (1-2 hr) — es el core del cambio
- [x] T-3.3 implemented — AuthService with register, login, refresh, logout, get_me

---

### T-3.4: Create `modules/auth/router.py`

- **Files**: `backend/app/modules/auth/router.py` (CREATE)
- **Depends on**: T-3.3 (AuthService), T-3.1 (schemas), T-4.1 (get_current_user/require_role)
- **Acceptance**:
  - `router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])`

  **`POST /register`**:
  - Input: `RegisterRequest` body
  - Output: 201 con `TokenResponse` (response_model)
  - Llama a `AuthService.register()` con uow inyectado
  - **Público** (sin autenticación)

  **`POST /login`**:
  - Input: `LoginRequest` body
  - Output: 200 con `TokenResponse`
  - Rate limit: `@limiter.limit(settings.rate_limit_auth_limit)` → "5/15minutes" (REQ-LOG-04, RN-AU06 → LOG-05)
  - **Público** (sin autenticación)

  **`POST /refresh`**:
  - Input: `RefreshRequest(BaseModel): refresh_token: str` body
  - Output: 200 con `TokenResponse`
  - Rate limit: `@limiter.limit(settings.rate_limit_refresh_limit)` → "10/1minute"
  - **Público** (el token mismo es la autenticación)

  **`POST /logout`**:
  - Input: `RefreshRequest` body + `Authorization: Bearer <token>`
  - Output: 204 No Content (sin body)
  - `Depends(get_current_user)` (REQ-LOGOUT-03 → LOGOUT-03)

  **`GET /me`**:
  - Output: 200 con `UserResponse`
  - `Depends(get_current_user)` (ME-02, ME-03)
  - Llama a `AuthService.get_me()`

  **Error handling**:
  - `AuthService` lanza `AppException` subclasses → manejadas por el handler global en `main.py`
  - RFC 7807 format: `{"detail": "...", "code": "...", "field": "..."}`

- **Effort**: Medium (30-60 min)
- [x] T-3.4 implemented — auth router with 5 endpoints (register, login, refresh, logout, me) + rate limiting

---

## Phase 4: Integration

**Goal**: Conectar los módulos nuevos con el resto del sistema: dependencias FastAPI, modelo Usuario, y registro del router.

---

### T-4.1: Update `app/dependencies.py` — add `get_current_user` + `require_role`

- **Files**: `backend/app/dependencies.py` (MODIFY)
- **Depends on**: T-1.1 (security.decode_access_token), existing `Usuario` model, existing `BaseRepository`
- **Acceptance**:

  **`async get_current_user(token: str = Depends(oauth2_scheme), uow: UnitOfWork = Depends(get_uow)) -> Usuario`**:
  - Extrae token de `Authorization: Bearer <token>` via `OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")` (REQ-RBAC-01)
  - Decodifica JWT con `decode_access_token()` (REQ-RBAC-02)
  - Extrae `sub` (user_id como string), lo convierte a int
  - Carga usuario de BD via `BaseRepository[Usuario].find(user_id)` (REQ-RBAC-03)
  - Si token faltante, inválido, expirado → HTTPException 401, code="UNAUTHORIZED" (REQ-RBAC-04 → RBAC-02, RBAC-03)
  - Si usuario no encontrado o `not usuario.activo` → HTTPException 401, code="UNAUTHORIZED"
  - Retorna instancia de `Usuario` (RBAC-01)

  **`def require_role(roles: list[str]) -> Callable`**:
  - Factory que retorna una dependency function
  - Lee los roles del JWT (no consulta BD) — REQ-RBAC-07
  - Valida que `usuario.roles` contenga al menos uno de los roles requeridos (OR lógico) — REQ-RBAC-06
  - Si no tiene ninguno → HTTPException 403, code="FORBIDDEN" (REQ-RBAC-05 → RBAC-05)
  - Si tiene rol suficiente → no lanza nada (RBAC-04)

  **Exports**:
  - `get_current_user`, `require_role` exportados en `dependencies.py` (REQ-RBAC-08)
  - `oauth2_scheme` instanciado como módulo-level para reuso

- **Effort**: Medium (30-60 min)
- [x] T-4.1 implemented — get_current_user() + require_role() factory added to dependencies.py

---

### T-4.2: Update `app/models/__init__.py` — add RefreshToken + Usuario.refresh_tokens relationship

- **Files**:
  - `backend/app/models/__init__.py` (MODIFY)
  - `backend/app/models/usuario.py` (MODIFY)
- **Depends on**: T-2.1 (RefreshToken model)
- **Acceptance**:
  - Models `__init__.py`:
    - Importa `RefreshToken` desde `app.modules.refreshtokens.model`
    - Agrega `"RefreshToken"` a `__all__`
  - `usuario.py`:
    - Agrega relación `refresh_tokens: list[RefreshToken]` con `back_populates="usuario"`, `cascade="all, delete-orphan"`
    - NO crea dependencia circular (import diferido o string)
- **Effort**: Small (< 15 min)
- [x] T-4.2 implemented — RefreshToken added to models __init__, refresh_tokens relationship added to Usuario

---

### T-4.3: Update `app/main.py` — register auth router

- **Files**: `backend/app/main.py` (MODIFY)
- **Depends on**: T-3.4 (auth router)
- **Acceptance**:
  - Importa `auth_router` desde `app.modules.auth.router`
  - Registra con `app.include_router(auth_router)`
- **Effort**: Small (< 10 min)
- [x] T-4.3 implemented — auth_router registered in main.py

---

## Phase 5: Tests

**Goal**: Validar que todo funciona correctamente en los tres niveles. TDD estricto: los tests existen y pasan antes de dar el cambio por terminado.

**Nota global**: Monkeypatch `hash_password` a cost=4 en `conftest.py` para evitar lentitud por bcrypt en tests. Ver diseño/testing-strategy.

---

### T-5.1: Create `tests/unit/test_security.py`

- **Files**: `backend/tests/unit/test_security.py` (CREATE)
- **Depends on**: T-1.1 (security.py implementado)
- **Acceptance**:

  **Hashing**:
  - `test_hash_password_returns_60_chars`: hash de password válido retorna string de 60 chars (SEC-01)
  - `test_verify_password_correct`: verify con password correcto retorna True (SEC-01)
  - `test_verify_password_incorrect`: verify con password incorrecto retorna False (SEC-02)
  - `test_hash_different_salts`: mismo password produce distintos hashes (salt automático)

  **JWT**:
  - `test_create_and_decode_token`: payload `{sub: "1", email: "a@b.com", roles: ["CLIENT"]}` → create → decode retorna payload original con exp e iat (SEC-03)
  - `test_decode_tampered_token`: modificar payload → JWTError (SEC-04)
  - `test_decode_expired_token`: JWT con exp en pasado → error por expiración (SEC-05)
  - `test_token_contains_required_claims`: access token contiene sub, email, roles, exp, iat

  **Refresh Token**:
  - `test_generate_refresh_token_returns_uuid_v4`: string UUID v4 válido
  - `test_hash_refresh_token_returns_64_chars`: SHA-256 hex digest de 64 chars
  - `test_hash_is_deterministic`: mismo UUID → mismo hash
  - `test_different_tokens_different_hashes`: distinto UUID → distinto hash

  **Monkeypatch**: Usar monkeypatch de pytest o fixture para setear bcrypt rounds a 4

- **Effort**: Medium (30-60 min)
- [x] T-5.1 implemented — security unit tests (hashing, JWT, refresh tokens) all passing

---

### T-5.2: Create `tests/unit/test_auth_service.py`

- **Files**: `backend/tests/unit/test_auth_service.py` (CREATE)
- **Depends on**: T-3.3 (AuthService), T-2.3 (RefreshTokenService), T-1.1 (security)
- **Acceptance**:

  **Mocks**: Mock `UnitOfWork`, `AuthRepository`, `RefreshTokenRepository`, `AsyncSession`.

  **Register**:
  - `test_register_success`: email no existente → crea usuario con rol CLIENT → retorna TokenResponse (REG-01)
  - `test_register_duplicate_email`: email existente → raise ConflictError (REG-02)
  - `test_register_password_too_short`: password < 8 chars → raise ValidationError via Pydantic (REG-03)

  **Login**:
  - `test_login_success`: credenciales válidas, activo=True → retorna TokenResponse (LOG-01)
  - `test_login_email_not_found`: email no registrado → raise UnauthorizedError con mensaje genérico (LOG-02)
  - `test_login_wrong_password`: password incorrecto → raise UnauthorizedError con mismo mensaje que email no encontrado (LOG-03)
  - `test_login_inactive_account`: activo=False → raise UnauthorizedError "Cuenta deshabilitada" (LOG-04)

  **Refresh**:
  - `test_refresh_success`: token válido → nuevo par, anterior revocado (REF-01)
  - `test_refresh_expired_token`: token expirado → raise UnauthorizedError (REF-02)
  - `test_refresh_replay_detection`: token ya revocado → revoca TODOS los tokens del usuario → raise UnauthorizedError (REF-03)
  - `test_refresh_token_not_found`: token no existe en BD → raise UnauthorizedError (REF-04)

  **Logout**:
  - `test_logout_success`: token válido → revocado en BD (LOGOUT-01)
  - `test_logout_token_not_found`: token no existe o ya revocado → raise UnauthorizedError (LOGOUT-02)

  **Get Me**:
  - `test_get_me_success`: usuario autenticado → retorna UserResponse sin password_hash (ME-01)

  **Mock injection**: Verificar que mock de `hash_password` se usa (cost bajo). Verificar llamadas al repositorio.

- **Effort**: Medium (30-60 min)
- [x] T-5.2 implemented — auth service unit tests with mocks all passing

---

### T-5.3: Create `tests/integration/test_auth_api.py`

- **Files**: `backend/tests/integration/test_auth_api.py` (CREATE)
- **Depends on**: T-4.3 (router registrado), T-4.1 (get_current_user implementado), T-3.4 (router endpoints)
- **Acceptance**:

  **Register**:
  - `test_register_full_flow`: POST `/api/v1/auth/register` con datos válidos → 201 + TokenResponse con access_token, refresh_token, token_type="bearer", expires_in=1800. Usuario existe en BD con rol CLIENT y password hasheado. (REG-01)
  - `test_register_duplicate_email`: registrar dos veces mismo email → 409, code="CONFLICT", detail="El email ya está registrado" (REG-02)
  - `test_register_weak_password`: password de 6 chars → 422, code="VALIDATION_ERROR" (REG-03)
  - `test_register_missing_fields`: body sin nombre → 422 con error de validación Pydantic (REG-04)

  **Login**:
  - `test_login_full_flow`: registrar → login con mismas credenciales → 200 + TokenResponse. Refresh token almacenado en BD con hash. (LOG-01)
  - `test_login_email_not_found`: login con email no registrado → 401, detail="Email o contraseña incorrectos" (LOG-02)
  - `test_login_wrong_password`: login con password incorrecto → 401, detail="Email o contraseña incorrectos" (LOG-03)
  - `test_login_inactive_account`: crear usuario → setear activo=False → login → 401, detail="Cuenta deshabilitada" (LOG-04)
  - `test_login_rate_limit`: 6 intentos fallidos seguidos → 429, code="RATE_LIMIT_EXCEEDED", header Retry-After presente (LOG-05) [requiere deshabilitar rate limit en test o usar monkeypatch]

  **Refresh**:
  - `test_refresh_rotation`: login → refresh con token → 200 + nuevo TokenResponse. Token anterior revocado en BD. (REF-01)
  - `test_refresh_expired_token`: forzar token expirado → 401, code="UNAUTHORIZED" (REF-02)
  - `test_refresh_replay_attack`: refresh con mismo token dos veces → segunda vez 401, TODOS los tokens del usuario revocados (REF-03)
  - `test_refresh_token_not_found`: refresh con token inexistente → 401, code="UNAUTHORIZED" (REF-04)

  **Logout**:
  - `test_logout_flow`: registrar → logout con refresh_token + Bearer → 204 No Content. Token revocado en BD. (LOGOUT-01)
  - `test_logout_no_auth`: logout sin Bearer token → 401 (LOGOUT-03)

  **Me**:
  - `test_me_authenticated`: registrar → usar access token para GET /me → 200 con UserResponse (ME-01)
  - `test_me_no_token`: GET /me sin Authorization → 401 (ME-02)
  - `test_me_expired_token`: GET /me con JWT expirado → 401 (ME-03)

  **RBAC via integration** (endpoint protegido con require_role en test):
  - `test_admin_role_passes`: crear endpoint de prueba protegido con `require_role(["ADMIN"])`, llamar con token ADMIN → 200 (RBAC-04)
  - `test_client_role_forbidden`: llamar mismo endpoint con token CLIENT → 403, code="FORBIDDEN" (RBAC-05)

  **Infra**:
  - SQLite in-memory con `async_sessionmaker` + `Base.metadata.create_all`
  - `httpx.AsyncClient` contra `app` con `dependency_overrides` para session
  - Monkeypatch bcrypt a cost=4 en fixture de sesión o conftest
  - Limpiar tablas entre tests (truncate o drop/create)

- **Effort**: Large (1-2 hr)
- [x] T-5.3 implemented — full integration auth API tests (register, login, refresh, logout, me, RBAC) all passing

---

## Summary

| Phase | Tasks | Effort Total |
|-------|-------|-------------|
| Phase 1: Infrastructure | 2 (T-1.1, T-1.2) | Small + Small |
| Phase 2: RefreshToken Module | 3 (T-2.1, T-2.2, T-2.3) | Small + Small + Medium |
| Phase 3: Auth Module | 4 (T-3.1, T-3.2, T-3.3, T-3.4) | Small + Small + Large + Medium |
| Phase 4: Integration | 3 (T-4.1, T-4.2, T-4.3) | Medium + Small + Small |
| Phase 5: Tests | 3 (T-5.1, T-5.2, T-5.3) | Medium + Medium + Large |
| **Total** | **17 tasks** | **~6-8 hr estimado** |

## Dependency Graph

```
T-1.1 ──→ T-2.3 ──→ T-3.3 ──→ T-3.4 ──→ T-4.3 ──→ T-5.3
           ↑         ↑         │         │
T-1.2 ──→ T-2.1 ──→ T-2.2 ──┘         │         │
                                        │         │
T-3.1 ──────────────────────────→ T-3.3 │         │
                                        │         │
T-3.2 ──────────────────────────→ T-3.3 │         │
                                        │         │
                              T-4.1 ←───┴──T-3.4   │
                                ↑                    │
                              T-1.1                  │
                                                     │
T-1.1 ──→ T-5.1                                      │
T-3.3 ──→ T-5.2                                      │
T-4.3 ──→ T-5.3 ←────────────────────────────────────┘
```

## Acceptance Criteria (global, from proposal)

- [x] `POST /api/v1/auth/register` crea usuario con rol CLIENT y devuelve tokens
- [x] `POST /api/v1/auth/login` devuelve access + refresh token
- [x] `POST /api/v1/auth/login` con credenciales inválidas devuelve 401
- [x] `POST /api/v1/auth/login` excede rate limit → 429
- [x] `POST /api/v1/auth/refresh` rota tokens y revoca el anterior
- [x] `POST /api/v1/auth/refresh` con token revocado → replay detection → todos los tokens del usuario revocados
- [x] `POST /api/v1/auth/logout` revoca refresh token
- [x] `GET /api/v1/auth/me` devuelve usuario autenticado
- [x] `GET /api/v1/auth/me` sin token devuelve 401
- [x] `require_role(["ADMIN"])` en endpoint devuelve 403 si el usuario es CLIENT
- [x] Migración 003 ejecuta `alembic upgrade head` sin errores
