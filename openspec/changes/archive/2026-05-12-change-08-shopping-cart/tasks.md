## 1. Refactor cartStore (features/cart/store.ts)

- [x] 1.1 Update `CartItem` type: change `productoId` to `number`, add `costoEnvio` constant ($50), change `personalizacion` to `number[]` (ingredient IDs array) instead of `{ingredienteId, removido}[]`
- [x] 1.2 Add `costoEnvio` selector: flat rate $50 if items.length > 0, $0 if empty
- [x] 1.3 Fix `total()` selector to include `costoEnvio()`: `subtotal() + costoEnvio()`
- [x] 1.4 Update `addItem` to match spec: accept `(producto, cantidad?, personalizacion?)` signature, check by `productoId + personalizacion` for duplicate detection (same product with different personalization = separate entry)
- [x] 1.5 Ensure `partialize` only persists `items` array (already done, verify)
- [x] 1.6 Verify `removeItem`, `updateQuantity` work correctly with `number` IDs

## 2. Create Cart UI Components (features/cart/components/)

- [x] 2.1 Create `CartDrawer.tsx` — slide-over panel from right:
  - Opens/closes via state (isOpen, onClose)
  - Dark overlay behind drawer
  - Close button (X) and click-outside-to-close
  - Renders list of `CartItemRow` components
  - Shows empty state: "Tu carrito está vacío" + link to catálogo
- [x] 2.2 Create `CartItemRow.tsx` — individual item in drawer:
  - Product name, unit price, quantity with +/- controls, line subtotal
  - Delete/remove button
  - Shows "Sin: [ingredientes]" if personalization exists
  - Decrement to 0 removes the item
- [x] 2.3 Create `CartSummary.tsx` — bottom section of drawer:
  - Subtotal, costo de envío ($50), divider, total
  - Checkout button: disabled with tooltip "Próximamente" (CHANGE-09 not implemented)
- [x] 2.4 Create `useCartDrawer.ts` — custom hook + Zustand `cartUIStore` for shared drawer state across components

## 3. Integrate with Catalog (ProductCard + ProductDetail)

- [x] 3.1 Create `AddToCartButton.tsx` — reusable button component:
  - Props: producto, cantidad (default 1), personalizacion (default [])
  - Calls `addItem` from cartStore
  - Shows toast feedback on add
  - If product already in cart, show "En carrito (N)" indicator
- [x] 3.2 Create `IngredientCustomizer.tsx` — ingredient exclusion UI:
  - Receives list of ingredients with `es_removible` flag
  - Shows toggle for each removable ingredient
  - Returns array of excluded ingredient IDs
  - Only shows removable ingredients (filters es_removible=false)
- [x] 3.3 Update `ProductCard.tsx` — add "Agregar al carrito" button at bottom of card
  - Button text: "Agregar" or "En carrito (N)"
  - Prevents event propagation (stopPropagation)
  - Shows toast confirmation via AddToCartButton
- [x] 3.4 Update `ProductDetailPage` — add quantity selector + IngredientCustomizer + "Agregar al carrito" button
  - Section below product info with quantity controls (+/-)
  - IngredientCustomizer showing only removable ingredients
  - Big "Agregar al carrito" button
  - On add: reset customizer, show toast, update CartBadge reactively

## 4. Implement CartPage (/carrito)

- [x] 4.1 Update `CartPage.tsx` — replace "Próximamente" placeholder with full cart page:
  - Full-page layout with cart items table
  - Each row: image, name, unit price, quantity (+/-), personalization, subtotal, remove
  - Summary sidebar: subtotal, shipping, total
  - Checkout button (disabled, "Próximamente")
  - Empty state: illustration + "Tu carrito está vacío" + link to catálogo
- [x] 4.2 Add responsive design: mobile = stacked layout, desktop = table + sidebar

## 5. Wire Up CartDrawer in AppLayout

- [x] 5.1 Update `CartBadge.tsx` — clicking cart icon opens CartDrawer via `useCartUIStore.openCart()`
  - Import and use `useCartUIStore` for shared state
  - CartDrawer rendered in AppLayout (not inside CartBadge)
  - Link to /carrito kept as secondary action via NavMenu "Mi Carrito"
- [x] 5.2 Add `CartDrawer` to `AppLayout.tsx` — rendered below main content with isOpen/onClose from cartUIStore

## 6. UI Polish & Edge Cases

- [x] 6.1 Add product image thumbnail to CartDrawer items (CartItemRow shows 64x64 thumbnail)
- [x] 6.2 Toast notifications for: add item, remove item, clear cart
- [x] 6.3 Handle loading states: images use `loading="lazy"` with placeholder fallbacks
- [x] 6.4 Edge case: addItem guards `cantidad <= 0` — silently ignored
- [x] 6.5 Edge case: max quantity clamped to 50 (CART_MAX_ITEMS constant)
- [x] 6.6 CartBadge count updates reactively — Zustand persist + selector subscription handles cross-tab updates
