# Tasks: CHANGE-05 — Direcciones de Entrega

## 1. Task Summary

| # | Task | Phase | Files | Effort | Status |
|---|------|-------|-------|--------|--------|
| [x] 1.1 | Create `DireccionEntrega` SQLModel | Infrastructure | `app/models/direccion_entrega.py` | 15 min | ✅ |
| [x] 1.2 | Add `direcciones` relationship to `Usuario` | Infrastructure | `app/models/usuario.py` | 5 min | ✅ |
| [x] 1.3 | Create Alembic migration for `direcciones_entrega` table | Infrastructure | `migrations/versions/007_add_direcciones_table.py` | 15 min | ✅ |
| [x] 1.4 | Export `DireccionEntrega` from models package | Infrastructure | `app/models/__init__.py` | 5 min | ✅ |
| [x] 2.1 | Create `DireccionRepository` with ownership + default methods | Data Access | `app/repositories/direccion_repository.py` | 20 min | ✅ |
| [x] 2.2 | Add `direcciones` property to `UnitOfWork` | Data Access | `app/uow.py` | 5 min | ✅ |
| [x] 3.1 | Create `direcciones` module package | Schemas | `app/modules/direcciones/__init__.py` | 2 min | ✅ |
| [x] 3.2 | Create Pydantic v2 schemas (Create, Update, Read, ListResponse) | Schemas | `app/modules/direcciones/schemas.py` | 15 min | ✅ |
| [x] 4.1 | Create `DireccionService` with business logic | Service | `app/modules/direcciones/service.py` | 30 min | ✅ |
| [x] 5.1 | Create router with 5 REST endpoints | API | `app/modules/direcciones/router.py` | 30 min | ✅ |
| [x] 6.1 | Register `router_direcciones` in app | Registration | `app/main.py` | 5 min | ✅ |
| [x] 7.1 | Create integration tests for all 5 endpoints | Testing | `backend/tests/test_direcciones.py` | 45 min | ✅ |
| | **Total** | | **13 files (8 new, 4 modified, 1 test)** | **~3 h** | **13/13 ✅** |

---

## 2. Detailed Tasks

### Phase 1: Infrastructure (Model + DB)

#### 1.1 — Create `DireccionEntrega` SQLModel

**Action**: Create SQLModel class extending `BaseModel` with `table=True`.

**File**: `backend/app/models/direccion_entrega.py`

**Spec**:
- `__tablename__ = "direcciones_entrega"`
- Inherits from `BaseModel` (→ `TimestampMixin` + `SoftDeleteMixin`)
- Columns:
  - `id: Optional[int] = Field(default=None, primary_key=True)`
  - `usuario_id: int = Field(foreign_key="usuarios.id", nullable=False)`
  - `alias: Optional[str] = Field(default=None, max_length=50)`
  - `linea1: str = Field(nullable=False, max_length=500)`
  - `es_principal: bool = Field(default=False, nullable=False)`
- Relationship back to `Usuario`:
  - `usuario: Optional["Usuario"] = Relationship(back_populates="direcciones")`
- Add `if TYPE_CHECKING` guard for `Usuario` forward reference

**Verification**:
```bash
# Python import works
python -c "from app.models.direccion_entrega import DireccionEntrega; print('OK')"
# Instantiate in-memory
python -c "from app.models.direccion_entrega import DireccionEntrega; d = DireccionEntrega(usuario_id=1, linea1='test'); print(d)"
```

---

#### 1.2 — Add `direcciones` relationship to `Usuario`

**Action**: Add `direcciones` relationship list to `Usuario` model for bidirectional ORM navigation.

**File**: `backend/app/models/usuario.py`

**Spec**:
```python
# Add import at top
from typing import Optional, TYPE_CHECKING, List

# Inside class Usuario, after existing relationships:
direcciones: List["DireccionEntrega"] = Relationship(
    back_populates="usuario",
    sa_relationship_kwargs={"cascade": "all, delete-orphan"},
)
```

Add `DireccionEntrega` to the `TYPE_CHECKING` import block.

