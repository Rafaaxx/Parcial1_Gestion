# Tasks: CHANGE-04 — Ingredientes y Alérgenos

Implementation checklist for ingredient and allergen management system.

---

## 1. Database Schema & Migrations

- [ ] 1.1 Create SQLModel Ingrediente model with fields: id, nombre, es_alergeno, creado_en, actualizado_en, eliminado_en
- [ ] 1.2 Add unique constraint on nombre WHERE eliminado_en IS NULL in database
- [ ] 1.3 Create Alembic migration: `alembic revision --autogenerate -m "add ingrediente table"`
- [ ] 1.4 Test migration up/down cycle (migrate up, verify table exists; migrate down, verify table removed)
- [ ] 1.5 Add indices on `nombre` and `es_alergeno` for query performance

---

## 2. Backend Model & Schemas

- [ ] 2.1 Create `backend/app/ingredientes/model.py` with SQLModel Ingrediente
- [ ] 2.2 Create `backend/app/ingredientes/schemas.py` with Pydantic:
  - [ ] 2.2a IngredienteCreate (nombre, es_alergeno)
  - [ ] 2.2b IngredienteUpdate (nombre optional, es_alergeno optional)
  - [ ] 2.2c IngredienteRead (all fields + timestamps)
  - [ ] 2.2d IngredienteListResponse (items[], total, skip, limit)
- [ ] 2.3 Validate schema field constraints (non-empty nombre, boolean es_alergeno, max lengths)
- [ ] 2.4 Add Pydantic validators for whitespace trimming and type coercion

---

## 3. Backend Repository

- [ ] 3.1 Create `backend/app/ingredientes/repository.py` extending BaseRepository[Ingrediente]
- [ ] 3.2 Implement custom method: `find_by_nombre(nombre: str)` with soft delete filter
- [ ] 3.3 Implement custom method: `list_by_allergen(es_alergeno: bool)` with soft delete filter
- [ ] 3.4 Implement custom method: `soft_delete(id: int)` that sets eliminado_en timestamp
- [ ] 3.5 Add database query tests for each repository method (using pytest + in-memory SQLite)

---

## 4. Backend Service

- [ ] 4.1 Create `backend/app/ingredientes/service.py` with IngredienteService class
- [ ] 4.2 Implement `create_ingrediente(data: IngredienteCreate)`:
  - [ ] 4.2a Validate nombre is unique (check both DB and existing non-deleted)
  - [ ] 4.2b Raise 409 Conflict if duplicate
  - [ ] 4.2c Create and return IngredienteRead response
- [ ] 4.3 Implement `list_ingredientes(skip: int, limit: int, es_alergeno: Optional[bool])`:
  - [ ] 4.3a Filter by soft delete (eliminado_en IS NULL)
  - [ ] 4.3b Apply es_alergeno filter if provided
  - [ ] 4.3c Return paginated response with total count
- [ ] 4.4 Implement `get_ingrediente_by_id(id: int)`:
  - [ ] 4.4a Return IngredienteRead or raise 404
  - [ ] 4.4b Exclude soft-deleted
- [ ] 4.5 Implement `update_ingrediente(id: int, data: IngredienteUpdate)`:
  - [ ] 4.5a Raise 404 if soft-deleted
  - [ ] 4.5b Validate unique nombre if updating
  - [ ] 4.5c Update actualizado_en timestamp
- [ ] 4.6 Implement `delete_ingrediente(id: int)`:
  - [ ] 4.6a Raise 404 if not found or already deleted
  - [ ] 4.6b Call repository.soft_delete()
- [ ] 4.7 Add unit tests for each service method (cover happy path + error cases)

---

## 5. Backend Router

- [ ] 5.1 Create `backend/app/ingredientes/router.py` with FastAPI APIRouter
- [ ] 5.2 Implement POST `/api/v1/ingredientes`:
  - [ ] 5.2a Require role STOCK or ADMIN via `require_role(["STOCK", "ADMIN"])`
  - [ ] 5.2b Call service.create_ingrediente
  - [ ] 5.2c Return 201 Created with Location header
  - [ ] 5.2d Handle validation errors (422) and conflict (409)
- [ ] 5.3 Implement GET `/api/v1/ingredientes`:
  - [ ] 5.3a No auth required
  - [ ] 5.3b Support query params: skip, limit, es_alergeno
  - [ ] 5.3c Call service.list_ingredientes
  - [ ] 5.3d Return 200 with IngredienteListResponse
- [ ] 5.4 Implement GET `/api/v1/ingredientes/{id}`:
  - [ ] 5.4a No auth required
  - [ ] 5.4b Call service.get_ingrediente_by_id
  - [ ] 5.4c Return 200 with IngredienteRead or 404
- [ ] 5.5 Implement PUT `/api/v1/ingredientes/{id}`:
  - [ ] 5.5a Require role STOCK or ADMIN
  - [ ] 5.5b Call service.update_ingrediente
  - [ ] 5.5c Return 200 with updated IngredienteRead or 404/409
