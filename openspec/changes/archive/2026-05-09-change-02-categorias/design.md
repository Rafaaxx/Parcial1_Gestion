# Design: Categorías Jerárquicas (change-02-categorias)

## Technical Approach

This design implements hierarchical product categories using **self-referential foreign keys** and **recursive Common Table Expressions (CTEs)** to enable efficient tree traversal at the database level. The module follows the strict layered architecture: Router → Service → UoW → Repository → Model, with async/await throughout. Soft-delete is applied consistently with existing patterns (Usuario model) to preserve audit trails.

**Key principle**: Complexity lives in the **Repository** (SQL CTE queries) and **Service** (validation logic), not in the Router. The Router is purely HTTP ceremony.

---

## Architecture Decisions

| Decision | Choice | Alternatives Rejected | Rationale |
|----------|--------|----------------------|-----------|
| **CTE for tree queries** | PostgreSQL WITH RECURSIVE | Python recursive loops + N+1 queries | CTE queries the database once; Python loops cause N+1 select statements. Scale matters: 1000 categories → 1 CTE query vs. 1000+ Python queries. |
| **Soft-delete strategy** | Reuse `SoftDeleteMixin` + `deleted_at TIMESTAMPTZ` | Hard delete + backup table | Matches existing Usuario pattern; preserves audit trail; reverses accidental deletes in v2. |
| **Cycle detection** | Recursive CTE with depth limit + iterative parent trace | Recursive DFS in Python | DFS on large trees causes stack overflow; CTE with depth limit (20) detects cycles safely and delegates to database. |
| **Self-reference validation** | Application-level check (`parent_id != id`) | Database trigger | Application layer is faster for this simple check; v2 can add triggers for defense-in-depth. |
| **Parent FK constraint** | `categoria.parent_id` → `categoria.id` (self-ref) | Separate parent table | Self-referential design is simpler and proven for tree structures. |
| **RBAC enforcement** | `require_role(['ADMIN', 'STOCK'])` for write ops | Granular endpoint-level checks | Matches existing auth pattern (dependencies.py); reuses OAuth2 + JWT infrastructure. |
| **Tree serialization** | Nested Pydantic `CategoriaTree` with `subcategorias` | Flat list + client-side nesting | Nested response reduces client complexity; CTE already returns nested rows, minor denormalization acceptable. |

---

## Data Flow

```
HTTP Request (POST /api/v1/categorias)
    ↓
Router: Parse request, validate schema (Pydantic), check auth
    ↓
Service: Business logic (validate parent exists, no cycle, no self-ref)
    ↓
UnitOfWork: Open transaction context
    ↓
Repository: Execute CTE query or INSERT (SQL)
    ↓
PostgreSQL: Atomic operation (commit/rollback)
    ↓
Response: JSON (201 Created / 422 Unprocessable Entity / 403 Forbidden)
```

### Concrete Example: Create Category with Parent
1. **Router** receives `POST /api/v1/categorias` → `{"nombre": "Pizzas", "parent_id": 1}`
2. **Route Handler** extracts auth token → calls `require_role(['ADMIN', 'STOCK'])` dependency
3. **Service** (`categoria_service.create_categoria()`):
   - Check if `parent_id=1` exists (and is not soft-deleted)
   - Check `parent_id != id` (self-ref prevention)
   - Call `repo.validate_no_cycle(parent_id=1)` → CTE depth check
4. **Repository** (`categoria_repository.validate_no_cycle()`):
   - Execute CTE: traverse from `parent_id=1` up the tree, count depth
   - If depth > 20 → ValidationError
5. **Repository** (`create()` — inherited from BaseRepository):
   - INSERT into `categorias` table
6. **UoW** context manager:
   - On success → `await session.commit()`
   - On error → `await session.rollback()`
7. **Response**: `201 Created` + `CategoriaRead` schema

