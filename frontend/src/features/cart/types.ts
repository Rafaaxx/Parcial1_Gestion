/**
 * Cart store types for CHANGE-08 (Shopping Cart)
 *
 * - CartItem stores a snapshot of product data at the time of adding.
 * - personalizacion is an array of ingredient IDs that the user wants excluded/removed.
 * - Duplicate detection uses productoId + personalizacion (same product with different
 *   personalization = separate cart entries).
 */

import type { IngredientInfo } from '@/features/ProductCatalog/types/catalog'

export interface CartItem {
  productoId: number
  nombre: string
  /** precio snapshot at the time the item was added to cart */
  precio: number
  imagenUrl: string
  cantidad: number
  /** IDs of ingredients the user chose to remove (excluded) */
  personalizacion: number[]
  /** Full ingredient info for display (names of excluded ingredients, etc.) */
  ingredientes: IngredientInfo[]
}

/**
 * Minimal product shape accepted by addItem.
 * Both ProductListItem and ProductDetail from the catalog match this interface.
 */
export interface ProductoParaCarrito {
  id: number
  nombre: string
  precio_base: number | string
  imagen?: string | null
  ingredientes?: IngredientInfo[]
}

export interface CartState {
  items: CartItem[]
  userId?: number | null

  // Actions
  addItem: (producto: ProductoParaCarrito, cantidad?: number, personalizacion?: number[]) => void
  removeItem: (productoId: number, personalizacion?: number[]) => void
  updateQuantity: (productoId: number, cantidad: number, personalizacion?: number[]) => void
  clearCart: () => void
  _init?: () => void

  // Selectors (computed)
  totalItems: () => number
  subtotal: () => number
  costoEnvio: () => number
  total: () => number
}

export const COSTO_ENVIO_FLAT = 50
export const CART_STORAGE_KEY = 'food-store-cart'
export const CART_MAX_ITEMS = 50