**Verification**:
```bash
python -c "from app.models.usuario import Usuario; print(hasattr(Usuario, 'direcciones'))"
```

---

#### 1.3 — Create Alembic migration

**Action**: Create migration script `007_add_direcciones_table.py` following the pattern of `004_add_categorias_table.py`.

**File**: `backend/migrations/versions/007_add_direcciones_table.py`

**Spec**:
- `revision: str = "007_add_direcciones_table"`
- `down_revision: Union[str, None] = "006_add_ingredientes_table"`

**upgrade()**:
1. `op.create_table("direcciones_entrega", ...)`:
   - `sa.Column("id", sa.Integer(), autoincrement=True, nullable=False)`
   - `sa.Column("usuario_id", sa.Integer(), nullable=False)`
   - `sa.Column("alias", sa.String(50), nullable=True)`
   - `sa.Column("linea1", sa.String(500), nullable=False)`
   - `sa.Column("es_principal", sa.Boolean(), nullable=False, server_default=sa.text("false"))`
   - `sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False)`
   - `sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False)`
   - `sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True)`
   - `sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"], name="fk_direcciones_usuario", ondelete="CASCADE")`
   - `sa.PrimaryKeyConstraint("id")`
2. `op.create_index("idx_direcciones_usuario", "direcciones_entrega", ["usuario_id"])`
3. `op.execute("CREATE UNIQUE INDEX idx_direccion_principal_unico ON direcciones_entrega (usuario_id) WHERE es_principal = true AND deleted_at IS NULL")`
4. `op.execute("CREATE INDEX idx_direcciones_usuario_activas ON direcciones_entrega (usuario_id) WHERE deleted_at IS NULL")`

**downgrade()**:
1. `op.execute("DROP INDEX IF EXISTS idx_direccion_principal_unico")`
2. `op.execute("DROP INDEX IF EXISTS idx_direcciones_usuario_activas")`
3. `op.drop_index("idx_direcciones_usuario", table_name="direcciones_entrega")`
4. `op.drop_table("direcciones_entrega")`

**Verification**:
```bash
# Verify migration can be applied
cd backend && alembic upgrade head
# Verify rollback works
cd backend && alembic downgrade -1 && alembic upgrade head
```

---

#### 1.4 — Export `DireccionEntrega` from models package

**Action**: Add import and `__all__` entry for `DireccionEntrega`.

**File**: `backend/app/models/__init__.py`

**Spec**:
```python
# Add import (alphabetically after Categoria — but Categoria is not there, 
# put after auth-related imports or at end):
from app.models.direccion_entrega import DireccionEntrega

# Add to __all__ list:
__all__.append("DireccionEntrega")
# OR insert alphabetically between existing entries
```

**Verification**:
```bash
python -c "from app.models import DireccionEntrega; print('OK')"
```

---

### Phase 2: Data Access (Repository + UoW)

#### 2.1 — Create `DireccionRepository`

**Action**: Create repository extending `BaseRepository[DireccionEntrega]` with specialized query methods.

**File**: `backend/app/repositories/direccion_repository.py`

**Methods to implement** (all async):

| Method | SQL Equivalent | Returns |
|--------|---------------|---------|
| `find_by_usuario(usuario_id, skip, limit)` | `SELECT ... WHERE usuario_id=? AND deleted_at IS NULL ORDER BY created_at DESC OFFSET ? LIMIT ?` | `tuple[list[DireccionEntrega], int]` |
| `find_user_direccion(direccion_id, usuario_id)` | `SELECT ... WHERE id=? AND usuario_id=? AND deleted_at IS NULL` | `Optional[DireccionEntrega]` |
| `find_principal(usuario_id)` | `SELECT ... WHERE usuario_id=? AND es_principal=true AND deleted_at IS NULL` | `Optional[DireccionEntrega]` |
| `count_by_usuario(usuario_id)` | `SELECT COUNT(*) FROM ... WHERE usuario_id=? AND deleted_at IS NULL` | `int` |
| `unset_previous_default(usuario_id)` | `UPDATE ... SET es_principal=false WHERE usuario_id=? AND es_principal=true AND deleted_at IS NULL` | `None` |
| `set_es_principal(direccion_id, value)` | `UPDATE ... SET es_principal=? WHERE id=? AND deleted_at IS NULL` | `None` |
| `find_most_recent_active(usuario_id, exclude_id)` | `SELECT ... WHERE usuario_id=? AND deleted_at IS NULL AND id!=? ORDER BY created_at DESC LIMIT 1` | `Optional[DireccionEntrega]` |

