## Context

**Current State**: CHANGE-06 has established the product data model and backend CRUD/stock endpoints (`GET /api/v1/productos`, `GET /api/v1/productos/{id}`, etc.). These endpoints already support public read access (no authentication required).

**Constraints**:
- Frontend currently has no catalog UI — users cannot browse products without admin/stock roles
- Product detail endpoint exists but lacks eager loading of associations (categories, ingredients)
- No pagination control on frontend — no UX for handling large product lists
- No search/filter UI — customers cannot find products by name, price, or allergen restrictions

**Stakeholders**: Customers (primary), Product team (requirements), Backend team (endpoint stability)

---

## Goals / Non-Goals

**Goals:**
- ✅ Create React UI page for public product catalog (no login required)
- ✅ Support search by name, filter by category, price range, and allergen exclusion
- ✅ Implement pagination with skip/limit controls on frontend
- ✅ Display product cards with name, price, image, and stock indicator
- ✅ Ensure backend endpoints are stable and properly document the public contract
- ✅ Maintain strict separation: no customer-specific data (addresses, orders, cart) visible on catalog

**Non-Goals:**
- ❌ Personalization engine (e.g., "recommended for you")
- ❌ Advanced search (NLP, full-text search indices) — ILIKE suffices for v1
- ❌ Product ratings/reviews (scope for future)
- ❌ Inventory reservations — catalog shows real-time stock only

---

## Decisions

### 1. **Backend: Public Endpoints Already Exist, Document Formally**
**Decision**: Reuse existing `GET /api/v1/productos` and `GET /api/v1/productos/{id}` endpoints from CHANGE-06. Create formal OpenAPI schema documentation.

**Rationale**: 
- CHANGE-06 already implemented these endpoints with filters (skip, limit, categoria, busqueda, precio_desde, precio_hasta)
- Reduces scope — no backend code changes, only documentation
- Public read-only endpoints pose no security risk

**Alternative Considered**: Create new `/api/v1/catalogo/` namespace — rejected (unnecessary API proliferation, complicates versioning)

---

### 2. **Frontend: Zustand for Filter State, TanStack Query for Server State**
**Decision**: 
- **Zustand store** (`src/stores/catalogStore.ts`): manages UI filters (searchText, selectedCategory, priceRange, excludedAllergens)
- **TanStack Query** (`useProducts()` hook): caches server data, handles refetch on filter changes
- Query key includes filters: `['productos', { skip, limit, categoria, busqueda, ... }]`

