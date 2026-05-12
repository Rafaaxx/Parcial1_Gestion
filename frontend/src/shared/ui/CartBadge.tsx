/**
 * CartBadge component showing item count with shopping cart icon
 *
 * - Primary click: opens CartDrawer (slide-over panel)
 * - Secondary: link to /carrito full page is available via the NavMenu "Mi Carrito" link
 */

import React from 'react'
import { useAuth } from '@/shared/hooks/useAuth'
import { useCartStore } from '@/features/cart/store'
import { useCartUIStore } from '@/features/cart/stores/cartUIStore'

export const CartBadge: React.FC = () => {
  const { user, hasRole } = useAuth()
  const count = useCartStore((state) => state.totalItems())
  const openCart = useCartUIStore((s) => s.openCart)

  // Only visible for CLIENT role or any authenticated user
  if (!user || !hasRole('CLIENT')) return null

  return (
    <button
      onClick={openCart}
      className="relative p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
      aria-label={`Carrito de compras${count > 0 ? `, ${count} artículos` : ''}`}
    >
      <svg
        className="w-6 h-6 text-gray-700 dark:text-gray-300"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 100 4 2 2 0 000-4z"
        />
      </svg>

      {count > 0 && (
        <span className="absolute -top-1 -right-1 inline-flex items-center justify-center w-5 h-5 text-xs font-bold text-white bg-red-500 rounded-full">
          {count > 99 ? '99+' : count}
        </span>
      )}
    </button>
  )
}

export default CartBadge
