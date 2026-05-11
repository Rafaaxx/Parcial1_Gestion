# Proposal: CHANGE-04 — Ingredientes y Alérgenos

## Why

The Food Store platform requires a complete system for managing product ingredients and identifying allergens. This capability is critical for:
- **Customer Safety**: Clients with dietary restrictions or allergies must know exactly what's in each product.
- **Regulatory Compliance**: Food businesses are legally required to disclose allergen information.
- **Operational Efficiency**: Stock managers need a single source of truth for ingredients and their allergen properties, which can then be associated with products in CHANGE-06.
- **Data Integrity**: The system must support soft deletes so historical product ingredients are preserved even if an ingredient becomes obsolete.

## What Changes

- **New Model `Ingrediente`**: Table with `id`, `nombre` (unique), `es_alergeno` (boolean), `creado_en`, `actualizado_en`, `eliminado_en` (soft delete).
- **RBAC Restrictions**: Only users with role `STOCK` or `ADMIN` can create, edit, or delete ingredients.
- **Soft Delete Pattern**: Ingredients are logically deleted (set `eliminado_en`), not physically removed, so products created with that ingredient maintain historical integrity.
- **Four REST Endpoints**:
  - `POST /api/v1/ingredientes` — Create a new ingredient
  - `GET /api/v1/ingredientes` — List all ingredients with optional filters (pagination, allergen filter)
  - `PUT /api/v1/ingredientes/{id}` — Edit an ingredient
  - `DELETE /api/v1/ingredientes/{id}` — Soft delete an ingredient
- **Validation Rules**:
  - Ingredient name must be unique (non-empty).
  - `es_alergeno` is required (boolean).
  - Editing must not create duplicate names across active ingredients.
  - Deletion applies soft delete (timestamp set), not physical deletion.

## Capabilities

### New Capabilities

- `ingredient-crud-basic`: Core create/read/update/delete operations for ingredients with RBAC enforcement and soft delete support.
- `ingredient-allergen-flag`: Ability to mark ingredients as allergens and filter by allergen status in listings.
- `ingredient-soft-delete`: Logical deletion via timestamp field, preserving historical associations with products.

### Modified Capabilities

- None. CHANGE-03 (categories) is independent and completed before this change.

## Impact

### Backend

- **New Module**: `backend/app/ingredientes/` with feature-first structure:
  - `model.py` — SQLModel for `Ingrediente` table
  - `schemas.py` — Pydantic schemas (Create, Update, Read)
  - `repository.py` — BaseRepository[Ingrediente] with custom methods (find by name, filter by allergen)
  - `service.py` — Business logic (validation, soft delete)
  - `router.py` — REST endpoints with RBAC checks
- **Database**: One new table `ingrediente` with soft delete support (follows Food Store conventions).
- **Dependencies**: SQLModel, Pydantic (already in stack). No new external dependencies.

### Frontend

- **New Feature Module**: `frontend/src/features/ingredientes/` with:
  - React components for ingredient CRUD (list, create, edit, delete modals)
  - TanStack Query hooks for fetching/mutating ingredients
  - TypeScript types aligned with backend schemas
- **Navigation**: Only visible to STOCK and ADMIN roles (RBAC check via `authStore`).

### APIs

- Four new REST endpoints under `/api/v1/ingredientes`
- All responses follow RFC 7807 error format (from CHANGE-15)
- Rate limiting via slowapi on sensitive endpoints (inherited from CHANGE-00)

### Testing

- Backend: Unit tests for `IngredienteRepository` (CRUD, soft delete), integration tests for endpoints with RBAC
- Frontend: Component tests for ingredient forms, TanStack Query hook tests
- E2E: Stock manager can create, list, filter by allergen, and soft delete ingredients

---

## Linked User Stories

- **US-011**: Crear ingrediente
- **US-012**: Listar ingredientes  
- **US-013**: Editar ingrediente
- **US-014**: Eliminar ingrediente (soft delete)

---

## Technical Notes

1. **Dependency on CHANGE-03**: Categorías must be completed first so the database is initialized and conventions are established.
2. **Independence from CHANGE-06**: This change is self-contained. CHANGE-06 (Productos) will consume these endpoints to associate ingredients with products.
3. **Naming Convention**: Field is `es_alergeno` (Spanish, per project convention), not `is_allergen`.
4. **Soft Delete Field**: Uses `eliminado_en` (TIMESTAMPTZ, nullable) per Food Store convention, consistent with other entities.
5. **Unique Constraint**: Database-level unique constraint on `nombre` WHERE `eliminado_en IS NULL` to allow reusing names only after permanent deletion.

---

**Estimated Duration**: ~8 hours  
**Blocks**: CHANGE-06 (Productos CRUD y Stock)
