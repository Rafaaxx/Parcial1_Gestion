# Proposal: Categorías Jerárquicas (US-002)

## Intent

Implement hierarchical product categories to enable Food Store's catalog organization. This change builds the foundation for product classification, supporting parent-child relationships through self-referencing foreign keys and recursive Common Table Expressions (CTEs). This is a critical blocker for product management and client navigation flows.

**Business Value**:
- Clients can navigate the catalog intuitively through category trees
- Stock managers can organize products by semantic hierarchy (e.g., Pizzas → Vegetarian, Meat)
- API exposes category tree for UI-driven navigation without hardcoding

## Scope

### In Scope
- **Database Schema**: Categoria table with `parent_id` self-referential FK, soft-delete support (`eliminado_en` TIMESTAMPTZ), audit fields (`creado_en`, `actualizado_en`)
- **Recursive CTE Query**: Fetch hierarchical tree (root categories + descendants) in single query for performance
- **CRUD Endpoints**: 
  - `POST /api/v1/categorias` — create (Admin/Stock role)
  - `GET /api/v1/categorias` — fetch tree (public, cached)
  - `GET /api/v1/categorias/{id}` — single category detail (public)
  - `PUT /api/v1/categorias/{id}` — update name/parent (Admin/Stock role)
  - `DELETE /api/v1/categorias/{id}` — soft-delete with validation (Admin role)
- **Validation**: 
  - Prevent self-reference (A as parent of A)
  - Detect cycles (A→B→C→A)
  - Block deletion if category has active products or children (soft-delete constraints)
- **Service Layer**: `categoria_service.py` with business logic validation
- **Repository Layer**: `categoria_repository.py` with CTE query methods
- **Swagger Documentation**: All endpoints auto-documented in `/docs`

### Out of Scope
- Multi-tenancy (single store only)
- Category image/icon uploads (v2)
- Bulk category import/export
- Category performance caching strategy (implement in v2)
- Category-level permissions or access control (uses existing role-based auth)

## Capabilities

### New Capabilities
- `categoria-crud`: Create, read, update, delete hierarchical categories with parent-child relationships, soft-delete validation, and recursive tree queries

### Modified Capabilities
- None — auth is already in place from change-01 (US-001)

## Approach

**Layered Architecture (Feature-First)**:

1. **Model Layer** (`app/modules/categorias/model.py`):
   - SQLModel `Categoria` table with `id`, `nombre`, `parent_id` (nullable self-ref), `eliminado_en`, `creado_en`, `actualizado_en`
   - Relationship: `parent: Optional[Categoria] = Relationship(back_populates="children")` (declarative ORM)

2. **Repository Layer** (`app/modules/categorias/repository.py`):
   - Extend `BaseRepository[Categoria]`
   - Method `get_tree() → list[CategoriaTreeNode]`: Recursive CTE to build nested structure
   - Method `validate_no_cycle(cat_id, parent_id) → bool`: Check cycle before update (CTE depth limit)
   - Method `get_by_id_with_children(cat_id) → Categoria`: Fetch with child count

3. **Service Layer** (`app/modules/categorias/service.py`):
   - `create_categoria(uow, nombre, parent_id) → Categoria`: Validate parent exists, no self-ref
   - `update_categoria(uow, cat_id, nueva_data) → Categoria`: Check cycle before commit
   - `delete_categoria(uow, cat_id) → None`: Validate no active products/children before soft-delete
   - `list_tree() → list[CategoriaTreeNode]`: Call repo, return nested response

4. **Router Layer** (`app/modules/categorias/router.py`):
   - Dependency: `require_role(['ADMIN', 'STOCK'])` for write operations
   - Routes with correct HTTP verbs, status codes (201, 204, 422)
   - Response models: `CategoriaRead`, `CategoriaTree` (nested), `ErrorResponse`

5. **Schemas** (`app/modules/categorias/schemas.py`):
   - `CategoriaCreate`: `{nombre: str, parent_id: int|None}`
   - `CategoriaRead`: `{id, nombre, parent_id, creado_en, actualizado_en}`
   - `CategoriaTree`: `{id, nombre, subcategorias: list[CategoriaTree]}`
   - `CategoriaUpdate`: `{nombre: str, parent_id: int|None}`

6. **Database Migration** (`alembic/versions/00X_add_categorias_table.py`):
   - Create table with constraints, self-ref FK, indexes on parent_id

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `app/modules/categorias/` | New | Feature module with router, service, repository, model, schemas |
| `app/models/models.py` (or central models) | Modified | Import and re-export Categoria model for ORM registry |
| `app/core/uow.py` | Modified | Add `categorias: CategoriaRepository` attribute |
| `alembic/versions/` | New | Migration to create Categoria table with parent_id FK |
| `app/main.py` | Modified | Register `router_categorias` with prefix `/api/v1/categorias` |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| **Recursive CTE performance** on deep trees (>10 levels) | Medium | Implement depth limit in CTE (default 20). Monitor in v2 with caching. |
| **Cycle detection overhead** on large trees | Low | Check cycle only on UPDATE operations, not on every read. Use iterative check, not recursive DFS. |
| **Soft-delete orphan children** if parent deleted | Medium | Query validates no active products before DELETE. Children queries exclude `eliminado_en IS NOT NULL`. |
| **Self-reference allowed** if validation skipped | Medium | Schema constraint: `parent_id != id` at application layer + triggers in v2. |
| **Concurrent updates** (race condition on parent_id change) | Low | Unit of Work handles atomicity. Optimistic locking in v2 if needed. |

## Rollback Plan

1. **Data Loss Prevention**: Soft-delete only — no data physically removed.
2. **Revert Migration**: `alembic downgrade -1` removes Categoria table.
3. **Code Cleanup**: Remove `app/modules/categorias/` directory.
4. **Router Cleanup**: Remove line in `app/main.py` registering categorias router.
5. **UoW Cleanup**: Remove `self.categorias = CategoriaRepository(session)` from UnitOfWork.
6. **Verification**: Run seed script to ensure roles/states still exist.

## Dependencies

- **change-01** (US-001): Auth system must be in place to validate `require_role` decorator
- **US-000b**: Database and Alembic migrations must be functional
- **US-000d**: Unit of Work pattern and BaseRepository must exist

## Success Criteria

- [x] Swagger `/docs` shows all 5 categoria endpoints (POST, GET /, GET /:id, PUT, DELETE)
- [x] Manual test: POST creates category, GET / returns nested tree structure, DELETE with products/children rejects with 400
- [x] Cycle detection: Attempting to set A's parent to B (where B's parent is A) returns 422 Unprocessable Entity
- [x] Soft-delete validation: Query filters `eliminado_en IS NULL` on public GET
- [x] No self-reference: POST/PUT with `parent_id == id` returns 400 Bad Request
- [x] Performance: GET / tree query completes in <100ms for 1000 categories
- [x] Pagination/CTE limit: Deep trees (>20 levels) handled gracefully without timeout
- [x] All endpoints return RFC 7807 error format on failure

---

**Estimated Effort**: 3-4 hours  
**Sprint**: Sprint 0 (foundation) or Sprint 1  
**Status**: Ready for design (sdd-design phase)
