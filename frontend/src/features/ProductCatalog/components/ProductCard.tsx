/**
 * ProductCard Component
 * Displays a single product in card format with image, price, categories, availability,
 * and an "Agregar al carrito" button.
 */

import { ProductListItem } from '../types/catalog'
import { AddToCartButton } from '@/features/cart/components/AddToCartButton'

interface ProductCardProps {
  product: ProductListItem
  onClick?: () => void
}

export function ProductCard({ product, onClick }: ProductCardProps) {
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if ((e.key === 'Enter' || e.key === ' ') && onClick) {
      e.preventDefault()
      onClick()
    }
  }

  return (
    <div
      onClick={onClick}
      onKeyDown={handleKeyDown}
      role="button"
      tabIndex={0}
      className="group relative flex flex-col h-full bg-white rounded-lg shadow hover:shadow-lg transition-shadow duration-300 overflow-hidden cursor-pointer hover:-translate-y-1"
      aria-label={`Product: ${product.nombre}`}
    >
      {/* Image Container */}
      <div className="relative w-full h-48 bg-gray-200 overflow-hidden">
        {product.imagen ? (
          <img
            src={product.imagen}
            alt={product.nombre}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center bg-gray-300">
            <svg
              className="w-12 h-12 text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
              />
            </svg>
          </div>
        )}

        {/* Stock Badge */}
        <div className="absolute top-3 right-3">
          {product.disponible ? (
            <span className="inline-block px-3 py-1 bg-green-500 text-white text-xs font-semibold rounded-full">
              In Stock
            </span>
          ) : (
            <span className="inline-block px-3 py-1 bg-red-500 text-white text-xs font-semibold rounded-full">
              Out of Stock
            </span>
          )}
        </div>
      </div>

      {/* Content Container */}
      <div className="flex flex-col flex-grow p-4">
        {/* Product Name */}
        <h3 className="text-lg font-semibold text-gray-900 line-clamp-2 mb-2 text-left group-hover:text-blue-600 transition-colors">
          {product.nombre}
        </h3>

        {/* Description */}
        <p className="text-sm text-gray-600 line-clamp-2 mb-3 text-left">
          {product.descripcion}
        </p>

        {/* Categories */}
        {product.categorias && product.categorias.length > 0 && (
          <div className="flex flex-wrap gap-1 mb-3">
            {product.categorias.slice(0, 2).map((cat) => (
              <span
                key={cat.id}
                className="inline-block px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded"
              >
                {cat.nombre}
              </span>
            ))}
            {product.categorias.length > 2 && (
              <span className="inline-block px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded">
                +{product.categorias.length - 2}
              </span>
            )}
          </div>
        )}

        {/* Price (bottom of card) */}
        <div className="mt-auto pt-4 border-t border-gray-200">
          <div className="text-2xl font-bold text-gray-900">
            ${typeof product.precio_base === 'string' 
              ? parseFloat(product.precio_base).toFixed(2) 
              : product.precio_base.toFixed(2)}
          </div>
          <p className="text-xs text-gray-500 mt-1">per unit</p>
        </div>

        {/* Add to Cart Button */}
        {product.disponible && (
          <div className="mt-3">
            <AddToCartButton
              producto={product}
              className="w-full text-center"
            />
          </div>
        )}
      </div>
    </div>
  )
}
