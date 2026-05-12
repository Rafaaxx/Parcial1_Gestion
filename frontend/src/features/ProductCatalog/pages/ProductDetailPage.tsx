/**
 * ProductDetailPage Component
 * Displays full product details: name, description, price, image, categories, ingredients
 * Shows allergen warnings and stock status
 */

import { useParams, useNavigate } from 'react-router-dom'
import { useProductDetail } from '../hooks/useCatalogFilters'

export function ProductDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const productId = id ? Number(id) : null

  const { product, isLoading, error } = useProductDetail(productId || 0)

  if (!productId) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-4xl mx-auto px-4">
          <div className="text-center py-12">
            <p className="text-red-600 font-medium mb-4">Invalid product ID</p>
            <button
              onClick={() => navigate('/catalog')}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              Back to Catalog
            </button>
          </div>
        </div>
      </div>
    )
  }

  // Loading State
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-4xl mx-auto px-4">
          <button
            onClick={() => navigate('/catalog')}
            className="mb-6 text-blue-600 hover:text-blue-700 font-medium flex items-center gap-2"
          >
            ← Back to Catalog
          </button>
          <div className="bg-white rounded-lg p-8">
            <div className="animate-pulse space-y-4">
              <div className="h-96 bg-gray-200 rounded-lg" />
              <div className="h-8 bg-gray-200 rounded w-3/4" />
              <div className="h-4 bg-gray-200 rounded w-1/2" />
            </div>
          </div>
        </div>
      </div>
    )
  }

  // Error State
  if (error || !product) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-4xl mx-auto px-4">
          <button
            onClick={() => navigate('/catalog')}
            className="mb-6 text-blue-600 hover:text-blue-700 font-medium flex items-center gap-2"
          >
            ← Back to Catalog
          </button>
          <div className="bg-white rounded-lg p-8 text-center">
            <p className="text-red-600 font-medium mb-4">
              {error instanceof Error ? error.message : 'Product not found'}
            </p>
            <button
              onClick={() => navigate('/catalog')}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              Back to Catalog
            </button>
          </div>
        </div>
      </div>
    )
  }

  // Check for allergens in ingredients
  const hasAllergens = product.ingredientes?.some((ing) => ing.es_alergeno) ?? false

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Back Button */}
        <button
          onClick={() => navigate('/catalog')}
          className="mb-6 text-blue-600 hover:text-blue-700 font-medium flex items-center gap-2"
        >
          ← Back to Catalog
        </button>

        {/* Main Product Card */}
        <div className="bg-white rounded-lg shadow-lg overflow-hidden">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 p-8">
            {/* Product Image */}
            <div>
              {product.imagen_url ? (
                <img
                  src={product.imagen_url}
                  alt={product.nombre}
                  className="w-full h-96 object-cover rounded-lg"
                />
              ) : (
                <div className="w-full h-96 bg-gray-200 rounded-lg flex items-center justify-center">
                  <svg
                    className="w-24 h-24 text-gray-400"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={1.5}
                      d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
                    />
                  </svg>
                </div>
              )}
            </div>

            {/* Product Info */}
            <div className="flex flex-col justify-between">
              {/* Stock Badge */}
              <div className="mb-4">
                {product.disponible ? (
                  <span className="inline-block px-4 py-2 bg-green-500 text-white font-semibold rounded-full text-sm">
                    ✓ In Stock
                  </span>
                ) : (
                  <span className="inline-block px-4 py-2 bg-red-500 text-white font-semibold rounded-full text-sm">
                    ✕ Out of Stock
                  </span>
                )}
              </div>

              {/* Product Name */}
              <h1 className="text-4xl font-bold text-gray-900 mb-4">{product.nombre}</h1>

              {/* Price */}
              <div className="mb-6 pb-6 border-b border-gray-200">
                <p className="text-gray-600 text-sm mb-2">Price per unit</p>
                <p className="text-5xl font-bold text-gray-900">${product.precio.toFixed(2)}</p>
              </div>

              {/* Description */}
              <div className="mb-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Description</h3>
                <p className="text-gray-700 leading-relaxed">{product.descripcion}</p>
              </div>

              {/* Categories */}
              {product.categorias && product.categorias.length > 0 && (
                <div className="mb-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-3">Categories</h3>
                  <div className="flex flex-wrap gap-2">
                    {product.categorias.map((cat) => (
                      <span
                        key={cat.id}
                        className="px-4 py-2 bg-blue-100 text-blue-700 rounded-full font-medium text-sm"
                      >
                        {cat.nombre}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Ingredients & Allergen Information */}
          <div className="border-t border-gray-200 p-8 bg-gray-50">
            <div className="mb-8">
              <div className="flex items-center gap-3 mb-4">
                <h2 className="text-2xl font-bold text-gray-900">Ingredients</h2>
                {hasAllergens && (
                  <span className="inline-flex items-center gap-1 px-3 py-1 bg-red-100 text-red-700 rounded-full text-sm font-semibold">
                    ⚠️ Contains Allergens
                  </span>
                )}
              </div>

              {product.ingredientes && product.ingredientes.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {product.ingredientes.map((ingredient) => (
                    <div
                      key={ingredient.id}
                      className={`p-4 rounded-lg border-2 ${
                        ingredient.es_alergeno
                          ? 'bg-red-50 border-red-200'
                          : 'bg-white border-gray-200'
                      }`}
                    >
                      <div className="flex items-start justify-between">
                        <span className="font-medium text-gray-900">{ingredient.nombre}</span>
                        {ingredient.es_alergeno && (
                          <span className="inline-block px-2 py-1 bg-red-500 text-white text-xs font-bold rounded">
                            ALLERGEN
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-600">No ingredients information available</p>
              )}
            </div>

            {/* Allergen Info Box */}
            {hasAllergens && (
              <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mt-6">
                <div className="flex gap-3">
                  <span className="text-2xl">⚠️</span>
                  <div>
                    <h4 className="font-semibold text-yellow-800">Allergen Warning</h4>
                    <p className="text-yellow-700 text-sm mt-1">
                      This product contains ingredients marked as allergens. If you have food
                      allergies, please review the ingredients list carefully before consuming.
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Bottom Actions */}
        <div className="mt-8 flex justify-center">
          <button
            onClick={() => navigate('/catalog')}
            className="px-8 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors"
          >
            Back to Catalog
          </button>
        </div>
      </div>
    </div>
  )
}