**Implementation notes**:
- Use `session.execute()` with raw SQLAlchemy `select`/`update`/`func.count` for direct queries
- For `unset_previous_default` and `set_es_principal`, use `update()` statement with `execution_options(synchronize_session="evaluate")` or `session.execute(update(...))`
- Follow the pattern of `CategoriaRepository`: accept `session` in `__init__`, call `super().__init__(session, DireccionEntrega)`
- Import `DireccionEntrega` from `app.models.direccion_entrega`

**Verification**:
```bash
python -c "from app.repositories.direccion_repository import DireccionRepository; print('OK')"
```

---

#### 2.2 — Add `direcciones` property to `UnitOfWork`

**Action**: Add `DireccionRepository` import, private field, and lazy property to `UnitOfWork`.

**File**: `backend/app/uow.py`

**Spec**:
```python
# Import at top
from app.repositories.direccion_repository import DireccionRepository

# In __init__, add:
self._direcciones: Optional[DireccionRepository] = None

# New property:
@property
def direcciones(self) -> DireccionRepository:
    if self._direcciones is None:
        self._direcciones = DireccionRepository(self.session)
    return self._direcciones
```

**Verification**:
```bash
python -c "from app.uow import UnitOfWork; print(hasattr(UnitOfWork, 'direcciones')); print('OK')"
```

---

### Phase 3: Schemas

#### 3.1 — Create module package init

**Action**: Create empty `__init__.py` for the `direcciones` module.

**File**: `backend/app/modules/direcciones/__init__.py`

**Spec**: Empty file (same as `categorias/__init__.py`). Optional: add docstring.

**Verification**:
```bash
python -c "from app.modules import direcciones; print('OK')"
```

---

#### 3.2 — Create Pydantic v2 schemas

**Action**: Create schemas for request/response validation.

**File**: `backend/app/modules/direcciones/schemas.py`

**Spec** (exact from design Section 4.1):

| Schema | Fields | Config |
|--------|--------|--------|
| `DireccionBase` | `alias: Optional[str] = Field(None, max_length=50)`, `linea1: str = Field(..., max_length=500, min_length=1)` | — |
| `DireccionCreate(DireccionBase)` | Inherits all | — |
| `DireccionUpdate(BaseModel)` | `alias: Optional[str] = Field(None, max_length=50)`, `linea1: Optional[str] = Field(None, max_length=500, min_length=1)` | — |
| `DireccionRead(DireccionBase)` | + `id: int`, `usuario_id: int`, `es_principal: bool`, timestamps | `from_attributes = True` |
| `DireccionListResponse(BaseModel)` | `items: List[DireccionRead]`, `total: int`, `skip: int`, `limit: int` | — |

**Validation rules**:
- `alias`: max_length=50 (pre-validated by Pydantic)
- `linea1`: min_length=1, max_length=500 (pre-validated by Pydantic)
- Trim will happen in service layer (not in schema)
- `es_principal` NOT in Create/Update schemas (auto-assigned by service)
- `usuario_id` NOT sent by client (injected from JWT by service)

**Verification**:
```bash
python -c "from app.modules.direcciones.schemas import DireccionCreate, DireccionUpdate, DireccionRead, DireccionListResponse; print('OK')"
# Validate Create works
python -c "from app.modules.direcciones.schemas import DireccionCreate; c = DireccionCreate(linea1='test'); print(c); print('OK')"
# Validate Create rejects empty linea1
python -c "from app.modules.direcciones.schemas import DireccionCreate; import pydantic; c = DireccionCreate(linea1='')" 2>&1 | grep -q "validation_error" && echo "Rejected OK"
```

