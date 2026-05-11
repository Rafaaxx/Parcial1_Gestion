# Design: CHANGE-05 — Direcciones de Entrega

## 1. Architecture Decisions (ADR)

### ADR-05-01: Feature-first module with strict layering

**Context**: El módulo `direcciones` necesita 5 endpoints, un modelo nuevo, repository propio, y lógica de negocio para ownership, dirección predeterminada y soft delete.

**Decision**: Se implementa con la misma estructura feature-first que `categorias`: modelo separado en `app/models/`, repository en `app/repositories/`, y módulo feature en `app/modules/direcciones/` con `schemas.py` + `service.py` + `router.py`. Se sigue el patrón de `CategoriaService` (recibe `uow` en constructor), no el de `IngredienteService` (que recibe `session` directa).

**Rationale**: `CategoriaService` es el patrón más alineado con la arquitectura oficial (Router → Service → UoW → Repository → Model). Permite transacciones atómicas en operaciones multi-repo (como PATCH /predeterminada que toca dos direcciones distintas).

**Consequences**: El service depende de `UnitOfWork`, no de `AsyncSession`. Todas las operaciones se ejecutan dentro del contexto del UoW y el commit se maneja desde el router.

---

### ADR-05-02: Ownership validation con 404 en lugar de 403

**Context**: Por regla de negocio RN-DI03, un cliente solo puede ver/editar/eliminar sus propias direcciones. Si otro usuario intenta acceder, no debe saber si la dirección existe o no.

**Decision**: Cuando `direccion.usuario_id != jwt_user.id`, se retorna 404 (NOT_FOUND), nunca 403 (FORBIDDEN). Esto es idéntico al principio de seguridad de GitHub/GitLab para recursos privados.

**Rationale**: 
- 404 no revela existencia del recurso
- 403 sí revela que el recurso existe pero no tienes acceso
- Previene ataques de enumeración de IDs

**Consequences**: Los handlers de error en el router capturan `AppException` y convierten a `HTTPException(404)`. No se necesita lógica extra de roles; la validación es siempre por `usuario_id` del JWT vs `direccion.usuario_id`.

---

### ADR-05-03: Índice único parcial para integridad de predeterminada

**Context**: RN-DI02 exige que solo una dirección sea predeterminada por usuario. En un sistema concurrente, dos requests PATCH simultáneas podrían crear dos direcciones con `es_principal=true` para el mismo usuario.

**Decision**: Se agrega un índice único parcial a nivel de base de datos:

```sql
CREATE UNIQUE INDEX idx_direccion_principal_unico 
ON direcciones_entrega (usuario_id) 
WHERE es_principal = true AND deleted_at IS NULL;
```

Esto actúa como doble seguridad junto con la lógica de aplicación:
1. **Service layer**: la transacción atómica unset + set en el mismo flush
2. **DB constraint**: el índice único parcial garantiza que jamás haya dos con `es_principal=true`

Si el índice detecta una violación (race condition), se captura `IntegrityError` y se retorna 409 Conflict.

**Rationale**: La lógica de aplicación es suficiente para el caso normal, pero en sistemas async con PostgreSQL y múltiples workers, el índice es la red de seguridad definitiva. Es un patrón conocido como "optimistic locking con constraint".

**Consequences**: La migración de Alembic debe crear este índice. El service debe capturar `IntegrityError` (de `sqlalchemy.exc`) y traducirlo a `ConflictError` (409).

---

### ADR-05-04: Reasignación automática de predeterminada al eliminar

**Context**: REQ-DI-26 (US-027) especifica que si se elimina la dirección predeterminada y existen otras direcciones activas, se debe asignar `es_principal=true` a la más reciente.

**Decision**: La reasignación se hace con una subquery dentro de la misma transacción que el soft delete. Se selecciona la dirección activa más reciente (`created_at DESC`) y se le setea `es_principal=true`. Si no hay más direcciones activas, no se hace nada (queda sin predeterminada).

**Rationale**: 
- Todo ocurre en la misma transacción → atómico
- "Más reciente" se define como `max(created_at)` entre las direcciones activas del usuario
- Si solo quedan direcciones con `deleted_at` seteado, no hay predeterminada que reasignar

**Consequences**: El repository necesita un método `find_most_recent_active(usuario_id)` que devuelva la dirección activa más reciente.

---

### ADR-05-05: Pydantic v2 con `from_attributes` para schemas de respuesta

**Context**: Los schemas de respuesta (`DireccionRead`, `DireccionListResponse`) deben convertir modelos ORM de SQLModel a JSON.

**Decision**: Se usa `model_validate()` (Pydantic v2) con `Config.from_attributes = True`, idéntico a `CategoriaRead` en el módulo de categorías.

