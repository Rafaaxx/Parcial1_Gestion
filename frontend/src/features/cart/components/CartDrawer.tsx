/**
 * CartDrawer — slide-over panel from the right side
 *
 * Features:
 * - Dark overlay behind drawer (click to close)
 * - Close (X) button
 * - Renders list of CartItemRow components
 * - Empty state: "Tu carrito está vacío" + link to catalog
 * - Summary section with totals
 */

import React, { useEffect, useCallback } from 'react'
import { Link } from 'react-router-dom'
import { useCartStore } from '../store'
import { CartItemRow } from './CartItemRow'
import { CartSummary } from './CartSummary'

interface CartDrawerProps {
  isOpen: boolean
  onClose: () => void
}

export const CartDrawer: React.FC<CartDrawerProps> = ({ isOpen, onClose }) => {
  const items = useCartStore((s) => s.items)
  const totalItems = useCartStore((s) => s.totalItems())

  // Close on Escape key
  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    },
    [onClose]
  )

  useEffect(() => {
    if (isOpen) {
      document.addEventListener('keydown', handleKeyDown)
      // Prevent body scroll when drawer is open
      document.body.style.overflow = 'hidden'
    }
    return () => {
      document.removeEventListener('keydown', handleKeyDown)
      document.body.style.overflow = ''
    }
  }, [isOpen, handleKeyDown])

  return (
    <>
      {/* Overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/40 z-50 transition-opacity"
          onClick={onClose}
          aria-hidden="true"
        />
      )}

      {/* Drawer panel */}
      <div
        className={`fixed top-0 right-0 h-full w-full sm:w-[420px] bg-white dark:bg-gray-900 shadow-2xl z-50 transform transition-transform duration-300 ease-in-out ${
          isOpen ? 'translate-x-0' : 'translate-x-full'
        }`}
        role="dialog"
        aria-modal="true"
        aria-label="Carrito de compras"
      >
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-4 border-b border-gray-200 dark:border-gray-800">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
            Tu Carrito
            {totalItems > 0 && (
              <span className="ml-2 text-sm font-normal text-gray-500 dark:text-gray-400">
                ({totalItems} {totalItems === 1 ? 'artículo' : 'artículos'})
              </span>
            )}
          </h2>
          <button
            onClick={onClose}
            className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
            aria-label="Cerrar carrito"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className="flex flex-col h-[calc(100%-64px)]">
          {/* Items list */}
          <div className="flex-1 overflow-y-auto px-4 py-2">
            {items.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full text-center py-12">
                <svg
                  className="w-16 h-16 text-gray-300 dark:text-gray-600 mb-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={1.5}
                    d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 100 4 2 2 0 000-4z"
                  />
                </svg>
                <p className="text-gray-500 dark:text-gray-400 font-medium mb-2">
                  Tu carrito está vacío
                </p>
                <p className="text-sm text-gray-400 dark:text-gray-500 mb-4">
                  Agregá productos del catálogo para empezar
                </p>
                <Link
                  to="/productos"
                  onClick={onClose}
                  className="inline-flex px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white text-sm font-medium rounded-lg transition-colors"
                >
                  Ver catálogo
                </Link>
              </div>
            ) : (
              items.map((item) => (
                <CartItemRow key={`${item.productoId}-${JSON.stringify(item.personalizacion)}`} item={item} />
              ))
            )}
          </div>

          {/* Summary (fixed at bottom) */}
          {items.length > 0 && (
            <div className="px-4 py-4 border-t border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-800/50">
              <CartSummary />
            </div>
          )}
        </div>
      </div>
    </>
  )
}

export default CartDrawer