---

### Phase 4: Business Logic

#### 4.1 — Create `DireccionService`

**Action**: Create service class implementing all business logic for the 5 operations.

**File**: `backend/app/modules/direcciones/service.py`

**Class**: `DireccionService`
**Constructor**: `def __init__(self, uow: UnitOfWork)` (same pattern as `CategoriaService`)

**Methods**:

| Method | Logic | Exceptions |
|--------|-------|------------|
| `_trim_fields(data)` | Trim `alias` and `linea1` whitespace; if `alias` empty after trim → `None`; if `linea1` empty after trim → raise `ValidationError` | `ValidationError(422)` |
| `_validate_update_has_fields(data)` | `model_dump(exclude_none=True) == {}` → raise `ValidationError` | `ValidationError(422)` |
| `create_direccion(usuario_id, data)` → `DireccionRead` | 1. Trim fields; 2. Count user addresses; 3. If count==0 → `es_principal=True`; 4. Create repo obj → repo.create(); 5. Return `DireccionRead.model_validate(...)` | `ValidationError` |
| `list_direcciones(usuario_id, skip, limit)` → `DireccionListResponse` | Call `repo.find_by_usuario(...)` → return paginated response | — |
| `update_direccion(direccion_id, usuario_id, data)` → `DireccionRead` | 1. Trim; 2. Validate has fields; 3. `find_user_direccion` → 404 if None; 4. `repo.update(id, filtered_data)` → 404 if None; 5. Return `DireccionRead` | `NotFoundError(404)`, `ValidationError(422)` |
| `delete_direccion(direccion_id, usuario_id)` → `None` | 1. `find_user_direccion` → 404 if None; 2. If `es_principal`: `find_most_recent_active` → if found, `set_es_principal(most_recent, True)`; 3. `repo.soft_delete(id)` | `NotFoundError(404)` |
| `set_predeterminada(direccion_id, usuario_id)` → `DireccionRead` | 1. `find_user_direccion` → 404 if None; 2. If already `es_principal` → return (idempotent); 3. `repo.unset_previous_default(user_id)`; 4. `repo.set_es_principal(id, True)`; 5. `repo.find(id)` → return `DireccionRead` | `NotFoundError(404)`, `ConflictError(409)` (from `IntegrityError`) |

**Error handling**:
- Import `AppException`, `ValidationError`, `NotFoundError`, `ConflictError` from `app.exceptions`
- Import `IntegrityError` from `sqlalchemy.exc` for catching DB unique constraint violations in `set_predeterminada`

**Edge cases** (from spec):
- `alias` after trim empty → treat as `None` (EC-04)
- `linea1` after trim empty → raise `ValidationError(422)` (EC-05)
- Empty body `{}` → raise `ValidationError(422)` — "No hay campos para actualizar" (EC-10)
- Delete principal with other addresses → reassign to most recent (REQ-DI-26)
- Delete only address → allow it, no reassignment needed (EC-03)
- PATCH idempotent: if already default → return 200 without changes (REQ-DI-30)

**Verification**:
```bash
python -c "from app.modules.direcciones.service import DireccionService; print('OK')"
```

---

### Phase 5: API Endpoints

#### 5.1 — Create router with 5 REST endpoints

**Action**: Create FastAPI router with 5 endpoints following the pattern of `categorias/router.py`.

**File**: `backend/app/modules/direcciones/router.py`

**Router**: `router = APIRouter(prefix="/api/v1/direcciones", tags=["direcciones"])`

**Dependencies per endpoint**:
- `uow: UnitOfWork = Depends(get_uow)`
- `_: None = Depends(require_role(["CLIENT", "ADMIN"]))`
- `current_user: Usuario = Depends(get_current_user)`

**Endpoints**:

| Method | Path | Status | Response | Description |
|--------|------|--------|----------|-------------|
| POST | `/` | 201 | `DireccionRead` | Create address (first = default) |
| GET | `/` | 200 | `DireccionListResponse` | List own addresses (skip, limit) |
| PUT | `/{direccion_id}` | 200 | `DireccionRead` | Update own address |
| DELETE | `/{direccion_id}` | 204 | None | Soft delete own address |
| PATCH | `/{direccion_id}/predeterminada` | 200 | `DireccionRead` | Set as default |