- [ ] 5.6 Implement DELETE `/api/v1/ingredientes/{id}`:
  - [ ] 5.6a Require role STOCK or ADMIN
  - [ ] 5.6b Call service.delete_ingrediente
  - [ ] 5.6c Return 204 No Content or 404
- [ ] 5.7 Register router in main app: `app.include_router(router, prefix="/api/v1")`
- [ ] 5.8 Verify endpoints in Swagger UI at `/docs`

---

## 6. Backend Integration Tests

- [ ] 6.1 Create `backend/tests/test_ingredientes.py` with test fixtures
- [ ] 6.2 Test POST /api/v1/ingredientes:
  - [ ] 6.2a Successful creation returns 201
  - [ ] 6.2b Duplicate name returns 409
  - [ ] 6.2c Missing fields returns 422
  - [ ] 6.2d Unauthorized role returns 403
- [ ] 6.3 Test GET /api/v1/ingredientes:
  - [ ] 6.3a List returns 200 with items and total
  - [ ] 6.3b Pagination works correctly
  - [ ] 6.3c Filter by es_alergeno=true returns only allergens
  - [ ] 6.3d Soft-deleted ingredients excluded
- [ ] 6.4 Test GET /api/v1/ingredientes/{id}:
  - [ ] 6.4a Existing ingredient returns 200
  - [ ] 6.4b Non-existent returns 404
  - [ ] 6.4c Soft-deleted returns 404
- [ ] 6.5 Test PUT /api/v1/ingredientes/{id}:
  - [ ] 6.5a Successful update returns 200
  - [ ] 6.5b Duplicate name returns 409
  - [ ] 6.5c Non-existent returns 404
  - [ ] 6.5d Unauthorized returns 403
- [ ] 6.6 Test DELETE /api/v1/ingredientes/{id}:
  - [ ] 6.6a Successful soft delete returns 204
  - [ ] 6.6b Deleted ingredient no longer appears in list
  - [ ] 6.6c Non-existent returns 404
  - [ ] 6.6d Unauthorized returns 403
- [ ] 6.7 Run full test suite: `pytest backend/tests/test_ingredientes.py -v --cov`

---

## 7. Frontend Types & API Layer

- [ ] 7.1 Create `frontend/src/entities/ingrediente/types.ts`:
  - [ ] 7.1a IngredienteRead interface
  - [ ] 7.1b IngredienteCreate interface
  - [ ] 7.1c IngredienteUpdate interface
  - [ ] 7.1d IngredienteListResponse interface
- [ ] 7.2 Create `frontend/src/entities/ingrediente/api.ts`:
  - [ ] 7.2a Function: `fetchIngredientes(skip, limit, esAlergeno)`
  - [ ] 7.2b Function: `fetchIngredienteById(id)`
  - [ ] 7.2c Function: `createIngrediente(data)`
  - [ ] 7.2d Function: `updateIngrediente(id, data)`
  - [ ] 7.2e Function: `deleteIngrediente(id)`
  - [ ] 7.2f Use Axios instance with JWT auth for POST/PUT/DELETE
- [ ] 7.3 Verify API functions work with mock Axios (no real backend calls yet)

---

## 8. Frontend TanStack Query Hooks

- [ ] 8.1 Create `frontend/src/entities/ingrediente/hooks.ts`:
  - [ ] 8.1a `useIngredientes(skip, limit, esAlergeno)` → useQuery
  - [ ] 8.1b `useIngredienteDetail(id)` → useQuery
  - [ ] 8.1c `useCreateIngrediente()` → useMutation + invalidateQueries
  - [ ] 8.1d `useUpdateIngrediente(id)` → useMutation + invalidateQueries
  - [ ] 8.1e `useDeleteIngrediente(id)` → useMutation + invalidateQueries
- [ ] 8.2 Test hooks with mock TanStack Query client (no real API calls)

---

## 9. Frontend Components

- [ ] 9.1 Create `frontend/src/features/ingredientes/ui/IngredientList.tsx`:
  - [ ] 9.1a Display table of ingredients
  - [ ] 9.1b Show columns: nombre, es_alergeno (with badge), creado_en
  - [ ] 9.1c Pagination controls (skip, limit)
  - [ ] 9.1d Edit/Delete buttons for each row (only if STOCK/ADMIN role)
  - [ ] 9.1e Filter toggle for allergens only
  - [ ] 9.1f Loading/error states
- [ ] 9.2 Create `frontend/src/features/ingredientes/ui/CreateIngredientModal.tsx`:
  - [ ] 9.2a Form fields: nombre, es_alergeno checkbox
  - [ ] 9.2b Submit button calls useCreateIngrediente()
  - [ ] 9.2c Success: close modal, refetch list
  - [ ] 9.2d Error: display error message
- [ ] 9.3 Create `frontend/src/features/ingredientes/ui/EditIngredientModal.tsx`:
  - [ ] 9.3a Pre-populate form with ingredient data
  - [ ] 9.3b Submit button calls useUpdateIngrediente()
  - [ ] 9.3c Success: close modal, refetch list
  - [ ] 9.3d Error: display error message
