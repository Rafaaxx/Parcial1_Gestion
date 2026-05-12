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

- [ ] 2.1 Create directory structure: `src/features/ProductCatalog/` with subdirs: pages, components, hooks, stores, api, types
- [ ] 2.2 Create `src/pages/CatalogPage.tsx` as the main route page
- [ ] 2.3 Create TypeScript types: `src/features/ProductCatalog/types/catalog.ts` with ProductCard, ProductListItem, ProductDetail, CatalogFilters interfaces
- [ ] 2.4 Configure route: Add `/catalogo` route to React Router (both `:id` for detail and root for listing)
- [ ] 2.5 Update navigation: Add "Catalog" link to Navbar (accessible even when not logged in)

## 3. Frontend: API Integration

- [ ] 3.1 Create `src/features/ProductCatalog/api/catalogApi.ts` with axios calls
- [ ] 3.2 Implement `getProducts(filters)` function: `GET /api/v1/productos` with query params
- [ ] 3.3 Implement `getProductDetail(id)` function: `GET /api/v1/productos/{id}`
- [ ] 3.4 Implement error handling: map 404 to "Product not found", 500 to "Server error"
- [ ] 3.5 Add TypeScript strict typing for API responses and request params

## 4. Frontend: State Management (Zustand)

- [ ] 4.1 Create `src/features/ProductCatalog/stores/catalogStore.ts`
- [ ] 4.2 Define store state: searchText, selectedCategory, priceFrom, priceTo, excludedAllergens, currentPage, limit
- [ ] 4.3 Define actions: setSearch, setCategory, setPriceRange, setAllergenExclusions, setPage, resetFilters
- [ ] 4.4 Implement selector: getQueryParams() — returns object ready for API call
- [ ] 4.5 Implement selector: isFilterActive() — returns true if any filter applied (for "Clear Filters" button)

## 5. Frontend: TanStack Query Integration

- [ ] 5.1 Create custom hook `src/features/ProductCatalog/hooks/useCatalogFilters.ts`
- [ ] 5.2 Implement `useProducts()` hook: wraps `useQuery` with catalog API call
- [ ] 5.3 Use query key with filters: `['productos', { skip, limit, categoria, busqueda, precio_desde, precio_hasta, excluirAlergenos }]`
- [ ] 5.4 Handle loading and error states in hook (return `{ products, total, isLoading, error }`)
- [ ] 5.5 Implement `invalidate` function: on filter change, invalidate query to refetch
- [ ] 5.6 Test query deduplication: rapid filter changes should not spam API

## 6. Frontend: Filter Components

- [ ] 6.1 Create `src/features/ProductCatalog/components/CatalogFilters.tsx`
- [ ] 6.2 Implement search input: bind to Zustand, triggers API call on Enter or button click
- [ ] 6.3 Implement category dropdown: fetch categories from API or use static list
- [ ] 6.4 Implement price range inputs: min and max price fields with validation (numbers only, min <= max)
- [ ] 6.5 Implement allergen checkboxes: fetch allergens from `GET /api/v1/ingredientes?es_alergeno=true`
- [ ] 6.6 Implement "Clear Filters" button: reset all filters and reload products
- [ ] 6.7 Add loading skeleton for filters while fetching (categories, allergens)
- [ ] 6.8 Style filters with Tailwind (responsive: vertical on mobile, horizontal on desktop)

## 7. Frontend: Product List and Pagination

- [ ] 7.1 Create `src/features/ProductCatalog/components/ProductList.tsx`: render array of ProductCards
- [ ] 7.2 Create `src/features/ProductCatalog/components/ProductCard.tsx`: display name, price, image, categories, stock badge
- [ ] 7.3 Make ProductCard clickable: navigate to `/catalogo/{id}` on click or button
- [ ] 7.4 Add image fallback: if imagen_url is null, show placeholder image
- [ ] 7.5 Format price: use Intl.NumberFormat for currency (ARS or USD)
- [ ] 7.6 Stock badge: show "In Stock" if disponible=true, "Sold Out" if false
- [ ] 7.7 Create `src/features/ProductCatalog/components/PaginationControls.tsx`
- [ ] 7.8 Implement pagination: Previous, Page display, Next buttons
- [ ] 7.9 Disable Previous on page 1, disable Next on last page
- [ ] 7.10 Show total count and page calculation: "Page 1 of 5" (ceil(total / limit))
- [ ] 7.11 Clicking pagination refetches with new skip value and scrolls to top
- [ ] 7.12 Add page size dropdown (10, 20, 50) that resets to page 1

