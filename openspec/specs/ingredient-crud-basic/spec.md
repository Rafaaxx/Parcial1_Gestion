# Specification: Ingredient CRUD Basic

## ADDED Requirements

### Requirement: Create Ingredient via POST

The system SHALL allow users with STOCK or ADMIN roles to create a new ingredient with a unique name and allergen flag.

#### Scenario: Successful creation of new ingredient
- **WHEN** an authenticated user with role STOCK POSTs to `/api/v1/ingredientes` with `{ "nombre": "Gluten", "es_alergeno": true }`
- **THEN** the system creates the ingredient with a 201 Created response including the new ingredient's id, nombre, es_alergeno, creado_en, and actualizado_en

#### Scenario: Duplicate ingredient name returns conflict
- **WHEN** a user tries to POST an ingredient with a name that already exists (and is not soft-deleted)
- **THEN** the system returns 409 Conflict with error detail "Ingredient name already exists"

#### Scenario: Missing required fields returns validation error
- **WHEN** a user POSTs without `nombre` or `es_alergeno`
- **THEN** the system returns 422 Unprocessable Entity with field-level validation errors per RFC 7807

#### Scenario: Unauthorized role cannot create
- **WHEN** a user with role CLIENT attempts to create an ingredient
- **THEN** the system returns 403 Forbidden

### Requirement: List Ingredients via GET

The system SHALL return a paginated list of all active (non-deleted) ingredients. This endpoint is public (no authentication required).

#### Scenario: Successful list retrieval
- **WHEN** a client GETs `/api/v1/ingredientes?skip=0&limit=20`
- **THEN** the system returns 200 OK with an array of ingredients, total count, skip, and limit

#### Scenario: Soft-deleted ingredients are excluded
- **WHEN** an ingredient is soft-deleted (eliminado_en is set) and a user GETs the list
- **THEN** the deleted ingredient does not appear in the response

#### Scenario: Empty list when no ingredients exist
- **WHEN** a user GETs `/api/v1/ingredientes` and no ingredients have been created
- **THEN** the system returns 200 OK with empty array and total=0

#### Scenario: Pagination works correctly
- **WHEN** a user GETs `/api/v1/ingredientes?skip=10&limit=5`
- **THEN** the system returns items 10-14 (or fewer if fewer exist) and total count matches actual database count

### Requirement: Get Ingredient by ID via GET

The system SHALL return detailed information for a single ingredient by its ID. Public endpoint (no auth required).

#### Scenario: Ingredient exists
- **WHEN** a client GETs `/api/v1/ingredientes/123`
- **THEN** the system returns 200 OK with the ingredient's id, nombre, es_alergeno, creado_en, actualizado_en, eliminado_en

#### Scenario: Ingredient not found
- **WHEN** a client GETs `/api/v1/ingredientes/999999` (non-existent ID)
- **THEN** the system returns 404 Not Found

#### Scenario: Soft-deleted ingredient returns not found
- **WHEN** a client GETs an ingredient that has been soft-deleted (eliminado_en is not null)
- **THEN** the system returns 404 Not Found

### Requirement: Update Ingredient via PUT

The system SHALL allow users with STOCK or ADMIN roles to update an ingredient's name and/or allergen flag.

#### Scenario: Successful update
- **WHEN** an authenticated STOCK user PUTs to `/api/v1/ingredientes/5` with `{ "nombre": "Trigo", "es_alergeno": true }`
- **THEN** the system updates the ingredient, returns 200 OK with the updated object, and sets actualizado_en to current timestamp

#### Scenario: Update with duplicate name returns conflict
- **WHEN** a user tries to update ingredient 5's name to a name already used by ingredient 6
- **THEN** the system returns 409 Conflict with error "Ingredient name already exists"

#### Scenario: Update deleted ingredient fails
- **WHEN** a user tries to update an ingredient that has been soft-deleted
- **THEN** the system returns 404 Not Found

#### Scenario: Unauthorized role cannot update
- **WHEN** a CLIENT user tries to update an ingredient
- **THEN** the system returns 403 Forbidden

#### Scenario: Invalid JSON returns validation error
- **WHEN** a user PUTs malformed JSON or missing required fields
- **THEN** the system returns 422 Unprocessable Entity with field errors

### Requirement: Delete Ingredient via DELETE (Soft Delete)

The system SHALL allow users with STOCK or ADMIN roles to soft-delete an ingredient by setting its eliminado_en timestamp.

#### Scenario: Successful soft delete
- **WHEN** an authenticated STOCK user DELETEs `/api/v1/ingredientes/5`
- **THEN** the system soft-deletes the ingredient (sets eliminado_en to current timestamp), returns 204 No Content

#### Scenario: Ingredient no longer appears after deletion
- **WHEN** an ingredient is soft-deleted and a user GETs the list
- **THEN** the deleted ingredient does not appear in GET /api/v1/ingredientes results

#### Scenario: Deleted ingredient can still be referenced in historical products
- **WHEN** a product was created with ingredient 5 and ingredient 5 is later soft-deleted
- **THEN** the product's ingredient association remains intact (ingredient ID in snapshot or association table)

#### Scenario: Delete non-existent ingredient returns not found
- **WHEN** a user DELETEs `/api/v1/ingredientes/999999`
- **THEN** the system returns 404 Not Found

#### Scenario: Unauthorized role cannot delete
- **WHEN** a CLIENT user tries to delete an ingredient
- **THEN** the system returns 403 Forbidden

---

## API Contract

### POST /api/v1/ingredientes

**Request**:
```json
{
  "nombre": "string (required, non-empty, max 255 chars)",
  "es_alergeno": "boolean (required)"
}
```

**Response (201)**:
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

### GET /api/v1/ingredientes

**Query Parameters**:
- `skip`: integer (default 0)
- `limit`: integer (default 100, max 1000)

**Response (200)**:
```json
{
  "items": [
    {
      "id": "integer",
      "nombre": "string",
      "es_alergeno": "boolean",
      "creado_en": "ISO 8601 timestamp",
      "actualizado_en": "ISO 8601 timestamp",
      "eliminado_en": "null"
    }
  ],
  "total": "integer",
  "skip": "integer",
  "limit": "integer"
}
```

### GET /api/v1/ingredientes/{id}

**Response (200)**:
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

### PUT /api/v1/ingredientes/{id}

**Request**:
```json
{
  "nombre": "string (optional, if provided must be unique)",
  "es_alergeno": "boolean (optional)"
}
```

**Response (200)**:
Same as POST response with updated fields

### DELETE /api/v1/ingredientes/{id}

**Response (204)**: No content

---

## Validation Rules

1. **Nombre**:
   - Required on POST
   - Non-empty (whitespace trimmed)
   - Maximum 255 characters
   - Unique among non-deleted ingredients (database constraint)

2. **es_alergeno**:
   - Required on POST
   - Must be boolean true or false
   - Optional on PUT

3. **RBAC**:
   - POST: requires STOCK or ADMIN
   - GET: public (no auth)
   - PUT: requires STOCK or ADMIN
   - DELETE: requires STOCK or ADMIN

4. **Soft Delete**:
   - DELETE sets eliminado_en to current timestamp
   - GET and GET {id} exclude soft-deleted records
   - PUT on soft-deleted returns 404
   - DELETE on soft-deleted returns 404

---

**Status**: Specification Complete  
**Version**: v1.0  
**Date**: 2026-05-10
