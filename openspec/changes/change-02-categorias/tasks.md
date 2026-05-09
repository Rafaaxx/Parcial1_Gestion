# Tasks: Categorías Jerárquicas (change-02-categorias)

## Phase 1: Foundation / Infrastructure

- [x] 1.1 Create Alembic migration `004_add_categorias_table.py` — table with `id` (PK), `nombre` (VARCHAR 100), `parent_id` (nullable FK self-ref), timestamps via `BaseModel`, soft-delete `deleted_at`, indexes on `parent_id` and `(parent_id, deleted_at)` for CTE efficiency
- [x] 1.2 Create `backend/app/models/categoria.py` — SQLModel `Categoria(BaseModel, table=True)` with relationships: `parent: Optional[Categoria]`, `children: List[Categoria]` (back_populates, cascade delete), inherits `created_at, updated_at, deleted_at` from `BaseModel`
- [x] 1.3 Create `backend/app/modules/categorias/schemas.py` — Pydantic models: `CategoriaCreate`, `CategoriaUpdate`, `CategoriaRead`, `CategoriaTree` (nested with `subcategorias: List[CategoriaTree]`)
- [x] 1.4 Create `backend/app/repositories/categoria_repository.py` — extend `BaseRepository[Categoria]` with methods: `get_tree()`, `validate_no_cycle()`, `count_children()`, `count_descendants()`, `has_descendants()`, `get_all_descendants_ids()` (all async, docstrings with type hints)
- [x] 1.5 Update `backend/app/uow.py` — add `@property def categorias(self) -> CategoriaRepository` lazy-loading property and import CategoriaRepository

## Phase 2: Core Business Logic (TDD Red-Green-Refactor)

### Sub-Phase 2a: Cycle Detection & Validation (RED-GREEN-REFACTOR)

- [x] 2.1 **RED** — Create `backend/tests/unit/test_categoria_service.py` with failing tests: `test_create_categoria_validates_cycle_detection` (mock repo, assert cycle detection raises `ValidationError`), `test_create_categoria_rejects_self_reference` (assert parent_id != id), `test_update_categoria_prevents_cycle` (assert cycle prevention on update)
- [x] 2.2 **GREEN** — Implement `backend/app/modules/categorias/service.py` — `CategoriaService` class with methods: `create_categoria()`, `update_categoria()`, `delete_categoria()`, `get_by_id()`, `list_tree()` (all async); include cycle detection logic (call `repo.validate_no_cycle()`) and self-ref check (`if parent_id == categoria_id`)
- [x] 2.3 **REFACTOR** — Extract cycle detection logic to separate `_check_cycle_and_self_ref()` function, add comprehensive docstrings explaining business rules (cycle depth limit 20, soft-delete behavior), add type hints to all parameters/returns

### Sub-Phase 2b: Router Endpoints (TDD Red-Green-Refactor)

- [x] 2.4 **RED** — Create `backend/tests/unit/test_router_categorias.py` with failing tests: `test_post_categorias_requires_admin_role` (unauthenticated → 401, CLIENT role → 403, ADMIN → 201), `test_delete_categorias_admin_only` (STOCK role → 403), `test_post_rejects_invalid_schema` (missing `nombre` → 422)
- [x] 2.5 **GREEN** — Create `backend/app/modules/categorias/router.py` — FastAPI router with 5 endpoints:
  - `POST ""` — create (status 201, requires ADMIN/STOCK)
  - `GET ""` — list tree (status 200, public)
  - `GET "/{id}"` — get single (status 200, public)
  - `PUT "/{id}"` — update (status 200, requires ADMIN/STOCK)
  - `DELETE "/{id}"` — soft-delete (status 204, requires ADMIN)
  - Use `Depends(get_uow)`, `Depends(require_role(...))`, proper response models
- [x] 2.6 Create `backend/app/modules/categorias/__init__.py` — empty package init (for clean imports)
- [x] 2.7 Update `backend/app/main.py` — import `router` from `modules.categorias` and register at `app.include_router(router, prefix="/api/v1/categorias", tags=["categorias"])`

## Phase 3: Integration Testing & Validation

- [ ] 3.1 **RED** — Create `backend/tests/integration/test_categorias_api.py` with failing integration tests (AsyncClient, pytest fixtures):
  - `test_post_creates_root_categoria` — POST without parent_id → 201, verify response
  - `test_post_creates_subcategoria` — POST with valid parent_id → 201, verify parent_id
  - `test_get_tree_returns_nested_structure` — GET / → 200, verify nested subcategorias array
  - `test_get_by_id_single_category` — GET /{id} → 200, verify single response
  - `test_put_updates_category` — PUT /{id} with new name → 200, verify updated
  - `test_delete_soft_deletes_category` — DELETE /{id} → 204, then GET /{id} → 404
  - `test_delete_with_children_returns_conflict` — POST child, try DELETE parent → 409
  - `test_cycle_detection_rejects_cycle` — Create A→B→C, try C.parent=A → 422
  - `test_self_reference_rejected` — POST with parent_id=id → 400
  - `test_unauthorized_returns_401` — GET / without token → 401
  - `test_forbidden_client_role_post` — POST with CLIENT role → 403