**Error handling per endpoint** (categorias pattern):

```python
try:
    service = DireccionService(uow)
    result = await service.method(...)
    await uow.commit()
    return result
except AppException as e:
    raise HTTPException(status_code=e.status_code, detail=e.message)
except IntegrityError:
    await uow.rollback()
    raise HTTPException(status_code=409, detail="Ya existe una dirección predeterminada")
except Exception as e:
    await uow.rollback()
    logger.error(...)
    raise HTTPException(status_code=500, detail="Error interno del servidor")
```

**Note**: PATCH endpoint needs EXTRA handling for `IntegrityError` (unique partial index violation). Use `from sqlalchemy.exc import IntegrityError`.

**Imports needed**:
```python
from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.modules.direcciones.schemas import (
    DireccionCreate, DireccionUpdate, DireccionRead, DireccionListResponse,
)
from app.modules.direcciones.service import DireccionService
from app.uow import UnitOfWork
from app.dependencies import get_uow, require_role, get_current_user
from app.exceptions import AppException, ConflictError
from sqlalchemy.exc import IntegrityError
import logging
```

**Verification**:
```bash
python -c "from app.modules.direcciones.router import router; print('OK'); print(f'{len(router.routes)} routes')"
# Should print at least 5 routes
```

---

### Phase 6: App Registration

#### 6.1 — Register `router_direcciones` in main.py

**Action**: Add import and `app.include_router()` call.

**File**: `backend/app/main.py`

**Spec**:
```python
# Add import at top (grouped with other module imports):
from app.modules.direcciones.router import router as router_direcciones

# Add include_router after existing routers:
app.include_router(router_direcciones)
```

Place after `app.include_router(ingredientes_router)` line.

**Verification**:
```bash
python -c "from app.main import app; print('OK'); routes = [r.path for r in app.routes if '/api/v1/direcciones' in r.path]; print(f'Direcciones routes: {routes}')"
```

---

### Phase 7: Testing

#### 7.1 — Create integration tests [x]

**Action**: Create comprehensive test file covering all 5 endpoints, edge cases, and business rules.

**File**: `backend/tests/test_direcciones.py`

**Test structure** (follow `test_ingredientes.py` pattern but with proper fixtures for auth):

**Fixtures needed**:

```python
@pytest_asyncio.fixture
async def test_db():
    """Create in-memory SQLite test DB with all tables"""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield engine
    await engine.dispose()

@pytest_asyncio.fixture
async def test_session(test_db):
    """Test session"""
    async with AsyncSession(test_db, expire_on_commit=False) as session:
        yield session

@pytest_asyncio.fixture
def test_uow(test_session):
    return UnitOfWork(test_session)

@pytest_asyncio.fixture
async def usuario_cliente(test_session):
    """Create a CLIENT user for testing"""
    from app.models.usuario import Usuario
    user = Usuario(email="cliente@test.com", password_hash="hash", nombre="Test", apellido="User", activo=True)
    test_session.add(user)
    await test_session.flush()
    # Could add role assignment here if needed
    return user

@pytest_asyncio.fixture
async def direccion_data():
    return DireccionCreate(linea1="Av. Siempre Viva 123, CABA", alias="Casa")

@pytest_asyncio.fixture
def override_get_uow(test_uow):
    """Override get_uow dependency"""
    ...  # same pattern as test_ingredientes
```

**Auth mocking**:
- Since tests use `require_role` + `get_current_user`, you need to mock these dependencies
- Option A: Override `get_current_user` to return a test user
- Option B: Override `require_role` to be a no-op
- Recommended: Override both in `client` fixture, similar to how `get_uow` is overridden

**Test scenarios** (grouped by US):