- [ ] 9.4 Create `frontend/src/features/ingredientes/ui/DeleteConfirmModal.tsx`:
  - [ ] 9.4a Confirmation text: "Are you sure?"
  - [ ] 9.4b Delete button calls useDeleteIngrediente()
  - [ ] 9.4c Success: close modal, refetch list
  - [ ] 9.4d Error: display error message

---

## 10. Frontend Navigation & RBAC

- [ ] 10.1 Add "Ingredientes" link to admin sidebar (only visible for STOCK/ADMIN roles)
- [ ] 10.2 Create route `/admin/ingredientes` pointing to IngredientList component
- [ ] 10.3 Wrap route with ProtectedRoute HOC requiring role [STOCK, ADMIN]
- [ ] 10.4 Test navigation: CLIENT role should not see link; STOCK role should see it

---

## 11. Frontend Testing

- [ ] 11.1 Create `frontend/src/features/ingredientes/__tests__/IngredientList.test.tsx`:
  - [ ] 11.1a Render list of ingredients from mock data
  - [ ] 11.1b Loading state displays spinner
  - [ ] 11.1c Error state displays error message
  - [ ] 11.1d Edit button opens EditIngredientModal
  - [ ] 11.1e Delete button opens DeleteConfirmModal
- [ ] 11.2 Create `frontend/src/features/ingredientes/__tests__/CreateIngredientModal.test.tsx`:
  - [ ] 11.2a Form submission validates non-empty nombre
  - [ ] 11.2b Submit button disabled during mutation
  - [ ] 11.2c Success closes modal and shows toast
  - [ ] 11.2d Error displays error message
- [ ] 11.3 Create `frontend/src/features/ingredientes/__tests__/EditIngredientModal.test.tsx`:
  - [ ] 11.3a Form pre-populates with ingredient data
  - [ ] 11.3b Submit button updates ingredient
  - [ ] 11.3c Success closes modal and refetches
- [ ] 11.4 Create `frontend/src/features/ingredientes/__tests__/DeleteConfirmModal.test.tsx`:
  - [ ] 11.4a Delete button calls delete mutation
  - [ ] 11.4b Success closes modal and refetches
- [ ] 11.5 Run frontend tests: `npm run test frontend/src/features/ingredientes`

---

## 12. End-to-End Testing

- [ ] 12.1 Manual E2E: Stock manager creates ingredient "Gluten" (es_alergeno=true)
  - [ ] 12.1a Verify ingredient appears in list
  - [ ] 12.1b Verify ingredient appears in allergen filter
  - [ ] 12.1c Verify ingredient details show correct data
- [ ] 12.2 Manual E2E: Edit ingredient name from "Gluten" to "Trigo"
  - [ ] 12.2a Verify list shows updated name
  - [ ] 12.2b Verify actualizado_en timestamp updated
- [ ] 12.3 Manual E2E: Delete ingredient
  - [ ] 12.3a Verify ingredient no longer appears in list
  - [ ] 12.3c Verify GET /api/v1/ingredientes/{id} returns 404
  - [ ] 12.3d Verify database: eliminado_en is set (not physically deleted)
- [ ] 12.4 Manual E2E: CLIENT role cannot create/edit/delete (403 responses)

---

## 13. Code Quality & Documentation

- [ ] 13.1 Run backend linters: `black backend/app/ingredientes`, `flake8 backend/app/ingredientes`, `mypy backend/app/ingredientes`
- [ ] 13.2 Run frontend linters: `eslint frontend/src/features/ingredientes`, `prettier --check frontend/src/features/ingredientes`
- [ ] 13.3 Add docstrings to service methods (summary + param + return types)
- [ ] 13.4 Add comments for non-obvious logic (e.g., soft delete filter)
- [ ] 13.5 Update `backend/README.md` with ingredient module documentation

---

## 14. Final Verification & Merge

- [ ] 14.1 Verify all tests pass: `pytest backend/tests/test_ingredientes.py` + `npm run test frontend`
- [ ] 14.2 Verify Swagger UI shows all 5 endpoints correctly
- [ ] 14.3 Git status clean (all changes staged/committed)
- [ ] 14.4 Create conventional commits:
  - [ ] 14.4a `feat(db): add ingrediente table migration`
  - [ ] 14.4b `feat(ingredientes): implement CRUD service + router`
  - [ ] 14.4c `feat(ingredientes): add TanStack Query hooks`
  - [ ] 14.4d `feat(ingredientes): add React components`
  - [ ] 14.4e `test(ingredientes): add integration + unit tests`
- [ ] 14.5 Create pull request with link to change-04 design/specs
- [ ] 14.6 Code review: verify against design decisions, check RBAC, validate soft delete behavior
- [ ] 14.7 Merge to main once approved

---

**Estimated Duration**: ~8 hours  
**Dependencies**: CHANGE-00 (completed), CHANGE-01 (completed), CHANGE-03 (completed)  
**Blocks**: CHANGE-06 (Productos CRUD y Stock)