**Rationale**: Es el patrón estándar del proyecto. `model_validate(orm_obj)` es el reemplazo de Pydantic v1's `from_orm()`. Todos los schemas existentes lo usan.

**Consequences**: Los schemas de respuesta importan `from pydantic import BaseModel, Field` y tienen `class Config: from_attributes = True`.

---

### ADR-05-06: Schema `DireccionUpdate` como `BaseModel` con todos los campos opcionales

**Context**: PUT /direcciones/{id} permite actualización parcial (solo alias, solo linea1, o ambos).

**Decision**: Se define `DireccionUpdate(BaseModel)` con `alias: Optional[str]` y `linea1: Optional[str]`. Ambos opcionales. En el service, si el campo es `None` no se actualiza.

**Rationale**: 
- Un schema con campos opcionales permite que el cliente envíe solo los campos que quiere cambiar
- `model_dump(exclude_none=True)` genera el dict solo con los campos provistos
- Es idéntico al patrón de `CategoriaUpdate`

**Consequences**: El body vacío `{}` resulta en `model_dump(exclude_none=True) == {}`. Según EC-10, esto debe devolver 422 (no hay campos para actualizar). Se valida en el service antes de llamar al repository.

---

## 2. Module Structure

```
backend/
├── app/
│   ├── models/
│   │   ├── __init__.py                    # + DireccionEntrega export
│   │   ├── direccion_entrega.py           # [NEW] SQLModel
│   │   └── ...
│   │
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── base.py                        # BaseRepository[T]
│   │   ├── direccion_repository.py        # [NEW] DireccionRepository
│   │   └── ...
│   │
│   ├── modules/
│   │   ├── __init__.py
│   │   ├── direcciones/                   # [NEW] Feature module
│   │   │   ├── __init__.py
│   │   │   ├── schemas.py
│   │   │   ├── service.py
│   │   │   └── router.py
│   │   └── ...
│   │
│   ├── uow.py                             # + direcciones property
│   └── main.py                            # + include_router(direcciones_router)
│
├── migrations/
│   └── versions/
│       └── XXXX_crear_direcciones_entrega.py  # [NEW] Migration
│
└── tests/
    └── test_direcciones.py                # [NEW] Integration tests
```

### File-by-file responsibility

| File | Purpose |
|------|---------|
| `app/models/direccion_entrega.py` | SQLModel `DireccionEntrega` (table=True), FK → usuarios.id |
| `app/repositories/direccion_repository.py` | `DireccionRepository(BaseRepository[DireccionEntrega])` + métodos de ownership/predeterminada |
| `app/modules/direcciones/__init__.py` | Package init (vacío, como categorias) |
| `app/modules/direcciones/schemas.py` | Pydantic v2 schemas: Create, Update, Read, ListResponse |
| `app/modules/direcciones/service.py` | `DireccionService` con lógica de negocio |
| `app/modules/direcciones/router.py` | 5 endpoints REST con auth y ownership |
| `app/uow.py` | + `direcciones` property → `DireccionRepository` |
| `app/models/__init__.py` | + `DireccionEntrega` al `__all__` |
| `app/main.py` | + `include_router(direcciones_router)` |
| `migrations/versions/XXXX_crear_direcciones_entrega.py` | Create table + partial unique index |
| `tests/test_direcciones.py` | Integration tests covering all 5 endpoints |

---

## 3. Data Model

### 3.1 `DireccionEntrega` (SQLModel)

```python
# backend/app/models/direccion_entrega.py

from typing import Optional
from sqlmodel import Field, SQLModel, Relationship
from app.models.mixins import BaseModel

class DireccionEntrega(BaseModel, table=True):
    __tablename__ = "direcciones_entrega"

    id: Optional[int] = Field(default=None, primary_key=True)
    usuario_id: int = Field(
        foreign_key="usuarios.id",
        nullable=False,
        description="FK al usuario propietario de la dirección",
    )
    alias: Optional[str] = Field(
        default=None,
        max_length=50,
        description="Etiqueta opcional: Casa, Trabajo, etc.",
    )
    linea1: str = Field(
        nullable=False,
        max_length=500,
        description="Dirección completa (línea 1)",
    )
    es_principal: bool = Field(
        default=False,
        nullable=False,
        description="Indica si es la dirección predeterminada del usuario",
    )

    # Relationship (opcional, para navegación ORM)
    usuario: Optional["Usuario"] = Relationship(
        back_populates="direcciones",
    )
```

### 3.2 Database-level constraints

