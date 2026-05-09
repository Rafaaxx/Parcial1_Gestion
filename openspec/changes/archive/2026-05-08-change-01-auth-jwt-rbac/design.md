# Design: Change 01 — Auth JWT + RBAC

## Technical Approach

Arquitectura feature-first existente con dos módulos nuevos (`auth/` y `refreshtokens/`) más un módulo transversal (`security.py`). Se extienden las dependencias FastAPI existentes (`get_current_user`, `require_role`). Todo opera sobre el patrón UoW existente sin modificarlo.

---

## Architecture Decisions

### Decision: RefreshToken NO hereda de BaseModel (ni SoftDeleteMixin)

**Choice**: SQLModel plano con `TimestampMixin` + campo `revoked_at` en lugar de `deleted_at`
**Rationale**: El modelo usa `revoked_at` como semántica de revocación (no soft-delete). El `BaseRepository` genérico asume `SoftDeleteMixin` para filtrar registros, pero RefreshToken no debe excluirse por `deleted_at`. Además, la tarea de limpieza de tokens vencidos es un job aparte, no soft-delete.
**Tradeoff**: No podemos usar `BaseRepository.find()` directamente porque filtraría por `deleted_at`. Solución: RefreshTokenRepository tiene su propio `find_by_hash()` que no aplica ese filtro.

### Decision: AuthRepository hereda de BaseRepository[Usuario]

**Choice**: Custom repository que extiende el genérico con `find_by_email()` + `create_with_roles()`
**Rationale**: `BaseRepository.create()` ya sirve para persistir el Usuario. Solo necesitamos agregar el lookup por email (único) y la creación atómica del registro UsuarioRol. Esto reusa el código existente sin duplicar CRUD.

### Decision: RefreshTokenService separado de AuthService

**Choice**: Servicio independiente en `modules/refreshtokens/service.py`
**Rationale**: Responsabilidad única. AuthService orquesta el flujo pero delega la lógica de refresh tokens al servicio especializado. AuthService no conoce detalles de hashing SHA-256 ni validación de replay.

### Decision: Roles en JWT claims, no en BD en `require_role`

**Choice**: `require_role` lee los roles del payload del JWT, no consulta la BD
**Rationale**: Rendimiento — evitar round-trip a BD en cada request protegido. Los roles cambian poco y el token expira en 30 min, la demora es aceptable como tradeoff de consistencia eventual.

### Decision: `LoginRequest` con mensaje genérico en errores

**Choice**: Siempre "Credenciales inválidas" sin distinguir email vs contraseña
**Rationale**: RN-AU08. Seguridad — no filtrar qué campo es incorrecto. Implementado en service, no en router.

---

## Data Flow

### Flow 1: POST /api/v1/auth/login

```
Client ──POST /auth/login──→ Router.login()
                                 │
                                 ▼
                            AuthService.login()
                                 │
                    ┌────────────┼────────────┐
                    ▼            ▼            ▼
              UsuarioRepo   verify_       RefreshToken
              .find_by_     password()    Service
              email()                     .create_token()
                    │            │            │
                    └────────────┴────────────┘
                                 │
                                 ▼
                     create_access_token()
                                 │
                                 ▼
                          TokenResponse
```

### Flow 2: POST /api/v1/auth/refresh (rotation + replay detection)

```
Client ──POST /auth/refresh──→ Router.refresh()
                                 │
                                 ▼
                            AuthService.refresh()
                                 │
                                 ▼
                         RefreshTokenService
                         .validate_and_rotate()
                                 │
                    ┌────────────┼────────────┐
                    ▼            │            ▼
              find_by_hash()     │      if revoked →
              (por SHA-256)     │      revoke_all_
                    │           │      for_user()
                    ▼           │            ▼
              verify not        │        raise 401
              expired +         │     ("Session
              not revoked       │     compromised")
                    │           │
                    └───────────┘
                                 │
                                 ▼
                        revoke_current()  ← marca revoked_at
                        create_new_token() ← nuevo par
                        create_access_token()
                                 │
                                 ▼
                          TokenResponse
```

### Flow 3: get_current_user() + require_role() Dependencies

