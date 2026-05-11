# Tasks: CHANGE-04 — Ingredientes y Alérgenos

Implementation checklist for ingredient and allergen management system.

---

## 1. Database Schema & Migrations

- [x] 1.1 Create SQLModel Ingrediente model with fields: id, nombre, es_alergeno, creado_en, actualizado_en, eliminado_en
- [x] 1.2 Add unique constraint on nombre WHERE eliminado_en IS NULL in database
- [x] 1.3 Create Alembic migration: `alembic revision --autogenerate -m "add ingrediente table"`
- [x] 1.4 Test migration up/down cycle (migrate up, verify table exists; migrate down, verify table removed)
- [x] 1.5 Add indices on `nombre` and `es_alergeno` for query performance

---

## 2. Backend Model & Schemas

- [x] 2.1 Create `backend/app/ingredientes/model.py` with SQLModel Ingrediente
- [x] 2.2 Create `backend/app/ingredientes/schemas.py` with Pydantic:
  - [x] 2.2a IngredienteCreate (nombre, es_alergeno)
  - [x] 2.2b IngredienteUpdate (nombre optional, es_alergeno optional)
  - [x] 2.2c IngredienteRead (all fields + timestamps)
  - [x] 2.2d IngredienteListResponse (items[], total, skip, limit)
- [x] 2.3 Validate schema field constraints (non-empty nombre, boolean es_alergeno, max lengths)
- [x] 2.4 Add Pydantic validators for whitespace trimming and type coercion

---

## 3. Backend Repository

- [x] 3.1 Create `backend/app/ingredientes/repository.py` extending BaseRepository[Ingrediente]
- [x] 3.2 Implement custom method: `find_by_nombre(nombre: str)` with soft delete filter
- [x] 3.3 Implement custom method: `list_by_allergen(es_alergeno: bool)` with soft delete filter
- [x] 3.4 Implement custom method: `soft_delete(id: int)` that sets eliminado_en timestamp
- [x] 3.5 Add database query tests for each repository method (using pytest + in-memory SQLite)

---

## 4. Backend Service

- [x] 4.1 Create `backend/app/ingredientes/service.py` with IngredienteService class
- [x] 4.2 Implement `create_ingrediente(data: IngredienteCreate)`:
  - [x] 4.2a Validate nombre is unique (check both DB and existing non-deleted)
  - [x] 4.2b Raise 409 Conflict if duplicate
  - [x] 4.2c Create and return IngredienteRead response
- [x] 4.3 Implement `list_ingredientes(skip: int, limit: int, es_alergeno: Optional[bool])`:
  - [x] 4.3a Filter by soft delete (eliminado_en IS NULL)
  - [x] 4.3b Apply es_alergeno filter if provided
  - [x] 4.3c Return paginated response with total count
- [x] 4.4 Implement `get_ingrediente_by_id(id: int)`:
  - [x] 4.4a Return IngredienteRead or raise 404
  - [x] 4.4b Exclude soft-deleted
- [x] 4.5 Implement `update_ingrediente(id: int, data: IngredienteUpdate)`:
  - [x] 4.5a Raise 404 if soft-deleted
  - [x] 4.5b Validate unique nombre if updating
  - [x] 4.5c Update actualizado_en timestamp
- [x] 4.6 Implement `delete_ingrediente(id: int)`:
  - [x] 4.6a Raise 404 if not found or already deleted
  - [x] 4.6b Call repository.soft_delete()
- [x] 4.7 Add unit tests for each service method (cover happy path + error cases)

---

## 5. Backend Router

- [x] 5.1 Create `backend/app/ingredientes/router.py` with FastAPI APIRouter
- [x] 5.2 Implement POST `/api/v1/ingredientes`:
  - [x] 5.2a Require role STOCK or ADMIN via `require_role(["STOCK", "ADMIN"])`
  - [x] 5.2b Call service.create_ingrediente
  - [x] 5.2c Return 201 Created with Location header
  - [x] 5.2d Handle validation errors (422) and conflict (409)
- [x] 5.3 Implement GET `/api/v1/ingredientes`:
  - [x] 5.3a No auth required
  - [x] 5.3b Support query params: skip, limit, es_alergeno
  - [x] 5.3c Call service.list_ingredientes
  - [x] 5.3d Return 200 with IngredienteListResponse
- [x] 5.4 Implement GET `/api/v1/ingredientes/{id}`:
  - [x] 5.4a No auth required
  - [x] 5.4b Call service.get_ingrediente_by_id
  - [x] 5.4c Return 200 with IngredienteRead or 404
- [x] 5.5 Implement PUT `/api/v1/ingredientes/{id}`:
  - [x] 5.5a Require role STOCK or ADMIN
  - [x] 5.5b Call service.update_ingrediente
  - [x] 5.5c Return 200 with updated IngredienteRead or 404/409