```sql
-- Tabla
CREATE TABLE direcciones_entrega (
    id              SERIAL PRIMARY KEY,
    usuario_id      INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    alias           VARCHAR(50),
    linea1          VARCHAR(500) NOT NULL,
    es_principal    BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ DEFAULT NULL
);

-- Partial unique index: at most one es_principal=true per user (non-deleted)
CREATE UNIQUE INDEX idx_direccion_principal_unico
ON direcciones_entrega (usuario_id)
WHERE es_principal = true AND deleted_at IS NULL;

-- Index for listing addresses of a user
CREATE INDEX idx_direcciones_usuario
ON direcciones_entrega (usuario_id)
WHERE deleted_at IS NULL;
```

### 3.3 Model inheritance chain

```
SQLModel
  └── TimestampMixin (created_at, updated_at)
        └── SoftDeleteMixin (deleted_at, is_deleted())
              └── BaseModel (combined — used by all models)
                    ├── Categoria
                    ├── Usuario
                    ├── Ingrediente
                    ├── RefreshToken
                    └── DireccionEntrega  [NEW]
```

### 3.4 Foreign key to Usuario

The `Usuario` model needs a `direcciones` relationship for bidirectional navigation:

```python
# In app/models/usuario.py (modification)
class Usuario(BaseModel, table=True):
    ...
    # ── Existing Relationships ──
    refresh_tokens: List["RefreshToken"] = Relationship(...)
    usuario_roles: List["UsuarioRol"] = Relationship(...)

    # ── ADD ──
    direcciones: List["DireccionEntrega"] = Relationship(
        back_populates="usuario",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
```

Note: This relationship is optional (no code depends on it). It's added for ORM navigation convenience and can be omitted if tight coupling is a concern. The cascade `delete-orphan` with `ON DELETE CASCADE` on the FK ensures consistency.

---

## 4. Component Design

### 4.1 Schemas (`app/modules/direcciones/schemas.py`)

```python
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class DireccionBase(BaseModel):
    """Common address fields for Create/Read"""
    alias: Optional[str] = Field(
        None, max_length=50, description="Etiqueta opcional (max 50 chars)"
    )
    linea1: str = Field(
        ..., max_length=500, min_length=1,
        description="Dirección completa (línea 1, requerido, max 500 chars)"
    )


class DireccionCreate(DireccionBase):
    """Schema for creating a new address.
    
    Note: es_principal is NOT in this schema — it's auto-assigned
    by the service (first address = principal).
    """
    pass


class DireccionUpdate(BaseModel):
    """Schema for updating an address — all fields optional.
    
    Note: es_principal cannot be changed via PUT.
    To change the default address, use PATCH /{id}/predeterminada.
    """
    alias: Optional[str] = Field(None, max_length=50)
    linea1: Optional[str] = Field(None, max_length=500, min_length=1)


class DireccionRead(DireccionBase):
    """Schema for address response"""
    id: int
    usuario_id: int
    es_principal: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DireccionListResponse(BaseModel):
    """Paginated list response"""
    items: List[DireccionRead]
    total: int
    skip: int = Field(default=0)
    limit: int = Field(default=100)
```

**Validation strategy**:
- `alias`: `max_length=50` en Pydantic (pre-validación antes de llegar al service). Se trimea en el service.
- `linea1`: `min_length=1` y `max_length=500` en Pydantic. Se trimea en el service.
- Si `alias` después del trim queda vacío → se trata como `None` (EC-04).
- Si `linea1` después del trim queda vacío → rechazar con 422 (EC-05).
- `es_principal` no existe en `DireccionCreate` ni `DireccionUpdate` — solo se asigna por el service o vía PATCH.
- `usuario_id` no se envía desde el cliente — lo inyecta el service desde el JWT.

---

### 4.2 Repository (`app/repositories/direccion_repository.py`)

