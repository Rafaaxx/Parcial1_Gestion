## Why

The Food Store needs a public product catalog interface so customers can browse, search, and filter available products without authentication. This capability is the **entry point for the customer journey** — without it, clients have no way to discover products before checkout. CHANGE-06 built the backend product CRUD and inventory system; CHANGE-07 exposes that inventory to the public frontend, enabling US-018, US-019, and US-023.

## What Changes

- **New Frontend**: Public catalog page with search, filter, and pagination UI components (no login required)
- **Backend Enhancement**: Public read endpoints for product listing and detail (already exist in CHANGE-06, now documented formally)
- **Search & Filter**: Support for text search (ILIKE), category filters, price range, and allergen exclusion
- **Inventory Display**: Show stock status (in-stock vs. out-of-stock) without revealing exact quantities to unauthenticated users
- **Pagination**: Client-side pagination with server-side total count for accurate page controls

## Capabilities

### New Capabilities

- `catalog-search`: Public product search with ILIKE by name, category filter, price range (precio_desde, precio_hasta), skip/limit pagination, and total count response
- `catalog-filter-allergens`: Filter products by excluding specific allergen IDs (via query param `excluirAlergenos`); returns products that do NOT contain those ingredients
- `catalog-ui`: React component suite for product listing page (ProductList, ProductFilters, ProductCard, PaginationControls) with Zustand query state and TanStack Query integration
- `product-detail-page`: Public product detail page showing name, description, price, image, ingredients with allergen badges, categories, and in-stock indicator

### Modified Capabilities

- `product-crud`: The CHANGE-06 product model already supports public visibility (disponible flag, deleted_at soft delete). This change formally publishes the existing `GET /api/v1/productos` and `GET /api/v1/productos/{id}` endpoints as the catalog API contract

## Impact

**Code changes**:
- Frontend: `src/pages/Catalog/`, `src/features/ProductList/`, `src/hooks/useCatalogFilters.ts`, Zustand store for filters
- Backend: Documentation + schema export (endpoints already exist from CHANGE-06, now formally versioned as `catalog-api`)

**User Stories**: US-018 (list products), US-019 (product detail), US-023 (filter by allergen)

**Database**: No schema changes (reuses CHANGE-06 product/ingredient/category tables)

**APIs**: Public endpoints (no authentication required):
- `GET /api/v1/productos` with query params: `skip`, `limit`, `categoria`, `busqueda`, `precio_desde`, `precio_hasta`, `excluirAlergenos`
- `GET /api/v1/productos/{id}` (returns 404 if not available or deleted)

**Risk**: None — read-only, uses existing data models