---

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `backend/app/models/categoria.py` | Create | SQLModel `Categoria` table with self-ref FK, timestamps, soft-delete |
| `backend/app/repositories/categoria_repository.py` | Create | Extends `BaseRepository[Categoria]` with CTE methods: `get_tree()`, `validate_no_cycle()`, `list_children()`, `count_products()` |
| `backend/app/modules/categorias/__init__.py` | Create | Package init (imports for clean API) |
| `backend/app/modules/categorias/schemas.py` | Create | Pydantic models: `CategoriaCreate`, `CategoriaRead`, `CategoriaTree` (nested), `CategoriaUpdate` |
| `backend/app/modules/categorias/service.py` | Create | `CategoriaService` with methods: `create_categoria()`, `update_categoria()`, `delete_categoria()`, `list_tree()`, `get_by_id()` |
| `backend/app/modules/categorias/router.py` | Create | FastAPI router with 5 endpoints (POST, GET /, GET /{id}, PUT, DELETE) |
| `backend/app/main.py` | Modify | Import and register `router` from `modules/categorias/` at line ~113 |
| `backend/app/uow.py` | Modify | Add lazy property `@property def categorias() → CategoriaRepository` (optional, or use generic `get_repository(Categoria)`) |
| `backend/migrations/versions/004_add_categorias_table.py` | Create | Alembic migration: CREATE TABLE categorias, FK self-ref, indexes, seed root category |
| `backend/tests/integration/test_categorias_api.py` | Create | Integration tests: CRUD, cycle detection, soft-delete validation, CTE correctness |

---

## Interfaces / Contracts

### 1. SQLModel: `Categoria` Table

```python
from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from app.models.mixins import BaseModel

class Categoria(BaseModel, table=True):
    __tablename__ = "categorias"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(max_length=100, nullable=False)
    parent_id: Optional[int] = Field(
        default=None,
        foreign_key="categorias.id",
        nullable=True,
        description="Parent category ID (NULL for root categories)"
    )
    
    # Relationships
    parent: Optional["Categoria"] = Relationship(
        back_populates="children",
        sa_relationship_kwargs={"remote_side": "Categoria.id"}
    )
    children: List["Categoria"] = Relationship(
        back_populates="parent",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    
    # Inherited from BaseModel: created_at, updated_at, deleted_at
```

### 2. Pydantic Schemas: Request/Response

```python
from datetime import datetime
from typing import Optional, List

class CategoriaCreate(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100)
    parent_id: Optional[int] = Field(None, description="Parent category ID or NULL for root")

class CategoriaUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    parent_id: Optional[int] = Field(None)

class CategoriaRead(BaseModel):
    id: int
    nombre: str
    parent_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class CategoriaTree(BaseModel):
    """Nested tree response for GET /api/v1/categorias"""
    id: int
    nombre: str
    parent_id: Optional[int]
    subcategorias: List["CategoriaTree"] = []
    
    class Config:
        from_attributes = True

CategoriaTree.model_rebuild()  # For recursive definition
```

### 3. Repository Methods Signature

```python
class CategoriaRepository(BaseRepository[Categoria]):
    """
    Methods:
    - find(id) → Optional[Categoria]  [inherited from BaseRepository]
    - list_all(...) → tuple[List[Categoria], int]  [inherited]
    - create(obj) → Categoria  [inherited]
    - update(id, data) → Optional[Categoria]  [inherited]
    - soft_delete(id) → Optional[Categoria]  [inherited]
    - exists(id) → bool  [inherited]
    
    New methods:
    """
    
    async def get_tree(self) -> List[Dict]:
        """
        Fetch all root categories with their descendants in nested structure.
        Uses recursive CTE for performance.
        
        Returns:
            List of dicts with keys: id, nombre, parent_id, subcategorias[]
        
        Raises:
            DatabaseError: If CTE query fails
        """
        pass
    
    async def validate_no_cycle(self, parent_id: int, depth_limit: int = 20) -> bool:
        """
        Check if setting parent_id creates a cycle.
        Traverses from parent_id up the tree; fails if depth > depth_limit.
        
        Args:
            parent_id: The proposed parent_id to validate
            depth_limit: Maximum tree depth allowed (default 20)
        
        Returns:
            True if valid (no cycle), False otherwise
        
        Raises:
            ValidationError: If cycle detected or depth limit exceeded
        """
        pass
    
    async def count_children(self, categoria_id: int) -> int:
        """Count direct children of a category (non-soft-deleted)."""
        pass
    
    async def count_products(self, categoria_id: int) -> int:
        """Count products in this category (for delete validation)."""
        pass
    
    async def has_descendants(self, categoria_id: int) -> bool:
        """Check if category has any descendants (recursive)."""
        pass
```

