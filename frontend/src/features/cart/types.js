/**
 * Cart store types for CHANGE-08 (Shopping Cart)
 *
 * - CartItem stores a snapshot of product data at the time of adding.
 * - personalizacion is an array of ingredient IDs that the user wants excluded/removed.
 * - Duplicate detection uses productoId + personalizacion (same product with different
 *   personalization = separate cart entries).
 */
export const COSTO_ENVIO_FLAT = 50;
export const CART_STORAGE_KEY = 'food-store-cart';
export const CART_MAX_ITEMS = 50;
//# sourceMappingURL=types.js.map