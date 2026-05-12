/**
 * CartSummary — bottom section of cart drawer
 *
 * Shows:
 * - Subtotal, costo de envío ($50), divider, total
 * - Checkout button: disabled with tooltip "Próximamente" (CHANGE-09 not implemented)
 */

import React from 'react'
import { useCartStore } from '../store'

interface CartSummaryProps {
  /** Optional override: set to true to hide the checkout button (e.g. in full-page view with its own button) */
  hideCheckoutButton?: boolean
}

export const CartSummary: React.FC<CartSummaryProps> = ({ hideCheckoutButton = false }) => {
  const subtotal = useCartStore((s) => s.subtotal())
  const costoEnvio = useCartStore((s) => s.costoEnvio())
  const total = useCartStore((s) => s.total())
  const items = useCartStore((s) => s.items)

  if (items.length === 0) return null

  return (
    <div className="border-t border-gray-200 dark:border-gray-700 pt-4 space-y-3">
      {/* Subtotal */}
      <div className="flex justify-between text-sm">
        <span className="text-gray-600 dark:text-gray-400">Subtotal</span>
        <span className="text-gray-900 dark:text-gray-100 font-medium">
          ${subtotal.toFixed(2)}
        </span>
      </div>

      {/* Shipping */}
      <div className="flex justify-between text-sm">
        <span className="text-gray-600 dark:text-gray-400">Envío</span>
        <span className="text-gray-900 dark:text-gray-100 font-medium">
          ${costoEnvio.toFixed(2)}
        </span>
      </div>

      <hr className="border-gray-200 dark:border-gray-700" />

      {/* Total */}
      <div className="flex justify-between text-base">
        <span className="text-gray-900 dark:text-gray-100 font-semibold">Total</span>
        <span className="text-gray-900 dark:text-gray-100 font-bold text-lg">
          ${total.toFixed(2)}
        </span>
      </div>

      {/* Checkout button */}
      {!hideCheckoutButton && (
        <div className="relative group pt-2">
          <button
            disabled
            className="w-full py-3 px-4 bg-gray-300 dark:bg-gray-700 text-gray-500 dark:text-gray-400 font-semibold rounded-lg cursor-not-allowed text-sm"
          >
            Ir a pagar
          </button>
          {/* Tooltip */}
          <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 hidden group-hover:block">
            <div className="bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900 text-xs rounded py-1 px-2 whitespace-nowrap shadow-lg">
              Próximamente
              <div className="absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent border-t-gray-900 dark:border-t-gray-100" />
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default CartSummary
