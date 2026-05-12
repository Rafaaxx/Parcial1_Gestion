# Specification: catalog-ui

React UI components for browsing and filtering the public product catalog.

---

## ADDED Requirements

### Requirement: Catalog page (main page)
The system SHALL display a catalog page accessible without authentication at `/catalogo` (or `/catalog`).

#### Scenario: User visits catalog page
- **WHEN** unauthenticated user navigates to `/catalogo`
- **THEN** system renders a layout with:
  - Header/navbar (showing logo, search bar, login/register links)
  - Left sidebar or top bar with filters (search, category, price, allergens)
  - Main product grid/list area with product cards
  - Pagination controls at the bottom

#### Scenario: Page loads products on mount
- **WHEN** page mounts
- **THEN** system fetches `GET /api/v1/productos?skip=0&limit=20` (default pagination)
- **AND** displays a loading state while fetching
- **AND** shows products once loaded

#### Scenario: No products available
- **WHEN** filters result in 0 products
- **THEN** system shows "No products found" message instead of empty grid
- **AND** suggests refining filters

---

### Requirement: Product card component
The system SHALL display each product as a card with essential information.

#### Scenario: Product card content
- **WHEN** a product card is rendered
- **THEN** it displays:
  - Product name (clickable to detail page)
  - Product image (thumbnail)
  - Price (formatted as currency)
  - Category badge(s)
  - Stock status badge ("In Stock" or "Sold Out")
  - "View Details" or "Add to Cart" button (for later phases)

#### Scenario: Card is responsive
- **WHEN** viewing on mobile (< 768px width)
- **THEN** cards stack vertically or show 1-2 per row
- **WHEN** viewing on desktop (> 768px)
- **THEN** cards show 3-4 per row in a grid

#### Scenario: Image placeholder for missing images
- **WHEN** product has no image_url
- **THEN** card displays a generic "no image" placeholder
- **AND** does not break layout

---

### Requirement: Search input component
The system SHALL provide a search bar for filtering by product name.

#### Scenario: User types in search
- **WHEN** user types "pizza" in search input
- **THEN** Zustand store updates `searchText` state immediately (no API call yet)
- **AND** search input shows the typed text

#### Scenario: User submits search (on Enter or button click)
- **WHEN** user presses Enter or clicks "Search" button
- **THEN** system fetches `GET /api/v1/productos?busqueda=pizza&skip=0&limit=20`
- **AND** resets pagination to page 1
- **AND** displays new results (or loading spinner if fetching)

#### Scenario: Clear search
- **WHEN** user clears search input and presses Enter
- **THEN** system fetches all products (no busqueda filter)
- **AND** pagination resets to page 1

---

### Requirement: Category filter component
The system SHALL provide a dropdown or checkbox list to filter by category.

#### Scenario: User selects category
- **WHEN** user selects "Pizzas" from category dropdown
- **THEN** system fetches `GET /api/v1/productos?categoria=5&skip=0&limit=20` (assuming categoria_id=5)
- **AND** only products in that category are displayed
- **AND** pagination resets

#### Scenario: Clear category filter
- **WHEN** user selects "All Categories" or clears selection
- **THEN** system removes the categoria param and reloads

#### Scenario: Categories list is populated
- **WHEN** catalog page loads
- **THEN** category dropdown is populated from a static list or fetched from `GET /api/v1/categorias`
- **AND** "All Categories" is the default

---

### Requirement: Price range filter component
The system SHALL provide inputs to filter by minimum and maximum price.

#### Scenario: User enters price range
- **WHEN** user enters `precio_desde=50` and `precio_hasta=200` in input fields
- **THEN** clicking "Apply Filter" or pressing Enter fetches `GET /api/v1/productos?precio_desde=50&precio_hasta=200&skip=0&limit=20`
- **AND** only products in that range are displayed

#### Scenario: Only minimum price
- **WHEN** user enters only `precio_desde=100` (leaving precio_hasta empty)
- **THEN** system fetches `GET /api/v1/productos?precio_desde=100`
- **AND** returns all products >= 100

#### Scenario: Only maximum price
- **WHEN** user enters only `precio_hasta=500`
- **THEN** system fetches `GET /api/v1/productos?precio_hasta=500`
- **AND** returns all products <= 500

---

### Requirement: Allergen exclusion filter component
The system SHALL provide checkboxes or multi-select to exclude products with allergens.

#### Scenario: User excludes allergen
- **WHEN** user checks "Peanuts" in allergen list
- **THEN** system fetches `GET /api/v1/productos?excluirAlergenos=5` (assuming peanuts = id 5)
- **AND** displays only products without peanuts

#### Scenario: User excludes multiple allergens
- **WHEN** user checks "Peanuts", "Tree Nuts", "Dairy"
- **THEN** system fetches `GET /api/v1/productos?excluirAlergenos=5,6,7`
- **AND** displays products free of all three allergens

#### Scenario: Allergen list is available
- **WHEN** catalog page loads
- **THEN** allergen filter shows list of all allergens fetched from `GET /api/v1/ingredientes?es_alergeno=true`
- **AND** each allergen is a checkbox with label

---

### Requirement: Pagination controls
The system SHALL provide UI controls to navigate through paginated results.

#### Scenario: Pagination on initial load
- **WHEN** catalog shows results
- **THEN** displays pagination controls with:
  - "Previous" button (disabled if on page 1)
  - Page number display (e.g., "Page 1 of 5")
  - "Next" button (disabled if on last page)
  - Optional: page number input or dropdown for page size

#### Scenario: User clicks next page
- **WHEN** user clicks "Next"
- **THEN** system calculates new skip (e.g., skip=20 if limit=20)
- **AND** fetches `GET /api/v1/productos?skip=20&limit=20`
- **AND** scrolls to top of product grid

#### Scenario: User clicks previous page
- **WHEN** user clicks "Previous"
- **THEN** system decreases skip by limit
- **AND** fetches new page

#### Scenario: User changes page size
- **WHEN** user selects "Show 50 per page" from dropdown
- **THEN** system sets limit=50 and resets skip=0
- **AND** fetches `GET /api/v1/productos?skip=0&limit=50`

---

### Requirement: Combined filters work together
The system SHALL allow applying multiple filters simultaneously.

#### Scenario: User applies multiple filters
- **WHEN** user enters:
  - Search: "pizza"
  - Category: "Italian"
  - Price range: 50-200
  - Exclude: "Dairy"
  - Pagination: page 2 (skip=20, limit=20)
- **THEN** system fetches: `GET /api/v1/productos?busqueda=pizza&categoria=2&precio_desde=50&precio_hasta=200&excluirAlergenos=7&skip=20&limit=20`
- **AND** displays matching products

#### Scenario: Clear all filters
- **WHEN** user clicks "Clear Filters" button
- **THEN** all filters reset to defaults
- **AND** system fetches `GET /api/v1/productos?skip=0&limit=20`

---

### Requirement: Loading and error states
The system SHALL display appropriate states during data fetching and on errors.

#### Scenario: Loading state
- **WHEN** system is fetching products
- **THEN** displays loading spinner or skeleton cards
- **AND** pagination controls are disabled

#### Scenario: API error
- **WHEN** API call fails (e.g., HTTP 500)
- **THEN** displays error message: "Failed to load products. Please try again."
- **AND** shows "Retry" button
- **AND** allows user to try again

#### Scenario: Network error
- **WHEN** network is unavailable
- **THEN** displays error message: "No internet connection"
- **AND** caches last successful results (via TanStack Query)
- **AND** allows user to view cached data if available
