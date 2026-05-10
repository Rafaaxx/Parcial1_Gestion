/**
 * ProductListPage — Catalog of products
 */

import React from 'react'

export const ProductListPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-50">
        Catálogo de Productos
      </h1>
      <div className="card-base p-12 text-center">
        <span className="text-5xl block mb-4">🍽️</span>
        <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-50 mb-2">
          Próximamente
        </h2>
        <p className="text-gray-600 dark:text-gray-400">
          El catálogo de productos estará disponible pronto.
        </p>
      </div>
    </div>
  )
}

export default ProductListPage
