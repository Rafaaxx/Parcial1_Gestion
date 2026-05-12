/**
 * CatalogPage Component
 * Main catalog page with filters sidebar, product grid, and pagination
 * Layout: Responsive - sidebar on desktop, top bar on mobile
 */

import { useNavigate } from 'react-router-dom'
import { CatalogFilters } from '../components/CatalogFilters'
import { ProductList } from '../components/ProductList'
import { PaginationControls } from '../components/PaginationControls'
import { useProducts } from '../hooks/useCatalogFilters'
import { useCatalogStore } from '../stores/catalogStore'

export function CatalogPage() {
  const navigate = useNavigate()
  const { products, total, isLoading, error } = useProducts()
  const { currentPage, limit, setPage } = useCatalogStore()

  const handleProductClick = (id: number) => {
    navigate(`/productos/${id}`)
  }

  const handlePageChange = (page: number) => {
    setPage(page)
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Public Catalog</h1>
          <p className="text-gray-600">
            Browse our selection of {total} available products
          </p>
        </div>

        {/* Main Layout: Filters + Content */}
        <div className="flex flex-col lg:flex-row gap-8">
          {/* Sidebar Filters (Desktop) / Mobile Filters */}
          <div className="w-full lg:w-64 flex-shrink-0">
            <CatalogFilters />
          </div>

          {/* Main Content Area */}
          <div className="flex-1 min-w-0">
            {/* Error State */}
            {error && (
              <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-red-800 font-medium">
                  {error instanceof Error ? error.message : 'Failed to load products'}
                </p>
              </div>
            )}

            {/* Product List */}
            <ProductList
              products={products}
              onProductClick={handleProductClick}
              isLoading={isLoading}
            />

            {/* Pagination */}
            {!isLoading && products.length > 0 && (
              <PaginationControls
                currentPage={currentPage}
                totalItems={total}
                itemsPerPage={limit}
                onPageChange={handlePageChange}
                isLoading={isLoading}
              />
            )}

            {/* Empty State (after loading) */}
            {!isLoading && !error && products.length === 0 && (
              <div className="text-center py-12">
                <p className="text-gray-600 mb-4">No products match your filters.</p>
                <button
                  onClick={() => window.location.reload()}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                >
                  Try Again
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