```
Request with Authorization: Bearer <token>
                │
                ▼
      get_current_user Dependency
                │
                ▼
      decode_access_token()
      (verify signature + exp)
                │
          ┌─────┴─────┐
          │           │
       valid       invalid
          │           │
          ▼           ▼
    UsuarioRepo   raise 401
    .find(sub)    UnauthorizedError
          │
     ┌────┴────┐
     │         │
   found     None
     │         │
     ▼         ▼
  return     raise 401
  Usuario

Protected Route → require_role(["ADMIN"])
    │
    ▼
  get_current_user (runs first via Depends)
    │
    ▼
  Check if user.roles ∩ ["ADMIN"] ≠ ∅
    │
  ┌─┴──┐
  │    │
 yes   no
  │    │
  ▼    ▼
pass  raise 403
      ForbiddenError
```

---

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `backend/app/security.py` | Create | Hashing bcrypt (cost 12), JWT create/decode HS256, refresh token UUID v4 + SHA-256 |
| `backend/app/dependencies.py` | Modify | + `get_current_user()`, + `require_role(roles)` factory |
| `backend/app/modules/__init__.py` | Create | Package init |
| `backend/app/modules/auth/__init__.py` | Create | Package init |
| `backend/app/modules/auth/schemas.py` | Create | LoginRequest, RegisterRequest, TokenResponse, UserResponse |
| `backend/app/modules/auth/repository.py` | Create | AuthRepository — find_by_email, create_with_roles |
| `backend/app/modules/auth/service.py` | Create | register(), login(), refresh(), logout(), get_me() |
| `backend/app/modules/auth/router.py` | Create | 5 endpoints con rate limiting |
| `backend/app/modules/refreshtokens/__init__.py` | Create | Package init |
| `backend/app/modules/refreshtokens/model.py` | Create | RefreshToken SQLModel (sin SoftDeleteMixin) |
| `backend/app/modules/refreshtokens/repository.py` | Create | RefreshTokenRepository — find_by_hash, revoke, revoke_all_for_user |
| `backend/app/modules/refreshtokens/service.py` | Create | create_token, validate_and_rotate, detect_replay |
| `backend/app/models/__init__.py` | Modify | + RefreshToken import |
| `backend/app/main.py` | Modify | Register auth_router con prefijo `/api/v1/auth` |
| `backend/migrations/versions/003_add_refresh_token.py` | Create | RefreshToken table migration |
| `backend/tests/unit/test_security.py` | Create | Unit tests: hashing, JWT, refresh token gen |
| `backend/tests/unit/test_auth_service.py` | Create | Service layer with mocked UoW |
| `backend/tests/integration/test_auth_api.py` | Create | Full API integration tests |

---

## Interfaces / Contracts

### 1. security.py — pure functions

```python
def hash_password(password: str) -> str:
    """bcrypt con cost=12. Retorna string de 60 chars."""

def verify_password(plain: str, hashed: str) -> bool:
    """Verifica contra hash bcrypt. Retorna bool."""

def create_access_token(data: dict) -> str:
    """HS256, 30min exp.
    Payload: sub (str: user_id), email, roles (list[str]), exp, iat.
    """

def decode_access_token(token: str) -> dict:
    """Verifica firma + exp. Retorna payload dict o lanza jwt.PyJWTError."""

def generate_refresh_token() -> str:
    """UUID v4 como string."""

def hash_refresh_token(token: str) -> str:
    """SHA-256 hex digest (64 chars)."""
```

### 2. RefreshToken model

```python
class RefreshToken(TimestampMixin, SQLModel, table=True):
    __tablename__ = "refresh_tokens"
    id: int         # PK auto, BIGSERIAL
    token_hash: str # CHAR(64), UNIQUE, NOT NULL — SHA-256 hex
    usuario_id: int # FK → usuarios.id, NOT NULL
    expires_at: datetime  # TIMESTAMPTZ, NOT NULL — 7 days
    revoked_at: Optional[datetime]  # TIMESTAMPTZ, NULL = active
    created_at: datetime  # TIMESTAMPTZ, NOT NULL, default now
```

**Indexes**: UNIQUE on token_hash, INDEX on usuario_id

**NOTE**: NO hereda de `BaseModel` (no `SoftDeleteMixin`). Usa `TimestampMixin` directamente + `revoked_at`.

### 3. Auth schemas (Pydantic v2)

```python
class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)

class RegisterRequest(BaseModel):
    nombre: str = Field(min_length=2, max_length=80)
    apellido: str = Field(min_length=2, max_length=80)
    email: EmailStr
    password: str = Field(min_length=8)

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 1800  # 30 min en segundos

class UserResponse(BaseModel):
    id: int
    nombre: str
    apellido: str
    email: EmailStr
    roles: list[str]
    activo: bool
```

### 4. AuthRepository