**US-024: Crear dirección** (6 tests)
- `test_create_success_without_alias` — POST básico, verifica 201 + `es_principal=true`
- `test_create_success_with_alias` — POST con alias, verifica 201 + alias correcto
- `test_create_second_address_not_principal` — Crear 2da dirección, verifica `es_principal=false`
- `test_create_linea1_empty` — POST `linea1=""` → 422
- `test_create_alias_too_long` — POST alias>50 → 422
- `test_create_no_auth` — POST sin token → 401

**US-025: Listar direcciones** (5 tests)
- `test_list_own_addresses` — GET normal, verifica items propios
- `test_list_empty` — GET sin direcciones → items=[]
- `test_list_pagination` — GET `?skip=0&limit=5`, verifica slicing
- `test_list_excludes_soft_deleted` — DELETE una, GET verifica excluida
- `test_list_other_user_not_included` — Usuario A ve solo A's

**US-026: Editar dirección** (6 tests)
- `test_update_alias_and_linea1` — PUT ambos campos → 200
- `test_update_only_alias` — PUT parcial → 200, alias cambia
- `test_update_not_owned` — PUT dirección ajena → 404
- `test_update_not_found` — PUT id inexistente → 404
- `test_update_soft_deleted` — PUT sobre deleted → 404
- `test_update_empty_body` — PUT `{}` → 422

**US-027: Eliminar dirección** (5 tests)
- `test_soft_delete_success` — DELETE normal → 204, `deleted_at` seteado
- `test_delete_not_owned` — DELETE dirección ajena → 404
- `test_delete_already_deleted` — DELETE sobre deleted → 404
- `test_delete_principal_reassigns_default` — DELETE predeterminada con otras → otra se vuelve predeterminada
- `test_delete_only_address` — DELETE única dirección → 204, usuario sin direcciones

**US-028: Establecer predeterminada** (5 tests)
- `test_set_predeterminada_success` — PATCH → 200, flags switched
- `test_set_predeterminada_idempotent` — PATCH ya predeterminada → 200, sin cambios
- `test_set_predeterminada_not_owned` — PATCH ajena → 404
- `test_set_predeterminada_soft_deleted` — PATCH sobre deleted → 404
- `test_set_predeterminada_atomicity` — Verifica atomicidad (concurrente opcional)

**Total: ~27 test functions**

**Note**: Use `@pytest.mark.asyncio` on all test functions.

**Verification**:
```bash
cd backend && pytest tests/test_direcciones.py -v --asyncio-mode=auto
# All tests should pass (green)
```

---

## 3. Dependency Graph

```
1.1 (Model)
 ├── 1.2 (Usuario relationship)     — depends on 1.1 (needs DireccionEntrega class)
 ├── 1.3 (Migration)                — depends on 1.1 (needs model definition)
 └── 1.4 (models/__init__.py)       — depends on 1.1 (needs import target)

2.1 (Repository)                     — depends on 1.1 (model reference)
 └── 2.2 (UoW property)             — depends on 2.1 (imports DireccionRepository)

3.1 (Module __init__)                — independent
 └── 3.2 (Schemas)                  — depends on 3.1 (package must exist)

4.1 (Service)                        — depends on 2.2 (UoW access), 3.2 (schemas)

5.1 (Router)                         — depends on 3.2 (schemas), 4.1 (service), 2.2 (UoW)

6.1 (main.py registration)          — depends on 5.1 (router must exist)

7.1 (Tests)                          — depends on 6.1 (full app wired)
```

**Parallel batches**:
- **Batch A** (fully parallel): 1.1, 3.1
- **Batch B** (after 1.1): 1.2, 1.3, 1.4, 2.1
- **Batch C** (after 2.1 + 3.1): 2.2, 3.2
- **Batch D** (after 2.2 + 3.2): 4.1
- **Batch E** (after 4.1): 5.1
- **Batch F** (after 5.1): 6.1
- **Batch G** (after 6.1): 7.1

---

## 4. Verification Steps Per Task