**Rationale**:
- Zustand handles transient UI state (user is typing in search box, hasn't hit enter)
- TanStack Query deduplicates requests, caches results, handles stale-while-revalidate
- Separates concerns: filter logic (Zustand) vs. server sync (TanStack Query)

**Alternative Considered**: Redux for filters — rejected (over-engineering for simple state, Zustand is already established in the project)

---

### 3. **Frontend: Feature-Sliced Design Structure**
**Decision**: Organize catalog UI under `src/features/ProductCatalog/` with internal layers:
```
src/features/ProductCatalog/
├── pages/CatalogPage.tsx         # Route page
├── components/
│   ├── ProductCard.tsx           # Reusable product card (name, price, image, stock badge)
│   ├── ProductList.tsx           # Render list of cards
│   ├── CatalogFilters.tsx        # Search, category, price, allergen filters
│   └── PaginationControls.tsx    # Skip/limit controls
├── hooks/
│   └── useCatalogFilters.ts      # Custom hook: returns { filters, setFilters, products, loading }
├── api/
│   └── catalogApi.ts             # Axios calls (GET /productos)
├── stores/
│   └── catalogStore.ts           # Zustand: filters state
├── types/
│   └── catalog.ts                # CatalogFilters, ProductCard TypeScript interfaces
└── index.ts                      # Public exports
```

**Rationale**: Follows established Feature-Sliced Design (FSD) convention. Keeps concerns isolated, allows future extraction as shared component library.

---

### 4. **Product Detail: Eager Loading of Associations**
**Decision**: Backend `GET /api/v1/productos/{id}` will use SQLAlchemy `selectinload()` to fetch categories and ingredients in a single round trip.

**Rationale**:
- Detail page needs ingredients (to show allergens) and categories — requires N+1 prevention
- `selectinload()` avoids SELECT N+1 on product card render
- Reduces latency: 1 roundtrip instead of 3 (product + categories + ingredients)

**Alternative Considered**: Separate endpoints for ingredients/categories — rejected (adds complexity, increases latency)

---

### 5. **Stock Display: Show Status, Not Quantity**
**Decision**: 
- Public list (`ProductCard`): show only badge ("In Stock" / "Out of Stock") or "Stock Sold Out" — never exact quantity
- Public detail: same — show "Available" / "Sold Out" indicator
- Backend: `ProductoListItem` schema excludes `stock_cantidad` field entirely

**Rationale**:
- Security/UX: don't reveal inventory levels to competitors
- User doesn't need exact quantity (1 item or 100 items — both say "available")

---

### 6. **Allergen Filter: Exclusion Logic**
**Decision**: Query parameter `excluirAlergenos=1,3,7` excludes products containing those ingredient IDs.

**Database**: `NOT EXISTS (SELECT 1 FROM ProductoIngrediente pi WHERE pi.producto_id = p.id AND pi.ingrediente_id IN (1,3,7))`

**Rationale**:
- User's mental model: "I'm allergic to peanuts (id=5), hide products with peanuts"
- Simpler than inclusion logic ("show only products with X")
- Reduces returned rows early (filter at query level, not in app code)

---

### 7. **Pagination: Skip/Limit (Offset-Limit)**
**Decision**: Use `skip` and `limit` query params (not cursor-based pagination).

**Rationale**:
- Simpler for frontend pagination controls ("page 1, 2, 3..." with page size dropdown)
- Acceptable for product catalog (< 50k SKUs typically)
- Cursor pagination adds complexity without benefit for this use case

---

## Risks / Trade-offs

| Risk | Probability | Mitigation |
|------|-------------|-----------|
| **N+1 query on detail page** (if `selectinload()` not used) | HIGH | Implement `selectinload(Producto.categorias, Producto.ingredientes)` in repository. Test with profiler. |
| **Slow ILIKE search on large datasets** (no FTS index) | MEDIUM | Add `CREATE INDEX idx_productos_nombre_ilike ON productos (nombre COLLATE "C")` if search becomes bottleneck. Monitor query times. |
| **Typo in filter params** (typo in `excluirAlergenos=1,3,x`) causes silent failure | LOW | Frontend validates allergen IDs before sending; backend silently ignores invalid IDs (safe default). |
| **Cache invalidation on product updates** | MEDIUM | TanStack Query key includes all filters. On product update, invalidate `['productos']` with `queryClient.invalidateQueries({ queryKey: ['productos'] })`. |
| **Pagination UX break** (user on page 3, page shrinks to 2 pages) | LOW | Show "No results" message if skip >= total; don't render invalid pages. |

---

## Migration Plan

**Deployment Order**:
1. ✅ Backend: No changes (endpoints already exist from CHANGE-06)
2. 🆕 Frontend: Develop React components and Zustand store locally
3. 🔧 Test: Verify pagination, search, allergen filter with mock data
4. 🚀 Deploy: Merge to `main`, no backend rollback needed (read-only)

**Rollback**: N/A — frontend changes only, easy to revert. Backend endpoints are read-only and stable.

---

## Open Questions

1. **Product image serving**: Are images stored in cloud (S3) or served from backend? How is `image_url` populated in `Producto` model? (Answer: Check CHANGE-06 design or Integrador.txt for image storage strategy)
2. **Sorting**: Should catalog support sorting by price, newest, bestseller? (Proposal: defer to CHANGE-08 or later optimization)
3. **Category tree rendering**: Subcategories (hierarchical)? Flat list? (Proposal: flat list for v1, show parent + child as breadcrumb)