### 4. Service Methods Signature

```python
class CategoriaService:
    """Business logic for categoria management."""
    
    async def create_categoria(
        self,
        uow: UnitOfWork,
        nombre: str,
        parent_id: Optional[int] = None,
    ) -> CategoriaRead:
        """
        Create a new category with validation.
        
        Args:
            uow: Active UnitOfWork
            nombre: Category name
            parent_id: Parent category ID (None for root)
        
        Returns:
            CategoriaRead with created category
        
        Raises:
            ValidationError: If parent doesn't exist, or self-ref, or cycle
            NotFoundError: If parent_id specified but doesn't exist
        """
        pass
    
    async def update_categoria(
        self,
        uow: UnitOfWork,
        categoria_id: int,
        update_data: CategoriaUpdate,
    ) -> CategoriaRead:
        """
        Update category name and/or parent with cycle detection.
        
        Raises:
            NotFoundError: If categoria not found
            ValidationError: If cycle detected or self-ref
        """
        pass
    
    async def delete_categoria(
        self,
        uow: UnitOfWork,
        categoria_id: int,
    ) -> None:
        """
        Soft-delete a category with constraints.
        
        Raises:
            NotFoundError: If categoria not found
            ValidationError: If category has children or products
        """
        pass
    
    async def get_by_id(
        self,
        uow: UnitOfWork,
        categoria_id: int,
    ) -> CategoriaRead:
        """Fetch single category by ID (non-soft-deleted only)."""
        pass
    
    async def list_tree(
        self,
        uow: UnitOfWork,
    ) -> List[CategoriaTree]:
        """Fetch full category tree (all root categories with descendants)."""
        pass
```

### 5. Router Endpoints

```python
@router.post(
    "",
    response_model=CategoriaRead,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"description": "Self-reference or invalid parent"},
        422: {"description": "Cycle detected or validation error"},
        403: {"description": "Insufficient permissions"},
    }
)
async def create_categoria(
    request: CategoriaCreate,
    uow: UnitOfWork = Depends(get_uow),
    _: None = Depends(require_role(["ADMIN", "STOCK"])),
):
    """Create a new category (Admin/Stock only)."""
    pass

@router.get("", response_model=List[CategoriaTree])
async def list_tree(
    uow: UnitOfWork = Depends(get_uow),
):
    """Fetch all categories as nested tree (public)."""
    pass

@router.get("/{id}", response_model=CategoriaRead)
async def get_categoria(
    id: int,
    uow: UnitOfWork = Depends(get_uow),
):
    """Fetch single category by ID (public)."""
    pass

@router.put("/{id}", response_model=CategoriaRead)
async def update_categoria(
    id: int,
    request: CategoriaUpdate,
    uow: UnitOfWork = Depends(get_uow),
    _: None = Depends(require_role(["ADMIN", "STOCK"])),
):
    """Update category (Admin/Stock only)."""
    pass

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_categoria(
    id: int,
    uow: UnitOfWork = Depends(get_uow),
    _: None = Depends(require_role(["ADMIN"])),
):
    """Soft-delete category (Admin only). Validates no children/products."""
    pass
```

---

## Testing Strategy

