# Specification: catalog-search

Public product search with filtering and pagination.

---

## ADDED Requirements

### Requirement: Search products by name (ILIKE)
The system SHALL support searching products by name using case-insensitive substring matching (ILIKE). The search parameter is optional; if not provided, all products are returned.

#### Scenario: User searches for "pizza"
- **WHEN** client calls `GET /api/v1/productos?busqueda=pizza`
- **THEN** system returns only products whose name contains "pizza" (case-insensitive)
- **AND** response includes products named "Pizza Napolitana", "pizza familiar", "PIZZA VEGANA", etc.

#### Scenario: Search with no results
- **WHEN** client calls `GET /api/v1/productos?busqueda=xyznotaproduct`
- **THEN** system returns HTTP 200 with empty array `[]`
- **AND** total count is 0

#### Scenario: Search parameter is empty
- **WHEN** client calls `GET /api/v1/productos?busqueda=`
- **THEN** system treats it as no filter (returns all available products)

---

### Requirement: Filter products by category
The system SHALL support filtering products by category ID. Only products explicitly associated with the specified category are returned.

#### Scenario: Filter by category ID
- **WHEN** client calls `GET /api/v1/productos?categoria=5`
- **THEN** system returns products where ProductoCategoria.categoria_id = 5
- **AND** each product in response includes associated categories in `categorias` array

#### Scenario: Filter by non-existent category
- **WHEN** client calls `GET /api/v1/productos?categoria=99999`
- **THEN** system returns HTTP 200 with empty array `[]`

#### Scenario: Multiple category filters (future, not yet supported)
- **WHEN** client calls `GET /api/v1/productos?categorias=5,6,7`
- **THEN** system returns products in ANY of those categories (OR logic)

---

### Requirement: Filter products by price range
The system SHALL support filtering products by minimum and maximum price. Both parameters are optional and independent.

#### Scenario: Filter by minimum price
- **WHEN** client calls `GET /api/v1/productos?precio_desde=100`
- **THEN** system returns only products where precio_base >= 100

#### Scenario: Filter by maximum price
- **WHEN** client calls `GET /api/v1/productos?precio_hasta=500`
- **THEN** system returns only products where precio_base <= 500

#### Scenario: Filter by price range (both boundaries)
- **WHEN** client calls `GET /api/v1/productos?precio_desde=100&precio_hasta=500`
- **THEN** system returns products where 100 <= precio_base <= 500

#### Scenario: Inverted price range
- **WHEN** client calls `GET /api/v1/productos?precio_desde=500&precio_hasta=100`
- **THEN** system returns no products (empty array, HTTP 200)
- **AND** total count is 0

---

### Requirement: Pagination with skip and limit
The system SHALL support offset-limit pagination via `skip` and `limit` query parameters.

#### Scenario: Default pagination
- **WHEN** client calls `GET /api/v1/productos`
- **THEN** system applies default `skip=0` and `limit=20`
- **AND** response includes only the first 20 available products

#### Scenario: Custom pagination
- **WHEN** client calls `GET /api/v1/productos?skip=40&limit=10`
- **THEN** system returns 10 products starting at offset 40

#### Scenario: Skip beyond available products
- **WHEN** client calls `GET /api/v1/productos?skip=10000&limit=20`
- **THEN** system returns HTTP 200 with empty array `[]`

#### Scenario: Response includes total count
- **WHEN** client calls any `GET /api/v1/productos` endpoint
- **THEN** response includes header or field `X-Total-Count` (or JSON field `total`) with the total number of available products (ignoring skip/limit)

---

### Requirement: Combine search, filters, and pagination
The system SHALL allow combining search, category filter, price filter, and pagination in a single request.

#### Scenario: Complex filter
- **WHEN** client calls `GET /api/v1/productos?busqueda=pizza&categoria=5&precio_desde=50&precio_hasta=200&skip=0&limit=10`
- **THEN** system applies all filters in AND logic (search AND category AND price)
- **AND** returns up to 10 matching products with total count

---

### Requirement: Only available products are returned
The system SHALL exclude soft-deleted and unavailable products from all search results.

#### Scenario: Deleted product not in results
- **WHEN** client calls `GET /api/v1/productos`
- **THEN** only products with `deleted_at IS NULL` and `disponible = true` are included
- **AND** soft-deleted products (deleted_at IS NOT NULL) never appear

#### Scenario: Unavailable product not in results
- **WHEN** client calls `GET /api/v1/productos`
- **THEN** only products with `disponible = true` are returned
- **AND** products with `disponible = false` never appear, even if stock > 0

---

### Requirement: Public endpoint (no authentication)
The system SHALL allow unauthenticated access to product search endpoints.

#### Scenario: Anonymous client searches products
- **WHEN** anonymous client calls `GET /api/v1/productos` without Authorization header
- **THEN** system returns HTTP 200 with results
- **AND** no 401 or 403 error is raised

---

### Requirement: Response schema (ProductoListResponse)
The system SHALL return products in a consistent list schema with pagination metadata.

#### Scenario: Response structure
- **WHEN** client calls `GET /api/v1/productos`
- **THEN** response includes:
  - `items: ProductoListItem[]` — array of products
  - `total: int` — total count (ignoring pagination)
  - `skip: int` — offset applied
  - `limit: int` — page size applied
  - `pages: int` — calculated ceiling(total / limit)

#### Scenario: ProductoListItem schema
- **WHEN** client receives a product in the list
- **THEN** each product includes: `id`, `nombre`, `descripcion`, `precio_base`, `imagen_url`, `disponible`
- **AND** does NOT include `stock_cantidad` (not revealed to public)
