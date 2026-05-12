# Tasks: CHANGE-07 — Catálogo Público (Listado y Búsqueda)

## 1. Backend: Documentación y Validación de Endpoints

- [x] 1.1 Verify existing `GET /api/v1/productos` endpoint supports all query params (skip, limit, categoria, busqueda, precio_desde, precio_hasta)
- [x] 1.2 Add eager loading to productos repository: use `selectinload()` for categories and ingredients to prevent N+1
- [x] 1.3 Update `GET /api/v1/productos/{id}` to include eager loading of categorias and ingredientes associations
- [x] 1.4 Ensure `ProductoListItem` schema excludes `stock_cantidad` field (public list should not reveal inventory)
- [x] 1.5 Ensure `ProductoDetail` schema includes allergen info in ingredientes (es_alergeno flag)
- [x] 1.6 Add validation for `excluirAlergenos` query param: parse comma-separated integers
- [x] 1.7 Implement allergen exclusion filter in repository: `NOT EXISTS` query to exclude products with specified ingredient IDs
- [x] 1.8 Add OpenAPI/Swagger documentation tags for public endpoints (`tags=["products"]`)
- [x] 1.9 Write integration tests for producto search with all filter combinations (search + category + price + allergens)
- [x] 1.10 Test pagination edge cases: skip beyond total, zero results, default limit=20
- [x] 1.11 Validate allergen filter with real ingredient IDs from test DB

## 2. Frontend: Project Structure and Setup

- [x] 2.1 Create directory structure: `src/features/ProductCatalog/` with subdirs: pages, components, hooks, stores, api, types
- [x] 2.2 Create `src/pages/CatalogPage.tsx` as the main route page
- [x] 2.3 Create TypeScript types: `src/features/ProductCatalog/types/catalog.ts` with ProductCard, ProductListItem, ProductDetail, CatalogFilters interfaces
- [x] 2.4 Configure route: Add `/catalogo` route to React Router (both `:id` for detail and root for listing)
- [x] 2.5 Update navigation: Add "Catalog" link to Navbar (accessible even when not logged in)

## 3. Frontend: API Integration

- [x] 3.1 Create `src/features/ProductCatalog/api/catalogApi.ts` with axios calls
- [x] 3.2 Implement `getProducts(filters)` function: `GET /api/v1/productos` with query params
- [x] 3.3 Implement `getProductDetail(id)` function: `GET /api/v1/productos/{id}`
- [x] 3.4 Implement error handling: map 404 to "Product not found", 500 to "Server error"
- [x] 3.5 Add TypeScript strict typing for API responses and request params

## 4. Frontend: State Management (Zustand)

- [x] 4.1 Create `src/features/ProductCatalog/stores/catalogStore.ts`
- [x] 4.2 Define store state: searchText, selectedCategory, priceFrom, priceTo, excludedAllergens, currentPage, limit
- [x] 4.3 Define actions: setSearch, setCategory, setPriceRange, setAllergenExclusions, setPage, resetFilters
- [x] 4.4 Implement selector: getQueryParams() — returns object ready for API call
- [x] 4.5 Implement selector: isFilterActive() — returns true if any filter applied (for "Clear Filters" button)

## 5. Frontend: TanStack Query Integration

- [x] 5.1 Create custom hook `src/features/ProductCatalog/hooks/useCatalogFilters.ts`
- [x] 5.2 Implement `useProducts()` hook: wraps `useQuery` with catalog API call
- [x] 5.3 Use query key with filters: `['productos', { skip, limit, categoria, busqueda, precio_desde, precio_hasta, excluirAlergenos }]`
- [x] 5.4 Handle loading and error states in hook (return `{ products, total, isLoading, error }`)
- [x] 5.5 Implement `invalidate` function: on filter change, invalidate query to refetch
- [x] 5.6 Test query deduplication: rapid filter changes should not spam API

## 6. Frontend: Filter Components

- [x] 6.1 Create `src/features/ProductCatalog/components/CatalogFilters.tsx`
- [x] 6.2 Implement search input: bind to Zustand, triggers API call on Enter or button click
- [x] 6.3 Implement category dropdown: fetch categories from API or use static list
- [x] 6.4 Implement price range inputs: min and max price fields with validation (numbers only, min <= max)
- [x] 6.5 Implement allergen checkboxes: fetch allergens from `GET /api/v1/ingredientes?es_alergeno=true`
- [x] 6.6 Implement "Clear Filters" button: reset all filters and reload products
- [x] 6.7 Add loading skeleton for filters while fetching (categories, allergens)
- [x] 6.8 Style filters with Tailwind (responsive: vertical on mobile, horizontal on desktop)

## 7. Frontend: Product List and Pagination