| Layer | What | Approach |
|-------|------|----------|
| **Unit: Validation** | Self-ref prevention, cycle detection | Isolated tests of `CategoriaService` methods; mock repository with test data |
| **Unit: Repository** | CTE query correctness | Direct SQL tests against test database; verify nested structure, depth limits |
| **Integration: CRUD** | All 5 endpoints via AsyncClient | Full request/response cycle; verify status codes, error messages |
| **Integration: Soft-delete** | Query filters `deleted_at IS NULL` | Create, delete, verify GET returns 404; verify count excludes soft-deleted |
| **Integration: Constraints** | No products/children deletion | Create category, add products (mock), attempt DELETE → expect 400 |
| **Integration: RBAC** | Role-based access | Unauthenticated → 401; CLIENT role → 403; ADMIN → 200 |
| **Integration: Cycles** | Cycle detection end-to-end | Create A, B, C with A→B→C; try C.parent=A → expect 422 |

**Test file**: `backend/tests/integration/test_categorias_api.py`

Example test structure:
```python
@pytest.mark.asyncio
class TestCategoriasAPI:
    async def test_create_root_categoria(self, admin_token, async_client, uow):
        """POST / without parent_id creates root category."""
        response = await async_client.post(
            "/api/v1/categorias",
            json={"nombre": "Comidas", "parent_id": None},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 201
        assert response.json()["nombre"] == "Comidas"
    
    async def test_cycle_detection(self, admin_token, async_client, uow):
        """Attempting A→B→C→A returns 422."""
        # Create chain, then try to create cycle
        pass
    
    async def test_soft_delete_with_children(self, admin_token, async_client, uow):
        """DELETE category with children returns 400."""
        pass
    
    async def test_self_reference(self, admin_token, async_client, uow):
        """POST with parent_id=id returns 400."""
        pass
```

---

## Migration / Rollout

### Migration: `004_add_categorias_table.py`

```python
def upgrade() -> None:
    """Create Categoria table with self-referential FK and seed root."""
    op.create_table(
        "categorias",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("nombre", sa.String(100), nullable=False),
        sa.Column("parent_id", sa.Integer, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["parent_id"], ["categorias.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_categorias_parent_id", "categorias", ["parent_id"])
    
    # Seed root categories (e.g., for Food Store)
    op.execute(
        "INSERT INTO categorias (nombre, parent_id, created_at, updated_at) "
        "VALUES ('Comidas', NULL, NOW(), NOW())"
    )

def downgrade() -> None:
    """Drop Categoria table."""
    op.drop_table("categorias")
```

### Seed Data
Root categories are seeded at migration time:
- `Comidas` (root)
- Can be extended in UI during setup

### Rollback Plan
1. **Alembic downgrade**: `alembic downgrade -1` removes table
2. **Code removal**: Delete `backend/app/modules/categorias/`
3. **Router cleanup**: Remove import + `app.include_router()` from `main.py`
4. **UoW cleanup**: Remove `categorias` property from `UnitOfWork`
5. **Verification**: Seed script confirms roles/states intact

---

## Open Questions

- [ ] **Product deletion policy**: When a product is deleted (soft or hard), should its category be cleaned up? → Decision: Categories survive product deletion. Categories are only deleted explicitly.
- [ ] **Depth limit tuning**: Is 20 the right default for max tree depth? → Proposal: Start with 20, monitor in v2 with telemetry.
- [ ] **CTE performance caching**: Should GET /tree be cached with Redis? → Out-of-scope for v1; implement in v2 with cache invalidation on write.
- [ ] **Bulk operations**: Should we support batch create/delete categories? → Out-of-scope; single operations only for v1.

---

## Architecture Compliance Checklist

- ✅ Router → Service → UoW → Repository → Model (strict layering)
- ✅ Async/await throughout (no sync DB calls)
- ✅ BaseRepository inheritance for generic CRUD
- ✅ SoftDeleteMixin reuse (no duplicate deleted_at logic)
- ✅ UnitOfWork transaction management (commit/rollback)
- ✅ RBAC via `require_role` dependency
- ✅ Pydantic validation on input
- ✅ RFC 7807 error responses (via `AppException` handler)
- ✅ Alembic migrations for schema versioning
- ✅ Integration tests with AsyncClient
- ✅ SQLModel + PostgreSQL as per stack

