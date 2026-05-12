# Specification: product-detail-page

Public product detail page with full product information, including ingredients and allergens.

---

## ADDED Requirements

### Requirement: Product detail page accessible from catalog
The system SHALL provide a detail page for each product accessible via `/catalogo/{id}` or `/productos/{id}`.

#### Scenario: User navigates to product detail
- **WHEN** user clicks on a product card in catalog
- **THEN** system navigates to `/catalogo/5` (or equivalent URL)
- **AND** page mounts and fetches `GET /api/v1/productos/5`

#### Scenario: Direct URL access
- **WHEN** user directly enters `/catalogo/123` in browser
- **THEN** system fetches `GET /api/v1/productos/123`
- **AND** displays product details if available

#### Scenario: Product not found
- **WHEN** user visits detail page for non-existent product (e.g., `/catalogo/99999`)
- **THEN** system receives HTTP 404 from backend
- **AND** displays "Product not found" message
- **AND** provides "Back to Catalog" link

---

### Requirement: Product information display
The system SHALL display complete product information including name, description, price, image, categories, and ingredients.

#### Scenario: Product detail content
- **WHEN** page loads product detail
- **THEN** displays:
  - Large product image (or gallery)
  - Product name (heading)
  - Short description
  - Price (formatted as currency)
  - Availability badge ("In Stock" or "Out of Stock")
  - Categories (breadcrumb or tags)
  - Ingredients section with allergen indicators
  - "Add to Cart" button (for future phases)

#### Scenario: Product image display
- **WHEN** product has image_url
- **THEN** displays image in full resolution (or carousel if multiple images)
- **WHEN** product has no image_url
- **THEN** displays placeholder image

#### Scenario: Price display
- **WHEN** page displays price
- **THEN** formats as currency (e.g., "$99.50" or "99,50 ARS")
- **AND** matches backend currency format

---

### Requirement: Ingredients and allergens
The system SHALL display all ingredients associated with a product, clearly marking which are allergens.

#### Scenario: Ingredients list
- **WHEN** user views product detail
- **THEN** system displays "Ingredients" section with list of ingredient names
- **AND** each ingredient that is an allergen (es_alergeno=true) is clearly marked
- **AND** allergen indicator (e.g., ⚠️ icon or "ALLERGEN" badge) is visible

#### Scenario: Allergen badge styling
- **WHEN** ingredient is marked as allergen
- **THEN** it displays with distinctive styling (e.g., red background, warning icon, bold text)
- **AND** user can immediately identify allergens without reading fine print

#### Scenario: No ingredients
- **WHEN** product has no associated ingredients
- **THEN** displays "No ingredients listed" or similar message
- **AND** does not crash or show empty section

#### Scenario: Removable ingredients for customization (future scope)
- **WHEN** product has ingredient marked as removable (es_removible=true)
- **THEN** (in future phases with cart) user can remove it from order
- **AND** detail page may indicate which ingredients can be customized

---

### Requirement: Categories display
The system SHALL display the categories a product belongs to.

#### Scenario: Primary category
- **WHEN** product is associated with categories
- **THEN** displays categories prominently (e.g., breadcrumb: "Home > Pizzas > Margherita")
- **OR** displays as tags: "Pizza", "Italian", "Vegetarian"

#### Scenario: Multiple categories
- **WHEN** product belongs to multiple categories
- **THEN** displays all associated categories
- **AND** does not duplicate categories

---

### Requirement: Stock status (no exact quantity)
The system SHALL display stock availability without revealing exact quantities.

#### Scenario: In-stock product
- **WHEN** product has stock > 0
- **THEN** displays "In Stock" or similar badge
- **AND** does NOT show exact quantity (e.g., "15 units" is NOT shown)

#### Scenario: Out-of-stock product
- **WHEN** product has stock <= 0 or disponible=false
- **THEN** displays "Out of Stock" or "Sold Out" badge
- **AND** "Add to Cart" button (if present) is disabled or hidden

---

### Requirement: Public endpoint (no authentication)
The system SHALL allow unauthenticated access to product detail.

#### Scenario: Anonymous user views detail
- **WHEN** unauthenticated user navigates to `/catalogo/5`
- **THEN** system fetches `GET /api/v1/productos/5` without auth header
- **AND** displays full product information
- **AND** no 401 or 403 error is raised

---

### Requirement: Only available products are viewable
The system SHALL hide deleted or unavailable products from detail view.

#### Scenario: Unavailable product
- **WHEN** user tries to access product with disponible=false or deleted_at IS NOT NULL
- **THEN** system returns HTTP 404
- **AND** displays "Product not found" message
- **AND** does not reveal product exists but is hidden

---

### Requirement: Backend response schema (ProductoDetail)
The system SHALL return detailed product information with all associations.

#### Scenario: Product detail response structure
- **WHEN** client calls `GET /api/v1/productos/{id}`
- **THEN** response includes:
  - `id`, `nombre`, `descripcion`, `precio_base`
  - `imagen_url` (or null if not set)
  - `disponible: boolean`
  - `categorias: CategoriaBasico[]` — array of categories with id, nombre
  - `ingredientes: IngredienteDetail[]` — array with id, nombre, es_alergeno, es_removible
  - `stock_cantidad: int | null` — stock (only for authenticated admin/stock, null for public)
  - `created_at`, `updated_at` (optional)

#### Scenario: No stock quantity in public response
- **WHEN** unauthenticated user calls `GET /api/v1/productos/{id}`
- **THEN** response does NOT include exact `stock_cantidad`
- **AND** includes only availability flag (in_stock / out_of_stock via disponible)

---

### Requirement: Loading and error states (detail page)
The system SHALL display appropriate states during loading and on errors.

#### Scenario: Loading state on page mount
- **WHEN** detail page mounts
- **THEN** displays loading spinner or skeleton content
- **AND** main content area is disabled until data loads

#### Scenario: API error on detail fetch
- **WHEN** `GET /api/v1/productos/{id}` returns error
- **THEN** displays error message: "Failed to load product details"
- **AND** shows "Back to Catalog" or "Retry" button

#### Scenario: Page not found
- **WHEN** user accesses invalid product ID
- **THEN** system receives HTTP 404
- **AND** displays "This product is not available"
- **AND** provides navigation back to catalog

---

### Requirement: Browser history and navigation
The system SHALL support browser back button and internal navigation links.

#### Scenario: Back button from detail
- **WHEN** user presses browser back button
- **THEN** system returns to previous page (catalog with same filters/pagination)

#### Scenario: "Back to Catalog" link
- **WHEN** user clicks "Back to Catalog" link on detail page
- **THEN** system navigates to `/catalogo` with filters reset
- **OR** navigates to previous catalog state (with filters preserved if using query params)