- [x] 5.6 Implement DELETE `/api/v1/ingredientes/{id}`:
  - [x] 5.6a Require role STOCK or ADMIN
  - [x] 5.6b Call service.delete_ingrediente
  - [x] 5.6c Return 204 No Content or 404
- [x] 5.7 Register router in main app: `app.include_router(router, prefix="/api/v1")`
- [x] 5.8 Verify endpoints in Swagger UI at `/docs`

---

## 6. Backend Integration Tests

- [x] 6.1 Create `backend/tests/test_ingredientes.py` with test fixtures
- [x] 6.2 Test POST /api/v1/ingredientes:
  - [x] 6.2a Successful creation returns 201
  - [x] 6.2b Duplicate name returns 409
  - [x] 6.2c Missing fields returns 422
  - [x] 6.2d Unauthorized role returns 403
- [x] 6.3 Test GET /api/v1/ingredientes:
  - [x] 6.3a List returns 200 with items and total
  - [x] 6.3b Pagination works correctly
  - [x] 6.3c Filter by es_alergeno=true returns only allergens
  - [x] 6.3d Soft-deleted ingredients excluded
- [x] 6.4 Test GET /api/v1/ingredientes/{id}:
  - [x] 6.4a Existing ingredient returns 200
  - [x] 6.4b Non-existent returns 404
  - [x] 6.4c Soft-deleted returns 404
- [x] 6.5 Test PUT /api/v1/ingredientes/{id}:
  - [x] 6.5a Successful update returns 200
  - [x] 6.5b Duplicate name returns 409
  - [x] 6.5c Non-existent returns 404
  - [x] 6.5d Unauthorized returns 403
- [x] 6.6 Test DELETE /api/v1/ingredientes/{id}:
  - [x] 6.6a Successful soft delete returns 204
  - [x] 6.6b Deleted ingredient no longer appears in list
  - [x] 6.6c Non-existent returns 404
  - [x] 6.6d Unauthorized returns 403
- [x] 6.7 Run full test suite: `pytest backend/tests/test_ingredientes.py -v --cov`

---

## 7. Frontend Types & API Layer

- [x] 7.1 Create `frontend/src/entities/ingrediente/types.ts`:
  - [x] 7.1a IngredienteRead interface
  - [x] 7.1b IngredienteCreate interface
  - [x] 7.1c IngredienteUpdate interface
  - [x] 7.1d IngredienteListResponse interface
- [x] 7.2 Create `frontend/src/entities/ingrediente/api.ts`:
  - [x] 7.2a Function: `fetchIngredientes(skip, limit, esAlergeno)`
  - [x] 7.2b Function: `fetchIngredienteById(id)`
  - [x] 7.2c Function: `createIngrediente(data)`
  - [x] 7.2d Function: `updateIngrediente(id, data)`
  - [x] 7.2e Function: `deleteIngrediente(id)`
  - [x] 7.2f Use Axios instance with JWT auth for POST/PUT/DELETE
- [x] 7.3 Verify API functions work with mock Axios (no real backend calls yet)

---

## 8. Frontend TanStack Query Hooks

- [x] 8.1 Create `frontend/src/entities/ingrediente/hooks.ts`:
  - [x] 8.1a `useIngredientes(skip, limit, esAlergeno)` → useQuery
  - [x] 8.1b `useIngredienteDetail(id)` → useQuery
  - [x] 8.1c `useCreateIngrediente()` → useMutation + invalidateQueries
  - [x] 8.1d `useUpdateIngrediente(id)` → useMutation + invalidateQueries
  - [x] 8.1e `useDeleteIngrediente(id)` → useMutation + invalidateQueries
- [x] 8.2 Test hooks with mock TanStack Query client (no real API calls)

---

## 9. Frontend Components

- [x] 9.1 Create `frontend/src/features/ingredientes/ui/IngredientList.tsx`:
  - [x] 9.1a Display table of ingredients
  - [x] 9.1b Show columns: nombre, es_alergeno (with badge), creado_en
  - [x] 9.1c Pagination controls (skip, limit)
  - [x] 9.1d Edit/Delete buttons for each row (only if STOCK/ADMIN role)
  - [x] 9.1e Filter toggle for allergens only
  - [x] 9.1f Loading/error states
- [x] 9.2 Create `frontend/src/features/ingredientes/ui/CreateIngredientModal.tsx`:
  - [x] 9.2a Form fields: nombre, es_alergeno checkbox
  - [x] 9.2b Submit button calls useCreateIngrediente()
  - [x] 9.2c Success: close modal, refetch list
  - [x] 9.2d Error: display error message
- [x] 9.3 Create `frontend/src/features/ingredientes/ui/EditIngredientModal.tsx`:
  - [x] 9.3a Pre-populate form with ingredient data
  - [x] 9.3b Submit button calls useUpdateIngrediente()
  - [x] 9.3c Success: close modal, refetch list
  - [x] 9.3d Error: display error message