- [ ] 3.2 **GREEN** — Run `pytest backend/tests/integration/test_categorias_api.py -v` → all tests pass (implement any missing fixtures or mock UoW if needed)
- [ ] 3.3 Verify soft-delete behavior: POST category, DELETE via API, query DB raw SQL `SELECT * FROM categorias WHERE id=X` → verify `deleted_at IS NOT NULL`, then `SELECT * FROM categorias WHERE parent_id=X AND deleted_at IS NULL` in GET tree → verify excluded
- [ ] 3.4 Verify RBAC: Create test with CLIENTE role token, attempt POST → assert 403 Forbidden, assert response includes error detail
- [ ] 3.5 Verify cycle detection: Create categories A (parent=None), B (parent=A), C (parent=B), attempt PUT C with parent_id=A → assert 422 Unprocessable Entity with cycle error message
- [ ] 3.6 Verify cascade validation: Create category with children (via multiple POSTs), attempt DELETE parent → assert 409 Conflict with message "Cannot delete category with children"

## Phase 4: Documentation & Verification

- [ ] 4.1 Swagger verification: Start dev server `uvicorn app.main:app --reload`, visit `http://localhost:8000/docs` → verify 5 endpoints under `/api/v1/categorias` tag, verify request/response schemas shown, verify 403/422 error responses documented
- [ ] 4.2 Add docstrings to all service methods: `create_categoria()`, `update_categoria()`, `delete_categoria()`, `get_by_id()`, `list_tree()` — explain business logic (cycle detection depth=20, soft-delete filters, RBAC roles)
- [ ] 4.3 Add docstrings to all repository methods: `get_tree()`, `validate_no_cycle()`, `count_children()`, `count_products()`, `has_descendants()` — include CTE query explanation, parameters, return types
- [ ] 4.4 Update `docs/Integrador.txt` (if section exists) — add note about `categorias` module: "Categories use self-referential FK, recursive CTE queries for tree, soft-delete pattern, depth limit 20"
- [ ] 4.5 Seed root categories: Via Alembic migration or management script — ensure root category (e.g., "Comidas") exists in DB after first run for manual testing

---

## Implementation Order & Rationale

**Strict Dependency Chain** (tasks must run in this order):

1. **Phase 1** (1.1-1.5): Infrastructure first — models, schemas, repo, UoW binding. Other tasks depend on these types existing.
   - 1.1 (migration) can be written but not run yet
   - 1.2-1.5 define contracts (types, schemas, repo interface)

2. **Phase 2a** (2.1-2.3): Test-drive cycle detection logic (RED-GREEN-REFACTOR)
   - Tests mock the repository, so they run independently of Phase 1
   - Forces clear business logic separation before router layer

3. **Phase 2b** (2.4-2.7): Test-drive router layer (RED-GREEN-REFACTOR)
   - Tests mock UoW, so they also run independently
   - Forces RBAC, schema validation, HTTP contract before integration

4. **Phase 3** (3.1-3.6): Integration tests — run against real DB with alembic migration (1.1 must be applied)
   - These tests orchestrate the full stack: migration + model + repo + service + router
   - Validates end-to-end workflows: tree nesting, soft-delete, cycle detection, RBAC

5. **Phase 4** (4.1-4.5): Documentation & verification
   - Assumes all tests pass and server is running
   - Swagger docs auto-generated from router docstrings
   - Seed data validates schema assumptions

---

## TDD Discipline Checkpoints

✅ **Phase 2a (Service Logic)**:
- Test code written BEFORE service.py implementation
- Tests mock repository → service logic tested in isolation
- All assertions on cycle detection, self-ref, validation errors

✅ **Phase 2b (Router Layer)**:
- Test code written BEFORE router.py implementation
- Tests mock UoW → router layer tested in isolation
- All assertions on HTTP status, RBAC, error responses, schema

✅ **Phase 3 (Integration)**:
- Tests run against real DB (migration applied)
- All 5 endpoints tested with AsyncClient
- Soft-delete behavior, cascade validation, CTE correctness verified

✅ **No Task Exceeds 1 Hour**:
- Individual tasks (1.1, 1.2, etc.) map to single file/feature
- Refactor tasks explicit (2.3, 4.2, 4.3)
- Verification tasks concrete (3.1, 3.3, 3.5)

---

## Success Criteria (Automatic Checklist)

- [ ] All Phase 1 tasks complete: migration exists, models/schemas defined, repo interface defined
- [ ] All Phase 2 tests pass: unit tests for service (2.1-2.3) and router (2.4-2.5)
- [ ] All Phase 3 integration tests pass: `pytest backend/tests/integration/test_categorias_api.py -v`
- [ ] Swagger `/docs` shows 5 endpoints with correct schemas (4.1)
- [ ] Database query verified: `SELECT COUNT(*) FROM categorias WHERE deleted_at IS NULL` > 0 after seed (4.5)
- [ ] Cycle detection confirmed: Attempt cycle via API → 422 error with message (3.5)
- [ ] RBAC enforced: Unauthenticated POST → 401, CLIENT POST → 403, ADMIN POST → 201 (3.4)