```python
class DireccionRepository(BaseRepository[DireccionEntrega]):
    """
    Repository for DireccionEntrega with ownership and default address support.
    
    Inherits from BaseRepository:
    - find(id) → Optional[DireccionEntrega]  (excluye soft-deleted)
    - list_all(skip, limit) → tuple[list, total]
    - count(filters) → int
    - create(obj) → DireccionEntrega
    - update(id, data) → Optional[DireccionEntrega]
    - soft_delete(id) → Optional[DireccionEntrega]
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session, DireccionEntrega)

    async def find_by_usuario(
        self, usuario_id: int, skip: int = 0, limit: int = 100
    ) -> tuple[list[DireccionEntrega], int]:
        """
        List active addresses for a user, ordered by created_at DESC.
        Uses BaseRepository.list_all with a usuario_id filter.
        """
        ...

    async def find_user_direccion(
        self, direccion_id: int, usuario_id: int
    ) -> Optional[DireccionEntrega]:
        """
        Find a single address with ownership check.
        Returns None if address doesn't exist, doesn't belong to user,
        or is soft-deleted.
        
        SELECT * FROM direcciones_entrega
        WHERE id = :direccion_id
          AND usuario_id = :usuario_id
          AND deleted_at IS NULL
        """
        ...

    async def find_principal(self, usuario_id: int) -> Optional[DireccionEntrega]:
        """
        Find the current default address for a user.
        
        SELECT * FROM direcciones_entrega
        WHERE usuario_id = :usuario_id
          AND es_principal = true
          AND deleted_at IS NULL
        """
        ...

    async def count_by_usuario(self, usuario_id: int) -> int:
        """
        Count active addresses for a user.
        
        SELECT COUNT(*) FROM direcciones_entrega
        WHERE usuario_id = :usuario_id AND deleted_at IS NULL
        """
        ...

    async def unset_previous_default(self, usuario_id: int) -> None:
        """
        Unset es_principal for the current default address.
        This is called within the same transaction as set_es_principal.
        
        UPDATE direcciones_entrega
        SET es_principal = false
        WHERE usuario_id = :usuario_id
          AND es_principal = true
          AND deleted_at IS NULL
        """
        ...

    async def set_es_principal(self, direccion_id: int, value: bool) -> None:
        """
        Set es_principal for a specific address.
        No need to load the full entity — direct UPDATE via session.execute().
        
        UPDATE direcciones_entrega
        SET es_principal = :value
        WHERE id = :direccion_id AND deleted_at IS NULL
        """
        ...

    async def find_most_recent_active(
        self, usuario_id: int, exclude_id: Optional[int] = None
    ) -> Optional[DireccionEntrega]:
        """
        Find the most recently created active address for a user.
        Used when reassigning default after deleting the current default.
        
        SELECT * FROM direcciones_entrega
        WHERE usuario_id = :usuario_id
          AND deleted_at IS NULL
          AND id != :exclude_id   -- exclude the one being deleted
        ORDER BY created_at DESC
        LIMIT 1
        """
        ...
```

**Design notes**:
- `find_user_direccion` combina filtro por `id`, `usuario_id` y `deleted_at IS NULL` en una sola consulta. No se necesita "verificar ownership" como paso separado — la query lo hace atómicamente.
- `unset_previous_default` y `set_es_principal` usan `session.execute()` con UPDATE directo en lugar de cargar entidades. Más eficiente y evita lecturas innecesarias.
- `find_most_recent_active` se usa en el flujo de DELETE cuando se elimina la predeterminada.

---

### 4.3 Service (`app/modules/direcciones/service.py`)

```python
class DireccionService:
    """
    Business logic for address management.
    
    Key responsibilities:
    - Ownership validation (usuario_id from JWT vs direccion.usuario_id)
    - Auto-assign es_principal on first address (RN-DI01)
    - Atomic default address switching (RN-DI02)
    - Reassign default on delete of current default (REQ-DI-26)
    - Trimming/cleaning input fields
    """
    
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def create_direccion(
        self, usuario_id: int, data: DireccionCreate
    ) -> DireccionRead:
        """
        1. Trim alias and linea1
        2. Validate alias not empty after trim (treat as None)
        3. Validate linea1 not empty after trim
        4. Count user's existing addresses
        5. If count == 0 → set es_principal = True (RN-DI01)
        6. Create via repository
        7. Return DireccionRead
        """
        ...

    async def list_direcciones(
        self, usuario_id: int, skip: int = 0, limit: int = 100
    ) -> DireccionListResponse:
        """
        1. Call repo.find_by_usuario(usuario_id, skip, limit)
        2. Return paginated response with total count
        """
        ...

    async def update_direccion(
        self, direccion_id: int, usuario_id: int, data: DireccionUpdate
    ) -> DireccionRead:
        """
        1. Trim fields
        2. Validate at least one field to update (otherwise 422 — EC-10)
        3. Verify ownership: repo.find_user_direccion(id, user_id) → 404 if None
        4. Validate linea1 after trim if provided
        5. Update via repo.update(id, filtered_data)
        6. Return DireccionRead
        """
        ...

    async def delete_direccion(
        self, direccion_id: int, usuario_id: int
    ) -> None:
        """
        1. Verify ownership + existence: repo.find_user_direccion(id, user_id) → 404 if None
        2. Check if this is the principal address
        3. If principal:
           a. Find most recent active address (repo.find_most_recent_active)
           b. If found → set es_principal = True on that one
        4. repo.soft_delete(direccion_id)
        5. All within same transaction (commit in router)
        """
        ...

    async def set_predeterminada(
        self, direccion_id: int, usuario_id: int
    ) -> DireccionRead:
        """
        ATOMIC transaction (all-or-nothing):
        1. Verify ownership + existence → 404 if None
        2. If already es_principal == True → return current (idempotent)
        3. repo.unset_previous_default(usuario_id)
        4. repo.set_es_principal(direccion_id, True)
        5. Reload and return updated DireccionRead
        """
        ...
```

