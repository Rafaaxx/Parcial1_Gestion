/**
 * CartSummary — bottom section of cart drawer
 *
 * Shows:
 * - Subtotal, costo de envío ($50), divider, total
 * - Checkout button: redirects to /checkout
 */

import React from 'react'
import { useNavigate } from 'react-router-dom'
import { useCartStore } from '../store'

interface CartSummaryProps {
  /** Optional override: set to true to hide the checkout button (e.g. in full-page view with its own button) */
  hideCheckoutButton?: boolean
}

export const CartSummary: React.FC<CartSummaryProps> = ({ hideCheckoutButton = false }) => {
  const navigate = useNavigate()
  const subtotal = useCartStore((s) => s.subtotal())
  const costoEnvio = useCartStore((s) => s.costoEnvio())
  const total = useCartStore((s) => s.total())
  const items = useCartStore((s) => s.items)

  if (items.length === 0) return null

  const handleCheckout = () => {
    navigate('/carrito')
  }

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
        <button
          onClick={handleCheckout}
          className="w-full py-3 px-4 bg-primary-600 hover:bg-primary-700 text-white font-semibold rounded-lg transition-colors text-sm mt-2"
        >
          Ir a pagar
        </button>
      )}
    </div>
  )
}

export default CartSummary
