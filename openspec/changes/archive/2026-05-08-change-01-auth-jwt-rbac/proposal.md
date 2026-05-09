# Proposal: Change 01 — Auth JWT + RBAC

## Intent

Implementar el flujo completo de autenticación (register, login, refresh, logout) con JWT de doble token + RBAC de 4 roles, cumpliendo las reglas de negocio RN-AU01 a RN-AU10 y RN-RB01 a RN-RB09 documentadas en `Historias_de_usuario.txt`. Esto desbloquea **todos** los endpoints protegidos del sistema.

## Scope

### In Scope
- `app/security.py`: hashing bcrypt (cost 12), creación/validación JWT HS256, generación de refresh tokens UUID v4
- `app/dependencies.py`: `get_current_user()` (extrae JWT, carga usuario de BD), `require_role(roles)` factory (valida contra JWT claims)
- `app/modules/auth/`: router + service + repository + schemas para register/login/refresh/logout/me
- `app/modules/refreshtokens/`: model + repository + service para RefreshToken en BD con SHA-256
- `app/models/__init__.py`: agregar RefreshToken, relación `refresh_tokens` en Usuario
- `backend/migrations/versions/003_add_refresh_token.py`: tabla `refresh_tokens`
- `app/main.py`: registrar `auth_router` con prefijo `/api/v1/auth`
- Tests: `test_security.py` (unit), `test_auth_service.py` (unit con mock UoW), `test_auth_api.py` (integration)

### Out of Scope
- Frontend auth (authStore, interceptors, etc.) — será Change 02
- CRUD de usuarios (admin) — será Change separado en módulo `usuarios/`
- Rate limiting de registro y creación de pedido — US-073 lo pide pero lo limitamos a login endpoint por ahora
- Invalidación de refresh tokens al cambiar contraseña — se hará en el módulo perfil
- Mecanismo de "último admin" (RN-RB04) — se cubre en el módulo usuarios/admin

## Capabilities

### New Capabilities
- `auth-jwt`: Flujo completo de autenticación JWT con register, login, refresh (con rotación), logout, y perfil propio. Incluye detección de replay attack (RN-AU05).
- `rbac-authorization`: Dependencias `get_current_user` (401 si no autenticado) y `require_role` (403 si rol insuficiente).
- `refresh-token-storage`: Modelo RefreshToken en BD con SHA-256 del UUID, revoked_at tracking, rotación atómica.

### Modified Capabilities
- None

## Approach

Arquitectura feature-first existente. Se crean dos módulos nuevos:

1. **`auth/`**: schemas Pydantic → repository (find_by_email, create_user sobre Usuario) → service (register, login, refresh, logout, get_me) → router (5 endpoints).
2. **`refreshtokens/`**: model (RefreshToken table) → repository (create, find_by_hash, revoke, revoke_all_for_user) → service (create_token, validate_and_rotate, detect_replay).

`security.py` es un módulo utilitario transversal (no feature) con funciones puras para hashing y JWT.

El service de `auth` importa y usa el service de `refreshtokens` para manejar los refresh tokens. El router de `auth` se registra en `main.py`.

**Flujo login**: valida credenciales → genera access token JWT (sub=user_id, email, roles) → genera refresh token UUID v4 → almacena hash SHA-256 en BD → devuelve TokenResponse.

**Flujo refresh**: recibe refresh token → busca por hash en BD → si revocado → detecta replay (revoca TODOS los tokens del usuario) → si válido → rota: revoca el anterior, emite nuevo par.

**RBAC**: `get_current_user` decodifica JWT, carga usuario fresco de BD (o 401). `require_role(["ADMIN"])` chequea roles del token JWT (no va a BD), 403 si falta.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `backend/app/security.py` | New | Hashing bcrypt, JWT create/decode, refresh gen |
| `backend/app/dependencies.py` | Modified | + get_current_user, + require_role factory |
| `backend/app/modules/auth/__init__.py` | New | Package init |
| `backend/app/modules/auth/schemas.py` | New | LoginRequest, RegisterRequest, TokenResponse, UserResponse |
| `backend/app/modules/auth/repository.py` | New | AuthRepository (find_by_email, create_user) |
| `backend/app/modules/auth/service.py` | New | register, login, refresh, logout, get_me |
| `backend/app/modules/auth/router.py` | New | 5 endpoints con rate limiting en login |
| `backend/app/modules/refreshtokens/__init__.py` | New | Package init |
| `backend/app/modules/refreshtokens/model.py` | New | RefreshToken SQLModel |
| `backend/app/modules/refreshtokens/repository.py` | New | RefreshTokenRepository |
| `backend/app/modules/refreshtokens/service.py` | New | create_token, validate_and_rotate, detect_replay |
| `backend/app/models/__init__.py` | Modified | + RefreshToken import, + refresh_tokens rel |
| `backend/app/main.py` | Modified | Register auth_router |
| `backend/migrations/versions/003_add_refresh_token.py` | New | Create refresh_tokens table |
| `backend/tests/unit/test_security.py` | New | Password hashing, JWT, refresh token unit tests |
| `backend/tests/unit/test_auth_service.py` | New | Service layer with mocked UoW |
| `backend/tests/integration/test_auth_api.py` | New | Full API integration tests |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| bcrypt cost 12 muy lento en tests | High | Monkeypatch a cost=4 en conftest |
| Replay attack detection puede falsar si el usuario hace refresh concurrente legítimo | Low | El UUID v4 + rotación hace muy improbable colisión; si ocurre, el usuario hace login de nuevo |
| SQLite en tests no soporta `TIMESTAMPTZ` igual que PostgreSQL | Medium | Usar `DateTime(timezone=True)` que SQLite sí soporta; mantener consistencia con `sa_type` |

## Rollback Plan

1. `alembic downgrade -1` para revertir migración 003
2. Eliminar `openspec/changes/change-01-auth-jwt-rbac/`
3. Remover registro de `auth_router` en `main.py`
4. Eliminar archivos de `modules/auth/` y `modules/refreshtokens/`
5. Revertir cambios en `dependencies.py` y `models/__init__.py`

## Dependencies

- Ninguna externa — passlib, python-jose, slowapi ya están en `requirements.txt`

## Success Criteria

- [ ] `POST /api/v1/auth/register` crea usuario con rol CLIENT y devuelve tokens (test verde)
- [ ] `POST /api/v1/auth/login` devuelve access + refresh token (test verde)
- [ ] `POST /api/v1/auth/login` con credenciales inválidas devuelve 401 (test verde)
- [ ] `POST /api/v1/auth/login` excede rate limit → 429 (test verde)
- [ ] `POST /api/v1/auth/refresh` rota tokens y revoca el anterior (test verde)
- [ ] `POST /api/v1/auth/refresh` con token revocado → replay detection → todos los tokens del usuario revocados (test verde)
- [ ] `POST /api/v1/auth/logout` revoca refresh token (test verde)
- [ ] `GET /api/v1/auth/me` devuelve usuario autenticado (test verde)
- [ ] `GET /api/v1/auth/me` sin token devuelve 401 (test verde)
- [ ] `require_role(["ADMIN"])` en endpoint devuelve 403 si el usuario es CLIENT (test verde)
- [ ] Migración 003 ejecuta `alembic upgrade head` sin errores
