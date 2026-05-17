/**
 * CartPage — Full shopping cart page (/carrito)
 *
 * Responsive layout:
 * - Desktop: table + sidebar with summary
 * - Mobile: stacked card layout
 */

import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import { useCartStore } from '@/features/cart/store'
import { CartSummary } from '@/features/cart/components/CartSummary'
import { CheckoutForm } from '@/features/cart/components/CheckoutForm'
import { AddressSelector } from '@/features/cart/components/AddressSelector'
import { useToast } from '@/features/cart/components/ToastNotifier'

export const CartPage: React.FC = () => {
  const items = useCartStore((s) => s.items)
  const removeItem = useCartStore((s) => s.removeItem)
  const updateQuantity = useCartStore((s) => s.updateQuantity)
  const clearCart = useCartStore((s) => s.clearCart)
  const totalItems = useCartStore((s) => s.totalItems())
  const { showToast } = useToast()

  // Selected delivery address
  const [selectedDireccionId, setSelectedDireccionId] = useState<number | null>(null)

  // Debug: log when component renders
  console.log('CartPage render - items:', items.length, 'selectedDireccionId:', selectedDireccionId)

  const handleClearCart = () => {
    clearCart()
    showToast('info', 'Carrito vaciado')
  }

  const handleRemove = (item: (typeof items)[0]) => {
    removeItem(item.productoId, item.personalizacion)
    showToast('info', `${item.nombre} eliminado del carrito`)
  }

  // Empty state
  if (items.length === 0) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-50">
          Carrito de Compras
        </h1>
        <div className="card-base p-12 text-center">
          <svg
            className="w-20 h-20 mx-auto text-gray-300 dark:text-gray-600 mb-4"
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
          <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-50 mb-2">
            Tu carrito está vacío
          </h2>
          <p className="text-gray-600 dark:text-gray-400 mb-6">
            Agregá productos del catálogo para empezar
          </p>
          <Link
            to="/productos"
            className="inline-flex items-center px-6 py-3 bg-primary-600 hover:bg-primary-700 text-white font-medium rounded-lg transition-colors"
          >
            Ver catálogo
          </Link>
        </div>
      </div>
    )
  }

  // Desktop: table + sidebar
  // Mobile: stacked cards
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-50">
          Carrito de Compras
          <span className="ml-2 text-base font-normal text-gray-500 dark:text-gray-400">
            ({totalItems} {totalItems === 1 ? 'artículo' : 'artículos'})
          </span>
        </h1>
        <button
          onClick={handleClearCart}
          className="text-sm text-red-600 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300 font-medium transition-colors"
        >
          Vaciar carrito
        </button>
      </div>

      <div className="flex flex-col lg:flex-row gap-8">
        {/* Cart items — Desktop Table */}
        <div className="flex-1">
          {/* Desktop table view */}
          <div className="hidden lg:block">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm overflow-hidden">
              <table className="w-full">
                <thead className="bg-gray-50 dark:bg-gray-700/50">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Producto
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Precio unit.
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Cantidad
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Personalización
                    </th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Subtotal
                    </th>
                    <th className="px-4 py-3" />
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                  {items.map((item, idx) => {
                    const excludedNames = item.personalizacion
                      .map((id) => item.ingredientes?.find((i) => i.id === id)?.ingrediente?.nombre)
                      .filter(Boolean) as string[]

                    return (
                      <tr key={`${item.productoId}-${idx}`} className="hover:bg-gray-50 dark:hover:bg-gray-700/30">
                        <td className="px-4 py-4">
                          <div className="flex items-center gap-3">
                            <div className="flex-shrink-0 w-14 h-14 rounded-lg overflow-hidden bg-gray-100 dark:bg-gray-700">
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
                            <span className="font-medium text-gray-900 dark:text-gray-100">
                              {item.nombre}
                            </span>
                          </div>
                        </td>
                        <td className="px-4 py-4 text-sm text-gray-600 dark:text-gray-400">
                          ${item.precio.toFixed(2)}
                        </td>
                        <td className="px-4 py-4">
                          <div className="flex items-center border border-gray-200 dark:border-gray-700 rounded-md w-fit">
                            <button
                              onClick={() => updateQuantity(item.productoId, item.cantidad - 1, item.personalizacion)}
                              className="px-2 py-1 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                              aria-label="Disminuir cantidad"
                            >
                              <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 12H4" />
                              </svg>
                            </button>
                            <span className="px-3 py-1 text-sm font-medium text-gray-900 dark:text-gray-100 min-w-[2rem] text-center">
                              {item.cantidad}
                            </span>
                            <button
                              onClick={() => updateQuantity(item.productoId, item.cantidad + 1, item.personalizacion)}
                              className="px-2 py-1 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                              aria-label="Aumentar cantidad"
                            >
                              <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                              </svg>
                            </button>
                          </div>
                        </td>
                        <td className="px-4 py-4 text-sm">
                          {excludedNames.length > 0 ? (
                            <span className="text-amber-600 dark:text-amber-400">
                              Sin: {excludedNames.join(', ')}
                            </span>
                          ) : (
                            <span className="text-gray-400">—</span>
                          )}
                        </td>
                        <td className="px-4 py-4 text-sm font-semibold text-gray-900 dark:text-gray-100 text-right">
                          ${(item.precio * item.cantidad).toFixed(2)}
                        </td>
                        <td className="px-4 py-4 text-right">
                          <button
                            onClick={() => handleRemove(item)}
                            className="p-1 text-gray-400 hover:text-red-500 transition-colors"
                            aria-label={`Eliminar ${item.nombre}`}
                          >
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                            </svg>
                          </button>
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          </div>

          {/* Mobile/tablet stacked view */}
          <div className="lg:hidden space-y-3">
            {items.map((item, idx) => {
              const excludedNames = item.personalizacion
                .map((id) => item.ingredientes?.find((i) => i.id === id)?.ingrediente?.nombre)
                .filter(Boolean) as string[]

              return (
                <div
                  key={`${item.productoId}-${idx}`}
                  className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-4 flex gap-3"
                >
                  {/* Thumbnail */}
                  <div className="flex-shrink-0 w-16 h-16 rounded-lg overflow-hidden bg-gray-100 dark:bg-gray-700">
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
                    <div className="flex items-start justify-between">
                      <h3 className="font-medium text-gray-900 dark:text-gray-100">{item.nombre}</h3>
                      <button
                        onClick={() => handleRemove(item)}
                        className="p-1 text-gray-400 hover:text-red-500 transition-colors"
                        aria-label={`Eliminar ${item.nombre}`}
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      </button>
                    </div>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      ${item.precio.toFixed(2)} c/u
                    </p>
                    {excludedNames.length > 0 && (
                      <p className="text-xs text-amber-600 dark:text-amber-400">
                        Sin: {excludedNames.join(', ')}
                      </p>
                    )}

                    {/* Quantity + line total */}
                    <div className="flex items-center justify-between mt-2">
                      <div className="flex items-center border border-gray-200 dark:border-gray-700 rounded-md">
                        <button
                          onClick={() => updateQuantity(item.productoId, item.cantidad - 1, item.personalizacion)}
                          className="px-2 py-1 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                          aria-label="Disminuir cantidad"
                        >
                          <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 12H4" />
                          </svg>
                        </button>
                        <span className="px-3 py-1 text-sm font-medium text-gray-900 dark:text-gray-100">
                          {item.cantidad}
                        </span>
                        <button
                          onClick={() => updateQuantity(item.productoId, item.cantidad + 1, item.personalizacion)}
                          className="px-2 py-1 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                          aria-label="Aumentar cantidad"
                        >
                          <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                          </svg>
                        </button>
                      </div>
                      <span className="text-sm font-semibold text-gray-900 dark:text-gray-100">
                        ${(item.precio * item.cantidad).toFixed(2)}
                      </span>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        {/* Summary sidebar */}
        <div className="w-full lg:w-80 flex-shrink-0">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 sticky top-24">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
              Resumen del pedido
            </h2>
            <CartSummary hideCheckoutButton />

            {/* Address Selector */}
            <div className="mt-4 border-t border-gray-200 dark:border-gray-700 pt-4">
              <AddressSelector onAddressChange={setSelectedDireccionId} />
            </div>

            {/* Checkout button - using CheckoutForm */}
            <div className="mt-4">
              <CheckoutForm
                items={items.map(item => ({
                  productoId: item.productoId,
                  cantidad: item.cantidad,
                  personalizacion: item.personalizacion,
                }))}
                direccionId={selectedDireccionId}
                onPaymentStart={() => showToast('info', 'Creando pedido...')}
                onError={(error) => showToast('error', error)}
              />
            </div>

            {/* Continue shopping */}
            <Link
              to="/productos"
              className="block text-center mt-4 text-sm text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300 font-medium transition-colors"
            >
              Seguir comprando
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}

export default CartPage
