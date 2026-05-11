# Specification: Ingredient Allergen Flag

## ADDED Requirements

### Requirement: Mark Ingredient as Allergen

The system SHALL allow stock managers and admins to mark ingredients as allergens (es_alergeno=true) to indicate they contain common food allergens.

#### Scenario: Create ingredient with allergen flag true
- **WHEN** a STOCK user creates an ingredient with `{ "nombre": "Cacahuete", "es_alergeno": true }`
- **THEN** the ingredient is created with es_alergeno=true and is immediately queryable as an allergen

#### Scenario: Create ingredient without allergen flag (safe ingredient)
- **WHEN** a STOCK user creates an ingredient with `{ "nombre": "Sal", "es_alergeno": false }`
- **THEN** the ingredient is created with es_alergeno=false and will not appear in allergen-specific queries

#### Scenario: Toggle allergen status on existing ingredient
- **WHEN** a STOCK user PUTs to `/api/v1/ingredientes/3` with `{ "es_alergeno": true }` (changing from false)
- **THEN** the ingredient's es_alergeno flag is updated, actualizado_en is set, and subsequent queries reflect the new status

### Requirement: Filter Ingredients by Allergen Status

The system SHALL support filtering ingredients by allergen status via query parameter.

#### Scenario: Filter to show only allergens
- **WHEN** a user GETs `/api/v1/ingredientes?es_alergeno=true`
- **THEN** the response contains only ingredients where es_alergeno=true (excluding soft-deleted)

#### Scenario: Filter to show only non-allergen ingredients
- **WHEN** a user GETs `/api/v1/ingredientes?es_alergeno=false`
- **THEN** the response contains only ingredients where es_alergeno=false (excluding soft-deleted)

#### Scenario: No filter parameter returns all ingredients
- **WHEN** a user GETs `/api/v1/ingredientes` without es_alergeno parameter
- **THEN** the response contains all active ingredients (both allergens and non-allergens)

### Requirement: Allergen Information in Product Context

The system SHALL include allergen information when returning ingredient data, allowing frontend to display allergen badges/warnings.

#### Scenario: Get ingredient detail includes allergen flag
- **WHEN** a client GETs `/api/v1/ingredientes/5`
- **THEN** the response includes the es_alergeno boolean field to indicate allergen status

#### Scenario: List response includes allergen flag for all items
- **WHEN** a client GETs `/api/v1/ingredientes`
- **THEN** each item in the response includes es_alergeno field for visual filtering/display on frontend

---

## Query Parameter Specification

### GET /api/v1/ingredientes Query Params

Extended parameters:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `skip` | integer | 0 | Offset for pagination |
| `limit` | integer | 100 | Limit for pagination (max 1000) |
| `es_alergeno` | boolean | null (all) | Filter: true=allergens only, false=non-allergens only, omitted=all |

**Examples**:
- `/api/v1/ingredientes?es_alergeno=true` → only allergens
- `/api/v1/ingredientes?es_alergeno=false&limit=50` → non-allergens, paginated
- `/api/v1/ingredientes?skip=10&limit=10` → all ingredients, page 2 (items 10-19)
- `/api/v1/ingredientes` → all ingredients, default limit 100

---

## Response Schema Updates

### Ingredient Read Schema

All endpoints returning ingredients SHALL include:

```json
{
  "id": "integer",
  "nombre": "string",
  "es_alergeno": "boolean",
  "creado_en": "ISO 8601 timestamp",
  "actualizado_en": "ISO 8601 timestamp",
  "eliminado_en": "ISO 8601 timestamp or null"
}
```

The `es_alergeno` field is always present and is a true boolean (never null).

---

## Frontend Expectations

Stock managers and clients who view ingredient lists MUST be able to:

1. **See allergen status visually** (e.g., badge or icon next to allergen ingredient names)
2. **Filter by allergen** via a toggle or checkbox in the UI
3. **Search/sort by allergen status** (allergens first, then non-allergens)

---

## Validation Rules

1. **es_alergeno field**:
   - Must be boolean (true or false)
   - Cannot be null
   - Required on POST
   - Optional on PUT (if omitted, existing value is preserved)

2. **Filter behavior**:
   - `es_alergeno=true` → WHERE es_alergeno=true AND eliminado_en IS NULL
   - `es_alergeno=false` → WHERE es_alergeno=false AND eliminado_en IS NULL
   - No parameter → no filter on es_alergeno (all active ingredients)

3. **Uniqueness**:
   - Allergen ingredient names are subject to same uniqueness constraint as non-allergen ingredients
   - Two ingredients (one allergen, one not) cannot share the same name

---

**Status**: Specification Complete  
**Version**: v1.0  
**Date**: 2026-05-10
