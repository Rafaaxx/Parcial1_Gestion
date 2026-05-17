/**
 * CartItemRow — individual item row in the cart drawer
 *
 * Shows:
 * - Product thumbnail
 * - Name, unit price, quantity with +/- controls, line subtotal
 * - Delete/remove button
 * - Excluded ingredients (if personalization exists)
 */

import React from 'react'
import type { CartItem } from '../types'
import { useCartStore } from '../store'

interface CartItemRowProps {
  item: CartItem
}

export const CartItemRow: React.FC<CartItemRowProps> = ({ item }) => {
  const updateQuantity = useCartStore((s) => s.updateQuantity)
  const removeItem = useCartStore((s) => s.removeItem)

  const handleIncrement = () => {
    updateQuantity(item.productoId, item.cantidad + 1, item.personalizacion)
  }

  const handleDecrement = () => {
    if (item.cantidad <= 1) {
      removeItem(item.productoId, item.personalizacion)
    } else {
      updateQuantity(item.productoId, item.cantidad - 1, item.personalizacion)
    }
  }

  const handleRemove = () => {
    removeItem(item.productoId, item.personalizacion)
  }

  const lineSubtotal = item.precio * item.cantidad

  // Find names of excluded ingredients
  const excludedIngredientNames = item.personalizacion
    .map((id) => {
      const ing = item.ingredientes?.find((i) => i.id === id)
      return ing?.ingrediente?.nombre
    })
    .filter(Boolean) as string[]

  return (
    <div className="flex gap-3 py-3 border-b border-gray-100 dark:border-gray-800 last:border-b-0">
      {/* Thumbnail */}
      <div className="flex-shrink-0 w-16 h-16 rounded-lg overflow-hidden bg-gray-100 dark:bg-gray-800">
        {item.imagenUrl ? (
          <img
            src={item.imagenUrl}
            alt={item.nombre}
            className="w-full h-full object-cover"
            loading="lazy"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-gray-400">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </div>
        )}
      </div>

      {/* Details */}
      <div className="flex-1 min-w-0">
        <div className="flex items-start justify-between gap-2">
          <h4 className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
            {item.nombre}
          </h4>
          <button
            onClick={handleRemove}
            className="flex-shrink-0 p-1 text-gray-400 hover:text-red-500 transition-colors"
            aria-label={`Eliminar ${item.nombre}`}
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        </div>

        <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
          ${item.precio.toFixed(2)} c/u
        </p>

        {/* Excluded ingredients */}
        {excludedIngredientNames.length > 0 && (
          <p className="text-xs text-amber-600 dark:text-amber-400 mt-0.5">
            Sin: {excludedIngredientNames.join(', ')}
          </p>
        )}

        {/* Quantity controls */}
        <div className="flex items-center gap-3 mt-2">
          <div className="flex items-center border border-gray-200 dark:border-gray-700 rounded-md">
            <button
              onClick={handleDecrement}
              className="px-2 py-1 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
              aria-label="Decrementar cantidad"
            >
              <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 12H4" />
              </svg>
            </button>
            <span className="px-3 py-1 text-sm font-medium text-gray-900 dark:text-gray-100 min-w-[2rem] text-center">
              {item.cantidad}
            </span>
            <button
              onClick={handleIncrement}
              className="px-2 py-1 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
              aria-label="Incrementar cantidad"
            >
              <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
            </button>
          </div>
          <span className="text-sm font-semibold text-gray-900 dark:text-gray-100 ml-auto">
            ${lineSubtotal.toFixed(2)}
          </span>
        </div>
      </div>
    </div>
  )
}

export default CartItemRow
