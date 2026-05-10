/**
 * Cart store for managing shopping cart state
 */

import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export interface CartItem {
  productoId: string
  producto: {
    id: string
    nombre: string
    precio: number
    imagen?: string
  }
  cantidad: number
  personalizacion?: {
    ingredienteId: string
    removido: boolean
  }[]
}

export interface CartState {
  items: CartItem[]
  addItem: (item: CartItem) => void
  removeItem: (productoId: string) => void
  updateQuantity: (productoId: string, cantidad: number) => void
  clearCart: () => void
  totalItems: () => number
  subtotal: () => number
  total: () => number
}

export const useCartStore = create<CartState>()(
  persist(
    (set, get) => ({
      items: [],

      addItem: (item: CartItem) => {
        const { items } = get()
        const existingIndex = items.findIndex(
          (i) => i.productoId === item.productoId
        )

        if (existingIndex >= 0) {
          const updated = [...items]
          updated[existingIndex] = {
            ...updated[existingIndex],
            cantidad: updated[existingIndex].cantidad + item.cantidad,
          }
          set({ items: updated })
        } else {
          set({ items: [...items, item] })
        }
      },

      removeItem: (productoId: string) => {
        const { items } = get()
        set({ items: items.filter((i) => i.productoId !== productoId) })
      },

      updateQuantity: (productoId: string, cantidad: number) => {
        const { items } = get()
        if (cantidad <= 0) {
          set({ items: items.filter((i) => i.productoId !== productoId) })
          return
        }
        set({
          items: items.map((i) =>
            i.productoId === productoId ? { ...i, cantidad } : i
          ),
        })
      },

      clearCart: () => {
        set({ items: [] })
      },

      totalItems: () => {
        return get().items.reduce((sum, item) => sum + item.cantidad, 0)
      },

      subtotal: () => {
        return get().items.reduce(
          (sum, item) => sum + item.producto.precio * item.cantidad,
          0
        )
      },

      total: () => {
        return get().subtotal()
      },
    }),
    {
      name: 'food-store-cart',
      partialize: (state) => ({
        items: state.items,
      }),
    }
  )
)
