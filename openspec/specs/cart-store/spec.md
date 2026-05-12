## ADDED Requirements

### Requirement: Cart Store — Initial State
The cartStore SHALL initialize with an empty items array.

#### Scenario: Empty cart on first load
- **GIVEN** a user visits the site for the first time
- **WHEN** the cartStore initializes
- **THEN** `items` SHALL be an empty array `[]`
- **AND** `totalItems()` SHALL return `0`
- **AND** `total()` SHALL return `0`

### Requirement: Cart Store — Add Item
The cartStore SHALL provide an `addItem` action that adds a product to the cart or increments the quantity if the product already exists (RN-CR03).

#### Scenario: Add new product to empty cart
- **GIVEN** the cart is empty
- **WHEN** `addItem({ producto: { id: 1, nombre: 'Pizza', precio: 100 }, cantidad: 2 })` is called
- **THEN** `items` SHALL contain one entry with `productoId: 1`, `cantidad: 2`, and the product details

#### Scenario: Add existing product increments quantity (no duplicate)
- **GIVEN** the cart contains `{ productoId: 1, cantidad: 2 }`
- **WHEN** `addItem({ producto: { id: 1 }, cantidad: 1 })` is called
- **THEN** `items.length` SHALL remain `1`
- **AND** the item's `cantidad` SHALL be `3`

#### Scenario: Add item with personalization (excluded ingredients)
- **GIVEN** a product has removable ingredients with IDs `[5, 7]`
- **WHEN** `addItem({ producto: { id: 2 }, cantidad: 1, personalizacion: [5] })` is called
- **THEN** the item SHALL store `personalizacion: [5]`

#### Scenario: Add same product with different personalization creates separate entry
- **GIVEN** the cart contains `{ productoId: 1, personalizacion: [5] }`
- **WHEN** `addItem({ producto: { id: 1 }, cantidad: 1, personalizacion: [7] })` is called
- **THEN** the cart SHALL have two separate entries for productId 1
- **AND** each entry SHALL maintain its own `personalizacion` and `cantidad`

### Requirement: Cart Store — Remove Item
The cartStore SHALL provide a `removeItem` action that removes a product from the cart by `productoId`.

#### Scenario: Remove item from cart
- **GIVEN** the cart contains `{ productoId: 1, cantidad: 2 }`
- **WHEN** `removeItem(1)` is called
- **THEN** `items` SHALL NOT contain any entry with `productoId: 1`

#### Scenario: Remove non-existent item is no-op
- **GIVEN** the cart is empty
- **WHEN** `removeItem(999)` is called
- **THEN** `items` SHALL remain `[]`

### Requirement: Cart Store — Update Quantity
The cartStore SHALL provide an `updateQuantity` action that changes the quantity of a specific item.

#### Scenario: Update quantity of existing item
- **GIVEN** the cart contains `{ productoId: 1, cantidad: 2 }`
- **WHEN** `updateQuantity(1, 5)` is called
- **THEN** the item's `cantidad` SHALL be `5`

#### Scenario: Update quantity to 0 removes the item
- **GIVEN** the cart contains `{ productoId: 1, cantidad: 2 }`
- **WHEN** `updateQuantity(1, 0)` is called
- **THEN** the item SHALL be removed from the cart

#### Scenario: Update quantity of non-existent item is no-op
- **GIVEN** the cart is empty
- **WHEN** `updateQuantity(999, 3)` is called
- **THEN** `items` SHALL remain `[]`

### Requirement: Cart Store — Clear Cart
The cartStore SHALL provide a `clearCart` action that removes all items from the cart.

#### Scenario: Clear cart with items
- **GIVEN** the cart contains 3 items
- **WHEN** `clearCart()` is called
- **THEN** `items` SHALL be `[]`
- **AND** `totalItems()` SHALL return `0`

### Requirement: Cart Store — Total Items Selector
The cartStore SHALL provide a `totalItems` selector that returns the sum of all item quantities.

#### Scenario: Total items with multiple quantities
- **GIVEN** the cart has `{ productoId: 1, cantidad: 2 }` and `{ productoId: 2, cantidad: 3 }`
- **WHEN** `totalItems()` is called
- **THEN** it SHALL return `5`

### Requirement: Cart Store — Subtotal Selector
The cartStore SHALL provide a `subtotal` selector that returns the sum of `precio * cantidad` for each item.

#### Scenario: Subtotal calculation
- **GIVEN** the cart has `{ productoId: 1, precio: 100, cantidad: 2 }` and `{ productoId: 2, precio: 50, cantidad: 3 }`
- **WHEN** `subtotal()` is called
- **THEN** it SHALL return `350` (200 + 150)

### Requirement: Cart Store — Costo Envío Selector
The cartStore SHALL provide a `costoEnvio` selector that returns the flat shipping rate of $50 if there are items in the cart, or $0 if the cart is empty.

#### Scenario: Costo envío with items
- **GIVEN** the cart has at least one item
- **WHEN** `costoEnvio()` is called
- **THEN** it SHALL return `50`

#### Scenario: Costo envío with empty cart
- **GIVEN** the cart is empty
- **WHEN** `costoEnvio()` is called
- **THEN** it SHALL return `0`

### Requirement: Cart Store — Total Selector
The cartStore SHALL provide a `total` selector that returns `subtotal() + costoEnvio()`.

#### Scenario: Total calculation
- **GIVEN** the cart has items with `subtotal() = 350` and `costoEnvio() = 50`
- **WHEN** `total()` is called
- **THEN** it SHALL return `400`

### Requirement: Cart Store — Persistence
The cartStore SHALL persist its items to localStorage using Zustand's persist middleware with the key `food-store-cart`.

#### Scenario: Cart survives page refresh
- **GIVEN** the cart has items
- **WHEN** the page is refreshed
- **THEN** the cart SHALL retain all items, quantities, and personalization

#### Scenario: Cart survives browser close and reopen
- **GIVEN** the cart has items
- **WHEN** the browser is closed and reopened
- **THEN** the cart SHALL retain all items (localStorage persistence)

#### Scenario: Cart survives logout and login
- **GIVEN** a user with items in the cart logs out
- **WHEN** the same user logs back in
- **THEN** the cart SHALL retain all items

### Requirement: Cart Store — Partialize
The cartStore SHALL use `partialize` to persist only the `items` array, excluding computed selectors and transient state.

#### Scenario: Only items persisted to localStorage
- **GIVEN** the cart has items
- **WHEN** inspecting localStorage key `food-store-cart`
- **THEN** the persisted state SHALL contain only `{ items: [...] }`
- **AND** SHALL NOT contain `totalItems`, `subtotal`, `costoEnvio`, or `total` functions

### Requirement: Cart Store — Personalization Validation
The cartStore SHALL accept `personalizacion` as an array of ingredient IDs representing excluded (removed) ingredients. Only ingredients marked as `es_removible = true` in the product SHALL be customizable (RN-CR04, RN-CR05).

#### Scenario: Personalization with valid ingredient IDs
- **GIVEN** a product with removable ingredients `[3, 5, 7]`
- **WHEN** `addItem({ producto, cantidad: 1, personalizacion: [5, 7] })` is called
- **THEN** the item SHALL store `personalizacion: [5, 7]`

#### Scenario: Personalization with empty array means no exclusions
- **GIVEN** a product with removable ingredients
- **WHEN** `addItem({ producto, cantidad: 1, personalizacion: [] })` is called
- **THEN** the item SHALL store `personalizacion: []`
