# Design: CHANGE-04 — Ingredientes y Alérgenos

## Context

**Current State**: The Food Store database schema is initialized (CHANGE-00 completed), categories are hierarchical (CHANGE-03 completed), and authentication with RBAC is operational (CHANGE-01 completed). The next requirement is to build the ingredient management system, which serves as a foundation for the product catalog (CHANGE-06).

**Constraints**:
- Strict backend layering: Router → Service → UoW → Repository → Model
- Frontend follows Feature-Sliced Design (FSD)
- Database uses 3NF, soft delete pattern, and audit fields (`creado_en`, `actualizado_en`, `eliminado_en`)
- All API responses follow RFC 7807 error format (CHANGE-15)
- RBAC: Only STOCK and ADMIN roles can manage ingredients
- Rate limiting inherited from CHANGE-00

**Stakeholders**:
- **Gestor de Stock (STOCK role)**: Creates, edits, deletes ingredients; filters by allergen status
- **Admin (ADMIN role)**: Full access to ingredient management
- **Frontend Components**: Ingredient forms and lists used by admin/stock panels
- **Product Catalog (CHANGE-06)**: Depends on ingredient endpoints for N:M associations

## Goals / Non-Goals

**Goals**:
- ✅ Build a complete CRUD system for ingredients with RBAC enforcement
- ✅ Support allergen flagging and filtering to enable dietary restrictions
- ✅ Implement soft delete so historical product-ingredient associations are preserved
- ✅ Follow the Food Store architecture patterns strictly
- ✅ Provide backend endpoints and frontend UI for stock managers
- ✅ Ensure data consistency (unique names, nullable soft delete field)