#### Input sanitization rules

| Field | Trim | After-trim behavior |
|-------|------|---------------------|
| `alias` | Sí | Si queda vacío → se guarda como `None` |
| `linea1` | Sí | Si queda vacío → rechazar con 422 |

#### Error matrix

| Condición | Excepción | HTTP Code |
|-----------|-----------|-----------|
| `linea1` vacío (después de trim) | `ValidationError("linea1 no puede estar vacío")` | 422 |
| `alias` > 50 chars (después de trim) | `ValidationError("alias no puede exceder 50 caracteres")` | 422 |
| Dirección no encontrada / no owned / soft-deleted | `NotFoundError("Dirección no encontrada")` | 404 |
| Violación índice único parcial (race condition) | `ConflictError("Ya existe una dirección predeterminada")` | 409 |
| PUT con body vacío | `ValidationError("No hay campos para actualizar")` | 422 |

---

### 4.4 Router (`app/modules/direcciones/router.py`)

```python
router = APIRouter(prefix="/api/v1/direcciones", tags=["direcciones"])

@router.post(
    "",
    response_model=DireccionRead,
    status_code=201,
    summary="Crear dirección de entrega",
)
async def create_direccion(
    data: DireccionCreate,
    uow: UnitOfWork = Depends(get_uow),
    _: None = Depends(require_role(["CLIENT", "ADMIN"])),
    current_user: Usuario = Depends(get_current_user),
) -> DireccionRead:
    """
    Protected: CLIENT or ADMIN role required.
    The first address for a user is auto-assigned as default (es_principal=True).
    """
    try:
        service = DireccionService(uow)
        result = await service.create_direccion(current_user.id, data)
        await uow.commit()
        return result
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        await uow.rollback()
        logger.error(f"POST /direcciones failed: {type(e).__name__}: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.get(
    "",
    response_model=DireccionListResponse,
    summary="Listar direcciones del usuario autenticado",
)
async def list_direcciones(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    uow: UnitOfWork = Depends(get_uow),
    _: None = Depends(require_role(["CLIENT", "ADMIN"])),
    current_user: Usuario = Depends(get_current_user),
) -> DireccionListResponse:
    """
    Protected: CLIENT or ADMIN role required.
    Only returns addresses belonging to the authenticated user.
    """
    try:
        service = DireccionService(uow)
        result = await service.list_direcciones(current_user.id, skip, limit)
        return result
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"GET /direcciones failed: {type(e).__name__}: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.put(
    "/{direccion_id}",
    response_model=DireccionRead,
    summary="Actualizar dirección de entrega",
)
async def update_direccion(
    direccion_id: int,
    data: DireccionUpdate,
    uow: UnitOfWork = Depends(get_uow),
    _: None = Depends(require_role(["CLIENT", "ADMIN"])),
    current_user: Usuario = Depends(get_current_user),
) -> DireccionRead:
    """
    Protected: CLIENT or ADMIN role required.
    Validates ownership (404 if not owned).
    Only alias and linea1 can be updated (not es_principal).
    """
    try:
        service = DireccionService(uow)
        result = await service.update_direccion(direccion_id, current_user.id, data)
        await uow.commit()
        return result
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        await uow.rollback()
        logger.error(f"PUT /direcciones/{direccion_id} failed: {type(e).__name__}: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.delete(
    "/{direccion_id}",
    status_code=204,
    summary="Eliminar dirección de entrega (soft delete)",
)
async def delete_direccion(
    direccion_id: int,
    uow: UnitOfWork = Depends(get_uow),
    _: None = Depends(require_role(["CLIENT", "ADMIN"])),
    current_user: Usuario = Depends(get_current_user),
) -> None:
    """
    Protected: CLIENT or ADMIN role required.
    Soft delete — sets deleted_at timestamp.
    If deleting the default address, reassigns to the most recent active one.
    """
    try:
        service = DireccionService(uow)
        await service.delete_direccion(direccion_id, current_user.id)
        await uow.commit()
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        await uow.rollback()
        logger.error(f"DELETE /direcciones/{direccion_id} failed: {type(e).__name__}: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.patch(
    "/{direccion_id}/predeterminada",
    response_model=DireccionRead,
    summary="Establecer dirección como predeterminada",
)
async def set_predeterminada(
    direccion_id: int,
    uow: UnitOfWork = Depends(get_uow),
    _: None = Depends(require_role(["CLIENT", "ADMIN"])),
    current_user: Usuario = Depends(get_current_user),
) -> DireccionRead:
    """
    Protected: CLIENT or ADMIN role required.
    
    Atomic operation within a single transaction:
    1. Unset es_principal on current default (if exists)
    2. Set es_principal = true on the target address
    
    Idempotent: if already the default, returns 200 without changes.
    """
    try:
        service = DireccionService(uow)
        result = await service.set_predeterminada(direccion_id, current_user.id)
        await uow.commit()
        return result
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except ConflictError as e:
        raise HTTPException(status_code=409, detail=e.message)
    except IntegrityError:
        await uow.rollback()
        raise HTTPException(
            status_code=409,
            detail="Ya existe una dirección predeterminada"
        )
    except Exception as e:
        await uow.rollback()
        logger.error(
            f"PATCH /direcciones/{direccion_id}/predeterminada failed: "
            f"{type(e).__name__}: {e}"
        )
        raise HTTPException(status_code=500, detail="Error interno del servidor")
```