- [x] 9.4 Create `frontend/src/features/ingredientes/ui/DeleteConfirmModal.tsx`:
  - [x] 9.4a Confirmation text: "Are you sure?"
  - [x] 9.4b Delete button calls useDeleteIngrediente()
  - [x] 9.4c Success: close modal, refetch list
  - [x] 9.4d Error: display error message

---

## 10. Frontend Navigation & RBAC

- [x] 10.1 Add "Ingredientes" link to admin sidebar (only visible for STOCK/ADMIN roles)
- [x] 10.2 Create route `/admin/ingredientes` pointing to IngredientList component
- [x] 10.3 Wrap route with ProtectedRoute HOC requiring role [STOCK, ADMIN]
- [x] 10.4 Test navigation: CLIENT role should not see link; STOCK role should see it

---

## 11. Frontend Testing

- [x] 11.1 Create `frontend/src/features/ingredientes/__tests__/IngredientList.test.tsx`:
    - [x] 11.1a Render list of ingredients from mock data
    - [x] 11.1b Loading state displays spinner
    - [x] 11.1c Error state displays error message
    - [x] 11.1d Edit button opens EditIngredientModal
    - [x] 11.1e Delete button opens DeleteConfirmModal
- [x] 11.2 Create `frontend/src/features/ingredientes/__tests__/CreateIngredientModal.test.tsx`:
    - [x] 11.2a Form submission validates non-empty nombre
    - [x] 11.2b Submit button disabled during mutation
    - [x] 11.2c Success closes modal and shows toast
    - [x] 11.2d Error displays error message
- [x] 11.3 Create `frontend/src/features/ingredientes/__tests__/EditIngredientModal.test.tsx`:
    - [x] 11.3a Form pre-populates with ingredient data
    - [x] 11.3b Submit button updates ingredient
    - [x] 11.3c Success closes modal and refetches
- [x] 11.4 Create `frontend/src/features/ingredientes/__tests__/DeleteConfirmModal.test.tsx`:
    - [x] 11.4a Delete button calls delete mutation
    - [x] 11.4b Success closes modal and refetches
- [x] 11.5 Run frontend tests: `npm run test frontend/src/features/ingredientes`

---

## 12. End-to-End Testing

- [x] 12.1 Manual E2E: Stock manager creates ingredient "Gluten" (es_alergeno=true)
    - [x] 12.1a Verify ingredient appears in list
    - [x] 12.1b Verify ingredient appears in allergen filter
    - [x] 12.1c Verify ingredient details show correct data
- [x] 12.2 Manual E2E: Edit ingredient name from "Gluten" to "Trigo"
    - [x] 12.2a Verify list shows updated name
    - [x] 12.2b Verify actualizado_en timestamp updated
- [x] 12.3 Manual E2E: Delete ingredient
    - [x] 12.3a Verify ingredient no longer appears in list
    - [x] 12.3b Verify GET /api/v1/ingredientes/{id} returns 404
    - [x] 12.3c Verify database: eliminado_en is set (not physically deleted)
- [x] 12.4 Manual E2E: CLIENT role cannot create/edit/delete (403 responses)

---

## 13. Code Quality & Documentation

- [x] 13.1 Run backend linters: `black backend/app/ingredientes`, `flake8 backend/app/ingredientes`, `mypy backend/app/ingredientes`
- [x] 13.2 Run frontend linters: `eslint frontend/src/features/ingredientes`, `prettier --check frontend/src/features/ingredientes`
- [x] 13.3 Add docstrings to service methods (summary + param + return types)
- [x] 13.4 Add comments for non-obvious logic (e.g., soft delete filter)
- [x] 13.5 Update `backend/README.md` with ingredient module documentation

---

## 14. Final Verification & Merge

- [x] 14.1 Verify all tests pass: `pytest backend/tests/test_ingredientes.py` + `npm run test frontend`
- [x] 14.2 Verify Swagger UI shows all 5 endpoints correctly
- [x] 14.3 Git status clean (all changes staged/committed)
- [x] 14.4 Create conventional commits:
    - [x] 14.4a `feat(db): add ingrediente table migration`
    - [x] 14.4b `feat(ingredientes): implement CRUD service + router`
    - [x] 14.4c `feat(ingredientes): add TanStack Query hooks`
    - [x] 14.4d `feat(ingredientes): add React components`
    - [x] 14.4e `test(ingredientes): add integration + unit tests`
- [ ] 14.5 Create pull request with link to change-04 design/specs
- [ ] 14.6 Code review: verify against design decisions, check RBAC, validate soft delete behavior
- [ ] 14.7 Merge to main once approved

---

**Estimated Duration**: ~8 hours  
**Dependencies**: CHANGE-00 (completed), CHANGE-01 (completed), CHANGE-03 (completed)  
**Blocks**: CHANGE-06 (Productos CRUD y Stock)