**Non-Goals**:
- ❌ Product-ingredient associations (that's CHANGE-06)
- ❌ Allergen descriptions or detailed allergen metadata (simple boolean flag only)
- ❌ Ingredient substitution or cross-allergen detection
- ❌ Multi-language ingredient names
- ❌ Performance optimization beyond standard indexing (name, allergen filter)

## Decisions

### 1. **Use `es_alergeno` (Spanish) instead of `is_allergen`**

**Decision**: Column and field names use Spanish (`es_alergeno`), consistent with the entire Food Store codebase.

**Rationale**: The project is built by a Spanish-speaking team in a Spanish-speaking market. All other models use Spanish naming (e.g., `eliminado_en`, `usuario`, `dirección`). Consistency across the codebase reduces cognitive load.

**Alternatives Considered**:
- English naming (`is_allergen`) — rejected because it breaks consistency with the rest of the schema
- Bilingual naming — rejected because it creates mixed-language confusion

---

### 2. **Soft Delete via `eliminado_en` TIMESTAMPTZ field**

**Decision**: Ingredients use a nullable `eliminado_en` field of type TIMESTAMPTZ, set when deleted. Not physically removed.

**Rationale**:
- Preserves historical data so products created with a deleted ingredient still show the correct ingredient in snapshots
- Aligns with Food Store's soft delete pattern used across all entities
- Simplifies auditing and troubleshooting
- Unique constraint on `nombre` uses `WHERE eliminado_en IS NULL` to allow name reuse after permanent deletion

**Alternatives Considered**:
- Physical deletion — rejected because it breaks referential integrity for historical products
- Logical flag (`activo` boolean) — rejected because timestamps are better for audit trails

---

### 3. **Unique Constraint on `nombre` (soft delete aware)**

**Decision**: Database constraint: `UNIQUE (nombre) WHERE eliminado_en IS NULL`

**Rationale**:
- Prevents duplicate ingredient names among active ingredients
- Allows the same name to be reused after a logical deletion (in a future permanent cleanup)
- Partial index improves query performance for active ingredients

**Alternatives Considered**:
- Unconditional UNIQUE on `nombre` — rejected because it prevents reusing names after deletion
- Application-level validation only — rejected because database constraints are the source of truth

---

### 4. **Backend Module Structure: Feature-First (`ingredientes/`)**

**Decision**: Create module `backend/app/ingredientes/` with:
- `model.py` — SQLModel definition for `Ingrediente`
- `schemas.py` — Pydantic schemas (Create, Update, Read)
- `repository.py` — Custom repository methods
- `service.py` — Business logic
- `router.py` — REST endpoints

**Rationale**:
- Matches existing Food Store architecture (feature-first, vertical slicing)
- All ingredient-related code lives together → easy to find, modify, test
- Unidirectional dependencies: Router calls Service calls UoW calls Repository calls Model
- Clear separation of concerns

---

### 5. **RBAC: Restrict to STOCK and ADMIN**

**Decision**: All ingredient endpoints require either `STOCK` or `ADMIN` role via `require_role(["STOCK", "ADMIN"])` dependency.

**Rationale**:
- Only stock managers and admins should manage ingredients
- Clients (CLIENT role) should only read ingredients to see allergen info
- GET endpoint is public (no auth required) so clients can filter products by allergen

**Alternatives Considered**:
- Admin-only — rejected because stock managers are the primary users of this system
- Allow CLIENT role — rejected for security (prevent data pollution)

---

### 6. **GET endpoint is public, no authentication required**

**Decision**: `GET /api/v1/ingredientes` and `GET /api/v1/ingredientes/{id}` do NOT require authentication.

**Rationale**:
- Clients need to see allergen information when browsing products
- Listing ingredients is non-sensitive (public metadata)
- Enables frontend to pre-populate ingredient selectors without forcing login first

**Alternatives Considered**:
- Auth-only GET — rejected because allergen info is critical for client safety

---

### 7. **No Pagination Limit on GET if Total < 1000**

**Decision**: GET `/api/v1/ingredientes` supports `skip` and `limit` query params. Default: `skip=0, limit=100`. No hard limit because ingredients are expected to be a small, manageable set.

**Rationale**:
- Ingredients typically number in the dozens, not thousands
- Reduces complexity vs. products (which have thousands)
- Simple offset-limit pagination is sufficient

**Alternatives Considered**:
- Cursor-based pagination — rejected as over-engineering for a small dataset
- No pagination — rejected because future flexibility is needed

---

### 8. **Filter by `es_alergeno` via Query Parameter**

**Decision**: GET includes optional query param `?es_alergeno=true` to filter allergens only.

**Rationale**:
- Common use case: stock manager wants to see "all allergens" for risk assessment
- Easy to implement: `WHERE eliminado_en IS NULL AND (es_alergeno=true OR es_alergeno param not provided)`
- Client can filter products by allergen via frontend logic after fetching ingredients

---

### 9. **Validation: Unique Name + Non-Empty**

**Decision**: 
- Pydantic schema validates non-empty, non-whitespace-only names
- Database constraint enforces uniqueness (considering soft delete)
- Service layer checks before creating/updating and returns 409 Conflict if duplicate

**Rationale**:
- Defense in depth: validation at multiple layers
- Clear error messages for clients
- Prevents accidental duplication from race conditions

---

### 10. **Frontend: Ingredient CRUD Modal Components**

**Decision**: Build React components in `frontend/src/features/ingredientes/`:
- `IngredientList.tsx` — Table showing all ingredients with allergen badge
- `CreateIngredientModal.tsx` — Form for new ingredient
- `EditIngredientModal.tsx` — Form for editing
- `DeleteConfirmModal.tsx` — Confirmation for deletion

Use TanStack Query hooks to manage server state:
- `useIngredients(filters)` — Fetch ingredient list
- `useCreateIngredient()` — POST hook
- `useUpdateIngredient(id)` — PUT hook
- `useDeleteIngredient(id)` — DELETE hook

**Rationale**:
- Modal-based UI is familiar and space-efficient
- TanStack Query handles caching and automatic refetches
- Separates server state (TanStack Query) from local form state (React hooks or TanStack Form)
- RBAC check in authStore determines whether to show these components

---

### 11. **Migration Strategy: Alembic Auto-Generation**

**Decision**: After defining `Ingrediente` model in SQLModel, run `alembic revision --autogenerate -m "add ingrediente table"` to create the migration script.

**Rationale**:
- Alembic auto-generates DDL from model changes
- Creates a version-controlled, reversible migration
- Integrates with existing Food Store migration pipeline (CHANGE-00d)

---

## Risks / Trade-offs

| Risk | Impact | Mitigation |
|------|--------|-----------|
| **Soft delete leaves orphaned records** | Disk usage grows; queries must always filter `eliminado_en IS NULL` | Implement periodic archival job (out of scope) or accept growth as acceptable |
| **Name uniqueness constraint blocks recovery** | Admin can't recreate deleted ingredient with same name immediately | Document that deleted ingredients stay "reserved" for 30 days before permanent cleanup (procedural, not automated) |
| **No ingredient categories/hierarchies** | Can't group allergens (e.g., "Tree Nuts" parent with "Almond", "Walnut" children) | Accept for v5.0; if needed, CHANGE-06 or future can extend model with `parent_id` |
| **Boolean allergen flag is too simple** | Can't track severity (anaphylaxis vs. intolerance) or prevalence | Accept; allergen severity is a client concern, not a backend concern |
| **Race condition: duplicate name check** | Two concurrent POST requests both see name as free | Database constraint catches second; client gets 409 Conflict; retry logic in frontend |
| **GET is unauthenticated** | Potential information disclosure | Allergen list is non-sensitive public metadata; no risk |

---

## Migration Plan

### Deployment

1. **Database**: Run Alembic migration to create `ingrediente` table with:
   - `id` (SERIAL PRIMARY KEY)
   - `nombre` (VARCHAR(255) UNIQUE WHERE eliminado_en IS NULL)
   - `es_alergeno` (BOOLEAN NOT NULL)
   - `creado_en` (TIMESTAMPTZ NOT NULL, DEFAULT now())
   - `actualizado_en` (TIMESTAMPTZ NOT NULL, DEFAULT now())
   - `eliminado_en` (TIMESTAMPTZ, NULL by default)

2. **Backend**: Deploy new `ingredientes/` module with router, service, repository, schemas.

3. **Frontend**: Deploy ingredient components; update navigation to show "Ingredientes" in admin menu for STOCK/ADMIN roles.

4. **Validation**: 
   - Stock manager can create an ingredient via UI
   - GET `/api/v1/ingredientes` returns the created ingredient
   - GET `/api/v1/ingredientes?es_alergeno=true` filters correctly
   - Edit and delete work end-to-end

### Rollback

1. **If critical bug found before merge to main**:
   - Revert commits to backend and frontend
   - Run `alembic downgrade -1` to remove table
   - No production data loss

2. **If bug found in production**:
   - Keep table and data
   - Disable ingredient endpoints (comment out router registration)
   - Patch and redeploy without migration rollback
   - Document incident

---

## Open Questions

1. **Should we seed default allergens?** (e.g., "Gluten", "Lactose", "Peanuts")
   - Defer to CHANGE-00d (Seed Data) or manual creation after deployment?
   - **Recommendation**: Manual creation in v5.0-beta phase, seed after stabilization.

2. **Should we support ingredient translations (es, en)?**
   - Out of scope for v5.0, but design should not block future i18n.
   - **Recommendation**: Accept current single-language design; future can add `translations` JSONB field.

3. **Should DELETE return soft-deleted ingredient details or 204 No Content?**
   - **Recommendation**: Return 204 (No Content) for consistency with REST conventions.

4. **Should we track which user created/edited an ingredient?**
   - `creado_por` / `actualizado_por` user_id foreign keys?
   - **Recommendation**: Defer to CHANGE-15 (global audit trail); out of scope for v5.0.

---

**Reviewed**: 2026-05-10  
**Architecture Alignment**: ✅ Confirmed against `docs/Integrador.txt`  
**Risk Assessment**: Acceptable for v5.0