**Router dependency injection pattern**:

```
DireccionService(uow)
            ↑
       get_uow()  →  UnitOfWork(session)
                         ↑
                    get_db()  →  AsyncSession
```

All endpoints follow this chain. The router creates a new `DireccionService` instance per request, passing the UoW from `get_uow`. No service singletons.

---

## 5. Sequence Diagrams for Critical Flows

### 5.1 PATCH /{id}/predeterminada (Set default address)

This is the most critical flow — must be atomic (RN-DI02).

```
Client                  Router                  DireccionService           DireccionRepository        DB
  │                       │                          │                          │                    │
  │  PATCH /direcciones/2 │                          │                          │                    │
  │  /predeterminada      │                          │                          │                    │
  │──────────────────────>│                          │                          │                    │
  │                       │                          │                          │                    │
  │                       │  require_role()          │                          │                    │
  │                       │  get_current_user()      │                          │                    │
  │                       │  get_uow()               │                          │                    │
  │                       │                          │                          │                    │
  │                       │  service.set_predeterminada(2, 42)                  │                    │
  │                       │─────────────────────────>│                          │                    │
  │                       │                          │                          │                    │
  │                       │                          │  find_user_direccion(2, 42)                  │
  │                       │                          │─────────────────────────>│                    │
  │                       │                          │                          │── SELECT ... ─────>│
  │                       │                          │                          │<───── row ─────────│
  │                       │                          │<───── DireccionEntrega ───│                    │
  │                       │                          │                          │                    │
  │                       │                          │  Verify: owns? exists? not deleted?           │
  │                       │                          │  Verify: es_principal?                        │
  │                       │                          │  (if true → idempotent, return)               │
  │                       │                          │                          │                    │
  │                       │                          │  unset_previous_default(42)                   │
  │                       │                          │─────────────────────────>│                    │
  │                       │                          │                          │── UPDATE SET       │
  │                       │                          │                          │   es_principal=F   │
  │                       │                          │                          │   WHERE user=42   │
  │                       │                          │                          │   AND principal=T ─>│
  │                       │                          │<───────── ok ────────────│                    │
  │                       │                          │                          │                    │
  │                       │                          │  set_es_principal(2, True)                    │
  │                       │                          │─────────────────────────>│                    │
  │                       │                          │                          │── UPDATE SET       │
  │                       │                          │                          │   es_principal=T   │
  │                       │                          │                          │   WHERE id=2 ─────>│
  │                       │                          │<───────── ok ────────────│                    │
  │                       │                          │                          │                    │
  │                       │                          │  find(2)  (reload)       │                    │
  │                       │                          │─────────────────────────>│                    │
  │                       │                          │                          │── SELECT id=2 ────>│
  │                       │                          │<───── refreshed row ─────│                    │
  │                       │                          │                          │                    │
  │                       │<─── DireccionRead ───────│                          │                    │
  │                       │                          │                          │                    │
  │                       │  uow.commit()            │                          │                    │
  │                       │───────────────────────────────────────────────────────────────────────>│
  │                       │                          │                          │              COMMIT │
  │                       │<───────────────────────────────────────────────────────────────────────│
  │                       │                          │                          │                    │
  │  200 + DireccionRead  │                          │                          │                    │
  │<──────────────────────│                          │                          │                    │
```

**Error path (race condition)**:

```
  ...mismo flujo hasta set_es_principal...
  │                       │                          │  set_es_principal(2, True)                    │
  │                       │                          │─────────────────────────>│                    │
  │                       │                          │                          │── UPDATE SET       │
  │                       │                          │                          │   es_principal=T   │
  │                       │                          │                          │   WHERE id=2 ─────>│
  │                       │                          │                          │                    │
  │                       │                          │                          │  !! UNIQUE INDEX   │
  │                       │                          │                          │  VIOLATION !!      │
  │                       │                          │                          │<── IntegrityError ─│
  │                       │                          │<── IntegrityError ───────│                    │
  │                       │                          │                          │                    │
  │                       │  await uow.rollback()    │                          │                    │
  │                       │───────────────────────────────────────────────────────────────────────>│
  │                       │<───────────────────────────────────────────────────────────────────────│
  │                       │                          │                          │            ROLLBACK│
  │                       │                          │                          │                    │
  │  409 Conflict         │                          │                          │                    │
  │<──────────────────────│                          │                          │                    │
```

