/**
 * PaginationControls Component
 * Navigation controls for paginated product listing
 */

interface PaginationControlsProps {
  currentPage: number
  totalItems: number
  itemsPerPage: number
  onPageChange: (page: number) => void
  isLoading?: boolean
}

export function PaginationControls({
  currentPage,
  totalItems,
  itemsPerPage,
  onPageChange,
  isLoading,
}: PaginationControlsProps) {
  const totalPages = Math.ceil(totalItems / itemsPerPage)
  const hasNextPage = currentPage < totalPages
  const hasPrevPage = currentPage > 1
  const startItem = (currentPage - 1) * itemsPerPage + 1
  const endItem = Math.min(currentPage * itemsPerPage, totalItems)

  return (
    <div className="flex flex-col sm:flex-row items-center justify-between gap-4 py-6 border-t border-gray-200">
      {/* Items Info */}
      <div className="text-sm text-gray-600">
        Showing{' '}
        <span className="font-semibold text-gray-900">{startItem}</span> to{' '}
        <span className="font-semibold text-gray-900">{endItem}</span> of{' '}
        <span className="font-semibold text-gray-900">{totalItems}</span> products
      </div>

      {/* Pagination Buttons */}
      <div className="flex items-center gap-2">
        {/* Previous Button */}
        <button
          onClick={() => onPageChange(currentPage - 1)}
          disabled={!hasPrevPage || isLoading}
          className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md font-medium hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          aria-label="Previous page"
        >
          ← Previous
        </button>

        {/* Page Numbers */}
        <div className="flex items-center gap-1">
          {/* First page */}
          <PageButton
            pageNumber={1}
            isActive={currentPage === 1}
            onClick={() => onPageChange(1)}
            isLoading={isLoading}
          />

          {/* Ellipsis before middle pages */}
          {currentPage > 3 && <span className="px-2 py-1 text-gray-600">...</span>}

          {/* Middle pages (current ± 1) */}
          {totalPages > 2 &&
            Array.from({ length: Math.min(3, totalPages - 1) }, (_, i) => {
              const pageNum = Math.max(2, currentPage - 1) + i
              if (pageNum >= totalPages) return null
              return (
                <PageButton
                  key={pageNum}
                  pageNumber={pageNum}
                  isActive={currentPage === pageNum}
                  onClick={() => onPageChange(pageNum)}
                  isLoading={isLoading}
                />
              )
            })}

          {/* Ellipsis after middle pages */}
          {currentPage < totalPages - 2 && (
            <span className="px-2 py-1 text-gray-600">...</span>
          )}

          {/* Last page */}
          {totalPages > 1 && (
            <PageButton
              pageNumber={totalPages}
              isActive={currentPage === totalPages}
              onClick={() => onPageChange(totalPages)}
              isLoading={isLoading}
            />
          )}
        </div>

        {/* Next Button */}
        <button
          onClick={() => onPageChange(currentPage + 1)}
          disabled={!hasNextPage || isLoading}
          className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md font-medium hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          aria-label="Next page"
        >
          Next →
        </button>
      </div>

      {/* Page Info */}
      <div className="text-sm text-gray-600">
        Page <span className="font-semibold text-gray-900">{currentPage}</span> of{' '}
        <span className="font-semibold text-gray-900">{totalPages}</span>
      </div>
    </div>
  )
}

interface PageButtonProps {
  pageNumber: number
  isActive: boolean
  onClick: () => void
  isLoading?: boolean
}

function PageButton({ pageNumber, isActive, onClick, isLoading }: PageButtonProps) {
  return (
    <button
      onClick={onClick}
      disabled={isLoading}
      className={`px-3 py-2 rounded-md font-medium transition-colors ${
        isActive
          ? 'bg-blue-600 text-white'
          : 'border border-gray-300 text-gray-700 hover:bg-gray-50'
      } disabled:opacity-50 disabled:cursor-not-allowed`}
      aria-label={`Go to page ${pageNumber}`}
      aria-current={isActive ? 'page' : undefined}
    >
      {pageNumber}
    </button>
  )
}