```python
class AuthRepository(BaseRepository[Usuario]):
    async def find_by_email(self, email: str) -> Optional[Usuario]
    async def create_with_roles(
        self, usuario: Usuario, roles: list[str],
        asignado_por_id: Optional[int] = None
    ) -> Usuario
```

### 5. RefreshTokenRepository

```python
class RefreshTokenRepository:
    def __init__(self, session: AsyncSession)
    async def create(self, token: RefreshToken) -> RefreshToken
    async def find_by_hash(self, token_hash: str) -> Optional[RefreshToken]
    async def revoke(self, token_id: int) -> None
    async def revoke_all_for_user(self, usuario_id: int) -> int  # retorna count
```

### 6. Dependencies

```python
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    uow: UnitOfWork = Depends(get_uow)
) -> Usuario:
    """Decodifica JWT, carga usuario de BD. 401 si inválido/expirado."""

def require_role(roles: list[str]) -> Callable:
    """Factory que retorna dependency. Lee roles del token JWT (no BD).
    403 si el usuario no tiene ninguno de los roles especificados."""
```

### 7. Router Endpoints

```
POST   /api/v1/auth/register  201 → UserResponse        (público)
POST   /api/v1/auth/login     200 → TokenResponse        (rate limit 5/15min)
POST   /api/v1/auth/refresh   200 → TokenResponse        (rate limit 10/1min)
POST   /api/v1/auth/logout    204 → No Content           (requiere Bearer)
GET    /api/v1/auth/me        200 → UserResponse         (requiere Bearer)
```

---

## Testing Strategy

| Layer | What to Test | Approach |
|-------|-------------|----------|
| Unit — security | hash/verify_password, create/decode JWT, gen/hash refresh token | Funciones puras, sin BD |
| Unit — auth service | register, login, refresh (rotation), logout, get_me con mock UoW | Mock repos, verificar llamadas |
| Integration — auth API | Flujo completo register→login→refresh→me→logout | SQLite in-memory, AsyncClient, full stack |
| Integration — replay | Refresh con token revocado → todos los tokens del user revocados | SQLite in-memory, AsyncClient |

**bcrypt monkeypatch**: Monkeypatch `hash_password` a cost=4 en `conftest.py` para evitar lentitud en tests.

---

## Migration / Rollout

- Migración 003: `alembic revision --autogenerate -m "003_add_refresh_token"` o manual con SQLAlchemy `op.create_table()`
- Rollback: `alembic downgrade -1`

### Migration 003 — RefreshToken table

```python
def upgrade():
    op.create_table(
        "refresh_tokens",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("token_hash", sa.CHAR(length=64), nullable=False),
        sa.Column("usuario_id", sa.BigInteger(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token_hash", name="uq_refresh_token_hash"),
    )
    op.create_index(op.f("ix_refresh_tokens_usuario_id"), "refresh_tokens", ["usuario_id"])

def downgrade():
    op.drop_index(op.f("ix_refresh_tokens_usuario_id"), table_name="refresh_tokens")
    op.drop_table("refresh_tokens")
```

---

## Open Questions

- [ ] **Token blacklist**: ¿Necesitamos blacklist de access tokens o confiamos en exp natural? Decisión: stateless JWT, no hay blacklist. RN-AU02 lo cubre con 30 min de exp.
- [ ] **OAuth2 scheme**: FastAPI requiere `OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")` para Swagger UI. Confirmar que funciona con el prefijo `/api/v1`.
- [ ] **bcrypt cost en CI/CD**: Cost=12 puede ser lento en pipelines CI. Usar variable de entorno `BCRYPT_COST` con default 12, override 4 en tests.

---

## Design Created

**Change**: change-01-auth-jwt-rbac
**Location**: `openspec/changes/change-01-auth-jwt-rbac/design.md` + Engram `sdd/change-01-auth-jwt-rbac/design`

### Summary
- **Approach**: 2 nuevos módulos feature-first (auth, refreshtokens) + security.py transversal.
- **Key Decisions**: 5 decisions documentadas (RefreshToken sin soft-delete, AuthRepository hereda de BaseRepository, RefreshTokenService separado, roles en JWT para require_role, error genérico en login).
- **Files Affected**: 18 new files, 3 modified files, 1 new migration.
- **Testing Strategy**: Unit (security + service con mock) + Integration (full API stack con SQLite).

### Open Questions
- Blacklist de access tokens → No, stateless JWT.
- OAuth2PasswordBearer tokenUrl → Confirmar ruta.
- bcrypt cost variable → Usar env var con default 12, test override 4.

### Next Step
Ready for tasks (sdd-tasks).