### 5.2 DELETE /{id} con reasignación de predeterminada

```
Client                  Router                  DireccionService           DireccionRepository        DB
  │                       │                          │                          │                    │
  │  DELETE /direcciones  │                          │                          │                    │
  │  /1                   │                          │                          │                    │
  │──────────────────────>│                          │                          │                    │
  │                       │  (auth + uow)            │                          │                    │
  │                       │  service.delete_direccion(1, 42)                   │                    │
  │                       │─────────────────────────>│                          │                    │
  │                       │                          │                          │                    │
  │                       │                          │  find_user_direccion(1, 42) → exists + owned   │
  │                       │                          │─────────────────────────>│                    │
  │                       │                          │<──── OK, es_principal ───│                    │
  │                       │                          │                          │                    │
  │                       │                          │  (es principal? yes)     │                    │
  │                       │                          │  find_most_recent_active  │                    │
  │                       │                          │  (42, exclude_id=1)      │                    │
  │                       │                          │─────────────────────────>│                    │
  │                       │                          │<─── DireccionEntrega ────│                    │
  │                       │                          │     (id=3, más reciente) │                    │
  │                       │                          │                          │                    │
  │                       │                          │  set_es_principal(3, True)                    │
  │                       │                          │─────────────────────────>│                    │
  │                       │                          │<───────── ok ────────────│                    │
  │                       │                          │                          │                    │
  │                       │                          │  soft_delete(1)                              │
  │                       │                          │─────────────────────────>│                    │
  │                       │                          │<───────── ok ────────────│                    │
  │                       │                          │                          │                    │
  │                       │  uow.commit()            │                          │                    │
  │                       │───────────────────────────────────────────────────── COMMIT ────────────>│
  │  204 No Content       │                          │                          │                    │
  │<──────────────────────│                          │                          │                    │
```

**Atomicity guarantee**: All DB operations happen in the same session flush. If any step fails (e.g. the `soft_delete`), `uow.rollback()` undoes everything. The transaction boundary is controlled by the router.

---

## 6. Unit of Work Integration

### 6.1 Modified `app/uow.py`

```python
from app.repositories.direccion_repository import DireccionRepository

class UnitOfWork:
    def __init__(self, session: AsyncSession):
        self.session = session
        self._repositories: dict[Type, BaseRepository] = {}
        self._categorias: Optional[CategoriaRepository] = None
        self._direcciones: Optional[DireccionRepository] = None  # ADD
        self.logger = logging.getLogger(f"{__name__}.UnitOfWork")

    # ── Existing properties ──
    @property
    def categorias(self) -> CategoriaRepository:
        if self._categorias is None:
            self._categorias = CategoriaRepository(self.session)
        return self._categorias

    # ── ADD ──
    @property
    def direcciones(self) -> DireccionRepository:
        """Get or create DireccionRepository instance."""
        if self._direcciones is None:
            self._direcciones = DireccionRepository(self.session)
        return self._direcciones
```

### 6.2 Usage in service

```python
# In DireccionService.create_direccion
direccion = await self.uow.direcciones.create(direccion_model)

# In DireccionService.set_predeterminada
await self.uow.direcciones.unset_previous_default(usuario_id)
await self.uow.direcciones.set_es_principal(direccion_id, True)
```

The UoW ensures both `unset` and `set` hit the same database session. When the router calls `uow.commit()`, both changes are flushed atomically.

---

## 7. App Initialization

### 7.1 Modified `app/main.py`

```python
from app.modules.direcciones.router import router as router_direcciones

app.include_router(router_direcciones)
```

### 7.2 Modified `app/models/__init__.py`

```python
from app.models.direccion_entrega import DireccionEntrega

__all__ = [
    ...
    "DireccionEntrega",
]
```

---

## 8. Testing Strategy

### 8.1 Test hierarchy

Tests in `backend/tests/test_direcciones.py` follow the same structure as the existing integration tests.

#### US-024: Crear dirección
| Test | Description | Key assertion |
|------|-------------|---------------|
| `test_create_success_without_alias` | POST con solo linea1 | 201, es_principal=true (first address) |
| `test_create_success_with_alias` | POST con alias | 201, alias="Casa" |
| `test_create_second_address_not_principal` | POST after 1 exists | 201, es_principal=false |
| `test_create_linea1_empty` | POST con linea1="" | 422 |
| `test_create_alias_too_long` | POST con alias>50 | 422 |
| `test_create_no_auth` | POST sin token | 401 |