## 8. Frontend: Catalog Page Layout

- [ ] 8.1 Create `src/features/ProductCatalog/pages/CatalogPage.tsx`
- [ ] 8.2 Layout structure: Navbar + Left sidebar filters + Main product grid + Pagination
- [ ] 8.3 Responsive design: Sidebar collapses to top bar on mobile
- [ ] 8.4 Loading state: show skeleton cards while fetching
- [ ] 8.5 Empty state: "No products found" message if results are 0
- [ ] 8.6 Error state: display error message with "Retry" button if API fails
- [ ] 8.7 Grid layout: 3-4 columns on desktop, 1-2 on tablet, 1 on mobile (Tailwind)

## 9. Frontend: Product Detail Page

- [ ] 9.1 Create `src/features/ProductCatalog/pages/ProductDetailPage.tsx`
- [ ] 9.2 Extract ID from URL param and fetch product via `getProductDetail(id)`
- [ ] 9.3 Display product info: name, description, price, image (large), categories, ingredients with allergen badges
- [ ] 9.4 Show "In Stock" / "Out of Stock" badge (do NOT show exact stock_cantidad)
- [ ] 9.5 Display ingredients list with allergen indicators (e.g., ⚠️ or red badge for es_alergeno=true)
- [ ] 9.6 Show "Back to Catalog" or breadcrumb navigation
- [ ] 9.7 Handle 404: if product not found or not available (deleted/unavailable), show "Product not found"
- [ ] 9.8 Loading skeleton: show placeholder while fetching
- [ ] 9.9 Error handling: display error message with retry option
- [ ] 9.10 Responsive layout: image on top (mobile) or left side (desktop)

## 10. Frontend: Styling and UX Polish

- [ ] 10.1 Add Tailwind CSS classes to all components (colors, spacing, typography match design system)
- [ ] 10.2 Add hover states to ProductCard (scale, shadow, cursor)
- [ ] 10.3 Add active/focus states to filter inputs and buttons
- [ ] 10.4 Add allergen badge styling: red background, white text, warning icon
- [ ] 10.5 Add loading spinner component (if not already exists)
- [ ] 10.6 Add error toast or inline error message styling
- [ ] 10.7 Test accessibility: keyboard navigation, screen reader labels (alt text, aria-labels)
- [ ] 10.8 Mobile responsiveness: test all pages on common breakpoints

## 11. Testing: Integration Tests

- [ ] 11.1 Write test for catalog page load and default pagination
- [ ] 11.2 Write test for search by name
- [ ] 11.3 Write test for category filter
- [ ] 11.4 Write test for price range filter
- [ ] 11.5 Write test for allergen exclusion filter
- [ ] 11.6 Write test for combined filters
- [ ] 11.7 Write test for pagination: next/previous page navigation
- [ ] 11.8 Write test for error states: 404, 500, network error
- [ ] 11.9 Write test for product detail page
- [ ] 11.10 Write test for loading states (skeleton display)
- [ ] 11.11 Verify no N+1 queries via backend query counting

## 12. Documentation and Code Review

- [ ] 12.1 Update `docs/Integrador.txt` to document public catalog endpoints
- [ ] 12.2 Add JSDoc comments to key functions (hooks, API calls, Zustand store)
- [ ] 12.3 Create a README section in `src/features/ProductCatalog/README.md` documenting structure and usage
- [ ] 12.4 Ensure conventional commits: `feat(catalog): <description>`, `test(catalog): <description>`, etc.
- [ ] 12.5 Code review: check for TypeScript errors, eslint warnings, unused imports
- [ ] 12.6 Performance review: verify query deduplication, no unnecessary re-renders
- [ ] 12.7 Final QA: manual test all filters, pagination, detail page, responsive design

---

**Total Tasks**: 72  
**Estimated Duration**: 12-16 hours  
**Phase Order**: Backend (1-2h) → Frontend structure (1h) → API integration (1h) → State management (1h) → Components (6h) → Styling (1h) → Testing (2h) → Documentation (1h)
