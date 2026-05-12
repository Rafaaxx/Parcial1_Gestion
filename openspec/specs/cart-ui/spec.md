## ADDED Requirements

### Requirement: Cart Badge — Item Count Display
The system SHALL display a CartBadge component in the navigation bar showing the total number of items in the cart.

#### Scenario: Cart badge shows correct count
- **GIVEN** the cart has 3 items
- **WHEN** the navbar renders
- **THEN** a badge SHALL display the number `3` next to the cart icon

#### Scenario: Cart badge shows 0 when cart is empty
- **GIVEN** the cart is empty
- **WHEN** the navbar renders
- **THEN** the badge SHALL display `0` or be hidden

#### Scenario: Cart badge updates reactively
- **GIVEN** the CartBadge is displayed with count `2`
- **WHEN** a new item is added to the cart
- **THEN** the badge SHALL update to `3` without page refresh

### Requirement: Cart Drawer — Open and Close
The system SHALL provide a CartDrawer component that slides in from the right side of the screen, showing the cart contents.

#### Scenario: Open cart drawer
- **GIVEN** a user is browsing the catalog
- **WHEN** the user clicks the cart icon in the navbar
- **THEN** a drawer SHALL slide in from the right side
- **AND** it SHALL display all items in the cart

#### Scenario: Close cart drawer via close button
- **GIVEN** the cart drawer is open
- **WHEN** the user clicks the close (X) button
- **THEN** the drawer SHALL slide out and close

#### Scenario: Close cart drawer via overlay click
- **GIVEN** the cart drawer is open
- **WHEN** the user clicks the dark overlay behind the drawer
- **THEN** the drawer SHALL close

### Requirement: Cart Drawer — Item Display
Each item in the cart drawer SHALL display: product name, unit price, quantity, subtotal per line, and excluded ingredients (if any).

#### Scenario: Display item details
- **GIVEN** the cart contains `{ nombre: 'Pizza', precio: 100, cantidad: 2, personalizacion: [5] }`
- **WHEN** the cart drawer renders
- **THEN** it SHALL show: "Pizza", "$100.00", "x2", line subtotal "$200.00", and "Sin: [ingrediente_name]"

#### Scenario: Display item without personalization
- **GIVEN** the cart contains `{ nombre: 'Empanada', precio: 50, cantidad: 3, personalizacion: [] }`
- **WHEN** the cart drawer renders
- **THEN** it SHALL NOT show any "Sin:" message

### Requirement: Cart Drawer — Quantity Controls
Each item in the cart drawer SHALL have increment (+) and decrement (-) buttons to adjust quantity.

#### Scenario: Increment quantity
- **GIVEN** the cart drawer shows item with `cantidad: 1`
- **WHEN** the user clicks the (+) button
- **THEN** the quantity SHALL update to `2`
- **AND** the line subtotal SHALL update accordingly

#### Scenario: Decrement to 0 removes item
- **GIVEN** the cart drawer shows item with `cantidad: 1`
- **WHEN** the user clicks the (-) button
- **THEN** the item SHALL be removed from the cart drawer

### Requirement: Cart Drawer — Remove Button
Each item in the cart drawer SHALL have a remove (trash/bin) button that removes the item entirely.

#### Scenario: Remove item via trash button
- **GIVEN** the cart has 2 items
- **WHEN** the user clicks the remove button on one item
- **THEN** that item SHALL be removed from the cart
- **AND** the remaining item SHALL still be displayed

### Requirement: Cart Drawer — Summary Section
The cart drawer SHALL display a summary section at the bottom showing subtotal, shipping cost, and total, plus a checkout button.

#### Scenario: Summary calculation
- **GIVEN** the cart has items with subtotal `$350.00` and shipping `$50.00`
- **WHEN** the cart drawer renders the summary
- **THEN** it SHALL show:
  - Subtotal: `$350.00`
  - Envío: `$50.00`
  - **Total: `$400.00`**

#### Scenario: Checkout button (disabled placeholder)
- **GIVEN** the cart drawer is open with items
- **WHEN** the summary section renders
- **THEN** it SHALL display a checkout button labeled "Ir a pagar"
- **AND** the button SHALL be disabled with a tooltip "Próximamente" (since CHANGE-09 is not implemented)

### Requirement: Add to Cart Button — Product Card
The system SHALL display an "Agregar al carrito" button on each product card in the catalog listing.

#### Scenario: Add to cart from catalog listing
- **GIVEN** a product card for "Pizza" at $100.00
- **WHEN** the user clicks "Agregar al carrito"
- **THEN** one unit of "Pizza" SHALL be added to the cart
- **AND** a visual feedback (toast or badge animation) SHALL confirm the action

#### Scenario: Product already in cart shows quantity
- **GIVEN** "Pizza" is already in the cart with `cantidad: 2`
- **WHEN** the user views the product card
- **THEN** the button SHALL show "En carrito (2)" or similar indicator

### Requirement: Add to Cart — Product Detail Page
The product detail page SHALL have a quantity selector, ingredient customizer (for removable ingredients), and an "Agregar al carrito" button.

#### Scenario: Add to cart with custom quantity from detail
- **GIVEN** the product detail page for "Pizza" at $100.00
- **WHEN** the user sets quantity to `3` and clicks "Agregar al carrito"
- **THEN** `addItem({ ..., cantidad: 3 })` SHALL be called
- **AND** the cart SHALL reflect 3 units of "Pizza"

#### Scenario: Customize removable ingredients before adding
- **GIVEN** "Pizza" has ingredient "Cebolla" with `es_removible: true`
- **WHEN** the user toggles "Cebolla" off in the IngredientCustomizer and clicks "Agregar al carrito"
- **THEN** the cart item SHALL store `personalizacion: [cebolla_id]`

#### Scenario: Only removable ingredients shown in customizer
- **GIVEN** "Pizza" has ingredients "Queso" (es_removible: false) and "Cebolla" (es_removible: true)
- **WHEN** the IngredientCustomizer renders
- **THEN** only "Cebolla" SHALL appear as a toggleable option
- **AND** "Queso" SHALL NOT be toggleable

### Requirement: Empty Cart State
The system SHALL display an empty cart state when the cart has no items.

#### Scenario: Empty cart message
- **GIVEN** the cart is empty
- **WHEN** the user opens the cart drawer
- **THEN** a message "Tu carrito está vacío" SHALL be displayed
- **AND** a link/button to "Ver catálogo" SHALL be shown