#### US-025: Listar direcciones
| Test | Description | Key assertion |
|------|-------------|---------------|
| `test_list_own_addresses` | GET normal | 200, items match user |
| `test_list_empty` | GET sin direcciones | 200, items=[] |
| `test_list_pagination` | GET con skip/limit | 200, correct slicing |
| `test_list_excludes_soft_deleted` | GET after soft delete | total excludes deleted |
| `test_list_other_user_addresses_not_included` | User A sees only A's | total correct per user |

#### US-026: Editar dirección
| Test | Description | Key assertion |
|------|-------------|---------------|
| `test_update_alias_and_linea1` | PUT ambos campos | 200, values updated |
| `test_update_only_alias` | PUT parcial | 200, alias changes |
| `test_update_not_owned` | PUT dirección ajena | 404 |
| `test_update_not_found` | PUT id inexistente | 404 |
| `test_update_soft_deleted` | PUT sobre deleted | 404 |
| `test_update_empty_body` | PUT {} | 422 |

#### US-027: Eliminar dirección
| Test | Description | Key assertion |
|------|-------------|---------------|
| `test_soft_delete_success` | DELETE normal | 204, deleted_at set |
| `test_delete_not_owned` | DELETE dirección ajena | 404 |
| `test_delete_already_deleted` | DELETE sobre deleted | 404 |
| `test_delete_principal_reassigns_default` | DELETE predeterminada con otras | 204, otra se vuelve predeterminada |
| `test_delete_only_address` | DELETE única dirección | 204, usuario sin direcciones |

#### US-028: Establecer predeterminada
| Test | Description | Key assertion |
|------|-------------|---------------|
| `test_set_predeterminada_success` | PATCH normal | 200, es_principal switched |
| `test_set_predeterminada_idempotent` | PATCH ya predeterminada | 200, no change |
| `test_set_predeterminada_not_owned` | PATCH dirección ajena | 404 |
| `test_set_predeterminada_soft_deleted` | PATCH sobre deleted | 404 |
| `test_set_predeterminada_atomicity` | Verify both unset+set in same TX | DB consistent after |

### 8.2 Fixtures needed

```
@pytest_asyncio.fixture
async def usuario_cliente(db_session):  # Usuario with CLIENT role
    ...

@pytest_asyncio.fixture
async def direccion_data():  # Sample DireccionCreate payload
    ...

@pytest_asyncio.fixture
async def direccion(db_session, usuario_cliente):  # Created DireccionEntrega for tests
    ...
```

### 8.3 Race condition test (manual / stress)

The `test_set_predeterminada_atomicity` test should ideally send concurrent `PATCH` requests and verify DB consistency:
- Create user with 3 addresses
- Fire 2 concurrent PATCH requests targeting different addresses
- Both finish (one succeeds, one gets 409)
- Verify exactly one address has `es_principal=true`

This can use `asyncio.gather` with `httpx.AsyncClient`.

---

## 9. Error Handling Summary

All endpoints follow a consistent error handling pattern:

```
try:
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

HTTP status codes used:

| Code | When |
|------|------|
| 201 | POST create success |
| 200 | GET, PUT, PATCH success |
| 204 | DELETE success (No Content) |
| 400 | Validation logic error (not used in direcciones, but available) |
| 401 | Missing/invalid token |
| 403 | Insufficient role (from `require_role`) |
| 404 | Resource not found / not owned / soft-deleted |
| 409 | Race condition on unique partial index |
| 422 | Pydantic validation error (field format) or business validation |
| 500 | Unexpected server error |

---

## 10. Migration Plan

The Alembic migration (`XXXX_crear_direcciones_entrega.py`) will:

1. Create table `direcciones_entrega`:
   - `id` SERIAL PRIMARY KEY
   - `usuario_id` INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE
   - `alias` VARCHAR(50) DEFAULT NULL
   - `linea1` VARCHAR(500) NOT NULL
   - `es_principal` BOOLEAN NOT NULL DEFAULT FALSE
   - `created_at` TIMESTAMPTZ NOT NULL DEFAULT NOW()
   - `updated_at` TIMESTAMPTZ NOT NULL DEFAULT NOW()
   - `deleted_at` TIMESTAMPTZ DEFAULT NULL

2. Create indexes:
   ```sql
   CREATE UNIQUE INDEX idx_direccion_principal_unico
   ON direcciones_entrega (usuario_id)
   WHERE es_principal = true AND deleted_at IS NULL;

   CREATE INDEX idx_direcciones_usuario_activas
   ON direcciones_entrega (usuario_id)
   WHERE deleted_at IS NULL;
   ```

3. Downgrade:
   ```sql
   DROP TABLE direcciones_entrega;
   ```
