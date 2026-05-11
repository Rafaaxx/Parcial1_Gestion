# Specification: Ingredient Soft Delete

## ADDED Requirements

### Requirement: Soft Delete Ingredient via Timestamp

The system SHALL implement logical deletion for ingredients by setting an eliminado_en timestamp, not removing the record from the database.

#### Scenario: Successful soft delete sets timestamp
- **WHEN** an authenticated STOCK user DELETEs `/api/v1/ingredientes/5`
- **THEN** the ingredient's eliminado_en field is set to the current ISO 8601 timestamp, and the record remains in the database

#### Scenario: Deleted ingredient is hidden from lists
- **WHEN** a user GETs `/api/v1/ingredientes` after deleting an ingredient
- **THEN** the deleted ingredient does not appear in the results (query filters WHERE eliminado_en IS NULL)

#### Scenario: Deleted ingredient returns 404 on direct GET
- **WHEN** a user GETs `/api/v1/ingredientes/5` where ingredient 5 is soft-deleted
- **THEN** the system returns 404 Not Found (soft-deleted items are treated as non-existent for public queries)

#### Scenario: Deleted ingredient cannot be updated
- **WHEN** a STOCK user tries to PUT to `/api/v1/ingredientes/5` where ingredient 5 is soft-deleted
- **THEN** the system returns 404 Not Found (cannot update what doesn't exist from a public perspective)

### Requirement: Preserve Historical Data in Products

The system SHALL preserve ingredient-product associations even if an ingredient is subsequently soft-deleted.

#### Scenario: Product retains ingredient reference after ingredient deletion
- **WHEN** a product was created with ingredient 5 (e.g., "Pizza contains Gluten"), and then ingredient 5 is soft-deleted
- **THEN** the product's ingredient association remains intact; the product still shows "Gluten" in its ingredient list (from the snapshot or association)

#### Scenario: Snapshot data is immutable
- **WHEN** an ingredient is soft-deleted after being used in a product
- **THEN** any snapshots or JSON fields in products/orders that captured the ingredient name/properties are not retroactively changed

### Requirement: Database Soft Delete Constraint

The system SHALL enforce a database-level unique constraint on ingredient name that respects soft deletion.

#### Scenario: Deleted ingredient name can be reused (theoretically)
- **WHEN** ingredient "Gluten" (id=1, es_alergeno=true) is soft-deleted, and a new ingredient is created with name "Gluten"
- **THEN** the system allows the creation because the database constraint is `UNIQUE (nombre) WHERE eliminado_en IS NULL`

#### Scenario: Two active ingredients cannot share the same name
- **WHEN** two ingredients with the same name both have eliminado_en=NULL
- **THEN** the database constraint prevents the second INSERT with a unique violation error

### Requirement: Soft Delete Fields in Responses

The system SHALL include eliminado_en in ingredient responses to allow frontends and admins to see deletion status.

#### Scenario: Active ingredient has null eliminado_en
- **WHEN** a user GETs an active ingredient
- **THEN** the eliminado_en field is null in the response

#### Scenario: Admin endpoint (future) can view soft-deleted ingredients
- **WHEN** a STOCK user uses an admin GET endpoint that includes `include_deleted=true` parameter (future capability)
- **THEN** the response includes ingredients with non-null eliminado_en (reserved for v5.1+, document for future use)

---

## Database Schema

### Ingrediente Table Columns

| Column | Type | Null | Default | Notes |
|--------|------|------|---------|-------|
| `id` | SERIAL | NO | nextval(...) | Primary key |
| `nombre` | VARCHAR(255) | NO | | Unique among active ingredients |
| `es_alergeno` | BOOLEAN | NO | | True if allergen |
| `creado_en` | TIMESTAMPTZ | NO | now() | Audit: creation timestamp |
| `actualizado_en` | TIMESTAMPTZ | NO | now() | Audit: last update timestamp |
| `eliminado_en` | TIMESTAMPTZ | YES | NULL | Soft delete: set on deletion, NULL if active |

### Unique Constraint

```sql
CONSTRAINT uk_ingrediente_nombre 
UNIQUE (nombre) 
WHERE eliminado_en IS NULL
```

This allows:
- At most one active ingredient per name
- Inactive (deleted) ingredients don't participate in uniqueness
- Names can theoretically be reused after permanent deletion (future)

---

## Query Behavior

### List Query (GET /api/v1/ingredientes)

```sql
SELECT id, nombre, es_alergeno, creado_en, actualizado_en, eliminado_en
FROM ingrediente
WHERE eliminado_en IS NULL
ORDER BY nombre ASC
LIMIT :limit OFFSET :skip
```

### Single Ingredient Query (GET /api/v1/ingredientes/{id})

```sql
SELECT id, nombre, es_alergeno, creado_en, actualizado_en, eliminado_en
FROM ingrediente
WHERE id = :id AND eliminado_en IS NULL
```

If no match, return 404.

### Delete Operation (DELETE /api/v1/ingredientes/{id})

```sql
UPDATE ingrediente
SET eliminado_en = NOW()
WHERE id = :id AND eliminado_en IS NULL
```

If no match (already deleted or doesn't exist), return 404.

---

## Validation Rules

1. **Soft Delete Behavior**:
   - DELETE endpoint MUST set eliminado_en to current timestamp, not remove the row
   - GET queries MUST exclude rows where eliminado_en IS NOT NULL
   - PUT on soft-deleted returns 404 (treat as non-existent)
   - Unique constraint MUST be partial (WHERE eliminado_en IS NULL)

2. **Response Inclusion**:
   - eliminado_en MUST be in all ingredient response schemas
   - For active ingredients, eliminado_en = null
   - For soft-deleted (admin views, future), eliminado_en = ISO 8601 timestamp

3. **Data Integrity**:
   - Product ingredient associations use ingredient IDs, which remain stable even after soft delete
   - Snapshots of ingredient data in orders are immutable and unaffected by ingredient deletions
   - Historical audit trail (HistorialEstadoPedido, etc.) never references ingredient deletion status

---

## Migration Path

1. **Schema Creation** (Alembic):
   - Create `ingrediente` table with all columns
   - Add `UNIQUE (nombre) WHERE eliminado_en IS NULL` constraint
   - Add indices on `nombre` and `es_alergeno` for query performance

2. **Future Permanent Deletion** (v5.1+):
   - Implement archival job that permanently deletes ingredients with eliminado_en older than 12 months
   - Document cleanup procedure in operations manual

---

**Status**: Specification Complete  
**Version**: v1.0  
**Date**: 2026-05-10