| Task | Verification | Command / Check |
|------|-------------|-----------------|
| 1.1 | Import + instantiate | `python -c "from app.models.direccion_entrega import DireccionEntrega; d = DireccionEntrega(usuario_id=1, linea1='test'); print(d)"` |
| 1.2 | Import + attribute | `python -c "from app.models.usuario import Usuario; print(hasattr(Usuario, 'direcciones'))"` |
| 1.3 | Alembic apply + rollback | `cd backend && alembic upgrade head && alembic downgrade -1 && alembic upgrade head` |
| 1.4 | Import from package | `python -c "from app.models import DireccionEntrega; print('OK')"` |
| 2.1 | Import Repository | `python -c "from app.repositories.direccion_repository import DireccionRepository; print('OK')"` |
| 2.2 | UoW has property | `python -c "from app.uow import UnitOfWork; print(hasattr(UnitOfWork, 'direcciones'))"` |
| 3.1 | Package importable | `python -c "from app.modules import direcciones; print('OK')"` |
| 3.2 | Schemas import + validation | `python -c "from app.modules.direcciones.schemas import *; c = DireccionCreate(linea1='test'); print(c); e = DireccionCreate(linea1='')"` (expects 422) |
| 4.1 | Import Service | `python -c "from app.modules.direcciones.service import DireccionService; print('OK')"` |
| 5.1 | Router has 5 routes | `python -c "from app.modules.direcciones.router import router; print(f'{len(router.routes)} routes')"` |
| 6.1 | App has direcciones routes | `python -c "from app.main import app; routes = [r.path for r in app.routes if '/api/v1/direcciones' in r.path]; print(f'{len(routes)} direcciones routes')"` |
| 7.1 | All tests passing | `cd backend && pytest tests/test_direcciones.py -v --asyncio-mode=auto` (0 failures) |

---

## 5. Implementation Notes

### Auth mocking in tests
The `require_role(["CLIENT", "ADMIN"])` and `get_current_user` dependencies need to be overridden in test fixtures. Follow the same pattern as `test_ingredientes.py`:

```python
# Override get_uow
def override_get_uow(uow):
    def _get_uow():
        return uow
    return _get_uow

# Override get_current_user
def override_get_current_user(user):
    async def _get_current_user():
        return user
    return _get_current_user

# Override require_role
async def override_require_role():
    return None
```

### SQLite vs PostgreSQL considerations in tests
- The unique partial index (`WHERE es_principal = true AND deleted_at IS NULL`) works in SQLite too, but syntax may differ. In SQLite, use:
  ```python
  await session.execute(text(
      "CREATE UNIQUE INDEX IF NOT EXISTS idx_direccion_principal_unico "
      "ON direcciones_entrega (usuario_id) "
      "WHERE es_principal = 1 AND deleted_at IS NULL"
  ))
  ```
- Note: SQLite uses `1`/`0` for boolean, not `true`/`false` in partial index predicates.

### Naming convention
- Column names in Spanish: `usuario_id`, `es_principal`, `linea1`
- Repository methods in Spanish: `find_by_usuario`, `count_by_usuario`, `unset_previous_default`, `set_es_principal`
- Service methods in Spanish: `create_direccion`, `list_direcciones`, `update_direccion`, `delete_direccion`, `set_predeterminada`

### Error format
All exceptions follow RFC 7807 via `AppException` → `app_exception_to_http_exception()`. The router should raise `HTTPException` with `detail=e.message` for `AppException` subclasses.

---

## 6. Batch Execution Guide

For efficient implementation, execute tasks in this batch order:

1. **Batch 1** (independent): Tasks 1.1, 3.1 → can run in parallel
2. **Batch 2** (depends on 1.1): Tasks 1.2, 1.3, 1.4, 2.1 → can run in parallel after 1.1
3. **Batch 3** (depends on 2.1 + 3.1): Tasks 2.2, 3.2 → can run in parallel after Batch 2
4. **Batch 4** (depends on 2.2 + 3.2): Task 4.1 → single task
5. **Batch 5** (depends on 4.1): Task 5.1 → single task
6. **Batch 6** (depends on 5.1): Task 6.1 → single task
7. **Batch 7** (depends on 6.1): Task 7.1 → single task

Total: 7 batches, ~3 hours estimated.