- [x] 7.1 Create `src/features/ProductCatalog/components/ProductList.tsx`: render array of ProductCards
- [x] 7.2 Create `src/features/ProductCatalog/components/ProductCard.tsx`: display name, price, image, categories, stock badge
- [x] 7.3 Make ProductCard clickable: navigate to `/catalogo/{id}` on click or button
- [x] 7.4 Add image fallback: if imagen_url is null, show placeholder image
- [x] 7.5 Format price: use Intl.NumberFormat for currency (ARS or USD)
- [x] 7.6 Stock badge: show "In Stock" if disponible=true, "Sold Out" if false
- [x] 7.7 Create `src/features/ProductCatalog/components/PaginationControls.tsx`
- [x] 7.8 Implement pagination: Previous, Page display, Next buttons
- [x] 7.9 Disable Previous on page 1, disable Next on last page
- [x] 7.10 Show total count and page calculation: "Page 1 of 5" (ceil(total / limit))
- [x] 7.11 Clicking pagination refetches with new skip value and scrolls to top
- [x] 7.12 Add page size dropdown (10, 20, 50) that resets to page 1

## 8. Frontend: Catalog Page Layout

- [x] 8.1 Create `src/features/ProductCatalog/pages/CatalogPage.tsx`
- [x] 8.2 Layout structure: Navbar + Left sidebar filters + Main product grid + Pagination
- [x] 8.3 Responsive design: Sidebar collapses to top bar on mobile
- [x] 8.4 Loading state: show skeleton cards while fetching
- [x] 8.5 Empty state: "No products found" message if results are 0
- [x] 8.6 Error state: display error message with "Retry" button if API fails
- [x] 8.7 Grid layout: 3-4 columns on desktop, 1-2 on tablet, 1 on mobile (Tailwind)

## 9. Frontend: Product Detail Page

- [x] 9.1 Create `src/features/ProductCatalog/pages/ProductDetailPage.tsx`
- [x] 9.2 Extract ID from URL param and fetch product via `getProductDetail(id)`
- [x] 9.3 Display product info: name, description, price, image (large), categories, ingredients with allergen badges
- [x] 9.4 Show "In Stock" / "Out of Stock" badge (do NOT show exact stock_cantidad)
- [x] 9.5 Display ingredients list with allergen indicators (e.g., ⚠️ or red badge for es_alergeno=true)
- [x] 9.6 Show "Back to Catalog" or breadcrumb navigation
- [x] 9.7 Handle 404: if product not found or not available (deleted/unavailable), show "Product not found"
- [x] 9.8 Loading skeleton: show placeholder while fetching
- [x] 9.9 Error handling: display error message with retry option
- [x] 9.10 Responsive layout: image on top (mobile) or left side (desktop)

## 10. Frontend: Styling and UX Polish

- [x] 10.1 Add Tailwind CSS classes to all components (colors, spacing, typography match design system)
- [x] 10.2 Add hover states to ProductCard (scale, shadow, cursor)
- [x] 10.3 Add active/focus states to filter inputs and buttons
- [x] 10.4 Add allergen badge styling: red background, white text, warning icon
- [x] 10.5 Add loading spinner component (if not already exists)
- [x] 10.6 Add error toast or inline error message styling
- [x] 10.7 Test accessibility: keyboard navigation, screen reader labels (alt text, aria-labels)
- [x] 10.8 Mobile responsiveness: test all pages on common breakpoints

## 11. Testing: Integration Tests

- [x] 11.1 Write test for catalog page load and default pagination
- [x] 11.2 Write test for search by name
- [x] 11.3 Write test for category filter
- [x] 11.4 Write test for price range filter
- [x] 11.5 Write test for allergen exclusion filter
- [x] 11.6 Write test for combined filters
- [x] 11.7 Write test for pagination: next/previous page navigation
- [x] 11.8 Write test for error states: 404, 500, network error
- [x] 11.9 Write test for product detail page
- [x] 11.10 Write test for loading states (skeleton display)
- [x] 11.11 Verify no N+1 queries via backend query counting

## 12. Documentation and Code Review

- [x] 12.1 Update `docs/Integrador.txt` to document public catalog endpoints
- [x] 12.2 Add JSDoc comments to key functions (hooks, API calls, Zustand store)
- [x] 12.3 Create a README section in `src/features/ProductCatalog/README.md` documenting structure and usage
- [x] 12.4 Ensure conventional commits: `feat(catalog): <description>`, `test(catalog): <description>`, etc.
- [x] 12.5 Code review: check for TypeScript errors, eslint warnings, unused imports
- [x] 12.6 Performance review: verify query deduplication, no unnecessary re-renders
- [x] 12.7 Final QA: manual test all filters, pagination, detail page, responsive design

---

**Total Tasks**: 72  
**Estimated Duration**: 12-16 hours  
**Phase Order**: Backend (1-2h) → Frontend structure (1h) → API integration (1h) → State management (1h) → Components (6h) → Styling (1h) → Testing (2h) → Documentation (1h)
