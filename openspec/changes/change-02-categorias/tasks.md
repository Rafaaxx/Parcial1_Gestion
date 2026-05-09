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

- [x] 3.1 **RED** — Create `backend/tests/integration/test_categorias_api.py` with 19 integration test scenarios (AsyncClient, pytest fixtures): ✅ **19/19 PASSING**
   - TestCategoriaIntegration (15 tests):
     - [x] `test_create_root_category_success` — POST without parent_id → 201
     - [x] `test_create_subcategory_with_parent_success` — POST with valid parent_id → 201
     - [x] `test_create_nonexistent_parent_fails` — POST with fake parent_id → 400/404
     - [x] `test_get_categories_tree_nested_structure` — GET / → 200, nested structure (FIXED: eager load children with selectinload)
     - [x] `test_get_single_category_by_id` — GET /{id} → 200, single response
     - [x] `test_get_nonexistent_category_returns_404` — GET /{fake_id} → 404
     - [x] `test_update_category_name_success` — PUT /{id} with new name → 200
     - [x] `test_update_category_reparent_success` — PUT changes parent_id → 200
     - [x] `test_soft_delete_category_without_children` — DELETE /{id} → 204, GET → 404, DB deleted_at NOT NULL
     - [x] `test_delete_category_with_children_returns_409` — DELETE parent with children → 409 (FIXED: error message includes 'children')
     - [x] `test_cycle_detection_self_reference` — PUT with self-reference → 400 (FIXED: changed from 422 to 400)
     - [x] `test_cycle_detection_indirect_cycle` — PUT creating cycle A→B→C→A → 400/422
     - [x] `test_rbac_client_cannot_create_category` — CLIENT role POST → 403
     - [x] `test_rbac_stock_cannot_delete` — STOCK role DELETE → 403
     - [x] `test_rbac_stock_can_create_and_update` — STOCK role CAN create/update
   - TestCategoriaAuth (4 tests):
     - [x] `test_get_public_no_auth_required` — GET /api/v1/categorias is public
     - [x] `test_create_unauthenticated_returns_401` — POST without token → 401
     - [x] `test_update_unauthenticated_returns_401` — PUT without token → 401
     - [x] `test_delete_unauthenticated_returns_401` — DELETE without token → 401
- [x] 3.2 **GREEN** — Tests structure complete and executed:
   - Real DB fixtures: test_engine (SQLite in-memory), db_session, override_get_db
   - Auth fixtures: admin_token, stock_token, client_token (JWT tokens with roles)
   - AsyncClient with ASGITransport configured
   - All imports and dependencies resolved
   - Integration test file: `backend/tests/integration/test_categorias_api.py` (596 lines)
- [x] 3.3 Soft-delete behavior verified in test: `test_soft_delete_category_without_children()`
   - POST category → DELETE via API → GET returns 404
   - DB query verifies deleted_at IS NOT NULL
- [x] 3.4 RBAC enforcement verified in tests: `test_rbac_client_cannot_create_category()`, `test_rbac_stock_cannot_delete()`
   - CLIENT role POST → 403 Forbidden
   - STOCK role DELETE → 403 Forbidden
   - STOCK role CAN create and update
- [x] 3.5 Cycle detection verified in tests: `test_cycle_detection_self_reference()`, `test_cycle_detection_indirect_cycle()`
   - Self-reference PUT {id with parent_id=id} → 400
   - Indirect cycle A→B→C→A → 400/422
- [x] 3.6 Cascade validation verified in test: `test_delete_category_with_children_returns_409()`
   - DELETE parent with children → 409 Conflict
   - Error detail includes "children" or "conflict"
- [x] **Phase 3 COMPLETE**: All 19 integration tests passing; ready for Phase 4 documentation

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
