/**
 * Cart store for managing shopping cart state
 *
 * State: client-side only (Zustand + persist middleware → localStorage)
 * Persists only the `items` array (selectors are computed, not stored).
 * Cart is cleared when user changes (detected by userId in localStorage).
 */

import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { CartItem, CartState, ProductoParaCarrito } from './types'
import { COSTO_ENVIO_FLAT, CART_STORAGE_KEY, CART_MAX_ITEMS } from './types'

function buildItemKey(productoId: number, personalizacion: number[]): string {
  const sorted = [...personalizacion].sort()
  return `${productoId}_${JSON.stringify(sorted)}`
}

// Get current user ID from auth storage
function getCurrentUserId(): number | null {
  try {
    const stored = localStorage.getItem('food-store-auth')
    if (stored) {
      const parsed = JSON.parse(stored)
      return parsed.state?.user?.id || null
    }
  } catch {
    // Ignore parse errors
  }
  return null
}

// Check if stored cart belongs to current user
function getStoredUserId(): number | null {
  try {
    const stored = localStorage.getItem(CART_STORAGE_KEY)
    if (stored) {
      const data = JSON.parse(stored)
      return data.state?.userId || null
    }
  } catch {
    // Ignore
  }
  return null
}

export const useCartStore = create<CartState>()(
  persist(
    (set, get) => ({
      items: [],

      addItem: (producto: ProductoParaCarrito, cantidad = 1, personalizacion: number[] = []) => {
        // Verify user before adding items
        const currentUserId = getCurrentUserId()
        const storedUserId = getStoredUserId()
        
        // If user changed, clear cart first
        if (currentUserId && storedUserId && currentUserId !== storedUserId) {
          set({ items: [], userId: currentUserId })
        } else if (!storedUserId && currentUserId) {
          // No user was stored, set current user
          set({ userId: currentUserId })
        }

        if (cantidad <= 0) return

        const { items } = get()
        const productoId = producto.id
        const newKey = buildItemKey(productoId, personalizacion)

        const existingIndex = items.findIndex(
          (item) => buildItemKey(item.productoId, item.personalizacion) === newKey
        )

        if (existingIndex >= 0) {
          // Same product + same personalization → increment quantity
          const updated = [...items]
          const current = updated[existingIndex]
          const newCantidad = Math.min(current.cantidad + cantidad, CART_MAX_ITEMS)
          updated[existingIndex] = { ...current, cantidad: newCantidad }
          set({ items: updated })
        } else {
          // New entry
          const precio =
            typeof producto.precio_base === 'string'
              ? parseFloat(producto.precio_base)
              : producto.precio_base

          const newItem: CartItem = {
            productoId,
            nombre: producto.nombre,
            precio,
            imagenUrl: producto.imagen ?? '',
            cantidad: Math.min(cantidad, CART_MAX_ITEMS),
            personalizacion,
            ingredientes: producto.ingredientes ?? [],
          }
          set({ items: [...items, newItem] })
        }
      },

      removeItem: (productoId: number, personalizacion?: number[]) => {
        const { items } = get()
        if (personalizacion !== undefined) {
          const key = buildItemKey(productoId, personalizacion)
          set({ items: items.filter((i) => buildItemKey(i.productoId, i.personalizacion) !== key) })
        } else {
          set({ items: items.filter((i) => i.productoId !== productoId) })
        }
      },

      updateQuantity: (productoId: number, cantidad: number, personalizacion?: number[]) => {
        const { items } = get()

        if (cantidad <= 0) {
          // Remove the item
          if (personalizacion !== undefined) {
            const key = buildItemKey(productoId, personalizacion)
            set({ items: items.filter((i) => buildItemKey(i.productoId, i.personalizacion) !== key) })
          } else {
            set({ items: items.filter((i) => i.productoId !== productoId) })
          }
          return
        }

        const clamped = Math.min(cantidad, CART_MAX_ITEMS)

        if (personalizacion !== undefined) {
          const key = buildItemKey(productoId, personalizacion)
          set({
            items: items.map((i) =>
              buildItemKey(i.productoId, i.personalizacion) === key ? { ...i, cantidad: clamped } : i
            ),
          })
        } else {
          set({
            items: items.map((i) =>
              i.productoId === productoId ? { ...i, cantidad: clamped } : i
            ),
          })
        }
      },

      clearCart: () => {
        set({ items: [] })
      },

      totalItems: () => {
        return get().items.reduce((sum, item) => sum + item.cantidad, 0)
      },

      subtotal: () => {
        return get().items.reduce((sum, item) => sum + item.precio * item.cantidad, 0)
      },

      costoEnvio: () => {
        return get().items.length > 0 ? COSTO_ENVIO_FLAT : 0
      },

      total: () => {
        const state = get()
        return state.subtotal() + state.costoEnvio()
      },

      // Initialize: verify user on store load
      _init: () => {
        const currentUserId = getCurrentUserId()
        const storedUserId = getStoredUserId()
        
        // If different users, clear cart
        if (currentUserId && storedUserId && currentUserId !== storedUserId) {
          set({ items: [], userId: currentUserId })
        } else if (currentUserId) {
          set({ userId: currentUserId })
        }
      },
    }),
    {
      name: CART_STORAGE_KEY,
      partialize: (state) => ({
        items: state.items,
        userId: state.userId,
      }),
    }
  )
)

// Initialize on import - clear cart if user changed
if (typeof window !== 'undefined') {
  setTimeout(() => {
    const store = useCartStore.getState()
    if (store._init) {
      store._init()
    }
  }, 0)
}
